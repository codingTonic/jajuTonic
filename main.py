from flask import Flask, render_template, request, session, redirect, url_for, send_file, jsonify, render_template_string
from flask_wtf.csrf import CSRFProtect
from config import AppConfig
from ai_saju_analyzer import AISajuAnalyzer
from saju_calculator import calculate_saju
from cache_manager import CacheManager
from utils.logger import setup_logger
from email_sender import EmailSender
from datetime import datetime
import tempfile
import os
import hashlib
import json
import threading
import time

app = Flask(__name__)
app.config.from_object(AppConfig)

# CSRF 보호 설정
csrf = CSRFProtect(app)

# Jinja2 필터 등록
@app.template_filter('format_content')
def format_content_filter(content):
    """템플릿에서 사용할 수 있는 포맷팅 필터"""
    return format_analysis_content(content)

# 로거 설정
logger = setup_logger(__name__)

# 캐시 매니저 초기화
cache_manager = CacheManager()

# 이메일 전송기 초기화
email_sender = EmailSender()

# 구글 시트 연동 기능 제거됨

# ========================== 헬퍼 함수들 ==========================

def generate_user_hash(birth_date_str: str, birth_time_str: str) -> str:
    """사용자 식별용 해시 생성 (개인정보 보호)"""
    combined = f"{birth_date_str}_{birth_time_str}"
    return hashlib.sha256(combined.encode()).hexdigest()[:8]

def validate_session() -> tuple[str, dict, dict]:
    """세션 유효성 검사 및 데이터 반환"""
    session_id = session.get('session_id')
    if not session_id:
        return None, None, None
    
    # 캐시에서 사주 결과와 사용자 정보 로드
    saju_result, user_info = cache_manager.load_user_data(session_id)
    
    return session_id, saju_result, user_info

def validate_and_extract_form_data(request_form) -> tuple[str, str, dict]:
    """폼 데이터 검증 및 추출"""
    name = request_form.get('name')
    birth_date_str = request_form.get('birth_date')
    birth_time_str = request_form.get('birth_time', '12:00')
    
    if not birth_date_str or not name:
        raise ValueError("이름과 생년월일을 모두 입력해주세요.")
    
    # 사용자 정보 수집
    user_info = {
        'name': name,
        'birthdate': birth_date_str,
        'birthtime': birth_time_str,
        'gender': request_form.get('gender', 'male'),
        'relationship': request_form.get('relationship', 'single'),
        'mbti': request_form.get('mbti', '')
    }
    
    return birth_date_str, birth_time_str, user_info

def create_saju_result(birth_date_str: str, birth_time_str: str) -> dict:
    """사주 계산 수행"""
    full_datetime_str = f"{birth_date_str} {birth_time_str}"
    birth_datetime_obj = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M')
    return calculate_saju(birth_datetime_obj)

