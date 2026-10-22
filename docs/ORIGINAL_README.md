# IT Service Desk & SLA Analytics

**Fictional company:** Pi Systems Private Limited  
**Period:** 2025-01-01 to 2026-12-31  
**Technology:** Python, Pandas, NumPy, MySQL, SQL, Excel, Matplotlib

> **This project uses synthetic data and a fictional company for portfolio and educational purposes.**

## Project Overview
This project analyzes IT support tickets, incidents, SLA performance, first response, resolution time, backlog aging, technician workload, reopened tickets, customer satisfaction, assets and operational trends.

## Business Problem
How can an IT service desk improve SLA compliance, control backlog, understand incident drivers and support technician/workload decisions while maintaining customer satisfaction?

## Objectives
- Generate reproducible, relational synthetic service-desk data with realistic patterns.
- Clean controlled data-quality issues without deleting useful business records.
- Calculate SLA, resolution, backlog, reopen, CSAT, technician and volume KPIs.
- Analyze monthly/quarterly/yearly trends, working-hour patterns and category Pareto concentration.
- Query the model in MySQL and communicate results through Matplotlib and Excel.

## Dataset
| Dataset | Records |
|---|---:|
| Cleaned tickets | 20,000 |
| Employees | 1,500 |
| Technicians | 25 |
| Assets | 2,500 |
| Ticket history events | 75,360 |
| Satisfaction responses | 15,061 |

The raw ticket file contains controlled duplicates, mixed date formats, spaces, inconsistent capitalization, missing technician values, missing CSAT responses and invalid text/score values.

## Data Dictionary
The cleaned ticket dataset contains the requested ticket identifiers, created/resolved/closed dates, employee/department/location fields, category/subcategory, priority/status, assigned technician, channel, asset, description, response/resolution measures, SLA target/status, reopen flag, resolution code and CSAT. Engineered fields add SLA breach indicator, remaining SLA hours, resolution/aging bands, timestamps and date/time components.

## Technology Stack
Python, Pandas, NumPy, MySQL 8+, SQL, Excel and Matplotlib. Power BI and Tableau are not used.

## Project Architecture
```text
generate_data.py -> data/raw/01_raw_tickets.csv + reference data
        |
clean_data.py -> data/processed/02_cleaned_tickets.csv + data_quality_report.md
        |
analysis.py -> reports/exports + business insights/recommendations
        |
generate_reports.py -> reports/charts/*.png
        |
MySQL schema + SQL analysis + Excel dashboard
```

## Data Cleaning
Cleaning uses `read_csv`, `isnull`, `fillna`, selective `dropna`, `drop_duplicates`, `loc`, `iloc`, `groupby`, `agg`, `merge`, `concat`, `pivot_table`, `apply`, `map`, `lambda`, `to_datetime`, and documented validation. Missing CSAT survey responses are intentionally not imputed.

## EDA
EDA covers data types, missingness, duplicates, descriptive statistics, ticket volume, category/subcategory mix, priority/status distribution, locations, channels, day/hour patterns and resolution-time outliers.

## SLA Analysis
The configurable SLA policy is Critical=4h, High=8h, Medium=24h, Low=48h. The generated dataset has **81.42% SLA compliance** and **18.58% breach rate** across measurable tickets.

## Key KPIs
- Total Tickets: **20,000**
- Current Backlog: **109**
- SLA Compliance: **81.42%**
- SLA Breach Rate: **18.58%**
- Average Resolution Time: **15.20 h**
- Median Resolution Time: **9.60 h**
- 95th Percentile Resolution Time: **49.21 h**
- Average First Response: **30.20 min**
- Average CSAT: **4.32/5**
- Reopen Rate: **4.31%**

## SQL Analysis
`sql/03_SQL_Service_Desk_Analysis.sql` contains 44 business queries using joins, left joins, CASE, COALESCE, subqueries, CTEs and window functions including RANK, DENSE_RANK, ROW_NUMBER and LAG.

## Excel Dashboard
`excel/Pi_Systems_IT_Service_Desk_Dashboard.xlsx` contains Raw_Data, Cleaned_Data, Calculations, Pivot_Tables, SLA_Analysis, Technician_Analysis, Category_Analysis, Department_Analysis, Monthly_Analysis and Dashboard sheets.

## Business Insights
See `reports/business_insights.md`. Every numbered insight is derived from the generated dataset.

## Recommendations
See `reports/business_recommendations.md`. Recommendations are separated from factual findings and tied to observed patterns.

## Screenshots / Charts
Twenty-two Matplotlib charts are stored in `reports/charts/`, including ticket volume, SLA trends, category/priority/department views, technician workload, backlog aging, CSAT, resolution distribution, Pareto analysis, channel use and day/hour patterns.

## How to Run
### Python Installation
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

### Execution Order
```bash
python python/generate_data.py
python python/clean_data.py
python python/analysis.py
python python/generate_reports.py
```

### MySQL Setup
1. Install/start MySQL 8+.
2. Set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`.
3. Run `python python/load_mysql.py`.
4. Execute `sql/03_SQL_Service_Desk_Analysis.sql`.

## Requirements
See `requirements.txt`.

## Project Structure
```text
it_service_desk_analytics/
├── data/
│   ├── raw/01_raw_tickets.csv
│   └── processed/
│       ├── 02_cleaned_tickets.csv
│       ├── employees.csv
│       ├── technicians.csv
│       ├── assets.csv
│       ├── departments.csv
│       ├── ticket_categories.csv
│       ├── sla_policies.csv
│       ├── ticket_history.csv
│       └── satisfaction.csv
├── notebooks/
│   ├── 01_Data_Cleaning.ipynb
│   └── 02_IT_Service_Desk_Analysis.ipynb
├── python/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── analysis.py
│   ├── generate_reports.py
│   └── load_mysql.py
├── sql/
│   ├── schema.sql
│   └── 03_SQL_Service_Desk_Analysis.sql
├── excel/Pi_Systems_IT_Service_Desk_Dashboard.xlsx
├── reports/charts/
├── reports/exports/
├── reports/data_quality_report.md
├── reports/business_insights.md
├── reports/business_recommendations.md
├── README.md
├── PORTFOLIO_CONTENT.md
├── INTERVIEW_PREPARATION.md
├── INTERVIEW_2_MINUTE_EXPLANATION.md
├── requirements.txt
└── .gitignore
```

## Future Improvements
- Add business-hours/holiday SLA calendars instead of elapsed-clock SLAs.
- Add first-contact resolution and assignment-group transfer metrics.
- Add problem/change records for recurring incidents.
- Add forecast accuracy and staffing scenario analysis.
- Add natural-language text classification only after establishing labeled real-world data and validation.
