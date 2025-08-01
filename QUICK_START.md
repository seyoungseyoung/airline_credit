# 🚀 Quick Start Guide

## 📋 Prerequisites

```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r config/requirements_pipeline.txt
```

## ⚡ Quick Commands

### 1. 🔧 Credit Rating Preprocessing
```bash
# Run preprocessing with Option A + Meta Flag approach
python run_preprocessing.py
```

### 2. 📊 Launch Dashboard
```bash
# Start interactive Streamlit dashboard
python run_dashboard.py

# Access at: http://localhost:8502
```

### 3. 🚀 Complete Pipeline
```bash
# Run full data pipeline with preprocessing
python run_pipeline.py
```

### 4. 🧪 Run Examples
```bash
# Demo preprocessing with monthly data
python examples/demo_preprocessing.py

# Slack alert system demo
python examples/slack_alert_demo.py
```

## 📁 Project Structure

```
korean-airlines-credit-rating/
├── 🚀 run_*.py               # Quick launch scripts
├── 📁 src/                   # Source code
│   ├── core/                 # Preprocessing engine
│   ├── data/                 # Data pipeline
│   ├── models/               # ML models
│   ├── dashboard/            # Web interface
│   └── utils/                # Utilities
├── 📚 docs/                  # Documentation
├── 📋 examples/              # Example scripts
├── 🧪 tests/                 # Test files
├── 📦 data/                  # Data storage
│   ├── raw/                  # Raw data
│   └── processed/            # Processed outputs
└── ⚙️ config/                # Configuration
```

## 🎯 Key Features

### Option A + Meta Flag Preprocessing
- **NR → WD conversion** with 4-state model preservation
- **30-day consecutive rule** for Withdrawn events
- **Meta flags**: nr_flag, consecutive_nr_days, nr_reason
- **Risk adjustments**: 20% multiplier for WD+NR states

### Real-time Dashboard
- Interactive visualizations with Plotly
- 90-day risk probability tracking
- Configurable Slack notifications
- CSV export for Excel integration

### Advanced ML Models
- Multi-state hazard modeling
- Cox proportional hazards
- Financial ratio integration (20+ metrics)
- Backtesting framework

## 🔧 Configuration

### Environment Setup
```bash
# Copy template
cp config/env_example.txt .env

# Edit your API keys (optional for demo)
DART_API_KEY=your_dart_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### Data Source Toggle
```python
# config/config.py
USE_REAL_DATA = False  # True for production, False for demo
```

## 📊 Expected Output

### Preprocessing Results
```
✅ Preprocessing completed successfully!
📊 Processed 80 records
📁 Output files created in: data/processed/
```

### Output Files
- `TransitionHistory.csv` - Rating transitions with meta flags
- `RatingMapping.csv` - Rating symbol mappings
- `processed_data_summary.csv` - Complete processed dataset
- `alerts.csv` - Alert conditions (if any)

## 🎮 Usage Examples

### Basic Preprocessing
```python
from src.core import CreditRatingPreprocessor, PreprocessingConfig

config = PreprocessingConfig(consecutive_nr_days=30)
preprocessor = CreditRatingPreprocessor(config)
df = preprocessor.run_preprocessing("data/raw/ratings.csv")
```

### Risk Scoring
```python
from src.models import FirmProfile, RatingRiskScorer

firm = FirmProfile(
    company_name="TwayAir",
    current_rating="NR",
    nr_flag=1,
    state="WD",
    consecutive_nr_days=90,
    # ... financial ratios ...
)

scorer = RatingRiskScorer()
assessment = scorer.score_firm(firm, horizon=90)
```

## 🆘 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure dependencies are installed
pip install -r config/requirements_pipeline.txt
```

**Missing Data Files**
```bash
# Check if data files exist
ls data/raw/
```

**Dashboard Not Starting**
```bash
# Check if Streamlit is installed
pip install streamlit
```

## 📞 Support

- 📖 **Full Documentation**: `docs/` folder
- 🧪 **Test Examples**: `examples/` folder
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions

---

**🎉 Ready to analyze Korean Airlines credit ratings!** ✈️