def convert_analysis_results_for_template(all_results: dict, analyzer) -> list:
    """
    AI 분석 결과를 템플릿에 맞는 구조로 변환
    
    Args:
        all_results: {part_number: json_result} 딕셔너리
        analyzer: AISajuAnalyzer 인스턴스
        
    Returns:
        템플릿에 맞는 구조의 분석 결과 리스트
    """
    analysis_parts = []
    
    for part_num in range(1, 9):
        if part_num not in all_results:
            continue
            
        json_result = all_results[part_num]
        part_info = analyzer.analysis_parts[part_num]
        
        # 파트 구조 생성
        part_data = {
            'title': part_info['title'],
            'sections': []
        }
        
        # 🔧 JSON 결과에서 분석 데이터 추출 (이중 래핑 처리)
        analysis_data = json_result.get('analysis', json_result)
        
        # 이중 래핑 처리: analysis.analysis 구조 확인
        if isinstance(analysis_data, dict) and 'analysis' in analysis_data:
            analysis_data = analysis_data['analysis']
        
        # 🔧 실패한 파트 처리 개선 (파트 레벨에서 처리)
        if 'error' in analysis_data:
            # 실패한 파트에 대한 친화적인 메시지 제공
            fallback_message = analysis_data.get('fallback_message', 
                                              "이 부분의 분석은 일시적으로 사용할 수 없습니다. 나중에 다시 시도해주세요.")
            
            section_data = {
                'title': '🔧 분석 준비 중',
                'content': [{'text': f"""
                <div class="error-section">
                    <h4>⚠️ 일시적 오류</h4>
                    <p>{fallback_message}</p>
                    <p class="error-note">
                        💡 <strong>참고:</strong> 다른 파트의 분석 결과를 통해서도 
                        많은 인사이트를 얻으실 수 있습니다.
                    </p>
                </div>
                """}]
            }
            part_data['sections'].append(section_data)
            analysis_parts.append(part_data)
            continue
        
        section_infos = part_info['sections']
        
        for i, (section_key, section_title, min_chars) in enumerate(section_infos):
            # JSON에서 해당 섹션 내용 찾기
            content_text = ""
            section_number_key = f"section_{i+1}"
            
            # 🔧 JSON 파싱 개선 - 직접 JSON 문자열 처리
            if isinstance(analysis_data, str):
                try:
                    # JSON 문자열을 파싱
                    parsed_data = json.loads(analysis_data)
                    if section_number_key in parsed_data:
                        content_text = parsed_data[section_number_key]
                    elif section_key in parsed_data:
                        content_text = parsed_data[section_key]
                    elif len(parsed_data) > i:
                        # 순서대로 가져오기
                        values = list(parsed_data.values())
                        if i < len(values):
                            content_text = values[i]
                    else:
                        # 첫 번째 값 사용
                        content_text = list(parsed_data.values())[0] if parsed_data else ""
                    print(f"[JSON 문자열 파싱 성공] Part {part_num}, Section {i+1}: {len(content_text)} 문자")
                except json.JSONDecodeError as e:
                    print(f"[JSON 문자열 파싱 오류] Part {part_num}, Section {i+1}: {e}")
                    content_text = analysis_data  # 원본 문자열 사용
            else:
                # 기존 딕셔너리 처리
                if section_number_key in analysis_data:
                    content_text = analysis_data[section_number_key]
                elif section_key in analysis_data:
                    content_text = analysis_data[section_key]
                elif len(analysis_data) > i:
                    # 순서대로 가져오기
                    keys = list(analysis_data.keys())
                    if i < len(keys):
                        content_text = analysis_data[keys[i]]
            
            # 🔧 마크다운 코드 블록 처리 개선
            if content_text and isinstance(content_text, str):
                original_content = content_text
                
                # 마크다운 코드 블록 감지 및 제거
                if content_text.strip().startswith('```json'):
                    try:
                        # ```json 과 ``` 제거
                        json_content = content_text.strip()
                        if json_content.startswith('```json'):
                            json_content = json_content[7:]  # ```json 제거
                        if json_content.endswith('```'):
                            json_content = json_content[:-3]  # ``` 제거
                        
                        # JSON 파싱
                        parsed_json = json.loads(json_content.strip())
                        
                        # 내부에서 실제 내용 찾기
                        if section_number_key in parsed_json:
                            content_text = parsed_json[section_number_key]
                        elif f'section_{i+1}' in parsed_json:
                            content_text = parsed_json[f'section_{i+1}']
                        elif 'section_1' in parsed_json and i == 0:
                            content_text = parsed_json['section_1']
                        elif 'section_2' in parsed_json and i == 1:
                            content_text = parsed_json['section_2']
                        elif len(parsed_json) > i:
                            # 순서대로 가져오기
                            values = list(parsed_json.values())
                            if i < len(values):
                                content_text = values[i]
                        else:
                            # 첫 번째 값 사용
                            content_text = list(parsed_json.values())[0] if parsed_json else ""
                        
                        print(f"[JSON 파싱 성공] Part {part_num}, Section {i+1}: {len(content_text)} 문자")
                                
                    except (json.JSONDecodeError, IndexError, KeyError) as e:
                        print(f"[JSON 파싱 오류] Part {part_num}, Section {i+1}: {e}")
                        # 파싱 실패 시 원본 텍스트 사용 (마크다운 블록 제거)
                        content_text = original_content.replace('```json', '').replace('```', '').strip()
                        print(f"[폴백 사용] Part {part_num}, Section {i+1}: {len(content_text)} 문자")
                
                # 빈 내용 체크
                if not content_text or content_text.strip() == "":
                    content_text = "내용을 불러올 수 없습니다."
                    print(f"[빈 내용 감지] Part {part_num}, Section {i+1}: 기본 메시지 사용")
                else:
                    print(f"[내용 확인] Part {part_num}, Section {i+1}: {content_text[:100]}...")
            else:
                content_text = "내용을 불러올 수 없습니다."
                print(f"[내용 없음] Part {part_num}, Section {i+1}: 기본 메시지 사용")
            
            # 마크다운 **강조**를 HTML <strong> 태그로 변환
            if content_text and isinstance(content_text, str):
                content_text = analyzer.convert_markdown_bold_to_html(content_text)
            
            # 섹션 데이터 생성
            section_data = {
                'title': section_title,
                'content': [{'text': content_text}]
            }
            
            part_data['sections'].append(section_data)
        
        # 파트에 섹션이 없는 경우 기본 메시지 추가
        if not part_data['sections']:
            part_data['sections'].append({
                'title': '🔄 분석 중',
                'content': [{'text': '이 파트의 분석이 진행 중입니다. 잠시 후 다시 확인해주세요.'}]
            })
        
        analysis_parts.append(part_data)
    
    return analysis_parts

