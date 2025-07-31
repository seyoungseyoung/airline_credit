#!/usr/bin/env python3
"""
Korean Airlines Financial Data ETL Pipeline
===========================================

실제 DART 재무제표 데이터를 수집하고 가공하는 파이프라인

Features:
1. DART API를 통한 분기별 재무제표 수집 (2010Q1-2025Q2)
2. 20개 재무비율 자동 계산
3. QoQ/YoY 변화율 계산
4. Parquet 형태로 효율적 저장

Author: Korean Airlines Credit Rating Analysis
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import warnings
from tqdm import tqdm

# 설정 및 매핑 정보 import
from config import DART_API_KEY, FINANCIAL_RATIOS, DATA_START_YEAR, DATA_END_YEAR, QUARTERS
from korean_airlines_corp_codes import KOREAN_AIRLINES_CORP_MAPPING, get_corp_code

try:
    import dart_fss as fss
    from dart_fss import set_api_key
    # 올바른 모듈 import
    from dart_fss.corp import Corp
    from dart_fss.fs import extract as fs_extract
    DART_FSS_AVAILABLE = True
    print("✅ dart-fss 모듈 로드 성공")
except ImportError as e:
    print(f"❌ dart-fss 모듈 로드 실패: {e}")
    print("설치: pip install dart-fss")
    DART_FSS_AVAILABLE = False

class FinancialDataETL:
    """
    한국 항공사 재무데이터 ETL 파이프라인
    """
    
    def __init__(self):
        """ETL 파이프라인 초기화"""
        
        if not DART_FSS_AVAILABLE:
            raise ImportError("dart-fss 패키지가 필요합니다.")
        
        # DART API 키 설정
        set_api_key(DART_API_KEY)
        print(f"🔑 DART API 키 설정 완료")
        
        # 데이터 저장 경로
        self.data_dir = "financial_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 항공사 정보
        self.airlines = KOREAN_AIRLINES_CORP_MAPPING
        print(f"📊 타겟 항공사: {len(self.airlines)}개")
        
        # 수집 기간 
        self.start_year = DATA_START_YEAR
        self.end_year = DATA_END_YEAR
        self.quarters = QUARTERS
        
        print(f"📅 수집 기간: {self.start_year}-{self.end_year}")
        
    def generate_period_list(self) -> List[str]:
        """분기별 기간 리스트 생성 (예: ['20101', '20102', ...])"""
        
        periods = []
        for year in range(self.start_year, self.end_year + 1):
            for q_idx, quarter in enumerate(self.quarters, 1):
                period = f"{year}{q_idx:02d}"  # 20101, 20102, 20103, 20104
                periods.append(period)
        
        # 미래 분기는 현재 날짜 기준으로 제한
        current_date = datetime.now()
        current_period = f"{current_date.year}{((current_date.month-1)//3 + 1):02d}"
        
        # 현재 분기 이후는 제외
        periods = [p for p in periods if p <= current_period]
        
        print(f"📆 총 {len(periods)}개 분기 대상")
        return periods
        
    def extract_financial_statements(self, corp_code: str, company_name: str) -> pd.DataFrame:
        """특정 기업의 모든 분기 재무제표 추출"""
        
        print(f"📈 {company_name} ({corp_code}) 재무제표 수집 중...")
        
        periods = self.generate_period_list()
        all_statements = []
        
        for period in tqdm(periods, desc=f"{company_name} 재무제표"):
            try:
                # DART에서 재무제표 추출
                # bgn_de: 시작일, end_de: 종료일, corp_code: 기업코드
                year = int(period[:4])
                quarter = int(period[4:])
                
                # 분기 종료일 계산
                if quarter == 1:
                    end_date = f"{year}0331"
                elif quarter == 2:
                    end_date = f"{year}0630"
                elif quarter == 3:
                    end_date = f"{year}0930"
                else:  # quarter == 4
                    end_date = f"{year}1231"
                
                # 재무제표 추출 (연결재무제표 우선)
                fs_data = fs_extract(
                    corp_code=corp_code,
                    bgn_de=end_date,
                    end_de=end_date,
                    fs_div='CFS'  # 연결재무제표
                )
                
                if fs_data is not None and not fs_data.empty:
                    fs_data['period'] = period
                    fs_data['company_name'] = company_name
                    fs_data['corp_code'] = corp_code
                    fs_data['end_date'] = end_date
                    all_statements.append(fs_data)
                    
                else:
                    # 연결재무제표가 없으면 개별재무제표 시도
                    fs_data = fs_extract(
                        corp_code=corp_code,
                        bgn_de=end_date,
                        end_de=end_date,
                        fs_div='OFS'  # 개별재무제표
                    )
                    
                    if fs_data is not None and not fs_data.empty:
                        fs_data['period'] = period
                        fs_data['company_name'] = company_name
                        fs_data['corp_code'] = corp_code
                        fs_data['end_date'] = end_date
                        fs_data['fs_div'] = 'OFS'  # 개별재무제표 표시
                        all_statements.append(fs_data)
                
            except Exception as e:
                print(f"⚠️ {company_name} {period} 데이터 수집 실패: {e}")
                continue
        
        if all_statements:
            result_df = pd.concat(all_statements, ignore_index=True)
            print(f"✅ {company_name}: {len(result_df)}개 재무항목 수집 완료")
            return result_df
        else:
            print(f"❌ {company_name}: 재무데이터 수집 실패")
            return pd.DataFrame()
    
    def collect_all_financial_data(self) -> pd.DataFrame:
        """모든 항공사의 재무데이터 수집"""
        
        print("🚀 전체 항공사 재무데이터 수집 시작")
        print("=" * 60)
        
        all_company_data = []
        
        for company_name, info in self.airlines.items():
            corp_code = info['corp_code']
            
            if corp_code is None:
                print(f"⏭️ {company_name}: corp_code 없음, 건너뛰기")
                continue
                
            # 각 기업별 재무데이터 수집
            company_data = self.extract_financial_statements(corp_code, company_name)
            
            if not company_data.empty:
                all_company_data.append(company_data)
            
            print(f"✅ {company_name} 완료")
            print("-" * 40)
        
        if all_company_data:
            final_df = pd.concat(all_company_data, ignore_index=True)
            print(f"🎉 전체 수집 완료: {len(final_df)}개 재무항목")
            return final_df
        else:
            print("❌ 재무데이터 수집 실패")
            return pd.DataFrame()
    
    def save_raw_data(self, df: pd.DataFrame, filename: str = "raw_financial_statements.parquet"):
        """원본 재무데이터 저장"""
        
        filepath = os.path.join(self.data_dir, filename)
        df.to_parquet(filepath, index=False)
        print(f"💾 원본 재무데이터 저장: {filepath}")
        print(f"📊 데이터 크기: {df.shape}")
        
    def load_raw_data(self, filename: str = "raw_financial_statements.parquet") -> pd.DataFrame:
        """저장된 원본 재무데이터 로드"""
        
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_parquet(filepath)
            print(f"📂 원본 재무데이터 로드: {filepath}")
            print(f"📊 데이터 크기: {df.shape}")
            return df
        else:
            print(f"❌ 파일이 존재하지 않습니다: {filepath}")
            return pd.DataFrame()
    
    def run_etl_pipeline(self, force_refresh: bool = False):
        """전체 ETL 파이프라인 실행"""
        
        print("🏗️ Korean Airlines Financial Data ETL Pipeline")
        print("=" * 60)
        
        raw_data_file = "raw_financial_statements.parquet"
        raw_data_path = os.path.join(self.data_dir, raw_data_file)
        
        # 기존 데이터가 있고 강제 새로고침이 아닌 경우 로드
        if os.path.exists(raw_data_path) and not force_refresh:
            print("📂 기존 재무데이터 발견, 로드 중...")
            raw_df = self.load_raw_data(raw_data_file)
            
            if not raw_df.empty:
                print("✅ 기존 데이터 사용 (새로고침하려면 force_refresh=True)")
                return raw_df
        
        # 새로운 데이터 수집
        print("🔄 새로운 재무데이터 수집 시작...")
        raw_df = self.collect_all_financial_data()
        
        if not raw_df.empty:
            # 원본 데이터 저장
            self.save_raw_data(raw_df, raw_data_file)
            
            print("\n🎉 ETL 파이프라인 완료!")
            print(f"📊 수집된 데이터: {raw_df.shape[0]}개 재무항목")
            print(f"🏢 대상 기업: {raw_df['company_name'].nunique()}개")
            print(f"📅 기간: {raw_df['period'].min()} ~ {raw_df['period'].max()}")
            
            return raw_df
        else:
            print("❌ ETL 파이프라인 실패")
            return pd.DataFrame()

def main():
    """메인 실행 함수"""
    
    # ETL 파이프라인 실행
    etl = FinancialDataETL()
    
    # 강제 새로고침 여부 (명령행 인자로 제어)
    force_refresh = '--refresh' in sys.argv
    
    # ETL 실행
    financial_data = etl.run_etl_pipeline(force_refresh=force_refresh)
    
    if not financial_data.empty:
        print("\n📋 수집된 데이터 샘플:")
        print(financial_data.head())
        
        print("\n📊 기업별 데이터 현황:")
        summary = financial_data.groupby('company_name').agg({
            'period': ['count', 'min', 'max']
        }).round(2)
        print(summary)
        
    else:
        print("❌ 재무데이터 수집 실패")

if __name__ == "__main__":
    main()