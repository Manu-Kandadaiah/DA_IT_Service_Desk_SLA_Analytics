from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20260924
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROC = ROOT / 'data' / 'processed'
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp('2025-01-01')
END = pd.Timestamp('2026-12-31 23:59:59')
AS_OF = END
N_EMPLOYEES = 1500
N_TECHS = 25
N_ASSETS = 2500
N_TICKETS = 20000

first_names = ['Aarav','Aditya','Akash','Ananya','Anil','Anisha','Arjun','Asha','Bhavna','Deepak','Dev','Diya','Harish','Ishaan','Jaya','Kabir','Karthik','Kavya','Manoj','Meera','Naveen','Neha','Nikhil','Nisha','Pooja','Pranav','Rahul','Raj','Ravi','Riya','Rohan','Sanjay','Sneha','Suresh','Tanvi','Varun','Vikram','Vivek']
last_names = ['Bhat','Das','Desai','Gupta','Iyer','Joshi','Kapoor','Kulkarni','Kumar','Mehta','Menon','Nair','Patel','Rao','Reddy','Shah','Sharma','Shetty','Singh','Verma']
locations = ['Bengaluru','Chennai','Hyderabad','Mumbai','Delhi','Pune','Kochi']
departments = ['IT','HR','Finance','Sales','Marketing','Operations','Administration','Management','Customer Support','Engineering']
dep_weights = np.array([0.07,0.07,0.09,0.15,0.08,0.16,0.07,0.05,0.12,0.14])
dep_weights = dep_weights / dep_weights.sum()
job_titles = {
    'IT':['IT Administrator','System Analyst','IT Coordinator','Infrastructure Engineer'],
    'HR':['HR Executive','Recruiter','HR Analyst','HR Manager'],
    'Finance':['Accountant','Finance Analyst','Accounts Executive','Finance Manager'],
    'Sales':['Sales Executive','Account Manager','Sales Coordinator','Regional Sales Manager'],
    'Marketing':['Marketing Executive','Content Specialist','Marketing Analyst','Brand Coordinator'],
    'Operations':['Operations Executive','Production Planner','Operations Analyst','Shift Coordinator'],
    'Administration':['Admin Executive','Office Coordinator','Facility Coordinator','Admin Manager'],
    'Management':['Department Head','General Manager','Senior Manager','Director'],
    'Customer Support':['Support Executive','Customer Success Associate','Team Lead','Service Coordinator'],
    'Engineering':['Design Engineer','Project Engineer','QA Engineer','Production Engineer']
}

# ---------------- employees ----------------
employees=[]
used=set()
for i in range(1,N_EMPLOYEES+1):
    dep=rng.choice(departments,p=dep_weights)
    loc=rng.choice(locations,p=[0.30,0.14,0.13,0.13,0.11,0.11,0.08])
    name=f"{rng.choice(first_names)} {rng.choice(last_names)}"
    suffix=1
    base=name
    while name in used:
        suffix+=1; name=f"{base} {suffix}"
    used.add(name)
    join=pd.Timestamp('2016-01-01')+pd.Timedelta(days=int(rng.integers(0,3650)))
    if join>END: join=END-pd.Timedelta(days=30)
    employees.append([f'EMP{i:05d}',name,dep,loc,rng.choice(job_titles[dep]),join.date()])
employees_df=pd.DataFrame(employees,columns=['Employee_ID','Employee_Name','Department','Location','Job_Title','Joining_Date'])

