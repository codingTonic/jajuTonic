import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        """
        파일 기반 캐시 매니저 초기화
        
        Args:
            cache_dir: 캐시 파일들을 저장할 디렉토리
        """
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """캐시 디렉토리가 존재하지 않으면 생성"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            # .gitignore에 캐시 디렉토리 추가를 위한 파일 생성
            gitignore_path = os.path.join(self.cache_dir, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write('*\n!.gitignore\n')
    
    def generate_session_id(self, user_info: Dict[str, Any]) -> str:
        """사용자 정보를 기반으로 고유한 세션 ID 생성"""
        # 중요한 정보들을 조합해서 해시 생성
        key_data = f"{user_info.get('birthdate', '')}-{user_info.get('birthtime', '')}-{user_info.get('gender', '')}-{user_info.get('relationship', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def save_analysis(self, session_id: str, part_number: int, analysis_result: str):
        """분석 결과를 파일에 저장"""
        try:
            file_path = os.path.join(self.cache_dir, f"{session_id}_part_{part_number}.json")
            data = {
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'part_number': part_number
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[CACHE] Part {part_number} 분석 결과 저장됨: {file_path}")
        except Exception as e:
            print(f"[CACHE ERROR] Part {part_number} 저장 실패: {e}")
    
    def load_analysis(self, session_id: str, part_number: int) -> Optional[str]:
        """파일에서 분석 결과를 로드"""
        try:
            file_path = os.path.join(self.cache_dir, f"{session_id}_part_{part_number}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"[CACHE] Part {part_number} 캐시된 결과 로드됨")
                return data.get('analysis')
            return None
        except Exception as e:
            print(f"[CACHE ERROR] Part {part_number} 로드 실패: {e}")
            return None
    
    def save_user_data(self, session_id: str, saju_result: Dict[str, Any], user_info: Dict[str, Any]):
        """사용자 데이터와 사주 결과를 파일에 저장"""
        try:
            file_path = os.path.join(self.cache_dir, f"{session_id}_data.json")
            data = {
                'saju_result': saju_result,
                'user_info': user_info,
                'timestamp': datetime.now().isoformat()
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[CACHE] 사용자 데이터 저장됨: {file_path}")
        except Exception as e:
            print(f"[CACHE ERROR] 사용자 데이터 저장 실패: {e}")
    
    def load_user_data(self, session_id: str) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """파일에서 사용자 데이터와 사주 결과를 로드"""
        try:
            file_path = os.path.join(self.cache_dir, f"{session_id}_data.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"[CACHE] 사용자 데이터 로드됨")
                return data.get('saju_result'), data.get('user_info')
            return None, None
        except Exception as e:
            print(f"[CACHE ERROR] 사용자 데이터 로드 실패: {e}")
            return None, None
    
    def load_all_analysis_results(self, session_id: str) -> Dict[int, Any]:
        """해당 세션의 모든 분석 결과 파트를 불러옵니다."""
        all_results = {}
        for part_num in range(1, 8): # Part 1부터 7까지
            analysis_data = self.load_analysis(session_id, part_num)
            if analysis_data:
                all_results[part_num] = analysis_data
        return all_results
    
    def set_analysis_complete(self, session_id: str):
        """분석 완료 상태를 캐시에 저장"""
        try:
            file_path = os.path.join(self.cache_dir, f"{session_id}_complete.json")
            data = {
                'completed': True,
                'timestamp': datetime.now().isoformat()
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[CACHE] 분석 완료 상태 저장됨: {file_path}")
        except Exception as e:
            print(f"[CACHE ERROR] 분석 완료 상태 저장 실패: {e}")
    
    def is_analysis_complete(self, session_id: str) -> bool:
        """분석 완료 상태를 확인 (모든 파트 존재 여부까지 검증)"""
        try:
            # 1. complete.json 파일 존재 확인
            file_path = os.path.join(self.cache_dir, f"{session_id}_complete.json")
            if not os.path.exists(file_path):
                return False
            
            # 2. 모든 파트(1-7) 존재 여부 확인
            for part_num in range(1, 8):
                part_file = os.path.join(self.cache_dir, f"{session_id}_part_{part_num}.json")
                if not os.path.exists(part_file):
                    print(f"[CACHE] 분석 완료로 표시되어 있지만 Part {part_num}이 없음: {session_id}")
                    return False
            
            print(f"[CACHE] 분석 완료 확인됨 (모든 파트 존재): {session_id}")
            return True
            
        except Exception as e:
            print(f"[CACHE ERROR] 분석 완료 상태 확인 실패: {e}")
            return False
    
    def get_completed_parts(self, session_id: str) -> list[int]:
        """완료된 파트 목록을 반환"""
        completed_parts = []
        for part_num in range(1, 8):
            if self.load_analysis(session_id, part_num) is not None:
                completed_parts.append(part_num)
        return completed_parts
    
    def clear_analysis_cache(self, session_id: str):
        """특정 세션의 분석 결과 캐시만 삭제 (사용자 데이터는 보호)"""
        try:
            pattern = f"{session_id}_"
            deleted_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(pattern):
                    # 사용자 데이터 파일은 보호 (삭제하지 않음)
                    if filename.endswith('_data.json'):
                        print(f"[CACHE] 사용자 데이터 파일 보호: {filename}")
                        continue
                    
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"[CACHE] 분석 캐시 파일 삭제: {filename}")
            
            print(f"[CACHE] 세션 {session_id} 분석 캐시 정리 완료 ({deleted_count}개 파일 삭제)")
        except Exception as e:
            print(f"[CACHE ERROR] 분석 캐시 정리 실패: {e}")
    
    def clear_session_cache(self, session_id: str):
        """특정 세션의 분석 결과 캐시 파일 삭제 (사용자 데이터는 보호)"""
        try:
            pattern = f"{session_id}_"
            deleted_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(pattern):
                    # 사용자 데이터 파일은 보호 (삭제하지 않음)
                    if filename.endswith('_data.json'):
                        print(f"[CACHE] 사용자 데이터 파일 보호: {filename}")
                        continue
                    
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"[CACHE] 분석 캐시 파일 삭제: {filename}")
            
            print(f"[CACHE] 세션 {session_id} 분석 캐시 정리 완료 ({deleted_count}개 파일 삭제)")
        except Exception as e:
            print(f"[CACHE ERROR] 캐시 정리 실패: {e}")
    
    def clear_user_data(self, session_id: str):
        """특정 세션의 사용자 데이터 파일 삭제"""
        try:
            filename = f"{session_id}_data.json"
            file_path = os.path.join(self.cache_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[CACHE] 사용자 데이터 파일 삭제: {filename}")
            else:
                print(f"[CACHE] 사용자 데이터 파일이 존재하지 않음: {filename}")
        except Exception as e:
            print(f"[CACHE ERROR] 사용자 데이터 삭제 실패: {e}")
    
    def cleanup_old_cache(self, hours: int = 24):
        """오래된 캐시 파일들을 정리 (기본 24시간)"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cleaned_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'timestamp' in data:
                            file_time = datetime.fromisoformat(data['timestamp'])
                            if file_time < cutoff_time:
                                os.remove(file_path)
                                cleaned_count += 1
                    except:
                        # 손상된 파일은 삭제
                        os.remove(file_path)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"[CACHE] {cleaned_count}개의 오래된 캐시 파일 정리 완료")
                
        except Exception as e:
            print(f"[CACHE ERROR] 캐시 정리 실패: {e}")
    
    def find_recent_completed_analysis(self) -> Optional[tuple]:
        """최근에 완료된 분석을 찾아서 세션 정보를 반환"""
        try:
            recent_sessions = []
            
            # 완료 상태 파일들 찾기
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('_complete.json'):
                    session_id = filename.replace('_complete.json', '')
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 타임스탬프가 있는 경우만 고려
                        if 'timestamp' in data:
                            timestamp = datetime.fromisoformat(data['timestamp'])
                            recent_sessions.append((session_id, timestamp))
                    except:
                        continue
            
            if not recent_sessions:
                print("[CACHE] 완료된 분석을 찾을 수 없습니다")
                return None
            
            # 가장 최근 세션 찾기
            recent_sessions.sort(key=lambda x: x[1], reverse=True)
            latest_session_id = recent_sessions[0][0]
            
            # 해당 세션의 사용자 데이터 로드
            saju_result, user_info = self.load_user_data(latest_session_id)
            
            if saju_result and user_info:
                print(f"[CACHE] 최근 완료된 분석 발견: {latest_session_id}")
                return latest_session_id, saju_result, user_info
            else:
                print(f"[CACHE ERROR] 세션 {latest_session_id}의 사용자 데이터를 로드할 수 없습니다")
                return None
                
        except Exception as e:
            print(f"[CACHE ERROR] 최근 분석 찾기 실패: {e}")
            return None
    


# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager() 