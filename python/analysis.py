from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'/'processed'
R=ROOT/'reports'
E=R/'exports'
E.mkdir(parents=True,exist_ok=True)

T=pd.read_csv(D/'02_cleaned_tickets.csv',parse_dates=['Created_Date','Resolved_Date','Closed_Date','Created_Timestamp','Resolved_Timestamp'])
TECH=pd.read_csv(D/'technicians.csv')
ASSETS=pd.read_csv(D/'assets.csv')
EMP=pd.read_csv(D/'employees.csv')
AS_OF=pd.Timestamp('2026-12-31 23:59:59')
active_status=['Open','Assigned','In Progress','Pending','Reopened']
active=T['Status'].isin(active_status)
measurable=T['SLA_Status'].isin(['Met','Breached'])
resolved=T['Resolution_Time_Hours'].notna()

# ---------------- KPIs ----------------
total=len(T)
status_counts=T['Status'].value_counts()
sla_compliance=100*T.loc[measurable,'SLA_Status'].eq('Met').mean()
sla_breach=100*T.loc[measurable,'SLA_Status'].eq('Breached').mean()
reopen_pct=100*T['Reopened'].eq('Yes').mean()
backlog=int(active.sum())
resolution=T.loc[resolved,'Resolution_Time_Hours']
active_age=T.loc[active,'Ticket_Age_Hours']
csat=T['Customer_Satisfaction'].dropna()
kpis={
    'Total Tickets':int(total),
    'Open Tickets':int(status_counts.get('Open',0)+status_counts.get('Assigned',0)+status_counts.get('In Progress',0)+status_counts.get('Pending',0)+status_counts.get('Reopened',0)),
    'Closed Tickets':int(status_counts.get('Closed',0)),
    'Resolved Tickets':int(status_counts.get('Resolved',0)),
    'Cancelled Tickets':int(status_counts.get('Cancelled',0)),
    'Reopened Tickets':int(T['Reopened'].eq('Yes').sum()),
    'SLA Compliance %':round(float(sla_compliance),2),
    'SLA Breach %':round(float(sla_breach),2),
    'Average Resolution Time Hours':round(float(np.mean(resolution)),2),
    'Median Resolution Time Hours':round(float(np.median(resolution)),2),
    'Min Resolution Time Hours':round(float(np.min(resolution)),2),
    'Max Resolution Time Hours':round(float(np.max(resolution)),2),
    '95th Percentile Resolution Time Hours':round(float(np.percentile(resolution,95)),2),
    'Average First Response Minutes':round(float(np.mean(T['First_Response_Minutes'])),2),
    'Average Active Ticket Age Hours':round(float(np.mean(active_age)),2),
    'Average Customer Satisfaction':round(float(np.mean(csat)),2),
    'Total SLA Breaches':int(T['SLA_Status'].eq('Breached').sum()),
    'Critical Ticket Count':int(T['Priority'].eq('Critical').sum()),
    'High Priority Ticket Count':int(T['Priority'].eq('High').sum()),
    'Medium Priority Ticket Count':int(T['Priority'].eq('Medium').sum()),
    'Low Priority Ticket Count':int(T['Priority'].eq('Low').sum()),
    'Reopened Ticket %':round(float(reopen_pct),2),
    'Current Backlog':backlog
}
pd.DataFrame({'KPI':list(kpis),'Value':list(kpis.values())}).to_csv(E/'kpi_summary.csv',index=False)

