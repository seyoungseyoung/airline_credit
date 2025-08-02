#!/usr/bin/env python3
"""
Credit Rating Risk Dashboard
============================

Streamlit-based dashboard for Korean Airlines credit rating monitoring:
1. Enterprise Hazard Curves visualization
2. 90-day Risk Top N Table  
3. Slack Webhook alerts for high-risk situations
4. Real-time monitoring for investment & risk teams

Author: Korean Airlines Credit Rating Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional, Any
import warnings
import os
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import our models
try:
    import sys
    import os
    # Add parent directories to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # src/
    root_dir = os.path.dirname(parent_dir)     # project root
    
    # Add all necessary paths in specific order
    paths_to_add = [
        parent_dir,  # src/
        root_dir,    # project root
        os.path.join(parent_dir, 'data'),    # src/data/
        os.path.join(parent_dir, 'utils'),   # src/utils/
        os.path.join(parent_dir, 'models'),  # src/models/
        os.path.join(parent_dir, 'rag'),     # src/rag/
        os.path.join(root_dir, 'config')     # config/
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"🔧 [DASHBOARD] Added {len(paths_to_add)} paths to Python path")
    
    # Import cache system (after path setup)
    try:
        from data.dart_data_cache import get_global_cache, DARTDataCache
        CACHE_AVAILABLE = True
        print("✅ Cache system loaded successfully")
    except ImportError:
        try:
            from src.data.dart_data_cache import get_global_cache, DARTDataCache
            CACHE_AVAILABLE = True
            print("✅ Cache system loaded from src.data path")
        except ImportError:
            CACHE_AVAILABLE = False
            print("❌ Cache system not available")
    
    # Try different import strategies
    try:
        from models.rating_risk_scorer import RatingRiskScorer, FirmProfile
        from models.enhanced_multistate_model import EnhancedMultiStateModel
        from models.backtest_framework import CreditRatingBacktester
    except ImportError:
        # Try absolute imports from src
        from src.models.rating_risk_scorer import RatingRiskScorer, FirmProfile
        from src.models.enhanced_multistate_model import EnhancedMultiStateModel
        from src.models.backtest_framework import CreditRatingBacktester
    
    MODEL_AVAILABLE = True
    print("✅ Model modules loaded successfully")
    
except ImportError as e:
    print(f"❌ Model modules not available: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:5]}")  # Show first 5 paths
    MODEL_AVAILABLE = False

# Configuration
RISK_THRESHOLD = 0.15  # 15% change probability threshold for alerts
SLACK_WEBHOOK_URL = None  # Set this to your Slack webhook URL

# OpenAI Configuration

# Import prompt manager
try:
    from config.prompts import get_prompt_manager
    PROMPT_MANAGER_AVAILABLE = True
    print("✅ Prompt manager loaded successfully")
except ImportError:
    try:
        import sys
        sys.path.insert(0, os.path.join(root_dir, 'config'))
        from prompts import get_prompt_manager
        PROMPT_MANAGER_AVAILABLE = True
        print("✅ Prompt manager loaded with explicit path")
    except ImportError:
        try:
            from config.prompts import get_prompt_manager
            PROMPT_MANAGER_AVAILABLE = True
            print("✅ Prompt manager loaded from config.prompts")
        except ImportError:
            PROMPT_MANAGER_AVAILABLE = False
            print("❌ Prompt manager not available")

# Import RAG system
try:
    from src.rag.airline_industry_rag import AirlineIndustryRAG
    RAG_AVAILABLE = True
    print("✅ RAG system loaded successfully")
except ImportError:
    try:
        from rag.airline_industry_rag import AirlineIndustryRAG
        RAG_AVAILABLE = True
        print("✅ RAG system loaded from rag path")
    except ImportError:
        try:
            import sys
            sys.path.insert(0, os.path.join(parent_dir, 'rag'))
            from airline_industry_rag import AirlineIndustryRAG
            RAG_AVAILABLE = True
            print("✅ RAG system loaded with explicit path")
        except ImportError:
            try:
                from src.rag.airline_industry_rag import AirlineIndustryRAG
                RAG_AVAILABLE = True
                print("✅ RAG system loaded from src.rag")
            except ImportError:
                RAG_AVAILABLE = False
                print("❌ RAG system not available")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

class CreditRatingDashboard:
    """
    Main dashboard class for credit rating monitoring
    """
    
    def __init__(self):
        """Initialize dashboard"""
        self.risk_scorer = None
        self.current_scores = None
        self.historical_data = None
        
        # Initialize RAG system
        if RAG_AVAILABLE and OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                self.rag_system = AirlineIndustryRAG(OPENAI_API_KEY)
                self.rag_available = True
                print("✅ RAG system initialized successfully")
            except Exception as e:
                print(f"❌ RAG system initialization failed: {e}")
                self.rag_available = False
        else:
            self.rag_available = False
            if not RAG_AVAILABLE:
                print("❌ RAG system not available")
            if OPENAI_API_KEY == "your_openai_api_key_here":
                print("❌ OpenAI API key not set")
        
        # Initialize session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'alert_history' not in st.session_state:
            st.session_state.alert_history = []
        if 'hazard_report' not in st.session_state:
            st.session_state.hazard_report = None
        if 'risk_table_report' not in st.session_state:
            st.session_state.risk_table_report = None
        if 'heatmap_report' not in st.session_state:
            st.session_state.heatmap_report = None
        if 'alerts_report' not in st.session_state:
            st.session_state.alerts_report = None
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "📈 Hazard Curves"
        if 'hazard_companies_selection' not in st.session_state:
            st.session_state.hazard_companies_selection = None
        if 'table_companies_selection' not in st.session_state:
            st.session_state.table_companies_selection = None
        if 'heatmap_companies_selection' not in st.session_state:
            st.session_state.heatmap_companies_selection = None
        if 'alerts_threshold_value' not in st.session_state:
            st.session_state.alerts_threshold_value = None
        if 'models_loaded_status' not in st.session_state:
            st.session_state.models_loaded_status = False
        if 'rag_context' not in st.session_state:
            st.session_state.rag_context = None
        if 'rag_last_update' not in st.session_state:
            st.session_state.rag_last_update = None
    
    def load_models(self):
        """Load and initialize risk scoring models"""
        
        logger.info("[LOAD_MODELS] Starting model loading process...")
        
        if not MODEL_AVAILABLE:
            logger.error("[LOAD_MODELS] Models not available")
            st.error("Models not available")
            return False
        
        try:
            logger.info("[LOAD_MODELS] Creating spinner for model loading...")
            with st.spinner("🏋️ Loading risk scoring models..."):
                logger.info("[LOAD_MODELS] Initializing RatingRiskScorer...")
                
                # 안전한 모델 로딩 (캐시 우선, 필요시에만 DART 데이터 수집)
                try:
                    # 타임아웃 설정을 위한 시도 횟수 제한
                    max_retries = 2
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            logger.info(f"[LOAD_MODELS] Attempt {retry_count + 1} to create RatingRiskScorer...")
                            
                            # 메모리 사용량 모니터링
                            import psutil
                            process = psutil.Process()
                            memory_before = process.memory_info().rss / 1024 / 1024  # MB
                            logger.info(f"[LOAD_MODELS] Memory usage before: {memory_before:.2f} MB")
                            
                            # RatingRiskScorer 생성 (타임아웃 보호)
                            import signal
                            import threading
                            import time
                            
                            # 타임아웃 설정 (5분)
                            timeout_seconds = 300
                            result = [None]
                            exception = [None]
                            
                            def create_scorer():
                                try:
                                    result[0] = RatingRiskScorer(use_financial_data=True)
                                except Exception as e:
                                    exception[0] = e
                            
                            # 별도 스레드에서 실행
                            thread = threading.Thread(target=create_scorer)
                            thread.daemon = True
                            thread.start()
                            
                            # 타임아웃 대기
                            thread.join(timeout_seconds)
                            
                            if thread.is_alive():
                                logger.error(f"[LOAD_MODELS] Timeout after {timeout_seconds} seconds")
                                st.error(f"❌ Model loading timed out after {timeout_seconds} seconds")
                                return False
                            
                            if exception[0] is not None:
                                raise exception[0]
                            
                            self.risk_scorer = result[0]
                            
                            # 메모리 사용량 확인
                            memory_after = process.memory_info().rss / 1024 / 1024  # MB
                            logger.info(f"[LOAD_MODELS] Memory usage after: {memory_after:.2f} MB")
                            logger.info(f"[LOAD_MODELS] Memory increase: {memory_after - memory_before:.2f} MB")
                            
                            logger.info("[LOAD_MODELS] RatingRiskScorer created successfully")
                            break
                            
                        except Exception as e:
                            retry_count += 1
                            logger.warning(f"[LOAD_MODELS] Attempt {retry_count} failed: {e}")
                            
                            if retry_count >= max_retries:
                                logger.error(f"[LOAD_MODELS] All {max_retries} attempts failed")
                                raise e
                            
                            # 재시도 전 잠시 대기
                            time.sleep(2)
                    
                except Exception as model_error:
                    logger.error(f"[LOAD_MODELS] Model loading failed: {model_error}")
                    st.warning(f"⚠️ Model loading failed: {model_error}")
                    st.info("💡 Using sample data for demonstration")
                    return False
                    
            logger.info("[LOAD_MODELS] Model loading completed successfully")
            st.success("✅ Models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"[LOAD_MODELS] Error loading models: {e}")
            st.error(f"❌ Error loading models: {e}")
            st.info("💡 Using sample data for demonstration")
            return False
    
    def get_sample_firms(self) -> List[FirmProfile]:
        """Get sample Korean airline firms with current financial data"""
        
        return [
            FirmProfile(
                company_name="대한항공",
                current_rating="A",
                debt_to_assets=0.65,
                current_ratio=0.8,
                roa=0.02,
                roe=0.05,
                operating_margin=0.03,
                equity_ratio=0.35,
                asset_turnover=0.6,
                interest_coverage=2.5,
                quick_ratio=0.7,
                working_capital_ratio=0.1
            ),
            FirmProfile(
                company_name="아시아나항공",
                current_rating="B",
                debt_to_assets=0.85,
                current_ratio=0.6,
                roa=-0.02,
                roe=-0.05,
                operating_margin=-0.01,
                equity_ratio=0.15,
                asset_turnover=0.5,
                interest_coverage=1.2,
                quick_ratio=0.5,
                working_capital_ratio=-0.05
            ),
            FirmProfile(
                company_name="제주항공",
                current_rating="BBB",
                debt_to_assets=0.55,
                current_ratio=1.1,
                roa=0.04,
                roe=0.08,
                operating_margin=0.06,
                equity_ratio=0.45,
                asset_turnover=0.8,
                interest_coverage=3.5,
                quick_ratio=1.0,
                working_capital_ratio=0.15
            ),
            FirmProfile(
                company_name="티웨이항공",
                current_rating="BB",
                debt_to_assets=0.60,
                current_ratio=0.9,
                roa=0.01,
                roe=0.03,
                operating_margin=0.02,
                equity_ratio=0.40,
                asset_turnover=0.7,
                interest_coverage=2.0,
                quick_ratio=0.8,
                working_capital_ratio=0.05
            ),
            FirmProfile(
                company_name="에어부산",
                current_rating="B",
                debt_to_assets=0.70,
                current_ratio=0.7,
                roa=-0.01,
                roe=0.01,
                operating_margin=0.01,
                equity_ratio=0.30,
                asset_turnover=0.6,
                interest_coverage=1.8,
                quick_ratio=0.6,
                working_capital_ratio=0.02
            )
        ]
    
    def calculate_current_risks(self, firms: List[FirmProfile]) -> pd.DataFrame:
        """Calculate current risk scores for all firms"""
        
        if self.risk_scorer is None:
            return pd.DataFrame()
        
        risk_data = []
        
        for firm in firms:
            try:
                risk_assessment = self.risk_scorer.score_firm(firm, horizon=90)
                
                risk_data.append({
                    'company_name': firm.company_name,
                    'current_rating': firm.current_rating,
                    'overall_risk': risk_assessment['overall_change_probability'],
                    'upgrade_prob': risk_assessment['upgrade_probability'],
                    'downgrade_prob': risk_assessment['downgrade_probability'],
                    'default_prob': risk_assessment['default_probability'],
                    'risk_classification': risk_assessment['risk_classification'],
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
            except Exception as e:
                st.warning(f"⚠️ Error calculating risk for {firm.company_name}: {e}")
                continue
        
        return pd.DataFrame(risk_data)
    
    def generate_gpt4_report(self, prompt: str, context_data: str) -> str:
        """Generate comprehensive report using GPT-4-Turbo for bank loan officers"""
        
        if not OPENAI_AVAILABLE:
            return "❌ OpenAI 패키지가 설치되지 않았습니다. `pip install openai`로 설치해주세요."
        
        # RAG 컨텍스트 추가
        rag_context = ""
        if self.rag_available:
            try:
                rag_context = self.rag_system.get_prompt_context()
            except Exception as e:
                st.warning(f"⚠️ RAG 컨텍스트 로드 오류: {e}")
        
        # 프롬프트 매니저 사용
        if PROMPT_MANAGER_AVAILABLE:
            try:
                prompt_manager = get_prompt_manager()
                system_prompts = prompt_manager.get_system_prompt("comprehensive_report")
                system_prompt = {"role": "system", "content": system_prompts.get("comprehensive_report", "당신은 한국 시중은행의 기업금융 대출심사 전문가입니다.")}
                user_prompt = prompt_manager.get_user_prompt("comprehensive_report", 
                                                           prompt=prompt, 
                                                           context_data=context_data)
                
                # RAG 컨텍스트를 사용자 프롬프트에 추가
                if rag_context:
                    user_prompt += f"\n\n{rag_context}"
                    
            except Exception as e:
                st.warning(f"⚠️ 프롬프트 매니저 오류, 기본 프롬프트 사용: {e}")
                # 기본 프롬프트로 폴백
                system_prompt = {"role": "system", "content": "당신은 한국 시중은행의 기업금융 대출심사 전문가입니다."}
                user_prompt = f"분석 요청: {prompt}\n\n대시보드 데이터: {context_data}"
                if rag_context:
                    user_prompt += f"\n\n{rag_context}"
        else:
            # 기본 프롬프트 사용
            system_prompt = {"role": "system", "content": "당신은 한국 시중은행의 기업금융 대출심사 전문가입니다."}
            user_prompt = f"분석 요청: {prompt}\n\n대시보드 데이터: {context_data}"
            if rag_context:
                user_prompt += f"\n\n{rag_context}"
        
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[system_prompt, {"role": "user", "content": user_prompt}],
                max_tokens=4096,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ 레포트 생성 중 오류가 발생했습니다: {str(e)}\n\n💡 OpenAI API 키가 올바른지 확인해주세요."
    
    def generate_comprehensive_report(self, risk_df: pd.DataFrame, firms: List) -> str:
        """Generate comprehensive integrated report combining analysis and actionable recommendations"""
        
        if not OPENAI_AVAILABLE:
            return "❌ OpenAI 패키지가 설치되지 않았습니다. `pip install openai`로 설치해주세요."
        
        # 데이터 분석
        high_risk_firms = risk_df[risk_df['overall_risk'] > RISK_THRESHOLD]
        avg_risk = risk_df['overall_risk'].mean()
        max_risk_firm = risk_df.loc[risk_df['overall_risk'].idxmax()]
        min_risk_firm = risk_df.loc[risk_df['overall_risk'].idxmin()]
        
        # 업그레이드/다운그레이드 가능성 분석
        upgrade_candidates = risk_df[risk_df['upgrade_prob'] > 0.1].sort_values('upgrade_prob', ascending=False)
        downgrade_risks = risk_df[risk_df['downgrade_prob'] > 0.05].sort_values('downgrade_prob', ascending=False)
        
        # 최근 알림 이력
        recent_alerts = st.session_state.get('alert_history', [])[-3:]
        
        # 분석 대상 기업명 리스트 생성
        firm_names = [firm.company_name for firm in firms]
        
        # 각 기업의 상세 재무정보 생성
        detailed_firm_info = []
        for firm in firms:
            firm_detail = f"""
