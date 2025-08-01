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

### 미래 시장 상황 (기본값)

```yaml
market_phase: "stable"
key_concerns:
  - "경제 불확실성"
  - "유가변동"
  - "환율리스크"
  - "규제 변화"
```

## 🔄 프롬프트 업데이트 프로세스

### 1. **자동 업데이트**
- 시스템 시작시 자동으로 현재 날짜 감지
- 연도별 시장 상황 자동 분석
- 프롬프트 파일 자동 생성

### 2. **수동 업데이트**
- 대시보드 사이드바의 "🔄 시장 컨텍스트 업데이트" 버튼
- `prompt_manager.update_market_context()` 메서드 호출

### 3. **파일 직접 수정**
- `config/prompts/` 디렉토리의 JSON/YAML 파일 직접 편집
- 변경사항은 즉시 반영됨

## 📝 프롬프트 템플릿 수정

### 시스템 프롬프트 수정

`config/prompts/system_prompts.json` 파일을 편집:

```json
{
  "credit_analysis": {
    "role": "system",
    "content_template": "당신은 한국 시중은행의 기업금융 대출심사 전문가입니다. 현재 날짜는 {current_date}입니다."
  }
}
```

### 사용자 프롬프트 수정

`config/prompts/user_prompts.json` 파일을 편집:

```json
{
  "credit_analysis": {
    "template": "분석 요청: {prompt}\n\n데이터: {context_data}"
  }
}
```

## 🛠️ 고급 설정

### 1. **새로운 프롬프트 타입 추가**

```python
# prompts.py에 새로운 프롬프트 타입 추가
def _create_system_prompts(self):
    system_prompts = {
        "credit_analysis": { ... },
        "comprehensive_report": { ... },
        "new_prompt_type": {
            "role": "system",
            "content_template": "새로운 프롬프트 템플릿 {variable}"
        }
    }
```

### 2. **커스텀 시장 컨텍스트**

```python
def _get_current_market_context(self) -> MarketContext:
    # 특정 조건에 따른 커스텀 로직 추가
    if some_condition:
        market_phase = "custom_phase"
        key_concerns = ["custom_concern1", "custom_concern2"]
    else:
        # 기본 로직
        ...
```

## 🔍 문제 해결

### 1. **프롬프트 매니저 로드 실패**

```
❌ 프롬프트 매니저 비활성화
```

**해결 방법:**
1. `config/prompts.py` 파일이 존재하는지 확인
2. Python 경로 설정 확인
3. 대시보드 재시작

### 2. **프롬프트 파일 생성 실패**

```
⚠️ 프롬프트 매니저 오류, 기본 프롬프트 사용
```

**해결 방법:**
1. `config/prompts/` 디렉토리 권한 확인
2. 디스크 공간 확인
3. 파일 시스템 접근 권한 확인

### 3. **변수 치환 오류**

**해결 방법:**
1. 템플릿의 변수명과 전달된 키워드 인자명 일치 확인
2. 필수 변수가 모두 제공되었는지 확인
3. 변수 타입 확인 (문자열, 숫자 등)

## 📈 모니터링 및 로그

### 프롬프트 사용 현황 확인

```python
# 프롬프트 시스템 정보 가져오기
info = prompt_manager.get_prompt_info()
print(f"마지막 업데이트: {info['last_updated']}")
print(f"사용 가능한 프롬프트: {info['available_prompt_types']}")
```

### 대시보드에서 모니터링

- 사이드바의 프롬프트 현황 섹션에서 실시간 정보 확인
- 시장 컨텍스트 업데이트 버튼으로 수동 갱신
- 확장 가능한 섹션에서 상세 정보 확인

## 🎉 장점

### 1. **유지보수성 향상**
- 코드 수정 없이 프롬프트 변경 가능
- 버전 관리 시스템에서 프롬프트 변경 이력 추적
- 팀 협업시 프롬프트 공유 용이

### 2. **시장 대응성**
- 시장 상황 변화에 즉시 대응
- 연도별 자동 시장 분석
- 시나리오별 확률 자동 계산

### 3. **확장성**
- 새로운 프롬프트 타입 쉽게 추가
- 다양한 업종별 프롬프트 템플릿 지원
- 다국어 프롬프트 지원 가능

### 4. **안정성**
- 오류 발생시 기본 프롬프트로 폴백
- 파일 시스템 오류 대응
- 백업 및 복구 메커니즘

## 🔮 향후 개선 계획

1. **웹 인터페이스**: 프롬프트 편집을 위한 웹 기반 에디터
2. **버전 관리**: 프롬프트 변경 이력 및 롤백 기능
3. **A/B 테스트**: 다양한 프롬프트 버전의 성능 비교
4. **자동 최적화**: AI를 활용한 프롬프트 자동 개선
5. **다국어 지원**: 영어, 중국어 등 다국어 프롬프트

---

이제 매번 코드를 수정할 필요 없이, 프롬프트 관리 시스템을 통해 효율적으로 GPT 프롬프트를 관리할 수 있습니다! 🚀 