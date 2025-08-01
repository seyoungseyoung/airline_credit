"""
GPT 프롬프트 관리 시스템
동적으로 프롬프트를 관리하고 시장 상황에 맞게 자동 업데이트하는 시스템
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import yaml


@dataclass
class MarketContext:
    """현재 시장 상황을 나타내는 데이터 클래스"""
    current_date: str
    market_phase: str  # 'recovery', 'stable', 'recession', 'growth'
    key_concerns: list
    scenario_probabilities: Dict[str, float]
    industry_trends: list


class PromptManager:
    """GPT 프롬프트를 동적으로 관리하는 클래스"""
    
    def __init__(self, prompts_dir: str = "config/prompts"):
        self.prompts_dir = prompts_dir
        self.market_context = self._get_current_market_context()
        self._ensure_prompts_directory()
        self._initialize_default_prompts()
    
    def _ensure_prompts_directory(self):
        """프롬프트 디렉토리가 없으면 생성"""
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
    
    def _get_current_market_context(self) -> MarketContext:
        """현재 시장 상황을 분석하여 컨텍스트 생성"""
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        # 2025년 기준 시장 상황 분석
        if datetime.now().year == 2025:
            market_phase = "recovery"  # 코로나 이후 회복세
            key_concerns = [
                "글로벌 경기침체 영향",
                "유가변동",
                "환율리스크", 
                "경쟁심화",
                "탄소중립 규제",
                "금리환경",
                "AI/디지털화"
            ]
            scenario_probabilities = {
                "optimistic": 0.30,  # 글로벌 경기 회복세
                "baseline": 0.50,    # 안정적 성장세 지속
                "pessimistic": 0.20  # 글로벌 경기침체 심화
            }
            industry_trends = [
                "항공업계 디지털 전환 가속화",
                "친환경 항공기 도입 확대",
                "저비용 항공사 시장 점유율 증가",
                "국제선 수요 회복세 지속"
            ]
        else:
            # 기본값 (미래 시장 상황에 대비)
            market_phase = "stable"
            key_concerns = [
                "경제 불확실성",
                "유가변동",
                "환율리스크",
                "규제 변화"
            ]
            scenario_probabilities = {
                "optimistic": 0.25,
                "baseline": 0.50,
                "pessimistic": 0.25
            }
            industry_trends = [
                "업계 디지털화",
                "친환경 정책 대응",
                "경쟁 심화"
            ]
        
        return MarketContext(
            current_date=current_date,
            market_phase=market_phase,
            key_concerns=key_concerns,
            scenario_probabilities=scenario_probabilities,
            industry_trends=industry_trends
        )
    
    def _initialize_default_prompts(self):
        """기본 프롬프트 파일들을 생성"""
        self._create_system_prompts()
        self._create_user_prompts()
        self._create_market_context_file()
    
    def _create_system_prompts(self):
        """시스템 프롬프트 파일 생성"""
        system_prompts = {
            "credit_analysis": {
                "role": "system",
                "content_template": "당신은 한국 시중은행의 기업금융 대출심사 전문가로서 20년 경력을 보유하고 있습니다. 항공업계 여신업무를 전문으로 합니다. 현재 날짜는 {current_date}입니다. 모든 분석과 권고사항은 현재 시점({current_date})을 기준으로 작성해주세요."
            },
            "comprehensive_report": {
                "role": "system", 
                "content_template": "당신은 한국 시중은행의 기업금융팀장으로서 20년 경력의 항공업계 여신 전문가입니다. 실무진과 경영진이 모두 납득할 수 있는 종합적이고 실행 가능한 분석 리포트를 작성합니다. 현재 날짜는 {current_date}입니다. 모든 분석과 권고사항은 현재 시점({current_date})을 기준으로 작성해주세요."
            }
        }
        
        filepath = os.path.join(self.prompts_dir, "system_prompts.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(system_prompts, f, ensure_ascii=False, indent=2)
    
    def _create_user_prompts(self):
        """사용자 프롬프트 파일 생성"""
        user_prompts = {
            "credit_analysis": {
                "template": """
