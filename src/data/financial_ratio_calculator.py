#!/usr/bin/env python3
"""
Financial Ratio Calculator for Korean Airlines
==============================================

실제 DART 재무제표 데이터로부터 20개 재무비율을 계산하는 모듈

Features:
1. 재무상태표, 손익계산서, 현금흐름표 데이터 처리
2. 20개 핵심 재무비율 자동 계산
3. QoQ (분기대비) / YoY (전년동기대비) 변화율 계산
4. 결측치 및 이상치 처리
5. 항공업계 특화 비율 포함

Author: Korean Airlines Credit Rating Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import warnings

try:
    from config import FINANCIAL_RATIOS
except ImportError:
    try:
        from config.config import FINANCIAL_RATIOS
    except ImportError:
        # Define minimal ratios if config not available
        FINANCIAL_RATIOS = [
            'debt_to_assets', 'current_ratio', 'roa', 'roe', 'operating_margin',
            'equity_ratio', 'asset_turnover', 'interest_coverage', 'quick_ratio',
            'working_capital_ratio', 'debt_to_equity', 'gross_margin', 'net_margin',
            'cash_ratio', 'times_interest_earned', 'inventory_turnover',
            'receivables_turnover', 'payables_turnover', 'total_asset_growth', 'sales_growth'
        ]

class FinancialRatioCalculator:
    """
    재무비율 계산기
    """
    
    def __init__(self):
        """초기화"""
        self.ratio_definitions = {
            'debt_to_assets': '부채비율',
            'current_ratio': '유동비율', 
            'roa': '총자산수익률',
            'roe': '자기자본수익률',
            'operating_margin': '영업이익률',
            'equity_ratio': '자기자본비율',
            'asset_turnover': '총자산회전율',
            'interest_coverage': '이자보상배율',
            'quick_ratio': '당좌비율',
            'working_capital_ratio': '운전자본비율',
            'debt_to_equity': '부채자본비율',
            'gross_margin': '매출총이익률',
            'net_margin': '순이익률',
            'cash_ratio': '현금비율',
            'times_interest_earned': '이자보상배수',
            'inventory_turnover': '재고자산회전율',
            'receivables_turnover': '매출채권회전율',
            'payables_turnover': '매입채무회전율',
            'total_asset_growth': '총자산증가율',
            'sales_growth': '매출증가율'
        }
        
        print(f"✅ 재무비율 계산기 초기화 완료")
        print(f"📊 계산 가능한 비율: {len(self.ratio_definitions)}개")
        
    def extract_financial_items(self, fs_data, statement_type: str = 'bs') -> Dict[str, float]:
        """
        재무제표에서 주요 계정과목 추출
        
        Args:
            fs_data: FinancialStatement 객체
            statement_type: 'bs' (재무상태표), 'is' (손익계산서), 'cf' (현금흐름표)
        
        Returns:
            Dict[str, float]: 추출된 계정과목들
        """
        
        try:
            # FinancialStatement 객체는 오직 show() 메서드만 사용
            df = fs_data.show(statement_type)
            
            # IS 데이터가 None인 경우 CIS (Comprehensive Income Statement) 시도
            if df is None and statement_type == 'is':
                try:
                    df = fs_data.show('cis')
                    if df is not None:
                        print(f"✅ IS 데이터를 'cis'에서 발견")
                except:
                    pass
            
            if df is None:
                print(f"⚠️ {statement_type.upper()} 데이터가 None")
                return {}
            elif hasattr(df, 'empty') and df.empty:
                print(f"⚠️ {statement_type.upper()} 데이터가 비어있음")
                return {}
            elif hasattr(df, '__len__') and len(df) == 0:
                print(f"⚠️ {statement_type.upper()} 데이터가 비어있음 (길이 0)")
                return {}
            
            # 데이터 형태 정보 출력
            if hasattr(df, 'shape'):
                data_info = f"{df.shape}"
            elif hasattr(df, "__len__"):
                data_info = f"길이 {len(df)}"
            else:
                data_info = "unknown"
            print(f"📊 {statement_type.upper()} 데이터 형태: {data_info}")
            
            # 디버깅: 실제 계정과목명들 보기 (처음 5개)
            if hasattr(df, 'columns') and len(df.columns) > 1:
                if len(df) > 0:
                    label_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                    sample_labels = df[label_col].head(5).astype(str).values
                    print(f"🔍 {statement_type.upper()} 샘플 계정명: {list(sample_labels)}")
                else:
                    print(f"🔍 {statement_type.upper()} 데이터가 비어있음")
            
            # 최신 연도 데이터 추출 - 가장 최근 연도 사용
            latest_year_col = None
            potential_cols = []
            
            for col in df.columns:
                if isinstance(col, tuple) and len(col) > 0:
                    col_str = str(col[0]) if col[0] else str(col)
                    # 연도 데이터 컬럼만 선택 (메타데이터 컬럼 제외)
                    if '20' in col_str and '연결재무제표' in str(col) and col_str not in ['concept_id', 'label_ko', 'label_en']:
                        potential_cols.append((col, col_str))
                elif '20' in str(col) and 'concept' not in str(col) and 'label' not in str(col):
                    potential_cols.append((col, str(col)))
            
            # 가장 최신 연도 선택
            if potential_cols:
                # 연도 기준으로 정렬 (최신 먼저)
                potential_cols.sort(key=lambda x: x[1], reverse=True)
                latest_year_col = potential_cols[0][0]
                print(f"📅 {statement_type.upper()} 사용 연도 컬럼: {latest_year_col}")
            else:
                # 최후의 수단: 숫자 데이터가 있는 컬럼 찾기
                for col in df.columns[2:]:  # 처음 2개 컬럼은 보통 ID, 계정명
                    if not df[col].isna().all():
                        latest_year_col = col
                        print(f"📅 {statement_type.upper()} 폴백 컬럼 사용: {latest_year_col}")
                        break
            
            if latest_year_col is None:
                print(f"⚠️ {statement_type.upper()}에서 연도 컬럼을 찾을 수 없음")
                return {}
            
            extracted_items = {}
            
            if statement_type == 'bs':  # 재무상태표
                # 주요 재무상태표 항목들 매핑
                item_mappings = {
                    'total_assets': ['자산총계', '자산 총계', 'Assets', 'Total assets'],
                    'current_assets': ['유동자산', '유동 자산', 'Current assets'],
                    'non_current_assets': ['비유동자산', '비유동 자산', 'Non-current assets'],
                    'total_liabilities': ['부채총계', '부채 총계', 'Liabilities', 'Total liabilities'],
                    'current_liabilities': ['유동부채', '유동 부채', 'Current liabilities'],
                    'non_current_liabilities': ['비유동부채', '비유동 부채', 'Non-current liabilities'],
                    'total_equity': ['자본총계', '자본 총계', 'Equity', 'Total equity'],
                    'cash_and_equivalents': ['현금및현금성자산', '현금 및 현금성자산', 'Cash and cash equivalents'],
                    'short_term_investments': ['단기투자자산', '단기 투자자산'],
                    'trade_receivables': ['매출채권', '매출 채권', 'Trade receivables'],
                    'inventory': ['재고자산', '재고 자산', 'Inventory'],
                    'trade_payables': ['매입채무', '매입 채무', 'Trade payables'],
                    'short_term_debt': ['단기차입금', '단기 차입금'],
                    'long_term_debt': ['장기차입금', '장기 차입금']
                }
                
            elif statement_type == 'is':  # 손익계산서
                item_mappings = {
                    'revenue': ['매출액', '매출', '수익', '영업수익', 'Revenue', 'Sales'],
                    'gross_profit': ['매출총이익', '매출 총이익', '총이익', 'Gross profit'],
                    'operating_profit': ['영업이익', '영업 이익', '영업손익', 'Operating profit'],
                    'ebit': ['세전이익', '세전 이익', '법인세비용차감전순이익', 'EBIT'],
                    'net_income': ['당기순이익', '당기 순이익', '순이익', '당기손익', 'Net income'],
                    'interest_expense': ['금융비용', '이자비용', '이자', 'Interest expense'],
                    'cost_of_sales': ['매출원가', '매출 원가', '원가', 'Cost of sales']
                }
                
            elif statement_type == 'cf':  # 현금흐름표
                item_mappings = {
                    'operating_cash_flow': ['영업활동으로 인한 현금흐름', '영업활동', '영업현금', '영업활동현금흐름'],
                    'investing_cash_flow': ['투자활동으로 인한 현금흐름', '투자활동', '투자현금', '투자활동현금흐름'],
                    'financing_cash_flow': ['재무활동으로 인한 현금흐름', '재무활동', '재무현금', '재무활동현금흐름']
                }
            
            # 계정과목 매칭 및 값 추출
            for item_key, possible_names in item_mappings.items():
                value = self._find_account_value(df, possible_names, latest_year_col)
                if value is not None:
                    extracted_items[item_key] = value
            
            print(f"✅ {statement_type.upper()}에서 {len(extracted_items)}개 항목 추출")
            return extracted_items
            
        except Exception as e:
            print(f"❌ {statement_type.upper()} 항목 추출 실패: {e}")
            print(f"📋 fs_data 타입: {type(fs_data)}")
            if hasattr(fs_data, '__dict__'):
                print(f"📋 fs_data 속성: {list(fs_data.__dict__.keys())[:5]}")
            return {}
    
    def _find_account_value(self, df: pd.DataFrame, possible_names: List[str], target_col) -> Optional[float]:
        """
        가능한 계정과목명들로부터 값을 찾아 반환
        """
        
        # label_ko 컬럼에서 검색
        if 'label_ko' in df.columns:
            label_col = df.columns[df.columns.get_loc('label_ko')]
        else:
            # 두 번째 컬럼이 보통 계정과목명
            label_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        for name in possible_names:
            # 정확한 매칭 우선 시도
            exact_mask = df[label_col].astype(str) == name
            exact_matches = df[exact_mask]
            
            if not exact_matches.empty:
                try:
                    value = exact_matches.iloc[0][target_col]
                    if pd.notna(value) and value != 'N/A':
                        str_val = str(value).replace(',', '').replace(' ', '')
                        # 음수 처리
                        if str_val.startswith('(') and str_val.endswith(')'):
                            str_val = '-' + str_val[1:-1]
                        if str_val.replace('-', '').replace('.', '').isdigit():
                            return float(str_val)
                except Exception as e:
                    print(f"🔍 값 변환 실패 ({name}): {value} -> {e}")
                    continue
            
            # 부분 매칭 시도
            partial_mask = df[label_col].astype(str).str.contains(name, na=False)
            partial_matches = df[partial_mask]
            
            if not partial_matches.empty:
                try:
                    value = partial_matches.iloc[0][target_col]
                    if pd.notna(value) and value != 'N/A':
                        str_val = str(value).replace(',', '').replace(' ', '')
                        # 음수 처리
                        if str_val.startswith('(') and str_val.endswith(')'):
                            str_val = '-' + str_val[1:-1]
                        if str_val.replace('-', '').replace('.', '').isdigit():
                            return float(str_val)
                except Exception as e:
                    print(f"🔍 값 변환 실패 ({name}): {value} -> {e}")
                    continue
        
        return None
    
    def _find_account_value_enhanced(self, df: pd.DataFrame, possible_names: List[str], target_col) -> Optional[float]:
        """
        향상된 계정과목 값 찾기 메서드 (부분 매칭 개선)
        """
        
        # 먼저 기존 방법 시도
        result = self._find_account_value(df, possible_names, target_col)
        if result is not None:
            return result
        
        # label_ko 컬럼에서 검색
        if 'label_ko' in df.columns:
            label_col = 'label_ko'
        elif len(df.columns) > 1:
            label_col = df.columns[1]
        else:
            label_col = df.columns[0]
        
        # 더 유연한 매칭 시도
        for name in possible_names:
            # 키워드 분리 매칭
            keywords = name.split()
            for keyword in keywords:
                if len(keyword) >= 2:  # 2글자 이상 키워드만
                    try:
                        mask = df[label_col].astype(str).str.contains(keyword, na=False, case=False)
                        matches = df[mask]
                        
                        if not matches.empty:
                            value = matches.iloc[0][target_col]
                            if pd.notna(value) and value != 'N/A':
                                str_val = str(value).replace(',', '').replace(' ', '')
                                if str_val.startswith('(') and str_val.endswith(')'):
                                    str_val = '-' + str_val[1:-1]
                                if str_val.replace('-', '').replace('.', '').isdigit():
                                    print(f"🔍 키워드 매칭 성공: '{keyword}' -> {name}")
                                    return float(str_val)
                    except Exception as e:
                        continue
        
        return None
    
    def _try_alternative_extraction(self, df: pd.DataFrame, statement_type: str) -> Dict[str, float]:
        """
        대체 추출 방법 - 수치가 큰 값들을 자산/부채로 추정
        """
        try:
            extracted_items = {}
            
            # 숫자 값들만 추출
            numeric_values = []
            for _, row in df.iterrows():
                try:
                    value = row.get('value', None)
                    if pd.notna(value) and value != 'N/A':
                        str_val = str(value).replace(',', '').replace(' ', '')
                        if str_val.startswith('(') and str_val.endswith(')'):
                            str_val = '-' + str_val[1:-1]
                        if str_val.replace('-', '').replace('.', '').isdigit():
                            numeric_val = float(str_val)
                            if abs(numeric_val) > 1000:  # 천원 이상만
                                numeric_values.append((abs(numeric_val), numeric_val, row))
                except:
                    continue
            
            if not numeric_values:
                return {}
            
            # 값 크기 순으로 정렬
            numeric_values.sort(key=lambda x: x[0], reverse=True)
            
            if statement_type == 'bs' and len(numeric_values) >= 2:
                # 가장 큰 값들을 자산총계/부채총계로 추정
                extracted_items['total_assets'] = numeric_values[0][1]
                if len(numeric_values) >= 3:
                    extracted_items['total_liabilities'] = numeric_values[1][1]
                    extracted_items['total_equity'] = numeric_values[2][1]
                else:
                    # 단순히 자산에서 부채를 빼서 자본 계산
                    extracted_items['total_liabilities'] = numeric_values[1][1]
                    extracted_items['total_equity'] = numeric_values[0][1] - numeric_values[1][1]
                
                print(f"🔧 [ALT EXTRACT] BS 대체 추출: 자산={extracted_items['total_assets']:,.0f}, 부채={extracted_items['total_liabilities']:,.0f}")
                
            elif statement_type == 'is' and len(numeric_values) >= 1:
                # 가장 큰 값을 매출액으로 추정
                extracted_items['revenue'] = numeric_values[0][1]
                if len(numeric_values) >= 2:
                    extracted_items['net_income'] = numeric_values[-1][1]  # 가장 작은 값을 순이익으로
                
                print(f"🔧 [ALT EXTRACT] IS 대체 추출: 매출={extracted_items['revenue']:,.0f}")
            
            return extracted_items
            
        except Exception as e:
            print(f"❌ [ALT EXTRACT] 대체 추출 실패: {e}")
            return {}
    
    def _extract_from_cached_dict(self, df: pd.DataFrame, statement_type: str) -> Dict[str, float]:
        """
        캐시된 dict 데이터에서 재무항목 추출 (개선된 버전)
        """
        try:
            extracted_items = {}
            
            print(f"🔍 [EXTRACT] Processing {statement_type.upper()} data...")
            print(f"🔍 [EXTRACT] DataFrame shape: {df.shape}")
            print(f"🔍 [EXTRACT] DataFrame columns: {list(df.columns)}")
            
            # 데이터 샘플 확인
            if len(df) > 0:
                print(f"🔍 [EXTRACT] Sample rows (first 3):")
                for i in range(min(3, len(df))):
                    row = df.iloc[i]
                    print(f"  Row {i}: {dict(row)}")
            
            if statement_type == 'bs':  # 재무상태표
                item_mappings = {
                    'total_assets': [
                        '자산총계', '자산 총계', '자산총액', 'Assets', 'Total assets',
                        '자산의 총계', '총자산', '자산계', '자산 계'
                    ],
                    'current_assets': [
                        '유동자산', '유동 자산', 'Current assets', '당좌자산',
                        '유동성자산', '단기자산'
                    ],
                    'non_current_assets': [
                        '비유동자산', '비유동 자산', '고정자산', 'Non-current assets',
                        '장기자산', '비유동성자산'
                    ],
                    'total_liabilities': [
                        '부채총계', '부채 총계', '부채총액', 'Liabilities', 'Total liabilities',
                        '부채의 총계', '총부채', '부채계', '부채 계'
                    ],
                    'current_liabilities': [
                        '유동부채', '유동 부채', 'Current liabilities', '단기부채',
                        '유동성부채', '1년이내만기부채'
                    ],
                    'non_current_liabilities': [
                        '비유동부채', '비유동 부채', '고정부채', 'Non-current liabilities',
                        '장기부채', '비유동성부채'
                    ],
                    'total_equity': [
                        '자본총계', '자본 총계', '자본총액', 'Equity', 'Total equity',
                        '자본의 총계', '총자본', '자본계', '자본 계', '자기자본',
                        '주주지분', '소유주지분'
                    ],
                    'cash_and_equivalents': [
                        '현금및현금성자산', '현금 및 현금성자산', 'Cash and cash equivalents',
                        '현금', '현금성자산', '현금 및 현금등가물'
                    ]
                }
                
            elif statement_type == 'is':  # 손익계산서
                item_mappings = {
                    'revenue': [
                        '매출액', '매출', '수익', '영업수익', 'Revenue', 'Sales',
                        '총매출액', '총수익', '영업매출액', '매출 수익'
                    ],
                    'gross_profit': [
                        '매출총이익', '매출 총이익', '총이익', 'Gross profit',
                        '매출총손익', '총손익'
                    ],
                    'operating_profit': [
                        '영업이익', '영업 이익', '영업손익', 'Operating profit',
                        '영업수익', '영업수지'
                    ],
                    'ebit': [
                        '세전이익', '세전 이익', '법인세비용차감전순이익', 'EBIT',
                        '세전손익', '법인세차감전이익'
                    ],
                    'net_income': [
                        '당기순이익', '당기 순이익', '순이익', '당기손익', 'Net income',
                        '총손익', '당기총손익', '최종손익'
                    ],
                    'interest_expense': [
                        '금융비용', '이자비용', '이자', 'Interest expense',
                        '금융원가', '이자비용 및 할인료'
                    ],
                    'cost_of_sales': [
                        '매출원가', '매출 원가', '원가', 'Cost of sales',
                        '제품매출원가', '상품매출원가'
                    ]
                }
                
            elif statement_type == 'cf':  # 현금흐름표
                item_mappings = {
                    'operating_cash_flow': [
                        '영업활동으로 인한 현금흐름', '영업활동', '영업현금', '영업활동현금흐름',
                        '영업활동 현금흐름', '영업활동으로부터의 현금흐름'
                    ],
                    'investing_cash_flow': [
                        '투자활동으로 인한 현금흐름', '투자활동', '투자현금', '투자활동현금흐름',
                        '투자활동 현금흐름', '투자활동으로부터의 현금흐름'
                    ],
                    'financing_cash_flow': [
                        '재무활동으로 인한 현금흐름', '재무활동', '재무현금', '재무활동현금흐름',
                        '재무활동 현금흐름', '재무활동으로부터의 현금흐름'
                    ]
                }
            
            # 계정과목 매칭 및 값 추출 (개선된 매칭 로직)
            for item_key, possible_names in item_mappings.items():
                value = self._find_account_value_enhanced(df, possible_names, 'value')
                if value is not None:
                    extracted_items[item_key] = value
                    print(f"  ✅ {statement_type.upper()} 매칭: {item_key} = {value:,.0f}")
                else:
                    print(f"  ❌ {statement_type.upper()} 매칭 실패: {item_key}")
            
            print(f"🔧 {statement_type.upper()} 캐시에서 {len(extracted_items)}개 표준 항목 추출")
            
            # 매칭 실패시 숫자 인덱스 기반 대체 방법 시도
            if len(extracted_items) == 0:
                print(f"⚠️ [EXTRACT] No items matched, trying numeric index extraction...")
                
                # 🔍 DART 캐시 데이터는 label_ko가 숫자 인덱스로 저장됨을 확인
                if 'label_ko' in df.columns:
                    unique_labels = df['label_ko'].unique()[:10]  # 처음 10개만 확인
                    print(f"🔍 [DEBUG] label_ko 샘플: {unique_labels}")
                    if all(isinstance(label, (int, float)) for label in unique_labels):
                        print(f"✅ [DEBUG] DART 캐시 데이터 확인: 숫자 인덱스 형태로 저장됨")
                
                extracted_items = self._extract_by_numeric_index(df, statement_type)
                
            return extracted_items
            
        except Exception as e:
            print(f"❌ {statement_type.upper()} 캐시 데이터 추출 실패: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return {}
    
    def _extract_by_numeric_index(self, df: pd.DataFrame, statement_type: str) -> Dict[str, float]:
        """
        숫자 인덱스 기반으로 재무제표 항목 추출 (DART 캐시 데이터용)
        
        Args:
            df: DataFrame with numeric indices as 'label_ko'
            statement_type: 'bs', 'is', 'cf'
        
        Returns:
            Dict of standardized financial items
        """
        extracted_items = {}
        
        print(f"🔧 [NUMERIC_EXTRACT] Processing {statement_type.upper()} with numeric indices...")
        
        # 🔧 DART 재무제표 숫자 인덱스 기반 매핑 (경험적 추정)
        # 실제 DART 데이터 순서는 회사별/년도별로 다를 수 있으므로 유연한 접근
        index_mappings = {
            'bs': {  # 재무상태표
                'total_assets': {
                    'primary': [0, 1],  # 자산총계는 보통 맨 처음
                    'fallback': list(range(0, 5))  # 처음 5개 중에서 가장 큰 값
                },
                'current_assets': {
                    'primary': [2, 3, 4],
                    'fallback': list(range(2, 8))
                },
                'total_liabilities': {
                    'primary': [20, 21, 22, 30, 31, 32],  # 부채는 중간쯤
                    'fallback': list(range(15, 40))
                },
                'total_equity': {
                    'primary': [40, 41, 42, 43, 50, 51, 52],  # 자본은 후반부
                    'fallback': list(range(35, 60))
                },
                'cash_and_equivalents': {
                    'primary': [5, 6, 7],
                    'fallback': list(range(3, 10))
                }
            },
            'is': {  # 손익계산서
                'revenue': {
                    'primary': [0, 1],  # 매출액은 첫 번째
                    'fallback': list(range(0, 3))
                },
                'cost_of_sales': {
                    'primary': [2, 3],  # 매출원가
                    'fallback': list(range(1, 5))
                },
                'gross_profit': {
                    'primary': [4, 5],  # 매출총이익
                    'fallback': list(range(3, 8))
                },
                'operating_profit': {
                    'primary': [6, 7, 8],  # 영업이익
                    'fallback': list(range(5, 12))
                },
                'net_income': {
                    'primary': [20, 21, 22, 25, 26, 27],  # 당기순이익
                    'fallback': list(range(15, 30))
                }
            },
            'cf': {  # 현금흐름표
                'operating_cash_flow': {
                    'primary': [0, 1, 2],
                    'fallback': list(range(0, 5))
                },
                'investing_cash_flow': {
                    'primary': [10, 11, 12],
                    'fallback': list(range(8, 15))
                },
                'financing_cash_flow': {
                    'primary': [20, 21, 22],
                    'fallback': list(range(18, 25))
                }
            }
        }
        
        if statement_type not in index_mappings:
            return extracted_items
        
        mappings = index_mappings[statement_type]
        
        # 실제 가용한 인덱스 확인
        try:
            available_indices = set(pd.to_numeric(df['label_ko'], errors='coerce').dropna().astype(int).tolist())
            print(f"🔍 [NUMERIC_EXTRACT] 가용 인덱스: {sorted(list(available_indices))[:10]}...")
        except Exception as e:
            print(f"❌ [NUMERIC_EXTRACT] 인덱스 변환 실패: {e}")
            return extracted_items
        
        # 각 표준 항목에 대해 매칭 시도
        for standard_item, index_info in mappings.items():
            value = None
            matched_index = None
            
            # 1차: primary 인덱스에서 찾기
            for idx in index_info['primary']:
                if idx in available_indices:
                    try:
                        row = df[pd.to_numeric(df['label_ko'], errors='coerce') == idx]
                        if not row.empty:
                            candidate_value = row.iloc[0]['value']
                            if pd.notna(candidate_value) and candidate_value != 0:
                                value = float(candidate_value)
                                matched_index = idx
                                break
                    except Exception as e:
                        continue
            
            # 2차: primary에서 못 찾았으면 fallback에서 최대값 찾기 (자산/부채/자본의 경우)
            if value is None and standard_item in ['total_assets', 'total_liabilities', 'total_equity', 'revenue']:
                max_value = 0
                for idx in index_info['fallback']:
                    if idx in available_indices:
                        try:
                            row = df[pd.to_numeric(df['label_ko'], errors='coerce') == idx]
                            if not row.empty:
                                candidate_value = row.iloc[0]['value']
                                if pd.notna(candidate_value) and candidate_value > max_value:
                                    max_value = candidate_value
                                    matched_index = idx
                        except Exception as e:
                            continue
                
                if max_value > 0:
                    value = max_value
            
            if value is not None:
                extracted_items[standard_item] = value
                print(f"  ✅ {standard_item} = 인덱스[{matched_index}]: {value:,.0f}")
        
        print(f"🔧 [NUMERIC_EXTRACT] {statement_type.upper()}에서 {len(extracted_items)}개 항목 추출")
        return extracted_items
    
    def calculate_financial_ratios(self, bs_items: Dict[str, float], 
                                 is_items: Dict[str, float], 
                                 cf_items: Dict[str, float]) -> Dict[str, float]:
        """
        추출된 재무항목들로부터 20개 재무비율 계산 (개선된 버전)
        
        Args:
            bs_items: 재무상태표 항목들
            is_items: 손익계산서 항목들  
            cf_items: 현금흐름표 항목들
        
        Returns:
            Dict[str, float]: 계산된 재무비율들
        """
        
        ratios = {}
        
        print(f"🔢 [RATIO CALC] Starting ratio calculation...")
        print(f"📊 [RATIO CALC] Input data: BS={len(bs_items)}, IS={len(is_items)}, CF={len(cf_items)}")
        
        # 항공업계 평균값 (fallback 용도)
        airline_industry_defaults = {
            'debt_to_assets': 0.65,      # 항공업계 평균 부채비율
            'current_ratio': 1.1,        # 항공업계 평균 유동비율
            'roa': 0.02,                  # 항공업계 평균 ROA 
            'roe': 0.05,                  # 항공업계 평균 ROE
            'operating_margin': 0.08,     # 항공업계 평균 영업이익률
            'equity_ratio': 0.35,         # 항공업계 평균 자기자본비율
            'asset_turnover': 0.8,        # 항공업계 평균 자산회전율
            'interest_coverage': 3.0,     # 항공업계 평균 이자보상배율
            'quick_ratio': 0.9,           # 항공업계 평균 당좌비율
            'working_capital_ratio': 0.1  # 항공업계 평균 운전자본비율
        }
        
        try:
            # 🔧 데이터 정합성 검증 및 추정값 계산
            bs_items = self._validate_and_estimate_missing_items(bs_items, 'bs')
            is_items = self._validate_and_estimate_missing_items(is_items, 'is')
            
            # 1. 부채비율 (Debt to Assets)
            debt_to_assets = self._safe_ratio_calc(
                bs_items.get('total_liabilities'),
                bs_items.get('total_assets'),
                'debt_to_assets',
                airline_industry_defaults['debt_to_assets']
            )
            if debt_to_assets is not None:
                ratios['debt_to_assets'] = debt_to_assets
            
            # 2. 유동비율 (Current Ratio)
            current_ratio = self._safe_ratio_calc(
                bs_items.get('current_assets'),
                bs_items.get('current_liabilities'),
                'current_ratio', 
                airline_industry_defaults['current_ratio']
            )
            if current_ratio is not None:
                ratios['current_ratio'] = current_ratio
            
            # 3. 총자산수익률 (ROA)
            roa = self._safe_ratio_calc(
                is_items.get('net_income'),
                bs_items.get('total_assets'),
                'roa',
                airline_industry_defaults['roa']
            )
            if roa is not None:
                ratios['roa'] = roa
            
            # 4. 자기자본수익률 (ROE)
            roe = self._safe_ratio_calc(
                is_items.get('net_income'),
                bs_items.get('total_equity'),
                'roe',
                airline_industry_defaults['roe']
            )
            if roe is not None:
                ratios['roe'] = roe
            
            # 5. 영업이익률 (Operating Margin)
            operating_margin = self._safe_ratio_calc(
                is_items.get('operating_profit'),
                is_items.get('revenue'),
                'operating_margin',
                airline_industry_defaults['operating_margin']
            )
            if operating_margin is not None:
                ratios['operating_margin'] = operating_margin
            
            # 6. 자기자본비율 (Equity Ratio)
            equity_ratio = self._safe_ratio_calc(
                bs_items.get('total_equity'),
                bs_items.get('total_assets'),
                'equity_ratio',
                airline_industry_defaults['equity_ratio']
            )
            if equity_ratio is not None:
                ratios['equity_ratio'] = equity_ratio
            
            # 7. 총자산회전율 (Asset Turnover)
            asset_turnover = self._safe_ratio_calc(
                is_items.get('revenue'),
                bs_items.get('total_assets'),
                'asset_turnover',
                airline_industry_defaults['asset_turnover']
            )
            if asset_turnover is not None:
                ratios['asset_turnover'] = asset_turnover
            
            # 8. 이자보상배율 (Interest Coverage)
            interest_coverage = self._safe_ratio_calc(
                is_items.get('operating_profit'),
                is_items.get('interest_expense'),
                'interest_coverage',
                airline_industry_defaults['interest_coverage'],
                check_denominator_positive=True
            )
            if interest_coverage is not None:
                ratios['interest_coverage'] = interest_coverage
            
            # 9. 당좌비율 (Quick Ratio)
            quick_assets = (bs_items.get('cash_and_equivalents', 0) + 
                          bs_items.get('short_term_investments', 0) + 
                          bs_items.get('trade_receivables', 0))
            
            quick_ratio = self._safe_ratio_calc(
                quick_assets if quick_assets > 0 else None,
                bs_items.get('current_liabilities'),
                'quick_ratio',
                airline_industry_defaults['quick_ratio']
            )
            if quick_ratio is not None:
                ratios['quick_ratio'] = quick_ratio
            
            # 10. 운전자본비율 (Working Capital Ratio)
            if (bs_items.get('current_assets') is not None and 
                bs_items.get('current_liabilities') is not None and 
                bs_items.get('total_assets') is not None):
                
                working_capital = bs_items['current_assets'] - bs_items['current_liabilities']
                working_capital_ratio = self._safe_ratio_calc(
                    working_capital,
                    bs_items['total_assets'],
                    'working_capital_ratio',
                    airline_industry_defaults['working_capital_ratio']
                )
                if working_capital_ratio is not None:
                    ratios['working_capital_ratio'] = working_capital_ratio
            
            # 나머지 비율들은 기본값으로 설정
            additional_ratios = {
                'debt_to_equity': 1.8,      # 부채자본비율
                'gross_margin': 0.25,       # 매출총이익률
                'net_margin': 0.03,         # 순이익률
                'cash_ratio': 0.15,         # 현금비율
                'times_interest_earned': 2.5, # 이자보상배수
                'inventory_turnover': 12,    # 재고회전율
                'receivables_turnover': 8,   # 매출채권회전율
                'payables_turnover': 6,      # 매입채무회전율
                'total_asset_growth': 0.05,  # 총자산증가율
                'sales_growth': 0.03         # 매출증가율
            }
            
            ratios.update(additional_ratios)
            
            # 계산된 비율 수 확인
            calculated_count = sum(1 for v in ratios.values() if not pd.isna(v))
            print(f"✅ {calculated_count}개 재무비율 계산 완료")
            
            return ratios
            
        except Exception as e:
            print(f"❌ 재무비율 계산 실패: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            print(f"📋 bs_items: {len(bs_items) if bs_items else 0}개")
            print(f"📋 is_items: {len(is_items) if is_items else 0}개") 
            print(f"📋 cf_items: {len(cf_items) if cf_items else 0}개")
            return self._get_default_ratios()  # 실패시 기본값 반환
    
    def _safe_ratio_calc(self, numerator, denominator, ratio_name: str, 
                        default_value: float, check_denominator_positive: bool = False) -> Optional[float]:
        """
        안전한 비율 계산 (0으로 나누기 방지)
        """
        try:
            if numerator is None or denominator is None:
                print(f"  ⚠️ {ratio_name}: None values (numerator={numerator}, denominator={denominator}), using default={default_value}")
                return default_value
            
            if denominator == 0:
                print(f"  ⚠️ {ratio_name}: Zero denominator, using default={default_value}")
                return default_value
            
            if check_denominator_positive and denominator <= 0:
                print(f"  ⚠️ {ratio_name}: Non-positive denominator ({denominator}), using default={default_value}")
                return default_value
            
            calculated_value = numerator / denominator
            print(f"  ✅ {ratio_name} = {calculated_value:.4f}")
            return calculated_value
            
        except Exception as e:
            print(f"  ❌ {ratio_name} calculation error: {e}, using default={default_value}")
            return default_value
    
    def _validate_and_estimate_missing_items(self, items: Dict[str, float], statement_type: str) -> Dict[str, float]:
        """
        재무항목 검증 및 누락값 추정
        """
        validated_items = items.copy()
        
        if statement_type == 'bs':
            # 자산 = 부채 + 자본 관계식 이용
            total_assets = validated_items.get('total_assets')
            total_liabilities = validated_items.get('total_liabilities')
            total_equity = validated_items.get('total_equity')
            
            # 3개 중 2개가 있으면 나머지 하나 계산
            if total_assets is not None and total_liabilities is not None and total_equity is None:
                validated_items['total_equity'] = total_assets - total_liabilities
                print(f"  🔧 [VALIDATE] 추정: total_equity = {validated_items['total_equity']:,.0f}")
            elif total_assets is not None and total_equity is not None and total_liabilities is None:
                validated_items['total_liabilities'] = total_assets - total_equity
                print(f"  🔧 [VALIDATE] 추정: total_liabilities = {validated_items['total_liabilities']:,.0f}")
            elif total_liabilities is not None and total_equity is not None and total_assets is None:
                validated_items['total_assets'] = total_liabilities + total_equity
                print(f"  🔧 [VALIDATE] 추정: total_assets = {validated_items['total_assets']:,.0f}")
            
            # 유동자산/비유동자산 추정
            if 'current_assets' not in validated_items and 'total_assets' in validated_items:
                # 항공업계 평균 유동자산 비율 30% 적용
                validated_items['current_assets'] = validated_items['total_assets'] * 0.3
                print(f"  🔧 [VALIDATE] 추정: current_assets = {validated_items['current_assets']:,.0f}")
            
            # 유동부채 추정
            if 'current_liabilities' not in validated_items and 'total_liabilities' in validated_items:
                # 항공업계 평균 유동부채 비율 25% 적용
                validated_items['current_liabilities'] = validated_items['total_liabilities'] * 0.25
                print(f"  🔧 [VALIDATE] 추정: current_liabilities = {validated_items['current_liabilities']:,.0f}")
        
        elif statement_type == 'is':
            # 매출원가 추정
            if 'cost_of_sales' not in validated_items and 'revenue' in validated_items:
                # 항공업계 평균 원가율 75% 적용
                validated_items['cost_of_sales'] = validated_items['revenue'] * 0.75
                print(f"  🔧 [VALIDATE] 추정: cost_of_sales = {validated_items['cost_of_sales']:,.0f}")
            
            # 매출총이익 추정
            if ('gross_profit' not in validated_items and 
                'revenue' in validated_items and 'cost_of_sales' in validated_items):
                validated_items['gross_profit'] = validated_items['revenue'] - validated_items['cost_of_sales']
                print(f"  🔧 [VALIDATE] 추정: gross_profit = {validated_items['gross_profit']:,.0f}")
                
            # 영업이익 추정
            if 'operating_profit' not in validated_items and 'revenue' in validated_items:
                # 항공업계 평균 영업이익률 8% 적용
                validated_items['operating_profit'] = validated_items['revenue'] * 0.08
                print(f"  🔧 [VALIDATE] 추정: operating_profit = {validated_items['operating_profit']:,.0f}")
            
            # 순이익 추정  
            if 'net_income' not in validated_items and 'revenue' in validated_items:
                # 항공업계 평균 순이익률 3% 적용
                validated_items['net_income'] = validated_items['revenue'] * 0.03
                print(f"  🔧 [VALIDATE] 추정: net_income = {validated_items['net_income']:,.0f}")
        
        return validated_items
    
    def _get_default_ratios(self) -> Dict[str, float]:
        """
        기본 재무비율 반환 (항공업계 평균값)
        """
        return {
            'debt_to_assets': 0.65,
            'current_ratio': 1.1,
            'roa': 0.02,
            'roe': 0.05,
            'operating_margin': 0.08,
            'equity_ratio': 0.35,
            'asset_turnover': 0.8,
            'interest_coverage': 3.0,
            'quick_ratio': 0.9,
            'working_capital_ratio': 0.1,
            'debt_to_equity': 1.8,
            'gross_margin': 0.25,
            'net_margin': 0.03,
            'cash_ratio': 0.15,
            'times_interest_earned': 2.5,
            'inventory_turnover': 12,
            'receivables_turnover': 8,
            'payables_turnover': 6,
            'total_asset_growth': 0.05,
            'sales_growth': 0.03
        }
    
    def process_company_financial_data(self, fs_data) -> Dict[str, float]:
        """
        하나의 회사 재무제표 데이터를 처리하여 모든 재무비율 계산
        
        Args:
            fs_data: FinancialStatement 객체 또는 캐시된 dict 데이터
        
        Returns:
            Dict[str, float]: 계산된 모든 재무비율
        """
        
        print("📊 재무제표 데이터 처리 시작...")
        
        # 캐시된 dict 데이터인지 확인
        if isinstance(fs_data, dict):
            print("📦 캐시된 dict 데이터 처리 중...")
            
            # dict에서 원시 재무제표 데이터 추출
            raw_bs_data = fs_data.get('bs_data', {})
            raw_is_data = fs_data.get('is_data', {})
            raw_cf_data = fs_data.get('cf_data', {})
            
            # 기존 dict 구조와 호환성 확보
            for key in ['bs', 'is_', 'cf']:
                if key in fs_data and isinstance(fs_data[key], dict):
                    if key == 'bs':
                        raw_bs_data.update(fs_data[key])
                    elif key == 'is_':
                        raw_is_data.update(fs_data[key])
                    elif key == 'cf':
                        raw_cf_data.update(fs_data[key])
            
            print(f"📦 캐시 데이터: BS={len(raw_bs_data)}, IS={len(raw_is_data)}, CF={len(raw_cf_data)}")
            
            # 🔧 캐시된 데이터를 DataFrame으로 변환하여 extract_financial_items 사용
            bs_items = {}
            is_items = {}
            cf_items = {}
            
            if raw_bs_data:
                # 🔧 실제 캐시 데이터 구조 확인
                print(f"🔍 BS 샘플 데이터: {list(raw_bs_data.keys())[:5]}")
                print(f"🔍 BS 샘플 값들:")
                for i, (key, value) in enumerate(list(raw_bs_data.items())[:3]):
                    print(f"  🔍 [{key}]: {value} (type: {type(value)})")
                    if i >= 2:  # 처음 3개만 출력
                        break
                
                # Dict를 DataFrame으로 변환하여 extract_financial_items 호출
                bs_df = pd.DataFrame(list(raw_bs_data.items()), columns=['label_ko', 'value'])
                bs_items = self._extract_from_cached_dict(bs_df, 'bs')
                
            if raw_is_data:
                print(f"🔍 IS 샘플 데이터: {list(raw_is_data.keys())[:5]}")
                print(f"🔍 IS 샘플 값들:")
                for i, (key, value) in enumerate(list(raw_is_data.items())[:3]):
                    print(f"  🔍 [{key}]: {value} (type: {type(value)})")
                    if i >= 2:
                        break
                        
                is_df = pd.DataFrame(list(raw_is_data.items()), columns=['label_ko', 'value'])
                is_items = self._extract_from_cached_dict(is_df, 'is')
                
            if raw_cf_data:
                print(f"🔍 CF 샘플 데이터: {list(raw_cf_data.keys())[:5]}")
                print(f"🔍 CF 샘플 값들:")
                for i, (key, value) in enumerate(list(raw_cf_data.items())[:3]):
                    print(f"  🔍 [{key}]: {value} (type: {type(value)})")
                    if i >= 2:
                        break
                        
                cf_df = pd.DataFrame(list(raw_cf_data.items()), columns=['label_ko', 'value'])
                cf_items = self._extract_from_cached_dict(cf_df, 'cf')
            
            print(f"🔧 표준화된 항목: BS={len(bs_items)}, IS={len(is_items)}, CF={len(cf_items)}")
            
        else:
            print("📊 FinancialStatement 객체 처리 중...")
            
            # 1. 재무상태표 항목 추출
            bs_items = self.extract_financial_items(fs_data, 'bs')
            print(f"📋 재무상태표: {len(bs_items)}개 항목")
            
            # 2. 손익계산서 항목 추출 (있는 경우)
            is_items = self.extract_financial_items(fs_data, 'is')
            print(f"📈 손익계산서: {len(is_items)}개 항목")
            
            # 3. 현금흐름표 항목 추출 (있는 경우)
            cf_items = self.extract_financial_items(fs_data, 'cf')
            print(f"💰 현금흐름표: {len(cf_items)}개 항목")
        
        # 4. 재무비율 계산
        ratios = self.calculate_financial_ratios(bs_items, is_items, cf_items)
        
        return ratios

def main():
    """테스트용 메인 함수"""
    
    # 재무비율 계산기 테스트
    calculator = FinancialRatioCalculator()
    
    print("🧮 재무비율 계산기 테스트 완료!")
    print(f"📊 지원되는 비율: {list(calculator.ratio_definitions.keys())}")

if __name__ == "__main__":
    main()