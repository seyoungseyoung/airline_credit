#!/usr/bin/env python3
"""
End-to-end test for unified rating mapping system

This test ensures consistent rating interpretation across all modules:
- CreditRatingPreprocessor
- EnhancedMultiStateModel
- RatingRiskScorer
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.rating_mapping import UnifiedRatingMapping
from core.credit_rating_preprocessor import CreditRatingPreprocessor
from models.rating_risk_scorer import RatingRiskScorer


class TestUnifiedRatingMapping(unittest.TestCase):
    """Test unified rating mapping consistency"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_ratings = ['AAA', 'A', 'BBB', 'BB', 'B', 'D', 'NR']
        self.unified_mapping = UnifiedRatingMapping()
    
    def test_mapping_consistency(self):
        """Test that all modules use the same rating mapping"""
        # Get mappings from different modules
        unified_map = UnifiedRatingMapping.get_rating_mapping()
        
        # Test preprocessor uses unified mapping
        preprocessor = CreditRatingPreprocessor()
        preprocessor_map = preprocessor.rating_mapping
        
        # Test that mappings are identical
        self.assertEqual(unified_map, preprocessor_map,
                        "Preprocessor should use unified mapping")
        
        # Key test cases
        test_cases = [
            ('AAA', 0),   # Highest grade = lowest risk number
            ('A', 5),     # Investment grade
            ('BBB', 8),   # Investment grade boundary
            ('BB', 11),   # Speculative grade
            ('D', 21),    # Default
            ('NR', 22),   # Not rated
        ]
        
        for rating, expected_numeric in test_cases:
            self.assertEqual(unified_map[rating], expected_numeric,
                           f"Rating {rating} should map to {expected_numeric}")
    
    def test_risk_score_direction(self):
        """Test that risk scores increase with rating deterioration"""
        risk_scores = []
        for rating in ['AAA', 'A', 'BBB', 'BB', 'B', 'D']:
            score = UnifiedRatingMapping.calculate_risk_score(rating)
            risk_scores.append((rating, score))
        
        # Check that risk scores are monotonically increasing
        for i in range(len(risk_scores) - 1):
            current_rating, current_score = risk_scores[i]
            next_rating, next_score = risk_scores[i + 1]
            
            self.assertLess(current_score, next_score,
                           f"Risk score should increase: {current_rating}({current_score}) < {next_rating}({next_score})")
    
    def test_investment_grade_boundary(self):
        """Test investment grade classification"""
        # Investment grade (should be True)
        investment_grades = ['AAA', 'AA', 'A', 'BBB+', 'BBB', 'BBB-']
        for rating in investment_grades:
            self.assertTrue(UnifiedRatingMapping.is_investment_grade(rating),
                           f"{rating} should be investment grade")
        
        # Speculative grade (should be False)
        speculative_grades = ['BB+', 'BB', 'BB-', 'B', 'CCC', 'D']
        for rating in speculative_grades:
            self.assertFalse(UnifiedRatingMapping.is_investment_grade(rating),
                            f"{rating} should not be investment grade")
    
    def test_dataframe_export(self):
        """Test DataFrame creation and validation"""
        df = UnifiedRatingMapping.create_rating_dataframe()
        
        # Check required columns
        required_cols = ['RatingSymbol', 'RatingNumber', 'InvestmentGrade', 'RiskCategory', 'RiskScore']
        for col in required_cols:
            self.assertIn(col, df.columns, f"DataFrame should have column {col}")
        
        # Check that ratings are sorted by numeric value
        self.assertTrue(df['RatingNumber'].is_monotonic_increasing,
                       "RatingNumber should be sorted")
        
        # Check that risk scores increase with rating number
        self.assertTrue(df['RiskScore'].is_monotonic_increasing,
                       "RiskScore should increase with RatingNumber")
        
        # Check AAA and D values
        aaa_row = df[df['RatingSymbol'] == 'AAA'].iloc[0]
        d_row = df[df['RatingSymbol'] == 'D'].iloc[0]
        
        self.assertEqual(aaa_row['RatingNumber'], 0, "AAA should have RatingNumber 0")
        self.assertEqual(d_row['RatingNumber'], 21, "D should have RatingNumber 21")
        self.assertLess(aaa_row['RiskScore'], d_row['RiskScore'], "AAA should have lower risk than D")
    
    def test_data_validation(self):
        """Test rating data validation function"""
        # Create test data with mixed valid/invalid ratings
        test_data = pd.DataFrame({
            'RatingSymbol': ['AAA', 'A', 'BBB', 'INVALID', 'D', 'NR', ''],
            'company': ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        })
        
        validated_df = UnifiedRatingMapping.validate_rating_data(test_data)
        
        # Check that RatingNumber column was added
        self.assertIn('RatingNumber', validated_df.columns)
        
        # Check valid ratings
        valid_mask = validated_df['RatingSymbol'].isin(['AAA', 'A', 'BBB', 'D', 'NR'])
        valid_data = validated_df[valid_mask]
        
        self.assertFalse(valid_data['RatingNumber'].isna().any(),
                        "Valid ratings should have numeric values")
        
        # Check invalid ratings
        invalid_mask = ~valid_mask
        invalid_data = validated_df[invalid_mask]
        
        if not invalid_data.empty:
            self.assertTrue(invalid_data['RatingNumber'].isna().all(),
                           "Invalid ratings should have NaN numeric values")