# ---------------- technicians ----------------
teams=['Service Desk','Desktop Support','Network Support','Application Support','Security & Access']
team_probs=[0.36,0.24,0.14,0.16,0.10]
techs=[]
tech_perf={}; tech_weight={}; tech_team={}
for i in range(1,N_TECHS+1):
    team=teams[i-1] if i <= len(teams) else rng.choice(teams,p=team_probs)
    level=rng.choice(['Junior','Intermediate','Senior'],p=[0.28,0.47,0.25])
    perf_base={'Junior':1.16,'Intermediate':1.00,'Senior':0.84}[level]
    perf=float(np.clip(rng.normal(perf_base,0.10),0.65,1.35))
    weight=float(np.clip(rng.lognormal(mean=0,sigma=.35),0.45,1.9))
    loc=rng.choice(locations,p=[0.42,0.11,0.11,0.10,0.10,0.09,0.07])
    name=f"{rng.choice(first_names)} {rng.choice(last_names)}"
    tid=f'TECH{i:03d}'
    join=pd.Timestamp('2015-01-01')+pd.Timedelta(days=int(rng.integers(0,3650)))
    techs.append([tid,name,team,level,loc,join.date()])
    tech_perf[tid]=perf; tech_weight[tid]=weight; tech_team[tid]=team
tech_df=pd.DataFrame(techs,columns=['Technician_ID','Technician_Name','Team','Experience_Level','Location','Joining_Date'])

# ---------------- assets ----------------
asset_types=['Laptop','Desktop','Monitor','Printer','Mobile','Network Device']
asset_probs=[0.42,0.20,0.16,0.08,0.09,0.05]
os_by_type={
    'Laptop':['Windows 10','Windows 11'],
    'Desktop':['Windows 10','Windows 11'],
    'Monitor':['N/A'],
    'Printer':['Embedded'],
    'Mobile':['Android','iOS'],
    'Network Device':['Network OS','Windows Server 2022']
}
asset_models={
    'Laptop':['AsterBook Pro 14','Vertex Note 15','Nivara Flex 13','Creston WorkBook 15'],
    'Desktop':['Orbin DeskPro','Tekvora OfficeStation','Aster MicroTower'],
    'Monitor':['Lumexa View 24','Vertex Panel 27','Creston OfficeView 22'],
    'Printer':['Nivara LaserJet M4','Orbin PrintPro','Aster LabelJet'],
    'Mobile':['Velora M12','Aster M8','Nivara Pocket Pro'],
    'Network Device':['Vertex EdgeSwitch','Orbin SecureRouter','Tekvora AccessPoint']
}
emp_records=employees_df.to_dict('records')
assets=[]
for i in range(1,N_ASSETS+1):
    emp=emp_records[int(rng.integers(0,len(emp_records)))]
    typ=rng.choice(asset_types,p=asset_probs)
    purchase=START-pd.Timedelta(days=int(rng.integers(30,2400)))
    warranty=purchase+pd.Timedelta(days=int(rng.choice([365,730,1095],p=[0.25,0.45,0.30])))
    status=rng.choice(['Active','Active','Active','Spare','Under Repair','Retired'],p=[0.27,0.27,0.27,0.07,0.07,0.05])
    assets.append([f'AST{i:05d}',typ,rng.choice(asset_models[typ]),rng.choice(os_by_type[typ]),emp['Department'],emp['Employee_ID'],purchase.date(),warranty.date(),status])
assets_df=pd.DataFrame(assets,columns=['Asset_ID','Asset_Type','Asset_Model','Operating_System','Department','Assigned_Employee','Purchase_Date','Warranty_End_Date','Asset_Status'])

