#!/usr/bin/env python3
"""
재무제표 추출 테스트 스크립트
==========================

수정된 dart-fss API로 실제 재무제표를 추출할 수 있는지 테스트
"""

from config import DART_API_KEY
from korean_airlines_corp_codes import KOREAN_AIRLINES_CORP_MAPPING

try:
    import dart_fss as fss
    from dart_fss import set_api_key
    from dart_fss.fs import extract as fs_extract
    
    print("✅ dart-fss 모듈 로드 성공")
    
    # API 키 설정
    set_api_key(DART_API_KEY)
    print("🔑 API 키 설정 완료")
    
    # 대한항공 2022년 4분기 재무제표 테스트
    corp_code = '00113526'  # 대한항공
    company_name = '대한항공'
    end_date = '20221231'  # 2022년 4분기
    
    print(f"\n📊 {company_name} ({corp_code}) {end_date} 재무제표 추출 테스트")
    print("=" * 60)
    
    # 연결재무제표 시도
    try:
        print("🔍 연결재무제표 추출 시도...")
        fs_data = fs_extract(
            corp_code=corp_code,
            bgn_de='20220101',  # 더 넓은 검색 범위
            end_de=end_date,
            separate=False,  # 연결재무제표 (기본값)
            report_tp='annual',  # 연간 보고서
            lang='ko',  # 한국어
            progressbar=True  # 진행상황 표시
        )
        
        if fs_data is not None and hasattr(fs_data, 'show'):
            print(f"✅ 연결재무제표 추출 성공!")
            
            # FinancialStatement 객체의 데이터 확인
            try:
                # 재무상태표 (Balance Sheet) 확인
                print("📊 재무상태표 (BS) 추출 중...")
                df_bs = fs_data.show('bs')
                print(f"✅ 재무상태표 크기: {df_bs.shape}")
                
                if not df_bs.empty:
                    print(f"📋 재무상태표 컬럼들: {list(df_bs.columns)}")
                    print(f"\n📋 재무상태표 샘플:")
                    print(df_bs.head())
                
                # 손익계산서 (Income Statement) 확인  
                print("\n📊 손익계산서 (IS) 추출 중...")
                df_is = fs_data.show('is')
                print(f"✅ 손익계산서 크기: {df_is.shape}")
                
                if not df_is.empty:
                    print(f"📋 손익계산서 컬럼들: {list(df_is.columns)}")
                    print(f"\n📋 손익계산서 샘플:")
                    print(df_is.head())
                
                # 현금흐름표 (Cash Flow) 확인
                print("\n📊 현금흐름표 (CF) 추출 중...")
                df_cf = fs_data.show('cf')
                print(f"✅ 현금흐름표 크기: {df_cf.shape}")
                
                if not df_cf.empty:
                    print(f"📋 현금흐름표 컬럼들: {list(df_cf.columns)}")
                    print(f"\n📋 현금흐름표 샘플:")
                    print(df_cf.head())
                
            except Exception as e:
                print(f"⚠️ 데이터 표시 실패: {e}")
                print(f"📊 FinancialStatement 객체 타입: {type(fs_data)}")
                print(f"📊 객체 속성들: {[attr for attr in dir(fs_data) if not attr.startswith('_')]}")
                
                # 다른 방법으로 데이터 확인
                try:
                    print("🔍 info 속성 확인:")
                    print(fs_data.info)
                except:
                    pass
            
        else:
            print("❌ 연결재무제표가 비어있음")
            
            # 개별재무제표 시도
            print("🔍 개별재무제표 추출 시도...")
            fs_data = fs_extract(
                corp_code=corp_code,
                bgn_de='20220101',  # 더 넓은 검색 범위
                end_de=end_date,
                separate=True,  # 개별재무제표
                report_tp='annual',  # 연간 보고서
                lang='ko',  # 한국어
                progressbar=True  # 진행상황 표시
            )
            
            if fs_data is not None and hasattr(fs_data, 'show'):
                print(f"✅ 개별재무제표 추출 성공!")
                df = fs_data.show()
                print(f"📊 데이터 크기: {df.shape}")
                print(f"📋 컬럼들: {list(df.columns)}")
            else:
                print("❌ 개별재무제표도 비어있음")
        
    except Exception as e:
        print(f"❌ 재무제표 추출 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 테스트 완료!")
    
except Exception as e:
    print(f"❌ 전체 테스트 실패: {e}")
    import traceback
    traceback.print_exc()