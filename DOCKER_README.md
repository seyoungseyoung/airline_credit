# 🐳 Docker Setup for Korean Airlines Credit Risk Analysis System

이 문서는 `credit_rating_transition` conda 환경을 Docker로 실행하는 방법을 설명합니다.

## 📋 Prerequisites

- **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치
- **Docker Compose**: Docker Desktop에 포함되어 있음
- **Git**: 프로젝트 클론용

## 🚀 Quick Start

### 1. 프로젝트 클론 및 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd kokmin

# 환경 변수 파일 생성
cp config/env_example.txt .env
```

### 2. Docker 이미지 빌드 및 실행

```bash
# 자동 빌드 스크립트 사용 (권장)
chmod +x docker-build.sh
./docker-build.sh run
```

또는 수동으로:

```bash
# Docker 이미지 빌드
docker build -t credit-rating-transition:latest .

# Docker Compose로 실행
docker-compose up -d
```

### 3. 애플리케이션 접속

- **대시보드**: http://localhost:8501
- **로그 확인**: `docker-compose logs -f`

## 🔧 Docker 빌드 스크립트 사용법

### 기본 명령어

```bash
# 애플리케이션 빌드 및 실행
./docker-build.sh run

# 개발 모드 (Jupyter 포함)
./docker-build.sh dev

# 이미지만 빌드
./docker-build.sh build

# 컨테이너 중지
./docker-build.sh stop

# 로그 확인
./docker-build.sh logs

# 정리 (모든 컨테이너 및 이미지 삭제)
./docker-build.sh clean

# 도움말
./docker-build.sh help
```

### 개발 모드

Jupyter Notebook과 함께 실행하려면:

```bash
./docker-build.sh dev
```

- **대시보드**: http://localhost:8501
- **Jupyter**: http://localhost:8888

## 📁 Docker 파일 구조

```
kokmin/
├── Dockerfile              # Docker 이미지 정의
├── docker-compose.yml      # 컨테이너 오케스트레이션
├── environment.yml         # Conda 환경 정의
├── .dockerignore          # Docker 빌드 제외 파일
├── docker-build.sh        # 자동화 빌드 스크립트
└── DOCKER_README.md       # 이 파일
```

## 🔍 Docker 이미지 상세 정보

### Base Image
- **continuumio/miniconda3:latest**: Conda 환경 지원

### Conda Environment
- **이름**: `credit_rating_transition`
- **Python 버전**: 3.9
- **주요 패키지**:
  - pandas, numpy, matplotlib, seaborn
  - scikit-learn, scipy, plotly
  - streamlit, jupyter
  - lifelines (생존 분석)
  - openai (GPT API)
  - opendart-python (DART API)

### 포트 설정
- **8501**: Streamlit 대시보드
- **8888**: Jupyter Notebook (개발 모드)

## 💾 데이터 영속성

Docker Compose는 다음 디렉토리를 호스트에 마운트합니다:

```yaml
volumes:
  - ./data:/app/data          # 데이터 저장소
  - ./rag_cache:/app/rag_cache # RAG 캐시
  - ./config:/app/config      # 설정 파일
  - ./.env:/app/.env         # 환경 변수
```

## 🔧 환경 변수 설정

### 필수 환경 변수

`.env` 파일에 다음을 설정하세요:

```bash
# OpenAI API (RAG 시스템 및 GPT 리포트용)
OPENAI_API_KEY=your_openai_api_key_here

# Slack Webhook (알림 시스템용, 선택사항)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# DART API (한국 기업 재무정보용, 선택사항)
DART_API_KEY=your_dart_api_key_here
```

### 환경 변수 템플릿

```bash
# config/env_example.txt에서 복사
cp config/env_example.txt .env
```

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8501

# 다른 포트 사용
docker-compose up -d -p 8502:8501
```

#### 2. 권한 문제
```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. 메모리 부족
```bash
# Docker Desktop 메모리 증가
# Docker Desktop > Settings > Resources > Memory: 4GB+
```

#### 4. 이미지 빌드 실패
```bash
# 캐시 없이 재빌드
docker build --no-cache -t credit-rating-transition:latest .

# 로그 확인
docker-compose logs -f
```

### 로그 확인

```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f credit-rating-app

# 마지막 100줄
docker-compose logs --tail=100
```

## 🔄 업데이트 및 유지보수

### 이미지 업데이트

```bash
# 최신 코드로 재빌드
./docker-build.sh clean
./docker-build.sh run
```

### 의존성 업데이트

1. `environment.yml` 또는 `config/requirements_pipeline.txt` 수정
2. 이미지 재빌드:
   ```bash
   ./docker-build.sh clean
   ./docker-build.sh run
   ```

### 데이터 백업

```bash
# 데이터 디렉토리 백업
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# RAG 캐시 백업
tar -czf rag_cache_backup_$(date +%Y%m%d).tar.gz rag_cache/
```

## 🚀 프로덕션 배포

### 프로덕션용 설정

```bash
# 프로덕션 환경 변수
cp .env .env.production

# 프로덕션용 Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### 보안 고려사항

1. **환경 변수**: 민감한 정보는 `.env` 파일에 저장
2. **포트 노출**: 필요한 포트만 노출
3. **볼륨 마운트**: 읽기 전용으로 설정 가능
4. **네트워크**: 격리된 네트워크 사용

## 📊 모니터링

### 헬스체크

Docker Compose는 자동 헬스체크를 포함합니다:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 리소스 모니터링

```bash
# 컨테이너 리소스 사용량
docker stats

# 특정 컨테이너 상세 정보
docker inspect credit_rating_transition
```

## 🤝 기여하기

Docker 관련 개선사항이 있다면:

1. 이슈 생성
2. 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📞 지원

문제가 발생하면:

1. 로그 확인: `./docker-build.sh logs`
2. 이슈 생성: GitHub Issues
3. 문서 확인: `docs/` 디렉토리

---

**🎯 목표**: 한국 항공업계 신용위험 분석 시스템을 Docker로 쉽게 실행할 수 있도록 하는 것 