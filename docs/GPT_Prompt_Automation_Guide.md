# GPT 프롬프트 자동화 시스템 가이드

## 🎯 개요

이 시스템은 GPT 프롬프트를 동적으로 관리하고 시장 상황에 맞게 자동으로 업데이트하는 자동화 솔루션입니다. 더 이상 매번 코드를 수정할 필요 없이, 외부 파일을 통해 프롬프트를 관리할 수 있습니다.

## 🚀 주요 기능

### 1. **동적 프롬프트 관리**
- 프롬프트를 코드에서 분리하여 외부 파일로 관리
- JSON/YAML 형태로 구조화된 프롬프트 템플릿
- 실시간 프롬프트 업데이트 가능

### 2. **시장 상황 자동 반영**
- 현재 날짜 자동 감지 및 반영
- 연도별 시장 상황 분석 (2025년 기준)
- 시나리오 확률 자동 계산

### 3. **템플릿 기반 프롬프트 생성**
- 변수 치환을 통한 동적 프롬프트 생성
- 기본값과 사용자 입력값 조합
- 오류 발생시 기본 프롬프트로 폴백

## 📁 파일 구조

```
config/
├── prompts.py              # 프롬프트 관리 시스템
└── prompts/                # 프롬프트 파일 디렉토리
    ├── system_prompts.json # 시스템 프롬프트 템플릿
    ├── user_prompts.json   # 사용자 프롬프트 템플릿
    └── market_context.yaml # 시장 상황 컨텍스트
```

## 🔧 사용 방법

### 1. **기본 사용법**

```python
from config.prompts import get_prompt_manager

# 프롬프트 매니저 인스턴스 가져오기
prompt_manager = get_prompt_manager()

# 시스템 프롬프트 가져오기
system_prompt = prompt_manager.get_system_prompt("credit_analysis")

# 사용자 프롬프트 가져오기
user_prompt = prompt_manager.get_user_prompt("credit_analysis", 
                                           prompt="분석 요청", 
                                           context_data="데이터")
```

### 2. **시장 컨텍스트 업데이트**

```python
# 현재 시장 상황을 반영하여 프롬프트 업데이트
prompt_manager.update_market_context()

# 프롬프트 시스템 정보 확인
info = prompt_manager.get_prompt_info()
print(f"현재 날짜: {info['market_context']['current_date']}")
print(f"시장 단계: {info['market_context']['market_phase']}")
```

### 3. **대시보드에서 사용**

대시보드의 사이드바에서 다음 기능들을 사용할 수 있습니다:

- **프롬프트 현황 확인**: 현재 날짜, 시장 단계, 사용 가능한 프롬프트 수
- **시장 컨텍스트 업데이트**: 버튼 클릭으로 즉시 업데이트
- **프롬프트 설정 확인**: 디렉토리, 주요 우려사항, 시나리오 확률
- **시장 트렌드 확인**: 업계 트렌드 정보

## 📊 시장 상황별 프롬프트

### 2025년 기준 시장 상황

```yaml
market_phase: "recovery"  # 코로나 이후 회복세
key_concerns:
  - "글로벌 경기침체 영향"
  - "유가변동"
  - "환율리스크"
  - "경쟁심화"
  - "탄소중립 규제"
  - "금리환경"
  - "AI/디지털화"

scenario_probabilities:
  optimistic: 0.30    # 글로벌 경기 회복세
  baseline: 0.50      # 안정적 성장세 지속
  pessimistic: 0.20   # 글로벌 경기침체 심화
```

## 🔍 프롬프트 템플릿 예시

### 시스템 프롬프트 템플릿
```json
{
  "credit_analysis": {
    "role": "system",
    "content": "당신은 한국 시중은행의 기업금융 대출심사 전문가입니다. 현재 날짜는 {current_date}이며, 시장 상황은 {market_phase}입니다. 주요 우려사항: {key_concerns}",
    "variables": ["current_date", "market_phase", "key_concerns"]
  }
}
```

### 사용자 프롬프트 템플릿
```json
{
  "credit_analysis": {
    "role": "user",
    "content": "다음 데이터를 바탕으로 신용위험을 분석해주세요: {context_data}",
    "variables": ["context_data"]
  }
}
```

## 🎯 활용 시나리오

### 1. **일일 분석**
- 현재 시장 상황을 반영한 프롬프트로 분석
- 실시간 경제 지표 반영

### 2. **시나리오 분석**
- 낙관/기본/비관 시나리오별 프롬프트 생성
- 확률 기반 가중치 적용

### 3. **업계별 분석**
- 항공업계 특화 프롬프트
- 업계별 주요 이슈 반영

## 🔧 설정 및 커스터마이징

### 프롬프트 디렉토리 설정
```python
# config/config.py
PROMPT_DIRECTORY = "config/prompts"
DEFAULT_SYSTEM_PROMPT = "credit_analysis"
CACHE_ENABLED = True
```

### 새로운 프롬프트 추가
1. `config/prompts/system_prompts.json`에 새 템플릿 추가
2. `config/prompts/user_prompts.json`에 대응하는 사용자 프롬프트 추가
3. 프롬프트 매니저에서 새 프롬프트 사용

## 📈 성능 최적화

### 캐싱 전략
- 프롬프트 템플릿 캐싱
- 변수 치환 결과 캐싱
- 시장 컨텍스트 캐싱

### 메모리 관리
- 불필요한 프롬프트 정리
- 캐시 크기 제한
- 주기적 메모리 정리

---

**🤖 이 시스템을 통해 GPT 프롬프트를 더욱 효율적이고 유연하게 관리할 수 있습니다!** 