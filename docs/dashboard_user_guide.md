# 🛩️ Korean Airlines Credit Risk Dashboard 사용자 가이드

## 📖 개요

Korean Airlines Credit Risk Dashboard는 **한국 항공사들의 신용등급 위험도를 실시간으로 모니터링**하고 **자동 알림을 제공**하는 대시보드입니다. 투자팀과 리스크팀의 업무 흐름에 바로 활용할 수 있도록 설계되었습니다.

---

## 🚀 빠른 시작

### 1. 대시보드 실행
```bash
# 프로젝트 디렉토리에서
streamlit run credit_rating_dashboard.py
```

### 2. 브라우저 접속
- 자동으로 브라우저가 열리거나
- 수동으로 `http://localhost:8501` 접속

### 3. 모델 로딩
- 사이드바에서 **"🔄 Load/Refresh Models"** 버튼 클릭
- 모델 로딩 완료까지 대기 (약 30초)

---

## 🎛️ 메인 기능

### 📊 **실시간 위험도 메트릭**
대시보드 상단에 4개 핵심 지표가 표시됩니다:

| 메트릭 | 설명 | 활용법 |
|--------|------|--------|
| **Average Risk** | 전체 항공사 평균 위험도 | 시장 전반 위험 수준 파악 |
| **High Risk Firms** | 임계값 초과 기업 수 | 즉시 주의 필요 기업 식별 |
| **Highest Risk** | 최고 위험도 기업 | 최우선 모니터링 대상 |
| **Last Update** | 마지막 업데이트 시간 | 데이터 신선도 확인 |

---

## 📈 대시보드 탭 기능

### **1. 📈 Hazard Curves (위험도 곡선)**

#### 기능 설명
- **시간 경과에 따른 위험도 변화**를 시각화
- 30일, 60일, 90일, 120일, 180일, 270일, 365일 구간별 예측

#### 4개 서브 차트
1. **Overall Risk**: 전체 등급 변화 확률
2. **Upgrade Probability**: 등급 상승 가능성
3. **Downgrade Probability**: 등급 하락 위험
4. **Default Risk**: 디폴트 확률

#### 실무 활용
```
✅ 포트폴리오 재조정 시점 결정
✅ 투자 기간별 위험 수준 평가
✅ 기업별 위험 패턴 비교 분석
```

### **2. 📋 Risk Table (위험도 테이블)**

#### 주요 특징
- **90일 기준 위험도** 순위별 정렬
- **Progress Bar** 형태로 직관적 표시
- **색상 코딩**: 빨간색(High), 노란색(Medium), 기본색(Low)

#### 데이터 컬럼
| 컬럼 | 의미 | 임계값 |
|------|------|--------|
| **Overall Risk** | 전체 변화 확률 | >15% 주의 |
| **Upgrade ↗️** | 상승 확률 | 긍정적 신호 |
| **Downgrade ↘️** | 하락 확률 | >10% 경고 |
| **Default ❌** | 디폴트 확률 | >1% 위험 |

#### 실무 활용
```
📥 CSV 다운로드 → Excel 분석
📊 일일 리스크 브리핑 자료
🎯 High-Risk 기업 우선순위 결정
```

### **3. 🔥 Heatmap (위험도 히트맵)**

#### 기능
- **기업 × 위험유형** 매트릭스 시각화
- **색상 강도**로 위험 수준 표현
- **Risk Distribution** 히스토그램 제공

#### 분석 인사이트
```
🔴 진한 빨강: 즉시 조치 필요
🟠 주황색: 모니터링 강화
🟡 노란색: 주의 관찰
🟢 초록색: 안정 상태
```

### **4. 🚨 Alerts (알림 관리)**

#### 자동 알림 기능
- **임계값 초과 기업** 자동 탐지
- **Slack 웹훅** 연동으로 실시간 알림
- **Alert History** 관리

#### 알림 설정
1. 사이드바에서 **Alert Threshold** 조정 (5% ~ 30%)
2. **Slack Webhook URL** 입력
3. **Send Slack Alert** 버튼으로 수동 전송

---

## 🔧 사이드바 컨트롤

### ⚙️ **Control Panel**
| 기능 | 설명 | 권장 설정 |
|------|------|-----------|
| **Load/Refresh Models** | 모델 재로딩 | 일일 1회 |
| **Alert Threshold** | 알림 임계값 | 15% (기본값) |
| **Slack Webhook URL** | 알림 URL | 팀 채널 연동 |
| **Auto Refresh** | 자동 새로고침 | 모니터링 시 ON |

---

## 📱 Slack 알림 설정

