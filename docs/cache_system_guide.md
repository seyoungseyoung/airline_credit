# DART 데이터 캐시 시스템 가이드

## 개요

DART 데이터 캐시 시스템은 DART API 호출 결과를 로컬에 저장하여 중복 요청을 방지하고 성능을 향상시키는 시스템입니다.

## 주요 기능

### 1. 자동 캐싱
- DART API 호출 결과를 자동으로 캐시에 저장
- 동일한 요청 시 캐시된 데이터 사용
- 캐시 유효 시간: 24시간 (기본값)

### 2. 캐시 관리
- 만료된 캐시 자동 정리
- 캐시 통계 모니터링
- 수동 캐시 삭제 기능

### 3. 대시보드 통합
- Streamlit 대시보드에서 캐시 상태 확인
- 캐시 활성화/비활성화 토글
- 실시간 캐시 통계 표시

## 캐시 시스템 상태 확인

### 대시보드에서 확인
1. 대시보드 실행: `python run_dashboard.py`
2. 사이드바에서 "💾 DART 데이터 캐시" 섹션 확인
3. 캐시 시스템 상태:
   - ✅ **활성화**: 캐시 시스템이 정상 작동
   - ❌ **비활성화**: 캐시 시스템 로드 실패

### 터미널에서 확인
```bash
python -c "import sys; sys.path.append('src'); from data.dart_data_cache import get_global_cache; cache = get_global_cache(); print(cache.get_cache_stats())"
```

## 캐시 시스템 활성화 방법

### 1. 파일 존재 확인
- `src/data/dart_data_cache.py` 파일이 존재하는지 확인

### 2. Python 경로 설정
- `src` 디렉토리가 Python 경로에 포함되어 있는지 확인

### 3. 대시보드 재시작
- 캐시 시스템 변경 후 대시보드 재시작

## 캐시 설정

### 기본 설정 (config/config.py)
```python
# Cache Configuration
CACHE_ENABLED = True                    # 캐시 기능 활성화 여부
CACHE_DIRECTORY = "financial_data/dart_cache"  # 캐시 파일 저장 경로
CACHE_DURATION_HOURS = 24              # 캐시 유효 시간 (시간 단위)
CACHE_MAX_SIZE_MB = 500                # 최대 캐시 크기 (MB)
```

### 대시보드에서 설정 변경
1. 사이드바의 "💾 캐시 시스템 사용" 체크박스로 활성화/비활성화
2. "⚙️ 캐시 설정" 확장 패널에서 현재 설정 확인

## 캐시 관리 기능

### 1. 캐시 통계 확인
- 총 엔트리 수
- 유효한 데이터 수
- 만료된 데이터 수
- 총 캐시 크기
- 캐시 유효 시간

### 2. 캐시 정리
- **만료 정리**: 만료된 캐시 엔트리만 삭제
- **전체 삭제**: 모든 캐시 데이터 삭제

### 3. 캐시 세부 정보
- 캐시된 회사 목록
- 캐시 생성 시간
- 데이터 유효성 상태

## 캐시 파일 구조

```
financial_data/dart_cache/
├── cache_metadata.json    # 캐시 메타데이터
├── [hash1].pkl           # 캐시된 데이터 파일들
├── [hash2].pkl
└── ...
```

## 성능 이점

### 1. API 호출 감소
- 동일한 데이터 요청 시 캐시 사용
- DART API 호출 횟수 최소화

### 2. 응답 시간 단축
- 로컬 캐시에서 즉시 데이터 로드
- 네트워크 지연 시간 제거

### 3. 비용 절약
- API 호출 비용 절약
- 대역폭 사용량 감소

## 문제 해결

### 캐시 시스템이 비활성화된 경우

1. **파일 경로 확인**
   ```bash
   ls src/data/dart_data_cache.py
   ```

2. **Python 경로 확인**
   ```python
   import sys
   print('src' in sys.path)
   ```

3. **대시보드 재시작**
   ```bash
   python run_dashboard.py
   ```

### 캐시 데이터 손상 시

1. **캐시 전체 삭제**
   - 대시보드에서 "🗑️ 전체 삭제" 버튼 클릭

2. **수동 삭제**
   ```bash
   rm -rf financial_data/dart_cache/
   ```

## 모니터링

### 캐시 히트율 확인
- 캐시 사용 통계를 통해 효율성 모니터링
- 낮은 히트율 시 캐시 전략 재검토

### 디스크 공간 모니터링
- 캐시 크기가 설정된 최대 크기 초과 시 경고
- 정기적인 캐시 정리 권장

## 고급 설정

### 캐시 유효 시간 변경
```python
# config/config.py에서 수정
CACHE_DURATION_HOURS = 48  # 48시간으로 변경
```

### 캐시 디렉토리 변경
```python
# config/config.py에서 수정
CACHE_DIRECTORY = "custom_cache_directory"
```

## 결론

DART 데이터 캐시 시스템은 성능 향상과 비용 절약을 위한 중요한 기능입니다. 대시보드에서 쉽게 모니터링하고 관리할 수 있으며, 설정 변경도 간단합니다.

캐시 시스템이 비활성화된 경우 위의 문제 해결 단계를 따라 활성화하시기 바랍니다. 