◈ **{firm.company_name}** (현재등급: {firm.current_rating})
   재무건전성 지표:
   - 부채비율: {firm.debt_to_assets:.1%} | 유동비율: {firm.current_ratio:.2f} | 당좌비율: {firm.quick_ratio:.2f}
   - ROA: {firm.roa:.1%} | ROE: {firm.roe:.1%} | 영업이익률: {firm.operating_margin:.1%}
   - 자기자본비율: {firm.equity_ratio:.1%} | 자산회전율: {firm.asset_turnover:.2f}
   - 이자보상배율: {firm.interest_coverage:.1f} | 운전자본비율: {firm.working_capital_ratio:.1%}
            """
            
            # 해당 기업의 위험도 정보 추가
            firm_risk = risk_df[risk_df['company_name'] == firm.company_name]
            if not firm_risk.empty:
                risk_row = firm_risk.iloc[0]
                firm_detail += f"""
   신용위험 현황:
   - 90일 전체변동위험: {risk_row['overall_risk']:.3%}
   - 등급상승 확률: {risk_row['upgrade_prob']:.3%} | 등급하락 확률: {risk_row['downgrade_prob']:.3%}
   - 부도발생 확률: {risk_row['default_prob']:.3%} | 위험분류: {risk_row['risk_classification']}
                """
            detailed_firm_info.append(firm_detail)
        
        # RAG 컨텍스트 추가
        rag_context = ""
        if self.rag_available:
            try:
                rag_context = self.rag_system.get_prompt_context()
            except Exception as e:
                st.warning(f"⚠️ RAG 컨텍스트 로드 오류: {e}")
        
        # 프롬프트 매니저 사용
        if PROMPT_MANAGER_AVAILABLE:
            try:
                prompt_manager = get_prompt_manager()
                system_prompts = prompt_manager.get_system_prompt("comprehensive_report")
                system_prompt = {"role": "system", "content": system_prompts.get("comprehensive_report", "당신은 한국 시중은행의 기업금융팀장입니다.")}
                user_prompt = prompt_manager.get_user_prompt("comprehensive_report",
                    company_count=len(risk_df),
                    company_names=', '.join(firm_names),
                    current_date=datetime.now().strftime('%Y년 %m월 %d일'),
                    avg_risk=avg_risk,
                    high_risk_count=len(high_risk_firms),
                    risk_threshold=RISK_THRESHOLD,
                    max_risk_company=max_risk_firm['company_name'],
                    max_risk_value=max_risk_firm['overall_risk'],
                    min_risk_company=min_risk_firm['company_name'],
                    min_risk_value=min_risk_firm['overall_risk'],
                    risk_std=risk_df['overall_risk'].std(),
                    detailed_firm_info=''.join(detailed_firm_info),
                    upgrade_candidates_info=upgrade_candidates[['company_name', 'upgrade_prob', 'current_rating']].to_string() if not upgrade_candidates.empty else "현재 등급 개선이 예상되는 기업 없음",
                    downgrade_risks_info=downgrade_risks[['company_name', 'downgrade_prob', 'current_rating']].to_string() if not downgrade_risks.empty else "현재 등급 악화가 우려되는 기업 없음",
                    risk_q25=risk_df['overall_risk'].quantile(0.25),
                    risk_q50=risk_df['overall_risk'].quantile(0.5),
                    risk_q75=risk_df['overall_risk'].quantile(0.75),
                    recent_alerts_info=f"최근 {len(recent_alerts)}건의 고위험 알림 발생 - 시스템 활성 모니터링 중" if recent_alerts else "최근 알림 없음 - 포트폴리오 안정적 운영"
                )
                
                # RAG 컨텍스트를 사용자 프롬프트에 추가
                if rag_context:
                    user_prompt += f"\n\n{rag_context}"
                    
            except Exception as e:
                st.warning(f"⚠️ 프롬프트 매니저 오류, 기본 프롬프트 사용: {e}")
                # 기본 프롬프트로 폴백
                system_prompt = {"role": "system", "content": "당신은 한국 시중은행의 기업금융팀장입니다."}
                user_prompt = f"항공업계 신용위험 분석 리포트를 작성해주세요. 데이터: {risk_df.to_string()}"
                if rag_context:
                    user_prompt += f"\n\n{rag_context}"
        else:
            # 기본 프롬프트 사용
            system_prompt = {"role": "system", "content": "당신은 한국 시중은행의 기업금융팀장입니다."}
            user_prompt = f"항공업계 신용위험 분석 리포트를 작성해주세요. 데이터: {risk_df.to_string()}"
            if rag_context:
                user_prompt += f"\n\n{rag_context}"

        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[system_prompt, {"role": "user", "content": user_prompt}],
                max_tokens=4096,  # 토큰 제한 문제 해결
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ 종합리포트 생성 중 오류가 발생했습니다: {str(e)}\n\n💡 OpenAI API 키가 올바른지 확인해주세요."
    
    def generate_hazard_curves_report(self, firms: List[FirmProfile]) -> str:
        """Generate comprehensive hazard curves report for bank loan officers"""
        
        if self.risk_scorer is None:
            return "❌ 모델이 로드되지 않았습니다. 먼저 모델을 로드해주세요."
        
        # 전체 화면 표시 데이터 수집
        risk_data = []
        horizons = [30, 60, 90, 120, 180, 270, 365]
        
        for firm in firms:
            # 각 기업의 재무정보
            firm_info = {
                'company': firm.company_name,
                'current_rating': firm.current_rating,
                'debt_to_assets': firm.debt_to_assets,
                'current_ratio': firm.current_ratio,
                'roa': firm.roa,
                'roe': firm.roe,
                'operating_margin': firm.operating_margin,
                'equity_ratio': firm.equity_ratio,
                'asset_turnover': firm.asset_turnover,
                'interest_coverage': firm.interest_coverage,
                'quick_ratio': firm.quick_ratio,
                'working_capital_ratio': firm.working_capital_ratio
            }
            
            # 시계열 위험도 데이터
            horizon_risks = []
            for horizon in horizons:
                try:
                    risk = self.risk_scorer.score_firm(firm, horizon=horizon)
                    horizon_risks.append({
                        'horizon': horizon,
                        'overall_risk': risk['overall_change_probability'],
                        'upgrade_prob': risk['upgrade_probability'],
                        'downgrade_prob': risk['downgrade_probability'],
                        'default_prob': risk['default_probability'],
                        'risk_classification': risk['risk_classification']
                    })
                except Exception as e:
                    continue
            
            firm_info['horizon_risks'] = horizon_risks
            risk_data.append(firm_info)
        
        # 포트폴리오 통계
        all_90d_risks = []
        all_365d_risks = []
        
        for firm_data in risk_data:
            for risk in firm_data['horizon_risks']:
                if risk['horizon'] == 90:
                    all_90d_risks.append(risk['overall_risk'])
                elif risk['horizon'] == 365:
                    all_365d_risks.append(risk['overall_risk'])
        
        # 대시보드 화면 표시 데이터 전체 정리
        context = f"""
