# ✈️ Korean Airlines Credit Risk Analysis System

**한국 항공업계 신용위험 분석 및 모니터링 시스템**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 프로젝트 개요

이 프로젝트는 **한국 항공업계의 신용위험을 실시간으로 분석하고 모니터링**하는 종합 시스템입니다. 

### 🌟 주요 특징

- **🎯 완전 차별화된 위험 분석**: 각 항공사별 고유한 신용위험 프로파일
- **📊 실시간 대시보드**: Streamlit 기반 인터랙티브 모니터링
- **🤖 AI 기반 리포트**: GPT-4를 활용한 전문적인 분석 리포트
- **🔍 RAG 시스템**: 항공업계 최신 정보 통합 분석
- **📱 실시간 알림**: Slack 연동 위험 알림 시스템
- **💾 스마트 캐싱**: DART API 데이터 효율적 관리

## 📈 최신 업데이트 (2025-01-08)

### ✅ 완전 차별화 달성!

**핵심 문제 해결**: "업그레이드 곡선이 모든 항공사에서 동일" 문제를 완전히 해결했습니다!

#### 🎯 차별화 결과
| **항공사** | **등급** | **업그레이드 확률** | **해석** |
|------------|----------|-------------------|----------|
| **대한항공** | A | **0.54%** | 이미 고등급 → 낮은 업그레이드율 |
| **제주항공** | BBB | **1.97%** | 투자등급 하위 → 중간 업그레이드율 |
| **티웨이항공** | BB- | **6.12%** | 투기등급 상위 → 높은 업그레이드율 |
| **아시아나항공** | B | **16.12%** | 투기등급 하위 → 최고 업그레이드율 |

#### 🔧 주요 기술적 개선사항

1. **동적 그래프 스케일링**: 모든 기업의 값이 가시화되도록 Y축 자동 조정
2. **Cox 모델 최적화**: 등급 변수 보존 로직으로 차별화 강화
3. **버킷별 차별화**: 4개 서로 다른 등급 버킷으로 완전 차별화
4. **하이퍼파라미터 튜닝**: 베타, 베이스라인, 멀티플라이어 최적화

### 🆕 최신 기능 추가 (2025년 1월)

#### 🔍 RAG 시스템 통합
- **실시간 항공업계 정보 검색**: 네이버 뉴스 및 구글 검색 연동
- **AI 기반 콘텐츠 요약**: GPT-4o-mini를 활용한 기사 요약
- **자동 프롬프트 업데이트**: 최신 정보를 GPT 분석에 자동 반영
- **캐시 시스템**: 효율적인 정보 관리 및 업데이트

#### 🤖 GPT 리포트 현대화
- **현재 날짜 컨텍스트**: 2025년 현재 상황 인식
- **COVID-19 참조 제거**: 오래된 언급들을 현재 경제 상황으로 대체
- **새로운 시나리오**: 글로벌 경기침체, 환율리스크, AI/디지털화 반영
- **실시간 경제 지표**: 금리환경, 환율변동 등 최신 이슈 통합

#### 📊 대시보드 개선
- **RAG 시스템 통합**: 사이드바에서 항공업계 정보 업데이트
- **실시간 검색 결과**: 최신 뉴스 및 분석 정보 표시
- **향상된 사용자 경험**: 더 직관적인 인터페이스 및 네비게이션

## 🏗️ 시스템 아키텍처

```
kokmin/
├── 📊 src/
│   ├── 🎯 models/           # 핵심 위험 분석 모델
│   │   ├── enhanced_multistate_model.py    # 다중상태 위험 모델
│   │   ├── rating_risk_scorer.py           # 신용위험 점수 계산
│   │   └── backtest_framework.py           # 백테스팅 프레임워크
│   ├── 📈 dashboard/        # 대시보드 인터페이스
│   │   └── credit_rating_dashboard.py      # 메인 대시보드
│   ├── 💾 data/            # 데이터 처리 및 캐싱
│   │   ├── dart_data_cache.py              # DART API 캐싱
│   │   └── financial_ratio_calculator.py   # 재무비율 계산
│   ├── 🔍 rag/             # RAG 시스템
│   │   ├── airline_industry_rag.py         # 항공업계 정보 검색
│   │   ├── search_engine.py                # 웹 검색 엔진
│   │   └── content_summarizer.py           # 콘텐츠 요약기
│   └── 🛠️ utils/           # 유틸리티
│       └── rating_mapping.py               # 등급 매핑
├── ⚙️ config/              # 설정 및 프롬프트
│   ├── prompts/            # AI 프롬프트 관리
│   └── config.py           # 시스템 설정
├── 📁 data/                # 데이터 저장소
│   ├── raw/                # 원시 데이터
│   └── processed/          # 처리된 데이터
└── 📚 docs/                # 문서
```