당신은 한국의 시중은행에서 20년 경력을 가진 기업금융 대출심사 팀장입니다. 
항공업계 대출심사와 기업여신 관리를 전문으로 하며, 아래 신용위험 데이터를 분석하여 
대출담당 직원들이 실무에서 바로 활용할 수 있는 상세한 여신심사 레포트를 작성해주세요.

분석 요청: {prompt}

대시보드 표시 데이터 (전체):
{context_data}

다음 형식으로 여신심사 관점의 레포트를 작성해주세요:

## 🏦 여신심사 종합의견
- 대출실행 관련 핵심 판단사항 (승인/보류/거절 권고)
- 신용등급 변동 가능성에 따른 여신리스크 평가
- 담보 및 보증 요구사항 검토 필요성

## 📊 재무건전성 분석
- 각 항공사별 신용도 상세 평가 (등급별 차등 분석)
- 단기/중기/장기 시계열 위험도 변화 추이 분석
- 업계 내 상대적 신용위험 순위 및 벤치마킹
- 재무비율 기반 상환능력 평가

## ⚠️ 여신관리 주의사항
- 즉시 여신한도 조정이 필요한 거래처 식별
- 담보인정비율(LTV) 조정 검토 대상
- 추가 담보제공 요구 또는 보증인 확보 필요 기업
- 여신회수 및 출구전략 준비가 필요한 고위험 거래처

## 🎯 대출심사 실행방안
- 신규 대출신청시 심사 포인트 및 승인조건
- 기존 여신의 연장/갱신시 고려사항
- 금리 차등적용 및 수수료 조정 방향
- 여신약정서 특약조항 추가 검토사항
- 사후관리 모니터링 주기 및 점검 항목

## 📈 포트폴리오 관리 전략
- 항공업계 여신 포트폴리오의 위험분산 현황 평가
- 업종 집중도 리스크 및 분산투자 필요성
- 경기변동 및 유가변동에 따른 시나리오별 대응방안
- 규제당국 건전성 지표 관리 관점의 권고사항

은행 실무진이 즉시 활용할 수 있도록 구체적인 수치, 비율, 임계값을 명시하고, 
여신규정과 리스크관리 기준에 부합하는 실무적 판단근거를 상세히 제시해주세요.
과도한 요약보다는 충분한 설명과 근거를 포함해주세요.
"""
            },
            "comprehensive_report": {
                "template": """
한국 시중은행의 기업금융팀장으로서, 항공업계 전문 대출심사위원회에 제출할 종합 신용위험 분석 리포트를 작성해주세요.

## 📊 현재 데이터 현황
- **분석 대상**: 한국 항공업계 선별 {company_count}개 기업 ({company_names})
- **분석 기준일**: {current_date}
- **위험도 측정**: 90일 신용등급 변동 확률 기준
- **평균 90일 위험도**: {avg_risk:.3%}
- **고위험 기업 수**: {high_risk_count}개 (임계값 {risk_threshold:.1%} 초과)
- **최고 위험 기업**: {max_risk_company} ({max_risk_value:.3%})
- **최저 위험 기업**: {min_risk_company} ({min_risk_value:.3%})
- **포트폴리오 위험분산도**: 표준편차 {risk_std:.3%}

## 💼 기업별 상세 정보
{detailed_firm_info}

## 📈 주요 발견사항 및 시장 동향

### 🔺 업그레이드 후보 기업 (등급 개선 가능성):
{upgrade_candidates_info}

### 🔻 다운그레이드 위험 기업 (등급 악화 우려):
{downgrade_risks_info}

### 📊 포트폴리오 위험 분포:
- 위험도 1사분위: {risk_q25:.3%}
- 위험도 2사분위(중위값): {risk_q50:.3%}
- 위험도 3사분위: {risk_q75:.3%}

### ⚠️ 최근 알림 이력 및 모니터링 현황:
{recent_alerts_info}

## 📋 종합 분석 리포트 요청사항

다음 구조로 **상세한 종합 분석 리포트**를 작성해주세요:

