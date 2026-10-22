# Data Quality Report

The raw ticket file intentionally contains controlled quality issues. Cleaning preserves useful records and applies documented business rules rather than deleting all imperfect rows.

## Record Counts

- Raw records: **20,090**
- Cleaned records: **20,000**
- Raw columns: **24**
- Cleaned columns (including engineered fields): **38**

## Duplicates

- Duplicate Ticket_ID rows before cleaning: **90**
- Duplicate Ticket_ID rows after cleaning: **0**

## Missing Values Before Cleaning

- Resolved_Date: 636
- Closed_Date: 4,351
- Assigned_Technician: 130
- Asset_ID: 7,501
- Resolution_Time_Hours: 636
- Customer_Satisfaction: 5,114

## Missing Values After Cleaning

- Resolved_Date: 633
- Closed_Date: 4,333
- Asset_ID: 7,468
- Resolution_Time_Hours: 633
- SLA_Remaining_Hours: 530
- Customer_Satisfaction: 5,106
- Resolved_Timestamp: 633
- Ticket_Age_Hours: 530

## Cleaning / Transformation Decisions

- Removed duplicate ticket IDs while retaining the first source record.
- Trimmed extra spaces and standardized category, priority, status, channel and reopen values.
- Parsed both ISO and day-first date formats.
- Replaced raw SLA target values with the configurable priority policy from `sla_policies.csv`.
- Imputed missing technician names from the most common Category + Location assignment, then Category fallback; retained `Unassigned` only if no defensible mapping existed.
- Invalid CSAT values outside 1–5 were converted to missing. Legitimate non-response CSAT values were not imputed.
- Invalid resolution-code text was preserved as `Other / Unclassified` rather than dropping the ticket.
- Recomputed SLA status logically from resolution time for resolved tickets and current age for active tickets.
- Added SLA_Breached, SLA_Remaining_Hours, resolution bands, ticket age, aging bands, and date/time features.
- Resolution-time outliers were flagged using the IQR method and retained because long-running incidents can be valid operational cases.

## Validation Checks

- **cleaned_unique_ticket_ids:** True
- **invalid_priority_values:** 0
- **invalid_status_values:** 0
- **invalid_channel_values:** 0
- **invalid_employee_fk:** 0
- **invalid_technician_fk:** 0
- **invalid_asset_fk:** 0
- **negative_resolution_time:** 0
- **negative_first_response:** 0
- **resolved_before_created:** 0
- **closed_before_resolved:** 0
- **sla_target_mismatch:** 0
- **sla_calculation_mismatch_resolved:** 0
- **invalid_csat_after_cleaning:** 0

## Outliers

- IQR-based long-resolution threshold: **36.67 hours**
- Valid tickets above threshold retained: **1,578**

## Important Missing-Value Interpretation

- `Resolved_Date`, `Closed_Date`, `Resolution_Time_Hours`, and `Resolved_Timestamp` are expected to be missing for active or cancelled tickets.
- `Customer_Satisfaction` is expected to be missing when a survey was not returned; missing CSAT is not automatically a data error.
- `Asset_ID` can legitimately be missing for account/access/password tickets that are not tied to a specific physical asset.