def parse_saju_result(saju_result: dict) -> dict:
    """사주 결과를 템플릿에서 사용할 수 있도록 파싱"""
    parsed_result = saju_result.copy()
    
    # 각 주(柱)를 천간과 지지로 분리
    for pillar_key, pillar_name in [("년주", "year_pillar"), ("월주", "month_pillar"), 
                                   ("일주", "day_pillar"), ("시주", "time_pillar")]:
        if pillar_key in saju_result:
            ganji = saju_result[pillar_key]
            if len(ganji) == 2:
                parsed_result[pillar_name] = {
                    "heavenly_stem": ganji[0],
                    "earthly_branch": ganji[1]
                }
    
    # 일간 추출 (일주의 천간)
    if "일주" in saju_result and len(saju_result["일주"]) >= 1:
        parsed_result["day_master"] = saju_result["일주"][0]
    
    return parsed_result

def format_analysis_content(content):
    """분석 내용을 가독성 있게 포맷팅"""
    if not content:
        return content
    
    import re
    
    # 1. 문장 끝에서 줄바꿈 추가 (마침표, 느낌표, 물음표 후) - 단일 줄바꿈으로 변경
    content = re.sub(r'([.!?])\s*([가-힣A-Za-z0-9])', r'\1\n\2', content)
    
    # 2. 특정 키워드 후 줄바꿈 (강조 표현들) - 단일 줄바꿈으로 변경
    keywords = ['그런데', '하지만', '또한', '특히', '중요한 건', '무엇보다', '예를 들어', '실제로', '그리고', '따라서']
    for keyword in keywords:
        content = re.sub(f'({keyword})', r'\n\1', content)
    
    # 3. 연속된 줄바꿈 정리 (2개 이상은 1개로)
    content = re.sub(r'\n{2,}', '\n', content)
    
    # 4. 앞뒤 공백 제거
    content = content.strip()
    
    return content

