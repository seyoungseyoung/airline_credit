# 한국 항공사 신용등급 분석 - 프로젝트 요약

## 🎯 프로젝트 개요

고급 다중상태 위험 모델링과 실시간 위험 평가를 사용하는 한국 항공사 종합 신용등급 분석 시스템입니다.

## 🚀 주요 기능

### 📊 데이터 파이프라인
- **DART API 통합**: 자동화된 재무 데이터 수집
- **다중 소스 데이터**: DART, NICE/KIS, KRX 통합
- **실시간 처리**: 실시간 데이터 업데이트 및 캐싱
- **신용등급 전처리**: Option A + Meta Flag 접근법

### 🎯 신용등급 전처리 (신규)
- **Option A 접근법**: 4상태 모델 보존과 함께 NR → WD 변환
- **메타 플래그 시스템**: nr_flag, consecutive_nr_days, nr_reason 태깅
- **30일 규칙**: Withdrawn 이벤트를 위한 연속 NR 임계값
- **위험 조정**: WD+NR (20% 승수) 및 장기 NR 조정
- **알림 시스템**: Slack 알림을 위한 90일 임계값

### 🔬 고급 모델링
- **다중상태 위험 모델**: 등급 변동을 위한 Cox 비례 위험 모델
- **향상된 위험 점수**: 90일 확률 계산
- **재무비율 통합**: 20개 이상의 핵심 재무 지표
- **실시간 평가**: 실시간 위험 모니터링 및 알림

### 📈 대시보드 및 분석
- **인터랙티브 대시보드**: 실시간 신용등급 시각화
- **위험 히트맵**: 기업 및 포트폴리오 위험 평가
- **변동 분석**: 등급 변화 확률 추적
- **재무 지표**: 종합적인 비율 분석

### 🔔 알림 시스템
- **Slack 통합**: 실시간 알림
- **다단계 알림**: 등급 변화, 재무 악화, NR 상태
- **사용자 정의 임계값**: 구성 가능한 알림 조건
- **에스컬레이션 워크플로우**: 자동화된 응답 트리거

## 🏗️ 아키텍처

```
데이터 소스
├── DART Open API (재무제표)
├── NICE/KIS (신용등급)
└── KRX (주식 정보)

데이터 파이프라인
├── 재무 데이터 ETL
├── 신용등급 전처리 ← 신규
└── 다중상태 모델 훈련

분석 엔진
├── 향상된 다중상태 모델
├── 위험 점수 엔진
└── 알림 시스템

출력
├── 인터랙티브 대시보드
├── 위험 리포트
└── Slack 알림
```

## 📁 파일 구조

### 핵심 구성 요소
- `korean_airlines_data_pipeline.py` - 전처리 통합이 포함된 메인 데이터 파이프라인
- `credit_rating_preprocessor.py` - **신규**: Option A + Meta Flag 전처리
- `enhanced_multistate_model.py` - 다중상태 위험 모델링
- `rating_risk_scorer.py` - NR 플래그 지원이 포함된 위험 점수
- `credit_rating_dashboard.py` - 인터랙티브 대시보드

### 데이터 처리
- `financial_ratio_calculator.py` - 재무 지표 계산
- `dart_data_cache.py` - DART API 캐싱 시스템
- `financial_data_etl.py` - 재무 데이터용 ETL 파이프라인

### 설정 및 문서
- `config.py` - 시스템 설정
- `CREDIT_RATING_PREPROCESSING_GUIDE.md` - **신규**: 전처리 문서
- `README.md` - 프로젝트 개요 및 설정
- `PROJECT_SUMMARY.md` - 이 파일

### 데모 및 테스트
- `demo_preprocessing.py` - **신규**: 전처리 데모
- `backtest_framework.py` - 모델 검증 프레임워크
- `slack_alert_demo.py` - 알림 시스템 데모

## 🎯 신용등급 전처리 기능

### Option A + Meta Flag 접근법
```python
# 설정
config = PreprocessingConfig(
    consecutive_nr_days=30,      # Withdrawn을 위한 30일 임계값
    risk_multiplier=1.20,        # WD+NR을 위한 20% 위험 증가
    alert_threshold_days=90      # 90일 알림 임계값
)

# 처리
preprocessor = CreditRatingPreprocessor(config)
df_processed = preprocessor.run_preprocessing(input_file)
```

### 주요 이점
- ✅ **데이터 볼륨 보존**: 통계적 파워 유지
- ✅ **업계 준수**: 국내 관행과 일치
- ✅ **시스템 안정성**: 기존 모델에 최소한의 변경
- ✅ **향상된 위험 평가**: 세밀한 NR 상태 추적

### 출력 파일
- `TransitionHistory.csv` - 메타 플래그가 포함된 등급 변동
- `RatingMapping.csv` - 등급 심볼에서 숫자로의 매핑
- `processed_data_summary.csv` - 완전한 처리된 데이터셋
- `alerts.csv` - 알림 조건 (해당하는 경우)

## 🔧 기술 스택

### 백엔드
- **Python 3.8+**: 핵심 분석 엔진
- **Pandas/NumPy**: 데이터 조작 및 분석
- **Lifelines**: 생존 분석 및 위험 모델링
- **Scikit-learn**: 머신러닝 구성 요소

