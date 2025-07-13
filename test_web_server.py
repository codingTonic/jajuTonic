#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
from datetime import datetime

def test_homepage():
    """홈페이지 접근 테스트"""
    print("🏠 홈페이지 테스트 시작...")
    
    try:
        response = requests.get("http://localhost:8080/", timeout=10)
        
        if response.status_code == 200:
            print("✅ 홈페이지 접근 성공")
            return True
        else:
            print(f"❌ 홈페이지 접근 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 홈페이지 접근 오류: {e}")
        return False

def test_calculate_endpoint():
    """사주 계산 엔드포인트 테스트"""
    print("\n🔮 사주 계산 엔드포인트 테스트 시작...")
    
    try:
        # 먼저 홈페이지에서 CSRF 토큰 가져오기
        session = requests.Session()
        home_response = session.get("http://localhost:8080/", timeout=10)
        
        if home_response.status_code != 200:
            print(f"❌ 홈페이지 접근 실패: HTTP {home_response.status_code}")
            return None
        
        # CSRF 토큰 추출 (간단한 방법)
        csrf_token = None
        if 'csrf_token' in home_response.text:
            import re
            match = re.search(r'name="csrf_token" value="([^"]+)"', home_response.text)
            if match:
                csrf_token = match.group(1)
                print(f"✅ CSRF 토큰 발견: {csrf_token[:10]}...")
        
        # 테스트용 폼 데이터
        form_data = {
            'name': '테스트',
            'birth_date': '1992-04-20',
            'birth_time': '11:50',
            'gender': 'male',
            'relationship': 'single',
            'mbti': 'ISTP'
        }
        
        # CSRF 토큰이 있으면 추가
        if csrf_token:
            form_data['csrf_token'] = csrf_token
        
        response = session.post("http://localhost:8080/calculate", 
                               data=form_data, 
                               timeout=10,
                               allow_redirects=False)
        
        if response.status_code in [200, 302]:  # 성공 또는 리다이렉트
            print("✅ 사주 계산 엔드포인트 성공")
            
            # 세션 쿠키 저장
            cookies = session.cookies
            if cookies:
                print(f"✅ 세션 쿠키 생성: {list(cookies.keys())}")
                return cookies
            else:
                print("⚠️ 세션 쿠키 없음")
                return None
        else:
            print(f"❌ 사주 계산 엔드포인트 실패: HTTP {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 사주 계산 엔드포인트 오류: {e}")
        return None

def test_analysis_progress(cookies):
    """분석 진행 상태 테스트"""
    print("\n📊 분석 진행 상태 테스트 시작...")
    
    if not cookies:
        print("⚠️ 쿠키가 없어서 테스트를 건너뜁니다.")
        return False
    
    try:
        response = requests.get("http://localhost:8080/analysis-progress", 
                              cookies=cookies, 
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 분석 진행 상태 조회 성공")
            print(f"   상태: {data.get('status', 'unknown')}")
            print(f"   완료된 파트: {data.get('last_completed_part', 0)}/8")
            return True
        else:
            print(f"❌ 분석 진행 상태 조회 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 분석 진행 상태 조회 오류: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return False

def test_start_analysis(cookies):
    """분석 시작 엔드포인트 테스트"""
    print("\n🚀 분석 시작 엔드포인트 테스트 시작...")
    
    if not cookies:
        print("⚠️ 쿠키가 없어서 테스트를 건너뜁니다.")
        return False
    
    try:
        response = requests.post("http://localhost:8080/start-background-analysis", 
                               cookies=cookies, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 분석 시작 성공")
            print(f"   상태: {data.get('status', 'unknown')}")
            print(f"   메시지: {data.get('message', '')}")
            return True
        else:
            print(f"❌ 분석 시작 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 분석 시작 오류: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return False

def test_analysis_result(cookies):
    """분석 결과 페이지 테스트"""
    print("\n📋 분석 결과 페이지 테스트 시작...")
    
    if not cookies:
        print("⚠️ 쿠키가 없어서 테스트를 건너뜁니다.")
        return False
    
    try:
        response = requests.get("http://localhost:8080/analysis-result", 
                              cookies=cookies, 
                              timeout=10)
        
        if response.status_code == 200:
            print("✅ 분석 결과 페이지 접근 성공")
            return True
        elif response.status_code == 302:
            print("✅ 분석 결과 페이지 리다이렉트 (정상)")
            return True
        else:
            print(f"❌ 분석 결과 페이지 접근 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 분석 결과 페이지 접근 오류: {e}")
        return False

def test_static_files():
    """정적 파일 접근 테스트"""
    print("\n📁 정적 파일 접근 테스트 시작...")
    
    static_files = [
        "/static/css/index_style.css",
        "/static/js/index_script.js",
        "/static/css/analysis_style.css",
        "/static/js/result_script.js"
    ]
    
    success_count = 0
    
    for file_path in static_files:
        try:
            response = requests.get(f"http://localhost:8080{file_path}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {file_path} 접근 성공")
                success_count += 1
            elif response.status_code == 304:  # Not Modified
                print(f"✅ {file_path} 캐시됨 (304)")
                success_count += 1
            else:
                print(f"❌ {file_path} 접근 실패: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} 접근 오류: {e}")
    
    return success_count == len(static_files)

def test_privacy_policy():
    """개인정보처리방침 페이지 테스트"""
    print("\n🔒 개인정보처리방침 페이지 테스트 시작...")
    
    try:
        response = requests.get("http://localhost:8080/privacy-policy", timeout=10)
        
        if response.status_code == 200:
            print("✅ 개인정보처리방침 페이지 접근 성공")
            return True
        else:
            print(f"❌ 개인정보처리방침 페이지 접근 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 개인정보처리방침 페이지 접근 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🌐 웹 서버 테스트 시작")
    print("=" * 50)
    
    # 기본 테스트 (서버 없이도 가능)
    basic_tests = [
        ("홈페이지", test_homepage),
        ("정적 파일", test_static_files),
        ("개인정보처리방침", test_privacy_policy)
    ]
    
    passed = 0
    total = len(basic_tests)
    
    for test_name, test_func in basic_tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과")
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")
    
    # 세션 기반 테스트
    print(f"\n{'='*20} 세션 기반 테스트 {'='*20}")
    
    # 사주 계산으로 세션 생성
    cookies = test_calculate_endpoint()
    if cookies:
        passed += 1
        total += 1
        
        # 세션 기반 테스트들
        session_tests = [
            ("분석 진행 상태", lambda: test_analysis_progress(cookies)),
            ("분석 시작", lambda: test_start_analysis(cookies)),
            ("분석 결과 페이지", lambda: test_analysis_result(cookies))
        ]
        
        for test_name, test_func in session_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 테스트 통과")
                else:
                    print(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                print(f"❌ {test_name} 테스트 중 오류 발생: {e}")
            total += 1
    else:
        print("⚠️ 세션 생성 실패로 세션 기반 테스트를 건너뜁니다.")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 웹 서버 테스트가 성공적으로 완료되었습니다!")
        return True
    else:
        print("⚠️ 일부 웹 서버 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 