=== 대출심사용 Hazard Curves 분석 데이터 ===

선택 분석 대상: {len(firms)}개 항공사 ({', '.join([f.company_name for f in firms])})
분석 시계: 30일, 60일, 90일, 120일, 180일, 270일, 365일

=== 각 항공사별 상세 정보 ===
"""
        
        for firm_data in risk_data:
            context += f"""
◈ {firm_data['company']} (현재등급: {firm_data['current_rating']})
  [재무지표]
  - 부채비율: {firm_data['debt_to_assets']:.1%}
  - 유동비율: {firm_data['current_ratio']:.2f}
  - ROA: {firm_data['roa']:.1%}
  - ROE: {firm_data['roe']:.1%}
  - 영업이익률: {firm_data['operating_margin']:.1%}
  - 자기자본비율: {firm_data['equity_ratio']:.1%}
  - 자산회전율: {firm_data['asset_turnover']:.2f}
  - 이자보상배율: {firm_data['interest_coverage']:.1f}
  - 당좌비율: {firm_data['quick_ratio']:.2f}
  - 운전자본비율: {firm_data['working_capital_ratio']:.1%}
  
  [시계열 신용위험 전망]"""
            
            for risk in firm_data['horizon_risks']:
                context += f"""
  - {risk['horizon']:3d}일 후: 전체변동 {risk['overall_risk']:.2%}, 등급상승 {risk['upgrade_prob']:.2%}, 등급하락 {risk['downgrade_prob']:.2%}, 부도위험 {risk['default_prob']:.3%} ({risk['risk_classification']})"""
        
        context += f"""

=== 포트폴리오 위험 집계 ===
- 90일 평균위험도: {np.mean(all_90d_risks):.2%}
- 90일 최대위험도: {np.max(all_90d_risks):.2%}
- 90일 최소위험도: {np.min(all_90d_risks):.2%}
- 365일 평균위험도: {np.mean(all_365d_risks):.2%}
- 365일 최대위험도: {np.max(all_365d_risks):.2%}
- 365일 최소위험도: {np.min(all_365d_risks):.2%}

=== 차트 해석 가이드 (대시보드 화면 기준) ===
- Overall Risk: 90일 내 신용등급 변동 확률 (대출심사 핵심지표)
- Upgrade Probability: 등급 개선 가능성 (긍정적 신호)
- Downgrade Probability: 등급 악화 위험 (여신 주의지표)
- Default Risk: 부도 발생 가능성 (여신손실 직결)
"""
        
        prompt = """대시보드의 Hazard Curves 탭에서 표시되는 시계열 신용위험 데이터를 기반으로, 
        은행 대출심사 및 여신관리 관점에서 다음 사항을 상세 분석해주세요:
        1) 각 항공사별 시간대별 신용위험 궤적 분석 및 여신심사 등급 판정
        2) 재무지표와 위험도 변화의 상관관계 분석 
        3) 단기(30-90일) vs 장기(270-365일) 위험패턴 차이점 및 대출만기 설정 권고
        4) 포트폴리오 관점에서의 항공업계 여신 집중도 리스크 평가"""
        
        return self.generate_gpt4_report(prompt, context)
    
    def generate_risk_table_report(self, risk_df: pd.DataFrame) -> str:
        """Generate comprehensive risk table report for bank loan officers"""
        
        if risk_df.empty:
            return "❌ 분석할 데이터가 없습니다."
        
        # 위험도 순으로 정렬 (대시보드와 동일)
        sorted_df = risk_df.sort_values('overall_risk', ascending=False)
        
        # 통계 계산
        avg_risk = sorted_df['overall_risk'].mean()
        max_risk = sorted_df['overall_risk'].max()
        min_risk = sorted_df['overall_risk'].min()
        std_risk = sorted_df['overall_risk'].std()
        
        # 임계값 정보
        high_risk_count = len(sorted_df[sorted_df['overall_risk'] > RISK_THRESHOLD])
        warning_risk_count = len(sorted_df[(sorted_df['overall_risk'] >= RISK_THRESHOLD * 0.7) & 
                                          (sorted_df['overall_risk'] <= RISK_THRESHOLD)])
        
        # 대시보드 화면 표시 데이터 전체 정리
        context = f"""
=== 대출심사용 90일 위험도 테이블 분석 데이터 ===

분석 대상: {len(risk_df)}개 항공사
분석 기준: 90일 신용등급 변동 확률
현재 알림 임계값: {RISK_THRESHOLD:.1%}
데이터 업데이트: {sorted_df['last_updated'].iloc[0] if 'last_updated' in sorted_df.columns else '실시간'}

=== 포트폴리오 위험도 통계 ===
- 평균 위험도: {avg_risk:.2%}
- 최대 위험도: {max_risk:.2%} 
- 최소 위험도: {min_risk:.2%}
- 표준편차: {std_risk:.2%}
- 고위험 기업수 (>{RISK_THRESHOLD:.1%}): {high_risk_count}개
- 주의 기업수 ({RISK_THRESHOLD*0.7:.1%}~{RISK_THRESHOLD:.1%}): {warning_risk_count}개

