#!/usr/bin/env python3
"""
Configuration file for Korean Airlines Credit Rating Analysis
===========================================================

Contains API keys and configuration settings for:
- DART Open API
- OpenAI GPT-4
- Slack Webhook

Author: Korean Airlines Credit Rating Analysis
"""

import os

# DART Open API Configuration
DART_API_KEY = os.getenv("DART_API_KEY", "your_dart_api_key_here")

# OpenAI API Configuration  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Slack Webhook URL (optional)
SLACK_WEBHOOK_URL = ""

# Data Source Configuration
# Set to False for fast dummy data during development
# Set to True for real DART financial data in production
USE_REAL_DATA = False  # 🔄 Toggle this for development vs production

# Korean Airlines Stock Codes
KOREAN_AIRLINES = {
    '대한항공': {
        'stock_code': '003490',
        'market': 'KOSPI',
        'status': 'active'
    },
    '아시아나항공': {
        'stock_code': '020560', 
        'market': 'KOSPI',
        'status': 'suspended'  # 거래정지
    },
    '제주항공': {
        'stock_code': '089590',
        'market': 'KOSDAQ',
        'status': 'active'
    },
    '티웨이항공': {
        'stock_code': '091810',
        'market': 'KOSDAQ', 
        'status': 'active'
    },
    '에어부산': {
        'stock_code': '298690',
        'market': 'KOSDAQ',
        'status': 'active'
    }
}

# Financial ratios to calculate
FINANCIAL_RATIOS = [
    'debt_to_assets',           # 부채비율
    'current_ratio',            # 유동비율
    'roa',                      # 총자산수익률
    'roe',                      # 자기자본수익률  
    'operating_margin',         # 영업이익률
    'equity_ratio',             # 자기자본비율
    'asset_turnover',           # 총자산회전율
    'interest_coverage',        # 이자보상배율
    'quick_ratio',              # 당좌비율
    'working_capital_ratio',    # 운전자본비율
    'debt_to_equity',           # 부채자본비율
    'gross_margin',             # 매출총이익률
    'net_margin',               # 순이익률
    'cash_ratio',               # 현금비율
    'times_interest_earned',    # 이자보상배수
    'inventory_turnover',       # 재고자산회전율
    'receivables_turnover',     # 매출채권회전율
    'payables_turnover',        # 매입채무회전율
    'total_asset_growth',       # 총자산증가율
    'sales_growth'              # 매출증가율
]

# Data collection period
DATA_START_YEAR = 2010
DATA_END_YEAR = 2025
QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']

# Cache Configuration
CACHE_ENABLED = True                    # 캐시 기능 활성화 여부
CACHE_DIRECTORY = "financial_data/dart_cache"  # 캐시 파일 저장 경로
CACHE_DURATION_HOURS = 24              # 캐시 유효 시간 (시간 단위)
CACHE_MAX_SIZE_MB = 500                # 최대 캐시 크기 (MB)

print("✅ Configuration loaded successfully")
print(f"📊 Target companies: {len(KOREAN_AIRLINES)}")
print(f"📈 Financial ratios: {len(FINANCIAL_RATIOS)}")
print(f"📅 Data period: {DATA_START_YEAR}-{DATA_END_YEAR}")