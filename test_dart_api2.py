#!/usr/bin/env python3
"""
DART API 상세 테스트 스크립트
==========================

dart-fss의 올바른 재무제표 추출 방법을 찾는 스크립트
"""

from config import DART_API_KEY

try:
    import dart_fss as fss
    print("✅ dart-fss 모듈 로드 성공")
    
    # API 키 설정
    fss.set_api_key(DART_API_KEY)
    print("🔑 API 키 설정 완료")
    
    # corp 모듈 테스트
    if hasattr(fss, 'corp'):
        print("\n🏢 dart_fss.corp 모듈 테스트")
        corp_attrs = [attr for attr in dir(fss.corp) if not attr.startswith('_')]
        print(f"corp 모듈 속성들: {corp_attrs}")
        
        # Company 클래스가 corp 모듈에 있는지 확인
        if hasattr(fss.corp, 'Company'):
            try:
                print("🔍 대한항공 Company 객체 생성 시도...")
                kal = fss.corp.Company('00113526')
                print(f"✅ 회사명: {kal.corp_name if hasattr(kal, 'corp_name') else 'N/A'}")
                
                # 재무제표 메소드 확인
                company_methods = [method for method in dir(kal) if not method.startswith('_')]
                print(f"Company 객체 메소드들: {company_methods[:10]}")
                
                # 재무제표 추출 시도
                if hasattr(kal, 'extract_fs'):
                    print("📊 재무제표 추출 시도...")
                    fs = kal.extract_fs(bgn_de='20231231', end_de='20231231')
                    if fs is not None:
                        print(f"✅ 재무제표 추출 성공: {type(fs)}")
                    else:
                        print("❌ 재무제표가 None")
                
            except Exception as e:
                print(f"❌ Company 객체 생성 실패: {e}")
        
    # extract 모듈 테스트 
    if hasattr(fss, 'extract'):
        print("\n📊 dart_fss.extract 모듈 테스트")
        extract_attrs = [attr for attr in dir(fss.extract) if not attr.startswith('_')]
        print(f"extract 모듈 속성들: {extract_attrs}")
        
        # finstate 함수가 있는지 확인
        if hasattr(fss.extract, 'finstate'):
            try:
                print("🔍 finstate 함수로 재무제표 추출 시도...")
                fs = fss.extract.finstate(
                    corp_code='00113526',
                    bgn_de='20231231',
                    end_de='20231231'
                )
                if fs is not None:
                    print(f"✅ 재무제표 추출 성공: {type(fs)}")
                    if hasattr(fs, 'shape'):
                        print(f"📊 크기: {fs.shape}")
                else:
                    print("❌ 재무제표가 None")
            except Exception as e:
                print(f"❌ finstate 함수 실패: {e}")
    
    # fs 모듈 테스트
    if hasattr(fss, 'fs'):
        print("\n📈 dart_fss.fs 모듈 테스트")
        fs_attrs = [attr for attr in dir(fss.fs) if not attr.startswith('_')]
        print(f"fs 모듈 속성들: {fs_attrs}")
    
    print("\n🎉 상세 테스트 완료!")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()