class TestModuleIntegration(unittest.TestCase):
    """Test integration between different modules using unified mapping"""
    
    def test_preprocessor_scorer_consistency(self):
        """Test that preprocessor and scorer use same mappings"""
        # Create test rating data
        test_data = pd.DataFrame({
            'RatingSymbol': ['AAA', 'A', 'BBB', 'BB', 'B', 'D'],
            'date': pd.date_range('2023-01-01', periods=6, freq='M'),
            'company_id': ['COMP1'] * 6
        })
        
        # Test preprocessor mapping
        preprocessor = CreditRatingPreprocessor()
        test_data_with_numeric = test_data.copy()
        test_data_with_numeric['rating_numeric'] = test_data['RatingSymbol'].map(preprocessor.rating_mapping)
        
        # Test that all mappings are consistent
        unified_mapping = UnifiedRatingMapping.get_rating_mapping()
        
        for idx, row in test_data.iterrows():
            rating = row['RatingSymbol']
            preprocessor_numeric = preprocessor.rating_mapping[rating]
            unified_numeric = unified_mapping[rating]
            
            self.assertEqual(preprocessor_numeric, unified_numeric,
                           f"Preprocessor and unified mapping disagree on {rating}: {preprocessor_numeric} vs {unified_numeric}")
    
    def test_end_to_end_risk_calculation(self):
        """Test end-to-end risk calculation consistency"""
        # Test data
        ratings = ['AAA', 'A', 'BBB', 'BB', 'B']
        
        # Calculate risk scores using different methods
        unified_scores = [UnifiedRatingMapping.calculate_risk_score(r) for r in ratings]
        
        # Create preprocessor data
        df = pd.DataFrame({
            'rating': ratings,
            'rating_numeric': [UnifiedRatingMapping.get_numeric_rating(r) for r in ratings],
            'state': ['current'] * len(ratings),
            'nr_flag': [0] * len(ratings)
        })
        
        preprocessor = CreditRatingPreprocessor()
        df_with_scores = preprocessor.calculate_risk_scores(df)
        preprocessor_scores = df_with_scores['risk_score'].tolist()
        
        # Compare results (should be very similar)
        for i, (rating, unified_score, prep_score) in enumerate(zip(ratings, unified_scores, preprocessor_scores)):
            self.assertAlmostEqual(unified_score, prep_score, places=6,
                                 msg=f"Risk scores should match for {rating}: unified={unified_score}, preprocessor={prep_score}")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)