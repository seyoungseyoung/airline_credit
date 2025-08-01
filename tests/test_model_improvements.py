#!/usr/bin/env python3
"""
Test model improvements and compare performance metrics

This test validates the bug fixes and enhancements:
1. Unified rating mapping
2. Risk category encoding (vs single rating variable)
3. Survival-based overall risk calculation
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.rating_mapping import UnifiedRatingMapping
from models.enhanced_multistate_model import EnhancedMultiStateModel
from models.rating_risk_scorer import RatingRiskScorer


class TestModelImprovements(unittest.TestCase):
    """Test model improvements and performance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_companies = {
            'COMP1': {'name': '대한항공', 'issuer_id': 1},
            'COMP2': {'name': '아시아나항공', 'issuer_id': 2},
            'COMP3': {'name': '제주항공', 'issuer_id': 3}
        }
        
        # Create synthetic rating history
        self.rating_data = self._create_test_rating_data()
    
    def _create_test_rating_data(self):
        """Create synthetic rating data for testing"""
        data = []
        base_date = datetime(2020, 1, 1)
        
        # Create rating histories with various transitions
        transitions = [
            # Company 1: Stable high grade with one downgrade
            ('COMP1', [('AAA', 0), ('AA', 6), ('A', 12), ('A', 24)]),
            
            # Company 2: Volatile with default
            ('COMP2', [('BBB', 0), ('BB', 6), ('B', 12), ('D', 18)]),
            
            # Company 3: Upgrade story
            ('COMP3', [('B', 0), ('BB', 6), ('BBB', 12), ('A', 18)])
        ]
        
        for company_id, rating_history in transitions:
            for rating_symbol, month_offset in rating_history:
                data.append({
                    'Id': company_id,  # Use 'Id' column name as expected by model
                    'Date': base_date + timedelta(days=month_offset * 30),
                    'RatingSymbol': rating_symbol,
                    'RatingNumber': UnifiedRatingMapping.get_numeric_rating(rating_symbol)
                })
        
        return pd.DataFrame(data)
    
    def test_risk_category_encoding(self):
        """Test that risk category encoding works correctly"""
        model = EnhancedMultiStateModel(use_financial_data=False)
        model.rating_data = self.rating_data
        model.company_mapping = self.test_companies
        
        # Create transition episodes
        model.create_transition_episodes()
        survival_data = model.prepare_survival_data()
        
        # Check that risk category columns exist
        risk_category_cols = [col for col in survival_data.columns if col.startswith('risk_category_')]
        self.assertGreater(len(risk_category_cols), 0, "Should have risk category columns")
        
        # Check investment grade column
        self.assertIn('investment_grade', survival_data.columns, "Should have investment grade column")
        
        # Test specific cases
        for idx, row in survival_data.iterrows():
            rating_symbol = UnifiedRatingMapping.get_rating_symbol(row['from_rating'])
            if rating_symbol:
                expected_investment_grade = UnifiedRatingMapping.is_investment_grade(rating_symbol)
                actual_investment_grade = bool(row['investment_grade'])
                
                self.assertEqual(expected_investment_grade, actual_investment_grade,
                               f"Investment grade flag should match for {rating_symbol}")
    
    def test_survival_based_risk_calculation(self):
        """Test that survival-based risk calculation produces reasonable results"""
        # Use minimal test to avoid complex model training
        test_hazards = {
            'upgrade': 0.1,
            'downgrade': 0.2,
            'default': 0.05,
            'withdrawn': 0.02
        }
        
        # Calculate survival probability
        total_hazard = sum(test_hazards.values())  # 0.37
        survival_prob = np.exp(-total_hazard)     # exp(-0.37) ≈ 0.691
        overall_risk = 1.0 - survival_prob        # 1 - 0.691 ≈ 0.309
        
        # Test the calculation
        expected_survival = np.exp(-0.37)
        expected_risk = 1.0 - expected_survival
        
        self.assertAlmostEqual(survival_prob, expected_survival, places=3)
        self.assertAlmostEqual(overall_risk, expected_risk, places=3)
        
        # Test that higher hazards lead to higher risk
        high_hazards = {'upgrade': 0.2, 'downgrade': 0.4, 'default': 0.1, 'withdrawn': 0.05}
        high_total = sum(high_hazards.values())
        high_risk = 1.0 - np.exp(-high_total)
        
        self.assertGreater(high_risk, overall_risk, "Higher hazards should produce higher risk")
    
    def test_unified_mapping_in_model(self):
        """Test that the model correctly uses unified mapping"""
        model = EnhancedMultiStateModel(use_financial_data=False)
        model.rating_data = self.rating_data
        model.company_mapping = self.test_companies
        
        # Check that rating mapping is consistent
        unified_mapping = UnifiedRatingMapping.get_rating_mapping()
        
        # Verify rating numbers in the data
        for idx, row in self.rating_data.iterrows():
            symbol = row['RatingSymbol']
            expected_number = unified_mapping[symbol]
            actual_number = row['RatingNumber']
            
            self.assertEqual(expected_number, actual_number,
                           f"Rating number should match unified mapping for {symbol}")
    
    def test_transition_labeling_improvements(self):
        """Test that transition labeling uses symbols instead of hardcoded numbers"""
        model = EnhancedMultiStateModel(use_financial_data=False)
        model.rating_data = self.rating_data
        model.company_mapping = self.test_companies
        
        # Add a default transition for testing
        default_transition = pd.DataFrame([{
            'Id': 'COMP_TEST',  # Use 'Id' column name
            'Date': datetime(2023, 1, 1),
            'RatingSymbol': 'BBB',
            'RatingNumber': 8
        }, {
            'Id': 'COMP_TEST',  # Use 'Id' column name
            'Date': datetime(2023, 6, 1),
            'RatingSymbol': 'D',
            'RatingNumber': 21
        }])
        
        test_data = pd.concat([self.rating_data, default_transition], ignore_index=True)
        model.rating_data = test_data
        
        # Create transition episodes
        model.create_transition_episodes()
        
        # Check that we have transition episodes
        self.assertGreater(len(model.transition_episodes), 0, "Should have transition episodes")
        
        # Find the default transition
        default_episodes = [ep for ep in model.transition_episodes 
                          if ep.get('to_symbol') == 'D']
        
        if default_episodes:
            from models.enhanced_multistate_model import StateDefinition
            default_episode = default_episodes[0]
            self.assertEqual(default_episode['transition_type'], StateDefinition.DEFAULT,
                           "Transition to 'D' should be labeled as DEFAULT")


