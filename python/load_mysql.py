from pathlib import Path
import os
import pandas as pd
import mysql.connector

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'/'processed'
SQL=ROOT/'sql'
CFG={'host':os.getenv('MYSQL_HOST','localhost'),'port':int(os.getenv('MYSQL_PORT','3306')),'user':os.getenv('MYSQL_USER','root'),'password':os.getenv('MYSQL_PASSWORD','')}

conn=mysql.connector.connect(**CFG)
cur=conn.cursor()
script=(SQL/'schema.sql').read_text(encoding='utf-8')
for statement in [x.strip() for x in script.split(';') if x.strip()]:
    cur.execute(statement)
    if cur.with_rows: cur.fetchall()
cur.execute('USE pi_it_service_desk')

# Reference maps
dep=pd.read_csv(D/'departments.csv')
dep_map=dep.set_index('Department')['Department_ID'].to_dict()
cat=pd.read_csv(D/'ticket_categories.csv')
cat_map={(r.Category,r.Subcategory):r.Category_ID for r in cat.itertuples(index=False)}

# Departments
cur.executemany('INSERT INTO departments (Department_ID,Department_Name) VALUES (%s,%s)',[(r.Department_ID,r.Department) for r in dep.itertuples(index=False)])
# SLA policies
sla=pd.read_csv(D/'sla_policies.csv')
cur.executemany('INSERT INTO sla_policies (Priority,SLA_Target_Hours) VALUES (%s,%s)',[(r.Priority,float(r.SLA_Target_Hours)) for r in sla.itertuples(index=False)])
# Technicians
tech=pd.read_csv(D/'technicians.csv')
tech['Joining_Date']=pd.to_datetime(tech['Joining_Date'])
cur.executemany('INSERT INTO technicians VALUES (%s,%s,%s,%s,%s,%s)',[(r.Technician_ID,r.Technician_Name,r.Team,r.Experience_Level,r.Location,r.Joining_Date.date()) for r in tech.itertuples(index=False)])
# Employees
emp=pd.read_csv(D/'employees.csv'); emp['Joining_Date']=pd.to_datetime(emp['Joining_Date'])
cur.executemany('INSERT INTO employees VALUES (%s,%s,%s,%s,%s,%s)',[(r.Employee_ID,r.Employee_Name,dep_map[r.Department],r.Location,r.Job_Title,r.Joining_Date.date()) for r in emp.itertuples(index=False)])
# Assets
assets=pd.read_csv(D/'assets.csv'); assets['Purchase_Date']=pd.to_datetime(assets['Purchase_Date']); assets['Warranty_End_Date']=pd.to_datetime(assets['Warranty_End_Date'])
cur.executemany('INSERT INTO assets VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[(r.Asset_ID,r.Asset_Type,r.Asset_Model,r.Operating_System,dep_map.get(r.Department),r.Assigned_Employee,r.Purchase_Date.date(),r.Warranty_End_Date.date(),r.Asset_Status) for r in assets.itertuples(index=False)])
# Categories
cur.executemany('INSERT INTO ticket_categories VALUES (%s,%s,%s,%s,%s)',[(r.Category_ID,r.Category,r.Subcategory,r.Default_Team,float(r.Baseline_Resolution_Hours)) for r in cat.itertuples(index=False)])

# Tickets
t=pd.read_csv(D/'02_cleaned_tickets.csv')
for c in ['Created_Date','Resolved_Date','Closed_Date','Created_Timestamp','Resolved_Timestamp']:
    t[c]=pd.to_datetime(t[c],errors='coerce')
cols=['Ticket_ID','Created_Date','Created_Time','Created_Timestamp','Resolved_Date','Resolved_Timestamp','Closed_Date','Employee_ID','Category_ID','Priority','Status','Technician_ID','Channel','Asset_ID','Description','First_Response_Minutes','Resolution_Time_Hours','SLA_Target_Hours','SLA_Status','SLA_Breached','SLA_Remaining_Hours','Reopened','Resolution_Code','Customer_Satisfaction','Resolution_Time_Band','Ticket_Age_Hours','Ticket_Age_Band']
rows=[]
for r in t.itertuples(index=False):
    cat_id=cat_map[(r.Category,r.Subcategory)]
    vals=[r.Ticket_ID,r.Created_Date.date(),r.Created_Time,r.Created_Timestamp.to_pydatetime(),r.Resolved_Date.date() if pd.notna(r.Resolved_Date) else None,r.Resolved_Timestamp.to_pydatetime() if pd.notna(r.Resolved_Timestamp) else None,r.Closed_Date.date() if pd.notna(r.Closed_Date) else None,r.Employee_ID,cat_id,r.Priority,r.Status,r.Technician_ID if pd.notna(r.Technician_ID) else None,r.Channel,r.Asset_ID if pd.notna(r.Asset_ID) else None,r.Description,float(r.First_Response_Minutes),float(r.Resolution_Time_Hours) if pd.notna(r.Resolution_Time_Hours) else None,float(r.SLA_Target_Hours),r.SLA_Status,int(r.SLA_Breached),float(r.SLA_Remaining_Hours) if pd.notna(r.SLA_Remaining_Hours) else None,r.Reopened,r.Resolution_Code,float(r.Customer_Satisfaction) if pd.notna(r.Customer_Satisfaction) else None,r.Resolution_Time_Band,float(r.Ticket_Age_Hours) if pd.notna(r.Ticket_Age_Hours) else None,r.Ticket_Age_Band]
    rows.append(vals)
ph=','.join(['%s']*len(cols))
cur.executemany(f"INSERT INTO tickets ({','.join(cols)}) VALUES ({ph})",rows)

# History only for cleaned ticket IDs
hist=pd.read_csv(D/'ticket_history.csv'); hist['Event_Timestamp']=pd.to_datetime(hist['Event_Timestamp'])
valid=set(t['Ticket_ID'])
hist=hist[hist['Ticket_ID'].isin(valid)].drop_duplicates('History_ID')
cur.executemany('INSERT INTO ticket_history VALUES (%s,%s,%s,%s,%s)',[(r.History_ID,r.Ticket_ID,r.Event_Timestamp.to_pydatetime(),r.Event_Type,r.Event_Detail) for r in hist.itertuples(index=False)])
# Satisfaction
sat=pd.read_csv(D/'satisfaction.csv'); sat['Survey_Date']=pd.to_datetime(sat['Survey_Date']); sat=sat[sat['Ticket_ID'].isin(valid)].drop_duplicates('Ticket_ID')
cur.executemany('INSERT INTO satisfaction VALUES (%s,%s,%s,%s)',[(r.Survey_ID,r.Ticket_ID,int(r.CSAT_Score),r.Survey_Date.to_pydatetime()) for r in sat.itertuples(index=False)])

conn.commit(); cur.close(); conn.close()
print('MySQL load completed:',len(t),'tickets,',len(hist),'history events,',len(sat),'satisfaction responses')
