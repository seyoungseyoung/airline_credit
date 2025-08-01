#!/usr/bin/env python3
"""
DART API 테스트 스크립트
=====================

dart-fss의 올바른 사용법을 찾아보는 테스트 스크립트
"""

from config import DART_API_KEY

try:
    import dart_fss as fss
    print("✅ dart-fss 모듈 로드 성공")
    
    # API 키 설정
    fss.set_api_key(DART_API_KEY)
    print("🔑 API 키 설정 완료")
    
    # 사용 가능한 함수들 확인
    print("\n📋 dart_fss 모듈의 주요 속성들:")
    attrs = [attr for attr in dir(fss) if not attr.startswith('_')]
    for attr in attrs[:10]:  # 처음 10개만 출력
        print(f"  - {attr}")
    
    # Company 클래스 테스트
    if hasattr(fss, 'Company'):
        print("\n🏢 Company 클래스 발견")
        
        # 대한항공 테스트 (corp_code: 00113526)
        try:
            print("🔍 대한항공 Company 객체 생성 시도...")
            kal = fss.Company('00113526')
            print(f"✅ 회사명: {kal.corp_name}")
            print(f"✅ 업종: {kal.industry_code}")
            
            # 재무제표 가져오기 테스트
            if hasattr(kal, 'extract_fs'):
                print("📊 재무제표 추출 시도...")
                fs = kal.extract_fs(bgn_de='20231231', end_de='20231231')
                if fs:
                    print(f"✅ 재무제표 추출 성공: {type(fs)}")
                    print(f"📊 크기: {fs.shape if hasattr(fs, 'shape') else 'N/A'}")
                else:
                    print("❌ 재무제표 추출 실패")
            else:
                print("❌ extract_fs 메소드 없음")
                
        except Exception as e:
            print(f"❌ Company 객체 생성 실패: {e}")
    
    # get_corp_list 테스트
    if hasattr(fss, 'get_corp_list'):
        print("\n📋 get_corp_list 함수 발견")
        try:
            print("🔍 기업 리스트 가져오기 시도...")
            corp_list = fss.get_corp_list()
            print(f"✅ 기업 리스트 로드 성공: {len(corp_list.corps)}개 기업")
        except Exception as e:
            print(f"❌ 기업 리스트 로드 실패: {e}")
    
    print("\n🎉 테스트 완료!")
    
except ImportError as e:
    print(f"❌ dart-fss import 실패: {e}")
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")