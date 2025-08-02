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

## 🚀 빠른 시작

### Docker 사용 (권장)

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd kokmin

# 2. 환경 변수 설정
cp config/env_example.txt .env

# 3. Docker 실행
./docker-build.sh run  # Linux/Mac
# 또는
docker-build.bat run   # Windows

# 4. 대시보드 접속
# http://localhost:8501
```

### 로컬 환경 사용

```bash
# 1. 환경 설정
conda create -n credit_rating_transition python=3.9
conda activate credit_rating_transition
pip install -r config/requirements_pipeline.txt

# 2. 환경 변수 설정
cp config/env_example.txt .env

# 3. 대시보드 실행
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

### 🚨 4. Alerts (알림 시스템)
- **실시간 모니터링**: 임계값 초과 시 자동 감지
- **Slack 연동**: 위험 상황 실시간 알림

### 🔍 5. RAG 시스템 (항공업계 정보 검색)
- **실시간 뉴스 검색**: 네이버 뉴스 및 구글 검색 연동
- **AI 기반 요약**: GPT-4o-mini를 활용한 기사 요약

### 📊 6. 종합 리포트 (AI 분석)
- **GPT-4 기반 분석**: 전문적인 위험 분석 리포트
- **현재 날짜 컨텍스트**: 2025년 현재 상황 인식

## 🏗️ 시스템 아키텍처

```
kokmin/
├── 📊 src/
│   ├── 🎯 models/           # 핵심 위험 분석 모델
│   ├── 📈 dashboard/        # 대시보드 인터페이스
│   ├── 💾 data/            # 데이터 처리 및 캐싱
│   ├── 🔍 rag/             # RAG 시스템
│   └── 🛠️ utils/           # 유틸리티
├── ⚙️ config/              # 설정 및 프롬프트
├── 📁 data/                # 데이터 저장소
└── 📚 docs/                # 문서
```

## 🔧 기술 스택

### 📊 데이터 분석
- **Pandas**: 데이터 처리 및 분석
- **NumPy**: 수치 계산
- **Plotly**: 인터랙티브 시각화

### 🤖 AI/ML
- **Lifelines**: 생존 분석 (Cox Proportional Hazards)
- **OpenAI GPT-4**: 자연어 분석 리포트
- **RAG 시스템**: 검색 기반 생성 AI

### 🌐 웹 인터페이스
- **Streamlit**: 대시보드 프레임워크
- **Slack API**: 실시간 알림

## 📚 문서

- **[📖 상세 사용자 가이드](docs/dashboard_user_guide.md)** - 대시보드 사용법
- **[🐳 Docker 설정 가이드](DOCKER_README.md)** - Docker 환경 설정
- **[📋 프로젝트 요약](docs/PROJECT_SUMMARY.md)** - 전체 시스템 개요
- **[🚀 빠른 시작 가이드](QUICK_START.md)** - 빠른 설정 방법

## 🤝 기여하기

### 🐛 버그 리포트
1. GitHub Issues에서 버그 리포트 생성
2. 상세한 재현 단계와 에러 로그 포함

### 💡 기능 제안
1. 새로운 기능 아이디어 제안
2. 사용 사례와 기대 효과 설명

### 🔧 코드 기여
1. Fork 후 개발 브랜치 생성
2. 코드 스타일 가이드 준수
3. 테스트 코드 작성
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 연락처

- **프로젝트 관리자**: [GitHub Profile](https://github.com/seyoungseyoung)
- **이슈 리포트**: [GitHub Issues](https://github.com/seyoungseyoung/airline_credit/issues)

---

**✈️ 한국 항공업계의 미래를 위한 신용위험 분석 시스템** 🚀