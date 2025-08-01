# RAG 시스템 가이드 (항공업계 검색 및 요약)

## 개요

RAG (Retrieval-Augmented Generation) 시스템은 항공업계 최신 정보를 자동으로 검색하고 요약하여 GPT 프롬프트에 반영하는 시스템입니다. 이를 통해 GPT가 항상 최신의 항공업계 동향을 반영한 분석을 제공할 수 있습니다.

## 주요 기능

### 1. 자동 웹 검색
- **네이버 뉴스 검색**: 항공업계 관련 최신 뉴스 검색
- **구글 검색**: 백업 검색 엔진으로 활용
- **키워드 기반 검색**: 항공업계 관련 핵심 키워드로 검색

### 2. 콘텐츠 요약
- **GPT-4o-mini 활용**: 검색된 기사를 AI가 요약
- **핵심 포인트 추출**: 중요한 정보만 선별
- **종합 요약**: 여러 기사를 종합하여 전체 동향 파악

### 3. 프롬프트 통합
- **자동 프롬프트 업데이트**: 검색된 정보를 GPT 프롬프트에 자동 반영
- **컨텍스트 제공**: 항공업계 현황을 GPT 분석에 반영
- **실시간 업데이트**: 최신 정보로 지속적 업데이트

## 시스템 구조

```
src/rag/
├── __init__.py                 # RAG 모듈 초기화
├── search_engine.py           # 웹 검색 엔진
├── content_summarizer.py      # 콘텐츠 요약기
└── airline_industry_rag.py    # 메인 RAG 시스템
```

### 1. SearchEngine 클래스
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

### 2. ContentSummarizer 클래스
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
- 핵심 포인트 추출

### 3. AirlineIndustryRAG 클래스
```python
class AirlineIndustryRAG:
    def get_airline_industry_context(force_update=False)
    def get_prompt_context()
    def get_cache_info()
```

**주요 기능:**
- 검색 및 요약 통합 관리
- 캐시 시스템 관리
- 프롬프트 컨텍스트 생성

## 사용법

### 1. 대시보드에서 사용

#### RAG 시스템 활성화
1. 대시보드 사이드바에서 "🔍 RAG 시스템 (항공업계 검색)" 섹션 확인
2. 시스템 상태가 "✅ RAG 시스템 활성화"로 표시되는지 확인

#### 정보 업데이트
1. "🔄 항공업계 정보 업데이트" 버튼 클릭
2. 검색 및 요약 진행 상황 확인
3. 업데이트 완료 후 GPT 리포트 생성 시 최신 정보 반영

#### 상세 정보 확인
1. "📋 RAG 상세 정보" 확장하여 검색 키워드, 핵심 포인트, 정보 출처 확인
2. "⚙️ RAG 설정" 확장하여 시스템 설정 확인

### 2. 프로그래밍 방식 사용

```python
from src.rag.airline_industry_rag import AirlineIndustryRAG

# RAG 시스템 초기화
rag_system = AirlineIndustryRAG(openai_api_key)

# 항공업계 컨텍스트 가져오기
context = rag_system.get_airline_industry_context()

# 프롬프트 컨텍스트 생성
prompt_context = rag_system.get_prompt_context()

# 캐시 정보 확인
cache_info = rag_system.get_cache_info()
```

## 검색 키워드

시스템에서 자동으로 검색하는 항공업계 관련 키워드:

1. **항공업계** - 현재 연도별 동향
2. **항공사 경영현황** - 경영 상태 정보
3. **항공업계 전망** - 미래 전망 분석
4. **항공사 실적** - 재무 실적 정보
5. **항공업계 규제** - 규제 관련 정보
6. **항공사 부채** - 부채 현황
7. **항공업계 투자** - 투자 동향
8. **항공사 신용등급** - 신용등급 정보
9. **항공업계 리스크** - 리스크 요인
10. **항공사 대출** - 대출 관련 정보

## 캐시 시스템

### 캐시 구조
```
rag_cache/
└── airline_industry_cache.json
```