### 1. 🎯 **핵심 요약** (Executive Summary)
- 선별 분석한 항공업계 {company_count}개 기업의 전반적 신용위험 현황
- 포트폴리오 전체 위험도 수준 및 주요 리스크 요인
- 향후 3개월간 예상되는 신용등급 변동 동향
- 대출심사위원회 의사결정을 위한 핵심 권고사항

### 2. 📊 **업계별 상세 분석**
- **항공업계 전반적 동향**: {current_date} 기준 시장 상황
- **업계 특성을 고려한 주요 우려사항 5가지**: {key_concerns_str}
- **경쟁사 대비 상대적 신용도**: 업계 내 순위 및 벤치마킹
- **업종별 리스크 요인별 영향도 분석**:
  - **글로벌 경기침체 영향**: 국내선/국제선 수요 변화, 소비자 여행 패턴 변화
  - **유가변동**: 연료비 비중 및 수익성에 미치는 영향
  - **환율리스크**: 달러화 강세가 항공사 수익성에 미치는 영향
  - **경쟁심화**: 저비용항공사 등장과 기존 항공사 경쟁력 변화
  - **탄소중립 규제**: 친환경 항공기 도입 비용 및 규제 대응 현황
  - **금리환경**: 고금리 기조가 항공사 부채부담에 미치는 영향
  - **AI/디지털화**: 항공업계 디지털 전환과 운영 효율성 개선

### 3. 🏢 **기업별 신용도 평가 및 등급 전망**
- **개별 기업 상세 분석**: 각 기업별 신용등급 변동 요인 분석
- **등급별 그룹핑**: AAA~D 등급별 기업 분포 및 특성
- **등급 변동 예측**: 향후 3개월간 등급 상향/하향 전망
- **등급별 리스크 관리 방안**: 등급별 차등화된 여신 관리 전략

### 4. ⚠️ **여신관리 실행계획**

**A. 고위험 기업 관리:**
- [ ] {max_risk_company} 등 고위험 {high_risk_count}개사 대상 월간 재무제표 제출 의무화
- [ ] 신용등급 하락시 자동 여신한도 축소 장치 설정
- [ ] 부도위험 기업 대상 보증보험 가입 검토

**B. 포트폴리오 관리:**
- [ ] 항공업종 여신 집중도 한도 재설정 (현재 집중도 검토)
- [ ] 업종 내 위험분산을 위한 우량 기업 여신 확대 검토
- [ ] 유가헤지 등 리스크 완화 상품 활용 의무화 검토
- [ ] 계절성 요인을 고려한 유동성 공급 계획 수립

**C. 모니터링 체계:**
- [ ] 실시간 신용위험 모니터링 시스템 구축
- [ ] 월간 항공업계 동향 보고서 작성 체계 확립
- [ ] 유가/환율 변동시 스트레스 테스트 정기 실시
- [ ] 경쟁사 대비 상대적 신용도 변화 추적 시스템 도입

### 5. 🎲 **향후 3개월 시나리오별 예측 및 대응방안**

**🟢 낙관 시나리오 (확률 {optimistic_prob:.0%}): 글로벌 경기 회복세**
- 위험도 개선 예상 기업: [구체적 기업명과 개선폭 제시]
- 여신 확대 검토 대상 및 신규 여신 기회
- 금리 인하 혜택 적용 기업 선별

**🟡 기본 시나리오 (확률 {baseline_prob:.0%}): 안정적 성장세 지속**
- 현상 유지 예상 기업들의 안정적 관리 방안
- 기존 여신조건 유지하되 모니터링 강화
- 분기별 재평가를 통한 조건 조정 검토

**🔴 비관 시나리오 (확률 {pessimistic_prob:.0%}): 글로벌 경기침체 심화**
- 위험도 급속 악화 우려 기업 및 선제적 대응책
- 여신회수 및 구조조정 지원 방안
- 정부 지원정책 연계를 통한 손실 최소화 전략

### 6. 💡 **종합 리스크 완화 전략**

**A. 포트폴리오 다각화:**
- 항공업종 내 세부 업종별 분산 (대형항공사 vs 저비용항공사)
- 지역별 노선 특성을 고려한 위험분산 (국내선 vs 국제선)
- 항공기 리스 vs 운항 전문 기업 간 위험분산