# ---------------- categories / SLA ----------------
category_subs={
    'Hardware':['Laptop','Desktop','Keyboard','Mouse','Monitor','Docking Station'],
    'Software':['Installation','License','Crash','Performance','Configuration'],
    'Network':['Wi-Fi','LAN','Internet','DNS','Connectivity'],
    'Email/Outlook':['Outlook','Mailbox','Email Delivery','Password','Calendar'],
    'Access Management':['Active Directory','File Share','Application Access','Group Access'],
    'VPN':['Connection','Authentication','Client Configuration','Performance'],
    'Printer':['Print Queue','Driver','Paper Jam','Network Printer','Toner'],
    'Windows':['Windows Update','Login','Performance','Blue Screen','Configuration'],
    'Security':['Antivirus Alert','Phishing','Account Lock','Malware','Endpoint Compliance'],
    'Application':['ERP','CRM','Browser','Business Application','Database Client'],
    'Account/Password':['Password Reset','Account Locked','MFA','New Account','Password Expired']
}
cat_order=list(category_subs)
cat_probs=np.array([0.10,0.13,0.08,0.08,0.10,0.06,0.05,0.12,0.05,0.09,0.14])
cat_probs=cat_probs/cat_probs.sum()
cat_base_hours={'Hardware':14,'Software':11,'Network':10,'Email/Outlook':6,'Access Management':7,'VPN':8,'Printer':7,'Windows':12,'Security':10,'Application':14,'Account/Password':3.5}
cat_first_response={'Hardware':35,'Software':30,'Network':24,'Email/Outlook':20,'Access Management':22,'VPN':20,'Printer':28,'Windows':30,'Security':12,'Application':32,'Account/Password':10}
team_for_cat={'Hardware':'Desktop Support','Software':'Application Support','Network':'Network Support','Email/Outlook':'Service Desk','Access Management':'Security & Access','VPN':'Network Support','Printer':'Desktop Support','Windows':'Desktop Support','Security':'Security & Access','Application':'Application Support','Account/Password':'Service Desk'}
priority_targets={'Critical':4.0,'High':8.0,'Medium':24.0,'Low':48.0}
priority_probs={'Hardware':[0.015,0.16,0.58,0.245],'Software':[0.015,0.14,0.60,0.245],'Network':[0.035,0.23,0.55,0.185],
                'Email/Outlook':[0.01,0.12,0.60,0.27],'Access Management':[0.015,0.18,0.58,0.225],'VPN':[0.02,0.20,0.58,0.20],
                'Printer':[0.005,0.08,0.55,0.365],'Windows':[0.02,0.16,0.60,0.22],'Security':[0.05,0.28,0.50,0.17],
                'Application':[0.02,0.19,0.59,0.20],'Account/Password':[0.005,0.08,0.56,0.355]}
priority_list=['Critical','High','Medium','Low']
priority_factor={'Critical':0.36,'High':0.58,'Medium':1.0,'Low':1.28}
channels=['Email','Phone','Portal','Chat','Walk-in']
channel_probs=[0.24,0.16,0.37,0.17,0.06]

# Department bias toward categories
dep_category_boost={
    'IT':{'Network':1.4,'Security':1.3,'Windows':1.2},
    'HR':{'Account/Password':1.35,'Access Management':1.25,'Email/Outlook':1.2},
    'Finance':{'Application':1.35,'Access Management':1.2,'Email/Outlook':1.15},
    'Sales':{'VPN':1.4,'Email/Outlook':1.25,'Account/Password':1.2},
    'Marketing':{'Software':1.3,'Application':1.2,'Email/Outlook':1.15},
    'Operations':{'Hardware':1.25,'Printer':1.3,'Windows':1.15},
    'Administration':{'Printer':1.45,'Hardware':1.25},
    'Management':{'VPN':1.25,'Email/Outlook':1.2},
    'Customer Support':{'Application':1.3,'Account/Password':1.2,'Windows':1.15},
    'Engineering':{'Software':1.3,'Windows':1.25,'Hardware':1.2}
}

tech_by_team={t:tech_df.loc[tech_df['Team'].eq(t),'Technician_ID'].tolist() for t in teams}
tech_name_map=tech_df.set_index('Technician_ID')['Technician_Name'].to_dict()
asset_by_emp=assets_df.groupby('Assigned_Employee')['Asset_ID'].apply(list).to_dict()
asset_type_by_id=assets_df.set_index('Asset_ID')['Asset_Type'].to_dict()

