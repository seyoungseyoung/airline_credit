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

# Import our enhanced model
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

class RatingRiskScorer:
    """
    90-Day Rating Risk Scorer using Multi-State Hazard Models
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the risk scorer
        
        Args:
            model_path: Path to pre-trained model (if None, trains new model)
        """
        self.models = {}
        self.baseline_hazards = {}
        self.rating_mapping = {
            'AAA': 0, 'AA': 1, 'A': 2, 'BBB': 3, 
            'BB': 4, 'B': 5, 'CCC': 6, 'D': 7, 'NR': 8
        }
        self.reverse_rating_mapping = {v: k for k, v in self.rating_mapping.items()}
        
        # Train models if not provided
        if model_path is None:
            self._train_models()
        else:
            self._load_models(model_path)
    
    def _train_models(self):
        """Train the multi-state hazard models"""
        print("🏋️ Training multi-state hazard models...")
        
        if not MODEL_AVAILABLE:
            raise ImportError("EnhancedMultiStateModel not available")
        
        # Create and train enhanced model
        enhanced_model = EnhancedMultiStateModel(use_financial_data=True)
        enhanced_model.create_transition_episodes()
        enhanced_model.prepare_survival_data()
        model_results = enhanced_model.fit_enhanced_cox_models()
        
        # Store trained models
        self.models = enhanced_model.cox_models
        self.enhanced_model = enhanced_model
        
        print(f"✅ Trained {len(self.models)} Cox models")
        
        # Extract baseline hazards
        for transition_name, model in self.models.items():
            if hasattr(model, 'baseline_hazard_'):
                self.baseline_hazards[transition_name] = model.baseline_hazard_
                
        print(f"✅ Extracted {len(self.baseline_hazards)} baseline hazard functions")
    
    def _load_models(self, model_path: str):
        """Load pre-trained models from file"""
        # TODO: Implement model loading from pickle/joblib
        raise NotImplementedError("Model loading not yet implemented")
    
    def _firm_to_covariates(self, firm: FirmProfile) -> pd.Series:
        """Convert firm profile to model covariates"""
        
        # Convert rating to number if string
        if isinstance(firm.current_rating, str):
            current_rating = self.rating_mapping.get(firm.current_rating, 3)  # Default to BBB
        else:
            current_rating = firm.current_rating
        
        # Create covariate series
        covariates = pd.Series({
            'from_rating': current_rating,
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
        
        This represents the cumulative hazard up to the horizon
        """
        
        try:
            # Get survival function at the horizon
            horizon_years = horizon_days / 365.25
            
            # Predict survival function
            survival_func = model.predict_survival_function(
                covariates.to_frame().T, 
                times=[horizon_years]
            )
            
            if len(survival_func) == 0:
                return 0.0
            
            # S(t) = exp(-Λ(t)) where Λ(t) is cumulative hazard
            # So Λ(t) = -log(S(t))
            survival_prob = survival_func.iloc[0, 0]
            
            if survival_prob <= 0:
                return float('inf')  # Infinite hazard
            elif survival_prob >= 1:
                return 0.0  # No hazard
            else:
                cumulative_hazard = -np.log(survival_prob)
                return cumulative_hazard
                
        except Exception as e:
            print(f"⚠️ Error calculating hazard integral: {e}")
            return 0.0
    
    def _calculate_transition_probability(self, model: CoxPHFitter, covariates: pd.Series,
                                        horizon_days: int) -> float:
        """
        Calculate P(transition occurs within horizon)
        """
        
        try:
            horizon_years = horizon_days / 365.25
            
            # Get survival function (probability of NO transition)
            survival_func = model.predict_survival_function(
                covariates.to_frame().T,
                times=[horizon_years]
            )
            
            if len(survival_func) == 0:
                return 0.0
            
            survival_prob = survival_func.iloc[0, 0]
            
            # Transition probability = 1 - Survival probability
            transition_prob = 1 - survival_prob
            
            return max(0.0, min(1.0, transition_prob))  # Clamp to [0,1]
            
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
        
        # Calculate risk scores for each transition type
        risk_scores = {}
        cumulative_hazards = {}
        
        for transition_name, model in self.models.items():
            # Calculate cumulative hazard integral
            cum_hazard = self._calculate_hazard_integral(model, covariates, horizon)
            cumulative_hazards[transition_name] = cum_hazard
            
            # Calculate transition probability
            trans_prob = self._calculate_transition_probability(model, covariates, horizon)
            risk_scores[f'{transition_name}_probability'] = trans_prob
            
            print(f"  {transition_name}: Λ={cum_hazard:.4f}, P={trans_prob:.4f}")
        
        # Calculate overall rating change probability P(Δrating≠0 ≤ horizon)
        # This is 1 - P(rating stays stable)
        stable_prob = risk_scores.get('stable_probability', 0.0)  # This would be from a "stable" model
        
        # Alternative: Sum of all non-stable transition probabilities
        change_prob = (
            risk_scores.get('upgrade_probability', 0.0) +
            risk_scores.get('downgrade_probability', 0.0) +
            risk_scores.get('default_probability', 0.0) +
            risk_scores.get('withdrawn_probability', 0.0)
        )
        
        # Use the minimum of the two approaches (more conservative)
        overall_change_prob = min(1.0, change_prob)
        
        # Create comprehensive risk assessment
        assessment = {
            'company_name': firm.company_name,
            'current_rating': firm.current_rating,
            'horizon_days': horizon,
            'overall_change_probability': overall_change_prob,
            'upgrade_probability': risk_scores.get('upgrade_probability', 0.0),
            'downgrade_probability': risk_scores.get('downgrade_probability', 0.0),
            'default_probability': risk_scores.get('default_probability', 0.0),
            'withdrawn_probability': risk_scores.get('withdrawn_probability', 0.0),
            'cumulative_hazards': cumulative_hazards,
            'risk_classification': self._classify_risk_level(overall_change_prob)
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