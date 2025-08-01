# Korean Airlines Credit Rating Data Pipeline

## 🎯 Overview

This pipeline collects and processes credit rating transition data for major Korean airline companies:

- **대한항공** (Korean Air) - KOSPI: 003490
- **아시아나항공** (Asiana Airlines) - KOSPI: 020560  
- **제주항공** (Jeju Air) - KOSDAQ: 089590
- **티웨이항공** (T'way Air) - KOSDAQ: 091810

## 📊 Data Sources

### 1. DART API (Financial Data)
- **Source**: [DART Open API](https://opendart.fss.or.kr/)
- **Period**: 2010Q1 ~ 2025Q2
- **Data**: Quarterly financial statements
- **Output**: 20 key financial ratios per company per quarter

### 2. Credit Rating Agencies (Rating History) 
- **NICE신용평가** (NICE Credit Rating)
- **한국신용평가** (KIS Credit Rating)
- **Data**: effective_date, rating transitions
- **Format**: Standardized rating scale (AAA to D, NR)

## 🏗️ Pipeline Architecture

```
Data Collection → Processing → Normalization → Output
     ↓               ↓            ↓           ↓
  DART API       Financial     CSV Format   Required
  Rating APIs    Ratios        Mapping      Files
```

## 📁 Output Files

### TransitionHistory.csv
```csv
Id,Date,RatingSymbol
1,31-Dec-10,BBB
1,30-Jun-11,BBB
1,31-Dec-11,BB
...
```

### RatingMapping.csv
```csv
RatingSymbol,RatingNumber
AAA,0
AA,1
A,2
BBB,3
BB,4
B,5
CCC,6
D,7
NR,8
```

## 🚀 Quick Start

### Prerequisites
```bash
# Activate conda environment
conda activate credit_rating_transition

# Install additional dependencies (if needed)
pip install requests beautifulsoup4 lxml python-dotenv tqdm
```

### Basic Usage
```bash
# Run with sample data (no API key needed)
python run_korean_airlines_pipeline.py
```

### With DART API (Real Data)
```bash
# 1. Get DART API key from https://opendart.fss.or.kr/
# 2. Set environment variable
export DART_API_KEY=your_api_key_here

# 3. Run pipeline
python run_korean_airlines_pipeline.py
```

## 📈 Current Status

### ✅ Completed Features

1. **Target Company Definition**
   - [x] 4 major Korean airlines identified
   - [x] Stock codes and market classification
   - [x] Issuer ID mapping for transition matrix

2. **DART Scraper Framework** 
   - [x] DART Open API integration
   - [x] Quarterly financial statement collection
   - [x] 20 financial ratios calculation
   - [x] Error handling and rate limiting

3. **Data Format Compliance**
   - [x] TransitionHistory.csv format matching original repo
   - [x] RatingMapping.csv with standard rating scale
   - [x] CSV normalization and validation

4. **Sample Data Generation**
   - [x] Realistic rating progression for each airline
   - [x] Time-series format (2010-2024)
   - [x] Rating transitions reflecting industry events

### 🔄 Next Steps (Manual Data Collection Required)

1. **NICE Credit Rating Collection**
   - [ ] Manual collection from NICE disclosure reports
   - [ ] Parsing of PDF/HTML rating announcements
   - [ ] Date and rating extraction

2. **KIS Credit Rating Collection** 
   - [ ] Manual collection from KIS disclosure reports
   - [ ] Cross-validation with NICE ratings
   - [ ] Handling of rating disagreements

3. **Data Quality Validation**
   - [ ] Rating consistency checks
   - [ ] Missing data interpolation strategy
   - [ ] Outlier detection and handling

## 💰 Financial Ratios Calculated

The pipeline calculates 20 key financial ratios:

### Liquidity Ratios
- Current Ratio
- Quick Ratio  
- Working Capital Ratio

### Leverage Ratios
- Debt-to-Assets
- Debt-to-Equity
- Equity Ratio
- Interest Coverage

### Profitability Ratios
- ROA (Return on Assets)
- ROE (Return on Equity)
- Operating Margin
- Net Margin

### Efficiency Ratios
- Asset Turnover
- Cash Flow to Assets
- Operating CF Ratio

### Airline-Specific Ratios
- Cash Flow Coverage
- Debt Service Coverage
- Times Interest Earned

## 🔧 Configuration

### Environment Variables
```bash
# Required for real financial data
DART_API_KEY=your_dart_api_key

# Optional configurations
PIPELINE_LOG_LEVEL=INFO
OUTPUT_DIRECTORY=./output
```

### Pipeline Settings
```python
# In korean_airlines_data_pipeline.py
START_YEAR = 2010
END_YEAR = 2025
USE_SAMPLE_RATINGS = True  # Set to False for real rating data
```

## 📊 Data Quality Considerations

### Risks & Mitigation
1. **DART API Rate Limits**
   - ✅ Built-in rate limiting (0.1s between requests)
   - ✅ Retry logic for failed requests

2. **Missing Financial Data**
   - ✅ Graceful handling of missing quarters
   - ✅ Zero-filling for unavailable ratios

3. **Rating Data Quality** ⚠️ **Highest Risk**
   - ❌ Manual data collection required
   - ❌ Potential inconsistencies between agencies
   - ✅ Standardized rating scale mapping

### Data Validation
- Financial ratios sanity checks
- Rating progression logical validation  
- Time series continuity verification

## 🛠️ Extending the Pipeline

### Adding New Airlines
```python
# In korean_airlines_data_pipeline.py
AIRLINE_COMPANIES.append(
    AirlineCompany("New Airline", "새로운항공", "123456", "KOSDAQ", "", 5)
)
```

### Adding New Financial Ratios
```python
# In calculate_financial_ratios method
ratios['new_ratio'] = calculation_logic
```

### Real Rating Data Integration
```python
# Replace sample data in collect_rating_data method
def collect_rating_data(self, use_sample: bool = False):
    if not use_sample:
        # Implement real rating collection logic
        return self.scrape_nice_ratings() + self.scrape_kis_ratings()
```

## 📞 Support & Next Steps

For the PoC phase:
1. **Current implementation** handles the DART API integration (automated)
2. **Manual rating collection** needed for 4 companies (1 day effort as noted)
3. **Data quality validation** before running transition matrix analysis

The pipeline is ready for production use once real rating data is collected and integrated. 