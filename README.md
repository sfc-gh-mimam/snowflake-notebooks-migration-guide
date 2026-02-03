# Snowflake Notebooks Migration Guide

An enterprise-ready Streamlit application designed to help sales teams and customers migrate from deprecated warehouse-backed notebooks to compute pool-backed notebooks in Snowflake.

## Features

### Core Functionality

- **Migration Calculator**: Interactive tool to generate compute pool recommendations based on current warehouse configuration
- **Cost Comparison**: Side-by-side analysis of warehouse vs compute pool costs with savings projections
- **SQL Templates**: Production-ready SQL queries for cost monitoring, budget tracking, and usage analysis
- **Best Practices Guide**: Optimization strategies for right-sizing, timeout configuration, and cost management
- **Setup Wizard**: Step-by-step migration guide with validation checklists
- **PDF Export**: Generate downloadable PDF reports from any section

### Key Capabilities

✅ Warehouse to compute pool mapping recommendations  
✅ GPU instance family selection for ML workloads  
✅ Cost projections with customizable credit rates  
✅ Budget alert threshold calculator  
✅ User attribution and chargeback strategies  
✅ Idle pool detection queries  
✅ Configuration templates for common workload types  
✅ Scenario comparison (save and compare up to 3 configurations)  

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/sfc-gh-mimam/snowflake-notebooks-migration-guide.git
cd snowflake-notebooks-migration-guide

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/main.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Using the Make Script

```bash
# Install dependencies
./make.sh install

# Run locally
./make.sh run

# Build Docker image
./make.sh build

# Run in Docker
./make.sh run-docker

# Run tests
./make.sh test
```

## Usage

### Navigation

The application consists of 6 main sections:

1. **Landing Page**: Overview and quick navigation
2. **Why Compute Pools?**: Benefits, comparison tables, and migration urgency guide
3. **Migration Calculator**: Primary tool for generating recommendations
4. **Cost Monitoring**: SQL query library for tracking and budgeting
5. **Best Practices**: Optimization strategies and configuration templates
6. **Getting Started**: Step-by-step setup wizard

### Migration Calculator Workflow

1. Navigate to "Migration Calculator" page
2. Input your configuration:
   - Current warehouse size (XS - 6XL)
   - Workload type (SQL-heavy, ML-heavy, Balanced, Interactive)
   - Expected concurrent users
   - GPU requirement (if applicable)
   - Usage hours per day
   - Credit rate

3. Click "Calculate Recommendation"
4. Review:
   - Instance family recommendation
   - Node count guidance
   - Cost comparison charts
   - Monthly savings projection
   - Auto-suspend recommendations

5. Generate SQL:
   - Customize compute pool name
   - Download migration SQL
   - Save scenario for comparison

6. Export results as PDF

### Cost Monitoring Setup

1. Navigate to "Cost Monitoring" page
2. Review budget setup queries
3. Download SQL templates:
   - Daily credit consumption tracking
   - Budget threshold monitoring
   - User attribution queries
   - Idle pool detection
   - Weekly/hourly usage patterns

4. Customize pool names in queries
5. Use alert threshold calculator
6. Export complete monitoring guide as PDF

## Customization

### Pricing Data

The application uses placeholder pricing data. To customize for your organization:

1. **Edit warehouse specifications**:
   - File: `app/data/warehouse_specs.json`
   - Update `credits_per_hour` values based on your actual warehouse costs

2. **Edit compute pool specifications**:
   - File: `app/data/compute_pool_specs.json`
   - Update `credits_per_hour` values for each instance family

3. **Adjust credit rate**:
   - Default: $4 per credit
   - Users can customize in the calculator interface
   - Or modify default in `app/models/cost_calculator.py`

### Workload Multipliers

Adjust recommendation logic in `app/models/warehouse_mapping.py`:

```python
workload_multipliers = {
    "SQL-heavy": 0.8,     # Adjust based on your workload patterns
    "ML-heavy": 1.5,
    "Balanced": 1.0,
    "Interactive": 0.9
}
```

### Styling & Branding