**B. 헤지상품 및 보험 활용:**
- 유가연동 파생상품을 통한 연료비 헤지 의무화
- 신용보증기금/기술보증기금 연계 보증 확대
- 무역보험공사 해외투자보험 등 정책보험 활용

**C. 업계 전문 모니터링 체계:**
- 항공교통량, 유가지수, 환율 등 핵심지표 실시간 추적
- 국제항공운송협회(IATA) 등 글로벌 동향 분석 체계
- 동종업계 타행 여신동향 및 부실률 벤치마킹
- 정기적인 항공업계 전문가 자문회의 운영

### 7. 🏦 **은행 내부 관리 방안**
- 여신심사역 대상 항공업계 전문교육 실시
- 리스크관리 시스템 내 항공업종 특화 모델 구축
- 감독당국 보고용 업종별 건전성 지표 관리 체계
- 이사회 보고용 분기별 업종 리스크 현황 보고서 양식 표준화

**작성시 주의사항:**
1. 모든 수치는 소수점 3자리까지 정확히 제시
2. 구체적 기업명과 함께 실행 가능한 권고사항 명시
3. 은행 내부 승인 프로세스를 고려한 실무적 관점 반영
4. 각 섹션을 충분한 분량으로 상세히 작성 (요약보다는 구체적 설명 중심)
5. 표, 리스트, 체크박스를 적극 활용하여 가독성 확보
6. 정량적 분석과 정성적 판단을 균형있게 포함
7. 시장 상황 변화에 따른 동적 대응 방안 포함

이 리포트는 대출심사위원회에서 즉시 의사결정에 활용될 예정이므로, 실무진과 경영진 모두가 납득할 수 있는 종합적이고 실행 가능한 분석 리포트로 작성해주세요.
"""
            }
        }
        
        filepath = os.path.join(self.prompts_dir, "user_prompts.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_prompts, f, ensure_ascii=False, indent=2)
    
    def _create_market_context_file(self):
        """시장 컨텍스트 파일 생성"""
        filepath = os.path.join(self.prompts_dir, "market_context.yaml")
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self.market_context), f, default_flow_style=False, allow_unicode=True)
    
    def get_system_prompt(self, prompt_type: str) -> Dict[str, str]:
        """시스템 프롬프트 가져오기"""
        filepath = os.path.join(self.prompts_dir, "system_prompts.json")
        with open(filepath, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        if prompt_type not in prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        prompt_data = prompts[prompt_type]
        return {
            "role": prompt_data["role"],
            "content": prompt_data["content_template"].format(
                current_date=self.market_context.current_date
            )
        }
    
    def get_user_prompt(self, prompt_type: str, **kwargs) -> str:
        """사용자 프롬프트 가져오기"""
        filepath = os.path.join(self.prompts_dir, "user_prompts.json")
        with open(filepath, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        if prompt_type not in prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = prompts[prompt_type]["template"]
        
        # 기본값 설정
        default_kwargs = {
            "current_date": self.market_context.current_date,
            "key_concerns_str": ", ".join(self.market_context.key_concerns),
            "optimistic_prob": self.market_context.scenario_probabilities["optimistic"],
            "baseline_prob": self.market_context.scenario_probabilities["baseline"],
            "pessimistic_prob": self.market_context.scenario_probabilities["pessimistic"],
        }
        
        # 사용자 제공 kwargs로 기본값 덮어쓰기
        default_kwargs.update(kwargs)
        
        return template.format(**default_kwargs)
    
    def update_market_context(self):
        """시장 컨텍스트 업데이트"""
        self.market_context = self._get_current_market_context()
        self._create_market_context_file()
    
    def get_prompt_info(self) -> Dict[str, Any]:
        """현재 프롬프트 시스템 정보 반환"""
        return {
            "prompts_directory": self.prompts_dir,
            "market_context": asdict(self.market_context),
            "available_prompt_types": ["credit_analysis", "comprehensive_report"],
            "last_updated": datetime.now().isoformat()
        }


# 싱글톤 인스턴스
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """프롬프트 매니저 싱글톤 인스턴스 반환"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager 