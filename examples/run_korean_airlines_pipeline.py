#!/usr/bin/env python3
"""
Korean Airlines Data Pipeline - Demo Runner
==========================================

This script demonstrates how to run the data pipeline for Korean airline companies.

Usage:
1. Get DART API key from https://opendart.fss.or.kr/
2. Set environment variable: DART_API_KEY=your_api_key
3. Run: python run_korean_airlines_pipeline.py

For now, it runs with sample data for demonstration.
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)

def main():
    """Run the Korean Airlines credit rating data pipeline"""
    
    print("🏢 Korean Airlines Credit Rating Data Pipeline")
    print("=" * 50)
    
    # Check if pipeline module exists
    try:
        from korean_airlines_data_pipeline import DataPipeline, AIRLINE_COMPANIES
    except ImportError:
        print("❌ Error: korean_airlines_data_pipeline.py not found")
        print("Please ensure the pipeline script is in the same directory")
        return 1
    
    # Display target companies
    print("\n📋 Target Companies:")
    for i, company in enumerate(AIRLINE_COMPANIES, 1):
        print(f"  {i}. {company.name_kr} ({company.name})")
        print(f"     Stock Code: {company.stock_code} ({company.market})")
    
    # Check for DART API key
    dart_api_key = os.getenv('DART_API_KEY')
    if dart_api_key:
        print(f"\n🔑 DART API Key: {'*' * 10}{dart_api_key[-4:]}")
        print("✅ Will collect real financial data from DART API")
    else:
        print("\n⚠️  DART API Key not found in environment variables")
        print("📝 To get real financial data:")
        print("   1. Register at: https://opendart.fss.or.kr/")
        print("   2. Get your API key")
        print("   3. Set environment variable: DART_API_KEY=your_key")
        print("   4. Re-run this script")
        print("\n🔄 Running with sample data for now...")
    
    # Initialize and run pipeline
    try:
        print("\n🚀 Initializing pipeline...")
        pipeline = DataPipeline(dart_api_key)
        
        print("▶️  Running pipeline...")
        transition_file, mapping_file = pipeline.run_pipeline(
            dart_api_key=dart_api_key,
            use_sample_ratings=True  # Change to False when you have real rating data
        )
        
        print("\n✅ Pipeline completed successfully!")
        print(f"📄 Output files created:")
        print(f"   • {transition_file}")
        print(f"   • {mapping_file}")
        
        # Display sample of results
        import pandas as pd
        
        print(f"\n📊 Sample of TransitionHistory.csv:")
        df = pd.read_csv(transition_file)
        print(df.head(10).to_string(index=False))
        
        print(f"\n📈 Rating distribution:")
        rating_counts = df['RatingSymbol'].value_counts()
        for rating, count in rating_counts.items():
            print(f"   {rating}: {count} records")
        
        print(f"\n🏢 Company distribution:")
        company_counts = df['Id'].value_counts()
        for company_id, count in company_counts.items():
            company_name = next(c.name for c in AIRLINE_COMPANIES if c.issuer_id == company_id)
            print(f"   {company_name}: {count} records")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        logging.error(f"Pipeline error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 