### 1. Slack Webhook URL 생성
1. https://api.slack.com/messaging/webhooks 접속
2. 새 Webhook URL 생성
3. 알림받을 채널 선택 (예: #risk-monitoring)

### 2. 대시보드 연동
```
1. 사이드바 → "📱 Slack Webhook URL" 입력
2. Alert 탭 → "📱 Send Slack Alert" 테스트
3. Slack 채널에서 알림 수신 확인
```

### 3. 알림 메시지 형식
```
🚨 Credit Rating Risk Alert - Korean Airlines

2 firms exceed the risk threshold of 15%:

• 대한항공 (A): 18.0% risk, Downgrade: 12.0%
• 아시아나항공 (B): 22.0% risk, Downgrade: 15.0%

Recommended Actions:
• Monitor financial performance closely
• Review credit facilities
• Update risk assessments

Generated at 2024-01-15 14:30:00
```

---

## 🎯 실무 워크플로우

### **일일 모니터링 (10분)**
```
1. 대시보드 접속 및 모델 새로고침
2. 상단 메트릭으로 전반적 상황 파악
3. Risk Table에서 High-Risk 기업 확인
4. 필요시 CSV 다운로드하여 상세 분석
```

### **주간 리뷰 (30분)**
```
1. Hazard Curves로 트렌드 분석
2. Heatmap으로 섹터별 위험 분포 확인
3. Alert History 검토
4. 투자 포지션 조정 여부 결정
```

### **월간 전략 회의 (1시간)**
```
1. 전체 백테스트 결과 리뷰
2. COVID 편향성 분석 검토  
3. 모델 성능 지표 평가
4. 신규 임계값 설정 논의
```

---

## 🚨 알림 시나리오

### **🔴 High Alert (25% 이상)**
```
즉시 조치:
✅ 포지션 축소 검토
✅ 헤지 전략 실행
✅ 경영진 면담 요청
✅ 일일 모니터링 전환
```

### **🟠 Medium Alert (15-25%)**
```
강화 모니터링:
✅ 재무제표 정밀 분석
✅ 업계 동향 조사
✅ 신용정보 추가 수집
✅ 주간 리뷰 포함
```

### **🟡 Low Alert (10-15%)**
```
주의 관찰:
✅ 월간 모니터링 리스트 추가
✅ 분기 실적 주의 깊게 관찰
✅ 뉴스/공시 모니터링
```

---

## 🔍 고급 활용법

### **1. 사용자 정의 기업 추가**
```python
# credit_rating_dashboard.py 수정
custom_firm = FirmProfile(
    company_name="신규항공",
    current_rating="BBB",
    debt_to_assets=0.60,
    current_ratio=1.0,
    roa=0.03,
    # ... 기타 재무비율
)
```

### **2. 임계값 최적화**
```
백테스트 결과 기반:
• Conservative: 10% (높은 민감도)
• Balanced: 15% (권장 기본값)  
• Aggressive: 20% (낮은 오탐률)
```

### **3. 다중 채널 알림**
```python
# 여러 Slack 채널에 알림
channels = ["#risk-team", "#investment-team", "#management"]
for channel in channels:
    send_alert(high_risk_firms, channel=channel)
```

---

## 📊 성능 해석 가이드

### **모델 성능 지표**
| 메트릭 | 현재 성능 | 해석 |
|--------|-----------|------|
| **C-Index** | 0.740 | 강한 예측력 (>0.7) |
| **ROC-AUC@90d** | 0.500 | 개선 여지 있음 |
| **Brier Score** | 0.122 | 양호한 교정도 |

### **COVID 편향 검증**
```
✅ LOW Bias (8.5% 성능 저하)
→ 모델이 팬데믹 충격에 강건함
→ 분기별 모니터링으로 충분
```

---

## 🛠️ 문제해결

### **일반적 문제**

#### 1. 모델 로딩 실패
```
해결방법:
1. 모든 Python 파일이 같은 디렉토리에 있는지 확인
2. 필요 패키지 설치: pip install lifelines scikit-learn
3. Streamlit 재시작
```

#### 2. Slack 알림 안됨
```
확인사항:
1. Webhook URL 정확성
2. 인터넷 연결 상태
3. Slack 채널 권한
4. 방화벽 설정
```

#### 3. 데이터 업데이트 안됨
```
해결방법:
1. 브라우저 새로고침 (Ctrl+F5)
2. 사이드바에서 모델 재로딩
3. 페이지 재접속
```

### **고급 문제**

#### 모델 성능 저하 시
```
점검 항목:
1. 새로운 시장 이벤트 발생 여부
2. 재무데이터 품질 확인
3. 백테스트 재실행
4. 임계값 재조정 필요성
```

---

## 📞 지원 및 확장

### **확장 계획**
```
Phase 2:
✅ 다른 업종 확장
✅ 실시간 데이터 연동
✅ 모바일 앱 개발
✅ AI 해석 기능 추가
```

---

## 🎉 결론

Korean Airlines Credit Risk Dashboard는 **데이터 기반 의사결정**을 지원하는 강력한 도구입니다. 일일 모니터링부터 전략적 포트폴리오 관리까지, 투자와 리스크 관리의 모든 단계에서 활용할 수 있습니다.

### **핵심 가치**
```
⏱️ 시간 절약: 수동 분석 → 자동 모니터링
🎯 정확성: 정량적 모델 → 객관적 판단  
🚨 신속성: 실시간 알림 → 즉각적 대응
📊 투명성: 시각화 → 명확한 소통
```

**현재 구현된 기능을 통해 효과적인 리스크 관리 시스템을 구축할 수 있습니다!** 🚀 