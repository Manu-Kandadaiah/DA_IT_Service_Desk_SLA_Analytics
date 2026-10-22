# IT Service Desk & SLA Analytics

**Python | Pandas | SQL | Jupyter Notebook | Excel | Data Analytics**

**Professional Project | SPM India Limited**

## Project Overview

This IT Service Desk & SLA Analytics project was developed as part of my current professional role at **SPM India Limited**.

The project demonstrates how data analytics can be applied to IT service management to evaluate support efficiency, monitor Service Level Agreement (SLA) compliance, analyze technician performance, and identify opportunities for operational improvement.

Using Python, Pandas, SQL, Jupyter Notebook, and Microsoft Excel, I developed an analytical workflow covering data preparation, exploratory analysis, KPI reporting, and dashboard visualization.

The portfolio version uses **synthetic data and the fictional company name Pi Systems Private Limited** to demonstrate the analytical approach without disclosing actual company or employee information.

## Business Problem

IT service desk operations require continuous monitoring to ensure timely issue resolution, effective resource utilization, and consistent service quality.

The project addresses the following business questions:

- How effectively are IT support tickets being resolved?
- What percentage of tickets meet SLA targets?
- Which ticket categories experience higher resolution times?
- How is workload distributed among technicians?
- What factors contribute to unresolved tickets and backlog?
- How can support performance and customer satisfaction be improved?

## Dataset and Project Scope

The analytical dataset includes:

| Metric | Dataset Details |
|---|---|
| IT Support Tickets | 20,000 |
| Employees | 1,500 |
| Technicians | 25 |
| IT Assets | 2,500 |
| Reported SLA Compliance | 81.42% |
| Dataset Type | Synthetic / Demonstration |

**Data Privacy:** All portfolio datasets are fictional and do not represent actual SPM India Limited employees, customers, systems, or confidential operational records.

The reported SLA compliance figure originates from the existing project documentation and has not been independently recalculated for this README.

## Technologies Used

- **Python:** Data processing, automation, and analytical scripting.
- **Pandas:** Data cleaning, transformation, and KPI calculations.
- **SQL (MySQL dialect):** Relational data modeling, filtering, aggregation, and analytical queries.
- **Jupyter Notebook:** Exploratory Data Analysis (EDA) and interactive analysis.
- **Microsoft Excel:** Dashboard development, performance monitoring, and management reporting.

## Key Features and Analysis

### 1. IT Ticket Analysis

Analyzes service requests and incidents to identify ticket volumes, issue categories, priority distributions, and operational trends.

### 2. SLA Compliance Monitoring

Evaluates ticket performance against defined service-level targets and highlights potential SLA breaches.

### 3. Resolution Time Analysis

Examines resolution durations to identify delays, recurring issues, and opportunities to improve service efficiency.

### 4. Technician Performance

Analyzes technician workloads, ticket assignments, and resolution performance to support better resource planning.

### 5. Customer Satisfaction Analysis

Explores customer satisfaction indicators to understand the relationship between support performance and service quality.

### 6. Excel Dashboard and Reporting

Presents important operational KPIs, trends, and analytical findings in a structured format suitable for management review.

## Skills Demonstrated

- Data cleaning and preprocessing
- Exploratory Data Analysis (EDA)
- Python automation and data transformation
- SQL queries and relational database concepts
- KPI identification and performance analysis
- Data visualization and dashboard development
- Analytical reporting and business insights
- Problem-solving using operational data
- Technical documentation and project organization

## Project Deliverables

**Excel Dashboard**

`excel/Pi_Systems_IT_Service_Desk_Dashboard.xlsx`

**Jupyter Notebooks**

- `notebooks/01_Data_Cleaning.ipynb`
- `notebooks/02_IT_Service_Desk_Analysis.ipynb`

**Python Scripts**

The `python/` directory contains scripts for data generation, cleaning, analysis, and reporting.

**SQL Scripts**

The `sql/` directory contains the original MySQL-oriented database schema and analytical queries.

**Datasets**

The `data/` directory contains synthetic source, cleaned, and reference datasets.

**Reports**

The `reports/` directory contains existing analytical outputs, visualizations, business insights, and recommendations.

## Getting Started

### Prerequisites

- Python 3.11 or 3.12
- PyCharm or Visual Studio Code
- Jupyter Notebook
- Microsoft Excel

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/it-service-desk-sla-analytics.git
cd it-service-desk-sla-analytics
```

### Step 2: Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Open Jupyter Notebook

```powershell
python -m jupyter lab
```

Open the notebooks inside the `notebooks/` directory to explore the analytical workflow.

### Step 5: Run Python Scripts

The existing scripts can be run in dependency order:

```powershell
python python/clean_data.py
python python/analysis.py
python python/generate_reports.py
```

**Note:** Some scripts may overwrite generated files. Back up existing outputs before regenerating results.

The original SQL files use MySQL syntax. MySQL is not required to review the existing CSV files, Excel dashboard, or notebooks. The SQL scripts have not been fully converted or validated against SQLite.

## Project Structure

```text
it-service-desk-sla-analytics/
├── data/
│   └── Synthetic datasets
├── python/
│   └── Data processing and analysis scripts
├── notebooks/
│   └── Jupyter notebooks
├── sql/
│   └── MySQL-oriented SQL scripts
├── excel/
│   └── Excel analytics dashboard
├── reports/
│   └── Charts, insights and recommendations
├── docs/
│   └── Supporting documentation
├── README.md
├── requirements.txt
└── .gitignore
```

## Business Impact and Learning Outcomes

This project demonstrates how structured IT service desk analytics can help organizations:

- Monitor SLA performance and identify service gaps.
- Identify recurring issues and resolution delays.
- Evaluate technician workloads and support efficiency.
- Improve visibility into unresolved tickets and backlog.
- Support management decisions through KPI-based reporting.
- Identify opportunities to improve IT service quality.

The project reflects practical analytical problem-solving relevant to enterprise IT operations and business reporting.

## Project Limitations

- The published dataset is synthetic and intended for portfolio demonstration.
- The fictional company name Pi Systems Private Limited is retained in the original datasets and Excel workbook.
- The portfolio does not contain confidential operational data from SPM India Limited.
- Original SQL scripts use MySQL syntax.
- Some workflows may require MySQL or additional local configuration.
- Existing dashboards and reports have not been independently regenerated or validated as part of this README revision.
- The repository does not claim a live production deployment.

## Recruiter / Reviewer Guide

For a quick review of this project:

1. **Excel Dashboard:** Open the dashboard to understand the final analytical output.
2. **Business Insights:** Review the existing reports and recommendations.
3. **Python Scripts:** Examine the data-cleaning and analysis workflow.
4. **Jupyter Notebooks:** Explore the analytical approach and calculations.
5. **SQL Files:** Review database design and analytical queries.

## Professional Context

**Organization:** SPM India Limited  
**Project:** IT Service Desk & SLA Analytics  
**Domain:** IT Operations and Data Analytics  
**Project Context:** Developed as part of my current professional role, with a fictional dataset used for public portfolio demonstration.

---

*This repository demonstrates my practical experience applying Python, SQL, Excel, and data analytics techniques to IT service management and operational performance analysis.*
