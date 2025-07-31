#!/usr/bin/env python3
"""
Korean Airlines Corp Code Mapper
================================

DART corp_code를 자동으로 가져와서 매핑하는 스크립트

Usage:
    python get_corp_codes.py

Author: Korean Airlines Credit Rating Analysis
"""

import sys
from config import DART_API_KEY, KOREAN_AIRLINES

try:
    from dart_fss import set_api_key, get_corp_list
    print("✅ dart-fss 모듈 로드 성공")
except ImportError:
    print("❌ dart-fss가 설치되지 않았습니다.")
    print("설치: pip install dart-fss")
    sys.exit(1)

def get_airline_corp_codes():
    """한국 항공사들의 corp_code를 가져오는 함수"""
    
    print(f"🔑 DART API 키 설정 중...")
    set_api_key(DART_API_KEY)
    
    print("📋 기업 리스트 가져오는 중...")
    try:
        corp_list = get_corp_list()
        print(f"✅ 총 {len(corp_list.corps)}개 기업 정보 로드 완료")
    except Exception as e:
        print(f"❌ 기업 리스트 가져오기 실패: {e}")
        return None
    
    # 타겟 주식 코드들
    target_stock_codes = {info['stock_code'] for info in KOREAN_AIRLINES.values()}
    print(f"🎯 타겟 주식코드: {target_stock_codes}")
    
    # corp_code 매핑
    mapping = {}
    for corp in corp_list.corps:
        if corp.stock_code in target_stock_codes:
            mapping[corp.stock_code] = {
                'corp_code': corp.corp_code,
                'corp_name': corp.corp_name,
                'modify_date': corp.modify_date
            }
    
    print(f"\n📊 매핑 결과:")
    print("=" * 80)
    
    # 결과 출력 및 검증
    airline_mapping = {}
    for company_name, info in KOREAN_AIRLINES.items():
        stock_code = info['stock_code']
        if stock_code in mapping:
            corp_info = mapping[stock_code]
            airline_mapping[company_name] = {
                'stock_code': stock_code,
                'corp_code': corp_info['corp_code'],
                'corp_name': corp_info['corp_name'],
                'market': info['market'],
                'status': info['status'],
                'modify_date': corp_info['modify_date']
            }
            
            print(f"✅ {company_name:10} | {stock_code} | {corp_info['corp_code']} | {corp_info['corp_name']}")
        else:
            print(f"❌ {company_name:10} | {stock_code} | NOT FOUND")
            airline_mapping[company_name] = {
                'stock_code': stock_code,
                'corp_code': None,
                'corp_name': None,
                'market': info['market'], 
                'status': info['status'],
                'modify_date': None
            }
    
    print("=" * 80)
    print(f"🎉 매핑 완료: {len([k for k, v in airline_mapping.items() if v['corp_code']])}개 성공")
    
    return airline_mapping

def save_corp_mapping(mapping):
    """corp_code 매핑을 파일로 저장"""
    
    import json
    
    # JSON 파일로 저장
    with open('korean_airlines_corp_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"💾 매핑 결과 저장: korean_airlines_corp_mapping.json")
    
    # Python 코드 형태로도 저장
    with open('korean_airlines_corp_codes.py', 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("Korean Airlines Corp Codes Mapping\n")
        f.write("===================================\n\n")
        f.write("DART에서 자동 생성된 corp_code 매핑\n")
        f.write('"""\n\n')
        
        f.write("# Korean Airlines Corp Code Mapping\n")
        f.write("KOREAN_AIRLINES_CORP_MAPPING = {\n")
        
        for company_name, info in mapping.items():
            f.write(f"    '{company_name}': {{\n")
            for key, value in info.items():
                if isinstance(value, str):
                    f.write(f"        '{key}': '{value}',\n")
                else:
                    f.write(f"        '{key}': {value},\n")
            f.write("    },\n")
        
        f.write("}\n\n")
        
        # 검증 함수 추가
        f.write("def get_corp_code(company_name):\n")
        f.write('    """회사명으로 corp_code 가져오기"""\n')
        f.write("    return KOREAN_AIRLINES_CORP_MAPPING.get(company_name, {}).get('corp_code')\n\n")
        
        f.write("def get_stock_code(company_name):\n") 
        f.write('    """회사명으로 stock_code 가져오기"""\n')
        f.write("    return KOREAN_AIRLINES_CORP_MAPPING.get(company_name, {}).get('stock_code')\n\n")
        
        f.write("if __name__ == '__main__':\n")
        f.write("    print('Korean Airlines Corp Code Mapping:')\n")
        f.write("    for name, info in KOREAN_AIRLINES_CORP_MAPPING.items():\n")
        f.write("        print(f'{name}: {info[\"corp_code\"]}')\n")
    
    print(f"💾 Python 코드 저장: korean_airlines_corp_codes.py")

if __name__ == "__main__":
    print("🚀 한국 항공사 Corp Code 매핑 시작")
    print("=" * 50)
    
    # Corp code 매핑 가져오기
    mapping = get_airline_corp_codes()
    
    if mapping:
        # 결과 저장
        save_corp_mapping(mapping)
        print("\n🎉 Corp Code 매핑 완료!")
    else:
        print("\n❌ Corp Code 매핑 실패")
        sys.exit(1)