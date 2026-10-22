from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'/'processed'
E=ROOT/'reports'/'exports'
C=ROOT/'reports'/'charts'
C.mkdir(parents=True,exist_ok=True)

T=pd.read_csv(D/'02_cleaned_tickets.csv',parse_dates=['Created_Timestamp'])
monthly=pd.read_csv(E/'monthly_analysis.csv',parse_dates=['Month'])
tech=pd.read_csv(E/'technician_analysis.csv')
category=pd.read_csv(E/'category_analysis.csv')
dep=pd.read_csv(E/'department_analysis.csv')
loc=pd.read_csv(E/'location_analysis.csv')
backlog=pd.read_csv(E/'backlog_aging.csv')
pareto=pd.read_csv(E/'pareto_category_analysis.csv')
channel=pd.read_csv(E/'channel_analysis.csv')
csat_cat=pd.read_csv(E/'csat_by_category.csv')
active=T['Status'].isin(['Open','Assigned','In Progress','Pending','Reopened'])


def finish(fig,ax,title,ylabel=None,xlabel=None,rot=45):
    ax.set_title(title)
    if ylabel: ax.set_ylabel(ylabel)
    if xlabel: ax.set_xlabel(xlabel)
    ax.grid(axis='y',alpha=.2)
    ax.tick_params(axis='x',rotation=rot)
    fig.tight_layout()

def save_bar(series,title,filename,ylabel='Tickets',horizontal=False):
    fig,ax=plt.subplots(figsize=(10,6))
    if horizontal: series.sort_values().plot(kind='barh',ax=ax)
    else: series.plot(kind='bar',ax=ax)
    finish(fig,ax,title,ylabel,rot=45)
    fig.savefig(C/filename,dpi=150); plt.close(fig)

def save_line(df,x,y,title,filename,ylabel):
    fig,ax=plt.subplots(figsize=(10,6))
    ax.plot(df[x],df[y],marker='o',markersize=3)
    finish(fig,ax,title,ylabel,rot=45)
    fig.savefig(C/filename,dpi=150); plt.close(fig)

save_line(monthly,'Month','Tickets','Monthly Ticket Volume','01_monthly_ticket_volume.png','Tickets')
save_line(monthly,'Month','SLA_Compliance_%','Monthly SLA Compliance','02_monthly_sla_compliance.png','Compliance %')
save_line(monthly,'Month','SLA_Breaches','Monthly SLA Breaches','03_monthly_sla_breaches.png','Breaches')
save_bar(category.set_index('Category')['Tickets'],'Tickets by Category','04_tickets_by_category.png',horizontal=True)
save_bar(T['Priority'].value_counts().reindex(['Critical','High','Medium','Low']),'Tickets by Priority','05_tickets_by_priority.png')
save_bar(dep.set_index('Department')['Tickets'],'Tickets by Department','06_tickets_by_department.png',horizontal=True)
save_bar(loc.set_index('Location')['Tickets'],'Tickets by Location','07_tickets_by_location.png')
save_bar(category.set_index('Category')['Avg_Resolution_Hours'],'Average Resolution Time by Category','08_resolution_time_by_category.png','Hours',True)
save_bar(T.groupby('Priority')['Resolution_Time_Hours'].mean().reindex(['Critical','High','Medium','Low']),'Average Resolution Time by Priority','09_resolution_time_by_priority.png','Hours')
save_bar(tech.set_index('Assigned_Technician')['Tickets_Assigned'].nlargest(15),'Technician Workload – Top 15','10_technician_workload.png','Tickets',True)
save_bar(tech.set_index('Assigned_Technician')['SLA_Compliance_%'].nlargest(15),'Technician SLA Compliance – 15 Highest Observed','11_technician_sla_compliance.png','Compliance %',True)
save_bar(T['Status'].value_counts(),'Ticket Status Distribution','12_ticket_status_distribution.png')
save_line(monthly,'Month','Reopened_Tickets','Reopened Ticket Trend','13_reopened_ticket_trend.png','Reopened Tickets')
save_bar(T.loc[active,'Ticket_Age_Band'].value_counts().reindex(['0–4 Hours','4–8 Hours','8–24 Hours','1–3 Days','3–7 Days','7+ Days']).fillna(0),'Current Backlog Aging Distribution','14_ticket_aging_distribution.png')
save_bar(csat_cat.set_index('Category')['Avg_CSAT'],'Customer Satisfaction by Category','15_csat_by_category.png','Average CSAT',True)

fig,ax=plt.subplots(figsize=(10,6))
T['Resolution_Time_Hours'].dropna().clip(upper=T['Resolution_Time_Hours'].quantile(.99)).plot(kind='hist',bins=30,ax=ax)
finish(fig,ax,'Resolution Time Distribution (capped at 99th percentile)','Ticket Count','Hours',0)
fig.savefig(C/'16_resolution_time_distribution.png',dpi=150); plt.close(fig)

fig,ax=plt.subplots(figsize=(10,6))
ax.bar(pareto['Category'],pareto['Tickets'])
ax2=ax.twinx(); ax2.plot(pareto['Category'],pareto['Cumulative_%'],marker='o')
ax.set_ylabel('Tickets'); ax2.set_ylabel('Cumulative %'); ax.set_title('Pareto Analysis of Incident Categories')
ax.tick_params(axis='x',rotation=45); ax.grid(axis='y',alpha=.2); fig.tight_layout()
fig.savefig(C/'17_pareto_category_analysis.png',dpi=150); plt.close(fig)

save_bar(channel.set_index('Channel')['Tickets'],'Channel-wise Ticket Volume','18_channel_ticket_volume.png')
save_line(monthly,'Month','Avg_Resolution_Hours','Monthly Average Resolution Time','19_monthly_resolution_time.png','Hours')
save_line(monthly,'Month','Backlog','Month-End Backlog Trend','20_backlog_trend.png','Tickets')
save_bar(T['Created_Day_Name'].value_counts().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),'Ticket Volume by Day of Week','21_day_of_week_volume.png')
save_bar(T.groupby('Created_Hour')['Ticket_ID'].count(),'Ticket Volume by Hour','22_hourly_ticket_volume.png')

print('Charts created:',len(list(C.glob('*.png'))))
