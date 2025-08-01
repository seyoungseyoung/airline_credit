#!/usr/bin/env python3
"""
Rating Risk Scorer - 90-Day Risk Assessment Function
===================================================

Implements score_firm(firm, horizon=90) function that:
1. Takes firm characteristics as input
2. Integrates hazard function λ̂(t|X) over time horizon
3. Returns P(Δrating≠0 ≤ 90d) - probability of rating change within 90 days

Author: Korean Airlines Credit Rating Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from lifelines import CoxPHFitter
    from scipy import integrate
    LIFELINES_AVAILABLE = True
except ImportError:
    print("⚠️ Required packages not available. Install: pip install lifelines scipy")
    LIFELINES_AVAILABLE = False
    # Create dummy CoxPHFitter class to avoid NameError
    class CoxPHFitter:
        pass

# Import our enhanced model
try:
    from .enhanced_multistate_model import EnhancedMultiStateModel, StateDefinition
    MODEL_AVAILABLE = True
except ImportError:
    try:
        from enhanced_multistate_model import EnhancedMultiStateModel, StateDefinition
        MODEL_AVAILABLE = True
    except ImportError:
        print("⚠️ enhanced_multistate_model not available")
        MODEL_AVAILABLE = False

@dataclass
class FirmProfile:
    """Firm characteristics for risk scoring"""
    company_name: str
    current_rating: Union[str, int]  # Can be symbol (e.g., 'BBB') or number (e.g., 3)
    debt_to_assets: float
    current_ratio: float
    roa: float  # Return on Assets
    roe: float  # Return on Equity
    operating_margin: float
    equity_ratio: float
    asset_turnover: float
    interest_coverage: float
    quick_ratio: float
    working_capital_ratio: float
    
    # Optional additional ratios
    net_margin: Optional[float] = None
    liability_ratio: Optional[float] = None
    operating_cf_ratio: Optional[float] = None
    cf_to_debt: Optional[float] = None
    cf_coverage: Optional[float] = None
    debt_service_coverage: Optional[float] = None
    times_interest_earned: Optional[float] = None
    cash_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    total_asset_growth: Optional[float] = None
    
    # Credit rating preprocessing meta flags
    nr_flag: Optional[int] = 0  # 1 if currently NR, 0 if rated
    state: Optional[str] = None  # Current state (rating or 'WD')
    consecutive_nr_days: Optional[int] = 0  # Consecutive NR days

class RatingRiskScorer:
    """
    90-Day Rating Risk Scorer using Multi-State Hazard Models
    """
    
    def __init__(self, model_path: Optional[str] = None, use_financial_data: bool = False, 
                 hyperparams: Dict[str, float] = None):
        """
        Initialize the risk scorer
        
        Args:
            model_path: Path to pre-trained model (if None, trains new model)
            use_financial_data: Whether to use real financial data (DART API)
            hyperparams: Dictionary with hyperparameters for tuning
        """
        self.models = {}
        
        # 🔧 Store hyperparameters for dynamic adjustment
        self.hyperparams = hyperparams or {
            'beta': 0.7,                      # Acceleration factor
            'rating_multiplier_scale': 1.0,   # Scale for rating multipliers
            'baseline_hazard_scale': 1.0      # Scale for baseline hazards
        }
        self.baseline_hazards = {}
        
        # Use unified rating mapping for consistency
        from utils.rating_mapping import UnifiedRatingMapping
        self.rating_mapping = UnifiedRatingMapping.get_rating_mapping()
        self.reverse_rating_mapping = UnifiedRatingMapping.get_reverse_mapping()
        self.use_financial_data = use_financial_data
        
        # Train models if not provided
        if model_path is None:
            self._train_models()
        else:
            self._load_models(model_path)
    
    def _train_models(self):
        """Train the multi-state hazard models"""
        print("🏋️ [TRAIN MODELS] Training multi-state hazard models...")
        
        if not MODEL_AVAILABLE:
            raise ImportError("EnhancedMultiStateModel not available")
        
        try:
            # 타임아웃 설정 (5분)
            import threading
            import time
            
            timeout_seconds = 300
            result = [None]
            exception = [None]
            
            def train_enhanced_model():
                try:
                    # Create and train enhanced model (DART 데이터 수집 여부에 따라)
                    enhanced_model = EnhancedMultiStateModel(use_financial_data=self.use_financial_data)
                    enhanced_model.create_transition_episodes()
                    enhanced_model.prepare_survival_data()
                    model_results = enhanced_model.fit_enhanced_cox_models()
                    
                    # Store trained models
                    result[0] = {
                        'models': enhanced_model.cox_models,
                        'enhanced_model': enhanced_model,
                        'results': model_results
                    }
                except Exception as e:
                    exception[0] = e
            
            # 별도 스레드에서 모델 훈련
            thread = threading.Thread(target=train_enhanced_model)
            thread.daemon = True
            thread.start()
            
            # 타임아웃 대기
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                print(f"⚠️ [TRAIN MODELS] Training timeout after {timeout_seconds} seconds")
                raise TimeoutError(f"Model training timed out after {timeout_seconds} seconds")
            
            if exception[0] is not None:
                raise exception[0]
            
            if result[0] is None:
                raise RuntimeError("Model training failed - no result returned")
            
            # Store trained models
            self.models = result[0]['models']
            self.enhanced_model = result[0]['enhanced_model']
            
            print(f"✅ [TRAIN MODELS] Trained {len(self.models)} Cox models")
            
            # Debug: Check received models
            for name, model in self.models.items():
                print(f"  🔍 [SCORER DEBUG] Model {name}: type={type(model)}")
                print(f"  🔍 [SCORER DEBUG] Model {name}: has_summary={hasattr(model, 'summary')}")
                if hasattr(model, 'summary'):
                    try:
                        summary = model.summary
                        print(f"  🔍 [SCORER DEBUG] Model {name}: summary accessible, shape={summary.shape}")
                    except Exception as e:
                        print(f"  🔍 [SCORER DEBUG] Model {name}: summary error: {e}")
            
            # Extract baseline hazards
            for transition_name, model in self.models.items():
                if hasattr(model, 'baseline_hazard_'):
                    self.baseline_hazards[transition_name] = model.baseline_hazard_
                    
            print(f"✅ [TRAIN MODELS] Extracted {len(self.baseline_hazards)} baseline hazard functions")
            
        except Exception as e:
            print(f"❌ [TRAIN MODELS] Error training models: {e}")
            raise
    
    def _load_models(self, model_path: str):
        """Load pre-trained models from file"""
        # TODO: Implement model loading from pickle/joblib
        raise NotImplementedError("Model loading not yet implemented")
    
    def _firm_to_covariates(self, firm: FirmProfile) -> pd.Series:
        """Convert firm profile to model covariates using risk categories"""
        
        # Convert rating to number if string
        if isinstance(firm.current_rating, str):
            current_rating = self.rating_mapping.get(firm.current_rating, 8)  # Default to BBB
        else:
            current_rating = firm.current_rating
        
        # Use unified rating mapping for consistency
        from utils.rating_mapping import UnifiedRatingMapping
        rating_symbol = UnifiedRatingMapping.get_rating_symbol(current_rating)
        
        # Create risk category dummy variables
        risk_categories = {}
        for category in UnifiedRatingMapping.RISK_CATEGORIES.keys():
            cat_col = f'risk_category_{category.lower().replace(" ", "_")}'
            risk_categories[cat_col] = 0
        
        # Set the appropriate category
        if rating_symbol:
            risk_category = UnifiedRatingMapping.get_risk_category(rating_symbol)
            if risk_category:
                cat_col = f'risk_category_{risk_category.lower().replace(" ", "_")}'
                risk_categories[cat_col] = 1
        
        # 🔍 DEBUG: Rating conversion check
        print(f"  🔍 RATING DEBUG for {firm.company_name}:")
        print(f"    - Original rating: {firm.current_rating}")
        print(f"    - Converted to numeric: {current_rating}")
        print(f"    - Rating symbol: {rating_symbol}")
        
        # Create covariate series with rating + risk categories + financial ratios
        covariates = pd.Series({
            # 🔧 핵심 수정: Rating information for scoring
            'current_rating': current_rating,  # ← 누락된 핵심 키 추가!
            'from_rating': current_rating,     # Cox 모델 학습용 (기존 유지)
            
            # Risk category variables (new approach)
            **risk_categories,
            'investment_grade': 1 if rating_symbol and UnifiedRatingMapping.is_investment_grade(rating_symbol) else 0,
            
            # Financial ratios
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
        })
        
        # Add optional ratios if provided
        optional_ratios = [
            'net_margin', 'liability_ratio', 'operating_cf_ratio',
            'cf_to_debt', 'cf_coverage', 'debt_service_coverage',
            'times_interest_earned', 'cash_ratio', 'debt_to_equity',
            'total_asset_growth'
        ]
        
        for ratio in optional_ratios:
            value = getattr(firm, ratio, None)
            if value is not None:
                covariates[ratio] = value
        
        return covariates
    
    def _calculate_hazard_integral(self, model: CoxPHFitter, covariates: pd.Series, 
                                 horizon_days: int) -> float:
        """
        Calculate integral of hazard function λ̂(t|X) over time horizon
        
        Enhanced with time-dependent baseline hazard modeling
        """
        
        try:
            # 🔧 Convert to years for model prediction (models trained on annual data)
            horizon_years = horizon_days / 365.25
            
            # 🔧 Validate and clean covariates data with enhanced debugging
            print(f"  🔍 DEBUG: Original covariates shape: {len(covariates)}")
            print(f"  🔍 DEBUG: Original covariates dtypes: {covariates.dtypes}")
            
            clean_covariates = covariates.copy()
            
            # Check for NaN values and replace with 0
            nan_count = clean_covariates.isna().sum()
            if nan_count > 0:
                print(f"  ⚠️ Found {nan_count} NaN values in covariates, replacing with 0")
                clean_covariates = clean_covariates.fillna(0)
            
            # Ensure all values are numeric with detailed logging
            problematic_columns = []
            for idx, value in clean_covariates.items():
                original_type = type(value)
                if isinstance(value, (list, tuple, np.ndarray)):
                    print(f"  ⚠️ SEQUENCE FOUND: {idx} = {value} (type: {original_type})")
                    clean_covariates[idx] = float(value[0]) if len(value) > 0 else 0.0
                    problematic_columns.append(idx)
                elif isinstance(value, np.ndarray) and value.ndim > 0:
                    print(f"  ⚠️ NDARRAY FOUND: {idx} = {value} (shape: {value.shape})")
                    clean_covariates[idx] = float(value.flatten()[0]) if value.size > 0 else 0.0
                    problematic_columns.append(idx)
                elif hasattr(value, '__iter__') and not isinstance(value, (str, int, float, np.number)):
                    print(f"  ⚠️ ITERABLE FOUND: {idx} = {value} (type: {original_type})")
                    try:
                        clean_covariates[idx] = float(list(value)[0]) if len(list(value)) > 0 else 0.0
                    except:
                        clean_covariates[idx] = 0.0
                    problematic_columns.append(idx)
                elif not isinstance(value, (int, float, np.number)):
                    print(f"  ⚠️ Converting non-numeric {idx}: {value} ({original_type}) to float")
                    try:
                        clean_covariates[idx] = float(value)
                    except (ValueError, TypeError):
                        clean_covariates[idx] = 0.0
                        problematic_columns.append(idx)
            
            if problematic_columns:
                print(f"  🔧 Fixed {len(problematic_columns)} problematic columns: {problematic_columns}")
            
            # Final validation - ensure everything is scalar numeric
            final_check_failed = []
            for idx, value in clean_covariates.items():
                if not isinstance(value, (int, float, np.integer, np.floating)):
                    print(f"  ❌ FINAL CHECK FAILED: {idx} = {value} (type: {type(value)})")
                    clean_covariates[idx] = 0.0
                    final_check_failed.append(idx)
                elif hasattr(value, '__len__') and not isinstance(value, (str)):
                    print(f"  ❌ STILL HAS LENGTH: {idx} = {value} (type: {type(value)})")
                    clean_covariates[idx] = 0.0
                    final_check_failed.append(idx)
            
            if final_check_failed:
                print(f"  🔧 Final cleanup applied to: {final_check_failed}")
            
            print(f"  ✅ Clean covariates ready: {len(clean_covariates)} columns")
            
            # Prepare DataFrame for prediction with validation
            pred_df = clean_covariates.to_frame().T
            print(f"  🔍 Prediction DataFrame shape: {pred_df.shape}")
            print(f"  🔍 Prediction DataFrame columns: {list(pred_df.columns)[:10]}...")  # First 10 columns
            print(f"  🔍 Prediction DataFrame dtypes: {pred_df.dtypes.unique()}")
            
            # 🔧 Enhanced model validation with better error handling
            if not hasattr(model, 'summary'):
                print(f"  ⚠️ Model missing summary attribute, checking for fallback model...")
                if hasattr(model, 'base_hazard') and hasattr(model, 'predict_survival_function'):
                    print(f"  ✅ Using fallback model with base_hazard={getattr(model, 'base_hazard', 'unknown')}")
                else:
                    print(f"  ❌ Model appears not fitted properly (missing critical attributes)")
                    return self._calculate_time_dependent_hazard(covariates, horizon_days)
            
            # Double check that summary exists and is accessible (for regular Cox models)
            if hasattr(model, 'summary'):
                try:
                    _ = model.summary
                    print(f"  ✅ Model summary accessible")
                except (AttributeError, Exception) as e:
                    print(f"  ⚠️ Model summary not accessible: {e}, proceeding with caution...")
            else:
                print(f"  ✅ Using fallback model without summary")
            
            # 🔧 Enhanced prediction with time scaling for sub-annual horizons
            if horizon_years <= 1.0:
                # For horizons ≤ 1 year, use scaling approach to avoid flat curves
                print(f"  🔍 Short-term prediction: scaling {horizon_days} days from 1-year baseline")
                
                # Get 1-year survival probability as baseline
                survival_func_1year = model.predict_survival_function(
                    pred_df, 
                    times=[1.0]  # 1 year baseline
                )
                
                if len(survival_func_1year) == 0:
                    return self._calculate_time_dependent_hazard(covariates, horizon_days)
                
                # 🔧 Enhanced scaling with initial acceleration: S(t) = S(1)^(t^β) where β ≈ 0.7
                survival_1year = survival_func_1year.iloc[0, 0]
                beta = self.hyperparams.get('beta', 0.7)  # Dynamic acceleration factor
                scaling_factor = horizon_years ** beta  # Non-linear scaling for initial acceleration
                survival_prob = survival_1year ** scaling_factor
                
                print(f"  🔍 1-year survival: {survival_1year:.4f}")
                print(f"  🔍 Horizon years: {horizon_years:.4f}")
                print(f"  🔍 Beta (acceleration): {beta}")
                print(f"  🔍 Scaling factor (t^β): {scaling_factor:.4f}")
                print(f"  🔍 Scaled survival ({horizon_days}d): {survival_prob:.4f}")
                
            else:
                # For horizons > 1 year, predict directly
                print(f"  🔍 Long-term prediction: {horizon_years:.2f} years")
                survival_func = model.predict_survival_function(
                    pred_df, 
                    times=[horizon_years]
                )
                
                if len(survival_func) == 0:
                    return self._calculate_time_dependent_hazard(covariates, horizon_days)
                
                survival_prob = survival_func.iloc[0, 0]
            
            print(f"  🔍 Final survival probability: {survival_prob}")
            
            if survival_prob <= 0:
                print(f"  ⚠️ Survival prob <= 0, using fallback")
                return self._calculate_time_dependent_hazard(covariates, horizon_days)
            elif survival_prob >= 1.0:
                print(f"  ⚠️ Survival prob = 1.0 (perfect survival), using fallback")
                return self._calculate_time_dependent_hazard(covariates, horizon_days)
            elif survival_prob > 0.999:
                print(f"  ⚠️ Survival prob > 0.999 (too high), using fallback")
                return self._calculate_time_dependent_hazard(covariates, horizon_days)
            else:
                cumulative_hazard = -np.log(survival_prob)
                print(f"  ✅ Calculated cumulative hazard: {cumulative_hazard}")
                # Enhance with time dependency if hazard is too low
                if cumulative_hazard < 0.001:
                    print(f"  ⚠️ Hazard too low ({cumulative_hazard}), using time-dependent fallback")
                    cumulative_hazard = self._calculate_time_dependent_hazard(covariates, horizon_days)
                return cumulative_hazard
                
        except Exception as e:
            print(f"⚠️ Error calculating hazard integral, using fallback: {e}")
            return self._calculate_time_dependent_hazard(covariates, horizon_days)
    
    def _calculate_time_dependent_hazard(self, covariates: pd.Series, horizon_days: int) -> float:
        """
        Calculate time-dependent hazard using rating-differentiated baseline hazards
        """
        
        # Get firm's current rating risk level
        current_rating = covariates.get('current_rating', 3.0)  # Default to BBB
        financial_stress = self._assess_financial_stress(covariates)
        
        # 🔧 등급별 베이스라인 Hazard 분할 (Korean airline industry calibrated)
        def get_rating_bucket(rating: float) -> str:
            """Map rating to risk bucket for differentiated hazards"""
            if rating <= 6:     # AAA to A- (0-6): Investment Grade 상위
                return 'investment_grade'
            elif rating <= 9:   # BBB+ to BBB- (7-9): Investment Grade 하위  
                return 'investment_grade_lower'
            elif rating <= 12:  # BB+ to BB- (10-12): Speculative 상위
                return 'bb'
            elif rating <= 15:  # B+ to B- (13-15): Speculative 하위
                return 'b_or_lower'
            else:               # CCC+ to NR (16-22): High Risk
                return 'high_risk'
        
        bucket = get_rating_bucket(current_rating)
        
        # 등급별 베이스라인 hazard rates (대폭 차별화)
        base_hazards_by_bucket = {
            'investment_grade': {
                'upgrade': 0.015,   # 1.5% - 매우 낮은 업그레이드율 (이미 고등급)
                'downgrade': 0.03,  # 3% - 매우 낮은 다운그레이드율
                'default': 0.001    # 0.1% - 거의 없는 디폴트율
            },
            'investment_grade_lower': {
                'upgrade': 0.04,    # 4% - 중간 업그레이드율
                'downgrade': 0.06,  # 6% - 중간 다운그레이드율  
                'default': 0.003    # 0.3% - 낮은 디폴트율
            },
            'bb': {
                'upgrade': 0.08,    # 8% - 높은 업그레이드 가능성
                'downgrade': 0.12,  # 12% - 높은 다운그레이드율
                'default': 0.015    # 1.5% - 중간 디폴트율
            },
            'b_or_lower': {
                'upgrade': 0.12,    # 12% - 매우 높은 업그레이드 기회
                'downgrade': 0.20,  # 20% - 매우 높은 다운그레이드율
                'default': 0.040    # 4% - 높은 디폴트율
            },
            'high_risk': {
                'upgrade': 0.15,    # 15% - 최고 업그레이드 기회 (바닥에서)
                'downgrade': 0.25,  # 25% - 최고 다운그레이드율
                'default': 0.080    # 8% - 매우 높은 디폴트율
            }
        }
        
        # 🔧 올바른 등급별 위험 승수 (0-22 스케일 기준)
        rating_multiplier = 1.0
        
        if current_rating <= 3:      # AAA to AA- (0-3): 최고등급
            rating_multiplier = 0.5   
        elif current_rating <= 6:    # A+ to A- (4-6): 고등급
            rating_multiplier = 0.7
        elif current_rating <= 9:    # BBB+ to BBB- (7-9): 투자등급 하위
            rating_multiplier = 1.0   # 기준점
        elif current_rating <= 12:   # BB+ to BB- (10-12): 투기등급 상위
            rating_multiplier = 1.5
        elif current_rating <= 15:   # B+ to B- (13-15): 투기등급 하위  
            rating_multiplier = 2.5
        elif current_rating <= 20:   # CCC+ to C (16-20): 매우 위험
            rating_multiplier = 4.0
        else:                        # D, NR (21-22): 최고 위험
            rating_multiplier = 6.0
        
        # 🔧 스트레스 승수 완화
        stress_multiplier = 1.0 + financial_stress * 0.3  # 0.5 → 0.3
        
        # Time dependency: hazard increases with time (square root function)
        time_factor = np.sqrt(horizon_days / 365.25)
        
        # Calculate cumulative hazard with bucket-specific baseline
        transition_type = getattr(self, '_current_transition_type', 'downgrade')
        annual_baseline_hazard = base_hazards_by_bucket[bucket].get(transition_type, 0.05)
        
        # 🔧 Apply hyperparameter scaling
        scaled_baseline_hazard = annual_baseline_hazard * self.hyperparams.get('baseline_hazard_scale', 1.0)
        scaled_rating_multiplier = rating_multiplier * self.hyperparams.get('rating_multiplier_scale', 1.0)
        
        # 🔧 이중 위험 승수: bucket별 baseline + rating별 fine-tuning + hyperparameter scaling
        cumulative_hazard = scaled_baseline_hazard * scaled_rating_multiplier * stress_multiplier * time_factor
        
        print(f"  🔧 HYPERPARAMETER-TUNED FALLBACK HAZARD:")
        print(f"    - Transition type: {transition_type}")
        print(f"    - Current rating: {current_rating} (numeric)")
        print(f"    - Rating bucket: {bucket}")
        print(f"    - Base hazard: {annual_baseline_hazard:.4f}")
        print(f"    - Scaled baseline (×{self.hyperparams.get('baseline_hazard_scale', 1.0):.2f}): {scaled_baseline_hazard:.4f}")
        print(f"    - Rating multiplier: {rating_multiplier:.1f}x")
        print(f"    - Scaled rating (×{self.hyperparams.get('rating_multiplier_scale', 1.0):.2f}): {scaled_rating_multiplier:.1f}x")
        print(f"    - Stress multiplier: {stress_multiplier:.2f}")
        print(f"    - Time factor: {time_factor:.2f}")
        print(f"    - Beta: {self.hyperparams.get('beta', 0.7)}")
        print(f"    - Raw cumulative hazard: {cumulative_hazard:.4f}")
        
        # 🔧 MAX_LAMBDA = 1.0 상한 설정 (2.0 → 1.0)
        MAX_LAMBDA = 1.0
        final_hazard = max(0.001, min(MAX_LAMBDA, cumulative_hazard))
        print(f"    - Final hazard: {final_hazard}")
        
        return final_hazard
    
    def _assess_financial_stress(self, covariates: pd.Series) -> float:
        """
        Assess financial stress level (0-1) based on financial ratios
        """
        
        stress_score = 0.0
        
        # Debt ratios (higher = more stress)
        debt_to_assets = covariates.get('debt_to_assets', 0.5)
        if debt_to_assets > 0.8:
            stress_score += 0.3
        elif debt_to_assets > 0.6:
            stress_score += 0.1
        
        # Liquidity ratios (lower = more stress)
        current_ratio = covariates.get('current_ratio', 1.0)
        if current_ratio < 0.5:
            stress_score += 0.3
        elif current_ratio < 0.8:
            stress_score += 0.1
        
        # Profitability ratios (lower = more stress)
        roa = covariates.get('roa', 0.02)
        if roa < -0.02:  # Negative ROA
            stress_score += 0.4
        elif roa < 0.01:
            stress_score += 0.2
        
        return min(1.0, stress_score)
    
    def _calculate_transition_probability(self, model: CoxPHFitter, covariates: pd.Series,
                                        horizon_days: int) -> float:
        """
        Calculate P(transition occurs within horizon)
        """
        
        try:
            # 🔧 Convert to years for model prediction (models trained on annual data)
            horizon_years = horizon_days / 365.25
            
            # 🔧 Enhanced model validation for transition probability calculation
            if not hasattr(model, 'summary'):
                print(f"  ⚠️ Transition calc: Model missing summary, checking for fallback model...")
                if hasattr(model, 'base_hazard') and hasattr(model, 'predict_survival_function'):
                    print(f"  ✅ Transition calc: Using fallback model with base_hazard={getattr(model, 'base_hazard', 'unknown')}")
                else:
                    print(f"  ❌ Transition calc: Model appears not fitted properly")
                    return 0.0
            
            # Double check that summary exists and is accessible (for regular Cox models)
            if hasattr(model, 'summary'):
                try:
                    _ = model.summary
                    print(f"  ✅ Transition calc: Model summary accessible")
                except (AttributeError, Exception) as e:
                    print(f"  ⚠️ Transition calc: Model summary not accessible: {e}, proceeding...")
            else:
                print(f"  ✅ Transition calc: Using fallback model")
            
            # 🔧 Validate and clean covariates data with enhanced debugging  
            clean_covariates = covariates.copy()
            
            # Check for NaN values and replace with 0
            nan_count = clean_covariates.isna().sum()
            if nan_count > 0:
                clean_covariates = clean_covariates.fillna(0)
            
            # Ensure all values are numeric with detailed logging
            problematic_columns = []
            for idx, value in clean_covariates.items():
                original_type = type(value)
                if isinstance(value, (list, tuple, np.ndarray)):
                    clean_covariates[idx] = float(value[0]) if len(value) > 0 else 0.0
                    problematic_columns.append(idx)
                elif isinstance(value, np.ndarray) and value.ndim > 0:
                    clean_covariates[idx] = float(value.flatten()[0]) if value.size > 0 else 0.0
                    problematic_columns.append(idx)
                elif hasattr(value, '__iter__') and not isinstance(value, (str, int, float, np.number)):
                    try:
                        clean_covariates[idx] = float(list(value)[0]) if len(list(value)) > 0 else 0.0
                    except:
                        clean_covariates[idx] = 0.0
                    problematic_columns.append(idx)
                elif not isinstance(value, (int, float, np.number)):
                    try:
                        clean_covariates[idx] = float(value)
                    except (ValueError, TypeError):
                        clean_covariates[idx] = 0.0
                        problematic_columns.append(idx)
            
            # Final validation - ensure everything is scalar numeric
            for idx, value in clean_covariates.items():
                if not isinstance(value, (int, float, np.integer, np.floating)):
                    clean_covariates[idx] = 0.0
                elif hasattr(value, '__len__') and not isinstance(value, (str)):
                    clean_covariates[idx] = 0.0
            
            # 🔧 Enhanced prediction with time scaling for sub-annual horizons
            if horizon_years <= 1.0:
                # For horizons ≤ 1 year, use scaling approach
                print(f"  🔍 Transition calc - Short-term: scaling {horizon_days} days from 1-year baseline")
                
                # Get 1-year survival probability as baseline
                survival_func_1year = model.predict_survival_function(
                    clean_covariates.to_frame().T,
                    times=[1.0]  # 1 year baseline
                )
                
                if len(survival_func_1year) == 0:
                    return 0.0
                
                # 🔧 Enhanced scaling with initial acceleration: S(t) = S(1)^(t^β) where β ≈ 0.7
                survival_1year = survival_func_1year.iloc[0, 0]
                beta = self.hyperparams.get('beta', 0.7)  # Dynamic acceleration factor
                scaling_factor = horizon_years ** beta  # Non-linear scaling for initial acceleration
                survival_prob = survival_1year ** scaling_factor
                
                print(f"  🔍 Transition calc - 1y survival: {survival_1year:.4f}")
                print(f"  🔍 Transition calc - Scaling factor (t^β): {scaling_factor:.4f}")
                print(f"  🔍 Transition calc - Scaled survival ({horizon_days}d): {survival_prob:.4f}")
                
            else:
                # For horizons > 1 year, predict directly
                print(f"  🔍 Transition calc - Long-term: {horizon_years:.2f} years")
                survival_func = model.predict_survival_function(
                    clean_covariates.to_frame().T,
                    times=[horizon_years]
                )
                
                if len(survival_func) == 0:
                    return 0.0
                
                survival_prob = survival_func.iloc[0, 0]
            
            print(f"  🔍 Transition calc - Final survival probability: {survival_prob}")
            
            # Transition probability = 1 - Survival probability
            transition_prob = 1 - survival_prob
            print(f"  🔍 Raw transition probability: {transition_prob}")
            
            # 🔧 Default Risk 평평 문제 해결: Cox 모델이 의미 없는 결과를 낼 때 fallback 사용
            if survival_prob > 0.99 or transition_prob < 1e-4:
                print(f"  ⚠️ Cox model result too extreme (survival={survival_prob:.6f}, prob={transition_prob:.6f})")
                print(f"  🔄 Using time-dependent fallback instead...")
                
                # Fallback to time-dependent hazard model
                fallback_hazard = self._calculate_time_dependent_hazard(covariates, horizon_days)
                fallback_prob = 1.0 - np.exp(-fallback_hazard)
                
                print(f"  🔧 Fallback hazard: {fallback_hazard:.6f}")
                print(f"  🔧 Fallback probability: {fallback_prob:.6f}")
                
                clamped_prob = max(0.0, min(1.0, fallback_prob))
                print(f"  ✅ Final fallback probability: {clamped_prob}")
                
                return clamped_prob
            
            clamped_prob = max(0.0, min(1.0, transition_prob))
            print(f"  ✅ Final transition probability: {clamped_prob}")
            
            return clamped_prob
            
        except Exception as e:
            print(f"⚠️ Error calculating transition probability: {e}")
            return 0.0
    
    def score_firm(self, firm: Union[FirmProfile, Dict], horizon: int = 90) -> Dict[str, float]:
        """
        Calculate 90-day risk score for a firm
        
        Args:
            firm: FirmProfile object or dictionary with firm characteristics
            horizon: Time horizon in days (default: 90)
            
        Returns:
            Dictionary with risk scores for different transition types
        """
        
        if not LIFELINES_AVAILABLE:
            raise ImportError("lifelines and scipy required for risk scoring")
        
        # Convert dict to FirmProfile if needed
        if isinstance(firm, dict):
            firm = FirmProfile(**firm)
        
        # Convert firm characteristics to model covariates
        covariates = self._firm_to_covariates(firm)
        
        print(f"📊 Scoring {firm.company_name} (Rating: {firm.current_rating}) for {horizon} days")
        print(f"  🔍 Available models: {list(self.models.keys())}")
        print(f"  🔍 Covariates shape: {len(covariates)}")
        
        # Debug: Show sample covariate values
        sample_covariates = dict(list(covariates.items())[:5])
        print(f"  🔍 Sample covariates: {sample_covariates}")
        
        # Calculate risk scores for each transition type
        risk_scores = {}
        cumulative_hazards = {}
        
        # Process each transition type with enhanced time-dependent modeling
        transition_types = ['upgrade', 'downgrade', 'default']
        
        for transition_name in transition_types:
            # Set current transition type for hazard calculation
            self._current_transition_type = transition_name
            
            if transition_name in self.models:
                model = self.models[transition_name]
                print(f"  🔍 Using Cox model for {transition_name}")
                # Calculate cumulative hazard integral
                cum_hazard = self._calculate_hazard_integral(model, covariates, horizon)
                # Calculate transition probability
                trans_prob = self._calculate_transition_probability(model, covariates, horizon)
            else:
                print(f"  🔍 No Cox model for {transition_name}, using fallback")
                # Fallback to time-dependent model
                cum_hazard = self._calculate_time_dependent_hazard(covariates, horizon)
                trans_prob = 1.0 - np.exp(-cum_hazard)  # Convert hazard to probability
                print(f"  🔍 Fallback conversion: hazard={cum_hazard:.4f} -> prob={trans_prob:.4f}")
                
                # Validate the probability
                if trans_prob < 0 or trans_prob > 1:
                    print(f"  ⚠️ Invalid probability {trans_prob}, clamping to [0,1]")
                    trans_prob = max(0.0, min(1.0, trans_prob))
            
            cumulative_hazards[transition_name] = cum_hazard
            risk_scores[f'{transition_name}_probability'] = trans_prob
            
            print(f"  {transition_name}: Λ={cum_hazard:.4f}, P={trans_prob:.4f}")
        
        # Process additional models if they exist
        for transition_name, model in self.models.items():
            if transition_name not in transition_types:
                # Calculate cumulative hazard integral
                cum_hazard = self._calculate_hazard_integral(model, covariates, horizon)
                cumulative_hazards[transition_name] = cum_hazard
                
                # Calculate transition probability
                trans_prob = self._calculate_transition_probability(model, covariates, horizon)
                risk_scores[f'{transition_name}_probability'] = trans_prob
                
                print(f"  {transition_name}: Λ={cum_hazard:.4f}, P={trans_prob:.4f}")
        
        # 🔧 Calculate overall rating change probability using independent competing risks
        # Overall Risk = 1 - Π(1-Pᵢ) - assumes transition types are competing, not cumulative
        
        # Method 1: Individual transition probabilities (independent events)
        individual_risks = [prob for key, prob in risk_scores.items() 
                          if 'probability' in key and 'stable' not in key]
        
        # 🔧 극값 확률 경고 및 캘리브레이션
        for key, prob in risk_scores.items():
            if 'probability' in key and prob in (0.0, 1.0):
                transition_name = key.replace('_probability', '')
                print(f"⚠️ {transition_name} probability extreme ({prob}); check model calibration for {firm.company_name}")
        
        # Method 2: Independent competing risks formula = 1 - Π(1-Pᵢ)
        if individual_risks:
            # Product of survival probabilities for each transition type
            survival_product = np.prod([1 - p for p in individual_risks])
            overall_risk_independent = 1.0 - survival_product
        else:
            overall_risk_independent = 0.0
        
        # Method 3: Hazard-based (fallback, with capped hazards)
        total_cumulative_hazard = sum(cumulative_hazards.values())
        survival_prob = np.exp(-min(total_cumulative_hazard, 2.0))  # Cap at 2.0
        overall_risk_from_survival = 1.0 - survival_prob
        
        # 🔧 Use independent competing risks as primary method
        change_prob = overall_risk_independent if individual_risks else overall_risk_from_survival
        
        # Ensure probabilities are reasonable (stricter bounds)
        change_prob = min(0.85, max(0.001, change_prob))  # 0.99 → 0.85
        
        # Apply WD+NR risk adjustment if applicable
        overall_change_prob = change_prob  # Use the calculated change probability
        adjusted_change_prob = overall_change_prob
        risk_adjustment_factor = 1.0
        adjustment_reason = "None"
        
        if hasattr(firm, 'nr_flag') and hasattr(firm, 'state'):
            if firm.state == 'WD' and firm.nr_flag == 1:
                # Apply 20% risk multiplier for WD+NR state
                risk_adjustment_factor = 1.20
                adjusted_change_prob = min(1.0, overall_change_prob * risk_adjustment_factor)
                adjustment_reason = f"WD+NR state adjustment (x{risk_adjustment_factor})"
                
                print(f"  ⚠️ WD+NR state detected - applying {risk_adjustment_factor}x risk multiplier")
                print(f"  📊 Original risk: {overall_change_prob:.4f} → Adjusted: {adjusted_change_prob:.4f}")
            
            elif firm.nr_flag == 1 and firm.consecutive_nr_days >= 30:
                # Apply graduated risk adjustment for long-term NR
                days_factor = min(1.5, 1.0 + (firm.consecutive_nr_days - 30) / 365 * 0.5)
                risk_adjustment_factor = days_factor
                adjusted_change_prob = min(1.0, overall_change_prob * risk_adjustment_factor)
                adjustment_reason = f"Long-term NR adjustment (x{days_factor:.2f})"
                
                print(f"  ⚠️ Long-term NR detected ({firm.consecutive_nr_days} days) - applying {days_factor:.2f}x risk multiplier")
                print(f"  📊 Original risk: {overall_change_prob:.4f} → Adjusted: {adjusted_change_prob:.4f}")
        
        # Create comprehensive risk assessment
        assessment = {
            'company_name': firm.company_name,
            'current_rating': firm.current_rating,
            'horizon_days': horizon,
            'overall_change_probability': adjusted_change_prob,
            'original_change_probability': overall_change_prob,
            'risk_adjustment_factor': risk_adjustment_factor,
            'adjustment_reason': adjustment_reason,
            'upgrade_probability': risk_scores.get('upgrade_probability', 0.0),
            'downgrade_probability': risk_scores.get('downgrade_probability', 0.0),
            'default_probability': risk_scores.get('default_probability', 0.0),
            'withdrawn_probability': risk_scores.get('withdrawn_probability', 0.0),
            'cumulative_hazards': cumulative_hazards,
            'risk_classification': self._classify_risk_level(adjusted_change_prob),
            'nr_flag': getattr(firm, 'nr_flag', 0),
            'state': getattr(firm, 'state', None),
            'consecutive_nr_days': getattr(firm, 'consecutive_nr_days', 0)
        }
        
        return assessment
    
    def _classify_risk_level(self, change_prob: float) -> str:
        """Classify risk level based on change probability"""
        
        if change_prob >= 0.3:
            return "HIGH"
        elif change_prob >= 0.1:
            return "MEDIUM"
        elif change_prob >= 0.05:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def score_portfolio(self, firms: List[Union[FirmProfile, Dict]], 
                       horizon: int = 90) -> pd.DataFrame:
        """
        Score multiple firms and return as DataFrame
        
        Args:
            firms: List of FirmProfile objects or dictionaries
            horizon: Time horizon in days
            
        Returns:
            DataFrame with risk scores for all firms
        """
        
        results = []
        
        for firm in firms:
            try:
                score = self.score_firm(firm, horizon)
                results.append(score)
            except Exception as e:
                print(f"⚠️ Error scoring firm: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def create_risk_report(self, firm: Union[FirmProfile, Dict], 
                          horizon: int = 90) -> str:
        """Generate a comprehensive risk report for a firm"""
        
        scores = self.score_firm(firm, horizon)
        
        report = f"""
