# 🔍 프롬프트 로그 시스템 가이드

## 📋 개요

사주 분석 AI 시스템에서 OpenAI API와 주고받는 모든 프롬프트를 자동으로 로깅하는 시스템입니다.

## 🎯 주요 기능

### 1. 자동 프롬프트 로깅
- **입력 프롬프트**: 시스템 프롬프트 + 사용자 프롬프트
- **출력 프롬프트**: AI 응답 + 토큰 사용량 정보
- **세션별 분리**: 각 사용자 세션마다 별도 로그 파일 생성

### 2. 로그 파일 구조
```
logs/
├── prompts_YYYYMMDD.log                    # 기본 프롬프트 로그 (비어있음)
├── prompts_YYYYMMDD_HHMMSS_세션ID.log      # 세션별 프롬프트 로그 (타임스탬프 포함)
└── saju_analyzer.log                       # 일반 시스템 로그
```

### 3. 로그 내용 형식
```
2025-07-06 22:32:21 - [SESSION_START] 세션 54feead0d8ea97f8933f4b138cd0b626 프롬프트 로깅 시작
2025-07-06 22:32:21 - [INPUT_SYSTEM] 시스템 프롬프트 내용...
2025-07-06 22:32:21 - [INPUT_USER] 사용자 프롬프트 내용...
2025-07-06 22:32:21 - [OUTPUT_RESPONSE] AI 응답 내용...
2025-07-06 22:32:21 - [OUTPUT_USAGE] 토큰 사용량 정보...
```

## 🛠️ 사용 방법

### 1. 프롬프트 로그 파일 목록 확인
```bash
# 로그 디렉토리 확인
ls -la logs/

# 프롬프트 로그 파일만 확인
ls -la logs/prompts_*.log
```

### 2. 프롬프트 로그 뷰어 사용
```bash
# 대화형 모드
./venv/bin/python prompt_log_viewer.py

# 특정 파일 번호 지정
./venv/bin/python prompt_log_viewer.py 1
```

### 3. 로그 파일 직접 확인
```bash
# 최신 프롬프트 로그 파일 확인
tail -f logs/prompts_$(date +%Y%m%d)_*.log

# 특정 세션 로그 확인
cat logs/prompts_20250706_54feead0d8ea97f8933f4b138cd0b626.log
```

## 🔧 시스템 구성

### 1. 로깅 시스템 초기화
```python
# AI 분석기에서 자동 초기화
analyzer = AISajuAnalyzer()

# 세션 ID 설정 (자동으로 세션별 로그 파일 생성)
analyzer.set_session_id("54feead0d8ea97f8933f4b138cd0b626")
```

### 2. 프롬프트 로깅 과정
```python
# 1. 입력 프롬프트 로깅
analyzer.log_input_prompt(system_prompt, user_prompt)

# 2. OpenAI API 호출
response = openai.chat.completions.create(...)

# 3. 출력 프롬프트 로깅
analyzer.log_output_prompt(response.content, str(response.usage))
```

### 3. 로그 파일 명명 규칙
- **기본 로그**: `prompts_YYYYMMDD.log`
- **세션별 로그**: `prompts_YYYYMMDD_HHMMSS_세션ID.log`
- **날짜 형식**: `YYYYMMDD` (예: 20250706)
- **시간 형식**: `HHMMSS` (예: 143052)
- **세션 ID**: MD5 해시 32자리 (예: 54feead0d8ea97f8933f4b138cd0b626)
- **매번 새로운 파일**: 분석 시도마다 타임스탬프가 달라 새로운 파일 생성

## 📊 실제 사용 예시

### 1. 웹 애플리케이션에서 자동 로깅
```python
# application.py에서 AI 분석 시작 시
@app.route('/start-background-analysis', methods=['POST'])
def start_background_analysis():
    session_id = session.get('session_id')
    
    # AI 분석 시작 (자동으로 프롬프트 로깅 활성화)
    analyzer = AISajuAnalyzer()
    analyzer.set_session_id(session_id)
    
    # 분석 실행 (모든 프롬프트가 자동 로깅됨)
    results = analyzer.analyze_all_parts_sequential(
        saju_result, user_info, session_id=session_id
    )
```

