#!/usr/bin/env python3
"""
Credit Rating Preprocessing Demo
===============================

Demonstrates the Option A + Meta Flag preprocessing approach
with monthly data to show the 30-day consecutive NR rule in action.

Author: Korean Airlines Credit Rating Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.credit_rating_preprocessor import CreditRatingPreprocessor, PreprocessingConfig

def create_monthly_demo_data():
    """Create monthly demo data to show 30-day consecutive NR rule"""
    
    # Create monthly data for 2024-2025
    dates = pd.date_range('2024-01-01', '2025-12-31', freq='ME')
    
    # Demo scenario: TwayAir has NR from 2024-06 to 2024-12 (7 months = 210+ days)
    # This should trigger the 30-day consecutive NR rule
    demo_data = []
    
    for date in dates:
        year = date.year
        month = date.month
        
        # KoreanAir: Stable A- rating
        demo_data.append({
            'Year': f"{year}-{month:02d}",
            'KoreanAir': 'A-',
            'AsianaAirlines': 'BBB-',
            'JejuAir': 'BBB',
            'TwayAir': 'NR' if (year == 2024 and month >= 6) and (year == 2024 and month <= 12) else 'BB-',
            'AirBusan': 'NR'
        })
    
    return pd.DataFrame(demo_data)

def demo_preprocessing():
    """Demonstrate the preprocessing functionality"""
    
    print("🚀 Credit Rating Preprocessing Demo")
    print("=" * 50)
    
    # Create demo data
    print("📊 Creating monthly demo data...")
    demo_df = create_monthly_demo_data()
    
    # Save demo data
    demo_file = "demo_monthly_ratings.csv"
    demo_df.to_csv(demo_file, index=False)
    print(f"✅ Saved demo data: {demo_file}")
    
    # Configuration for demo
    config = PreprocessingConfig(
        consecutive_nr_days=30,  # 30 days for Withdrawn event
        risk_multiplier=1.20,    # 20% risk increase for WD+NR
        alert_threshold_days=90, # 90 days for alert
        output_dir="demo_processed_data"
    )
    
    # Initialize preprocessor
    preprocessor = CreditRatingPreprocessor(config)
    
    # Run preprocessing
    print("\n🔄 Running preprocessing with Option A + Meta Flag...")
    df_processed = preprocessor.run_preprocessing(demo_file, "demo_processed_data")
    
    # Show results
    print("\n📈 Preprocessing Results:")
    print("-" * 30)
    
    # Check for Withdrawn events
    withdrawn_events = df_processed[df_processed['event'] == 'Withdrawn']
    if not withdrawn_events.empty:
        print(f"✅ Withdrawn events detected: {len(withdrawn_events)}")
        for _, event in withdrawn_events.iterrows():
            print(f"   - {event['company']} on {event['date'].strftime('%Y-%m')} "
                  f"(consecutive NR: {event['consecutive_nr_days']} days)")
    else:
        print("❌ No Withdrawn events detected")
    
    # Check for WD+NR states
    wd_nr_states = df_processed[(df_processed['state'] == 'WD') & (df_processed['nr_flag'] == 1)]
    if not wd_nr_states.empty:
        print(f"✅ WD+NR states detected: {len(wd_nr_states)}")
        companies = wd_nr_states['company'].unique()
        for company in companies:
            company_data = wd_nr_states[wd_nr_states['company'] == company]
            max_days = company_data['consecutive_nr_days'].max()
            print(f"   - {company}: max consecutive NR days = {max_days}")
    else:
        print("❌ No WD+NR states detected")
    
    # Show risk score adjustments
    print("\n💰 Risk Score Analysis:")
    print("-" * 30)
    
    # Check for risk adjustments
    adjusted_risks = df_processed[df_processed['risk_score'] != df_processed['base_risk']]
    if not adjusted_risks.empty:
        print(f"✅ Risk adjustments applied: {len(adjusted_risks)} records")
        for _, risk in adjusted_risks.head(5).iterrows():
            adjustment_factor = risk['risk_score'] / risk['base_risk']
            print(f"   - {risk['company']} ({risk['date'].strftime('%Y-%m')}): "
                  f"base={risk['base_risk']:.4f}, adjusted={risk['risk_score']:.4f} "
                  f"(x{adjustment_factor:.2f})")
    else:
        print("❌ No risk adjustments applied")
    
    # Show NR reasons
    print("\n🏷️ NR Reason Analysis:")
    print("-" * 30)
    
    nr_reasons = df_processed[df_processed['nr_reason'].notna() & (df_processed['nr_reason'] != '')]
    if not nr_reasons.empty:
        reason_counts = nr_reasons['nr_reason'].value_counts()
        for reason, count in reason_counts.items():
            print(f"   - {reason}: {count} records")
    else:
        print("❌ No NR reasons tagged")
    
    # Check for alert conditions
    print("\n🚨 Alert Conditions:")
    print("-" * 30)
    
    alerts = preprocessor.detect_alert_conditions(df_processed)
    if alerts:
        print(f"✅ Alert conditions detected: {len(alerts)}")
        for alert in alerts:
            print(f"   - {alert['company']}: {alert['message']}")
    else:
        print("❌ No alert conditions detected")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print(f"📁 Check 'demo_processed_data' directory for output files")

def demo_risk_scoring():
    """Demonstrate risk scoring with nr_flag"""
    
    print("\n🔍 Risk Scoring Demo with NR Flag")
    print("=" * 50)
    
    # Create sample firm profiles with different NR scenarios
    from src.models.rating_risk_scorer import FirmProfile
    
    # Scenario 1: Normal rated company
    normal_firm = FirmProfile(
        company_name="KoreanAir",
        current_rating="A-",
        debt_to_assets=0.6,
        current_ratio=1.2,
        roa=0.05,
        roe=0.12,
        operating_margin=0.08,
        equity_ratio=0.4,
        asset_turnover=0.8,
        interest_coverage=3.5,
        quick_ratio=0.9,
        working_capital_ratio=0.15,
        nr_flag=0,
        state="A-",
        consecutive_nr_days=0
    )
    
    # Scenario 2: WD+NR company
    wd_nr_firm = FirmProfile(
        company_name="TwayAir",
        current_rating="NR",
        debt_to_assets=0.7,
        current_ratio=0.8,
        roa=0.02,
        roe=0.06,
        operating_margin=0.03,
        equity_ratio=0.3,
        asset_turnover=0.6,
        interest_coverage=1.8,
        quick_ratio=0.6,
        working_capital_ratio=0.05,
        nr_flag=1,
        state="WD",
        consecutive_nr_days=90
    )
    
    # Scenario 3: Long-term NR company
    long_nr_firm = FirmProfile(
        company_name="AirBusan",
        current_rating="NR",
        debt_to_assets=0.8,
        current_ratio=0.7,
        roa=0.01,
        roe=0.03,
        operating_margin=0.01,
        equity_ratio=0.2,
        asset_turnover=0.5,
        interest_coverage=1.2,
        quick_ratio=0.4,
        working_capital_ratio=0.02,
        nr_flag=1,
        state="NR",
        consecutive_nr_days=365
    )
    
    firms = [normal_firm, wd_nr_firm, long_nr_firm]
    
    print("📊 Risk Scoring Results:")
    print("-" * 30)
    
    for firm in firms:
        print(f"\n🏢 {firm.company_name}:")
        print(f"   Rating: {firm.current_rating}")
        print(f"   State: {firm.state}")
        print(f"   NR Flag: {firm.nr_flag}")
        print(f"   Consecutive NR Days: {firm.consecutive_nr_days}")
        
        # Simulate risk scoring (without actual model)
        base_risk = 0.1  # Simulated base risk
        
        if firm.state == 'WD' and firm.nr_flag == 1:
            adjusted_risk = base_risk * 1.20
            print(f"   ⚠️ WD+NR adjustment applied (x1.20)")
            print(f"   📊 Risk: {base_risk:.4f} → {adjusted_risk:.4f}")
        elif firm.nr_flag == 1 and firm.consecutive_nr_days >= 30:
            days_factor = min(1.5, 1.0 + (firm.consecutive_nr_days - 30) / 365 * 0.5)
            adjusted_risk = base_risk * days_factor
            print(f"   ⚠️ Long-term NR adjustment applied (x{days_factor:.2f})")
            print(f"   📊 Risk: {base_risk:.4f} → {adjusted_risk:.4f}")
        else:
            print(f"   📊 Risk: {base_risk:.4f} (no adjustment)")

if __name__ == "__main__":
    # Run preprocessing demo
    demo_preprocessing()
    
    # Run risk scoring demo
    demo_risk_scoring() 