# Interview Preparation

## 30 Data Analyst Questions and Answers
### 1. What business problem does this project solve?
It analyzes support demand, SLA performance, resolution time, backlog, technician workload, reopen behavior and CSAT to identify where service operations can improve.

### 2. Why use synthetic data?
The project demonstrates the workflow without exposing confidential employee or ticket information; a fixed random seed makes it reproducible.

### 3. How did you avoid completely random records?
Ticket category depends on department, volume depends on working hours/month/day patterns, SLA target depends on priority, resolution depends on category/priority/technician/load, and CSAT depends partly on breach/reopen/resolution behavior.

### 4. What were the main data-quality issues?
Duplicate ticket IDs, spaces, capitalization, category typos, mixed date formats, missing technician assignments, invalid CSAT scores and invalid text values.

### 5. How did you treat missing CSAT?
I did not impute survey non-responses because missing feedback has business meaning; only invalid scores outside 1–5 were converted to missing.

### 6. How did you validate SLA?
The policy table is the source of truth, and SLA status is recalculated from resolution time for resolved tickets or active age for open tickets.

### 7. What is the SLA compliance KPI?
Met tickets divided by tickets with a measurable Met/Breached SLA status, multiplied by 100.

### 8. Why separate average and median resolution time?
The distribution is right-skewed; the median represents a typical ticket better while the mean reflects the impact of long incidents.

### 9. Why calculate a 95th percentile?
It shows the upper-tail service experience and is useful for understanding difficult incidents without focusing only on the maximum.

### 10. How did you analyze backlog?
I filtered current open/assigned/in-progress/pending/reopened tickets and grouped them by priority, category, department, technician and aging band.

### 11. How did you define ticket aging?
For active tickets, age is hours from creation to the project as-of timestamp; resolved tickets use resolution duration.

### 12. What is Pareto analysis?
It sorts categories by ticket count and calculates cumulative share to identify the small set driving most incidents.

### 13. How did you analyze technicians fairly?
I report workload, resolution time, response time, SLA, reopens and CSAT together rather than declaring one best technician.

### 14. How did you analyze customer satisfaction?
I compared average CSAT across categories, priorities, technicians, resolution bands and departments and checked correlation with resolution time.

### 15. Does correlation prove longer resolution causes low CSAT?
No. Correlation is an association and can be affected by ticket complexity, priority, user expectations and other variables.

### 16. How did you identify outliers?
I used the IQR rule on resolution time and retained valid long-running incidents for review rather than deleting them automatically.

### 17. How did you measure seasonality?
Monthly, quarterly, yearly, day-of-week and hourly ticket patterns plus MoM, YoY and rolling three-month trends.

### 18. Why is working-hour volume important?
It helps determine staffing and shift coverage during periods when most users submit tickets.

### 19. What is a useful operational drill-down?
Start with SLA breach rate, then drill from priority/category to department, technician, age and specific tickets.

### 20. Why use a relational database?
Employees, technicians, assets, categories, SLA policies, tickets, history and satisfaction are naturally related and benefit from referential integrity.

### 21. What would you automate in production?
Incremental ticket ingestion, validation checks, SLA countdown alerts, backlog aging alerts and scheduled KPI/dashboard refresh.

### 22. What is an important limitation?
The data is synthetic, so findings demonstrate analytics methods rather than actual company performance.

### 23. What would you add with real ITSM data?
First-contact resolution, assignment groups, escalation timestamps, business-hours SLA calendars, problem/change links and actual service catalog data.

### 24. How did you keep insights honest?
All insight numbers are generated only after analysis; the report does not invent values in advance.

### 25. How do you separate insight from recommendation?
An insight states measured behavior; a recommendation proposes an action in response and is documented separately.

### 26. Why is SLA target configurable?
Priority targets live in a policy table, so the logic can change without rewriting every ticket record.

### 27. How is reopen rate calculated?
Tickets marked Reopened=Yes divided by total tickets, multiplied by 100.

### 28. Why analyze first response separately from resolution?
Users can receive quick acknowledgement but still wait a long time for resolution; the two metrics describe different service stages.

### 29. How do you explain this project to an interviewer?
I describe the business problem, relational synthetic data design, cleaning, KPI logic, Python/SQL analysis, Excel communication, actual findings and limitations.

### 30. What proves the project is reproducible?
A fixed seed, executable generation/cleaning/analysis scripts, requirements file, SQL schema and documented run order.

## 15 SQL Questions and Answers
### 1. JOIN vs LEFT JOIN?
JOIN/INNER JOIN keeps matches; LEFT JOIN keeps every left-row even when the right table has no match.

### 2. What is a CTE?
A named temporary result defined with WITH that improves readability of multi-step SQL.

### 3. What is a window function?
A calculation over related rows without collapsing detail, such as RANK, LAG or running SUM.

### 4. RANK vs DENSE_RANK?
RANK leaves gaps after ties; DENSE_RANK does not.

### 5. ROW_NUMBER use case?
Selecting the latest ticket per employee or de-duplicating ordered records.

### 6. What does LAG do?
Returns a prior row value, used here for month-over-month ticket growth.

### 7. WHERE vs HAVING?
WHERE filters rows before aggregation; HAVING filters grouped results after GROUP BY.

