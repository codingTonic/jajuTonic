#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모든 모듈 import 테스트"""
    print("🔍 모듈 import 테스트 시작...")
    
    try:
        from config import AppConfig, AIConfig
        print("✅ config 모듈 import 성공")
    except Exception as e:
        print(f"❌ config 모듈 import 실패: {e}")
        return False
    
    try:
        from saju_calculator import calculate_saju
        print("✅ saju_calculator 모듈 import 성공")
    except Exception as e:
        print(f"❌ saju_calculator 모듈 import 실패: {e}")
        return False
    
    try:
        from ai_saju_analyzer import AISajuAnalyzer
        print("✅ ai_saju_analyzer 모듈 import 성공")
    except Exception as e:
        print(f"❌ ai_saju_analyzer 모듈 import 실패: {e}")
        return False
    
    try:
        from cache_manager import CacheManager
        print("✅ cache_manager 모듈 import 성공")
    except Exception as e:
        print(f"❌ cache_manager 모듈 import 실패: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        print("✅ utils.logger 모듈 import 성공")
    except Exception as e:
        print(f"❌ utils.logger 모듈 import 실패: {e}")
        return False
    
    return True

def test_saju_calculation():
    """사주 계산 테스트"""
    print("\n🔮 사주 계산 테스트 시작...")
    
    try:
        from saju_calculator import calculate_saju
        from datetime import datetime
        
        # 테스트용 생년월일
        test_date = datetime(1992, 4, 20, 11, 50)
        
        result = calculate_saju(test_date)
        
        print(f"✅ 사주 계산 성공")
        print(f"   입력: {test_date}")
        print(f"   결과: {result}")
        
        # 필수 키 확인
        required_keys = ['년주', '월주', '일주', '시주', 'solar', 'lunar']
        for key in required_keys:
            if key in result:
                print(f"   ✅ {key}: {result[key]}")
            else:
                print(f"   ❌ {key} 누락")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 사주 계산 실패: {e}")
        return False

def test_ai_analyzer():
    """AI 분석기 테스트"""
    print("\n🤖 AI 분석기 테스트 시작...")
    
    try:
        from ai_saju_analyzer import AISajuAnalyzer
        
        # 분석기 초기화
        analyzer = AISajuAnalyzer()
        print("✅ AI 분석기 초기화 성공")
        
        # analysis_parts 구조 확인
        if hasattr(analyzer, 'analysis_parts'):
            print(f"✅ analysis_parts 존재: {len(analyzer.analysis_parts)}개 파트")
            
            # 각 파트의 section 구조 확인
            for part_num, part_info in analyzer.analysis_parts.items():
                sections = part_info.get('sections', [])
                print(f"   Part {part_num}: {len(sections)}개 섹션")
                
                for i, section in enumerate(sections):
                    if len(section) == 4:  # (번호, 제목, 최소글자수, 옵션딕셔너리)
                        print(f"     섹션 {i+1}: ✅ 올바른 구조")
                    else:
                        print(f"     섹션 {i+1}: ❌ 잘못된 구조 (길이: {len(section)})")
                        return False
        
        # part_package_mapping 확인
        if hasattr(analyzer, 'part_package_mapping'):
            print(f"✅ part_package_mapping 존재: {len(analyzer.part_package_mapping)}개 파트")
        
        return True
        
    except Exception as e:
        print(f"❌ AI 분석기 테스트 실패: {e}")
        return False

def test_cache_manager():
    """캐시 매니저 테스트"""
    print("\n💾 캐시 매니저 테스트 시작...")
    
    try:
        from cache_manager import CacheManager
        
        # 캐시 매니저 초기화
        cache_manager = CacheManager()
        print("✅ 캐시 매니저 초기화 성공")
        
        # 테스트용 데이터
        test_user_info = {
            'name': '테스트',
            'birthdate': '1992-04-20',
            'birthtime': '11:50',
            'gender': 'male',
            'relationship': 'single',
            'mbti': 'ISTP'
        }
        
        test_saju_result = {
            '년주': '임신',
            '월주': '갑진',
            '일주': '정유',
            '시주': '병오',
            'solar': '1992-04-20 11:50',
            'lunar': '1992년 3월 18일'
        }
        
        # 세션 ID 생성
        session_id = cache_manager.generate_session_id(test_user_info)
        print(f"✅ 세션 ID 생성: {session_id}")
        
        # 사용자 데이터 저장
        cache_manager.save_user_data(session_id, test_saju_result, test_user_info)
        print("✅ 사용자 데이터 저장 성공")
        
        # 사용자 데이터 로드
        loaded_saju, loaded_user = cache_manager.load_user_data(session_id)
        if loaded_saju and loaded_user:
            print("✅ 사용자 데이터 로드 성공")
        else:
            print("❌ 사용자 데이터 로드 실패")
            return False
        
        # 분석 결과 저장/로드 테스트
        test_analysis = {"section_1": "테스트 분석 결과"}
        cache_manager.save_analysis(session_id, 1, test_analysis)
        print("✅ 분석 결과 저장 성공")
        
        loaded_analysis = cache_manager.load_analysis(session_id, 1)
        if loaded_analysis:
            print("✅ 분석 결과 로드 성공")
        else:
            print("❌ 분석 결과 로드 실패")
            return False
        
        # 테스트 데이터 정리
        cache_manager.clear_analysis_cache(session_id)
        print("✅ 테스트 데이터 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 캐시 매니저 테스트 실패: {e}")
        return False

def test_analysis_structure():
    """분석 구조 테스트"""
    print("\n📊 분석 구조 테스트 시작...")
    
    try:
        from ai_saju_analyzer import AISajuAnalyzer
        from main import convert_analysis_results_for_template
        
        analyzer = AISajuAnalyzer()
        
        # 테스트용 분석 결과
        test_results = {
            1: {"section_1": "테스트 섹션 1 내용"},
            2: {"section_1": "테스트 섹션 2 내용", "section_2": "테스트 섹션 2-2 내용"}
        }
        
        # 템플릿 변환 테스트
        analysis_parts = convert_analysis_results_for_template(test_results, analyzer)
        
        print(f"✅ 템플릿 변환 성공: {len(analysis_parts)}개 파트")
        
        for i, part in enumerate(analysis_parts):
            print(f"   파트 {i+1}: {part.get('title', '제목 없음')}")
            sections = part.get('sections', [])
            print(f"     섹션 수: {len(sections)}")
            
            for j, section in enumerate(sections):
                title = section.get('title', '제목 없음')
                content = section.get('content', [])
                print(f"       섹션 {j+1}: {title} (내용 길이: {len(content)})")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 구조 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 사주 분석 시스템 내부 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("모듈 Import", test_imports),
        ("사주 계산", test_saju_calculation),
        ("AI 분석기", test_ai_analyzer),
        ("캐시 매니저", test_cache_manager),
        ("분석 구조", test_analysis_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과")
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 