def handle_integrated_analysis(saju_result: dict, user_info: dict, user_hash: str):
    """통합 분석 처리 - 모든 파트를 한 번에 분석"""
    # 캐시 매니저를 사용해서 세션 ID 생성 및 데이터 저장
    session_id = cache_manager.generate_session_id(user_info)
    cache_manager.save_user_data(session_id, saju_result, user_info)
    
    # 세션에는 최소한의 정보만 저장
    session['session_id'] = session_id
    
    # 사주 분석기 초기화
    analyzer = AISajuAnalyzer()

    # 모든 파트 분석 수행
    print("[INTEGRATED] 통합 분석 시작 (Part 1-8, 대화형)...")
    def on_part_complete(part_num, result):
        print(f"[INTEGRATED] Part {part_num} 완료")
        # 결과를 캐시에 저장
        cache_manager.save_analysis(session_id, part_num, result)
    
    logger.info(f"🚀 [사주 분석] 대화형 분석 시작: {session_id}")
    all_results = analyzer.analyze_all_parts(saju_result, user_info, on_part_complete, session_id)
    
    # 분석 결과를 템플릿에 맞게 변환
    analysis_parts = convert_analysis_results_for_template(all_results, analyzer)
    
    # 사주 결과 파싱 (템플릿에서 사용하기 위해)
    parsed_saju_result = parse_saju_result(saju_result)
    
    # 통합 분석 결과 페이지로 이동
    return render_template('integrated_analysis.html',
                         subtitle="사주 종합 분석 결과",
                         user_info=user_info,
                         saju_result=parsed_saju_result,
                         analysis_parts=analysis_parts)

@app.route('/')
def home():
    import time
    start_time = time.time()
    
    # 메인 페이지를 보여주는 역할
    logger.info("홈페이지 접속")
    # 새로운 분석 시작 시 세션 초기화
    session.clear()
    
    # 캐시 정리를 조건부로 실행 (10분에 한 번만)
    import random
    if random.randint(1, 20) == 1:  # 5% 확률로만 실행
        cache_manager.cleanup_old_cache(24)
        logger.info("캐시 정리 실행됨")
    
    response = render_template('index.html')
    
    # 성능 로깅
    load_time = time.time() - start_time
    logger.info(f"홈페이지 로딩 시간: {load_time:.3f}초")
    
    return response

