# Final Project Checklist

- [x] 20,000 unique synthetic tickets covering 2025–2026
- [x] 1,500 fictional employees
- [x] 25 fictional IT technicians with uneven workload/performance
- [x] 2,500 fictional assets
- [x] Configurable Critical/High/Medium/Low SLA policy
- [x] Controlled raw data-quality issues and documented cleaning
- [x] Cleaned ticket dataset with SLA, resolution and aging features
- [x] 5 executable Python scripts
- [x] 2 Jupyter notebooks
- [x] MySQL schema with 9 requested tables
- [x] 44 SQL business-analysis queries
- [x] Excel dashboard workbook
- [x] 22 Matplotlib charts
- [x] 23 dataset-derived business insights
- [x] Data-backed recommendations
- [x] README, portfolio content, interview preparation and two-minute explanation

## Validation
The latest cleaning run reports zero duplicate Ticket_ID values, zero invalid priority/status/channel values, zero invalid employee/technician/asset foreign keys, zero negative resolution/response times, zero date-order errors, zero SLA-target mismatches, zero resolved-ticket SLA calculation mismatches, and zero invalid CSAT values after cleaning.

## Run Order
```bash
pip install -r requirements.txt
python python/generate_data.py
python python/clean_data.py
python python/analysis.py
python python/generate_reports.py
# configure MySQL credentials, then:
python python/load_mysql.py
```

## Current Generated KPIs
- Total tickets: 20,000
- SLA compliance: 81.42%
- SLA breach rate: 18.58%
- Current backlog: 109
- Average resolution time: 15.20 hours
- Average first response: 30.20 minutes
- Average CSAT: 4.32/5
- Reopen rate: 4.31%

> This project uses synthetic data and a fictional company for portfolio and educational purposes.