# ---------------- SLA analysis ----------------
def group_sla(cols):
    g=T.groupby(cols,dropna=False).agg(
        Tickets=('Ticket_ID','nunique'),
        SLA_Breaches=('SLA_Breached','sum'),
        Avg_Resolution_Hours=('Resolution_Time_Hours','mean'),
        Median_Resolution_Hours=('Resolution_Time_Hours','median'),
        Avg_Response_Minutes=('First_Response_Minutes','mean'),
        Avg_CSAT=('Customer_Satisfaction','mean')
    ).reset_index()
    denom=T[T['SLA_Status'].isin(['Met','Breached'])].groupby(cols,dropna=False)['Ticket_ID'].count().rename('SLA_Measured').reset_index()
    met=T[T['SLA_Status'].eq('Met')].groupby(cols,dropna=False)['Ticket_ID'].count().rename('SLA_Met').reset_index()
    g=g.merge(denom,on=cols,how='left').merge(met,on=cols,how='left').fillna({'SLA_Measured':0,'SLA_Met':0})
    g['SLA_Compliance_%']=np.where(g['SLA_Measured']>0,g['SLA_Met']/g['SLA_Measured']*100,np.nan)
    g['SLA_Breach_Rate_%']=np.where(g['SLA_Measured']>0,g['SLA_Breaches']/g['SLA_Measured']*100,np.nan)
    return g

sla_priority=group_sla(['Priority']).sort_values('SLA_Breach_Rate_%',ascending=False)
sla_category=group_sla(['Category']).sort_values('SLA_Breaches',ascending=False)
sla_department=group_sla(['Department']).sort_values('SLA_Breach_Rate_%',ascending=False)
sla_priority.to_csv(E/'sla_by_priority.csv',index=False)
sla_category.to_csv(E/'sla_by_category.csv',index=False)
sla_department.to_csv(E/'sla_by_department.csv',index=False)

# ---------------- technician analysis ----------------
tech=T.groupby(['Technician_ID','Assigned_Technician'],dropna=False).agg(
    Tickets_Assigned=('Ticket_ID','nunique'),
    Tickets_Resolved=('Resolution_Time_Hours','count'),
    Average_Resolution_Time=('Resolution_Time_Hours','mean'),
    Median_Resolution_Time=('Resolution_Time_Hours','median'),
    Average_Response_Time=('First_Response_Minutes','mean'),
    SLA_Breaches=('SLA_Breached','sum'),
    Reopened_Tickets=('Reopened',lambda x:(x=='Yes').sum()),
    Customer_Satisfaction=('Customer_Satisfaction','mean'),
    Current_Backlog=('Status',lambda x:x.isin(active_status).sum())
).reset_index()
tech_sla=T[T['SLA_Status'].isin(['Met','Breached'])].groupby('Technician_ID')['SLA_Status'].apply(lambda x:(x=='Met').mean()*100).rename('SLA_Compliance_%').reset_index()
tech=tech.merge(tech_sla,on='Technician_ID',how='left').merge(TECH[['Technician_ID','Team','Experience_Level','Location']],on='Technician_ID',how='left')
tech['Workload_Share_%']=tech['Tickets_Assigned']/tech['Tickets_Assigned'].sum()*100
tech['Resolution_Time_Rank']=tech['Average_Resolution_Time'].rank(method='dense',ascending=True)
tech.to_csv(E/'technician_analysis.csv',index=False)

# ---------------- category / department / location / channel ----------------
category=group_sla(['Category']).sort_values('Tickets',ascending=False)
department=group_sla(['Department']).sort_values('Tickets',ascending=False)
location=group_sla(['Location']).sort_values('Tickets',ascending=False)
channel=T.groupby('Channel').agg(Tickets=('Ticket_ID','nunique'),Avg_Response_Minutes=('First_Response_Minutes','mean'),Avg_Resolution_Hours=('Resolution_Time_Hours','mean'),SLA_Breaches=('SLA_Breached','sum'),Avg_CSAT=('Customer_Satisfaction','mean')).reset_index().sort_values('Tickets',ascending=False)
category.to_csv(E/'category_analysis.csv',index=False)
department.to_csv(E/'department_analysis.csv',index=False)
location.to_csv(E/'location_analysis.csv',index=False)
channel.to_csv(E/'channel_analysis.csv',index=False)

