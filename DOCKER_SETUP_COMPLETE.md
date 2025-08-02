# 🐳 Docker 설정 완료 - Korean Airlines Credit Risk Analysis System

## ✅ 완료된 작업

`credit_rating_transition` conda 환경을 위한 Docker 설정이 완료되었습니다!

### 📁 생성된 파일들

1. **`Dockerfile`** - Docker 이미지 정의
2. **`environment.yml`** - Conda 환경 설정
3. **`docker-compose.yml`** - 컨테이너 오케스트레이션
4. **`.dockerignore`** - 빌드 제외 파일 목록
5. **`docker-build.sh`** - Linux/Mac용 자동화 스크립트
6. **`docker-build.bat`** - Windows용 자동화 스크립트
7. **`DOCKER_README.md`** - 상세 사용법 가이드

## 🚀 사용 방법

### Windows 사용자

```cmd
# 1. Docker Desktop 시작
# Docker Desktop 애플리케이션을 실행하세요

# 2. 환경 변수 파일 생성
copy config\env_example.txt .env

# 3. Docker 이미지 빌드 및 실행
docker-build.bat run

# 또는 수동으로:
docker build -t credit-rating-transition:latest .
docker-compose up -d
```

### Linux/Mac 사용자

```bash
# 1. Docker 시작
sudo systemctl start docker

# 2. 환경 변수 파일 생성
cp config/env_example.txt .env

# 3. Docker 이미지 빌드 및 실행
chmod +x docker-build.sh
./docker-build.sh run

# 또는 수동으로:
docker build -t credit-rating-transition:latest .
docker-compose up -d
```

## 🌐 접속 정보

- **Streamlit 대시보드**: http://localhost:8501
- **Jupyter Notebook** (개발 모드): http://localhost:8888

## 🔧 주요 명령어

### Windows
```cmd
docker-build.bat run      # 애플리케이션 실행
docker-build.bat dev      # Jupyter 포함 실행
docker-build.bat stop     # 컨테이너 중지
docker-build.bat logs     # 로그 확인
docker-build.bat clean    # 정리
```

### Linux/Mac
```bash
./docker-build.sh run     # 애플리케이션 실행
./docker-build.sh dev     # Jupyter 포함 실행
./docker-build.sh stop    # 컨테이너 중지
./docker-build.sh logs    # 로그 확인
./docker-build.sh clean   # 정리
```

## 📦 Docker 이미지 구성

### Base Image
- **continuumio/miniconda3:latest**
- Conda 환경 지원

### Conda Environment: `credit_rating_transition`
- **Python 3.9**
- **주요 패키지**:
  - pandas, numpy, matplotlib, seaborn
  - scikit-learn, scipy, plotly
  - streamlit, jupyter
  - lifelines (생존 분석)
  - openai (GPT API)
  - opendart-python (DART API)

### 추가 pip 패키지
- `config/requirements_pipeline.txt`의 모든 패키지

## 💾 데이터 영속성

다음 디렉토리가 호스트에 마운트됩니다:
- `./data` → `/app/data` (데이터 저장소)
- `./rag_cache` → `/app/rag_cache` (RAG 캐시)
- `./config` → `/app/config` (설정 파일)
- `./.env` → `/app/.env` (환경 변수)

## 🔧 환경 변수 설정

`.env` 파일에 다음을 설정하세요:

```bash
# OpenAI API (RAG 시스템 및 GPT 리포트용)
OPENAI_API_KEY=your_openai_api_key_here

# Slack Webhook (알림 시스템용, 선택사항)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# DART API (한국 기업 재무정보용, 선택사항)
DART_API_KEY=your_dart_api_key_here
```

## 🐛 문제 해결

### Docker Desktop이 실행되지 않는 경우
1. Docker Desktop 애플리케이션 실행
2. 시스템 트레이에서 Docker 아이콘 확인
3. Docker Desktop 설정에서 리소스 할당 확인 (메모리 4GB+ 권장)

### 포트 충돌
```cmd
# 포트 사용 확인
netstat -an | findstr :8501

# 다른 포트 사용
docker-compose up -d -p 8502:8501
```

### 권한 문제 (Linux/Mac)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 📊 시스템 요구사항

### 최소 요구사항
- **Docker Desktop**: 4.0+
- **메모리**: 4GB RAM
- **디스크**: 10GB 여유 공간

### 권장 사항
- **메모리**: 8GB RAM
- **CPU**: 4코어 이상
- **디스크**: SSD 20GB 여유 공간

## 🎯 다음 단계

1. **Docker Desktop 시작**
2. **환경 변수 설정** (`.env` 파일 편집)
3. **Docker 이미지 빌드 및 실행**
4. **대시보드 접속**: http://localhost:8501

## 📞 지원

문제가 발생하면:
1. `DOCKER_README.md` 확인
2. 로그 확인: `docker-compose logs -f`
3. GitHub Issues 생성

---

**🎉 축하합니다!** `credit_rating_transition` conda 환경이 Docker로 성공적으로 설정되었습니다. 