### 2. 생성되는 로그 파일 예시
```
logs/prompts_20250706_143052_54feead0d8ea97f8933f4b138cd0b626.log
```

### 3. 로그 내용 예시
```
2025-07-06 14:30:52 - [SESSION_START] 세션 54feead0d8ea97f8933f4b138cd0b626 프롬프트 로깅 시작
2025-07-06 22:29:40 - [INPUT_SYSTEM] 너는 사주 분석 전문가야. 한국의 전통 사주학을 바탕으로...
2025-07-06 22:29:40 - [INPUT_USER] 사주 데이터: {"year_pillar": {"cheongan": "임", "jiji": "신"}...
2025-07-06 22:29:45 - [OUTPUT_RESPONSE] {"section_1": "너는 임신(壬申)년, 갑진(甲辰)월..."}
2025-07-06 22:29:45 - [OUTPUT_USAGE] CompletionUsage(completion_tokens=1247, prompt_tokens=2891, total_tokens=4138)
```

## 🔍 로그 분석 및 디버깅

### 1. 프롬프트 품질 확인
- 시스템 프롬프트가 올바르게 설정되었는지 확인
- 사용자 프롬프트에 필요한 데이터가 모두 포함되었는지 확인
- AI 응답이 예상한 형식(JSON)으로 반환되는지 확인

### 2. 토큰 사용량 모니터링
- 각 API 호출별 토큰 사용량 추적
- 비용 최적화를 위한 프롬프트 길이 조정
- 모델별 성능 비교

### 3. 오류 분석
- API 호출 실패 시 입력 프롬프트 확인
- JSON 파싱 오류 시 AI 응답 내용 확인
- 재시도 로직 동작 확인

## 🚀 고급 기능

### 1. 실시간 로그 모니터링
```bash
# 실시간 로그 확인
tail -f logs/prompts_$(date +%Y%m%d)_*.log

# 특정 패턴 검색
grep "OUTPUT_RESPONSE" logs/prompts_*.log
```

### 2. 로그 통계 분석
```bash
# 세션별 API 호출 횟수
grep "INPUT_SYSTEM" logs/prompts_*.log | wc -l

# 토큰 사용량 추출
grep "OUTPUT_USAGE" logs/prompts_*.log | grep -o "total_tokens=[0-9]*"
```

### 3. 로그 파일 관리
```bash
# 오래된 로그 파일 정리 (30일 이상)
find logs/ -name "prompts_*.log" -mtime +30 -delete

# 로그 파일 압축
gzip logs/prompts_*.log
```

## ⚠️ 주의사항

### 1. 개인정보 보호
- 로그 파일에는 사용자의 개인정보(이름, 생년월일 등)가 포함됨
- 로그 파일 접근 권한 제한 필요
- 정기적인 로그 파일 정리 권장

### 2. 디스크 용량 관리
- 프롬프트 로그는 상당한 용량을 차지할 수 있음
- 정기적인 로그 로테이션 필요
- 압축 저장 고려

### 3. API 키 보안
- 로그 파일에 API 키가 노출되지 않도록 주의
- 환경변수를 통한 API 키 관리 필수

## 🔧 테스트 및 검증

### 1. 로깅 시스템 테스트
```bash
# 테스트 스크립트 실행
./venv/bin/python test_prompt_logging.py
```

### 2. 로그 파일 검증
```bash
# 로그 뷰어로 확인
./venv/bin/python prompt_log_viewer.py

# 직접 확인
cat logs/prompts_*_test_*.log
```

## 📝 문제 해결

### 1. 로그 파일이 생성되지 않는 경우
- `logs/` 디렉토리 존재 여부 확인
- 파일 쓰기 권한 확인
- 세션 ID 설정 여부 확인

### 2. 로그 내용이 비어있는 경우
- 프롬프트 로거 초기화 확인
- 핸들러 설정 상태 확인
- 로그 레벨 설정 확인

### 3. 로그 파일 크기가 너무 큰 경우
- 프롬프트 길이 최적화
- 불필요한 데이터 제거
- 로그 로테이션 설정

---

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 언제든지 문의해 주세요!

- 테스트 스크립트: `test_prompt_logging.py`
- 로그 뷰어: `prompt_log_viewer.py`
- 시스템 로그: `logs/saju_analyzer.log` 