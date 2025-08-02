# 한국 항공사 신용등급 데이터 파이프라인

## 🎯 개요

이 파이프라인은 주요 한국 항공사들의 신용등급 변동 데이터를 수집하고 처리합니다:

- **대한항공** (Korean Air) - KOSPI: 003490
- **아시아나항공** (Asiana Airlines) - KOSPI: 020560  
- **제주항공** (Jeju Air) - KOSDAQ: 089590
- **티웨이항공** (T'way Air) - KOSDAQ: 091810

## 📊 데이터 소스

### 1. DART API (재무 데이터)
- **소스**: [DART Open API](https://opendart.fss.or.kr/)
- **기간**: 2010Q1 ~ 2025Q2
- **데이터**: 분기별 재무제표
- **출력**: 기업당 분기별 20개 핵심 재무비율

### 2. 신용평가사 (등급 이력)
- **NICE신용평가** (NICE Credit Rating)
- **한국신용평가** (KIS Credit Rating)
- **데이터**: effective_date, 등급 변동
- **형식**: 표준화된 등급 체계 (AAA to D, NR)

## 🏗️ 파이프라인 아키텍처

```
데이터 수집 → 처리 → 정규화 → 출력
     ↓           ↓        ↓       ↓
  DART API    재무비율   CSV 형식  필요 파일
  등급 API    계산      매핑
```

## 📁 출력 파일

### TransitionHistory.csv
```csv
Id,Date,RatingSymbol
1,31-Dec-10,BBB
1,30-Jun-11,BBB
1,31-Dec-11,BB
...
```

### RatingMapping.csv
```csv
RatingSymbol,RatingNumber
AAA,0
AA,1
A,2
BBB,3
BB,4
B,5
CCC,6
D,7
NR,8
```

## 🚀 빠른 시작

### 사전 요구사항
```bash
# conda 환경 활성화
conda activate credit_rating_transition

# 추가 의존성 설치 (필요시)
pip install requests beautifulsoup4 lxml python-dotenv tqdm
```

### 기본 사용법
```bash
# 샘플 데이터로 실행 (API 키 불필요)
python run_korean_airlines_pipeline.py
```

### DART API 사용 (실제 데이터)
```bash
# 1. https://opendart.fss.or.kr/에서 DART API 키 발급
# 2. 환경 변수 설정
export DART_API_KEY=your_api_key_here

# 3. 파이프라인 실행
python run_korean_airlines_pipeline.py
```

## 📈 현재 상태

### ✅ 완료된 기능

1. **대상 기업 정의**
   - [x] 4개 주요 한국 항공사 식별
   - [x] 주식 코드 및 시장 분류
   - [x] 전환 매트릭스용 발행자 ID 매핑

2. **DART 스크래퍼 프레임워크**
   - [x] DART Open API 통합
   - [x] 분기별 재무제표 수집
   - [x] 20개 재무비율 계산
   - [x] 오류 처리 및 요청 제한

3. **신용등급 전처리**
   - [x] Option A + Meta Flag 접근법
   - [x] NR → WD 변환 로직
   - [x] 30일 연속 규칙
   - [x] 메타 플래그 시스템

4. **데이터 정규화**
   - [x] 등급 심볼 → 숫자 매핑
   - [x] 날짜 형식 표준화
   - [x] 중복 데이터 제거
   - [x] 데이터 품질 검증

### 🔄 진행 중인 작업

1. **실시간 데이터 수집**
   - [ ] 자동화된 데이터 수집 스케줄링
   - [ ] 실시간 알림 시스템
   - [ ] 데이터 변경 감지

2. **성능 최적화**
   - [ ] 병렬 처리 구현
   - [ ] 캐싱 시스템 개선
   - [ ] 메모리 사용량 최적화

## 🔧 설정 및 구성

### 환경 변수
```bash
# DART API 설정
DART_API_KEY=your_dart_api_key_here

# 데이터 소스 설정
USE_REAL_DATA=true  # true: 실제 API, false: 샘플 데이터
CACHE_ENABLED=true  # 캐싱 활성화 여부

# 출력 설정
OUTPUT_DIRECTORY=data/processed
LOG_LEVEL=INFO
```

### 설정 파일
```python
# config/config.py
DART_API_BASE_URL = "https://opendart.fss.or.kr/api"
RATE_LIMIT_DELAY = 1.0  # API 요청 간격 (초)
MAX_RETRIES = 3         # 최대 재시도 횟수
```

## 📊 데이터 처리 과정

### 1. 데이터 수집 단계
```python
# DART API에서 재무 데이터 수집
financial_data = dart_scraper.collect_financial_data(
    companies=target_companies,
    start_date="2010-01-01",
    end_date="2025-06-30"
)

# 신용등급 데이터 수집
rating_data = rating_scraper.collect_rating_history(
    companies=target_companies
)
```

### 2. 전처리 단계
```python
# 신용등급 전처리 (Option A + Meta Flag)
preprocessor = CreditRatingPreprocessor(config)
processed_data = preprocessor.run_preprocessing(rating_data)
```

### 3. 정규화 단계
```python
# 데이터 정규화 및 매핑
normalizer = DataNormalizer()
normalized_data = normalizer.normalize_data(processed_data)
```

### 4. 출력 단계
```python
# CSV 파일로 출력
output_writer = OutputWriter(output_directory)
output_writer.write_transition_history(normalized_data)
output_writer.write_rating_mapping(normalized_data)
```

## 🎯 사용 예시

### 기본 파이프라인 실행
```python
from src.data.korean_airlines_data_pipeline import KoreanAirlinesDataPipeline

# 파이프라인 초기화
pipeline = KoreanAirlinesDataPipeline()

# 전체 파이프라인 실행
pipeline.run_full_pipeline()

# 결과 확인
print("✅ 파이프라인 실행 완료!")
print(f"📁 출력 파일: {pipeline.output_directory}")
```

### 단계별 실행
```python
# 1. 데이터 수집만 실행
pipeline.collect_data()

# 2. 전처리만 실행
pipeline.preprocess_data()

# 3. 정규화만 실행
pipeline.normalize_data()

# 4. 출력만 실행
pipeline.write_output()
```

## 🔍 데이터 품질 검증

### 자동 검증
```python
# 데이터 품질 검증 실행
validator = DataValidator()
validation_results = validator.validate_pipeline_output()

# 검증 결과 확인
if validation_results.is_valid:
    print("✅ 데이터 품질 검증 통과")
else:
    print("❌ 데이터 품질 문제 발견:")
    for issue in validation_results.issues:
        print(f"  - {issue}")
```

### 수동 검증
```bash
# 출력 파일 확인
ls -la data/processed/

# 데이터 통계 확인
python -c "
import pandas as pd
df = pd.read_csv('data/processed/TransitionHistory.csv')
print(f'총 레코드 수: {len(df)}')
print(f'기간: {df.Date.min()} ~ {df.Date.max()}')
print(f'고유 등급: {df.RatingSymbol.nunique()}개')
"
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. DART API 오류
```bash
# API 키 확인
echo $DART_API_KEY

# 네트워크 연결 확인
curl -I https://opendart.fss.or.kr/api
```

#### 2. 메모리 부족
```python
# 배치 처리로 메모리 사용량 줄이기
pipeline = KoreanAirlinesDataPipeline(batch_size=1000)
```

#### 3. 데이터 누락
```python
# 누락된 데이터 확인
missing_data = pipeline.check_missing_data()
if missing_data:
    print("누락된 데이터 발견:")
    for item in missing_data:
        print(f"  - {item}")
```

## 📈 성능 모니터링

### 실행 시간 측정
```python
import time

start_time = time.time()
pipeline.run_full_pipeline()
end_time = time.time()

print(f"총 실행 시간: {end_time - start_time:.2f}초")
```

### 메모리 사용량 모니터링
```python
import psutil

process = psutil.Process()
memory_usage = process.memory_info().rss / 1024 / 1024  # MB
print(f"메모리 사용량: {memory_usage:.2f} MB")
```

## 🔮 향후 개선 계획

### 단기 계획 (1-3개월)
- [ ] 실시간 데이터 수집 자동화
- [ ] 웹 인터페이스 추가
- [ ] 성능 최적화

### 중기 계획 (3-6개월)
- [ ] 추가 항공사 지원
- [ ] 국제 항공사 데이터 수집
- [ ] 고급 분석 기능 추가

### 장기 계획 (6-12개월)
- [ ] AI 기반 데이터 품질 검증
- [ ] 예측 모델 통합
- [ ] 클라우드 배포 지원

---

**✈️ 한국 항공업계의 신용위험 분석을 위한 강력한 데이터 파이프라인입니다!** 