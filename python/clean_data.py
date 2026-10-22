from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'/'01_raw_tickets.csv'
PROC=ROOT/'data'/'processed'
REPORTS=ROOT/'reports'
PROC.mkdir(parents=True,exist_ok=True)
REPORTS.mkdir(parents=True,exist_ok=True)
AS_OF=pd.Timestamp('2026-12-31 23:59:59')

raw=pd.read_csv(RAW)
employees=pd.read_csv(PROC/'employees.csv')
technicians=pd.read_csv(PROC/'technicians.csv')
assets=pd.read_csv(PROC/'assets.csv')
sla=pd.read_csv(PROC/'sla_policies.csv')

before={
    'rows':int(len(raw)),
    'columns':int(raw.shape[1]),
    'duplicates_full':int(raw.duplicated().sum()),
    'duplicate_ticket_ids':int(raw.duplicated(subset=['Ticket_ID']).sum()),
    'missing':{c:int(v) for c,v in raw.isna().sum().items() if int(v)>0}
}

# Deduplicate by business key, retaining first observed source record.
df=raw.drop_duplicates(subset=['Ticket_ID'],keep='first').copy()

# Trim text fields.
text_cols=['Ticket_ID','Employee_ID','Employee_Name','Department','Location','Category','Subcategory','Priority','Status','Assigned_Technician','Channel','Asset_ID','Description','SLA_Status','Reopened','Resolution_Code']
for c in text_cols:
    df[c]=df[c].astype('string').str.strip()

# Standardize controlled categorical values.
category_map={x.lower():x for x in ['Hardware','Software','Network','Email/Outlook','Access Management','VPN','Printer','Windows','Security','Application','Account/Password']}
category_map['e-mail/outlook']='Email/Outlook'
df['Category']=df['Category'].str.lower().map(category_map).fillna(df['Category'])
priority_map={'critical':'Critical','high':'High','medium':'Medium','med':'Medium','low':'Low'}
df['Priority']=df['Priority'].str.lower().map(priority_map)
status_values=['Open','Assigned','In Progress','Pending','Resolved','Closed','Reopened','Cancelled']
status_map={x.lower():x for x in status_values}
df['Status']=df['Status'].str.lower().map(status_map)
channel_map={'email':'Email','e-mail':'Email','phone':'Phone','portal':'Portal','chat':'Chat','walk-in':'Walk-in'}
df['Channel']=df['Channel'].str.lower().map(channel_map)
reopen_map={'yes':'Yes','no':'No'}
df['Reopened']=df['Reopened'].str.lower().map(reopen_map).fillna('No')

# Robust mixed date parser: explicit ISO first, then dd/mm/yyyy.
def parse_mixed_date(series):
    s=series.astype('string')
    out=pd.to_datetime(s,format='%Y-%m-%d',errors='coerce')
    mask=out.isna() & s.notna()
    if mask.any(): out.loc[mask]=pd.to_datetime(s.loc[mask],format='%d/%m/%Y',errors='coerce')
    return out

for c in ['Created_Date','Resolved_Date','Closed_Date']:
    df[c]=parse_mixed_date(df[c])
# Time normalization; invalid times become midnight and are flagged later.
parsed_time=pd.to_datetime(df['Created_Time'],format='%H:%M:%S',errors='coerce')
invalid_created_time=int(parsed_time.isna().sum())
parsed_time=parsed_time.fillna(pd.Timestamp('1900-01-01 00:00:00'))
df['Created_Time']=parsed_time.dt.strftime('%H:%M:%S')
df['Created_Timestamp']=pd.to_datetime(df['Created_Date'].dt.strftime('%Y-%m-%d')+' '+df['Created_Time'],errors='coerce')

# Numeric conversion and range checks.
for c in ['First_Response_Minutes','Resolution_Time_Hours','SLA_Target_Hours','Customer_Satisfaction']:
    df[c]=pd.to_numeric(df[c],errors='coerce')
invalid_csat=int(((df['Customer_Satisfaction']<1)|(df['Customer_Satisfaction']>5)).fillna(False).sum())
df.loc[(df['Customer_Satisfaction']<1)|(df['Customer_Satisfaction']>5),'Customer_Satisfaction']=np.nan

# Configurable SLA policy: source of truth is sla_policies.csv, not ticket-level raw values.
sla_map=sla.set_index('Priority')['SLA_Target_Hours'].to_dict()
df['SLA_Target_Hours']=df['Priority'].map(sla_map).astype(float)

# Recover missing technician values from Category+Location, then Category, then Unassigned.
valid_tech_names=set(technicians['Technician_Name'])
df.loc[~df['Assigned_Technician'].isin(valid_tech_names),'Assigned_Technician']=pd.NA
pair_mode=(df.dropna(subset=['Assigned_Technician']).groupby(['Category','Location'])['Assigned_Technician']
           .agg(lambda x:x.mode().iloc[0] if not x.mode().empty else x.iloc[0]))