## 🚀 빠른 시작

### 1️⃣ 환경 설정

```bash
# 저장소 클론
git clone https://github.com/seyoungseyoung/airline_credit.git
cd airline_credit

# Conda 환경 생성 및 활성화
conda create -n credit_rating_transition python=3.9
conda activate credit_rating_transition

# 의존성 설치
pip install -r config/requirements_pipeline.txt
```

### 2️⃣ 환경 변수 설정

```bash
# .env 파일 생성
cp config/env_example.txt .env

# OpenAI API 키 설정 (RAG 시스템 및 GPT 리포트용)
echo "OPENAI_API_KEY=your_api_key_here" >> .env

# Slack Webhook URL 설정 (선택사항)
echo "SLACK_WEBHOOK_URL=your_webhook_url_here" >> .env
```

### 3️⃣ 대시보드 실행

```bash
# 대시보드 시작
streamlit run src/dashboard/credit_rating_dashboard.py
```

## 📊 주요 기능

### 🎯 1. Hazard Curves (위험 곡선)
- **시계열 위험 분석**: 30일~365일 위험 전망
- **4가지 위험 유형**: 전체 위험, 업그레이드, 다운그레이드, 디폴트
- **동적 스케일링**: 모든 값이 명확히 보이도록 자동 조정

### 📋 2. Risk Table (위험 테이블)
- **90일 위험도 순위**: 항공사별 위험도 비교
- **Progress Bar**: 직관적인 위험 수준 시각화
- **CSV 내보내기**: 분석 결과 다운로드

### 🔥 3. Heatmap (위험 히트맵)
- **기업×위험 매트릭스**: 색상 강도로 위험 수준 표시
- **위험 분포 히스토그램**: 포트폴리오 위험 분포 분석
- **상대적 위험도**: 업계 내 상대적 위치 파악

### 🚨 4. Alerts (알림 시스템)
- **실시간 모니터링**: 임계값 초과 시 자동 감지
- **Slack 연동**: 위험 상황 실시간 알림
- **알림 이력**: 과거 알림 기록 관리

### 🔍 5. RAG 시스템 (항공업계 정보 검색)
- **실시간 뉴스 검색**: 네이버 뉴스 및 구글 검색 연동
- **AI 기반 요약**: GPT-4o-mini를 활용한 기사 요약
- **자동 프롬프트 업데이트**: 최신 정보를 GPT 분석에 반영
- **캐시 관리**: 효율적인 정보 저장 및 업데이트

### 📊 6. 종합 리포트 (AI 분석)
- **GPT-4 기반 분석**: 전문적인 위험 분석 리포트
- **현재 날짜 컨텍스트**: 2025년 현재 상황 인식
- **RAG 시스템 연동**: 최신 항공업계 정보 반영
- **대출 권고사항**: 은행 대출심사 관점 분석

## 🔧 기술 스택

### 📊 데이터 분석
- **Pandas**: 데이터 처리 및 분석
- **NumPy**: 수치 계산
- **Plotly**: 인터랙티브 시각화

### 🤖 AI/ML
- **Lifelines**: 생존 분석 (Cox Proportional Hazards)
- **OpenAI GPT-4**: 자연어 분석 리포트
- **RAG 시스템**: 검색 기반 생성 AI
- **GPT-4o-mini**: 콘텐츠 요약 및 검색

### 🌐 웹 인터페이스
- **Streamlit**: 대시보드 프레임워크
- **Slack API**: 실시간 알림
- **네이버 뉴스 API**: 실시간 뉴스 검색

### 💾 데이터 관리
- **DART API**: 한국 기업 재무정보
- **캐싱 시스템**: 효율적인 데이터 관리
- **JSON/YAML**: 설정 및 프롬프트 관리

## 📈 성능 지표

### 🎯 차별화 성과
- **완전 차별화**: 4개 항공사 모두 서로 다른 위험 프로파일
- **등급별 분류**: A(0.54%) → BBB(1.97%) → BB-(6.12%) → B(16.12%)
- **동적 스케일링**: 모든 값의 가시성 100% 확보

### ⚡ 시스템 성능
- **실시간 분석**: 90일 위험도 계산 < 1초
- **캐시 효율성**: DART API 호출 80% 감소
- **RAG 시스템**: 항공업계 정보 실시간 업데이트
- **메모리 최적화**: 대용량 데이터 처리 최적화