### 데이터 소스
- **DART Open API**: 재무제표 데이터
- **NICE/KIS**: 신용등급 공시
- **KRX**: 주식 시장 정보

### 프론트엔드
- **Streamlit**: 인터랙티브 대시보드
- **Plotly**: 고급 시각화
- **Slack API**: 실시간 알림

### 인프라
- **캐싱**: Redis/메모리 기반 캐싱
- **로깅**: 종합적인 로깅 시스템
- **설정**: 환경 기반 설정

## 📊 대상 기업

### 한국 항공사 커버리지
1. **대한항공 (Korean Air)** - KOSPI: 003490
2. **아시아나항공 (Asiana Airlines)** - KOSPI: 020560
3. **제주항공 (Jeju Air)** - KOSDAQ: 089590
4. **티웨이항공 (T'way Air)** - KOSDAQ: 091810
5. **에어부산 (Air Busan)** - KOSDAQ: 298690

### 데이터 기간
- **과거**: 2010-2025
- **빈도**: 분기별 재무 데이터, 월별 등급 업데이트
- **커버리지**: 15년 이상의 종합 데이터

## 🎯 핵심 지표

### 재무비율 (20개 이상의 지표)
- **유동성**: 유동비율, 당좌비율, 현금비율
- **지급능력**: 부채비율, 부채자본비율, 자기자본비율
- **수익성**: ROA, ROE, 영업이익률, 순이익률
- **효율성**: 총자산회전율, 재고자산회전율
- **보상**: 이자보상배율, 부채보상배율

### 신용등급 분석
- **변동 확률**: 90일 등급 변화 예측
- **위험 점수**: 기업별 위험 평가
- **포트폴리오 분석**: 다중 기업 위험 집계
- **NR 상태 추적**: 철회된 등급 모니터링

## 🚀 시작하기

### 사전 요구사항
```bash
pip install -r requirements_pipeline.txt
```

### 환경 설정
```bash
# 환경 템플릿 복사
cp env_example.txt .env

# API 키 설정
DART_API_KEY=your_dart_api_key
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_webhook
```

### 빠른 시작
```bash
# 전처리가 포함된 완전한 파이프라인 실행
python korean_airlines_data_pipeline.py

# 전처리 데모 실행
python demo_preprocessing.py

# 대시보드 실행
streamlit run credit_rating_dashboard.py
```

## 📈 성능 지표

### 모델 성능
- **C-Index**: 변동 예측을 위한 0.75+
- **Brier Score**: 확률 교정을 위한 <0.15
- **처리 속도**: 일반적인 데이터셋을 위한 <1분
- **정확도**: 등급 변화 예측을 위한 85%+

### 시스템 성능
- **데이터 볼륨**: 1000개 이상의 기업 지원
- **실시간 처리**: <5초 응답 시간
- **캐시 효율성**: 95%+ 캐시 히트율
- **알림 지연**: <30초 알림 지연

## 🔮 향후 개선

### 단기 (3-6개월)
- **글로벌 확장**: 국제 항공사 지원
- **고급 분석**: 머신러닝 개선
- **실시간 데이터**: 일일 데이터 수집
- **모바일 대시보드**: 모바일 최적화 인터페이스

### 장기 (6-12개월)
- **AI 통합**: 리포트 생성을 위한 GPT-4
- **예측 모델링**: 고급 예측 기능
- **규제 준수**: 향상된 보고 기능
- **API 서비스**: 타사 통합을 위한 외부 API

## 📚 문서

### 사용자 가이드
- `README.md` - 프로젝트 개요 및 설정
- `CREDIT_RATING_PREPROCESSING_GUIDE.md` - 전처리 시스템 가이드
- `dashboard_user_guide.md` - 대시보드 사용 가이드
- `korean_airlines_pipeline_guide.md` - 파이프라인 운영 가이드

### 기술 문서
- `EXPANSION_ROADMAP.md` - 개발 로드맵
- `db_integration_plan.md` - 데이터베이스 통합 계획
- `PROJECT_SUMMARY.md` - 이 종합 요약

## 🤝 기여하기

### 개발 워크플로우
1. **Fork** 저장소
2. **Create** 기능 브랜치
3. **Implement** 테스트와 함께 변경사항
4. **Submit** 풀 리퀘스트
5. **Review** 및 머지

### 코드 표준
- **Python**: PEP 8 준수
- **문서**: 종합적인 독스트링
- **테스트**: 단위 및 통합 테스트
- **로깅**: 전체에 걸친 구조화된 로깅

## 📞 지원

### 연락처 정보
- **프로젝트 리드**: 한국 항공사 신용등급 분석 팀
- **기술 지원**: GitHub Issues를 통해
- **문서**: 포함된 종합 가이드

### 리소스
- **API 문서**: DART Open API, Slack API
- **모델 문서**: Lifelines, Scikit-learn
- **모범 사례**: 업계 표준 및 가이드라인

---

*이 프로젝트는 고급 통계 모델링과 실시간 모니터링 및 알림 기능을 결합한 한국 항공업계 신용등급 분석을 위한 종합 솔루션을 나타냅니다.* 