# Date weights with monthly seasonality and weekday patterns
days=pd.date_range(START.normalize(),END.normalize(),freq='D')
month_factor={1:1.12,2:1.02,3:1.10,4:0.98,5:0.96,6:0.94,7:1.06,8:1.02,9:1.12,10:1.08,11:1.02,12:0.88}
day_w=np.array([month_factor[d.month] * (1.18 if d.dayofweek==0 else 1.10 if d.dayofweek==1 else 1.0 if d.dayofweek<5 else 0.42) * (1.07 if d.year==2026 else 1.0) for d in days])
day_w=day_w/day_w.sum()

# Ticket count per day used later as high-volume factor
chosen_days=rng.choice(days,size=N_TICKETS,p=day_w)
day_counts=pd.Series(chosen_days).value_counts()
q80=float(day_counts.quantile(.80))

resolution_codes=['Resolved - Configuration','Resolved - User Guidance','Resolved - Replacement','Resolved - Reset/Unlock','Resolved - Patch/Update','Resolved - Access Granted','Resolved - Network Fix','Resolved - Application Fix','Cancelled - Duplicate','Cancelled - No Longer Required']

def choose_category(dep):
    weights=cat_probs.copy()
    boosts=dep_category_boost.get(dep,{})
    for j,c in enumerate(cat_order): weights[j]*=boosts.get(c,1.0)
    weights/=weights.sum()
    return rng.choice(cat_order,p=weights)

def choose_hour():
    if rng.random()<0.88:
        hours=np.arange(8,19)
        w=np.array([0.04,0.07,0.10,0.12,0.12,0.10,0.11,0.10,0.09,0.08,0.07]); w=w/w.sum()
        return int(rng.choice(hours,p=w))
    return int(rng.choice(list(range(0,8))+list(range(19,24))))

def choose_tech(cat,loc):
    team=team_for_cat[cat]; ids=tech_by_team[team]
    weights=[]
    for tid in ids:
        loc_bonus=1.25 if tech_df.loc[tech_df.Technician_ID.eq(tid),'Location'].iloc[0]==loc else 1.0
        weights.append(tech_weight[tid]*loc_bonus)
    weights=np.array(weights); weights/=weights.sum()
    return rng.choice(ids,p=weights)

def description(cat,sub):
    templates=[
        f"User reported {sub.lower()} issue affecting normal work.",
        f"Unable to complete task due to {sub.lower()} problem.",
        f"Support requested for {cat.lower()} - {sub.lower()}.",
        f"Intermittent {sub.lower()} issue observed during business activity.",
        f"Employee requires assistance with {sub.lower()} in {cat.lower()}."
    ]
    return rng.choice(templates)

