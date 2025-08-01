#!/usr/bin/env python3
"""
Credit Rating Data Preprocessor
==============================

Preprocesses credit rating data with Option A + Meta Flag approach:
- NR (Not Rated) → WD (Withdrawn) state
- Adds nr_flag meta flag for risk scoring
- Implements 30-day consecutive NR rule for Withdrawn events
- Adds reason tagging for NR causes

Author: Korean Airlines Credit Rating Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import os
import sys
from dataclasses import dataclass

# Add config path
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
sys.path.insert(0, config_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PreprocessingConfig:
    """Configuration for credit rating preprocessing"""
    consecutive_nr_days: int = 30  # Minimum consecutive NR days for Withdrawn event
    risk_multiplier: float = 1.20  # Risk multiplier for WD+NR state
    alert_threshold_days: int = 90  # Days for Slack alert threshold
    output_dir: str = "processed_data"
    backup_original: bool = True

class CreditRatingPreprocessor:
    """Credit rating data preprocessor with Option A + Meta Flag approach"""
    
    def __init__(self, config: PreprocessingConfig = None):
        self.config = config or PreprocessingConfig()
        self.rating_mapping = self._load_rating_mapping()
        
    def _load_rating_mapping(self) -> Dict[str, int]:
        """Load rating to numeric mapping"""
        # Standard S&P/Fitch rating scale
        rating_scale = {
            'AAA': 1, 'AA+': 2, 'AA': 3, 'AA-': 4,
            'A+': 5, 'A': 6, 'A-': 7,
            'BBB+': 8, 'BBB': 9, 'BBB-': 10,
            'BB+': 11, 'BB': 12, 'BB-': 13,
            'B+': 14, 'B': 15, 'B-': 16,
            'CCC+': 17, 'CCC': 18, 'CCC-': 19,
            'CC': 20, 'C': 21, 'D': 22,
            'NR': 23, 'WD': 23  # NR and WD mapped to same numeric value
        }
        return rating_scale
    
    def load_credit_ratings(self, file_path: str) -> pd.DataFrame:
        """Load credit rating data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded credit rating data: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading credit rating data: {e}")
            raise
    
    def reshape_to_long_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reshape wide format (companies as columns) to long format"""
        # Melt the dataframe to long format
        df_long = df.melt(
            id_vars=['Year'], 
            var_name='company', 
            value_name='rating'
        )
        
        # Convert Year to datetime - handle both YYYY and YYYY-MM formats
        try:
            df_long['date'] = pd.to_datetime(df_long['Year'], format='%Y-%m', errors='coerce')
        except:
            df_long['date'] = pd.to_datetime(df_long['Year'], format='%Y', errors='coerce')
        
        # Sort by company and date
        df_long = df_long.sort_values(['company', 'date']).reset_index(drop=True)
        
        logger.info(f"Reshaped to long format: {df_long.shape}")
        return df_long
    
    def apply_option_a_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Option A preprocessing: NR → WD with meta flags"""
        
        # Create a copy to avoid modifying original
        df_processed = df.copy()
        
        # Forward fill ratings to identify new NR occurrences
        df_processed['rating_ffill'] = df_processed.groupby('company')['rating'].ffill()
        
        # Identify new NR occurrences (where current is NR but previous was not)
        mask_new_nr = (
            df_processed['rating'].isna() & 
            df_processed['rating_ffill'].notna()
        )
        
        # Mark Withdrawn events for new NR occurrences
        df_processed['event'] = ''
        df_processed.loc[mask_new_nr, 'event'] = 'Withdrawn'
        
        # Apply 30-day consecutive NR rule
        df_processed = self._apply_consecutive_nr_rule(df_processed)
        
        # Create state column: NR → WD, others remain same
        df_processed['state'] = np.where(
            df_processed['rating'].isna(), 
            'WD', 
            df_processed['rating']
        )
        
        # Add nr_flag meta flag (1 for NR, 0 for rated)
        df_processed['nr_flag'] = df_processed['rating'].isna().astype(int)
        
        # Add reason tagging for NR causes
        df_processed['nr_reason'] = self._tag_nr_reasons(df_processed)
        
        # Add numeric rating for modeling
        df_processed['rating_numeric'] = df_processed['state'].map(self.rating_mapping)
        
        logger.info("Applied Option A preprocessing with meta flags")
        return df_processed
    
    def _apply_consecutive_nr_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply 30-day consecutive NR rule for Withdrawn events"""
        
        # Group by company and calculate consecutive NR days
        df_processed = df.copy()
        
        # Create date sequence for each company
        df_processed['date'] = pd.to_datetime(df_processed['date'])
        
        # Calculate consecutive NR days
        df_processed['consecutive_nr_days'] = 0
        
        for company in df_processed['company'].unique():
            company_mask = df_processed['company'] == company
            company_data = df_processed[company_mask].copy()
            
            # Calculate consecutive NR days
            nr_mask = company_data['rating'].isna()
            consecutive_days = 0
            
            for idx in company_data.index:
                if nr_mask.loc[idx]:
                    consecutive_days += 1
                else:
                    consecutive_days = 0
                
                df_processed.loc[idx, 'consecutive_nr_days'] = consecutive_days
            
            # Only mark as Withdrawn if consecutive NR days >= threshold
            withdrawn_mask = (
                company_mask & 
                (df_processed['consecutive_nr_days'] >= self.config.consecutive_nr_days) &
                (df_processed['event'] == 'Withdrawn')
            )
            
            # Reset event for those below threshold
            below_threshold_mask = (
                company_mask & 
                (df_processed['consecutive_nr_days'] < self.config.consecutive_nr_days) &
                (df_processed['event'] == 'Withdrawn')
            )
            df_processed.loc[below_threshold_mask, 'event'] = ''
        
        logger.info(f"Applied {self.config.consecutive_nr_days}-day consecutive NR rule")
        return df_processed
    
    def _tag_nr_reasons(self, df: pd.DataFrame) -> pd.Series:
        """Tag NR reasons based on patterns"""
        reasons = []
        
        for idx, row in df.iterrows():
            if pd.isna(row['rating']):
                # Determine reason based on context
                if idx == 0 or pd.isna(df.loc[idx-1, 'rating']):
                    reasons.append('never_rated')
                elif row['consecutive_nr_days'] >= self.config.consecutive_nr_days:
                    reasons.append('voluntary_withdrawal')
                else:
                    reasons.append('info_deficiency')
            else:
                reasons.append('')
        
        return pd.Series(reasons, index=df.index)
    
    def calculate_risk_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate risk scores with WD+NR adjustment"""
        df_scored = df.copy()
        
        # Find max rating number for normalization
        max_rating_numeric = df_scored['rating_numeric'].max()
        if pd.isna(max_rating_numeric):
            max_rating_numeric = 22  # Default max rating
        
        # Base risk score (higher number = higher risk, intuitive direction)
        df_scored['base_risk'] = df_scored['rating_numeric'] / max_rating_numeric
        
        # Apply WD+NR risk multiplier
        wd_nr_mask = (df_scored['state'] == 'WD') & (df_scored['nr_flag'] == 1)
        df_scored.loc[wd_nr_mask, 'risk_score'] = (
            df_scored.loc[wd_nr_mask, 'base_risk'] * self.config.risk_multiplier
        )
        
        # Regular risk score for others
        regular_mask = ~wd_nr_mask
        df_scored.loc[regular_mask, 'risk_score'] = df_scored.loc[regular_mask, 'base_risk']
        
        logger.info("Calculated risk scores with WD+NR adjustment (corrected direction: higher number = higher risk)")
        return df_scored
    
    def detect_alert_conditions(self, df: pd.DataFrame) -> List[Dict]:
        """Detect conditions for Slack alerts"""
        alerts = []
        
        for company in df['company'].unique():
            company_data = df[df['company'] == company]
            
            # Check for WD+NR state lasting more than alert threshold
            wd_nr_mask = (company_data['state'] == 'WD') & (company_data['nr_flag'] == 1)
            wd_nr_days = company_data[wd_nr_mask]['consecutive_nr_days'].max()
            
            if wd_nr_days >= self.config.alert_threshold_days:
                latest_date = company_data[wd_nr_mask]['date'].max()
                alerts.append({
                    'company': company,
                    'alert_type': 'Unrated > 90d',
                    'message': f"Unrated > {self.config.alert_threshold_days}d — 자본시장 접근 제약 우려",
                    'date': latest_date,
                    'consecutive_days': wd_nr_days
                })
        
        return alerts
    
    def create_output_files(self, df: pd.DataFrame, output_dir: str = None) -> Dict[str, str]:
        """Create output files for the pipeline"""
        output_dir = output_dir or self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create TransitionHistory.csv
        transition_history = df[['company', 'date', 'state', 'event', 'nr_flag']].copy()
        transition_history['Id'] = range(1, len(transition_history) + 1)
        transition_history = transition_history[['Id', 'company', 'date', 'state', 'event', 'nr_flag']]
        
        transition_file = os.path.join(output_dir, 'TransitionHistory.csv')
        transition_history.to_csv(transition_file, index=False)
        
        # Create RatingMapping.csv
        rating_mapping_df = pd.DataFrame([
            {'RatingSymbol': symbol, 'RatingNumber': number}
            for symbol, number in self.rating_mapping.items()
        ])
        
        mapping_file = os.path.join(output_dir, 'RatingMapping.csv')
        rating_mapping_df.to_csv(mapping_file, index=False)
        
        # Create processed data summary
        summary_file = os.path.join(output_dir, 'processed_data_summary.csv')
        df.to_csv(summary_file, index=False)
        
        # Create alerts file
        alerts = self.detect_alert_conditions(df)
        if alerts:
            alerts_df = pd.DataFrame(alerts)
            alerts_file = os.path.join(output_dir, 'alerts.csv')
            alerts_df.to_csv(alerts_file, index=False)
        
        logger.info(f"Created output files in {output_dir}")
        return {
            'transition_history': transition_file,
            'rating_mapping': mapping_file,
            'summary': summary_file,
            'alerts': os.path.join(output_dir, 'alerts.csv') if alerts else None
        }
    
    def run_preprocessing(self, input_file: str, output_dir: str = None) -> pd.DataFrame:
        """Run complete preprocessing pipeline"""
        logger.info("Starting credit rating preprocessing pipeline")
        
        # Load data
        df = self.load_credit_ratings(input_file)
        
        # Reshape to long format
        df_long = self.reshape_to_long_format(df)
        
        # Apply Option A preprocessing
        df_processed = self.apply_option_a_preprocessing(df_long)
        
        # Calculate risk scores
        df_scored = self.calculate_risk_scores(df_processed)
        
        # Create output files
        output_files = self.create_output_files(df_scored, output_dir)
        
        # Print summary statistics
        self._print_summary_statistics(df_scored)
        
        logger.info("Credit rating preprocessing pipeline completed")
        return df_scored
    
    def _print_summary_statistics(self, df: pd.DataFrame):
        """Print summary statistics of processed data"""
        print("\n" + "="*60)
        print("CREDIT RATING PREPROCESSING SUMMARY")
        print("="*60)
        
        print(f"Total records: {len(df)}")
        print(f"Companies: {df['company'].nunique()}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        print(f"\nState distribution:")
        state_counts = df['state'].value_counts()
        for state, count in state_counts.items():
            print(f"  {state}: {count}")
        
        print(f"\nEvent distribution:")
        event_counts = df['event'].value_counts()
        for event, count in event_counts.items():
            if event:  # Skip empty events
                print(f"  {event}: {count}")
        
        print(f"\nNR reasons:")
        reason_counts = df['nr_reason'].value_counts()
        for reason, count in reason_counts.items():
            if reason:  # Skip empty reasons
                print(f"  {reason}: {count}")
        
        # Check for alert conditions
        alerts = self.detect_alert_conditions(df)
        if alerts:
            print(f"\nAlert conditions detected: {len(alerts)}")
            for alert in alerts:
                print(f"  {alert['company']}: {alert['message']}")
        
        print("="*60)

def main():
    """Main function to run preprocessing"""
    # Configuration
    config = PreprocessingConfig(
        consecutive_nr_days=30,
        risk_multiplier=1.20,
        alert_threshold_days=90,
        output_dir="processed_data"
    )
    
    # Initialize preprocessor
    preprocessor = CreditRatingPreprocessor(config)
    
    # Run preprocessing
    input_file = "Airline_Credit_Ratings_2010-2025__NR___Not_Rated_.csv"
    
    try:
        df_processed = preprocessor.run_preprocessing(input_file)
        print(f"\n✅ Preprocessing completed successfully!")
        print(f"📊 Processed {len(df_processed)} records")
        print(f"📁 Output files created in: {config.output_dir}")
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise

if __name__ == "__main__":
    main() 