=== 위험도 순위별 상세 분석 (대시보드 테이블 기준) ===
"""
        
        for rank, (idx, row) in enumerate(sorted_df.iterrows(), 1):
            # 위험등급 분류
            if row['overall_risk'] > RISK_THRESHOLD:
                risk_level = "🔴 고위험"
            elif row['overall_risk'] > RISK_THRESHOLD * 0.7:
                risk_level = "🟡 주의"
            else:
                risk_level = "🟢 안전"
                
            context += f"""
[{rank}위] {row['company_name']} ({risk_level})
  - 현재 신용등급: {row['current_rating']}
  - 전체 변동위험: {row['overall_risk']:.3%} 
  - 등급 상승확률: {row['upgrade_prob']:.3%}
  - 등급 하락확률: {row['downgrade_prob']:.3%}
  - 부도 위험확률: {row['default_prob']:.3%}
  - 위험도 분류: {row['risk_classification']}
  - 업데이트: {row.get('last_updated', 'N/A')}
"""
        
        # 추가 분석 데이터
        context += f"""

=== 대시보드 Progress Bar 해석 ===
- Overall Risk: 90일 내 신용등급 변동 가능성 (0~50% 범위 표시)
- Upgrade ↗️: 등급 개선 확률 (0~30% 범위 표시) 
- Downgrade ↘️: 등급 악화 확률 (0~30% 범위 표시)
- Default ❌: 부도 발생 확률 (0~10% 범위 표시)

=== 색상 코딩 기준 ===
- 빨간색 하이라이트: 임계값({RISK_THRESHOLD:.1%}) 초과 기업
- 노란색 하이라이트: 임계값의 70% 이상 기업  
- 일반 표시: 안전 범위 기업

=== CSV 다운로드 데이터 포함 항목 ===
모든 수치 데이터, 업데이트 시간, 위험분류가 Excel 연동 가능
"""
        
        prompt = """대시보드의 Risk Table 탭에서 표시되는 90일 위험도 순위 데이터를 기반으로,
        은행 대출심사 및 여신관리 관점에서 다음 사항을 상세 분석해주세요:
        1) 각 항공사별 90일 신용위험 순위 및 여신심사 승인 권고등급 
        2) Progress Bar 수치 기반 담보/보증 요구사항 차등 적용 방안
        3) 고위험/주의/안전 그룹별 여신한도 및 금리 차등 정책 권고
        4) 정기 모니터링 주기 및 조기경보 시스템 운영 방안
        5) 업계 내 상대적 신용도 순위를 고려한 포트폴리오 재배분 전략"""
        
        return self.generate_gpt4_report(prompt, context)
    
    def generate_heatmap_report(self, risk_df: pd.DataFrame) -> str:
        """Generate comprehensive heatmap report for bank loan officers"""
        
        if risk_df.empty:
            return "❌ 분석할 데이터가 없습니다."
        
        # 위험 유형별 통계 계산
        upgrade_stats = {
            'mean': risk_df['upgrade_prob'].mean(),
            'max': risk_df['upgrade_prob'].max(),
            'min': risk_df['upgrade_prob'].min(),
            'std': risk_df['upgrade_prob'].std()
        }
        
        downgrade_stats = {
            'mean': risk_df['downgrade_prob'].mean(),
            'max': risk_df['downgrade_prob'].max(), 
            'min': risk_df['downgrade_prob'].min(),
            'std': risk_df['downgrade_prob'].std()
        }
        
        default_stats = {
            'mean': risk_df['default_prob'].mean(),
            'max': risk_df['default_prob'].max(),
            'min': risk_df['default_prob'].min(),
            'std': risk_df['default_prob'].std()
        }
        
        # 최고/최저 위험 기업 식별
        highest_risk_firm = risk_df.loc[risk_df['overall_risk'].idxmax()]
        lowest_risk_firm = risk_df.loc[risk_df['overall_risk'].idxmin()]
        highest_upgrade_firm = risk_df.loc[risk_df['upgrade_prob'].idxmax()]
        highest_downgrade_firm = risk_df.loc[risk_df['downgrade_prob'].idxmax()]
        
        # 대시보드 화면 표시 데이터 전체 정리
        context = f"""
=== 대출심사용 위험 히트맵 분석 데이터 ===

분석 대상: {len(risk_df)}개 항공사
히트맵 구성: 기업(행) × 위험유형(열) 매트릭스
색상 강도: 위험도 높을수록 진한 색상 표시

=== 각 항공사별 위험 매트릭스 (대시보드 히트맵 기준) ===
"""
        
        for idx, row in risk_df.iterrows():
            # 각 위험유형별 상대적 위치 계산
            upgrade_percentile = (risk_df['upgrade_prob'] <= row['upgrade_prob']).mean() * 100
            downgrade_percentile = (risk_df['downgrade_prob'] <= row['downgrade_prob']).mean() * 100
            default_percentile = (risk_df['default_prob'] <= row['default_prob']).mean() * 100
            overall_percentile = (risk_df['overall_risk'] <= row['overall_risk']).mean() * 100
            
            context += f"""
◈ {row['company_name']} (등급: {row['current_rating']})
  [위험유형별 절대치]
  - 등급상승 확률: {row['upgrade_prob']:.3%} (업계 상위 {100-upgrade_percentile:.0f}%)
  - 등급하락 확률: {row['downgrade_prob']:.3%} (업계 상위 {100-downgrade_percentile:.0f}%)  
  - 부도발생 확률: {row['default_prob']:.3%} (업계 상위 {100-default_percentile:.0f}%)
  - 전체변동 확률: {row['overall_risk']:.3%} (업계 상위 {100-overall_percentile:.0f}%)
  
  [히트맵 색상 해석]
  - 상승위험: {'🟢 연한색' if row['upgrade_prob'] < upgrade_stats['mean'] else '🟡 중간색' if row['upgrade_prob'] < upgrade_stats['mean'] + upgrade_stats['std'] else '🟠 진한색'}
  - 하락위험: {'🟢 연한색' if row['downgrade_prob'] < downgrade_stats['mean'] else '🟡 중간색' if row['downgrade_prob'] < downgrade_stats['mean'] + downgrade_stats['std'] else '🔴 진한색'}
  - 부도위험: {'🟢 연한색' if row['default_prob'] < default_stats['mean'] else '🟡 중간색' if row['default_prob'] < default_stats['mean'] + default_stats['std'] else '🔴 진한색'}
"""
        
        context += f"""

=== 포트폴리오 위험 분포 통계 ===

[등급상승 위험 분포]
- 평균: {upgrade_stats['mean']:.3%}
- 최대: {upgrade_stats['max']:.3%} ({highest_upgrade_firm['company_name']})
- 최소: {upgrade_stats['min']:.3%}
- 표준편차: {upgrade_stats['std']:.3%}

[등급하락 위험 분포]  
- 평균: {downgrade_stats['mean']:.3%}
- 최대: {downgrade_stats['max']:.3%} ({highest_downgrade_firm['company_name']})
- 최소: {downgrade_stats['min']:.3%}
- 표준편차: {downgrade_stats['std']:.3%}

[부도발생 위험 분포]
- 평균: {default_stats['mean']:.3%}
- 최대: {default_stats['max']:.3%}
- 최소: {default_stats['min']:.3%}  
- 표준편차: {default_stats['std']:.3%}

=== 위험 집중도 분석 ===
- 최고 종합위험: {highest_risk_firm['company_name']} ({highest_risk_firm['overall_risk']:.3%})
- 최저 종합위험: {lowest_risk_firm['company_name']} ({lowest_risk_firm['overall_risk']:.3%})
- 위험도 격차: {highest_risk_firm['overall_risk'] - lowest_risk_firm['overall_risk']:.3%}p

=== 대시보드 히스토그램 정보 ===
- 분포 구간: 10구간으로 나누어 표시
- 알림 임계값: {RISK_THRESHOLD:.1%} (빨간 점선으로 표시)
- 임계값 초과 기업: {len(risk_df[risk_df['overall_risk'] > RISK_THRESHOLD])}개
"""
        
        prompt = """대시보드의 Heatmap 탭에서 표시되는 기업×위험유형 매트릭스와 위험분포 히스토그램을 기반으로,
        은행 대출심사 및 여신관리 관점에서 다음 사항을 상세 분석해주세요:
        1) 위험유형별(상승/하락/부도) 색상 강도 기준 여신심사 차등 정책 수립 방안
        2) 각 항공사의 상대적 위험 포지션 기반 여신한도 배분 전략
        3) 포트폴리오 위험 집중도 및 분산투자 개선 방향
        4) 히스토그램 분포 패턴을 활용한 업종별 여신 가이드라인 설정
        5) 위험도 격차 분석을 통한 프리미엄/디스카운트 금리 적용 기준"""
        
        return self.generate_gpt4_report(prompt, context)
    
    def generate_alerts_report(self, risk_df: pd.DataFrame, threshold: float) -> str:
        """Generate comprehensive alerts report for bank loan officers"""
        
        if risk_df.empty:
            return "❌ 분석할 데이터가 없습니다."
        
        # 위험도별 기업 분류
        high_risk_firms = risk_df[risk_df['overall_risk'] > threshold]
        warning_firms = risk_df[(risk_df['overall_risk'] >= threshold * 0.8) & (risk_df['overall_risk'] <= threshold)]
        safe_firms = risk_df[risk_df['overall_risk'] < threshold * 0.8]
        
        # 알림 이력 정보 (세션 스테이트에서)
        alert_history_count = len(st.session_state.get('alert_history', []))
        last_alert_time = st.session_state.get('alert_history', [])[-1]['timestamp'].strftime('%Y-%m-%d %H:%M') if alert_history_count > 0 else '없음'
        
        # 대시보드 화면 표시 데이터 전체 정리
        context = f"""
