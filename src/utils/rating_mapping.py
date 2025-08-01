#!/usr/bin/env python3
"""
Unified rating mapping system for consistent rating-to-numeric conversion

This module provides a single source of truth for rating mappings across
all components of the credit rating analysis system.
"""

from typing import Dict, Optional
import pandas as pd


class UnifiedRatingMapping:
    """
    Unified rating mapping system using 0-based indexing
    
    This ensures consistent rating interpretation across:
    - CreditRatingPreprocessor
    - EnhancedMultiStateModel  
    - RatingRiskScorer
    - Dashboard components
    """
    
    # Master rating scale (0-based for mathematical consistency)
    RATING_SCALE = {
        # Investment Grade
        'AAA': 0,   'AA+': 1,   'AA': 2,    'AA-': 3,
        'A+': 4,    'A': 5,     'A-': 6,
        'BBB+': 7,  'BBB': 8,   'BBB-': 9,
        
        # Speculative Grade
        'BB+': 10,  'BB': 11,   'BB-': 12,
        'B+': 13,   'B': 14,    'B-': 15,
        'CCC+': 16, 'CCC': 17,  'CCC-': 18,
        'CC': 19,   'C': 20,    'D': 21,
        
        # Special States
        'NR': 22,   'WD': 22    # Not Rated and Withdrawn map to same value
    }
    
    # Reverse mapping for quick lookup
    NUMERIC_TO_RATING = {v: k for k, v in RATING_SCALE.items() if k != 'WD'}  # Exclude duplicate
    
    # Investment grade boundary
    INVESTMENT_GRADE_THRESHOLD = 9  # BBB- and above
    
    # Risk categories
    RISK_CATEGORIES = {
        'Prime': list(range(0, 4)),        # AAA to AA-
        'High Grade': list(range(4, 7)),   # A+ to A-  
        'Medium Grade': list(range(7, 10)), # BBB+ to BBB-
        'Speculative': list(range(10, 16)), # BB+ to B-
        'Highly Speculative': list(range(16, 21)), # CCC+ to C
        'Default': [21],                   # D
        'Not Rated': [22]                  # NR/WD
    }
    
    @classmethod
    def get_rating_mapping(cls) -> Dict[str, int]:
        """Get the standard rating to numeric mapping"""
        return cls.RATING_SCALE.copy()
    
    @classmethod
    def get_reverse_mapping(cls) -> Dict[int, str]:
        """Get numeric to rating mapping"""
        return cls.NUMERIC_TO_RATING.copy()
    
    @classmethod
    def get_numeric_rating(cls, rating_symbol: str) -> Optional[int]:
        """Convert rating symbol to numeric value"""
        return cls.RATING_SCALE.get(rating_symbol.upper())
    
    @classmethod
    def get_rating_symbol(cls, numeric_rating: int) -> Optional[str]:
        """Convert numeric rating to symbol"""
        return cls.NUMERIC_TO_RATING.get(numeric_rating)
    
    @classmethod
    def is_investment_grade(cls, rating: str) -> bool:
        """Check if rating is investment grade (BBB- and above)"""
        numeric = cls.get_numeric_rating(rating)
        return numeric is not None and numeric <= cls.INVESTMENT_GRADE_THRESHOLD
    
    @classmethod
    def get_risk_category(cls, rating: str) -> Optional[str]:
        """Get risk category for a rating"""
        numeric = cls.get_numeric_rating(rating)
        if numeric is None:
            return None
            
        for category, range_list in cls.RISK_CATEGORIES.items():
            if numeric in range_list:
                return category
        return None
    
    @classmethod
    def calculate_risk_score(cls, rating: str, max_rating: int = 22) -> float:
        """
        Calculate normalized risk score (0.0 to 1.0)
        
        Args:
            rating: Rating symbol (e.g., 'AAA', 'BBB', 'D')
            max_rating: Maximum rating numeric for normalization
            
        Returns:
            Risk score where 0.0 = lowest risk (AAA), 1.0 = highest risk (D)
        """
        numeric = cls.get_numeric_rating(rating)
        if numeric is None:
            return 0.5  # Default for unknown ratings
            
        return numeric / max_rating
    
    @classmethod
    def create_rating_dataframe(cls) -> pd.DataFrame:
        """Create a DataFrame with rating mappings for export/reference"""
        data = []
        for symbol, numeric in cls.RATING_SCALE.items():
            if symbol == 'WD':  # Skip duplicate entry
                continue
                
            data.append({
                'RatingSymbol': symbol,
                'RatingNumber': numeric,
                'InvestmentGrade': cls.is_investment_grade(symbol),
                'RiskCategory': cls.get_risk_category(symbol),
                'RiskScore': cls.calculate_risk_score(symbol)
            })
        
        return pd.DataFrame(data).sort_values('RatingNumber')
    
    @classmethod
    def validate_rating_data(cls, df: pd.DataFrame, rating_column: str = 'RatingSymbol') -> pd.DataFrame:
        """
        Validate and standardize rating data
        
        Args:
            df: DataFrame with rating data
            rating_column: Name of the rating column
            
        Returns:
            DataFrame with added RatingNumber column and validated ratings
        """
        df_clean = df.copy()
        
        # Standardize rating symbols
        df_clean[rating_column] = df_clean[rating_column].str.upper().str.strip()
        
        # Add numeric ratings
        df_clean['RatingNumber'] = df_clean[rating_column].map(cls.RATING_SCALE)
        
        # Flag invalid ratings
        invalid_mask = df_clean['RatingNumber'].isna()
        if invalid_mask.any():
            invalid_ratings = df_clean.loc[invalid_mask, rating_column].unique()
            print(f"⚠️ Warning: Found {invalid_mask.sum()} rows with invalid ratings: {invalid_ratings}")
        
        return df_clean
    
    @classmethod
    def export_mapping_csv(cls, file_path: str) -> None:
        """Export rating mapping to CSV file"""
        df = cls.create_rating_dataframe()
        df.to_csv(file_path, index=False)
        print(f"✅ Exported rating mapping to {file_path}")


# Convenience functions for backward compatibility
def get_rating_mapping() -> Dict[str, int]:
    """Get the unified rating mapping"""
    return UnifiedRatingMapping.get_rating_mapping()

def get_reverse_mapping() -> Dict[int, str]:
    """Get reverse rating mapping"""
    return UnifiedRatingMapping.get_reverse_mapping()


if __name__ == "__main__":
    # Demo usage
    mapping = UnifiedRatingMapping()
    
    print("📊 Unified Rating Mapping System")
    print("=" * 50)
    
    # Show mapping table
    df = mapping.create_rating_dataframe()
    print(df.to_string(index=False))
    
    print(f"\n📈 Total ratings: {len(mapping.RATING_SCALE) - 1}")  # -1 for WD duplicate
    print(f"📊 Investment grade threshold: {mapping.INVESTMENT_GRADE_THRESHOLD} (BBB- and above)")
    
    # Test some ratings
    test_ratings = ['AAA', 'A', 'BBB', 'BB', 'D', 'NR']
    print(f"\n🧪 Test Conversions:")
    for rating in test_ratings:
        numeric = mapping.get_numeric_rating(rating)
        risk_score = mapping.calculate_risk_score(rating)
        category = mapping.get_risk_category(rating)
        print(f"  {rating} → {numeric} (Risk: {risk_score:.3f}, Category: {category})")