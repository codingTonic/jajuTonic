# AI 사주 분석기 배포 가이드

이 문서는 AI 사주 분석기를 다양한 환경에 배포하는 방법을 설명합니다.

## 📋 사전 요구사항

### 필수 소프트웨어
- Docker (20.10 이상)
- Docker Compose (2.0 이상)
- Git

### 필수 환경 변수
다음 환경 변수들을 `.env` 파일에 설정해야 합니다:

```bash
# Flask 애플리케이션 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# OpenAI API 설정
OPENAI_API_KEY=your-openai-api-key-here

# Gmail 이메일 설정 (선택사항)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password-here
```

## 🚀 빠른 시작 (개발/테스트 환경)

### 1. 환경 설정
```bash
# 환경 변수 파일 생성
cp env.example .env
# .env 파일을 편집하여 실제 값들을 입력하세요
```

### 2. 배포 실행
```bash
# 배포 스크립트 실행
./deploy.sh
```

### 3. 접속 확인
브라우저에서 `http://localhost:5000`으로 접속하여 애플리케이션이 정상적으로 작동하는지 확인하세요.

## 🌐 프로덕션 배포

### 1. 서버 준비
- Ubuntu 20.04 LTS 이상 권장
- 최소 2GB RAM, 1 CPU 코어
- 도메인 설정 (선택사항)

### 2. 프로덕션 배포 실행
```bash
# 프로덕션 배포 스크립트 실행
./deploy-prod.sh
```

### 3. Nginx 설정 (도메인 사용 시)
`nginx.conf` 파일에서 `your-domain.com`을 실제 도메인으로 변경하세요.

### 4. SSL 인증서 설정 (HTTPS)
Let's Encrypt를 사용한 무료 SSL 인증서 설정:

```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 줄 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 모니터링 및 관리

### 로그 확인
```bash
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f saju-analyzer
```

### 컨테이너 관리
```bash
# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart

# 컨테이너 중지
docker-compose down

# 컨테이너 및 이미지 완전 제거
docker-compose down --rmi all --volumes --remove-orphans
```

### 백업 및 복구
```bash
# 데이터 백업
tar -czf backup-$(date +%Y%m%d).tar.gz logs/ cache/

# 데이터 복구
tar -xzf backup-YYYYMMDD.tar.gz
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 확인
sudo netstat -tulpn | grep :5000

# 다른 포트 사용
# docker-compose.yml에서 ports 섹션 수정
```

#### 2. 메모리 부족
```bash
# 컨테이너 리소스 제한 확인
docker stats

# 리소스 제한 조정
# docker-compose.prod.yml의 deploy 섹션 수정
```

#### 3. 환경 변수 오류
```bash
# 환경 변수 확인
docker-compose exec saju-analyzer env | grep -E "(SECRET_KEY|OPENAI_API_KEY)"

# .env 파일 재생성
cp env.example .env
# 실제 값들 입력
```

### 로그 분석
```bash
# 애플리케이션 로그 확인
docker-compose logs saju-analyzer

# Nginx 로그 확인 (프로덕션)
docker-compose logs nginx
```

## 🔒 보안 고려사항

### 1. 환경 변수 보안
- `.env` 파일을 Git에 커밋하지 마세요
- 프로덕션 환경에서는 환경 변수 관리 서비스 사용 권장

### 2. 방화벽 설정
```bash
# UFW 방화벽 설정
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 정기 업데이트
```bash
# 이미지 업데이트
docker-compose pull
docker-compose up -d

# 시스템 업데이트
sudo apt-get update && sudo apt-get upgrade
```

## 📈 성능 최적화

### 1. 리소스 모니터링
```bash
# 시스템 리소스 확인
htop
docker stats
```

### 2. 캐시 최적화
- `cache/` 디렉토리 정기 정리
- 캐시 TTL 설정 조정

### 3. 로그 로테이션
```bash
# 로그 파일 크기 제한 설정
# docker-compose.yml에 logging 섹션 추가
```

## 🆘 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 파일 확인
2. 환경 변수 설정 확인
3. 시스템 리소스 확인
4. 네트워크 연결 확인

추가 지원이 필요한 경우 프로젝트 이슈를 생성해주세요. 