@app.route('/calculate', methods=['POST'])
def calculate():
    """홈페이지(index.html)에서 사용자가 입력한 정보를 받는 역할"""
    try:
        # 폼 데이터 로깅 (디버깅용)
        logger.info(f"📝 [폼 제출] 받은 데이터: name={request.form.get('name')}, birth_date={request.form.get('birth_date')}, gender={request.form.get('gender')}, relationship={request.form.get('relationship')}")
        
        birth_date_str, birth_time_str, user_info = validate_and_extract_form_data(request.form)
        
        # 사주 계산
        saju_result = create_saju_result(birth_date_str, birth_time_str)
        
        # 세션 ID 생성 및 데이터 캐싱
        session_id = cache_manager.generate_session_id(user_info)
        cache_manager.save_user_data(session_id, saju_result, user_info)
        session['session_id'] = session_id
        
        # 사용자 정보를 지정된 이메일로 전송
        try:
            recipient_email = "wndgus920420@gmail.com"
            subject = f"🌟 새로운 사주 분석 요청 - {user_info['name']}"
            user_info_text = f"""
새로운 사주 분석 요청이 접수되었습니다.

📋 사용자 정보:
• 이름: {user_info['name']}
• 생년월일: {user_info['birthdate']}
• 출생시간: {user_info['birthtime']}
• 성별: {'남성' if user_info['gender'] == 'male' else '여성'}
• 연애상태: {user_info['relationship']}
• MBTI: {user_info['mbti']}
• 세션 ID: {session_id}

📊 사주 정보:
{json.dumps(saju_result, ensure_ascii=False, indent=2)}

접수 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # 이메일 전송 시도
            if email_sender.send_user_info_email(recipient_email, user_info, saju_result):
                logger.info(f"📧 [이메일 전송] 사용자 정보 전송 성공: {recipient_email}")
            else:
                logger.warning(f"📧 [이메일 전송] 사용자 정보 전송 실패: {recipient_email}")
                
        except Exception as e:
            logger.error(f"📧 [이메일 전송] 오류 발생: {e}")
        
        logger.info(f"✅ [사주 계산 성공] 사용자: {user_info['name']}, 세션 ID: {session_id}")
        
        # 분석 시작 페이지(result.html) 렌더링
        return render_template('result.html', result=saju_result, user_info=user_info)

    except ValueError as e:
        logger.warning(f"❌ [폼 검증 오류] {str(e)} - 폼 데이터: {dict(request.form)}")
        return render_template('index.html', error=str(e), form_data=request.form)
    except Exception as e:
        logger.error(f"❌ [계산 오류] {str(e)} - 폼 데이터: {dict(request.form)}", exc_info=True)
        return render_template('index.html', error="사주 계산 중 오류가 발생했습니다. 입력값을 확인해주세요.", form_data=request.form)

@app.route('/start-background-analysis', methods=['POST'])
def start_background_analysis():
    """
    백그라운드에서 실제 사주 분석을 시작하는 엔드포인트
    클라이언트에서 AJAX로 호출
    """
    try:
        # 항상 새로운 분석 시작 (이 엔드포인트 호출 = 새로운 분석 요청)
        session_id, saju_result, user_info = validate_session()
        if not session_id:
            return {"error": "세션이 만료되었습니다."}, 400

        # 새로운 분석 시작 시 기존 캐시 삭제
        logger.info(f"🗑️ [캐시 삭제] 사주 종합 분석 시작 - 기존 캐시 삭제: {session_id}")
        cache_manager.clear_analysis_cache(session_id)
        
        # 사주 분석기 초기화
        analyzer = AISajuAnalyzer()

        def on_part_complete(part_num, result):
            cache_manager.save_analysis(session_id, part_num, result)
            logger.info(f"Part {part_num} 분석 완료 및 캐시 저장")

        # 대화형 분석: Part 1-8 모두 대화 방식
        logger.info(f"🚀 [사주 분석] 대화형 분석 시작 (Part 1-8): {session_id}")
        import threading
        thread = threading.Thread(target=analyze_in_background_conversation, args=(session_id, (saju_result, user_info), analyzer, True))
        thread.daemon = True
        thread.start()
        
        return {"status": "started", "message": "사주 분석이 시작되었습니다", "mode": "ai"}
        
    except Exception as e:
        logger.error(f"백그라운드 분석 중 오류 발생: {e}", exc_info=True)
        return {"error": f"분석 중 오류가 발생했습니다: {str(e)}"}, 500

@app.route('/analysis-result')
def analysis_result():
    """캐시된 분석 결과를 보여주는 페이지 (새로고침 가능)"""
    try:
        # 세션 정보 디버깅
        current_session_id = session.get('session_id')
        logger.info(f"🔍 [결과 페이지 접근] 세션 ID: {current_session_id}")
        
        session_id, saju_result, user_info = validate_session()
        
        logger.info(f"🔍 [세션 검증 결과] session_id: {session_id is not None}, saju_result: {saju_result is not None}, user_info: {user_info is not None}")

        if not all([session_id, saju_result, user_info]):
            logger.warning(f"❌ [세션 오류] 세션 정보 없이 결과 페이지에 접근 시도")
            
            # 세션 복구 시도: 최근 완료된 분석을 찾기
            logger.info("🔄 [세션 복구] 최근 완료된 분석 찾는 중...")
            recovered_session = cache_manager.find_recent_completed_analysis()
            
            if recovered_session:
                session_id, saju_result, user_info = recovered_session
                session['session_id'] = session_id  # 세션 복구
                logger.info(f"✅ [세션 복구 성공] 세션 ID: {session_id}")
            else:
                logger.warning("❌ [세션 복구 실패] 복구 가능한 분석을 찾을 수 없습니다")
                return redirect(url_for('home'))

        # 모든 파트 분석 결과 수집 (일부 파트 누락 허용)
        all_results = {}
        missing_parts = []
        
        for part_num in range(1, 9):
            analysis_data = cache_manager.load_analysis(session_id, part_num)
            if analysis_data:
                all_results[part_num] = analysis_data
            else:
                missing_parts.append(part_num)
                logger.warning(f"⚠️ [부분 결과] Part {part_num} 분석 결과 없음. Session ID: {session_id}")
        
        # 사용 가능한 파트가 있으면 결과 표시
        if all_results:
            logger.info(f"📊 [부분 결과 표시] 사용 가능한 파트: {list(all_results.keys())}, 누락된 파트: {missing_parts}")
            
            analyzer = AISajuAnalyzer() # 템플릿 변환에 필요
            analysis_parts = convert_analysis_results_for_template(all_results, analyzer)
            parsed_saju_result = parse_saju_result(saju_result)

            return render_template('integrated_analysis.html',
                                 subtitle="사주 종합 분석 결과 (일부)",
                                 user_info=user_info,
                                 saju_result=parsed_saju_result,
                                 analysis_parts=analysis_parts,
                                 missing_parts=missing_parts)  # 누락된 파트 정보 전달
        else:
            logger.error(f"❌ [결과 없음] 표시할 분석 결과가 없습니다. Session ID: {session_id}")
            return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"분석 결과 페이지 로딩 중 오류 발생: {str(e)}")
        return redirect(url_for('home'))

@app.route('/analysis-progress')
def analysis_progress():
    """사주 분석 진행 상태를 반환"""
    session_id = session.get('session_id')
    if not session_id:
        return {"error": "No session"}, 400

    # 🔧 1. 먼저 분석 완료 상태 확인
    if cache_manager.is_analysis_complete(session_id):
        logger.info(f"✅ [분석 완료] 세션 {session_id} 분석이 완료되었습니다")
        return {
            "status": "completed",
            "last_completed_part": 8,
            "message": "분석이 완료되었습니다"
        }
    
    # 🔧 2. 완료된 파트 수 확인
    completed_parts = cache_manager.get_completed_parts(session_id)
    last_completed_part = len(completed_parts)
    
    logger.info(f"🔍 [진행 상태] 세션 {session_id} - 완료된 파트: {completed_parts} ({last_completed_part}/8)")
    
    # 🔧 3. 일정 시간 후 분석이 진행되지 않으면 타임아웃 처리
    # 실제 프로덕션에서는 분석 시작 시간을 추적해야 함
    return {
        "status": "in_progress",
        "last_completed_part": last_completed_part,
        "completed_parts": completed_parts,
        "message": f"분석 진행 중... ({last_completed_part}/8 완료)"
    }

@app.route('/download-html')
def download_html():
    """HTML 파일 다운로드 처리"""
    try:
        session_id, saju_result, user_info = validate_session()
        if not session_id:
            return "세션이 만료되었습니다. 다시 시도해주세요.", 400

        # 캐시에서 모든 분석 결과 로드
        all_results = cache_manager.load_all_analysis_results(session_id)
        if not all_results or len(all_results) < 8:
             return "아직 분석이 완료되지 않았습니다.", 404

        # 분석 결과를 템플릿용으로 변환
        analyzer = AISajuAnalyzer()
        analysis_parts = convert_analysis_results_for_template(all_results, analyzer)
        parsed_saju = parse_saju_result(saju_result)

        from html_generator import SajuHTMLGenerator

        # HTML 생성
        html_generator = SajuHTMLGenerator()
        html_content = html_generator.generate_standalone_html(
            user_info=user_info,
            saju_result=parsed_saju,
            analysis_parts=analysis_parts
        )

        # 임시 파일에 저장하여 전송
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".html", encoding='utf-8') as temp:
            temp.write(html_content)
            temp_path = temp.name

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{user_info.get('name', 'saju')}_analysis_report.html",
            mimetype='text/html'
        )
    except Exception as e:
        logger.error(f"HTML 생성 중 오류 발생: {e}", exc_info=True)
        return f"HTML 생성 중 오류가 발생했습니다: {e}", 500

@app.route('/clear-privacy-data', methods=['POST'])
def clear_privacy_data():
    """개인정보 및 분석 결과 삭제"""
    try:
        # 현재 세션 ID 가져오기
        current_session_id = session.get('session_id')
        
        if current_session_id:
            # 해당 세션의 모든 캐시 파일 삭제
            cache_manager.clear_session_cache(current_session_id)
            # 사용자 데이터도 삭제
            cache_manager.clear_user_data(current_session_id)
            logger.info(f"🗑️ [개인정보 삭제] 세션 {current_session_id}의 모든 데이터 삭제 완료")
        
        # 모든 세션 데이터 삭제
        session.clear()
        
        return jsonify({
            "success": True,
            "message": "개인정보가 성공적으로 삭제되었습니다."
        })
        
    except Exception as e:
        logger.error(f"개인정보 삭제 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/start-ai-analysis', methods=['POST'])
def start_ai_analysis():
    """사주 종합 분석 시작 (백그라운드 실행)"""
    try:
        session_id = request.json.get('session_id')
        
        if not session_id:
            return jsonify({"error": "세션 ID가 필요합니다"}), 400
        
        # 캐시된 사용자 데이터 확인
        user_data = cache_manager.load_user_data(session_id)
        if not user_data:
            return jsonify({"error": "사용자 데이터를 찾을 수 없습니다"}), 404

        # 기존 분석 결과 삭제 (새로운 분석 시작)
        cache_manager.clear_analysis_cache(session_id)
        app.logger.info(f"🔄 [새로운 분석] 사주 종합 분석 시작하기 버튼 클릭 - 기존 캐시 삭제: {session_id}")

        # 사주 분석기 초기화
        ai_analyzer = AISajuAnalyzer()
        app.logger.info(f"🚀 [사주 분석] 대화형 분석 시작 (Part 1-8): {session_id}")
        
        # 백그라운드 스레드로 분석 시작
        thread = threading.Thread(target=analyze_in_background_conversation, args=(session_id, user_data, ai_analyzer, True))
        thread.daemon = True
        thread.start()

        return jsonify({
            "status": "started", 
            "message": "사주 종합 분석이 시작되었습니다",
            "session_id": session_id,
            "mode": "ai"
        })

    except Exception as e:
        app.logger.error(f"사주 분석 시작 실패: {e}")
        return jsonify({"error": "분석 시작에 실패했습니다"}), 500



def analyze_in_background_conversation(session_id: str, user_data: tuple, ai_analyzer, force_conversation=False):
    """백그라운드에서 대화형 분석만 수행"""
    try:
        saju_result, user_info = user_data
        def on_part_complete(part_num, result):
            cache_manager.save_analysis(session_id, part_num, result)
            app.logger.info(f"🔮 [사주 분석] Part {part_num} 완료 및 저장")
        app.logger.info(f"🚀 [대화형 분석] 시작 - Part 1-8 모두 대화 방식")
        all_results = ai_analyzer.analyze_all_parts(saju_result, user_info, on_part_complete, session_id)
        # 분석 완료 상태 설정
        cache_manager.set_analysis_complete(session_id)
        # 성공률 계산
        success_count = sum(1 for result in all_results.values() if 'error' not in str(result))
        success_rate = (success_count / 8) * 100
        app.logger.info(f"🎯 [사주 분석] 완료 - 성공률: {success_rate:.1f}%")
    except Exception as e:
        app.logger.error(f"백그라운드 사주 분석 실패: {e}")
        # 실패 시 에러 로깅
        app.logger.error(f"❌ [사주 분석 실패] 세션 {session_id}: {e}")
        # 실패 상태를 캐시에 저장
        cache_manager.save_analysis(session_id, "error", {"error": str(e), "timestamp": datetime.now().isoformat()})





@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

if __name__ == '__main__':
    # Replit 환경에서는 0.0.0.0:8080으로 실행
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)