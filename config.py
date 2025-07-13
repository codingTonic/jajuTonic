"""
AI 사주 분석기 설정 파일
"""

import os
from typing import Dict, Any

class AIConfig:
    """AI 분석기 설정 클래스"""
    
    # OpenAI API 설정
    OPENAI_MODEL = "gpt-4.1-mini"        # GPT‑4.1 mini API 모델명
    OPENAI_TEMPERATURE = 0.7             # 창의적/부드러운 응답
    OPENAI_MAX_TOKENS = 32768           # 최대 출력 토큰 수 (32K)
    
    # OPENAI_MODEL = "gpt-4o"
    # OPENAI_TEMPERATURE = 0.7
    # OPENAI_MAX_TOKENS = 4000

    # OPENAI_MODEL = "gpt-4o-mini"
    # OPENAI_TEMPERATURE = 0.7
    # OPENAI_MAX_TOKENS = 16384

    # 재시도 설정
    MAX_RETRY_ATTEMPTS = 3
    RETRY_MIN_WAIT = 10  # 초 (기존 5초에서 10초로 증가)
    RETRY_MAX_WAIT = 120  # 초 (기존 30초에서 120초로 증가)
    RETRY_MULTIPLIER = 3  # 기존 2에서 3으로 증가
    
    # Rate Limits 전용 설정
    RATE_LIMIT_RETRY_ATTEMPTS = 5  # Rate Limit 시 더 많은 재시도
    RATE_LIMIT_MIN_WAIT = 30  # Rate Limit 시 최소 30초 대기
    RATE_LIMIT_MAX_WAIT = 300  # Rate Limit 시 최대 5분 대기
    
    # 파트 간 대기 시간 설정
    PART_INTERVAL_SECONDS = 5  # 각 파트 분석 간 5초 대기
    
    # 토큰 사용량 제한
    TOKEN_LIMITS = {
        'part_analysis': 4000,
        'batch_analysis': 8000,
        'single_part': 1500
    }
    
    # 프롬프트 파일 경로
    PROMPTS_DIR = "prompts"
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """OpenAI API 설정 반환"""
        return {
            'model': cls.OPENAI_MODEL,
            'temperature': cls.OPENAI_TEMPERATURE,
            'max_tokens': cls.OPENAI_MAX_TOKENS
        }
    
    @classmethod
    def get_retry_config(cls) -> Dict[str, Any]:
        """재시도 설정 반환"""
        return {
            'max_attempts': cls.MAX_RETRY_ATTEMPTS,
            'min_wait': cls.RETRY_MIN_WAIT,
            'max_wait': cls.RETRY_MAX_WAIT,
            'multiplier': cls.RETRY_MULTIPLIER
        }

class CacheConfig:
    """캐시 설정 클래스"""
    
    CACHE_DIR = "cache"
    MAX_CACHE_SIZE = 1000  # MB
    CACHE_TTL = 7 * 24 * 3600  # 7일 (초)
    
    @classmethod
    def get_cache_path(cls, filename: str) -> str:
        """캐시 파일 경로 반환"""
        return os.path.join(cls.CACHE_DIR, filename)

class EmailConfig:
    """이메일 설정 클래스"""
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # 첨부파일 설정
    MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25MB
    ALLOWED_FORMATS = ['pdf', 'html']
    
    @classmethod
    def get_smtp_config(cls) -> Dict[str, Any]:
        """SMTP 설정 반환"""
        return {
            'server': cls.SMTP_SERVER,
            'port': cls.SMTP_PORT,
            'gmail_address': os.getenv('GMAIL_ADDRESS'),
            'gmail_password': os.getenv('GMAIL_APP_PASSWORD')
        }

class AppConfig:
    """앱 전체 설정 클래스"""
    
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5002
    
    # 보안 설정
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("필수 환경 변수 'SECRET_KEY'가 설정되지 않았습니다. .env 파일을 확인하세요.")
    


    # 로깅 설정
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/saju_analyzer.log"
    
    @classmethod
    def get_flask_config(cls) -> Dict[str, Any]:
        """Flask 설정 반환"""
        return {
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT,
            'secret_key': cls.SECRET_KEY
        } 