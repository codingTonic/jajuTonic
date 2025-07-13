# AI 사주 분석기 - Replit 배포 가이드

## 📋 배포 전 준비사항

### 1. Replit 계정 생성
- [replit.com](https://replit.com)에서 계정 생성
- 무료 플랜으로 시작 가능

### 2. OpenAI API 키 준비
- OpenAI 계정에서 API 키 발급
- Replit Secrets에 저장 예정

## 🚀 배포 단계

### 1단계: 새 Replit 프로젝트 생성
1. Replit 대시보드에서 "Create Repl" 클릭
2. Template: "Python" 선택
3. Project name: "ai-saju-analyzer" 입력

### 2단계: 파일 업로드
다음 파일들을 Replit에 업로드:

**필수 파일들:**
- `application.py` (메인 Flask 앱)
- `ai_saju_analyzer.py` (AI 분석 엔진)
- `saju_calculator.py` (사주 계산)
- `cache_manager.py` (캐시 관리)
- `config.py` (설정)
- `email_sender.py` (이메일 전송)
- `html_generator.py` (HTML 생성)
- `requirements.txt` (의존성)

**디렉토리들:**
- `templates/` (HTML 템플릿)
- `static/` (CSS, JS, 이미지)
- `json/` (사주 데이터)
- `prompts/` (AI 프롬프트)
- `utils/` (유틸리티)

### 3단계: 환경변수 설정
Replit Secrets에서 다음 설정:

```
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
```

### 4단계: .replit 파일 생성
```toml
language = "python3"
run = "python application.py"
```

### 5단계: pyproject.toml 파일 생성 (선택사항)
```toml
[tool.poetry]
name = "ai-saju-analyzer"
version = "1.0.0"
description = "AI-powered Saju (Korean Fortune Telling) Analyzer"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
flask = "^2.3.0"
openai = "^1.0.0"
flask-wtf = "^1.1.0"
```

## ⚙️ Replit 특화 설정

### 1. 포트 설정
Replit은 자동으로 포트를 할당하므로 `application.py`에서:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

### 2. 환경변수 로드
```python
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드 (Replit Secrets는 자동 로드됨)
```

### 3. 파일 경로 수정
Replit의 파일 시스템에 맞게 경로 수정:

```python
# 기존
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Replit용
BASE_DIR = os.getcwd()
```

## 🔧 문제 해결

### 1. 패키지 설치 오류
```bash
# Replit Shell에서
pip install -r requirements.txt
```

### 2. 권한 문제
- Replit은 읽기/쓰기 권한이 제한적
- 임시 파일은 `/tmp` 디렉토리 사용

### 3. 메모리 부족
- 무료 플랜: 512MB RAM
- 캐시 크기 제한 설정 필요

## 📊 성능 최적화

### 1. 캐시 설정
```python
# config.py에서
CACHE_SIZE_LIMIT = 50  # MB 단위로 제한
```

### 2. 로그 레벨 조정
```python
# 개발 환경에서는 INFO, 프로덕션에서는 WARNING
LOG_LEVEL = "INFO"
```

### 3. 파일 압축
- JSON 데이터 파일 압축
- 정적 파일 최적화

## 🌐 외부 접근

### 1. 웹뷰 설정
- Replit 자동으로 웹뷰 제공
- 외부 URL도 자동 생성

### 2. 커스텀 도메인 (유료)
- Pro 플랜에서 커스텀 도메인 설정 가능

## 📈 모니터링

### 1. Replit Analytics
- 방문자 수, 실행 시간 등 기본 통계
- Pro 플랜에서 상세 분석

### 2. 로그 모니터링
- Replit 콘솔에서 실시간 로그 확인
- 에러 추적 및 디버깅

## 🔒 보안 고려사항

### 1. API 키 보안
- 절대 코드에 직접 입력하지 않음
- Replit Secrets 사용 필수

### 2. 세션 보안
- 강력한 SECRET_KEY 사용
- HTTPS 강제 (Replit 자동 제공)

### 3. 입력 검증
- 사용자 입력 데이터 검증 강화
- XSS, CSRF 방어

## 💰 비용 고려사항

### 무료 플랜 제한:
- 500MB 저장공간
- 512MB RAM
- 일정 시간 후 슬립 모드
- 월 1000 크레딧

### Pro 플랜 ($7/월):
- 1GB 저장공간
- 1GB RAM
- 항상 실행
- 무제한 크레딧
- 커스텀 도메인

## 🎯 배포 완료 후 확인사항

1. ✅ 웹뷰에서 애플리케이션 접속 가능
2. ✅ 사주 분석 기능 정상 작동
3. ✅ AI 분석 결과 생성
4. ✅ HTML 다운로드 기능
5. ✅ 이메일 전송 기능 (선택사항)
6. ✅ 로그 정상 기록
7. ✅ 캐시 시스템 작동

## 📞 지원

문제 발생 시:
1. Replit 커뮤니티 포럼
2. GitHub Issues
3. 개발자 문서 참조 