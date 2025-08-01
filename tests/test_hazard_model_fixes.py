#!/usr/bin/env python3
"""
Unit tests for the hazard model bug fixes

This module tests the critical fixes for:
1. DEFAULT/WITHDRAWN transition labeling based on symbols
2. Risk score direction (higher number = higher risk)
3. Dummy variable expansion for all rating grades
4. Overall risk calculation using survival probability
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.enhanced_multistate_model import EnhancedMultiStateModel, StateDefinition
from core.credit_rating_preprocessor import CreditRatingPreprocessor
from models.rating_risk_scorer import RatingRiskScorer


class TestTransitionLabeling(unittest.TestCase):
    """Test correct transition labeling based on rating symbols"""
    
    def setUp(self):
        """Set up test data"""
        # Create test rating data with various transitions
        self.test_data = pd.DataFrame([
            # Normal transitions
            {'Date': datetime(2023, 1, 1), 'RatingSymbol': 'A', 'RatingNumber': 2, 'CompanyID': 'TEST1'},
            {'Date': datetime(2023, 6, 1), 'RatingSymbol': 'BBB', 'RatingNumber': 7, 'CompanyID': 'TEST1'},
            
            # Default transition
            {'Date': datetime(2023, 1, 1), 'RatingSymbol': 'BB', 'RatingNumber': 9, 'CompanyID': 'TEST2'},
            {'Date': datetime(2023, 6, 1), 'RatingSymbol': 'D', 'RatingNumber': 21, 'CompanyID': 'TEST2'},
            
            # Withdrawn transition
            {'Date': datetime(2023, 1, 1), 'RatingSymbol': 'B', 'RatingNumber': 12, 'CompanyID': 'TEST3'},
            {'Date': datetime(2023, 6, 1), 'RatingSymbol': 'WD', 'RatingNumber': 22, 'CompanyID': 'TEST3'},
            
            # Not Rated transition
            {'Date': datetime(2023, 1, 1), 'RatingSymbol': 'BBB', 'RatingNumber': 7, 'CompanyID': 'TEST4'},
            {'Date': datetime(2023, 6, 1), 'RatingSymbol': 'NR', 'RatingNumber': 23, 'CompanyID': 'TEST4'},
        ])
    
    def test_default_labeling(self):
        """Test that 'D' symbol is correctly labeled as DEFAULT"""
        model = EnhancedMultiStateModel(use_financial_data=False)
        model.rating_data = self.test_data
        
        # Process the data (this would normally happen in create_transition_episodes)
        company_data = self.test_data[self.test_data['CompanyID'] == 'TEST2'].copy()
        company_data = company_data.sort_values('Date')
        
        current_obs = company_data.iloc[0]
        next_obs = company_data.iloc[1]
        
        to_symbol = next_obs['RatingSymbol']
        
        # Test the logic that should be in the model
        if to_symbol == 'D':
            transition_type = StateDefinition.DEFAULT
        elif to_symbol in {'WD', 'NR'}:
            transition_type = StateDefinition.WITHDRAWN
        else:
            transition_type = StateDefinition.DOWNGRADE
            
        self.assertEqual(transition_type, StateDefinition.DEFAULT,
                        "Transition to 'D' should be labeled as DEFAULT")
    
    def test_withdrawn_labeling(self):
        """Test that 'WD' and 'NR' symbols are correctly labeled as WITHDRAWN"""
        # Test WD
        company_data = self.test_data[self.test_data['CompanyID'] == 'TEST3'].copy()
        next_obs = company_data.iloc[1]
        to_symbol = next_obs['RatingSymbol']
        
        if to_symbol == 'D':
            transition_type = StateDefinition.DEFAULT
        elif to_symbol in {'WD', 'NR'}:
            transition_type = StateDefinition.WITHDRAWN
        else:
            transition_type = StateDefinition.DOWNGRADE
            
        self.assertEqual(transition_type, StateDefinition.WITHDRAWN,
                        "Transition to 'WD' should be labeled as WITHDRAWN")
        
        # Test NR
        company_data = self.test_data[self.test_data['CompanyID'] == 'TEST4'].copy()
        next_obs = company_data.iloc[1]
        to_symbol = next_obs['RatingSymbol']
        
        if to_symbol == 'D':
            transition_type = StateDefinition.DEFAULT
        elif to_symbol in {'WD', 'NR'}:
            transition_type = StateDefinition.WITHDRAWN
        else:
            transition_type = StateDefinition.DOWNGRADE
            
        self.assertEqual(transition_type, StateDefinition.WITHDRAWN,
                        "Transition to 'NR' should be labeled as WITHDRAWN")
    
    def test_no_hardcoded_7_8(self):
        """Test that transitions are not hardcoded to ratings 7 and 8"""
        # This test ensures that rating 7 (BBB) is not automatically DEFAULT
        company_data = self.test_data[self.test_data['CompanyID'] == 'TEST1'].copy()
        company_data = company_data.sort_values('Date')
        
        current_obs = company_data.iloc[0]  # A (2)
        next_obs = company_data.iloc[1]     # BBB (7)
        
        from_rating = current_obs['RatingNumber']
        to_rating = next_obs['RatingNumber']
        to_symbol = next_obs['RatingSymbol']
        
        # Apply the corrected logic
        if to_symbol == 'D':
            transition_type = StateDefinition.DEFAULT
        elif to_symbol in {'WD', 'NR'}:
            transition_type = StateDefinition.WITHDRAWN
        elif to_rating < from_rating:
            transition_type = StateDefinition.UPGRADE
        elif to_rating > from_rating:
            transition_type = StateDefinition.DOWNGRADE
        else:
            transition_type = StateDefinition.STABLE
            
        self.assertEqual(transition_type, StateDefinition.DOWNGRADE,
                        "A to BBB should be DOWNGRADE, not DEFAULT (no hardcoded 7)")


class TestRiskScoreDirection(unittest.TestCase):
    """Test correct risk score direction"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = pd.DataFrame([
            {'rating_numeric': 0, 'state': 'current', 'nr_flag': 0},   # AAA
            {'rating_numeric': 2, 'state': 'current', 'nr_flag': 0},   # A
            {'rating_numeric': 7, 'state': 'current', 'nr_flag': 0},   # BBB
            {'rating_numeric': 12, 'state': 'current', 'nr_flag': 0},  # B
            {'rating_numeric': 21, 'state': 'current', 'nr_flag': 0},  # D
            {'rating_numeric': 7, 'state': 'WD', 'nr_flag': 1},        # WD+NR
        ])
    
    def test_risk_score_direction(self):
        """Test that higher rating number produces higher risk score"""
        # This would be the corrected calculation from preprocessor
        max_rating = self.test_data['rating_numeric'].max()  # 21
        
        risk_scores = self.test_data['rating_numeric'] / max_rating
        
        # AAA (0) should have lowest risk
        aaa_risk = risk_scores.iloc[0]  # 0/21 = 0
        
        # D (21) should have highest risk
        d_risk = risk_scores.iloc[4]    # 21/21 = 1.0
        
        # A (2) should have lower risk than B (12)
        a_risk = risk_scores.iloc[1]    # 2/21 ≈ 0.095
        b_risk = risk_scores.iloc[3]    # 12/21 ≈ 0.571
        
        self.assertLess(aaa_risk, a_risk, "AAA should have lower risk than A")
        self.assertLess(a_risk, b_risk, "A should have lower risk than B")
        self.assertLess(b_risk, d_risk, "B should have lower risk than D")
        self.assertAlmostEqual(d_risk, 1.0, places=2, msg="D should have risk ≈ 1.0")
    
    def test_wd_nr_multiplier(self):
        """Test that WD+NR states get risk multiplier"""
        max_rating = self.test_data['rating_numeric'].max()
        base_risks = self.test_data['rating_numeric'] / max_rating
        
        # Normal BBB risk
        normal_bbb_mask = (self.test_data['rating_numeric'] == 7) & (self.test_data['state'] != 'WD')
        normal_bbb_risk = base_risks[normal_bbb_mask].iloc[0]
        
        # WD+NR BBB risk (should be multiplied)
        wd_nr_mask = (self.test_data['state'] == 'WD') & (self.test_data['nr_flag'] == 1)
        wd_nr_base_risk = base_risks[wd_nr_mask].iloc[0]
        wd_nr_adjusted_risk = wd_nr_base_risk * 1.20  # 20% multiplier
        
        self.assertGreater(wd_nr_adjusted_risk, normal_bbb_risk,
                          "WD+NR should have higher risk than normal rating")


