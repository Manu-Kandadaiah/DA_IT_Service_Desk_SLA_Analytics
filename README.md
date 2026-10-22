# IT Service Desk & SLA Analytics

**Python · Pandas · SQL (MySQL dialect) · Jupyter · Excel · Data Analytics**

> **Portfolio disclosure:** The source project uses the fictional company **Pi Systems Private Limited** and synthetic data. This repository preserves the original workbook and data labels rather than falsely claiming they were rebranded or independently verified.

## Project overview

Analyze service-desk ticket volume, SLA compliance, resolution times, backlog, technician workloads and customer satisfaction.

**Business question:** How can decision-makers use reliable operational data to identify trends, diagnose performance gaps and prioritize improvements?

## Dataset and scope

20,000 cleaned tickets, 1,500 employees, 25 technicians, 2,500 assets; 81.42% SLA compliance as reported in the original project.

Data are synthetic and provided for demonstration and education; they do not represent real employees, customers, or suppliers. Raw and processed data are kept separate where supplied.

## Skills demonstrated

- Data cleaning and validation with Python and Pandas
- Exploratory analysis, KPI definition and trend reporting
- Relational SQL schema and analytical queries (original scripts use MySQL syntax)
- Excel dashboard and management-oriented communication
- Reproducible analysis scripts, documentation and supporting notebooks

## Main deliverables

- **Excel dashboard:** [`excel/Pi_Systems_IT_Service_Desk_Dashboard.xlsx`](excel/Pi_Systems_IT_Service_Desk_Dashboard.xlsx)
- **Notebooks:** `notebooks/02_IT_Service_Desk_Analysis.ipynb`, `notebooks/01_Data_Cleaning.ipynb`
- **Python scripts:** `python/` for generation, cleaning, analysis and reporting
- **SQL:** `sql/` contains the original MySQL-oriented schema and analysis
- **Data:** `data/` includes source, processed and reference CSV files
- **Reports:** `reports/` includes existing exports, charts and business insights

## Getting started (Windows / PyCharm)

1. Clone the repository or download and extract the ZIP.
2. Open the repository root in PyCharm. Use Python 3.11 or 3.12.
3. In the terminal, create a virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

4. Start with the existing reports and Excel dashboard. For interactive work, run `python -m jupyter lab` and open a notebook from `notebooks/`.
5. To regenerate outputs, inspect the scripts and run them in dependency order. **Some scripts overwrite generated CSVs or charts; make a backup before regeneration.**

```powershell
python python/clean_data.py
python python/analysis.py
python python/generate_reports.py
```

**SQL note:** The existing `python/load_mysql.py` and `sql/` files target MySQL. MySQL is optional for reviewing the Excel dashboard, CSV datasets and Python analysis; **these SQL scripts have not been converted or tested against SQLite**.

## Results and interpretation

See `reports/` and the dashboard for calculated KPIs, trends, recommendations and data-quality findings. Reported figures originate from the original project documentation; this packaging step does not independently recalculate them.

## Repository organization

```text
it-service-desk-sla-analytics/
├── data/           # synthetic raw, cleaned and reference datasets
├── python/         # processing and analytics scripts
├── notebooks/      # interactive analysis
├── sql/            # MySQL SQL scripts
├── excel/          # Excel dashboard
├── reports/        # figures, exports and insights
├── docs/           # original README and supporting docs
├── README.md
├── requirements.txt
└── .gitignore
```

## Limitations

- Synthetic data and simulated business scenarios; not live operational reporting.
- Original company naming is preserved in the data and workbook.
- Some Python scripts may require MySQL if using the database import workflow.
- Existing charts and workbook were not regenerated during packaging.
- No claim of production deployment or independently validated end-to-end execution.

## Recruiter / reviewer quick tour

1. Open the Excel dashboard to see the final deliverable.
2. Read `reports/business_insights.md` and `reports/business_recommendations.md` if available.
3. Review `python/clean_data.py` and `python/analysis.py` for the analytical workflow.
4. Browse the notebooks and SQL scripts for implementation details.

## Publishing to GitHub

See [`GITHUB_UPLOAD_GUIDE.md`](GITHUB_UPLOAD_GUIDE.md) for exact commands and the upload/exclusion checklist.
