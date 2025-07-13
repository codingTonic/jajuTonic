"""
로깅 시스템 설정 모듈
"""

import logging
import os
from datetime import datetime
from config import AppConfig

def setup_logger(name: str = "saju_analyzer", log_file: str = None) -> logging.Logger:
    """
    로거 설정 및 반환
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (선택사항)
        
    Returns:
        설정된 로거 객체
    """
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, AppConfig.LOG_LEVEL))
    
    # 이미 핸들러가 있으면 중복 설정 방지
    if logger.handlers:
        return logger
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file is None:
        log_file = AppConfig.LOG_FILE
    
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_api_call(logger: logging.Logger, model: str, tokens_used: int, response_time: float):
    """
    API 호출 로깅
    
    Args:
        logger: 로거 객체
        model: 사용된 모델
        tokens_used: 사용된 토큰 수
        response_time: 응답 시간 (초)
    """
    logger.info(f"API_CALL - Model: {model}, Tokens: {tokens_used}, Time: {response_time:.2f}s")

def log_user_session(logger: logging.Logger, user_id: str, action: str, details: dict = None):
    """
    사용자 세션 로깅
    
    Args:
        logger: 로거 객체
        user_id: 사용자 ID (해시값)
        action: 수행한 동작
        details: 추가 세부사항
    """
    details_str = f", Details: {details}" if details else ""
    logger.info(f"USER_SESSION - ID: {user_id}, Action: {action}{details_str}")

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    오류 로깅
    
    Args:
        logger: 로거 객체
        error: 발생한 오류
        context: 오류 발생 컨텍스트
    """
    context_str = f" [{context}]" if context else ""
    logger.error(f"ERROR{context_str} - {type(error).__name__}: {str(error)}")

def log_performance(logger: logging.Logger, operation: str, duration: float, success: bool):
    """
    성능 로깅
    
    Args:
        logger: 로거 객체
        operation: 수행한 작업
        duration: 소요 시간 (초)
        success: 성공 여부
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"PERFORMANCE - Operation: {operation}, Duration: {duration:.2f}s, Status: {status}")