# ---------------- backlog / aging ----------------
backlog_df=T[active].copy()
backlog_summary=backlog_df.groupby(['Priority','Ticket_Age_Band']).agg(Tickets=('Ticket_ID','nunique'),Average_Age_Hours=('Ticket_Age_Hours','mean'),SLA_Breaches=('SLA_Breached','sum')).reset_index()
backlog_summary.to_csv(E/'backlog_aging.csv',index=False)
for dim in ['Priority','Category','Department','Assigned_Technician']:
    (backlog_df.groupby(dim).agg(Backlog=('Ticket_ID','nunique'),Avg_Age_Hours=('Ticket_Age_Hours','mean'),SLA_Breaches=('SLA_Breached','sum')).reset_index().sort_values('Backlog',ascending=False)
     .to_csv(E/f'backlog_by_{dim.lower().replace(" ","_")}.csv',index=False))

# ---------------- monthly trends ----------------
T['Month']=T['Created_Timestamp'].dt.to_period('M').dt.to_timestamp()
months=pd.date_range('2025-01-01','2026-12-01',freq='MS')
monthly=T.groupby('Month').agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum'),Avg_Resolution_Hours=('Resolution_Time_Hours','mean'),Avg_Response_Minutes=('First_Response_Minutes','mean'),Avg_CSAT=('Customer_Satisfaction','mean'),Reopened_Tickets=('Reopened',lambda x:(x=='Yes').sum())).reindex(months).reset_index().rename(columns={'index':'Month'})
monthly_meas=T[T['SLA_Status'].isin(['Met','Breached'])].groupby('Month')['Ticket_ID'].count()
monthly_met=T[T['SLA_Status'].eq('Met')].groupby('Month')['Ticket_ID'].count()
monthly['SLA_Compliance_%']=[100*monthly_met.get(m,0)/monthly_meas.get(m,1) for m in monthly['Month']]
# Month-end backlog: unresolved if created by month-end and final resolution is absent or after month end; current Reopened is treated as active.
backlog_trend=[]
for m in months:
    end=m+pd.offsets.MonthEnd(1)+pd.Timedelta(hours=23,minutes=59,seconds=59)
    existed=T['Created_Timestamp']<=end
    unresolved_at_end=(T['Resolved_Timestamp'].isna() | (T['Resolved_Timestamp']>end))
    current_reopened=T['Status'].eq('Reopened') & existed
    cancelled=T['Status'].eq('Cancelled')
    backlog_trend.append(int((existed & (unresolved_at_end | current_reopened) & ~cancelled).sum()))
monthly['Backlog']=backlog_trend
monthly['MoM_Ticket_Growth_%']=monthly['Tickets'].pct_change()*100
monthly['YoY_Ticket_Growth_%']=monthly['Tickets'].pct_change(12)*100
monthly['Rolling_3M_Tickets']=monthly['Tickets'].rolling(3,min_periods=1).mean()
monthly['Prior_Month_Tickets']=monthly['Tickets'].shift(1)
monthly.to_csv(E/'monthly_analysis.csv',index=False)