rows=[]
history=[]
sat_rows=[]
for i in range(N_TICKETS):
    emp=emp_records[int(rng.integers(0,len(emp_records)))]
    created_day=pd.Timestamp(chosen_days[i])
    hour=choose_hour(); minute=int(rng.integers(0,60)); second=int(rng.integers(0,60))
    created=created_day+pd.Timedelta(hours=hour,minutes=minute,seconds=second)
    dep=emp['Department']; loc=emp['Location']; cat=choose_category(dep); sub=rng.choice(category_subs[cat])
    priority=rng.choice(priority_list,p=priority_probs[cat]); sla=priority_targets[priority]
    tech=choose_tech(cat,loc)
    high_volume=day_counts.get(created_day,0)>=q80
    volume_factor=1.22 if high_volume else 1.0
    # Slightly longer around lunch/late afternoons and for remote channels
    time_factor=1.10 if hour in [12,13,17,18] else 1.0
    base=cat_base_hours[cat]*priority_factor[priority]*tech_perf[tech]*volume_factor*time_factor
    resolution=float(max(0.15,rng.lognormal(mean=np.log(max(base,0.2)),sigma=0.62)))
    # occasional vendor/dependency delays
    if rng.random() < {'Hardware':0.10,'Application':0.08,'Network':0.06}.get(cat,0.025):
        resolution*=rng.uniform(1.6,3.8)
    first_response=float(max(1,rng.lognormal(mean=np.log(cat_first_response[cat]),sigma=.55)*tech_perf[tech]*(1.20 if high_volume else 1.0)))
    first_response=min(first_response,720)
    # status behavior based on ticket age and closure probability
    age_days=(END-created).days
    if age_days <= 7:
        unresolved_prob=0.12
    elif age_days <= 30:
        unresolved_prob=0.045
    elif age_days <= 90:
        unresolved_prob=0.015
    elif age_days <= 180:
        unresolved_prob=0.002
    else:
        unresolved_prob=0.0002
    if high_volume:
        unresolved_prob += (0.012 if age_days <= 90 else 0.0003)
    cancelled=rng.random()<0.025
    unresolved=(not cancelled) and rng.random()<unresolved_prob
    reopened_flag=False
    reopen_current=False
    resolved_date=pd.NaT; closed_date=pd.NaT
    status='Closed'
    if cancelled:
        status='Cancelled'; resolution=np.nan; sla_status='Pending'; resolution_code=rng.choice(['Cancelled - Duplicate','Cancelled - No Longer Required'])
    elif unresolved:
        status=rng.choice(['Open','Assigned','In Progress','Pending'],p=[0.12,0.18,0.44,0.26])
        age=(AS_OF-created).total_seconds()/3600
        sla_status='Breached' if age>sla else 'Pending'
        resolution=np.nan; resolution_code='Pending Investigation'
    else:
        resolved_date=created+pd.Timedelta(hours=resolution)
        # Rarely push past dataset end -> unresolved instead
        if resolved_date>END:
            status='In Progress'; resolved_date=pd.NaT; resolution=np.nan
            age=(AS_OF-created).total_seconds()/3600; sla_status='Breached' if age>sla else 'Pending'; resolution_code='Pending Investigation'
        else:
            sla_status='Met' if resolution<=sla else 'Breached'
            reopened_flag=rng.random() < (0.035 + 0.025*(sla_status=='Breached') + 0.02*(cat in ['Application','Software','Windows']))
            if reopened_flag:
                reopen_at=resolved_date+pd.Timedelta(hours=float(rng.uniform(3,72)))
                reopen_age_days=(END-reopen_at).days if reopen_at<END else -1
                current_reopen_prob=0.22 if 0 <= reopen_age_days <= 14 else (0.035 if 14 < reopen_age_days <= 90 else 0.0002)
                if reopen_at<END and rng.random()<current_reopen_prob:
                    status='Reopened'; reopen_current=True; closed_date=pd.NaT
                    history.append([f'HIS{i+1:06d}-03',f'TKT{i+1:06d}',reopen_at,'Reopened','User reported recurrence'])
                else:
                    extra=float(rng.lognormal(mean=np.log(max(cat_base_hours[cat]*0.45,0.4)),sigma=.50))
                    final= min(END, reopen_at+pd.Timedelta(hours=extra))
                    resolution=(final-created).total_seconds()/3600
                    resolved_date=final
                    sla_status='Met' if resolution<=sla else 'Breached'
                    closed_date=min(END,final+pd.Timedelta(hours=float(rng.uniform(.5,20))))
                    status='Closed'
                    history.append([f'HIS{i+1:06d}-03',f'TKT{i+1:06d}',reopen_at,'Reopened','User reported recurrence'])
                    history.append([f'HIS{i+1:06d}-04',f'TKT{i+1:06d}',final,'Resolved','Resolved after reopen'])
            else:
                status=rng.choice(['Resolved','Closed'],p=[0.20,0.80])
                if status=='Closed': closed_date=min(END,resolved_date+pd.Timedelta(hours=float(rng.uniform(.25,24))))
            resolution_code=rng.choice(resolution_codes[:8])
    # Asset selection: issue-specific when possible
    emp_assets=asset_by_emp.get(emp['Employee_ID'],[])
    asset_id=None
    if emp_assets:
        preferred_types={
            'Hardware':['Laptop','Desktop','Monitor','Mobile'], 'Printer':['Printer'], 'Windows':['Laptop','Desktop'],
            'Network':['Laptop','Desktop','Network Device'], 'VPN':['Laptop','Desktop'], 'Software':['Laptop','Desktop'],
            'Application':['Laptop','Desktop'], 'Security':['Laptop','Desktop','Mobile'], 'Email/Outlook':['Laptop','Desktop','Mobile']
        }.get(cat,[])
        pref=[a for a in emp_assets if asset_type_by_id.get(a) in preferred_types]
        if pref: asset_id=rng.choice(pref)
        elif cat not in ['Account/Password','Access Management']: asset_id=rng.choice(emp_assets)
    channel=rng.choice(channels,p=channel_probs)
    # CSAT mostly on resolved/closed; lower with breaches/long resolution/reopen
    csat=np.nan
    if status in ['Resolved','Closed'] and rng.random()<0.78:
        expected=4.55 - (0.75 if sla_status=='Breached' else 0) - (0.45 if reopened_flag else 0) - (0.25 if resolution and resolution>48 else 0)
        csat=int(np.clip(round(rng.normal(expected,0.62)),1,5))
    ticket_id=f'TKT{i+1:06d}'
    rows.append([ticket_id,created.date(),created.strftime('%H:%M:%S'),resolved_date.date() if pd.notna(resolved_date) else None,
                 closed_date.date() if pd.notna(closed_date) else None,emp['Employee_ID'],emp['Employee_Name'],dep,loc,cat,sub,priority,status,tech_name_map[tech],channel,
                 asset_id,description(cat,sub),round(first_response,1),round(resolution,2) if pd.notna(resolution) else np.nan,sla,sla_status,
                 'Yes' if reopened_flag else 'No',resolution_code,csat])
    history.append([f'HIS{i+1:06d}-01',ticket_id,created,'Created','Ticket created'])
    if not cancelled:
        history.append([f'HIS{i+1:06d}-02',ticket_id,created+pd.Timedelta(minutes=float(first_response)),'Assigned',f'Assigned to {tech}'])
        if pd.notna(resolved_date) and not reopened_flag:
            history.append([f'HIS{i+1:06d}-03',ticket_id,resolved_date,'Resolved',resolution_code])
        if pd.notna(closed_date):
            history.append([f'HIS{i+1:06d}-05',ticket_id,closed_date,'Closed','Ticket closed'])
    if pd.notna(csat):
        sat_rows.append([f'SAT{i+1:06d}',ticket_id,int(csat),(closed_date if pd.notna(closed_date) else resolved_date)+pd.Timedelta(hours=float(rng.uniform(1,72)))])

