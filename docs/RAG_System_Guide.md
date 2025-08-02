# RAG 시스템 가이드

## 🎯 개요

RAG (Retrieval-Augmented Generation) 시스템은 항공업계 최신 정보를 자동으로 검색하고 요약하여 GPT 프롬프트에 반영하는 시스템입니다. 이를 통해 GPT가 항상 최신의 항공업계 동향을 반영한 분석을 제공할 수 있습니다.

## 🚀 주요 기능

### 1. **자동 웹 검색**
- **네이버 뉴스 검색**: 항공업계 관련 최신 뉴스 검색
- **구글 검색**: 백업 검색 엔진으로 활용
- **키워드 기반 검색**: 항공업계 관련 핵심 키워드로 검색

### 2. **콘텐츠 요약**
- **GPT-4o-mini 활용**: 검색된 기사를 AI가 요약
- **핵심 포인트 추출**: 중요한 정보만 선별
- **종합 요약**: 여러 기사를 종합하여 전체 동향 파악

### 3. **프롬프트 통합**
- **자동 프롬프트 업데이트**: 검색된 정보를 GPT 프롬프트에 자동 반영
- **컨텍스트 제공**: 항공업계 현황을 GPT 분석에 반영
- **실시간 업데이트**: 최신 정보로 지속적 업데이트

## 🏗️ 시스템 구조

```
src/rag/
├── __init__.py                 # RAG 모듈 초기화
├── search_engine.py           # 웹 검색 엔진
├── content_summarizer.py      # 콘텐츠 요약기
└── airline_industry_rag.py    # 메인 RAG 시스템
```

## 🔧 핵심 클래스

### 1. **SearchEngine 클래스**
```python
class SearchEngine:
    def search_airline_industry(query, max_results=5)
    def extract_content(url)
    def search_airline_keywords()
```

**주요 기능:**
- 네이버 뉴스 및 구글 검색
- 웹 페이지 콘텐츠 추출
- 항공업계 관련 키워드 관리

### 2. **ContentSummarizer 클래스**
```python
class ContentSummarizer:
    def summarize_content(content, max_length=500)
    def summarize_multiple_contents(contents)
    def _create_combined_summary(summaries)
    def _extract_key_points(summaries)
```

**주요 기능:**
- 개별 기사 요약
- 여러 기사 종합 요약
- 핵심 포인트 자동 추출

### 3. **AirlineIndustryRAG 클래스**
```python
class AirlineIndustryRAG:
    def get_airline_industry_context(force_update=False)
    def _search_and_summarize()
    def _remove_duplicates(results)
```

**주요 기능:**
- 전체 RAG 시스템 관리
- 캐시 시스템 연동
- 중복 제거 및 품질 관리

## 📊 검색 키워드

### 항공업계 핵심 키워드
```python
AIRLINE_KEYWORDS = [
    "한국 항공업계",
    "대한항공 아시아나항공",
    "국제선 수요",
    "항공사 실적",
    "항공유 가격",
    "항공업계 규제",
    "친환경 항공기",
    "항공업계 디지털화"
]
```

## 🔍 검색 프로세스

### 1. **키워드 기반 검색**
```python
# 상위 3개 키워드로 검색
keywords = search_engine.search_airline_keywords()
for keyword in keywords[:3]:
    results = search_engine.search_airline_industry(keyword, max_results=2)
```

### 2. **콘텐츠 추출 및 요약**
```python
# 웹 페이지 콘텐츠 추출
content = search_engine.extract_content(url)

# AI 요약 수행
summary = summarizer.summarize_content(content)
```

### 3. **종합 컨텍스트 생성**
```python
# 여러 기사 종합 요약
combined_summary = summarizer.summarize_multiple_contents(contents)

# 컨텍스트 구성
context = {
    "summary": combined_summary,
    "key_points": key_points,
    "sources": sources,
    "timestamp": datetime.now().isoformat()
}
```

## 💾 캐시 시스템

### 캐시 구조
```python
CACHE_FILE = "rag_cache/airline_industry_context.json"
CACHE_DURATION_HOURS = 6  # 6시간마다 업데이트
```

### 캐시 관리
- **자동 만료**: 6시간 후 자동 업데이트
- **수동 갱신**: `force_update=True` 옵션
- **오류 처리**: 캐시 실패시 기본 정보 제공

## 🎯 활용 방법

### 1. **대시보드에서 사용**
```python
# RAG 시스템 초기화
rag_system = AirlineIndustryRAG(openai_api_key="your_api_key")

# 항공업계 컨텍스트 가져오기
context = rag_system.get_airline_industry_context()
```

### 2. **GPT 프롬프트에 반영**
```python
# GPT 분석에 RAG 컨텍스트 포함
prompt = f"""
현재 항공업계 상황:
{context['summary']}

주요 이슈:
{chr(10).join(context['key_points'])}

위 정보를 바탕으로 신용위험을 분석해주세요.
"""
```

### 3. **실시간 업데이트**
- 대시보드 사이드바에서 "🔍 RAG 시스템" 섹션
- "업데이트" 버튼으로 수동 갱신
- 자동 6시간 주기 업데이트

## 📈 성능 최적화

### 1. **검색 효율성**
- 상위 3개 키워드만 사용 (안정성 향상)
- 요청 간격 조절 (2-3초)
- 중복 결과 자동 제거

### 2. **요약 품질**
- 최소 콘텐츠 길이 확인 (100자 이상)
- GPT-4o-mini 최적화 설정
- 오류 발생시 기본 정보 제공

### 3. **캐시 최적화**
- 6시간 캐시 유효기간
- JSON 형태로 효율적 저장
- 메모리 사용량 최소화

## 🔧 설정 및 커스터마이징

### 환경 변수 설정
```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# 검색 설정 (선택사항)
SEARCH_MAX_RESULTS=5
CACHE_DURATION_HOURS=6
```

### 검색 키워드 커스터마이징
```python
# src/rag/search_engine.py에서 키워드 수정
AIRLINE_KEYWORDS = [
    "커스텀 키워드 1",
    "커스텀 키워드 2",
    # ... 추가 키워드
]
```

## 🚨 문제 해결

### 1. **검색 실패**
- 네트워크 연결 확인
- API 키 유효성 확인
- 요청 간격 조정

### 2. **요약 실패**
- OpenAI API 키 확인
- 콘텐츠 길이 확인
- 기본 정보로 폴백

### 3. **캐시 오류**
- 디렉토리 권한 확인
- 디스크 공간 확인
- 수동 캐시 삭제

## 📊 모니터링

### 대시보드에서 확인
- RAG 시스템 상태 표시
- 마지막 업데이트 시간
- 검색된 기사 수
- 캐시 상태

### 로그 확인
```python
import logging
logging.getLogger('src.rag').setLevel(logging.INFO)
```

---

**🔍 RAG 시스템을 통해 항상 최신의 항공업계 정보를 반영한 정확한 분석을 제공할 수 있습니다!** 