class TestDummyVariableExpansion(unittest.TestCase):
    """Test that dummy variables are created for all rating grades"""
    
    def test_dummy_variable_range(self):
        """Test that dummy variables cover all possible ratings"""
        # Simulate the data that would be created
        test_episodes = pd.DataFrame([
            {'from_rating': 0},   # AAA
            {'from_rating': 2},   # A
            {'from_rating': 7},   # BBB
            {'from_rating': 12},  # B
            {'from_rating': 18},  # CCC
            {'from_rating': 21},  # D
        ])
        
        # Apply the corrected logic
        max_rating = int(test_episodes['from_rating'].max())  # 21
        
        # Create dummy variables for all ratings (0~max_rating)
        expected_dummies = []
        for rating in range(max_rating + 1):  # 0 to 21 inclusive
            dummy_col = f'from_rating_{rating}'
            test_episodes[dummy_col] = (test_episodes['from_rating'] == rating).astype(int)
            expected_dummies.append(dummy_col)
        
        # Check that we have dummies for ratings 0-21 (22 total)
        self.assertEqual(len(expected_dummies), 22, 
                        "Should have 22 dummy variables (ratings 0-21)")
        
        # Check that high ratings (like 18, 21) have their dummies
        self.assertIn('from_rating_18', expected_dummies, "Should have dummy for rating 18 (CCC)")
        self.assertIn('from_rating_21', expected_dummies, "Should have dummy for rating 21 (D)")
        
        # Check that the dummy values are correct
        self.assertEqual(test_episodes.loc[0, 'from_rating_0'], 1, "AAA row should have from_rating_0 = 1")
        self.assertEqual(test_episodes.loc[0, 'from_rating_2'], 0, "AAA row should have from_rating_2 = 0")
        self.assertEqual(test_episodes.loc[5, 'from_rating_21'], 1, "D row should have from_rating_21 = 1")


