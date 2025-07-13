# AI 사주 분석기 Makefile

.PHONY: help build run stop clean logs backup backup-source analyze-source monitor deploy deploy-prod install-deps

# 기본 타겟
help:
	@echo "AI 사주 분석기 관리 명령어"
	@echo ""
	@echo "개발 환경:"
	@echo "  make build        - Docker 이미지 빌드"
	@echo "  make run          - 개발 환경 실행"
	@echo "  make stop         - 컨테이너 중지"
	@echo "  make logs         - 로그 확인"
	@echo ""
	@echo "프로덕션 환경:"
	@echo "  make deploy       - 프로덕션 배포"
	@echo "  make deploy-prod  - 프로덕션 배포 (Nginx 포함)"
	@echo ""
	@echo "백업 및 분석:"
	@echo "  make backup       - 전체 데이터 백업"
	@echo "  make backup-source - 소스 코드만 백업"
	@echo "  make analyze-source - 소스 코드 분석"
	@echo ""
	@echo "유틸리티:"
	@echo "  make monitor      - 시스템 모니터링"
	@echo "  make clean        - 정리 (컨테이너, 이미지, 볼륨 제거)"
	@echo "  make install-deps - 로컬 개발 환경 설정"

# 개발 환경
build:
	docker-compose -f deployment/docker-compose.yml build --no-cache

run:
	docker-compose -f deployment/docker-compose.yml up -d

stop:
	docker-compose -f deployment/docker-compose.yml down

logs:
	docker-compose -f deployment/docker-compose.yml logs -f

# 프로덕션 환경
deploy:
	./deployment/deploy.sh

deploy-prod:
	./deployment/deploy-prod.sh

# 백업 및 분석
backup:
	./tools/scripts/backup.sh

backup-source:
	./tools/scripts/backup-source.sh

analyze-source:
	./tools/scripts/analyze-source.sh

# 유틸리티
monitor:
	./tools/scripts/monitor.sh

clean:
	docker-compose -f deployment/docker-compose.yml down --rmi all --volumes --remove-orphans
	docker system prune -f

install-deps:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "로컬 개발 환경 설정이 완료되었습니다."
	@echo "가상환경 활성화: source venv/bin/activate" 