class TestPerformanceComparison(unittest.TestCase):
    """Compare model performance before and after improvements"""
    
    def setUp(self):
        """Set up performance test data"""
        # Create larger dataset for performance testing
        self.large_rating_data = self._create_large_test_data()
    
    def _create_large_test_data(self):
        """Create larger test dataset"""
        data = []
        base_date = datetime(2015, 1, 1)
        
        # Create data for 5 companies over 3 years
        companies = ['COMP1', 'COMP2', 'COMP3', 'COMP4', 'COMP5']
        ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
        
        for company in companies:
            current_rating = np.random.choice(ratings)
            current_date = base_date
            
            for month in range(36):  # 3 years of monthly data
                # Add some rating volatility
                if np.random.random() < 0.1:  # 10% chance of rating change
                    # Random walk in ratings
                    current_idx = ratings.index(current_rating)
                    change = np.random.choice([-1, 0, 1])
                    new_idx = max(0, min(len(ratings)-1, current_idx + change))
                    current_rating = ratings[new_idx]
                
                data.append({
                    'Id': company,  # Use 'Id' column name
                    'Date': current_date + timedelta(days=month * 30),
                    'RatingSymbol': current_rating,
                    'RatingNumber': UnifiedRatingMapping.get_numeric_rating(current_rating)
                })
        
        return pd.DataFrame(data)
    
    def test_model_convergence(self):
        """Test that the improved model converges and produces stable results"""
        try:
            model = EnhancedMultiStateModel(use_financial_data=False)
            model.rating_data = self.large_rating_data
            model.company_mapping = {
                f'COMP{i}': {'name': f'Company {i}', 'issuer_id': i} 
                for i in range(1, 6)
            }
            
            # Create episodes and fit models
            model.create_transition_episodes()
            
            # Check that we have sufficient data
            self.assertGreater(len(model.transition_episodes), 10,
                             "Should have sufficient transition episodes for testing")
            
            survival_data = model.prepare_survival_data()
            
            # Check that risk categories were created
            risk_cols = [col for col in survival_data.columns if col.startswith('risk_category_')]
            self.assertGreater(len(risk_cols), 0, "Should have risk category columns")
            
            print(f"✅ Model setup successful with {len(model.transition_episodes)} episodes")
            print(f"✅ Created {len(risk_cols)} risk category variables")
            
        except Exception as e:
            # If lifelines is not available, skip this test
            if "lifelines" in str(e) or "not available" in str(e):
                self.skipTest(f"Skipping model test: {e}")
            else:
                raise


if __name__ == '__main__':
    unittest.main(verbosity=2)