# Quarterly / yearly / day patterns
T.groupby([T['Created_Timestamp'].dt.year.rename('Year'),T['Created_Timestamp'].dt.quarter.rename('Quarter')]).agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum')).reset_index().to_csv(E/'quarterly_analysis.csv',index=False)
T.groupby(T['Created_Timestamp'].dt.year.rename('Year')).agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum'),Avg_Resolution_Hours=('Resolution_Time_Hours','mean')).reset_index().to_csv(E/'yearly_analysis.csv',index=False)
dow=T.groupby('Created_Day_Name').agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum')).reset_index()
dow['Day_Order']=dow['Created_Day_Name'].map({'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5,'Saturday':6,'Sunday':7})
dow.sort_values('Day_Order').drop(columns='Day_Order').to_csv(E/'day_of_week_analysis.csv',index=False)
T.groupby('Created_Hour').agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum')).reset_index().to_csv(E/'hourly_analysis.csv',index=False)

# ---------------- CSAT and reopen analysis ----------------
csat_category=T.groupby('Category')['Customer_Satisfaction'].agg(['count','mean']).reset_index().rename(columns={'count':'Responses','mean':'Avg_CSAT'}).sort_values('Avg_CSAT')
csat_priority=T.groupby('Priority')['Customer_Satisfaction'].agg(['count','mean']).reset_index().rename(columns={'count':'Responses','mean':'Avg_CSAT'})
csat_tech=T.groupby(['Technician_ID','Assigned_Technician'])['Customer_Satisfaction'].agg(['count','mean']).reset_index().rename(columns={'count':'Responses','mean':'Avg_CSAT'})
csat_band=T.groupby('Resolution_Time_Band')['Customer_Satisfaction'].agg(['count','mean']).reset_index().rename(columns={'count':'Responses','mean':'Avg_CSAT'})
csat_dep=T.groupby('Department')['Customer_Satisfaction'].agg(['count','mean']).reset_index().rename(columns={'count':'Responses','mean':'Avg_CSAT'})
for name,dfx in [('category',csat_category),('priority',csat_priority),('technician',csat_tech),('resolution_band',csat_band),('department',csat_dep)]: dfx.to_csv(E/f'csat_by_{name}.csv',index=False)
csat_corr=float(T[['Resolution_Time_Hours','Customer_Satisfaction']].dropna().corr().iloc[0,1])

reopen=T.groupby('Category').agg(Tickets=('Ticket_ID','nunique'),Reopened=('Reopened',lambda x:(x=='Yes').sum())).reset_index(); reopen['Reopen_Rate_%']=100*reopen['Reopened']/reopen['Tickets']; reopen.sort_values('Reopen_Rate_%',ascending=False).to_csv(E/'reopen_by_category.csv',index=False)
for dim in ['Assigned_Technician','Priority','Department']:
    x=T.groupby(dim).agg(Tickets=('Ticket_ID','nunique'),Reopened=('Reopened',lambda s:(s=='Yes').sum())).reset_index(); x['Reopen_Rate_%']=100*x['Reopened']/x['Tickets']; x.sort_values('Reopen_Rate_%',ascending=False).to_csv(E/f'reopen_by_{dim.lower().replace(" ","_")}.csv',index=False)

# ---------------- Pareto ----------------
pareto=T.groupby('Category').size().rename('Tickets').sort_values(ascending=False).reset_index()
pareto['Share_%']=pareto['Tickets']/pareto['Tickets'].sum()*100
pareto['Cumulative_%']=pareto['Share_%'].cumsum()
pareto.to_csv(E/'pareto_category_analysis.csv',index=False)

# ---------------- asset incident analysis ----------------
asset_inc=T[T['Asset_ID'].notna()].merge(ASSETS,on='Asset_ID',how='left',suffixes=('','_Asset'))
asset_summary=asset_inc.groupby(['Asset_Type','Operating_System']).agg(Tickets=('Ticket_ID','nunique'),SLA_Breaches=('SLA_Breached','sum'),Avg_Resolution_Hours=('Resolution_Time_Hours','mean'),Reopened=('Reopened',lambda x:(x=='Yes').sum())).reset_index().sort_values('Tickets',ascending=False)
asset_summary.to_csv(E/'asset_incident_analysis.csv',index=False)

# ---------------- outliers ----------------
q1,q3=np.percentile(resolution,[25,75]); iqr=q3-q1; upper=q3+1.5*iqr
outliers=T[T['Resolution_Time_Hours']>upper][['Ticket_ID','Category','Priority','Assigned_Technician','Resolution_Time_Hours','SLA_Target_Hours','SLA_Status','Customer_Satisfaction']].sort_values('Resolution_Time_Hours',ascending=False)
outliers.to_csv(E/'resolution_time_outliers.csv',index=False)

# ---------------- dataset-derived insights ----------------
top_cat=category.iloc[0]
cat_breach=sla_category.sort_values('SLA_Breach_Rate_%',ascending=False).iloc[0]
top_dep=department.iloc[0]
dep_breach=sla_department.sort_values('SLA_Breach_Rate_%',ascending=False).iloc[0]
priority_breach=sla_priority.iloc[0]
priority_long=T.groupby('Priority')['Resolution_Time_Hours'].mean().sort_values(ascending=False)
peak_month=monthly.loc[monthly['Tickets'].idxmax()]
peak_breach_month=monthly.loc[monthly['SLA_Breaches'].idxmax()]
backlog_priority=backlog_df['Priority'].value_counts()
old_backlog=backlog_df[backlog_df['Ticket_Age_Hours']>168]
workload=tech.sort_values('Tickets_Assigned',ascending=False)
high_work=workload.iloc[0]
low_work=workload.iloc[-1]
reopen_cat=reopen.sort_values('Reopen_Rate_%',ascending=False).iloc[0]
low_csat=csat_category.iloc[0]
channel_top=channel.iloc[0]
pareto80=pareto[pareto['Cumulative_%']<=80]
if len(pareto80)<len(pareto): pareto80=pd.concat([pareto80,pareto.iloc[[len(pareto80)]]])
asset_top=asset_summary.iloc[0]
weekday=pd.read_csv(E/'day_of_week_analysis.csv').sort_values('Tickets',ascending=False).iloc[0]
yearly=pd.read_csv(E/'yearly_analysis.csv').set_index('Year')['Tickets']
yoy=float((yearly.get(2026,0)/yearly.get(2025,1)-1)*100)

insights=[
 f"1. {top_cat['Category']} generated the highest ticket volume with {int(top_cat['Tickets']):,} tickets ({100*top_cat['Tickets']/total:.1f}% of all tickets).",
 f"2. {cat_breach['Category']} had the highest category SLA breach rate at {cat_breach['SLA_Breach_Rate_%']:.1f}% among measurable tickets.",
 f"3. {top_dep['Department']} generated the most tickets with {int(top_dep['Tickets']):,} incidents.",
 f"4. {dep_breach['Department']} had the highest departmental SLA breach rate at {dep_breach['SLA_Breach_Rate_%']:.1f}%.",
 f"5. {priority_breach['Priority']} priority had the highest SLA breach rate at {priority_breach['SLA_Breach_Rate_%']:.1f}%.",
 f"6. {priority_long.index[0]} priority had the longest average resolution time at {priority_long.iloc[0]:.2f} hours; this is separate from its SLA target and breach rate.",
 f"7. SLA compliance across measurable tickets was {sla_compliance:.2f}%; {int(T['SLA_Status'].eq('Breached').sum()):,} tickets were classified as breached.",
 f"8. {peak_month['Month'].strftime('%b %Y')} had the highest ticket volume with {int(peak_month['Tickets']):,} tickets.",
 f"9. {peak_breach_month['Month'].strftime('%b %Y')} recorded the highest monthly SLA-breach count with {int(peak_breach_month['SLA_Breaches']):,} breaches.",
 f"10. Ticket volume changed by {yoy:.1f}% in 2026 versus 2025.",
 f"11. The current backlog is {backlog:,} tickets; {int(old_backlog.shape[0]):,} have aged more than 7 days.",
 f"12. {backlog_priority.index[0]} is the largest backlog priority with {int(backlog_priority.iloc[0]):,} active tickets.",
 f"13. Technician workload is intentionally uneven: {high_work['Assigned_Technician']} handled {int(high_work['Tickets_Assigned']):,} tickets while {low_work['Assigned_Technician']} handled {int(low_work['Tickets_Assigned']):,}.",
 f"14. {reopen_cat['Category']} had the highest category reopen rate at {reopen_cat['Reopen_Rate_%']:.2f}%.",
 f"15. Overall reopen rate was {reopen_pct:.2f}%.",
 f"16. Average CSAT was {np.mean(csat):.2f}/5 across {len(csat):,} survey responses.",
 f"17. {low_csat['Category']} had the lowest category average CSAT at {low_csat['Avg_CSAT']:.2f}/5 among returned surveys.",
 f"18. Resolution time and CSAT had a Pearson correlation of {csat_corr:.3f}; this is an association and does not prove that longer resolution time alone causes lower satisfaction.",
 f"19. {channel_top['Channel']} was the most-used support channel with {int(channel_top['Tickets']):,} tickets.",
 f"20. The categories needed to reach roughly 80% of incident volume are: {', '.join(pareto80['Category'].tolist())}.",
 f"21. {asset_top['Asset_Type']} / {asset_top['Operating_System']} generated the largest asset-linked incident combination with {int(asset_top['Tickets']):,} tickets.",
 f"22. {weekday['Created_Day_Name']} had the highest day-of-week ticket volume with {int(weekday['Tickets']):,} tickets across the two-year period.",
 f"23. Average resolution time was {np.mean(resolution):.2f} hours, median {np.median(resolution):.2f} hours, and the 95th percentile {np.percentile(resolution,95):.2f} hours, showing a long tail of difficult incidents."
]
(R/'business_insights.md').write_text('# Business Insights\n\n'+'\n'.join('- '+x for x in insights),encoding='utf-8')

# Recommendations tied to measured patterns.
recs=[
 f"Prioritize knowledge-base and self-service content for {top_cat['Category']} because it contributes the largest incident volume; automate repeatable subcategories where the resolution path is standardized.",
 f"Review escalation and diagnostic playbooks for {cat_breach['Category']} because it has the highest category SLA breach rate ({cat_breach['SLA_Breach_Rate_%']:.1f}%).",
 f"Create a focused SLA improvement plan for {dep_breach['Department']} tickets, including routing accuracy and dependency review, because this department has the highest measured breach rate.",
 f"Use staffing and shift planning around the observed peak period ({peak_month['Month'].strftime('%b %Y')}) and the highest-volume weekday ({weekday['Created_Day_Name']}) rather than assuming uniform demand.",
 f"Review the {int(old_backlog.shape[0]):,} backlog tickets older than 7 days through an aging exception queue with owner, next action and escalation date.",
 f"Balance technician assignment rules because workload ranges from {int(low_work['Tickets_Assigned']):,} to {int(high_work['Tickets_Assigned']):,} tickets; compare workload together with complexity, SLA and CSAT before changing staffing.",
 f"Investigate recurring fixes in {reopen_cat['Category']} because it has the highest reopen rate; use root-cause/problem-management reviews for repeat incidents rather than only closing individual tickets.",
 f"Monitor CSAT by resolution-time band and category; the observed resolution-time/CSAT correlation is {csat_corr:.3f}, so use it as an investigative signal rather than a causal conclusion.",
 f"Maintain automated SLA timers using the configurable Critical/High/Medium/Low policy table and alert before SLA_Remaining_Hours becomes negative.",
 f"Use the Pareto category view to focus service-improvement work on the small set of categories accounting for roughly 80% of incident volume before optimizing low-volume categories."
]
(R/'business_recommendations.md').write_text('# Business Recommendations\n\n'+'\n'.join('- '+x for x in recs),encoding='utf-8')

summary={'as_of':'2026-12-31 23:59:59','kpis':kpis,'csat_resolution_correlation':round(csat_corr,4),'resolution_outlier_threshold_hours':round(float(upper),2),'insight_count':len(insights),'recommendation_count':len(recs)}
(R/'analysis_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

print(json.dumps(kpis,indent=2))
print('CSAT-resolution correlation:',round(csat_corr,4))
print('Insights:',len(insights),'Recommendations:',len(recs))