=== 대출심사용 알림 관리 시스템 분석 데이터 ===

현재 알림 임계값: {threshold:.1%}
총 분석 대상: {len(risk_df)}개 항공사
시스템 상태: {'🔴 알림 발생' if len(high_risk_firms) > 0 else '🟢 정상 운영'}
마지막 알림: {last_alert_time}
총 알림 이력: {alert_history_count}건

=== 위험도별 기업 분류 현황 ===

🔴 고위험군 (임계값 {threshold:.1%} 초과): {len(high_risk_firms)}개
🟡 주의군 (임계값의 80%~100%): {len(warning_firms)}개  
🟢 안전군 (임계값의 80% 미만): {len(safe_firms)}개

=== 고위험 기업 상세 정보 ===
"""
        
        if len(high_risk_firms) > 0:
            for idx, row in high_risk_firms.iterrows():
                excess_risk = row['overall_risk'] - threshold
                context += f"""
◈ {row['company_name']} (등급: {row['current_rating']}) 🚨 즉시대응필요
  - 현재 위험도: {row['overall_risk']:.3%}
  - 임계값 초과폭: +{excess_risk:.3%}p ({excess_risk/threshold*100:+.1f}%)
  - 등급상승 확률: {row['upgrade_prob']:.3%}
  - 등급하락 확률: {row['downgrade_prob']:.3%}
  - 부도발생 확률: {row['default_prob']:.3%}
  - 위험도 분류: {row['risk_classification']}
  - 권고조치: 여신한도 재검토, 담보보강, 모니터링 강화
"""
        else:
            context += "✅ 현재 고위험 임계값을 초과하는 기업이 없습니다.\n"
        
        context += "\n=== 주의 기업 모니터링 대상 ===\n"
        
        if len(warning_firms) > 0:
            for idx, row in warning_firms.iterrows():
                remaining_buffer = threshold - row['overall_risk']
                context += f"""
◈ {row['company_name']} (등급: {row['current_rating']}) ⚡ 예방적모니터링
  - 현재 위험도: {row['overall_risk']:.3%}
  - 임계값까지 여유: {remaining_buffer:.3%}p
  - 주요 위험요소: {'등급하락' if row['downgrade_prob'] > row['upgrade_prob'] else '등급상승'}
  - 권고조치: 정기점검 강화, 재무제표 분기별 제출
"""
        else:
            context += "✅ 현재 주의 수준에 해당하는 기업이 없습니다.\n"
        
        # 포트폴리오 통계
        context += f"""

=== 포트폴리오 알림 시스템 통계 ===
- 평균 위험도: {risk_df['overall_risk'].mean():.3%}
- 최대 위험도: {risk_df['overall_risk'].max():.3%} ({risk_df.loc[risk_df['overall_risk'].idxmax(), 'company_name']})
- 최소 위험도: {risk_df['overall_risk'].min():.3%} ({risk_df.loc[risk_df['overall_risk'].idxmin(), 'company_name']})
- 위험도 표준편차: {risk_df['overall_risk'].std():.3%}
- 임계값 활용률: {len(high_risk_firms)/len(risk_df)*100:.1f}% (초과 기업 비율)

=== 대시보드 알림 설정 정보 ===
- Slack 웹훅: {'✅ 연동완료' if st.session_state.get('slack_webhook_url') else '❌ 미설정'}
- 자동새로고침: 30초 간격
- 알림 버튼: 수동 발송 가능
- 임계값 조정: 5%~30% 범위에서 실시간 변경 가능
- 알림 이력: 최근 5건 표시, 세션별 저장

=== 최근 알림 이력 요약 ===
"""
        
        if alert_history_count > 0:
            recent_alerts = st.session_state.get('alert_history', [])[-3:]  # 최근 3건
            for i, alert in enumerate(reversed(recent_alerts), 1):
                context += f"""
[{i}] {alert['timestamp'].strftime('%m/%d %H:%M')} - {len(alert['firms'])}개 기업 알림
    대상: {', '.join(alert['firms'])}
