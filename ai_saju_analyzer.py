import os
import time
import json
import re
from openai import OpenAI
from datetime import datetime
from typing import Dict, Any
from config import AIConfig
from utils.logger import LoggerMixin

class AISajuAnalyzer(LoggerMixin):
    def __init__(self, api_key: str = None):
        """
        사주 분석기 클래스 초기화.
        - OpenAI API 설정
        - 파트별 분석 구조, 참고 패키지명 사전 정의
        """
        super().__init__("AISajuAnalyzer")
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.ai_config = AIConfig()
        self.system_prompt = self._load_system_prompt()

        now = datetime.now()
        weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        self.current_date = f"{now.year}년 {now.month}월 {now.day}일 {weekdays[now.weekday()]}"

        # --- 개선된 파트별 분석 구조 ---
        self.analysis_parts = {
            1: {
                "title": "너의 인생 설계도: 사주팔자 열어보기",
                "intro": "가장 먼저, 너라는 우주를 구성하는 고유한 코드, 사주팔자부터 살펴보자. 이게 모든 이야기의 시작이야.",
                "sections": [(1, "너는 어떤 코드로 이루어져 있을까? (너의 사주팔자)", 400, {})]
            },
            2: {
                "title": "'나'라는 존재 깊이 보기",
                "intro": "자, 이제 설계도를 바탕으로 '너'라는 사람의 본질을 깊이 들여다볼 시간이야. 너는 어떤 사람일까?",
                "sections": [
                    (2, "너라는 사람의 '본캐'는? (핵심 정체성)", 800, {}),
                    (3, "네 안에 숨겨진 10가지 재능과 성향", 800, {}),
                    (4, "너의 에너지 레벨과 스타일은?", 600, {})
                ]
            },
            3: {
                "title": "현실 속의 나: 인생의 주요 테마",
                "intro": "타고난 기질이 현실에서는 어떻게 나타날까? 일, 돈, 사랑이라는 세 가지 핵심 주제로 나눠서 살펴볼게.",
                "sections": [
                    (5, "일할 때 너는 어떤 사람이야? (직업 & 사업)", 1000, {}),
                    (6, "너는 돈이랑 얼마나 친할까? (재물운)", 1000, {}),
                    (7, "사랑할 때 너는 어떤 모습이야? (연애 & 궁합)", 1000, {"is_love_related": True})
                ]
            },
            4: {
                "title": "시간 속의 나: 인생의 여정과 타이밍",
                "intro": "인생은 시간이라는 강을 따라 흘러가. 네 인생의 강이 언제 잔잔하고, 언제 폭풍우가 칠지 미리 알아보자.",
                "sections": [
                    (8, "네 인생의 하이라이트는 언제일까? (인생 전체의 흐름)", 900, {}),
                    (9, "올해 너에게 펼쳐질 이야기 (2025년)", 1000, {})
                ]
            },
            5: {
                "title": "인생의 파도를 항해하는 법",
                "intro": "누구의 인생에나 좋은 파도와 거친 파도가 찾아와. 이 파도들을 어떻게 타야 할지 그 항해술을 알려줄게.",
                "sections": [
                    (10, "앞으로 1년, 월별 연애 & 금전 예보", 1000, {"is_love_related": True}),
                    (11, "가까운 미래, 어떤 준비를 해야 할까? (향후 3~5년)", 1000, {})
                ]
            },
            6: {
                "title": "너의 잠재력을 깨우는 맞춤 솔루션",
                "intro": "사주를 알았으니 이제 더 나은 삶을 위해 활용해야지! 너의 기운을 북돋아주고, 인생의 중요한 순간을 잡을 수 있는 구체적인 방법들을 알려줄게.",
                "sections": [
                    (12, "네 인생의 '대박' 기회는 언제, 어떻게 잡을까?", 800, {}),
                    (13, "인생의 위기를 기회로 바꾸는 지혜", 800, {}),
                    (14, "네 기운을 충전해주는 맞춤 아이템 (색, 음식, 방향)", 500, {}),
                    (15, "너와 잘 맞는 사람 vs 피해야 할 사람 (인간관계 팁)", 600, {"is_love_related": True})
                ]
            },
            7: {
                "title": "너의 이야기, 너의 힘",
                "intro": "지금까지의 모든 이야기를 종합해서, 네 인생의 주인공인 너에게 해주고 싶은 진짜 중요한 이야기야.",
                "sections": [
                    (16, "너라는 보석을 가장 빛나게 닦는 법 (종합 조언)", 1000, {})
                ]
            }
        }

        # --- 개선된 파트별 참고 지식 매핑 ---
        self.part_package_mapping = {
            1: ["천간_지지_기초", "오행_분포_분석", "일주론_기본"],
            2: ["일간별_성격_심층분석", "십성_재능_및_심리", "12운성_에너지_흐름", "신살_잠재성_분석"],
            3: ["십성_직업적성_재물운", "궁합_인간관계론", "대운_흐름과_사회활동", "신살_사회적_특성"],
            4: ["대운_분석_프레임워크", "세운_연도별_운세_분석", "삼재_및_주요_신살_영향"],
            5: ["월운_분석_로직", "대운_세운_관계_분석", "단기_운세_변화_예측"],
            6: ["용신희신_기반_개운법", "오행별_건강_음식_매칭", "십성_기반_인간관계_팁", "대운_활용_전략"],
            7: ["사주팔자_종합_해석_가이드라인", "핵심_강점_약점_요약", "장기적_인생_조언_템플릿"]
        }
        self.log_info("사주 분석기 초기화 완료")

    def _load_system_prompt(self) -> str:
        """
        시스템 프롬프트 텍스트 파일에서 불러오거나, 없으면 기본값 사용
        """
        prompt_file = os.path.join(self.ai_config.PROMPTS_DIR, "system_prompt.txt")
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Warning: {prompt_file} not found, using default prompt")
            return "너는 전문 사주 분석가야. 각 파트별 분석에서 반드시 JSON 출력과 최소 글자수를 지켜줘."

    def set_session_id(self, session_id: str):
        """
        세션별 로깅 세팅
        """
        self.setup_session_logging(session_id)
        self.log_info(f"사주 분석기 세션 설정 완료 - 세션 ID: {session_id}")

    def analyze_all_parts(self, saju_result: Dict[str, Any], user_info: Dict[str, Any], 
                         on_part_complete=None, session_id: str = None) -> Dict[int, Any]:
        """
        전체 8파트를 순차적으로 대화형으로 분석 (API 사용)
        시스템 프롬프트는 최초 한 번만 전송하고, 이후에는 대화 히스토리만 유지
        """
        if session_id:
            self.set_session_id(session_id)
        all_results = {}

        # 시스템 프롬프트 최초 1회만 추가
        conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

        for part_num in range(1, 8):
            try:
                self.log_info(f"Part {part_num} 대화 분석 시작")
                start_time = time.time()

                # 각 파트의 사용자 프롬프트 추가
                user_prompt = self._create_conversation_prompt(part_num, saju_result, user_info)
                conversation_history.append({"role": "user", "content": user_prompt})

                # [LOGGING: 반드시 part_num==1에서만 system 프롬프트 로그 기록]
                if part_num == 1:
                    self.log_input_prompt(self.system_prompt, user_prompt)
                else:
                    self.log_input_prompt("", user_prompt)

                # API 호출
                result = self._call_conversation_api(conversation_history)

                # 대화 히스토리에 응답 추가 (다음 파트에서 참조)
                conversation_history.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})

                all_results[part_num] = result

                if on_part_complete:
                    on_part_complete(part_num, result)

                elapsed_time = time.time() - start_time
                self.log_info(f"PERFORMANCE - Operation: Part {part_num} 대화 분석, Duration: {elapsed_time:.2f}s, Status: SUCCESS")

                if part_num < 7:
                    self.log_info("⏱️ 다음 파트 대기 중... (5초)")
                    time.sleep(5)
            except Exception as e:
                self.log_error(f"Part {part_num} 대화 분석 실패: {e}")
                all_results[part_num] = {
                    "error": str(e),
                    "fallback_message": f"Part {part_num} 분석 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                }
                if on_part_complete:
                    on_part_complete(part_num, all_results[part_num])
        return all_results

    def _create_conversation_prompt(self, part_number: int, saju_result: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        part_info = self.analysis_parts[part_number]
        sections_info = ""
        safe_user_info = {
            "성별": user_info.get("gender", ""),
            "연애상태": user_info.get("relationship", "")
        }
        if user_info.get("mbti"):
            safe_user_info["MBTI"] = user_info["mbti"]
        package_names = self.part_package_mapping.get(part_number, [])

        # 연애 상태 반영: 각 섹션의 옵션 딕셔너리(is_love_related) 활용
        rel = user_info.get("relationship", "").lower()
        def get_love_note():
            if rel in ["솔로", "single"]:
                return "분석 시 현재 사용자는 솔로(싱글) 상태이므로, 연애의 시작, 새로운 인연, 소개팅 가능성, 이상형 등 '솔로' 관점에서 현실적이고 실용적으로 조언해줘."
            elif rel in ["연애중", "커플", "in_relationship"]:
                return "분석 시 현재 사용자는 연애중이므로, 커플로서의 관계 유지, 소통, 갈등관리, 미래 전망 등 '연애중' 관점에서 구체적으로 분석해줘."
            elif rel in ["기혼", "married"]:
                return "분석 시 현재 사용자는 결혼한 상태이므로, 부부 생활, 가족, 결혼생활의 변화와 안정, 배우자와의 궁합 등 '기혼' 관점에서 현실적으로 분석해줘."
            else:
                return "분석 시 현재 사용자의 연애상태를 반드시 반영해 현실적으로 분석해줘."

        # sections_info 작성(옵션 딕셔너리 기반 안내문 포함)
        sections_info = "\n".join([
            f"- {s[1]} (최소 {s[2]}자)" + (f"\n  ※ {get_love_note()}" if s[3].get("is_love_related", False) else "")
            for s in part_info['sections']
        ])

        prompt = f"""사주 데이터: {json.dumps(saju_result, ensure_ascii=False)}
사용자 정보: {json.dumps(safe_user_info, ensure_ascii=False)}
분석 기준일: {self.current_date}

참고 지식: {package_names}

{part_info['title']}
{part_info['intro']}

분석할 섹션:
{sections_info}
"""
        return prompt

    def _call_conversation_api(self, conversation_history: list) -> Dict[str, Any]:
        """
        OpenAI Chat API 호출 & JSON 결과 반환
        """
        try:
            # 프롬프트 로깅은 analyze_all_parts에서 수행
            response = self.client.chat.completions.create(
                model=self.ai_config.OPENAI_MODEL,
                messages=conversation_history,
                max_tokens=self.ai_config.OPENAI_MAX_TOKENS,
                temperature=self.ai_config.OPENAI_TEMPERATURE
            )
            content = response.choices[0].message.content
            self.log_info("사주 분석 응답 수신")

            # 응답 로깅
            usage_info = f"Tokens: {response.usage.total_tokens if response.usage else 'N/A'}"
            self.log_output_prompt(content, usage_info)

            # JSON 파싱 및 결과값 파싱
            parsed_result = self._parse_ai_response(content)
            return parsed_result
        except Exception as e:
            self.log_error(f"대화 API 호출 실패: {e}")
            raise

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """
        사주 분석 응답을 파싱하여 정규화된 형태로 반환
        """
        try:
            # 1. JSON 파싱 시도
            result = json.loads(content)

            # 2. 결과값 파싱 (래핑된 키 제거)
            parsed = self._parse_section_result(result)

            # 3. 섹션별로 강조 변환 적용
            if isinstance(parsed, dict):
                for section, text in parsed.items():
                    if isinstance(text, str):
                        parsed[section] = self.render_bold(text)

            return parsed
        except json.JSONDecodeError as e:
            self.log_error(f"JSON 파싱 실패: {e}")
            
            # 2. 텍스트에서 섹션 추출 시도
            try:
                parsed_sections = self._extract_sections_from_text(content)
                if parsed_sections:
                    # 섹션별로 강조 변환 적용
                    for section, text in parsed_sections.items():
                        if isinstance(text, str):
                            parsed_sections[section] = self.render_bold(text)
                    return parsed_sections
            except Exception as extract_error:
                self.log_error(f"섹션 추출 실패: {extract_error}")
            
            # 3. 최종 fallback: 전체 텍스트를 section_1으로 반환
            return {"section_1": self.render_bold(content)}

    def _extract_sections_from_text(self, text: str) -> Dict[str, str]:
        """
        텍스트에서 섹션을 추출하는 강화된 로직
        """
        sections = {}
        
        # 일반적인 섹션 패턴들
        patterns = [
            r'section_(\d+)["\s]*:["\s]*["\']([^"\']+)["\']',  # section_1: "내용"
            r'section_(\d+)["\s]*:["\s]*([^,\n}]+)',  # section_1: 내용
            r'"section_(\d+)"["\s]*:["\s]*["\']([^"\']+)["\']',  # "section_1": "내용"
            r'"section_(\d+)"["\s]*:["\s]*([^,\n}]+)',  # "section_1": 내용
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for section_num, content in matches:
                section_key = f"section_{section_num}"
                if section_key not in sections:
                    sections[section_key] = content.strip()
        
        # 섹션이 추출되지 않은 경우, 텍스트를 분석하여 섹션으로 분할
        if not sections:
            # 텍스트에서 자연스러운 구분점 찾기
            lines = text.split('\n')
            current_section = []
            section_count = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 새로운 섹션의 시작점 감지
                if (line.startswith('**') or 
                    line.startswith('내가 보기에') or 
                    line.startswith('내 느낌에는') or
                    line.startswith('내 짐작으로는')):
                    
                    if current_section:
                        sections[f"section_{section_count}"] = '\n'.join(current_section).strip()
                        section_count += 1
                        current_section = []
                
                current_section.append(line)
            
            # 마지막 섹션 추가
            if current_section:
                sections[f"section_{section_count}"] = '\n'.join(current_section).strip()
        
        return sections

    def _parse_section_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        'analysis', 'result', 'output' 등으로 래핑된 결과에서 내부 섹션만 추출
        """
        # 래핑 키들 확인
        wrap_keys = ('analysis', 'result', 'output', 'data')

        for wrap_key in wrap_keys:
            if isinstance(result, dict) and wrap_key in result:
                inner_result = result[wrap_key]
                if isinstance(inner_result, dict):
                    # 내부 결과도 다시 파싱 (중첩된 경우)
                    return self._parse_section_result(inner_result)
                elif isinstance(inner_result, str):
                    # 문자열인 경우 section_1으로 반환
                    return {"section_1": inner_result}

        # 래핑되지 않은 경우 그대로 반환
        return result

    @staticmethod
    def render_bold(text: str) -> str:
        """
        결과 문자열 내의 '**텍스트**' 또는 <strong>텍스트</strong> 패턴을 HTML <strong> 태그로 변환
        """
        # 마크다운 강조 → HTML 변환
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # 이미 strong인 경우는 중복 X
        return html

    @staticmethod
    def convert_markdown_bold_to_html(text: str) -> str:
        """
        마크다운 **강조**를 HTML <strong> 태그로 변환
        """
        if not text:
            return text
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    @staticmethod
    def render_result_dict(result: Dict[str, str]) -> Dict[str, str]:
        """
        결과 JSON(dict)에서 각 섹션의 텍스트를 <strong> 강조로 변환하여 반환
        """
        if not isinstance(result, dict):
            return result
        rendered = {}
        for k, v in result.items():
            if isinstance(v, str):
                rendered[k] = AISajuAnalyzer.render_bold(v)
            elif isinstance(v, dict):
                rendered[k] = AISajuAnalyzer.render_result_dict(v)
            else:
                rendered[k] = v
        return rendered

# 사용 예시
if __name__ == "__main__":
    test_saju = {
        "solar": "1992-04-20 11:50",
        "lunar": "1992년 3월 18일",
        "년주": "임신",
        "월주": "갑진",
        "일주": "정유",
        "시주": "병오"
    }
    test_user_info = {
        "gender": "남자",
        "relationship": "솔로",
        "mbti": "ISTP"
    }
    analyzer = AISajuAnalyzer()
    result = analyzer.analyze_all_parts(test_saju, test_user_info)
    # section_1, section_2 등 결과 강조 변환
    for part_num, part_result in result.items():
        print(f"\n[Part {part_num}]")
        rendered = AISajuAnalyzer.render_result_dict(part_result)
        print(rendered)
