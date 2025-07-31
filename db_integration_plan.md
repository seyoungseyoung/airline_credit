# 🗄️ Database Integration Plan
## Korean Airlines Credit Risk System

### 📋 **단계별 DB 도입 전략**

#### **Phase 0: 현재 유지 (권고)**
```yaml
Current State (PoC):
  Data Storage: 파일 기반 (CSV, JSON, pickle)
  Cache System: DART API 캐시 (완료)
  Target: 5개 항공사
  Users: 단일/소규모 팀
  
Recommendation: ✅ 현재 시스템 유지
Reason: 
  - 현재 요구사항에 충분
  - 개발 속도 최우선
  - 캐시 시스템으로 성능 확보
```

#### **Phase 1: 하이브리드 도입 (3-6개월 후)**
```yaml
Trigger Conditions:
  - 사용자 5명 이상
  - 항공사 10개 이상 확장
  - 실시간 동시 접근 필요
  - 데이터 무결성 이슈 발생

Hybrid Approach:
  Core Data: SQLite (경량 DB)
  Cache Layer: 현재 파일 시스템 유지
  Configuration: 파일 기반 유지
  
Implementation:
  - SQLite로 시작 (설치 불필요)
  - 기존 코드 최소 변경
  - 점진적 마이그레이션
```

#### **Phase 2: Full Database (Enterprise급)**
```yaml
Trigger Conditions:
  - 기업 50개 이상
  - 다중 테넌트 필요
  - 높은 동시성 요구
  - 복잡한 분석 쿼리 필요

Full Stack:
  Database: PostgreSQL
  Cache: Redis
  Search: Elasticsearch (선택)
  Queue: Celery (배치 작업)
```

### 🛠️ **현재 권고사항: 파일 시스템 최적화**

현재 상황에서는 DB보다는 **파일 시스템 개선**이 더 효과적:

#### **1. 캐시 시스템 완료** ✅
- DART API 호출 중복 방지
- 24시간 캐시 정책
- 대시보드 통합 완료

#### **2. 추가 최적화 방안**
```python
# 1. 데이터 압축
import gzip, pickle
def save_compressed(data, filename):
    with gzip.open(f"{filename}.gz", 'wb') as f:
        pickle.dump(data, f)

# 2. 인메모리 캐시 추가
from functools import lru_cache
@lru_cache(maxsize=128)
def get_financial_ratios(company, year):
    return cached_data

# 3. 비동기 데이터 로딩
import asyncio
async def load_all_companies():
    tasks = [load_company(name) for name in companies]
    return await asyncio.gather(*tasks)
```

### 🎯 **즉시 구현 가능한 개선사항**

#### **A. 데이터 구조 최적화**
```python
# financial_data/structure/
├── cache/              # DART API 캐시 (완료)
├── processed/          # 전처리된 데이터
├── models/            # 학습된 모델 저장
└── exports/           # CSV 내보내기
```

#### **B. 백업 자동화**
```python
# backup_manager.py
import shutil, datetime

def backup_data():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backups/backup_{timestamp}"
    shutil.copytree("financial_data", backup_dir)
    return backup_dir
```

#### **C. 데이터 검증**
```python
# data_validator.py
def validate_financial_data(df):
    checks = {
        'completeness': check_missing_values(df),
        'consistency': check_ratio_ranges(df),
        'freshness': check_data_age(df)
    }
    return checks
```

### 💡 **최종 권고**

#### **현재 단계에서는 DB 불필요**
1. ✅ **파일 기반 시스템 유지**
2. ✅ **캐시 시스템 활용** (이미 완료)
3. ✅ **성능 모니터링으로 DB 도입 시점 결정**

#### **DB 도입 판단 기준**
```yaml
도입 고려 시점:
  - 동시 사용자 5명 이상
  - 데이터 볼륨 1GB 이상
  - 복잡한 조인 쿼리 필요
  - 실시간 분석 요구사항
  - 데이터 일관성 이슈 발생

성능 벤치마크:
  - 대시보드 로딩 시간 > 10초
  - 파일 I/O 병목 현상
  - 메모리 사용량 과도
  - 동시성 오류 발생
```

### 🔄 **마이그레이션 준비**

현재부터 DB 마이그레이션을 염두에 둔 코드 작성:

```python
# data_layer.py (추상화 레이어)
class DataRepository:
    def get_company_data(self, company_name, year):
        # 현재: 파일 기반
        # 향후: DB 쿼리로 쉽게 변경 가능
        pass
    
    def save_risk_scores(self, scores):
        # 인터페이스 통일로 백엔드 변경 용이
        pass
```

이렇게 하면 **현재는 파일 시스템의 장점을 유지**하면서도 **향후 DB 도입시 최소한의 변경**으로 전환할 수 있습니다.