cat_mode=(df.dropna(subset=['Assigned_Technician']).groupby('Category')['Assigned_Technician']
          .agg(lambda x:x.mode().iloc[0] if not x.mode().empty else x.iloc[0]))
missing_tech_before=int(df['Assigned_Technician'].isna().sum())
for idx in df.index[df['Assigned_Technician'].isna()]:
    key=(df.at[idx,'Category'],df.at[idx,'Location'])
    if key in pair_mode.index:
        df.at[idx,'Assigned_Technician']=pair_mode.loc[key]
    elif df.at[idx,'Category'] in cat_mode.index:
        df.at[idx,'Assigned_Technician']=cat_mode.loc[df.at[idx,'Category']]
df['Assigned_Technician']=df['Assigned_Technician'].fillna('Unassigned')
tech_id_map=technicians.set_index('Technician_Name')['Technician_ID'].to_dict()
df['Technician_ID']=df['Assigned_Technician'].map(tech_id_map)

# Clean invalid resolution codes conservatively.
known_prefixes=('Resolved - ','Cancelled - ','Pending Investigation')
invalid_resolution_code=~df['Resolution_Code'].fillna('').apply(lambda x:any(str(x).startswith(p) for p in known_prefixes))
invalid_resolution_codes=int(invalid_resolution_code.sum())
df.loc[invalid_resolution_code,'Resolution_Code']='Other / Unclassified'

# Recompute timestamps and resolution time consistency.
resolved_like=df['Status'].isin(['Resolved','Closed','Reopened']) & df['Resolution_Time_Hours'].notna()
df['Resolved_Timestamp']=pd.NaT
df.loc[resolved_like,'Resolved_Timestamp']=df.loc[resolved_like,'Created_Timestamp']+pd.to_timedelta(df.loc[resolved_like,'Resolution_Time_Hours'],unit='h')
# Use calculated resolved date where measurable, preserving date-only field requested.
df.loc[resolved_like,'Resolved_Date']=df.loc[resolved_like,'Resolved_Timestamp'].dt.normalize()
# Closed date cannot precede resolved date.
bad_closed=(df['Closed_Date'].notna() & df['Resolved_Date'].notna() & (df['Closed_Date']<df['Resolved_Date']))
df.loc[bad_closed,'Closed_Date']=df.loc[bad_closed,'Resolved_Date']

# Status/date rules.
unresolved_status=['Open','Assigned','In Progress','Pending']
df.loc[df['Status'].isin(unresolved_status),['Resolved_Date','Resolved_Timestamp','Closed_Date','Resolution_Time_Hours']]=[pd.NaT,pd.NaT,pd.NaT,np.nan]
df.loc[df['Status'].eq('Cancelled'),['Resolved_Date','Resolved_Timestamp','Closed_Date','Resolution_Time_Hours']]=[pd.NaT,pd.NaT,pd.NaT,np.nan]
# Closed must have resolved timestamp; rows that cannot meet this rule are reclassified as In Progress.
bad_closed_missing=df['Status'].eq('Closed') & df['Resolved_Timestamp'].isna()
df.loc[bad_closed_missing,'Status']='In Progress'

# Ticket age for active/backlog tickets; resolved tickets use measured resolution duration.
active_mask=df['Status'].isin(['Open','Assigned','In Progress','Pending','Reopened'])
df['Ticket_Age_Hours']=np.where(active_mask,(AS_OF-df['Created_Timestamp']).dt.total_seconds()/3600,df['Resolution_Time_Hours'])
df['Ticket_Age_Hours']=pd.to_numeric(df['Ticket_Age_Hours'],errors='coerce').clip(lower=0)

# SLA status is calculated, never randomly assigned.
resolved_measure=df['Resolution_Time_Hours'].notna() & ~df['Status'].eq('Cancelled')
df['SLA_Status']='Pending'
df.loc[resolved_measure,'SLA_Status']=np.where(df.loc[resolved_measure,'Resolution_Time_Hours']<=df.loc[resolved_measure,'SLA_Target_Hours'],'Met','Breached')
active_measure=active_mask & df['Ticket_Age_Hours'].notna()
df.loc[active_measure,'SLA_Status']=np.where(df.loc[active_measure,'Ticket_Age_Hours']>df.loc[active_measure,'SLA_Target_Hours'],'Breached','Pending')
df.loc[df['Status'].eq('Cancelled'),'SLA_Status']='Pending'
df['SLA_Breached']=df['SLA_Status'].eq('Breached').astype(int)
measure_hours=np.where(active_mask,df['Ticket_Age_Hours'],df['Resolution_Time_Hours'])
df['SLA_Remaining_Hours']=(df['SLA_Target_Hours']-pd.Series(measure_hours,index=df.index)).round(2)