Rating Risk Assessment Report
============================

Company: {scores['company_name']}
Current Rating: {scores['current_rating']}
Assessment Period: {horizon} days
Risk Classification: {scores['risk_classification']}

Overall Rating Change Probability: {scores['overall_change_probability']:.1%}

Detailed Transition Probabilities:
- Upgrade:   {scores['upgrade_probability']:.1%}
- Downgrade: {scores['downgrade_probability']:.1%}
- Default:   {scores['default_probability']:.1%}
- Withdrawn: {scores['withdrawn_probability']:.1%}

Risk Interpretation:
"""
        
        if scores['risk_classification'] == 'HIGH':
            report += "⚠️  HIGH RISK: Significant probability of rating change within 90 days"
        elif scores['risk_classification'] == 'MEDIUM':
            report += "🔶 MEDIUM RISK: Moderate probability of rating change"
        elif scores['risk_classification'] == 'LOW':
            report += "🔵 LOW RISK: Low probability of rating change"
        else:
            report += "✅ VERY LOW RISK: Very stable rating expected"
        
        report += f"""

Key Risk Factors:
- Downgrade Risk: {'HIGH' if scores['downgrade_probability'] > 0.1 else 'MODERATE' if scores['downgrade_probability'] > 0.05 else 'LOW'}
- Default Risk: {'HIGH' if scores['default_probability'] > 0.01 else 'LOW'}

