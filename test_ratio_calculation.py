#!/usr/bin/env python3
"""
재무비율 계산 통합 테스트
======================

실제 DART 데이터로 재무비율 계산을 테스트하는 스크립트
"""

import pandas as pd
import numpy as np

from config import DART_API_KEY
from korean_airlines_corp_codes import KOREAN_AIRLINES_CORP_MAPPING
from financial_ratio_calculator import FinancialRatioCalculator

try:
    import dart_fss as fss
    from dart_fss import set_api_key
    from dart_fss.fs import extract as fs_extract
    
    print("✅ 모든 모듈 로드 성공")
    
    # API 키 설정
    set_api_key(DART_API_KEY)
    print("🔑 API 키 설정 완료")
    
    # 재무비율 계산기 초기화
    calculator = FinancialRatioCalculator()
    
    # 대한항공 2022년 재무제표로 테스트
    corp_code = '00113526'  # 대한항공
    company_name = '대한항공'
    
    print(f"\n🚀 {company_name} 재무비율 계산 테스트")
    print("=" * 50)
    
    # 1. 재무제표 추출
    print("📊 재무제표 추출 중...")
    fs_data = fs_extract(
        corp_code=corp_code,
        bgn_de='20220101',
        end_de='20221231',
        separate=False,  # 연결재무제표
        report_tp='annual',  # 연간 보고서
        lang='ko',
        progressbar=True
    )
    
    if fs_data is not None:
        print("✅ 재무제표 추출 성공!")
        
        # 2. 재무비율 계산
        print("\n🧮 재무비율 계산 시작...")
        ratios = calculator.process_company_financial_data(fs_data)
        
        # 3. 결과 출력
        print(f"\n📊 {company_name} 2022년 재무비율 결과:")
        print("=" * 60)
        
        if ratios:
            for ratio_key, ratio_name in calculator.ratio_definitions.items():
                value = ratios.get(ratio_key)
                if value is not None and not pd.isna(value):
                    if 'ratio' in ratio_key or 'margin' in ratio_key or 'growth' in ratio_key:
                        # 비율/마진/성장률은 퍼센트로 표시
                        print(f"{ratio_name:15} ({ratio_key:20}): {value:8.2%}")
                    elif 'coverage' in ratio_key or 'turnover' in ratio_key:
                        # 배율/회전율은 소수점 2자리
                        print(f"{ratio_name:15} ({ratio_key:20}): {value:8.2f}배")
                    else:
                        # 일반 비율
                        print(f"{ratio_name:15} ({ratio_key:20}): {value:8.2f}")
                else:
                    print(f"{ratio_name:15} ({ratio_key:20}): {'N/A':>8}")
            
            # 계산된 비율 통계
            valid_ratios = [v for v in ratios.values() if v is not None and not pd.isna(v)]
            print(f"\n📈 계산 결과 요약:")
            print(f"  - 총 계산 가능 비율: {len(valid_ratios)}개 / {len(calculator.ratio_definitions)}개")
            print(f"  - 계산 성공률: {len(valid_ratios)/len(calculator.ratio_definitions)*100:.1f}%")
            
            # 주요 비율 해석
            print(f"\n💡 주요 재무지표 해석:")
            
            if ratios.get('debt_to_assets'):
                debt_ratio = ratios['debt_to_assets']
                status = "양호" if debt_ratio < 0.6 else "주의" if debt_ratio < 0.8 else "위험"
                print(f"  - 부채비율 {debt_ratio:.1%}: {status} 수준")
            
            if ratios.get('current_ratio'):
                current_ratio = ratios['current_ratio']
                status = "양호" if current_ratio > 1.5 else "보통" if current_ratio > 1.0 else "주의"
                print(f"  - 유동비율 {current_ratio:.2f}: {status} 수준")
            
            if ratios.get('roa'):
                roa = ratios['roa']
                status = "우수" if roa > 0.05 else "양호" if roa > 0.02 else "보통" if roa > 0 else "적자"
                print(f"  - 총자산수익률 {roa:.2%}: {status} 수준")
            
            if ratios.get('roe'):
                roe = ratios['roe']
                status = "우수" if roe > 0.15 else "양호" if roe > 0.10 else "보통" if roe > 0 else "적자"
                print(f"  - 자기자본수익률 {roe:.2%}: {status} 수준")
        
        else:
            print("❌ 재무비율 계산 실패")
    
    else:
        print("❌ 재무제표 추출 실패")
    
    print(f"\n🎉 테스트 완료!")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()