"""
        else:
            context += "아직 발송된 알림이 없습니다.\n"
        
        prompt = f"""대시보드의 Alerts 탭에서 표시되는 알림 관리 시스템 데이터를 기반으로,
        은행 대출심사 및 여신관리 관점에서 다음 사항을 상세 분석해주세요:
        1) 현재 임계값({threshold:.1%}) 기준 고위험/주의 기업에 대한 즉시 여신조치 방안
        2) 알림 발생 빈도와 패턴 분석을 통한 조기경보 시스템 효과성 평가  
        3) 위험도별 차등 모니터링 주기 및 보고체계 수립 방안
        4) Slack 알림 연동을 통한 실시간 대응체계 구축 및 운영 프로세스
        5) 임계값 조정 및 알림 민감도 최적화를 위한 백테스팅 결과 반영 방안
        6) 포트폴리오 전체 관점에서의 위험 집중도 완화 및 분산 전략"""
        
        return self.generate_gpt4_report(prompt, context)
    
    def generate_hazard_curves(self, firms: List[FirmProfile]) -> go.Figure:
        """Generate hazard curves for all firms"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Overall Risk Over Time', 'Upgrade Probability', 'Downgrade Probability', 'Default Risk'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Generate time horizons (1 to 365 days)
        horizons = [30, 60, 90, 120, 180, 270, 365]
        colors = px.colors.qualitative.Set1
        
        # 🔧 Data collection for dynamic scaling
        all_overall_risks = []
        all_upgrade_probs = []
        all_downgrade_probs = []
        all_default_probs = []
        firm_data = []  # Store data for each firm
        
        for i, firm in enumerate(firms):
            if self.risk_scorer is None:
                continue
                
            overall_risks = []
            upgrade_probs = []
            downgrade_probs = []
            default_probs = []
            
            for horizon in horizons:
                try:
                    risk_assessment = self.risk_scorer.score_firm(firm, horizon=horizon)
                    
                    # 🔍 DEBUG: Graph value check
                    print(f"  🔍 GRAPH DEBUG {firm.company_name} @ {horizon}d:")
                    print(f"    - Overall: {risk_assessment['overall_change_probability']:.6f}")
                    print(f"    - Upgrade: {risk_assessment['upgrade_probability']:.6f}")  
                    print(f"    - Downgrade: {risk_assessment['downgrade_probability']:.6f}")
                    print(f"    - Default: {risk_assessment['default_probability']:.6f}")
                    
                    overall_risk = risk_assessment['overall_change_probability']
                    upgrade_prob = risk_assessment['upgrade_probability']
                    downgrade_prob = risk_assessment['downgrade_probability']
                    default_prob = risk_assessment['default_probability']
                    
                    overall_risks.append(overall_risk)
                    upgrade_probs.append(upgrade_prob)
                    downgrade_probs.append(downgrade_prob)
                    default_probs.append(default_prob)
                    
                    # 🔧 Collect all values for dynamic scaling
                    all_overall_risks.append(overall_risk)
                    all_upgrade_probs.append(upgrade_prob)
                    all_downgrade_probs.append(downgrade_prob)
                    all_default_probs.append(default_prob)
                    
                except Exception as e:
                    print(f"⚠️ Error getting risk assessment for {firm.company_name}: {e}")
                    # Fallback to simulated curves
                    base_risk = 0.05 + i * 0.02
                    overall_risk = base_risk * (1 + horizon/365)
                    upgrade_prob = base_risk * 0.6 * (1 + horizon/365)
                    downgrade_prob = base_risk * 0.4 * (1 + horizon/365)
                    default_prob = base_risk * 0.1 * (1 + horizon/365)
                    
                    overall_risks.append(overall_risk)
                    upgrade_probs.append(upgrade_prob)
                    downgrade_probs.append(downgrade_prob)
                    default_probs.append(default_prob)
                    
                    # Collect fallback values too
                    all_overall_risks.append(overall_risk)
                    all_upgrade_probs.append(upgrade_prob)
                    all_downgrade_probs.append(downgrade_prob)
                    all_default_probs.append(default_prob)
            
            # Store data for this firm
            firm_data.append({
                'name': firm.company_name,
                'overall_risks': overall_risks,
                'upgrade_probs': upgrade_probs,
                'downgrade_probs': downgrade_probs,
                'default_probs': default_probs
            })
            
            color = colors[i % len(colors)]
            
            # Overall risk curve
            fig.add_trace(
                go.Scatter(x=horizons, y=overall_risks, name=firm.company_name, 
                          line=dict(color=color), legendgroup=firm.company_name),
                row=1, col=1
            )
            
            # Upgrade probability
            fig.add_trace(
                go.Scatter(x=horizons, y=upgrade_probs, name=firm.company_name, 
                          line=dict(color=color), legendgroup=firm.company_name, showlegend=False),
                row=1, col=2
            )
            
            # Downgrade probability
            fig.add_trace(
                go.Scatter(x=horizons, y=downgrade_probs, name=firm.company_name, 
                          line=dict(color=color), legendgroup=firm.company_name, showlegend=False),
                row=2, col=1
            )
            
            # Default risk
            fig.add_trace(
                go.Scatter(x=horizons, y=default_probs, name=firm.company_name, 
                          line=dict(color=color), legendgroup=firm.company_name, showlegend=False),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Korean Airlines Credit Risk Hazard Curves",
            height=800,
            showlegend=True
        )
        
        # 🔧 Dynamic scale calculation with safety margins
        def calculate_dynamic_range(values, margin_factor=0.1, min_range=0.01):
            """Calculate dynamic range with margin"""
            if not values or all(v == 0 for v in values):
                return [0, min_range]
            
            min_val = min(values)
            max_val = max(values)
            
            # Add margin (10% by default)
            value_range = max_val - min_val
            margin = max(value_range * margin_factor, min_range * 0.1)
            
            # Ensure minimum range for visibility
            if value_range < min_range:
                center = (min_val + max_val) / 2
                return [max(0, center - min_range/2), center + min_range/2]
            
            return [max(0, min_val - margin), max_val + margin]
        
        # Calculate dynamic ranges for each subplot
        overall_range = calculate_dynamic_range(all_overall_risks, margin_factor=0.15)
        upgrade_range = calculate_dynamic_range(all_upgrade_probs, margin_factor=0.2, min_range=0.01)
        downgrade_range = calculate_dynamic_range(all_downgrade_probs, margin_factor=0.15)
        default_range = calculate_dynamic_range(all_default_probs, margin_factor=0.3, min_range=0.005)
        
        print(f"🔧 Dynamic ranges calculated:")
        print(f"  Overall: [{overall_range[0]:.4f}, {overall_range[1]:.4f}]")
        print(f"  Upgrade: [{upgrade_range[0]:.4f}, {upgrade_range[1]:.4f}]")
        print(f"  Downgrade: [{downgrade_range[0]:.4f}, {downgrade_range[1]:.4f}]")
        print(f"  Default: [{default_range[0]:.6f}, {default_range[1]:.6f}]")
        
        # Update axes with dynamic scales
        fig.update_xaxes(title_text="Days", row=1, col=1)
        fig.update_yaxes(title_text="Probability", range=overall_range, row=1, col=1)
        
        fig.update_xaxes(title_text="Days", row=1, col=2)
        fig.update_yaxes(title_text="Probability", range=upgrade_range, row=1, col=2)
        
        fig.update_xaxes(title_text="Days", row=2, col=1)
        fig.update_yaxes(title_text="Probability", range=downgrade_range, row=2, col=1)
        
        fig.update_xaxes(title_text="Days", row=2, col=2)
        fig.update_yaxes(title_text="Probability", range=default_range, row=2, col=2)
        
        return fig
    
    def create_risk_heatmap(self, risk_df: pd.DataFrame) -> go.Figure:
        """Create risk heatmap visualization"""
        
        if risk_df.empty:
            return go.Figure()
        
        # Prepare data for heatmap
        heatmap_data = risk_df[['company_name', 'upgrade_prob', 'downgrade_prob', 'default_prob']].copy()
        heatmap_data = heatmap_data.set_index('company_name').T
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=['Upgrade Risk', 'Downgrade Risk', 'Default Risk'],
            colorscale='RdYlBu_r',
            text=np.round(heatmap_data.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="Probability")
        ))
        
        fig.update_layout(
            title="Risk Heatmap - Korean Airlines",
            xaxis_title="Airlines",
            yaxis_title="Risk Type",
            height=400
        )
        
        return fig
    
    def send_slack_alert(self, high_risk_firms: pd.DataFrame):
        """Send Slack webhook alert for high-risk firms"""
        
        if SLACK_WEBHOOK_URL is None:
            st.info("💡 Slack webhook not configured. Set SLACK_WEBHOOK_URL to enable alerts.")
            return False
        
        if high_risk_firms.empty:
            return True
        
        # Prepare alert message
        alert_text = "🚨 *Credit Rating Risk Alert - Korean Airlines*\n\n"
        alert_text += f"*High Risk Firms (>{RISK_THRESHOLD:.1%} change probability):*\n"
        
        for _, firm in high_risk_firms.iterrows():
            alert_text += (
                f"• *{firm['company_name']}* ({firm['current_rating']}): "
                f"{firm['overall_risk']:.1%} risk, "
                f"Downgrade: {firm['downgrade_prob']:.1%}\n"
            )
        
        alert_text += f"\n_Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        # Slack message payload
        payload = {
            "text": alert_text,
            "username": "Credit Risk Monitor",
            "icon_emoji": ":warning:",
            "channel": "#risk-monitoring"
        }
        
        try:
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                st.success(f"✅ Slack alert sent for {len(high_risk_firms)} high-risk firms")
                
                # Log to session state
                st.session_state.alert_history.append({
                    'timestamp': datetime.now(),
                    'firms': high_risk_firms['company_name'].tolist(),
                    'message': alert_text
                })
                
                return True
            else:
                st.error(f"❌ Slack alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error sending Slack alert: {e}")
            return False
    
    def run_dashboard(self):
        """Main dashboard application"""
        
        logger.info("[DASHBOARD] Starting dashboard run...")
        logger.info(f"[DASHBOARD] Current session_state keys: {list(st.session_state.keys())}")
        
        # Page configuration (only set once)
        try:
            st.set_page_config(
                page_title="Korean Airlines Credit Risk Dashboard",
                page_icon="✈️",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except Exception as e:
            pass  # Config already set
        
        # Header
        st.title("✈️ Korean Airlines Credit Risk Dashboard")
        st.markdown("---")
        
        # Sidebar
        st.sidebar.header("🎛️ Control Panel")
        
        # Model loading/unloading using buttons
        if not st.session_state.models_loaded_status:
            if st.sidebar.button("🔄 Enable Models", key="enable_models_btn", help="Load and enable the risk models"):
                with st.spinner("🏋️ Loading models..."):
                    success = self.load_models()
                    if success:
                        st.session_state.models_loaded_status = True
                        st.success("✅ Models loaded successfully!")
                    else:
                        st.error("❌ Failed to load models")
        else:
            st.sidebar.success("✅ Models Enabled")
            if st.sidebar.button("🔴 Disable Models", key="disable_models_btn", help="Disable the risk models"):
                st.session_state.models_loaded_status = False
                self.risk_scorer = None
                st.info("🔄 Models disabled")
        
        # Data source information
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Data Source")
        
        try:
            # Try different import paths for config
            try:
                from config.config import USE_REAL_DATA
            except ImportError:
                from config import USE_REAL_DATA
            if USE_REAL_DATA:
                st.sidebar.success("🎯 **Real DART Data Mode**")
                st.sidebar.info("Using actual financial statements from DART API")
            else:
                st.sidebar.warning("⚡ **Fast Dummy Data Mode**")
                st.sidebar.info("Using synthetic data for development")
        except ImportError:
            st.sidebar.warning("⚡ **Fast Dummy Data Mode**")
            st.sidebar.info("Using synthetic data for development")
        
        st.sidebar.markdown("""
        **💡 To switch data mode:**
        Edit `config.py` and change:
        ```python
        USE_REAL_DATA = True   # Real data
        USE_REAL_DATA = False  # Dummy data
        ```
        Then restart the dashboard.
        """)
        
        # Risk threshold setting
        st.sidebar.markdown("---")
        global RISK_THRESHOLD, SLACK_WEBHOOK_URL
        old_threshold = RISK_THRESHOLD
        RISK_THRESHOLD = st.sidebar.slider(
            "⚠️ Alert Threshold", 
            min_value=0.05, 
            max_value=0.30, 
            value=RISK_THRESHOLD, 
            step=0.01,
            format="%.2f",
            key="risk_threshold_slider"
        )
        if old_threshold != RISK_THRESHOLD:
            logger.info(f"[SIDEBAR] Risk threshold changed from {old_threshold} to {RISK_THRESHOLD}")
        
        # Slack webhook configuration
        slack_url = st.sidebar.text_input(
            "📱 Slack Webhook URL", 
            value=SLACK_WEBHOOK_URL or "",
            type="password",
            help="Enter your Slack webhook URL for alerts"
        )
        
        if slack_url:
            SLACK_WEBHOOK_URL = slack_url
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False, key="auto_refresh_checkbox")
        
        if auto_refresh:
            logger.info("[WIDGET] Auto-refresh enabled")
            st.sidebar.info("Auto-refresh enabled")
            # Note: In production, you'd implement proper auto-refresh
        
        # DART 데이터 캐시 관리
            st.sidebar.markdown("---")
            st.sidebar.subheader("💾 DART 데이터 캐시")
        
        # 캐시 시스템 상태 표시
        if CACHE_AVAILABLE:
            st.sidebar.success("✅ 캐시 시스템 활성화")
            
            # 캐시 활성화/비활성화 토글
            cache_enabled = st.sidebar.checkbox(
                "💾 캐시 시스템 사용", 
                value=True, 
                key="cache_enabled_checkbox",
                help="DART API 데이터를 캐시하여 중복 요청을 방지합니다"
            )
            
            try:
                cache = get_global_cache()
                cache_stats = cache.get_cache_stats()
                
                # 캐시 통계 표시
                st.sidebar.info(f"""
                **📊 캐시 현황**
                - 총 엔트리: {cache_stats['total_entries']}개
                - 유효한 데이터: {cache_stats['valid_entries']}개
                - 만료된 데이터: {cache_stats['expired_entries']}개
                - 총 크기: {cache_stats['total_size_mb']} MB
                - 캐시 기간: {cache_stats['cache_duration_hours']}시간
                """)
                
                # 캐시 관리 버튼들
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    if st.button("🧹 만료 정리", key="cleanup_cache_btn", help="만료된 캐시 엔트리를 정리합니다"):
                        removed_count = cache.cleanup_expired_cache()
                        if removed_count > 0:
                            st.success(f"✅ {removed_count}개 항목 정리됨")
                        else:
                            st.info("🔍 정리할 만료 항목 없음")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ 전체 삭제", key="clear_all_cache_btn", help="모든 캐시를 삭제합니다"):
                        removed_count = cache.clear_all_cache()
                        if removed_count > 0:
                            st.success(f"✅ {removed_count}개 항목 삭제됨")
                        else:
                            st.info("🔍 삭제할 항목 없음")
                        st.rerun()
                
                # 캐시 설정 정보
                with st.sidebar.expander("⚙️ 캐시 설정"):
                    st.text(f"📁 캐시 디렉토리: {cache.cache_dir}")
                    st.text(f"⏱️ 캐시 유효시간: {cache.cache_duration.total_seconds() / 3600:.1f}시간")
                    st.text(f"📊 메타데이터 파일: {os.path.basename(cache.metadata_file)}")
                
                # 캐시 세부 정보 (확장 가능)
                with st.sidebar.expander("📋 캐시 세부 정보"):
                    entries = cache.list_cached_entries()
                    if entries:
                        for entry in entries[:5]:  # 최근 5개만 표시
                            status = "✅" if entry['is_valid'] else "⏰"
                            st.text(f"{status} {entry['company_name']} {entry['year']}")
                        
                        if len(entries) > 5:
                            st.text(f"...및 {len(entries)-5}개 더")
                    else:
                        st.text("캐시된 데이터가 없습니다")
                
            except Exception as e:
                st.sidebar.error(f"캐시 정보 로드 실패: {e}")
        else:
            st.sidebar.error("❌ 캐시 시스템 비활성화")
            st.sidebar.info("""
            **캐시 시스템 활성화 방법:**
            1. `src/data/dart_data_cache.py` 파일이 존재하는지 확인
            2. Python 경로 설정 확인
            3. 대시보드 재시작
            """)
        
        # RAG 시스템 관리
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 RAG 시스템 (항공업계 검색)")
        
        if self.rag_available:
            st.sidebar.success("✅ RAG 시스템 활성화")
            
            try:
                # RAG 캐시 정보
                cache_info = self.rag_system.get_cache_info()
                
                # RAG 상태 표시
                status_icon = "✅" if cache_info['cache_valid'] else "⏰"
                st.sidebar.info(f"""
                **🔍 RAG 시스템 현황**
                - 상태: {status_icon} {'최신 정보' if cache_info['cache_valid'] else '업데이트 필요'}
                - 마지막 업데이트: {cache_info['last_update']}
                - 처리된 기사: {cache_info['articles_processed']}개
                - 상태: {cache_info['status']}
                """)
                
                # RAG 정보 업데이트 버튼
                if st.sidebar.button("🔄 항공업계 정보 업데이트", key="update_rag_btn", help="최신 항공업계 정보를 검색하고 요약합니다"):
                    with st.spinner("항공업계 정보 검색 및 요약 중..."):
                        try:
                            context = self.rag_system.get_airline_industry_context(force_update=True)
                            st.session_state.rag_context = context
                            st.session_state.rag_last_update = datetime.now()
                            st.success("✅ 항공업계 정보 업데이트 완료")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 업데이트 실패: {e}")
                
                # RAG 상세 정보
                with st.sidebar.expander("📋 RAG 상세 정보"):
                    if st.session_state.rag_context:
                        context = st.session_state.rag_context
                        st.text("**검색 키워드:**")
                        for keyword in context.get('search_keywords', [])[:3]:
                            st.text(f"• {keyword}")
                        
                        st.text("**핵심 포인트:**")
                        for point in context.get('key_points', [])[:3]:
                            st.text(f"• {point}")
                        
                        st.text("**정보 출처:**")
                        for source in context.get('sources', [])[:2]:
                            st.text(f"• {source[:50]}...")
                    else:
                        st.text("RAG 정보가 없습니다")
                
                # RAG 설정
                with st.sidebar.expander("⚙️ RAG 설정"):
                    st.text(f"📁 캐시 디렉토리: {self.rag_system.cache_dir}")
                    st.text(f"⏱️ 캐시 유효시간: {self.rag_system.cache_duration}")
                    st.text(f"🔍 검색 엔진: 네이버 뉴스 + 구글")
                    st.text(f"📝 요약 모델: GPT-4o-mini")
                        
            except Exception as e:
                st.sidebar.error(f"RAG 시스템 오류: {e}")
        else:
            st.sidebar.error("❌ RAG 시스템 비활성화")
            st.sidebar.info("""
            **RAG 시스템 활성화 방법:**
            1. `src/rag/` 디렉토리가 존재하는지 확인
            2. OpenAI API 키가 설정되어 있는지 확인
            3. 필요한 패키지 설치: `pip install requests beautifulsoup4`
            4. 대시보드 재시작
            """)
        
        # 프롬프트 관리 시스템 UI
        st.sidebar.subheader("🤖 GPT 프롬프트 관리")
        
        if PROMPT_MANAGER_AVAILABLE:
            st.sidebar.success("✅ 프롬프트 매니저 활성화")
            
            try:
                prompt_manager = get_prompt_manager()
                prompt_info = prompt_manager.get_prompt_info()
                
                # 프롬프트 시스템 정보 표시
                st.sidebar.info(f"""
                **📊 프롬프트 현황**
                - 현재 날짜: {prompt_info['market_context']['current_date']}
                - 시장 단계: {prompt_info['market_context']['market_phase']}
                - 사용 가능한 프롬프트: {len(prompt_info['available_prompt_types'])}개
                - 마지막 업데이트: {prompt_info['last_updated'][:19]}
                """)
                
                # 시장 컨텍스트 업데이트 버튼
                if st.sidebar.button("🔄 시장 컨텍스트 업데이트", key="update_market_context_btn", help="현재 시장 상황을 반영하여 프롬프트를 업데이트합니다"):
                    prompt_manager.update_market_context()
                    st.success("✅ 시장 컨텍스트 업데이트 완료")
                    st.rerun()
                
                # 프롬프트 설정 정보
                with st.sidebar.expander("⚙️ 프롬프트 설정"):
                    st.text(f"📁 프롬프트 디렉토리: {prompt_info['prompts_directory']}")
                    st.text(f"📊 주요 우려사항: {', '.join(prompt_info['market_context']['key_concerns'][:3])}...")
                    st.text(f"🎲 시나리오 확률: 낙관 {prompt_info['market_context']['scenario_probabilities']['optimistic']*100:.0%}, 기본 {prompt_info['market_context']['scenario_probabilities']['baseline']*100:.0%}, 비관 {prompt_info['market_context']['scenario_probabilities']['pessimistic']*100:.0%}")
                
                # 시장 트렌드 정보
                with st.sidebar.expander("📈 시장 트렌드"):
                    for trend in prompt_info['market_context']['industry_trends']:
                        st.text(f"• {trend}")
                
            except Exception as e:
                st.sidebar.error(f"프롬프트 매니저 오류: {e}")
        else:
            st.sidebar.error("❌ 프롬프트 매니저 비활성화")
            st.sidebar.info("""
            **프롬프트 매니저 활성화 방법:**
            1. `config/prompts.py` 파일이 존재하는지 확인
            2. Python 경로 설정 확인
            3. 대시보드 재시작
            """)
        
        # Main content
        if not MODEL_AVAILABLE:
            st.error("❌ Model modules are not available. Please check your installation.")
            return
        
        if not st.session_state.models_loaded_status or self.risk_scorer is None:
            st.info("💡 Please enable models using the checkbox in the sidebar to start analysis.")
            return
        
        # Get current data
        firms = self.get_sample_firms()
        
        with st.spinner("📊 Calculating current risk scores..."):
            risk_df = self.calculate_current_risks(firms)
        
        if risk_df.empty:
            st.error("❌ No risk data available")
            return
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_risk = risk_df['overall_risk'].mean()
            st.metric("📊 Average Risk", f"{avg_risk:.1%}")
        
        with col2:
            high_risk_count = len(risk_df[risk_df['overall_risk'] > RISK_THRESHOLD])
            st.metric("⚠️ High Risk Firms", high_risk_count)
        
        with col3:
            max_risk_firm = risk_df.loc[risk_df['overall_risk'].idxmax(), 'company_name']
            max_risk_value = risk_df['overall_risk'].max()
            st.metric("🔥 Highest Risk", f"{max_risk_firm}", f"{max_risk_value:.1%}")
        
        with col4:
            last_update = datetime.now().strftime("%H:%M:%S")
            st.metric("🕐 Last Update", last_update)
        
        st.markdown("---")
        
        # Tab interface
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Hazard Curves", "📋 Risk Table", "🔥 Heatmap", "🚨 Alerts", "📊 종합리포트"])
        
        with tab1:
            # Company selection
            company_names = [firm.company_name for firm in firms]
            selected_companies = st.multiselect(
                "✈️ Select Airlines to Display",
                options=company_names,
                default=company_names,  # All companies selected by default
                help="Choose which airlines to show in the hazard curves",
                key="hazard_companies_multiselect"
            )
            
            if selected_companies:
                # Filter firms based on selection
                selected_firms = [firm for firm in firms if firm.company_name in selected_companies]
                
                with st.spinner("Generating hazard curves..."):
                    hazard_fig = self.generate_hazard_curves(selected_firms)
                
                st.plotly_chart(hazard_fig, use_container_width=True)
            else:
                st.warning("⚠️ Please select at least one airline to display hazard curves.")
            
            # Interpretation
            st.info("""
            **📊 How to read the curves:**
            - **Overall Risk**: Probability of any rating change
            - **Upgrade Probability**: Chance of rating improvement  
            - **Downgrade Probability**: Risk of rating deterioration
            - **Default Risk**: Probability of default event
            """)
        
        with tab2:
            # Company selection for risk table
            table_companies = st.multiselect(
                "✈️ Select Airlines for Risk Table",
                options=company_names,
                default=company_names,  # All companies selected by default
                help="Choose which airlines to include in the risk table",
                key="table_selection"
            )
            
            if table_companies:
                # Filter and sort by overall risk (descending)
                filtered_table_df = risk_df[risk_df['company_name'].isin(table_companies)]
                risk_df_sorted = filtered_table_df.sort_values('overall_risk', ascending=False)
            else:
                st.warning("⚠️ Please select at least one airline for the risk table.")
                return
            
            # Style the dataframe
            def style_risk_table(df):
                def highlight_risk(val):
                    if val > RISK_THRESHOLD:
                        return 'background-color: #ffcccc; font-weight: bold'
                    elif val > RISK_THRESHOLD * 0.7:
                        return 'background-color: #fff2cc'
                    return ''
                
                return df.style.map(highlight_risk, subset=['overall_risk', 'downgrade_prob'])
            
            # Display table
            st.dataframe(
                style_risk_table(risk_df_sorted),
                use_container_width=True,
                column_config={
                    "overall_risk": st.column_config.ProgressColumn(
                        "Overall Risk",
                        help="90-day rating change probability",
                        min_value=0,
                        max_value=0.5,
                        format="%.3f"
                    ),
                    "upgrade_prob": st.column_config.ProgressColumn(
                        "Upgrade ↗️",
                        min_value=0,
                        max_value=0.3,
                        format="%.3f"
                    ),
                    "downgrade_prob": st.column_config.ProgressColumn(
                        "Downgrade ↘️",
                        min_value=0,
                        max_value=0.3,
                        format="%.3f"
                    ),
                    "default_prob": st.column_config.ProgressColumn(
                        "Default ❌",
                        min_value=0,
                        max_value=0.1,
                        format="%.3f"
                    )
                }
            )
            
            # Export functionality
            csv = risk_df_sorted.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"korean_airlines_risk_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with tab3:
            # Company selection for heatmap
            heatmap_companies = st.multiselect(
                "✈️ Select Airlines for Heatmap",
                options=company_names,
                default=company_names,  # All companies selected by default
                help="Choose which airlines to include in the heatmap",
                key="heatmap_selection"
            )
            
            if heatmap_companies:
                # Filter risk data based on selection
                filtered_risk_df = risk_df[risk_df['company_name'].isin(heatmap_companies)]
                heatmap_fig = self.create_risk_heatmap(filtered_risk_df)
                st.plotly_chart(heatmap_fig, use_container_width=True)
            else:
                st.warning("⚠️ Please select at least one airline for the heatmap.")
            
            # Risk distribution chart
            st.subheader("📊 Risk Distribution")
            
            fig_dist = px.histogram(
                risk_df, 
                x='overall_risk', 
                nbins=10,
                title="Distribution of 90-Day Risk Scores",
                labels={'overall_risk': 'Risk Probability', 'count': 'Number of Firms'}
            )
            fig_dist.add_vline(x=RISK_THRESHOLD, line_dash="dash", line_color="red", 
                              annotation_text=f"Alert Threshold ({RISK_THRESHOLD:.1%})")
            
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with tab4:
            # High risk firms
            high_risk_firms = risk_df[risk_df['overall_risk'] > RISK_THRESHOLD]
            
            if not high_risk_firms.empty:
                st.error(f"⚠️ {len(high_risk_firms)} firms exceed risk threshold ({RISK_THRESHOLD:.1%})")
                
                # Send alert button
                if st.button("📱 Send Slack Alert", key="send_slack_alert_btn"):
                    self.send_slack_alert(high_risk_firms)
                
                # Display high risk firms
                st.dataframe(high_risk_firms, use_container_width=True)
                
            else:
                st.success("✅ No firms currently exceed the risk threshold")
            
            # Alert history
            st.subheader("📜 Alert History")
            
            if st.session_state.alert_history:
                for i, alert in enumerate(reversed(st.session_state.alert_history[-5:])):  # Last 5 alerts
                    with st.expander(f"Alert {len(st.session_state.alert_history)-i}: {alert['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                        st.write(f"**Firms:** {', '.join(alert['firms'])}")
                        st.text(alert['message'])
            else:
                st.info("No alerts sent yet")
        
        with tab5:
            st.markdown("### 🎯 종합 위험 분석 리포트")
            st.markdown("*한국 항공업계 신용위험 종합 평가 및 대출 권고사항*")
            
            # 항공사 선택 체크박스
            st.markdown("#### ✈️ 분석 대상 항공사 선택")
            st.info("💡 리포트 생성 전에 분석할 항공사를 선택해주세요. (최소 1개 이상 선택 필수)")
            
            # 체크박스 컬럼으로 배치
            col1, col2, col3, col4, col5 = st.columns(5)
            
            selected_airlines = []
            with col1:
                if st.checkbox("대한항공", key="report_kal", value=True):
                    selected_airlines.append("대한항공")
            with col2:
                if st.checkbox("아시아나항공", key="report_asiana", value=True):
                    selected_airlines.append("아시아나항공")
            with col3:
                if st.checkbox("제주항공", key="report_jeju", value=True):
                    selected_airlines.append("제주항공")
            with col4:
                if st.checkbox("티웨이항공", key="report_tway", value=True):
                    selected_airlines.append("티웨이항공")
            with col5:
                if st.checkbox("에어부산", key="report_airbusan", value=True):  
                    selected_airlines.append("에어부산")
            
            # 선택된 항공사 표시
            if selected_airlines:
                st.success(f"✅ 선택된 항공사: {', '.join(selected_airlines)} ({len(selected_airlines)}개)")
            else:
                st.warning("⚠️ 분석할 항공사를 최소 1개 이상 선택해주세요.")
            
            # 리포트 생성 버튼 (선택된 항공사가 있을 때만 활성화)
            if selected_airlines:
                if st.button("📋 종합리포트 생성하기", key="comprehensive_report_btn", type="primary"):
                    # 선택된 항공사에 해당하는 데이터만 필터링
                    selected_risk_df = risk_df[risk_df['company_name'].isin(selected_airlines)]
                    selected_firms = [firm for firm in firms if firm.company_name in selected_airlines]
                    
                    with st.spinner("🧠 AI가 종합 분석 리포트를 작성 중입니다..."):
                        comprehensive_report = self.generate_comprehensive_report(selected_risk_df, selected_firms)
                        st.session_state.comprehensive_report = comprehensive_report
                        st.session_state.last_selected_airlines = selected_airlines.copy()
                        
                    # 선택된 항공사 확인 메시지 추가
                    st.info(f"📊 분석 완료: {', '.join(selected_airlines)} ({len(selected_airlines)}개 항목 기준으로 리포트 생성)")
            else:
                st.button("📋 종합리포트 생성하기", key="comprehensive_report_btn_disabled", disabled=True, help="항공사를 선택한 후 리포트를 생성할 수 있습니다.")
            
            # 리포트 표시
            if 'comprehensive_report' in st.session_state and st.session_state.comprehensive_report:
                st.markdown("---")
                
                # 분석 대상 항공사 표시
                if 'last_selected_airlines' in st.session_state:
                    selected_count = len(st.session_state.last_selected_airlines)
                    st.success(f"🎯 **분석 대상**: {', '.join(st.session_state.last_selected_airlines)} (총 {selected_count}개 항공사)")
                
                st.markdown(st.session_state.comprehensive_report, unsafe_allow_html=True)
                
                # 리포트 지우기 버튼
                if st.button("🗑️ 리포트 지우기", key="clear_comprehensive_report"):
                    st.session_state.comprehensive_report = None
                    st.rerun()
            else:
                st.info("💡 종합리포트를 생성하려면 위의 버튼을 클릭해주세요.")
        
        # Footer
        st.markdown("---")
        
        # Show data source information
        try:
            # Try different import paths for config
            try:
                from config.config import USE_REAL_DATA
            except ImportError:
                from config import USE_REAL_DATA
            data_source = "🎯 Real DART Financial Data" if USE_REAL_DATA else "⚡ Fast Dummy Data (Development Mode)"
        except ImportError:
            data_source = "⚡ Fast Dummy Data (Development Mode)"
        
        st.markdown(f"""
        **🏢 Korean Airlines Credit Risk Dashboard** | 
        Data refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
        Model: Multi-State Hazard with Financial Covariates | 
        Source: {data_source}
        """)

def main():
    """Main application entry point"""
    # Create dashboard instance only once per session  
    if 'dashboard_instance' not in st.session_state:
        st.session_state.dashboard_instance = CreditRatingDashboard()
    
    st.session_state.dashboard_instance.run_dashboard()

if __name__ == "__main__":
    main() 