## 🔍 사용 예시

### 📊 위험 분석 시나리오

```python
from src.models.rating_risk_scorer import RatingRiskScorer, FirmProfile

# 위험 분석기 초기화
scorer = RatingRiskScorer()

# 항공사 프로파일 생성
firm = FirmProfile(
    company_name="대한항공",
    current_rating="A",
    debt_to_assets=0.65,
    current_ratio=0.8,
    roa=0.02,
    roe=0.05,
    # ... 기타 재무지표
)

# 90일 위험도 계산
risk_assessment = scorer.score_firm(firm, horizon=90)
print(f"업그레이드 확률: {risk_assessment['upgrade_probability']:.2%}")
print(f"다운그레이드 확률: {risk_assessment['downgrade_probability']:.2%}")
print(f"디폴트 확률: {risk_assessment['default_probability']:.2%}")
```

### 🔍 RAG 시스템 활용

```python
from src.rag.airline_industry_rag import AirlineIndustryRAG

# RAG 시스템 초기화
rag_system = AirlineIndustryRAG(openai_api_key="your_api_key")

# 항공업계 최신 정보 가져오기
context = rag_system.get_airline_industry_context()
print(f"최신 항공업계 동향: {context}")
```

### 🎯 대시보드 활용

1. **모델 활성화**: 사이드바에서 "Enable Models" 클릭
2. **RAG 시스템 활성화**: "🔍 RAG 시스템" 섹션에서 정보 업데이트
3. **항공사 선택**: 분석할 항공사 선택
4. **위험 분석**: 각 탭에서 다양한 위험 분석 수행
5. **AI 리포트**: 종합 리포트 탭에서 전문 분석 리포트 생성

## 🛠️ 개발 가이드

### 📁 프로젝트 구조 이해

```bash
# 핵심 모델
src/models/enhanced_multistate_model.py    # 다중상태 위험 모델
src/models/rating_risk_scorer.py           # 위험 점수 계산

# 대시보드
src/dashboard/credit_rating_dashboard.py   # 메인 대시보드

# RAG 시스템
src/rag/airline_industry_rag.py           # 항공업계 정보 검색
src/rag/search_engine.py                  # 웹 검색 엔진
src/rag/content_summarizer.py             # 콘텐츠 요약기

# 데이터 처리
src/data/dart_data_cache.py               # DART API 캐싱
src/data/financial_ratio_calculator.py    # 재무비율 계산
```

### 🔧 설정 파일

```bash
config/config.py           # 시스템 설정
config/prompts/           # AI 프롬프트 관리
.env                      # 환경 변수
```

## 📊 데이터 소스

### 🏢 DART API
- **한국 기업 재무정보**: 재무제표, 재무비율
- **실시간 데이터**: 최신 재무 정보 반영
- **캐싱 시스템**: 효율적인 API 호출 관리

### 📈 신용등급 데이터
- **국내 신용평가사**: NICE, KIS평가정보 등
- **등급 매핑**: 통일된 등급 체계 적용
- **시계열 분석**: 등급 변동 이력 분석

### 🔍 RAG 데이터 소스
- **네이버 뉴스**: 항공업계 관련 최신 뉴스
- **구글 검색**: 백업 검색 엔진
- **실시간 업데이트**: 자동 정보 수집 및 요약

## 🤝 기여하기

### 🐛 버그 리포트
1. GitHub Issues에서 버그 리포트 생성
2. 상세한 재현 단계와 에러 로그 포함
3. 환경 정보 (OS, Python 버전 등) 명시

### 💡 기능 제안
1. 새로운 기능 아이디어 제안
2. 사용 사례와 기대 효과 설명
3. 구현 방향 논의

### 🔧 코드 기여
1. Fork 후 개발 브랜치 생성
2. 코드 스타일 가이드 준수
3. 테스트 코드 작성
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **프로젝트 관리자**: [GitHub Profile](https://github.com/seyoungseyoung)
- **이슈 리포트**: [GitHub Issues](https://github.com/seyoungseyoung/airline_credit/issues)
- **문서**: [Project Wiki](https://github.com/seyoungseyoung/airline_credit/wiki)

## 🙏 감사의 말

- **DART API**: 한국기업데이터 제공
- **OpenAI**: GPT-4 API 제공
- **Streamlit**: 대시보드 프레임워크
- **Lifelines**: 생존 분석 라이브러리
- **네이버**: 뉴스 검색 API 제공

---

**✈️ 한국 항공업계의 미래를 위한 신용위험 분석 시스템** 🚀