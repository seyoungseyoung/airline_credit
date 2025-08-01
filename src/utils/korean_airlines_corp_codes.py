#!/usr/bin/env python3
"""
Korean Airlines Corp Codes Mapping
===================================

DART에서 자동 생성된 corp_code 매핑
"""

# Korean Airlines Corp Code Mapping
KOREAN_AIRLINES_CORP_MAPPING = {
    '대한항공': {
        'stock_code': '003490',
        'corp_code': '00113526',
        'corp_name': '대한항공',
        'market': 'KOSPI',
        'status': 'active',
        'modify_date': '20221229',
    },
    '아시아나항공': {
        'stock_code': '020560',
        'corp_code': '00138792',
        'corp_name': '아시아나항공',
        'market': 'KOSPI',
        'status': 'suspended',
        'modify_date': '20250117',
    },
    '제주항공': {
        'stock_code': '089590',
        'corp_code': '00555874',
        'corp_name': '제주항공',
        'market': 'KOSDAQ',
        'status': 'active',
        'modify_date': '20221227',
    },
    '티웨이항공': {
        'stock_code': '091810',
        'corp_code': '00671376',
        'corp_name': '티웨이항공',
        'market': 'KOSDAQ',
        'status': 'active',
        'modify_date': '20250630',
    },
    '에어부산': {
        'stock_code': '298690',
        'corp_code': '00651901',
        'corp_name': '에어부산',
        'market': 'KOSDAQ',
        'status': 'active',
        'modify_date': '20250117',
    },
}

def get_corp_code(company_name):
    """회사명으로 corp_code 가져오기"""
    return KOREAN_AIRLINES_CORP_MAPPING.get(company_name, {}).get('corp_code')

def get_stock_code(company_name):
    """회사명으로 stock_code 가져오기"""
    return KOREAN_AIRLINES_CORP_MAPPING.get(company_name, {}).get('stock_code')

if __name__ == '__main__':
    print('Korean Airlines Corp Code Mapping:')
    for name, info in KOREAN_AIRLINES_CORP_MAPPING.items():
        print(f'{name}: {info["corp_code"]}')