# NumPy-driven bands.
rt=df['Resolution_Time_Hours']
df['Resolution_Time_Band']=np.select(
    [rt.le(2),rt.gt(2)&rt.le(4),rt.gt(4)&rt.le(8),rt.gt(8)&rt.le(24),rt.gt(24)&rt.le(72),rt.gt(72)&rt.le(168),rt.gt(168)],
    ['0–2 Hours','2–4 Hours','4–8 Hours','8–24 Hours','1–3 Days','3–7 Days','7+ Days'],default='Unresolved')
age=df['Ticket_Age_Hours']
df['Ticket_Age_Band']=np.select(
    [age.le(4),age.gt(4)&age.le(8),age.gt(8)&age.le(24),age.gt(24)&age.le(72),age.gt(72)&age.le(168),age.gt(168)],
    ['0–4 Hours','4–8 Hours','8–24 Hours','1–3 Days','3–7 Days','7+ Days'],default='Unknown')

# Useful time features.
df['Created_Year']=df['Created_Timestamp'].dt.year
df['Created_Month']=df['Created_Timestamp'].dt.month
df['Created_Day']=df['Created_Timestamp'].dt.day
df['Created_Day_Name']=df['Created_Timestamp'].dt.day_name()
df['Created_Hour']=df['Created_Timestamp'].dt.hour
df['Created_Quarter']='Q'+df['Created_Timestamp'].dt.quarter.astype(str)

# Satisfaction non-response is legitimate: do not impute survey scores.
# Foreign key validation and asset cleanup.
valid_emp=set(employees['Employee_ID']); valid_assets=set(assets['Asset_ID'])
df.loc[~df['Employee_ID'].isin(valid_emp),'Employee_ID']=pd.NA
df.loc[df['Asset_ID'].notna() & ~df['Asset_ID'].isin(valid_assets),'Asset_ID']=pd.NA

# Stable column ordering.
base_cols=['Ticket_ID','Created_Date','Created_Time','Resolved_Date','Closed_Date','Employee_ID','Employee_Name','Department','Location','Category','Subcategory','Priority','Status','Assigned_Technician','Technician_ID','Channel','Asset_ID','Description','First_Response_Minutes','Resolution_Time_Hours','SLA_Target_Hours','SLA_Status','SLA_Breached','SLA_Remaining_Hours','Reopened','Resolution_Code','Customer_Satisfaction','Created_Timestamp','Resolved_Timestamp','Resolution_Time_Band','Ticket_Age_Hours','Ticket_Age_Band','Created_Year','Created_Month','Created_Day','Created_Day_Name','Created_Hour','Created_Quarter']
df=df[base_cols].sort_values(['Created_Timestamp','Ticket_ID']).reset_index(drop=True)
df.to_csv(PROC/'02_cleaned_tickets.csv',index=False,date_format='%Y-%m-%d %H:%M:%S')

# Validation metrics.
active_mask_validation=df['Status'].isin(['Open','Assigned','In Progress','Pending','Reopened'])
measure=df[df['Resolution_Time_Hours'].notna() & ~active_mask_validation]
validation={
    'cleaned_unique_ticket_ids':bool(df['Ticket_ID'].is_unique),
    'invalid_priority_values':int((~df['Priority'].isin(sla_map)).sum()),
    'invalid_status_values':int((~df['Status'].isin(status_values)).sum()),
    'invalid_channel_values':int((~df['Channel'].isin(['Email','Phone','Portal','Chat','Walk-in'])).sum()),
    'invalid_employee_fk':int(df['Employee_ID'].notna().sum()-df['Employee_ID'].dropna().isin(valid_emp).sum()),
    'invalid_technician_fk':int(df['Technician_ID'].notna().sum()-df['Technician_ID'].dropna().isin(set(technicians['Technician_ID'])).sum()),
    'invalid_asset_fk':int(df['Asset_ID'].notna().sum()-df['Asset_ID'].dropna().isin(valid_assets).sum()),
    'negative_resolution_time':int((df['Resolution_Time_Hours']<0).fillna(False).sum()),
    'negative_first_response':int((df['First_Response_Minutes']<0).fillna(False).sum()),
    'resolved_before_created':int((df['Resolved_Timestamp'].notna() & (df['Resolved_Timestamp']<df['Created_Timestamp'])).sum()),
    'closed_before_resolved':int((df['Closed_Date'].notna() & df['Resolved_Date'].notna() & (df['Closed_Date']<df['Resolved_Date'])).sum()),
    'sla_target_mismatch':int((df['SLA_Target_Hours']!=df['Priority'].map(sla_map)).sum()),
    'sla_calculation_mismatch_resolved':int(np.sum((measure['Resolution_Time_Hours'].to_numpy()<=measure['SLA_Target_Hours'].to_numpy())!=(measure['SLA_Status'].to_numpy()=='Met'))),
    'invalid_csat_after_cleaning':int(((df['Customer_Satisfaction']<1)|(df['Customer_Satisfaction']>5)).fillna(False).sum())
}

