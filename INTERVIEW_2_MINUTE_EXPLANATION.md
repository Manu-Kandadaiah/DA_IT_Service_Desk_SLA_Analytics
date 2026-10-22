# 2-Minute Interview Explanation

I built an **IT Service Desk & SLA Analytics** project for a fictional company, Pi Systems Private Limited, using completely synthetic data. The objective was to analyze support-ticket demand, SLA performance, resolution time, technician workload, backlog, reopened incidents and customer satisfaction.

I generated 20,000 tickets covering 2025 and 2026, linked to 1,500 employees, 25 technicians and 2,500 assets. I intentionally introduced issues such as duplicate ticket IDs, missing technician assignments, inconsistent capitalization, mixed date formats and invalid CSAT values. I cleaned and validated the data using Pandas, and I kept legitimate missing values such as non-response CSAT rather than blindly filling them.

For analysis I used Pandas and NumPy to calculate SLA compliance, breach rates, average/median/95th-percentile resolution time, backlog aging, technician workload, reopen rate, category and department patterns, Pareto concentration, monthly growth and rolling trends. In the generated dataset, SLA compliance is **81.42%**, average resolution is **15.20 hours**, current backlog is **109 tickets**, average CSAT is **4.32/5**, and reopen rate is **4.31%**.

I also created a relational MySQL schema with 44 business queries and an Excel dashboard for management reporting. My recommendations focus on high-volume categories, high-breach areas, aging backlog, staffing around demand peaks and recurring reopened issues. This is a portfolio project, not professional client work, and I clearly label the data as synthetic.