### 캐시 정보
- **유효기간**: 24시간
- **저장 내용**: 검색 결과, 요약 정보, 타임스탬프
- **자동 갱신**: 캐시 만료 시 자동으로 새로운 정보 검색

### 캐시 관리
```python
# 캐시 정보 확인
cache_info = rag_system.get_cache_info()

# 강제 업데이트
context = rag_system.get_airline_industry_context(force_update=True)
```

## 설정 및 환경

### 필요한 패키지
```bash
pip install requests beautifulsoup4 openai
```

### 환경 변수
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Python 경로 설정
```python
import sys
sys.path.append('src')
```

## 오류 처리

### 일반적인 오류 및 해결방법

1. **RAG 시스템 비활성화**
   - 원인: `src/rag/` 디렉토리 누락 또는 임포트 오류
   - 해결: 디렉토리 구조 확인 및 Python 경로 설정

2. **OpenAI API 오류**
   - 원인: API 키 미설정 또는 잘못된 키
   - 해결: `.env` 파일에 올바른 API 키 설정

3. **검색 실패**
   - 원인: 네트워크 오류 또는 웹사이트 구조 변경
   - 해결: 네트워크 연결 확인 및 폴백 정보 사용

4. **요약 실패**
   - 원인: OpenAI API 할당량 초과 또는 콘텐츠 부족
   - 해결: API 할당량 확인 및 기본 정보 사용

## 성능 최적화

### 검색 최적화
- 상위 5개 키워드만 사용하여 검색 속도 향상
- 각 검색 간 1초 간격으로 요청 제한
- 중복 URL 자동 제거

### 요약 최적화
- 콘텐츠 길이 제한 (최대 5000자)
- 요약 길이 제한 (최대 500자)
- 핵심 포인트 최대 5개로 제한

### 캐시 최적화
- 24시간 캐시 유효기간으로 API 호출 최소화
- JSON 형태로 효율적 저장
- 자동 만료 처리

## 모니터링 및 로깅

### 로그 레벨
- **INFO**: 정상적인 검색 및 요약 과정
- **WARNING**: 부분적 실패 또는 폴백 사용
- **ERROR**: 심각한 오류 발생

### 모니터링 지표
- 검색된 기사 수
- 요약 성공률
- 캐시 히트율
- API 호출 횟수

## 향후 개선 계획

### 기능 개선
1. **다양한 검색 엔진 추가**: Bing, Yahoo 등
2. **언어별 검색**: 영어, 중국어 등 다국어 지원
3. **이미지 분석**: 항공업계 관련 이미지 분석 추가

### 성능 개선
1. **병렬 처리**: 여러 검색을 동시에 수행
2. **스마트 캐싱**: 중요도에 따른 캐시 우선순위
3. **실시간 업데이트**: 웹소켓을 통한 실시간 정보 수집

### 사용성 개선
1. **웹 인터페이스**: 독립적인 RAG 관리 페이지
2. **API 엔드포인트**: RESTful API 제공
3. **알림 시스템**: 중요 정보 발견 시 알림

## 문제 해결

### 자주 묻는 질문

**Q: RAG 시스템이 왜 비활성화되어 있나요?**
A: 다음을 확인해주세요:
1. `src/rag/` 디렉토리가 존재하는지
2. OpenAI API 키가 설정되어 있는지
3. 필요한 패키지가 설치되어 있는지

**Q: 검색 결과가 없습니다.**
A: 다음을 확인해주세요:
1. 인터넷 연결 상태
2. 검색 키워드의 적절성
3. 폴백 정보 사용 여부

**Q: 요약이 부정확합니다.**
A: 다음을 확인해주세요:
1. OpenAI API 할당량
2. 검색된 콘텐츠의 품질
3. 요약 프롬프트의 적절성

## 지원 및 문의

RAG 시스템 관련 문제나 개선 제안이 있으시면:
1. GitHub Issues에 등록
2. 프로젝트 문서 확인
3. 개발팀에 직접 문의

---

**버전**: 1.0.0  
**최종 업데이트**: 2025년 8월 1일  
**작성자**: Korean Airlines Credit Rating Analysis Team 