cols=['Ticket_ID','Created_Date','Created_Time','Resolved_Date','Closed_Date','Employee_ID','Employee_Name','Department','Location','Category','Subcategory','Priority','Status','Assigned_Technician','Channel','Asset_ID','Description','First_Response_Minutes','Resolution_Time_Hours','SLA_Target_Hours','SLA_Status','Reopened','Resolution_Code','Customer_Satisfaction']
tickets=pd.DataFrame(rows,columns=cols)
history_df=pd.DataFrame(history,columns=['History_ID','Ticket_ID','Event_Timestamp','Event_Type','Event_Detail'])
satisfaction_df=pd.DataFrame(sat_rows,columns=['Survey_ID','Ticket_ID','CSAT_Score','Survey_Date'])

# ---------------- controlled data-quality issues in raw tickets ----------------
raw=tickets.copy()
# mixed date formats
for col in ['Created_Date','Resolved_Date','Closed_Date']:
    out=pd.to_datetime(raw[col],errors='coerce').dt.strftime('%Y-%m-%d').astype(object)
    valid=np.where(pd.notna(raw[col]))[0]
    n=max(1,int(len(valid)*0.012))
    for j in rng.choice(valid,size=min(n,len(valid)),replace=False):
        out.iloc[j]=pd.to_datetime(out.iloc[j]).strftime('%d/%m/%Y')
    raw[col]=out.where(pd.notna(raw[col]),np.nan)