def setup_prompt_logger(name: str = "prompt_logger") -> logging.Logger:
    """
    프롬프트 전용 로거 설정 및 반환
    
    Args:
        name: 로거 이름
        
    Returns:
        설정된 프롬프트 로거 객체
    """
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 이미 핸들러가 있으면 중복 설정 방지
    if logger.handlers:
        return logger
    
    # 프롬프트 전용 포맷터 (시간 + 메시지만)
    formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 프롬프트 로그 파일 경로
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[DEBUG] 로그 디렉토리 생성: {log_dir}")
    
    prompt_log_file = os.path.join(log_dir, f"prompts_{datetime.now().strftime('%Y%m%d')}.log")
    print(f"[DEBUG] 프롬프트 로그 파일: {prompt_log_file}")
    
    # 파일 핸들러만 추가 (콘솔 출력 없음)
    file_handler = logging.FileHandler(prompt_log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 다른 로거로 전파 방지
    logger.propagate = False
    
    print(f"[DEBUG] 프롬프트 로거 설정 완료 - 핸들러 수: {len(logger.handlers)}")
    
    return logger

def setup_session_prompt_logger(session_id: str, name: str = "session_prompt_logger") -> logging.Logger:
    """
    세션별 프롬프트 전용 로거 설정 및 반환
    
    Args:
        session_id: 세션 ID (고유 식별자)
        name: 로거 이름
        
    Returns:
        설정된 세션별 프롬프트 로거 객체
    """
    # 세션별 고유 로거 이름 생성
    logger_name = f"{name}_{session_id}"
    
    # 로거 생성
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # 이미 핸들러가 있으면 제거 후 재설정 (중복 방지)
    if logger.handlers:
        print(f"[DEBUG] 기존 핸들러 제거: {len(logger.handlers)}개")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    # 프롬프트 전용 포맷터 (시간 + 메시지만)
    formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 프롬프트 로그 파일 경로 (세션 ID 포함)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[DEBUG] 로그 디렉토리 생성: {log_dir}")
    
    # 세션별 로그 파일명: logs/prompts_20250706_143052_91cde5c62b5dfed6eb9366ed2f843cee.log
    current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_log_file = os.path.join(log_dir, f"prompts_{current_timestamp}_{session_id}.log")
    print(f"[DEBUG] 세션별 프롬프트 로그 파일: {session_log_file}")
    
    # 파일 핸들러 생성 및 추가
    try:
        file_handler = logging.FileHandler(session_log_file, encoding='utf-8', mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 다른 로거로 전파 방지
        logger.propagate = False
        
        print(f"[DEBUG] 세션별 프롬프트 로거 설정 완료 - 핸들러 수: {len(logger.handlers)}")
        
        # 테스트 로그 작성
        logger.info(f"[SESSION_START] 세션 {session_id} 프롬프트 로깅 시작")
        file_handler.flush()
        
        # 파일이 실제로 생성되었는지 확인
        if os.path.exists(session_log_file):
            file_size = os.path.getsize(session_log_file)
            print(f"[DEBUG] 세션 로그 파일 생성 확인: {session_log_file} ({file_size} bytes)")
        else:
            print(f"[ERROR] 세션 로그 파일 생성 실패: {session_log_file}")
        
        return logger
        
    except Exception as e:
        print(f"[ERROR] 세션별 로거 설정 실패: {e}")
        import traceback
        traceback.print_exc()
        # 실패 시 기본 프롬프트 로거 반환
        return setup_prompt_logger()

class LoggerMixin:
    """로깅 기능을 제공하는 믹스인 클래스"""
    
    def __init__(self, logger_name: str = None):
        self.logger = setup_logger(logger_name or self.__class__.__name__)
        self.prompt_logger = setup_prompt_logger()
        self.session_id = None  # 세션 ID 저장용
    
    def setup_session_logging(self, session_id: str):
        """
        세션별 프롬프트 로깅 설정
        
        Args:
            session_id: 세션 ID (고유 식별자)
        """
        self.session_id = session_id
        
        print(f"[DEBUG] 세션별 로깅 설정 시작 - 세션 ID: {session_id}")
        
        # 기존 세션 로거가 있으면 핸들러 제거
        if hasattr(self, 'session_prompt_logger'):
            print(f"[DEBUG] 기존 세션 로거 정리 중...")
            for handler in self.session_prompt_logger.handlers[:]:
                try:
                    handler.close()
                    self.session_prompt_logger.removeHandler(handler)
                    print(f"[DEBUG] 핸들러 제거 완료")
                except Exception as e:
                    print(f"[DEBUG] 핸들러 제거 중 오류: {e}")
        
        # 새로운 세션별 로거 생성
        try:
            self.session_prompt_logger = setup_session_prompt_logger(session_id)
            print(f"[DEBUG] 세션별 로거 생성 완료 - 핸들러 수: {len(self.session_prompt_logger.handlers)}")
            
            # 세션 로거가 올바르게 생성되었는지 확인
            if self.session_prompt_logger and self.session_prompt_logger.handlers:
                self.log_info(f"🔄 세션별 프롬프트 로깅 설정 완료 - 세션 ID: {session_id}")
                print(f"[DEBUG] 세션별 프롬프트 로깅 활성화 성공")
            else:
                print(f"[ERROR] 세션별 로거 생성에 실패했습니다")
                self.log_error(f"세션별 로거 생성 실패 - 세션 ID: {session_id}")
                
        except Exception as e:
            print(f"[ERROR] 세션별 로깅 설정 중 오류: {e}")
            import traceback
            traceback.print_exc()
            self.log_error(f"세션별 로깅 설정 실패: {e}")
    
    def log_info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Exception = None):
        """오류 로그"""
        if error:
            self.logger.error(f"{message} - {type(error).__name__}: {str(error)}")
        else:
            self.logger.error(message)
    
    def log_api_call(self, model: str, tokens_used: int, response_time: float):
        """API 호출 로그"""
        log_api_call(self.logger, model, tokens_used, response_time)
    
    def log_user_session(self, user_id: str, action: str, details: dict = None):
        """사용자 세션 로그"""
        log_user_session(self.logger, user_id, action, details)
    
    def log_performance(self, operation: str, duration: float, success: bool):
        """성능 로그"""
        log_performance(self.logger, operation, duration, success)
    
    def log_prompt(self, prompt_type: str, content: str):
        """프롬프트 로그 (별도 파일에 저장)"""
        # 세션별 로거가 있으면 우선 사용
        target_logger = getattr(self, 'session_prompt_logger', self.prompt_logger)
        target_logger.info(f"[{prompt_type}] {content}")
    
    def log_input_prompt(self, system_prompt: str, user_prompt: str):
        """입력 프롬프트 로그"""
        try:
            # 세션별 로거가 있으면 우선 사용
            target_logger = getattr(self, 'session_prompt_logger', self.prompt_logger)
            
            # 🔧 더 자세한 디버깅: 로거 상태 확인
            print(f"[DEBUG] 프롬프트 로거 핸들러 수: {len(target_logger.handlers)}")
            print(f"[DEBUG] 프롬프트 로거 레벨: {target_logger.level}")
            print(f"[DEBUG] 프롬프트 로거 이름: {target_logger.name}")
            
            # 세션별 로거 존재 여부 및 상태 확인
            has_session_logger = hasattr(self, 'session_prompt_logger')
            print(f"[DEBUG] 세션별 로거 존재: {has_session_logger}")
            
            if has_session_logger:
                print(f"[DEBUG] 세션별 로거 사용 중 - 세션 ID: {getattr(self, 'session_id', 'NO_SESSION_ID')}")
                print(f"[DEBUG] 세션별 로거 이름: {target_logger.name}")
                print(f"[DEBUG] 세션별 로거 핸들러 수: {len(target_logger.handlers)}")
                
                # 핸들러 정보 출력
                for i, handler in enumerate(target_logger.handlers):
                    print(f"[DEBUG] 핸들러 {i} 타입: {type(handler).__name__}")
                    if hasattr(handler, 'baseFilename'):
                        print(f"[DEBUG] 핸들러 {i} 파일: {handler.baseFilename}")
                    if hasattr(handler, 'level'):
                        print(f"[DEBUG] 핸들러 {i} 레벨: {handler.level}")
            else:
                print(f"[DEBUG] 기본 프롬프트 로거 사용 중")
            
            # 강제로 로그 메시지 작성
            if system_prompt:
                message = f"[INPUT_SYSTEM] {system_prompt}"
                print(f"[DEBUG] 시스템 프롬프트 로깅 시도: {len(message)} 문자")
                try:
                    target_logger.info(message)
                    print(f"[DEBUG] 시스템 프롬프트 로깅 성공")
                except Exception as e:
                    print(f"[ERROR] 시스템 프롬프트 로깅 실패: {e}")
            
            if user_prompt:
                message = f"[INPUT_USER] {user_prompt}"
                print(f"[DEBUG] 사용자 프롬프트 로깅 시도: {len(message)} 문자")
                try:
                    target_logger.info(message)
                    print(f"[DEBUG] 사용자 프롬프트 로깅 성공")
                except Exception as e:
                    print(f"[ERROR] 사용자 프롬프트 로깅 실패: {e}")
            
            # 강제 플러시 및 동기화
            for i, handler in enumerate(target_logger.handlers):
                try:
                    if hasattr(handler, 'flush'):
                        handler.flush()
                        print(f"[DEBUG] 핸들러 {i} 플러시 완료")
                    if hasattr(handler, 'close'):
                        # 파일을 닫지 말고 sync만 수행
                        if hasattr(handler.stream, 'flush'):
                            handler.stream.flush()
                            print(f"[DEBUG] 핸들러 {i} 스트림 플러시 완료")
                except Exception as e:
                    print(f"[ERROR] 핸들러 {i} 플러시 실패: {e}")
            
            print(f"[DEBUG] 프롬프트 로깅 완료 - 시스템: {len(system_prompt)} 문자, 사용자: {len(user_prompt)} 문자")
            
            # 파일 크기 확인
            if has_session_logger:
                for i, handler in enumerate(target_logger.handlers):
                    if hasattr(handler, 'baseFilename'):
                        try:
                            import os
                            file_path = handler.baseFilename
                            if os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                                print(f"[DEBUG] 로그 파일 {i} 크기: {file_size} bytes ({file_path})")
                            else:
                                print(f"[ERROR] 로그 파일 {i} 존재하지 않음: {file_path}")
                        except Exception as e:
                            print(f"[ERROR] 파일 크기 확인 실패 (핸들러 {i}): {e}")
            
        except Exception as e:
            print(f"[ERROR] 프롬프트 로깅 실패: {e}")
            import traceback
            traceback.print_exc()
            self.log_error(f"프롬프트 로깅 실패: {e}")

    def log_output_prompt(self, response: str, usage_info: str = None):
        """출력 프롬프트 로그"""
        try:
            # 세션별 로거가 있으면 우선 사용
            target_logger = getattr(self, 'session_prompt_logger', self.prompt_logger)
            
            # 응답 로깅
            if response:
                message = f"[OUTPUT_RESPONSE] {response}"
                target_logger.info(message)
                print(f"[DEBUG] 응답 로깅 시도: {len(message)} 문자")
            
            # 사용량 정보 로깅
            if usage_info:
                message = f"[OUTPUT_USAGE] {usage_info}"
                target_logger.info(message)
                print(f"[DEBUG] 사용량 로깅 시도: {len(message)} 문자")
            
            # 강제 플러시
            for handler in target_logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
                if hasattr(handler, 'stream'):
                    if hasattr(handler.stream, 'flush'):
                        handler.stream.flush()
            
            print(f"[DEBUG] 출력 로깅 완료 - 응답: {len(response)} 문자, 사용량: {usage_info or 'N/A'}")
            
        except Exception as e:
            print(f"[ERROR] 출력 로깅 실패: {e}")
            import traceback
            traceback.print_exc()
            self.log_error(f"출력 로깅 실패: {e}") 