### 8. Why COALESCE?
It substitutes a value for NULL, useful in left-joined technician summaries.

### 9. COUNT(*) vs COUNT(column)?
COUNT(*) counts rows; COUNT(column) ignores NULL values.

### 10. How calculate SLA compliance in SQL?
Average a CASE expression that returns 1 for Met and 0 for Breached over measurable tickets.

### 11. How calculate median in MySQL?
Use ROW_NUMBER and COUNT window functions, then average the middle one/two rows.

### 12. Why use foreign keys?
They enforce valid relationships among tickets, employees, technicians, assets, categories and policies.

### 13. What is a subquery?
A query embedded inside another query; used here to compare category breach rates with the overall rate.

### 14. How calculate a running total?
Aggregate monthly tickets, then SUM(Tickets) OVER (ORDER BY Month).

### 15. Why index ticket columns?
Indexes on created time, priority, status, SLA, technician and category speed common filters and joins.

## 15 Pandas Questions and Answers
### 1. groupby()?
Splits data into groups for aggregation, such as SLA metrics by priority or technician.

### 2. merge()?
Joins DataFrames using keys, such as tickets to technicians or assets.

### 3. pivot_table()?
Creates an aggregated matrix, useful for backlog by age band and priority.

### 4. apply()?
Runs a custom function on rows/columns; use only when vectorized logic is not clearer.

### 5. lambda?
A short anonymous function used inside groupby aggregation or apply.

### 6. loc?
Label/boolean selection for filters and assignments.

### 7. iloc?
Position-based selection for inspection or ordered subsets.

### 8. to_datetime()?
Converts date/time text to a datetime type for calculations and grouping.

### 9. rolling()?
Computes moving-window metrics, such as rolling three-month ticket volume.

### 10. shift()?
Offsets a series, used for prior-month or prior-year comparison.

### 11. rank()?
Creates numerical ranks for workload or response metrics without collapsing rows.

### 12. transform()?
Returns group-level calculations aligned to original rows, useful for within-group benchmarks.

### 13. value_counts()?
Counts category occurrences, such as status or priority distributions.

### 14. drop_duplicates()?
Removes repeated business keys while controlling which record is kept.

### 15. fillna/dropna?
fillna handles justified missing values; dropna is used selectively when a calculation requires observed values.

## 15 Excel Questions and Answers
### 1. What is a PivotTable?
An interactive aggregation tool for summarizing measures by dimensions.

### 2. What is a PivotChart?
A chart linked to a PivotTable that follows its grouping and filtering.

### 3. XLOOKUP?
Returns a related value from another range, used for ticket/technician/category lookups.

### 4. SUMIFS?
Sums values that meet multiple conditions.

### 5. COUNTIFS?
Counts rows that meet multiple conditions, useful for SLA/status/priority KPIs.

### 6. IF?
Returns one value when a condition is true and another when false.

### 7. IFS?
Evaluates multiple ordered conditions, useful for aging/action bands.

### 8. INDEX/MATCH?
A flexible lookup combination where MATCH locates the row and INDEX returns the value.

### 9. Conditional Formatting?
Visually highlights breaches, aging tickets or high workloads based on rules.

### 10. Excel Tables?
Structured, filterable ranges that expand formulas and make references easier to manage.

### 11. Data Validation?
Restricts cell input or provides dropdown filters.

### 12. How create KPI cards?
Use clearly labeled merged blocks with large formula-linked values and appropriate number formats.

### 13. How validate dashboard KPIs?
Cross-check key Excel values with the Python KPI export and formula audit.

### 14. How use slicers/filters?
Provide interactive filtering by year, month, department, category, priority, technician, location and status.

### 15. Why keep a dashboard simple?
Decision makers need a small number of high-value KPIs and exception trends rather than every available field.

## 15 Business / Dashboard Questions and Answers
### 1. What is an SLA?
A Service Level Agreement defines expected service targets such as response or resolution time.

### 2. SLA Compliance?
The percentage of measurable tickets completed within the SLA target.

### 3. SLA Breach?
A ticket exceeds its SLA target based on resolution time or active age.

### 4. First Response Time?
Minutes from ticket creation until support first responds or assigns/acknowledges the request.

### 5. Resolution Time?
Hours from ticket creation until the incident is resolved.

### 6. Backlog?
Tickets that remain open, assigned, in progress, pending or reopened at the analysis date.

### 7. Ticket Aging?
How long a current backlog ticket has remained active since creation.

### 8. CSAT?
Customer Satisfaction score returned after support, usually on a 1–5 scale in this project.

### 9. Reopen Rate?
Percentage of tickets that were reopened after an earlier resolution.

### 10. Why track category breach rate?
It identifies ticket types that are difficult to complete within the agreed target.

### 11. Why track technician workload?
Uneven workload can contribute to delays, but it must be interpreted with complexity and performance metrics.

### 12. What does Pareto tell you?
Which few categories account for the majority of ticket volume.

### 13. Why analyze backlog aging bands?
They separate recent work from tickets at risk of becoming persistent or forgotten.

### 14. Why monitor monthly SLA trend?
A monthly trend reveals whether compliance is stable, improving or deteriorating with workload.

### 15. What should an IT dashboard recommendation avoid?
It should avoid unsupported claims about individual performance or causation and should connect actions to measured data.