# spaces / capitalization / typo categories
for col in ['Employee_Name','Category','Subcategory','Department','Location']:
    idx=rng.choice(raw.index,size=35,replace=False)
    raw.loc[idx,col]='  '+raw.loc[idx,col].astype(str)+' '
idx=rng.choice(raw.index,size=30,replace=False); raw.loc[idx,'Category']=raw.loc[idx,'Category'].str.lower()
idx=rng.choice(raw.index,size=18,replace=False); raw.loc[idx,'Category']='E-mail/Outlook'
idx=rng.choice(raw.index,size=18,replace=False); raw.loc[idx,'Priority']='Med'
idx=rng.choice(raw.index,size=20,replace=False); raw.loc[idx,'Channel']='e-mail'
idx=rng.choice(raw.index,size=16,replace=False); raw.loc[idx,'Status']=raw.loc[idx,'Status'].str.lower()
# missing technicians in assignable tickets
eligible_idx=raw.index[~raw['Status'].isin(['Cancelled'])]
idx=rng.choice(eligible_idx,size=130,replace=False); raw.loc[idx,'Assigned_Technician']=np.nan
# controlled missing CSAT among closed/resolved
eligible_idx=raw.index[raw['Status'].isin(['Closed','Resolved']) & raw['Customer_Satisfaction'].notna()]
idx=rng.choice(eligible_idx,size=min(160,len(eligible_idx)),replace=False); raw.loc[idx,'Customer_Satisfaction']=np.nan
# invalid CSAT and response text
idx=rng.choice(raw.index,size=12,replace=False); raw.loc[idx,'Customer_Satisfaction']=7
idx=rng.choice(raw.index,size=10,replace=False); raw.loc[idx,'Resolution_Code']='unknown value'
# duplicate tickets
raw=pd.concat([raw,raw.sample(90,random_state=SEED)],ignore_index=True)

raw.to_csv(RAW/'01_raw_tickets.csv',index=False)
employees_df.to_csv(PROC/'employees.csv',index=False)
tech_df.to_csv(PROC/'technicians.csv',index=False)
assets_df.to_csv(PROC/'assets.csv',index=False)
history_df.to_csv(PROC/'ticket_history.csv',index=False,date_format='%Y-%m-%d %H:%M:%S')
satisfaction_df.to_csv(PROC/'satisfaction.csv',index=False,date_format='%Y-%m-%d %H:%M:%S')

cat_rows=[]
for ci,cat in enumerate(cat_order,1):
    for si,sub in enumerate(category_subs[cat],1):
        cat_rows.append([f'CAT{ci:02d}-{si:02d}',cat,sub,team_for_cat[cat],cat_base_hours[cat]])
pd.DataFrame(cat_rows,columns=['Category_ID','Category','Subcategory','Default_Team','Baseline_Resolution_Hours']).to_csv(PROC/'ticket_categories.csv',index=False)
pd.DataFrame([[p,h] for p,h in priority_targets.items()],columns=['Priority','SLA_Target_Hours']).to_csv(PROC/'sla_policies.csv',index=False)
pd.DataFrame({'Department_ID':[f'DEP{i+1:02d}' for i in range(len(departments))],'Department':departments}).to_csv(PROC/'departments.csv',index=False)

print('Raw tickets:',len(raw),'unique ticket IDs:',raw.Ticket_ID.nunique())
print('Employees:',len(employees_df),'Technicians:',len(tech_df),'Assets:',len(assets_df))
print('History events:',len(history_df),'Satisfaction responses:',len(satisfaction_df))