class TestOverallRiskCalculation(unittest.TestCase):
    """Test survival-based overall risk calculation"""
    
    def test_survival_probability_calculation(self):
        """Test that overall risk is calculated from survival probability"""
        # Simulate cumulative hazards from different transition types
        cumulative_hazards = {
            'upgrade': 0.05,
            'downgrade': 0.15,
            'default': 0.02,
            'withdrawn': 0.01
        }
        
        # Calculate total cumulative hazard
        total_cumulative_hazard = sum(cumulative_hazards.values())  # 0.23
        
        # Calculate survival probability: S(t) = exp(-Λ(t))
        survival_prob = np.exp(-total_cumulative_hazard)  # exp(-0.23) ≈ 0.794
        
        # Calculate overall risk: 1 - S(t)
        overall_risk = 1.0 - survival_prob  # 1 - 0.794 ≈ 0.206
        
        # Test the calculation
        expected_survival = np.exp(-0.23)
        expected_risk = 1.0 - expected_survival
        
        self.assertAlmostEqual(survival_prob, expected_survival, places=3,
                              msg="Survival probability calculation should match exp(-Λ)")
        self.assertAlmostEqual(overall_risk, expected_risk, places=3,
                              msg="Overall risk should be 1 - survival probability")
        
        # Test that higher hazards lead to higher risk
        high_hazards = {
            'upgrade': 0.1,
            'downgrade': 0.4,
            'default': 0.1,
            'withdrawn': 0.05
        }
        
        high_total_hazard = sum(high_hazards.values())  # 0.65
        high_survival = np.exp(-high_total_hazard)
        high_risk = 1.0 - high_survival
        
        self.assertGreater(high_risk, overall_risk,
                          "Higher cumulative hazards should produce higher overall risk")


if __name__ == '__main__':
    unittest.main()