after={
    'rows':int(len(df)),
    'columns':int(df.shape[1]),
    'duplicates_full':int(df.duplicated().sum()),
    'duplicate_ticket_ids':int(df.duplicated(subset=['Ticket_ID']).sum()),
    'missing':{c:int(v) for c,v in df.isna().sum().items() if int(v)>0}
}

# Outlier profile based on observed resolution distribution; retain valid business outliers.
res_vals=df['Resolution_Time_Hours'].dropna()
q1,q3=np.percentile(res_vals,[25,75]); iqr=q3-q1; threshold=q3+1.5*iqr
outlier_count=int((res_vals>threshold).sum())

metrics={'before':before,'after':after,'validation':validation,
         'controlled_issue_counts':{'invalid_created_time':invalid_created_time,'invalid_csat_detected':invalid_csat,'missing_technician_before_imputation':missing_tech_before,'invalid_resolution_codes':invalid_resolution_codes,'resolution_outliers_flagged_not_deleted':outlier_count,'outlier_threshold_hours':round(float(threshold),2)}}
(REPORTS/'data_quality_metrics.json').write_text(json.dumps(metrics,indent=2,default=str),encoding='utf-8')

lines=['# Data Quality Report','',
       'The raw ticket file intentionally contains controlled quality issues. Cleaning preserves useful records and applies documented business rules rather than deleting all imperfect rows.','',
       '## Record Counts','',
       f"- Raw records: **{before['rows']:,}**",f"- Cleaned records: **{after['rows']:,}**",f"- Raw columns: **{before['columns']}**",f"- Cleaned columns (including engineered fields): **{after['columns']}**",'',
       '## Duplicates','',f"- Duplicate Ticket_ID rows before cleaning: **{before['duplicate_ticket_ids']:,}**",f"- Duplicate Ticket_ID rows after cleaning: **{after['duplicate_ticket_ids']:,}**",'',
       '## Missing Values Before Cleaning','']
for c,v in before['missing'].items(): lines.append(f'- {c}: {v:,}')
lines+=['','## Missing Values After Cleaning','']
for c,v in after['missing'].items(): lines.append(f'- {c}: {v:,}')
lines+=['','## Cleaning / Transformation Decisions','',
        '- Removed duplicate ticket IDs while retaining the first source record.',
        '- Trimmed extra spaces and standardized category, priority, status, channel and reopen values.',
        '- Parsed both ISO and day-first date formats.',
        '- Replaced raw SLA target values with the configurable priority policy from `sla_policies.csv`.',
        '- Imputed missing technician names from the most common Category + Location assignment, then Category fallback; retained `Unassigned` only if no defensible mapping existed.',
        '- Invalid CSAT values outside 1–5 were converted to missing. Legitimate non-response CSAT values were not imputed.',
        '- Invalid resolution-code text was preserved as `Other / Unclassified` rather than dropping the ticket.',
        '- Recomputed SLA status logically from resolution time for resolved tickets and current age for active tickets.',
        '- Added SLA_Breached, SLA_Remaining_Hours, resolution bands, ticket age, aging bands, and date/time features.',
        '- Resolution-time outliers were flagged using the IQR method and retained because long-running incidents can be valid operational cases.','',
        '## Validation Checks','']
for k,v in validation.items(): lines.append(f'- **{k}:** {v}')
lines+=['','## Outliers','',f'- IQR-based long-resolution threshold: **{threshold:.2f} hours**',f'- Valid tickets above threshold retained: **{outlier_count:,}**','',
        '## Important Missing-Value Interpretation','',
        '- `Resolved_Date`, `Closed_Date`, `Resolution_Time_Hours`, and `Resolved_Timestamp` are expected to be missing for active or cancelled tickets.',
        '- `Customer_Satisfaction` is expected to be missing when a survey was not returned; missing CSAT is not automatically a data error.',
        '- `Asset_ID` can legitimately be missing for account/access/password tickets that are not tied to a specific physical asset.']
(REPORTS/'data_quality_report.md').write_text('\n'.join(lines),encoding='utf-8')

print('Cleaned rows:',len(df),'columns:',df.shape[1])
print('Validation:',validation)
print('Outliers retained:',outlier_count,'threshold hours:',round(float(threshold),2))
