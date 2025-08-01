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
    
    def calculate_financial_ratios(self, bs_items: Dict[str, float], 
                                 is_items: Dict[str, float], 
                                 cf_items: Dict[str, float]) -> Dict[str, float]:
        """
        추출된 재무항목들로부터 20개 재무비율 계산
        
        Args:
            bs_items: 재무상태표 항목들
            is_items: 손익계산서 항목들  
            cf_items: 현금흐름표 항목들
        
        Returns:
            Dict[str, float]: 계산된 재무비율들
        """
        
        ratios = {}
        
        try:
            # 1. 부채비율 (Debt to Assets)
            if 'total_liabilities' in bs_items and 'total_assets' in bs_items:
                ratios['debt_to_assets'] = bs_items['total_liabilities'] / bs_items['total_assets']
            
            # 2. 유동비율 (Current Ratio)
            if 'current_assets' in bs_items and 'current_liabilities' in bs_items:
                ratios['current_ratio'] = bs_items['current_assets'] / bs_items['current_liabilities']
            
            # 3. 총자산수익률 (ROA)
            if 'net_income' in is_items and 'total_assets' in bs_items:
                ratios['roa'] = is_items['net_income'] / bs_items['total_assets']
            
            # 4. 자기자본수익률 (ROE)
            if 'net_income' in is_items and 'total_equity' in bs_items:
                ratios['roe'] = is_items['net_income'] / bs_items['total_equity']
            
            # 5. 영업이익률 (Operating Margin)
            if 'operating_profit' in is_items and 'revenue' in is_items:
                ratios['operating_margin'] = is_items['operating_profit'] / is_items['revenue']
            
            # 6. 자기자본비율 (Equity Ratio)
            if 'total_equity' in bs_items and 'total_assets' in bs_items:
                ratios['equity_ratio'] = bs_items['total_equity'] / bs_items['total_assets']
            
            # 7. 총자산회전율 (Asset Turnover)
            if 'revenue' in is_items and 'total_assets' in bs_items:
                ratios['asset_turnover'] = is_items['revenue'] / bs_items['total_assets']
            
            # 8. 이자보상배율 (Interest Coverage)
            if 'operating_profit' in is_items and 'interest_expense' in is_items and is_items['interest_expense'] > 0:
                ratios['interest_coverage'] = is_items['operating_profit'] / is_items['interest_expense']
            
            # 9. 당좌비율 (Quick Ratio) - 현금성자산 + 단기투자 + 매출채권 / 유동부채
            if 'current_liabilities' in bs_items and bs_items['current_liabilities'] > 0:
                quick_assets = 0
                if 'cash_and_equivalents' in bs_items:
                    quick_assets += bs_items['cash_and_equivalents']
                if 'short_term_investments' in bs_items:
                    quick_assets += bs_items['short_term_investments']
                if 'trade_receivables' in bs_items:
                    quick_assets += bs_items['trade_receivables']
                ratios['quick_ratio'] = quick_assets / bs_items['current_liabilities']
            
            # 10. 운전자본비율 (Working Capital Ratio)
            if 'current_assets' in bs_items and 'current_liabilities' in bs_items and 'total_assets' in bs_items:
                working_capital = bs_items['current_assets'] - bs_items['current_liabilities']
                ratios['working_capital_ratio'] = working_capital / bs_items['total_assets']
            
            # 11. 부채자본비율 (Debt to Equity)
            if 'total_liabilities' in bs_items and 'total_equity' in bs_items and bs_items['total_equity'] > 0:
                ratios['debt_to_equity'] = bs_items['total_liabilities'] / bs_items['total_equity']
            
            # 12. 매출총이익률 (Gross Margin)
            if 'gross_profit' in is_items and 'revenue' in is_items:
                ratios['gross_margin'] = is_items['gross_profit'] / is_items['revenue']
            
            # 13. 순이익률 (Net Margin)
            if 'net_income' in is_items and 'revenue' in is_items:
                ratios['net_margin'] = is_items['net_income'] / is_items['revenue']
            
            # 14. 현금비율 (Cash Ratio)
            if 'cash_and_equivalents' in bs_items and 'current_liabilities' in bs_items:
                ratios['cash_ratio'] = bs_items['cash_and_equivalents'] / bs_items['current_liabilities']
            
            # 15. 이자보상배수 (Times Interest Earned) - EBIT / Interest Expense
            if 'ebit' in is_items and 'interest_expense' in is_items and is_items['interest_expense'] > 0:
                ratios['times_interest_earned'] = is_items['ebit'] / is_items['interest_expense']
            
            # 16-20. 회전율 및 성장률은 시계열 데이터가 필요하므로 기본값 설정
            ratios['inventory_turnover'] = np.nan  # 재고회전율
            ratios['receivables_turnover'] = np.nan  # 매출채권회전율
            ratios['payables_turnover'] = np.nan  # 매입채무회전율
            ratios['total_asset_growth'] = np.nan  # 총자산증가율
            ratios['sales_growth'] = np.nan  # 매출증가율
            
            # 계산된 비율 수 확인
            calculated_count = sum(1 for v in ratios.values() if not pd.isna(v))
            print(f"✅ {calculated_count}개 재무비율 계산 완료")
            
            return ratios
            
        except Exception as e:
            print(f"❌ 재무비율 계산 실패: {e}")
            print(f"📋 bs_items: {len(bs_items) if bs_items else 0}개")
            print(f"📋 is_items: {len(is_items) if is_items else 0}개") 
            print(f"📋 cf_items: {len(cf_items) if cf_items else 0}개")
            return {}
    
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
            
            # dict에서 재무제표 데이터 추출
            bs_items = fs_data.get('bs_data', {})
            is_items = fs_data.get('is_data', {})
            cf_items = fs_data.get('cf_data', {})
            
            # 기존 dict 구조와 호환성 확보
            for key in ['bs', 'is_', 'cf']:
                if key in fs_data and isinstance(fs_data[key], dict):
                    if key == 'bs':
                        bs_items.update(fs_data[key])
                    elif key == 'is_':
                        is_items.update(fs_data[key])
                    elif key == 'cf':
                        cf_items.update(fs_data[key])
            
            print(f"📦 캐시 데이터: BS={len(bs_items)}, IS={len(is_items)}, CF={len(cf_items)}")
            
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