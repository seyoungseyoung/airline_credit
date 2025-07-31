#!/usr/bin/env python3
"""
Korean Airlines Credit Rating Data Pipeline
==========================================

Pipeline for collecting and processing credit rating transition data for:
- 대한항공 (Korean Air)
- 아시아나항공 (Asiana Airlines) 
- 제주항공 (Jeju Air)
- 티웨이항공 (T'way Air)

Data Sources:
1. DART API: Financial statements (2010Q1~2025Q2)
2. NICE/KIS: Credit rating disclosures
3. KRX: Stock codes and company information

Output Format:
- TransitionHistory.csv: Id,Date,RatingSymbol
- RatingMapping.csv: RatingSymbol,RatingNumber
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import time
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AirlineCompany:
    """Airline company information"""
    name: str
    name_kr: str
    stock_code: str
    market: str  # KOSPI or KOSDAQ
    corp_code: str  # DART corporation code
    issuer_id: int

# Target companies with their stock codes
AIRLINE_COMPANIES = [
    AirlineCompany("Korean Air", "대한항공", "003490", "KOSPI", "", 1),
    AirlineCompany("Asiana Airlines", "아시아나항공", "020560", "KOSPI", "", 2), 
    AirlineCompany("Jeju Air", "제주항공", "089590", "KOSDAQ", "", 3),
    AirlineCompany("T'way Air", "티웨이항공", "091810", "KOSDAQ", "", 4)
]

class DARTScraper:
    """DART Open API scraper for financial statements"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://opendart.fss.or.kr/api"
        self.session = requests.Session()
        
    def get_corp_code(self, stock_code: str) -> Optional[str]:
        """Get DART corporation code from stock code"""
        url = f"{self.base_url}/company.json"
        params = {
            'crtfc_key': self.api_key,
            'stock_code': stock_code
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '000':
                return data['corp_code']
            else:
                logger.error(f"DART API error for {stock_code}: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting corp_code for {stock_code}: {e}")
            return None
    
    def get_financial_statements(self, corp_code: str, year: int, quarter: int) -> Optional[pd.DataFrame]:
        """Get quarterly financial statements"""
        url = f"{self.base_url}/fnlttSinglAcntAll.json"
        
        # Convert quarter to report code
        report_codes = {1: '11013', 2: '11012', 3: '11014', 4: '11011'}
        
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': str(year),
            'reprt_code': report_codes[quarter],
            'fs_div': 'CFS'  # Consolidated Financial Statements
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '000':
                return pd.DataFrame(data['list'])
            else:
                logger.warning(f"No data for {corp_code} {year}Q{quarter}: {data.get('message', '')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting financial data for {corp_code} {year}Q{quarter}: {e}")
            return None
        
        time.sleep(0.1)  # Rate limiting
    
    def calculate_financial_ratios(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate 20 key financial ratios"""
        if df is None or df.empty:
            return {}
        
        # Create a mapping of account names to values
        accounts = {}
        for _, row in df.iterrows():
            accounts[row['account_nm']] = float(row.get('thstrm_amount', 0) or 0)
        
        ratios = {}
        
        try:
            # Asset Quality Ratios
            total_assets = accounts.get('자산총계', 0)
            current_assets = accounts.get('유동자산', 0)
            current_liabilities = accounts.get('유동부채', 0)
            total_liabilities = accounts.get('부채총계', 0)
            total_equity = accounts.get('자본총계', 0)
            
            # Revenue and Profitability
            revenue = accounts.get('매출액', 0) or accounts.get('영업수익', 0)
            operating_income = accounts.get('영업이익', 0)
            net_income = accounts.get('당기순이익', 0)
            
            # Cash Flow (if available)
            operating_cf = accounts.get('영업활동현금흐름', 0)
            
            # Calculate ratios
            if total_assets > 0:
                ratios['debt_to_assets'] = total_liabilities / total_assets
                ratios['equity_to_assets'] = total_equity / total_assets
                ratios['asset_turnover'] = revenue / total_assets if revenue > 0 else 0
                ratios['roa'] = net_income / total_assets
                
            if current_assets > 0 and current_liabilities > 0:
                ratios['current_ratio'] = current_assets / current_liabilities
                
            if total_equity > 0:
                ratios['debt_to_equity'] = total_liabilities / total_equity
                ratios['roe'] = net_income / total_equity
                
            if revenue > 0:
                ratios['operating_margin'] = operating_income / revenue
                ratios['net_margin'] = net_income / revenue
                ratios['asset_turnover'] = revenue / total_assets if total_assets > 0 else 0
                
            # Additional ratios for airlines
            ratios['equity_ratio'] = total_equity / total_assets if total_assets > 0 else 0
            ratios['liability_ratio'] = total_liabilities / total_assets if total_assets > 0 else 0
            ratios['interest_coverage'] = 0  # Needs interest expense data
            ratios['quick_ratio'] = 0  # Needs quick assets data
            ratios['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets if total_assets > 0 else 0
            
            # Cash flow ratios
            ratios['operating_cf_ratio'] = operating_cf / total_assets if total_assets > 0 else 0
            ratios['cf_to_debt'] = operating_cf / total_liabilities if total_liabilities > 0 else 0
            ratios['cf_coverage'] = operating_cf / current_liabilities if current_liabilities > 0 else 0
            
            # Additional airline-specific ratios
            ratios['debt_service_coverage'] = 0  # Needs debt service data
            ratios['times_interest_earned'] = 0  # Needs interest expense data
            
        except Exception as e:
            logger.error(f"Error calculating ratios: {e}")
            
        return ratios

class RatingCollector:
    """Collect credit rating information from public disclosures"""
    
    def __init__(self):
        self.rating_history = []
        self.rating_mapping = {
            'AAA': 0, 'AA+': 1, 'AA': 1, 'AA-': 1,
            'A+': 2, 'A': 2, 'A-': 2,
            'BBB+': 3, 'BBB': 3, 'BBB-': 3,
            'BB+': 4, 'BB': 4, 'BB-': 4,
            'B+': 5, 'B': 5, 'B-': 5,
            'CCC+': 6, 'CCC': 6, 'CCC-': 6,
            'D': 7, 'NR': 8
        }
    
    def normalize_rating(self, rating: str) -> str:
        """Normalize rating format"""
        rating = rating.upper().strip()
        
        # Handle Korean rating agencies format
        if rating in ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D', 'NR']:
            return rating
        elif rating in ['AA+', 'AA-', 'A+', 'A-', 'BBB+', 'BBB-', 'BB+', 'BB-', 'B+', 'B-', 'CCC+', 'CCC-']:
            return rating[:-1]  # Remove + or - for simplification
        else:
            return 'NR'
    
    def add_rating_record(self, issuer_id: int, date: str, rating: str):
        """Add a rating record"""
        normalized_rating = self.normalize_rating(rating)
        self.rating_history.append({
            'Id': issuer_id,
            'Date': date,
            'RatingSymbol': normalized_rating
        })
    
    def get_sample_ratings(self) -> List[Dict]:
        """Generate sample rating data for demonstration"""
        sample_data = []
        
        for company in AIRLINE_COMPANIES:
            # Sample rating progression (this would be replaced with actual data collection)
            if company.name == "Korean Air":
                ratings = [
                    ('31-Dec-10', 'BBB'), ('30-Jun-11', 'BBB'), ('31-Dec-11', 'BB'),
                    ('30-Jun-12', 'BB'), ('31-Dec-12', 'B'), ('30-Jun-13', 'B'),
                    ('31-Dec-13', 'BB'), ('30-Jun-14', 'BB'), ('31-Dec-14', 'BBB'),
                    ('30-Jun-15', 'BBB'), ('31-Dec-15', 'BBB'), ('30-Jun-16', 'BBB'),
                    ('31-Dec-16', 'A'), ('30-Jun-17', 'A'), ('31-Dec-17', 'A'),
                    ('30-Jun-18', 'A'), ('31-Dec-18', 'BBB'), ('30-Jun-19', 'BBB'),
                    ('31-Dec-19', 'BB'), ('30-Jun-20', 'B'), ('31-Dec-20', 'B'),
                    ('30-Jun-21', 'BB'), ('31-Dec-21', 'BB'), ('30-Jun-22', 'BBB'),
                    ('31-Dec-22', 'BBB'), ('30-Jun-23', 'BBB'), ('31-Dec-23', 'A'),
                    ('30-Jun-24', 'A')
                ]
            elif company.name == "Asiana Airlines":
                ratings = [
                    ('31-Dec-10', 'BBB'), ('30-Jun-11', 'BBB'), ('31-Dec-11', 'BB'),
                    ('30-Jun-12', 'BB'), ('31-Dec-12', 'B'), ('30-Jun-13', 'CCC'),
                    ('31-Dec-13', 'B'), ('30-Jun-14', 'B'), ('31-Dec-14', 'BB'),
                    ('30-Jun-15', 'BB'), ('31-Dec-15', 'BBB'), ('30-Jun-16', 'BBB'),
                    ('31-Dec-16', 'BBB'), ('30-Jun-17', 'BB'), ('31-Dec-17', 'B'),
                    ('30-Jun-18', 'B'), ('31-Dec-18', 'CCC'), ('30-Jun-19', 'B'),
                    ('31-Dec-19', 'CCC'), ('30-Jun-20', 'D'), ('31-Dec-20', 'NR'),
                    ('30-Jun-21', 'NR'), ('31-Dec-21', 'NR'), ('30-Jun-22', 'NR'),
                    ('31-Dec-22', 'NR'), ('30-Jun-23', 'NR'), ('31-Dec-23', 'NR'),
                    ('30-Jun-24', 'NR')
                ]
            elif company.name == "Jeju Air":
                ratings = [
                    ('31-Dec-15', 'BBB'), ('30-Jun-16', 'BBB'), ('31-Dec-16', 'BBB'),
                    ('30-Jun-17', 'BBB'), ('31-Dec-17', 'A'), ('30-Jun-18', 'A'),
                    ('31-Dec-18', 'BBB'), ('30-Jun-19', 'BBB'), ('31-Dec-19', 'BB'),
                    ('30-Jun-20', 'B'), ('31-Dec-20', 'B'), ('30-Jun-21', 'BB'),
                    ('31-Dec-21', 'BB'), ('30-Jun-22', 'BBB'), ('31-Dec-22', 'BBB'),
                    ('30-Jun-23', 'A'), ('31-Dec-23', 'A'), ('30-Jun-24', 'A')
                ]
            else:  # T'way Air
                ratings = [
                    ('31-Dec-17', 'BB'), ('30-Jun-18', 'BB'), ('31-Dec-18', 'B'),
                    ('30-Jun-19', 'B'), ('31-Dec-19', 'CCC'), ('30-Jun-20', 'CCC'),
                    ('31-Dec-20', 'B'), ('30-Jun-21', 'B'), ('31-Dec-21', 'BB'),
                    ('30-Jun-22', 'BB'), ('31-Dec-22', 'BBB'), ('30-Jun-23', 'BBB'),
                    ('31-Dec-23', 'BBB'), ('30-Jun-24', 'BBB')
                ]
            
            for date, rating in ratings:
                sample_data.append({
                    'Id': company.issuer_id,
                    'Date': date,
                    'RatingSymbol': rating
                })
        
        return sample_data

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, dart_api_key: Optional[str] = None):
        self.dart_scraper = DARTScraper(dart_api_key) if dart_api_key else None
        self.rating_collector = RatingCollector()
        self.companies = AIRLINE_COMPANIES.copy()
        
    def setup_companies(self):
        """Setup company information with DART corp codes"""
        if not self.dart_scraper:
            logger.warning("DART API key not provided, skipping corp code setup")
            return
            
        for company in self.companies:
            logger.info(f"Getting corp code for {company.name} ({company.stock_code})")
            corp_code = self.dart_scraper.get_corp_code(company.stock_code)
            if corp_code:
                company.corp_code = corp_code
                logger.info(f"✓ {company.name}: {corp_code}")
            else:
                logger.error(f"✗ Failed to get corp code for {company.name}")
    
    def collect_financial_data(self, start_year: int = 2010, end_year: int = 2025):
        """Collect financial data for all companies"""
        if not self.dart_scraper:
            logger.warning("DART API key not provided, skipping financial data collection")
            return pd.DataFrame()
        
        all_data = []
        
        for company in self.companies:
            if not company.corp_code:
                logger.warning(f"No corp code for {company.name}, skipping")
                continue
                
            logger.info(f"Collecting financial data for {company.name}")
            
            for year in range(start_year, min(end_year + 1, 2025)):
                for quarter in range(1, 5):
                    # Don't try to get future quarters
                    if year == 2025 and quarter > 2:
                        break
                        
                    logger.info(f"  Processing {year}Q{quarter}")
                    
                    df = self.dart_scraper.get_financial_statements(
                        company.corp_code, year, quarter
                    )
                    
                    if df is not None and not df.empty:
                        ratios = self.dart_scraper.calculate_financial_ratios(df)
                        
                        record = {
                            'company_name': company.name,
                            'issuer_id': company.issuer_id,
                            'year': year,
                            'quarter': quarter,
                            'date': f"31-{['Mar', 'Jun', 'Sep', 'Dec'][quarter-1]}-{str(year)[-2:]}",
                            **ratios
                        }
                        all_data.append(record)
        
        return pd.DataFrame(all_data)
    
    def collect_rating_data(self, use_sample: bool = True):
        """Collect credit rating data"""
        if use_sample:
            logger.info("Using sample rating data for demonstration")
            return self.rating_collector.get_sample_ratings()
        else:
            logger.info("Manual rating collection needed - implement scraping logic here")
            # TODO: Implement actual rating collection from NICE/KIS disclosures
            return []
    
    def create_output_files(self, rating_data: List[Dict], output_dir: str = "."):
        """Create TransitionHistory.csv and RatingMapping.csv files"""
        
        # Create TransitionHistory.csv
        transition_df = pd.DataFrame(rating_data)
        transition_file = os.path.join(output_dir, "TransitionHistory.csv")
        transition_df.to_csv(transition_file, index=False)
        logger.info(f"✓ Created {transition_file} with {len(transition_df)} records")
        
        # Create RatingMapping.csv
        mapping_data = [
            ['RatingSymbol', 'RatingNumber'],
            ['AAA', 0], ['AA', 1], ['A', 2], ['BBB', 3],
            ['BB', 4], ['B', 5], ['CCC', 6], ['D', 7], ['NR', 8]
        ]
        
        mapping_file = os.path.join(output_dir, "RatingMapping.csv")
        with open(mapping_file, 'w') as f:
            for row in mapping_data:
                f.write(','.join(map(str, row)) + '\n')
        
        logger.info(f"✓ Created {mapping_file}")
        
        return transition_file, mapping_file
    
    def run_pipeline(self, dart_api_key: Optional[str] = None, use_sample_ratings: bool = True):
        """Run the complete data pipeline"""
        logger.info("🚀 Starting Korean Airlines Credit Rating Data Pipeline")
        
        # Step 1: Setup company information
        logger.info("📋 Step 1: Setting up company information")
        if dart_api_key:
            self.dart_scraper = DARTScraper(dart_api_key)
            self.setup_companies()
        
        # Step 2: Collect financial data (optional)
        logger.info("💰 Step 2: Collecting financial data")
        financial_data = self.collect_financial_data()
        if not financial_data.empty:
            financial_data.to_csv("korean_airlines_financial_data.csv", index=False)
            logger.info(f"✓ Saved financial data: {len(financial_data)} records")
        
        # Step 3: Collect rating data
        logger.info("⭐ Step 3: Collecting credit rating data")
        rating_data = self.collect_rating_data(use_sample=use_sample_ratings)
        
        # Step 4: Create output files
        logger.info("📄 Step 4: Creating output files")
        transition_file, mapping_file = self.create_output_files(rating_data)
        
        logger.info("🎉 Pipeline completed successfully!")
        logger.info(f"📊 Generated files:")
        logger.info(f"   - {transition_file}")
        logger.info(f"   - {mapping_file}")
        if not financial_data.empty:
            logger.info(f"   - korean_airlines_financial_data.csv")
        
        return transition_file, mapping_file

def main():
    """Main function for running the pipeline"""
    
    # Configuration
    DART_API_KEY = os.getenv('DART_API_KEY')  # Set your DART API key as environment variable
    USE_SAMPLE_RATINGS = True  # Set to False when you have real rating data
    
    if not DART_API_KEY:
        logger.warning("DART_API_KEY environment variable not set")
        logger.warning("You can get a free API key from: https://opendart.fss.or.kr/")
        logger.warning("Running with sample data only...")
    
    # Run pipeline
    pipeline = DataPipeline(DART_API_KEY)
    pipeline.run_pipeline(DART_API_KEY, USE_SAMPLE_RATINGS)

if __name__ == "__main__":
    main() 