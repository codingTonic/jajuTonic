# Replit 환경변수 설정 가이드

## 🔐 Replit Secrets 설정 방법

### 1단계: Secrets 패널 열기
1. Replit 프로젝트에서 왼쪽 사이드바의 "Tools" 섹션 클릭
2. "Secrets" 선택

### 2단계: 필요한 환경변수 추가

#### 필수 환경변수:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
FLASK_SECRET_KEY=your-random-secret-key-here
```

#### 선택적 환경변수:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### 3단계: 각 변수 추가 방법
1. "New Secret" 버튼 클릭
2. Key: `OPENAI_API_KEY`
3. Value: `sk-your-actual-api-key`
4. "Add Secret" 클릭

### 4단계: 확인
- 추가된 Secrets는 자동으로 환경변수로 사용 가능
- 코드에서 `os.environ.get('OPENAI_API_KEY')`로 접근

## 🔧 환경변수 사용 예시

### config.py에서:
```python
import os

class AppConfig:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 이메일 설정 (선택사항)
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

### ai_saju_analyzer.py에서:
```python
def __init__(self, api_key: str = None):
    self.client = OpenAI(api_key=api_key or os.environ.get('OPENAI_API_KEY'))
```

## ⚠️ 보안 주의사항

### 1. API 키 보안
- ✅ Replit Secrets 사용
- ❌ 코드에 직접 입력하지 않음
- ❌ GitHub에 업로드하지 않음

### 2. Secret Key 생성
```python
import secrets
print(secrets.token_hex(32))  # 64자리 랜덤 문자열 생성
```

### 3. 환경변수 확인
```python
# 디버깅용 (실제 배포 시에는 제거)
print("OPENAI_API_KEY:", "설정됨" if os.environ.get('OPENAI_API_KEY') else "설정되지 않음")
```

## 🚨 문제 해결

### 1. 환경변수가 로드되지 않는 경우
- Replit 재시작
- Secrets 다시 설정
- 코드에서 기본값 설정

### 2. API 키 오류
- OpenAI API 키 유효성 확인
- API 사용량 확인
- 키 형식 확인 (sk-로 시작)

### 3. 이메일 설정 오류
- Gmail 앱 비밀번호 사용
- 2단계 인증 활성화
- SMTP 설정 확인 