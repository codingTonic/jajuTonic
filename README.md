# AI 사주 분석기 (AI Saju Analyzer)

AI 기술을 활용한 개인 맞춤형 사주 분석 시스템입니다.

## 📁 프로젝트 구조

```
sajuJson/
├── 📄 application.py          # Flask 메인 애플리케이션
├── 📄 config.py               # 애플리케이션 설정
├── 📄 requirements.txt        # Python 의존성
├── 📄 Makefile               # 프로젝트 관리 명령어
├── 📄 .gitignore             # Git 제외 파일
│
├── 🐳 deployment/            # 배포 관련 파일들
│   ├── Dockerfile            # Docker 이미지 정의
│   ├── docker-compose.yml    # 개발 환경 Docker Compose
│   ├── docker-compose.prod.yml # 프로덕션 환경 Docker Compose
│   ├── deploy.sh             # 개발 환경 배포 스크립트
│   ├── deploy-prod.sh        # 프로덕션 배포 스크립트
│   ├── nginx.conf            # Nginx 설정
│   ├── env.example           # 환경 변수 예시
│   ├── .dockerignore         # Docker 빌드 제외 파일
│   ├── systemd/              # systemd 서비스 파일
│   └── README_DEPLOYMENT.md  # 배포 가이드
│
├── 📚 docs/                  # 문서 파일들
│   ├── README_DEPLOYMENT.md  # 배포 가이드 (복사본)
│   ├── deployment_guide.md   # 기존 배포 가이드
│   ├── email_setup_guide.md  # 이메일 설정 가이드
│   └── README_프롬프트_로그_시스템.md # 프롬프트 로그 시스템
│
├── 🛠️ tools/                 # 유틸리티 도구들
│   ├── prompt_log_viewer.py  # 프롬프트 로그 뷰어
│   └── scripts/              # 관리 스크립트들
│       ├── backup.sh         # 백업 스크립트
│       └── monitor.sh        # 모니터링 스크립트
│
├── 🧠 ai_saju_analyzer.py    # AI 분석 엔진
├── 📊 saju_calculator.py     # 사주 계산기
├── 💾 cache_manager.py       # 캐시 관리
├── 📧 email_sender.py        # 이메일 전송
├── 🎨 html_generator.py      # HTML 생성기
│
├── 📁 templates/             # HTML 템플릿
├── 📁 static/                # 정적 파일 (CSS, JS)
├── 📁 json/                  # 사주 데이터 JSON 파일들
├── 📁 prompts/               # AI 프롬프트 파일들
├── 📁 utils/                 # 유틸리티 모듈들
├── 📁 cache/                 # 캐시 디렉토리
├── 📁 logs/                  # 로그 디렉토리
└── 📁 venv/                  # Python 가상환경
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 환경 변수 파일 생성
cp deployment/env.example .env
# .env 파일을 편집하여 실제 값들을 입력하세요
```

### 2. 배포 실행
```bash
# 개발/테스트 환경
./deployment/deploy.sh

# 또는 프로덕션 환경
./deployment/deploy-prod.sh
```

### 3. 접속 확인
브라우저에서 `http://localhost:5000`으로 접속

## 🛠️ 관리 명령어

### Makefile 사용
```bash
make help          # 사용 가능한 명령어 확인
make deploy        # 배포
make monitor       # 모니터링
make backup        # 백업
make clean         # 정리
```

### 직접 명령어
```bash
# 로그 확인
docker-compose -f deployment/docker-compose.yml logs -f

# 컨테이너 상태 확인
docker-compose -f deployment/docker-compose.yml ps

# 백업
./tools/scripts/backup.sh

# 모니터링
./tools/scripts/monitor.sh
```

## 📋 주요 기능

- **AI 기반 사주 분석**: GPT 모델을 활용한 개인 맞춤형 분석
- **실시간 분석**: 백그라운드에서 비동기 분석 진행
- **결과 저장**: HTML 형태로 분석 결과 저장 및 다운로드
- **이메일 전송**: 분석 결과를 이메일로 전송
- **캐시 시스템**: 분석 결과 캐싱으로 성능 최적화
- **로깅 시스템**: 상세한 로그 기록 및 모니터링

## 🔧 기술 스택

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT API
- **Database**: 파일 기반 캐시 시스템
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker, Docker Compose, Nginx
- **Email**: SMTP (Gmail)

## 📚 문서

- [배포 가이드](docs/README_DEPLOYMENT.md) - 상세한 배포 방법
- [이메일 설정 가이드](docs/email_setup_guide.md) - 이메일 기능 설정
- [프롬프트 로그 시스템](docs/README_프롬프트_로그_시스템.md) - AI 프롬프트 관리

## 🔒 보안

- 환경 변수를 통한 민감 정보 관리
- CSRF 보호
- 세션 기반 사용자 관리
- 개인정보 해시화 처리

## 🆘 문제 해결

문제가 발생하면 다음을 확인하세요:
1. 로그 파일 확인: `docker-compose -f deployment/docker-compose.yml logs`
2. 환경 변수 설정 확인
3. 시스템 리소스 확인
4. 네트워크 연결 확인

## 📄 라이선스

이 프로젝트는 개인 및 교육 목적으로 사용할 수 있습니다.

---

**AI 사주 분석기** - AI 기술로 더 정확하고 개인화된 사주 분석을 제공합니다. 