Customize appearance in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#29B5E8"  # Your brand color
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F8FF"
```

Modify CSS in `app/components/styling.py` for advanced customization.

### SQL Templates

Add or modify SQL queries in `app/data/sql_templates/`:

- `cost_monitoring.sql` - Daily tracking queries
- `budget_setup.sql` - Budget configuration
- `usage_queries.sql` - Advanced analysis queries

## Architecture

### Project Structure

```
snowflake-notebooks-migration-guide/
├── .streamlit/
│   └── config.toml              # Theme configuration
├── app/
│   ├── main.py                  # Landing page
│   ├── pages/                   # Multi-page app sections
│   │   ├── 1_Why_Compute_Pools.py
│   │   ├── 2_Migration_Calculator.py
│   │   ├── 3_Cost_Monitoring.py
│   │   ├── 4_Best_Practices.py
│   │   └── 5_Getting_Started.py
│   ├── components/              # Reusable UI components
│   │   ├── styling.py           # CSS and styling utilities
│   │   ├── charts.py            # Plotly chart generators
│   │   └── pdf_export.py        # PDF generation
│   ├── models/                  # Business logic
│   │   ├── warehouse_mapping.py # Recommendation engine
│   │   └── cost_calculator.py   # Cost comparison logic
│   └── data/                    # Configuration data
│       ├── warehouse_specs.json
│       ├── compute_pool_specs.json
│       └── sql_templates/
│           ├── cost_monitoring.sql
│           ├── budget_setup.sql
│           └── usage_queries.sql
├── Dockerfile                   # Container definition
├── service-spec.yaml            # SPCS service specification
├── setup.sql                    # SPCS infrastructure setup
├── make.sh                      # Build automation
├── requirements.txt
└── README.md
```

### Key Components

**Recommendation Engine** (`warehouse_mapping.py`):
- Maps warehouse sizes to appropriate compute pool configurations
- Applies workload-specific multipliers
- Handles GPU instance selection
- Generates migration SQL

**Cost Calculator** (`cost_calculator.py`):
- Computes monthly cost projections
- Compares warehouse vs compute pool costs
- Calculates savings and ROI

**PDF Export** (`pdf_export.py`):
- Converts page content to print-friendly HTML
- Generates PDFs using WeasyPrint
- Includes disclaimers and timestamps

## Deployment

### Local Development

```bash
./make.sh run
# Access at http://localhost:8501
```

### Docker

```bash
# Build image
./make.sh build

# Run container
./make.sh run-docker
```

### Snowpark Container Services (SPCS)

For production deployment to Snowflake, see [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

Quick overview:

```bash
# Prepare for SPCS deployment
./make.sh spcs-prep

# Run setup.sql in Snowflake to create infrastructure

# Build and push to Snowflake registry
export REPO_URL='<your-snowflake-registry-url>'
./make.sh spcs-build

# Create service in Snowflake (see setup.sql)
```

### Streamlit Community Cloud

1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Deploy from `app/main.py`

## Troubleshooting

### Common Issues

**PDF Export Not Working**

WeasyPrint requires additional system libraries:

```bash
# On macOS:
brew install cairo pango gdk-pixbuf libffi

# On Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

**Port Already in Use**

```bash
streamlit run app/main.py --server.port=8502
```

**Import Errors**

```bash
# Ensure you're in the correct directory
cd snowflake-notebooks-migration-guide
python -c "import sys; sys.path.append('app'); from models import recommend_compute_pool"
```

## Disclaimers

⚠️ **Important Notes**:
- Cost estimates are based on placeholder credit rates
- Always validate pricing with your Snowflake account team
- SQL queries should be tested in non-production environments first
- Compute pool configurations may need adjustment based on actual usage

## Documentation

- **README.md** (this file) - Installation and usage guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete SPCS deployment guide
- **[QUICKREF.md](QUICKREF.md)** - Quick reference card
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Implementation details

## Support

- **Snowflake questions**: Contact your Snowflake account team
- **Application issues**: Check [Streamlit documentation](https://docs.streamlit.io)
- **Community support**: [community.snowflake.com](https://community.snowflake.com)

## Roadmap

Potential future enhancements:

- [ ] Integration with Snowflake APIs for live cost data
- [ ] Historical cost trend visualization
- [ ] Automated recommendation refinement based on actual usage
- [ ] Multi-pool comparison and optimization
- [ ] Role-based access control
- [ ] Custom report scheduling
- [ ] Snowflake Native App version

## Contributing

This tool is provided for customer enablement. Customize as needed for your organization.

## License

MIT License - See LICENSE file for details

## Version

**Current Version**: 1.0.0  
**Last Updated**: 2024

---

Built with ❄️ by Snowflake