Recommended Actions:
"""
        
        if scores['downgrade_probability'] > 0.1:
            report += "- Monitor financial performance closely\n"
            report += "- Review credit facilities and covenants\n"
        
        if scores['default_probability'] > 0.01:
            report += "- Immediate financial review required\n"
            report += "- Consider credit protection measures\n"
        
        if scores['risk_classification'] in ['HIGH', 'MEDIUM']:
            report += "- Increase monitoring frequency\n"
            report += "- Update financial projections\n"
        
        return report

def demo_risk_scorer():
    """Demonstrate the 90-day risk scoring function"""
    
    print("🎯 90-Day Rating Risk Scorer Demo")
    print("=" * 50)
    
    # Create sample firm profiles for Korean Airlines
    sample_firms = [
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
        )
    ]
    
    try:
        # Initialize risk scorer
        print("🏋️ Initializing risk scorer...")
        scorer = RatingRiskScorer()
        
        print("\n📊 Individual Risk Assessments:")
        print("=" * 50)
        
        # Score each firm individually
        for firm in sample_firms:
            print(f"\n🏢 {firm.company_name}")
            print("-" * 30)
            
            # Get risk score
            risk_score = scorer.score_firm(firm, horizon=90)
            
            # Generate report
            report = scorer.create_risk_report(firm, horizon=90)
            print(report)
            
        # Portfolio analysis
        print("\n📈 Portfolio Risk Analysis:")
        print("=" * 50)
        
        portfolio_scores = scorer.score_portfolio(sample_firms, horizon=90)
        
        # Display summary table
        summary_cols = ['company_name', 'current_rating', 'risk_classification', 
                       'overall_change_probability', 'downgrade_probability']
        
        print(portfolio_scores[summary_cols].to_string(index=False, float_format='%.3f'))
        
        print(f"\n📊 Portfolio Risk Summary:")
        print(f"- Average Change Probability: {portfolio_scores['overall_change_probability'].mean():.1%}")
        print(f"- Highest Risk Firm: {portfolio_scores.loc[portfolio_scores['overall_change_probability'].idxmax(), 'company_name']}")
        print(f"- Risk Distribution:")
        
        risk_dist = portfolio_scores['risk_classification'].value_counts()
        for risk_level, count in risk_dist.items():
            print(f"  {risk_level}: {count} firms")
        
        return scorer, portfolio_scores
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None, None

if __name__ == "__main__":
    demo_risk_scorer() 