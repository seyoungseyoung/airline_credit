# Credit Rating Preprocessing Guide
## Option A + Meta Flag Approach

### Overview

This guide explains the credit rating preprocessing system that implements **Option A + Meta Flag** approach for handling Not Rated (NR) states in credit rating analysis.

### Key Features

#### 🎯 Option A Approach
- **NR → WD (Withdrawn)**: Converts NR states to WD states for modeling
- **4-State Model**: Maintains existing 4-state structure (AAA-CCC, D, WD)
- **Minimal Changes**: No major modifications to existing models/dashboards

#### 🏷️ Meta Flag System
- **nr_flag**: Binary flag (1 for NR, 0 for rated)
- **consecutive_nr_days**: Tracks consecutive NR days
- **nr_reason**: Tags NR causes (never_rated, voluntary_withdrawal, info_deficiency)

#### ⚡ Risk Scoring Enhancements
- **WD+NR Adjustment**: 20% risk multiplier for WD+NR state
- **Long-term NR**: Graduated risk adjustment for extended NR periods
- **Alert System**: 90-day threshold for Slack notifications

### Architecture

```
Input Data (CSV)
       ↓
CreditRatingPreprocessor
       ↓
Option A Processing
├── NR → WD conversion
├── 30-day consecutive rule
├── Meta flag generation
└── Risk score calculation
       ↓
Output Files
├── TransitionHistory.csv
├── RatingMapping.csv
├── processed_data_summary.csv
└── alerts.csv (if applicable)
```

### Configuration

```python
from credit_rating_preprocessor import PreprocessingConfig, CreditRatingPreprocessor

config = PreprocessingConfig(
    consecutive_nr_days=30,      # Minimum days for Withdrawn event
    risk_multiplier=1.20,        # Risk multiplier for WD+NR
    alert_threshold_days=90,     # Days for Slack alert
    output_dir="processed_data"
)

preprocessor = CreditRatingPreprocessor(config)
```

### Usage Examples

#### Basic Preprocessing
```python
# Run complete preprocessing pipeline
df_processed = preprocessor.run_preprocessing(
    input_file="Airline_Credit_Ratings_2010-2025__NR___Not_Rated_.csv"
)
```

#### Integration with Pipeline
```python
from korean_airlines_data_pipeline import DataPipeline

pipeline = DataPipeline()
df_processed = pipeline.preprocess_credit_ratings(
    input_file="credit_ratings.csv",
    output_dir="processed_data"
)
```

#### Risk Scoring with NR Flag
```python
from rating_risk_scorer import FirmProfile, RatingRiskScorer

# Create firm profile with NR meta data
firm = FirmProfile(
    company_name="TwayAir",
    current_rating="NR",
    # ... financial ratios ...
    nr_flag=1,
    state="WD",
    consecutive_nr_days=90
)

# Score with NR adjustments
scorer = RatingRiskScorer()
assessment = scorer.score_firm(firm)
```

### Processing Rules

#### 1. 30-Day Consecutive NR Rule
- Only marks as "Withdrawn" if NR persists for ≥30 consecutive days
- Filters out temporary data gaps/delays
- Prevents false positive Withdrawn events

#### 2. NR Reason Tagging
```python
nr_reasons = {
    'never_rated': 'Company never had a rating',
    'voluntary_withdrawal': 'Company withdrew from rating',
    'info_deficiency': 'Insufficient information for rating'
}
```

#### 3. Risk Score Adjustments
```python
# WD+NR state: 20% risk increase
if state == 'WD' and nr_flag == 1:
    risk_score *= 1.20

# Long-term NR: Graduated adjustment
if nr_flag == 1 and consecutive_nr_days >= 30:
    days_factor = min(1.5, 1.0 + (days - 30) / 365 * 0.5)
    risk_score *= days_factor
```

### Output Files

#### TransitionHistory.csv
```csv
Id,company,date,state,event,nr_flag
1,TwayAir,2024-06-01,WD,Withdrawn,1
2,TwayAir,2024-07-01,WD,,1
```

#### processed_data_summary.csv
```csv
Year,company,rating,date,state,nr_flag,consecutive_nr_days,nr_reason,risk_score
2024-06,TwayAir,NR,2024-06-01,WD,1,30,voluntary_withdrawal,0.052
```

### Alert System

#### 90-Day Alert Threshold
- Detects WD+NR states lasting >90 days
- Generates Slack notifications
- Message: "Unrated > 90d — 자본시장 접근 제약 우려"

#### Alert Configuration
```python
alerts = preprocessor.detect_alert_conditions(df_processed)
for alert in alerts:
    print(f"{alert['company']}: {alert['message']}")
```

### Benefits

#### ✅ Data Volume Preservation
- Maintains sufficient event counts for parameter estimation
- Avoids splitting events into smaller categories
- Preserves statistical power

#### ✅ Industry Standard Compliance
- Aligns with domestic credit rating agency practices
- NR ≈ Withdrawn in practical applications
- Consistent with regulatory reporting

#### ✅ System Stability
- Minimal changes to existing models
- No major dashboard modifications required
- Backward compatibility maintained

#### ✅ Enhanced Risk Assessment
- Granular NR state tracking
- Graduated risk adjustments
- Real-time alert capabilities

### Migration Guide

#### From Traditional Approach
1. **Install**: Add `credit_rating_preprocessor.py`
2. **Configure**: Set up `PreprocessingConfig`
3. **Integrate**: Add to existing pipeline
4. **Test**: Run with sample data
5. **Deploy**: Update production systems

#### Backward Compatibility
- Existing 4-state models continue to work
- No changes to `enhanced_multistate_model.py`
- Dashboard displays remain unchanged
- Risk scoring enhanced, not replaced

### Future Enhancements

#### Global Expansion
- Support for S&P WR vs NR distinction
- 5-state model capability
- International rating agency compatibility

#### Advanced Analytics
- NR duration analysis
- Withdrawal pattern recognition
- Predictive NR modeling

#### Real-time Processing
- Daily data collection (vs current 30-day)
- Live alert system
- Automated risk adjustments

### Troubleshooting

#### Common Issues

**No Withdrawn Events Detected**
- Check consecutive_nr_days threshold
- Verify date format in input data
- Ensure sufficient NR periods

**Risk Adjustments Not Applied**
- Confirm nr_flag values
- Check state column values
- Verify risk multiplier configuration

**Alert System Not Triggering**
- Check alert_threshold_days setting
- Verify WD+NR state detection
- Confirm consecutive day calculation

#### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run preprocessing with detailed logging
df_processed = preprocessor.run_preprocessing(input_file)
```

### Performance Considerations

#### Data Volume
- Handles 1000+ companies efficiently
- Processes 15+ years of historical data
- Supports monthly/quarterly frequencies

#### Memory Usage
- Optimized for large datasets
- Streaming processing for big files
- Configurable cache settings

#### Processing Speed
- Fast preprocessing (<1 minute for typical datasets)
- Parallel processing capabilities
- Incremental updates supported

### Best Practices

#### Data Quality
- Validate input data formats
- Check for missing values
- Verify date consistency

#### Configuration
- Set appropriate thresholds
- Test with sample data
- Document custom settings

#### Monitoring
- Track processing logs
- Monitor alert frequencies
- Validate output quality

#### Maintenance
- Regular threshold reviews
- Update rating mappings
- Refresh alert rules

---

*This guide covers the complete credit rating preprocessing system. For specific implementation details, refer to the source code and API documentation.* 