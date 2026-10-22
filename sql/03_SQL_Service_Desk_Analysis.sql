USE pi_it_service_desk;

-- 01. Total tickets
SELECT COUNT(*) AS Total_Tickets FROM tickets;

-- 02. Open/current backlog tickets
SELECT COUNT(*) AS Current_Backlog
FROM tickets WHERE Status IN ('Open','Assigned','In Progress','Pending','Reopened');

-- 03. Closed tickets
SELECT COUNT(*) AS Closed_Tickets FROM tickets WHERE Status='Closed';

-- 04. Resolved tickets
SELECT COUNT(*) AS Resolved_Tickets FROM tickets WHERE Status='Resolved';

-- 05. SLA compliance and breach rate
SELECT ROUND(100*AVG(CASE WHEN SLA_Status='Met' THEN 1 ELSE 0 END),2) AS SLA_Compliance_Pct,
       ROUND(100*AVG(CASE WHEN SLA_Status='Breached' THEN 1 ELSE 0 END),2) AS SLA_Breach_Pct
FROM tickets WHERE SLA_Status IN ('Met','Breached');

-- 06. Total SLA breaches
SELECT COUNT(*) AS SLA_Breaches FROM tickets WHERE SLA_Status='Breached';

-- 07. Ticket volume by category
SELECT c.Category,COUNT(*) AS Tickets
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
GROUP BY c.Category ORDER BY Tickets DESC;

-- 08. Category SLA breach rate
SELECT c.Category,COUNT(*) AS Measured_Tickets,
       SUM(t.SLA_Breached) AS SLA_Breaches,
       ROUND(100*AVG(t.SLA_Breached),2) AS SLA_Breach_Rate_Pct
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
WHERE t.SLA_Status IN ('Met','Breached')
GROUP BY c.Category ORDER BY SLA_Breach_Rate_Pct DESC;

-- 09. Subcategory volume with HAVING threshold
SELECT c.Category,c.Subcategory,COUNT(*) AS Tickets
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
GROUP BY c.Category,c.Subcategory
HAVING COUNT(*) >= 100
ORDER BY Tickets DESC;

-- 10. Priority analysis
SELECT Priority,COUNT(*) AS Tickets,
       ROUND(AVG(Resolution_Time_Hours),2) AS Avg_Resolution_Hours,
       SUM(SLA_Breached) AS Breaches
FROM tickets GROUP BY Priority ORDER BY FIELD(Priority,'Critical','High','Medium','Low');

-- 11. Priority SLA compliance
SELECT Priority,
       ROUND(100*AVG(CASE WHEN SLA_Status='Met' THEN 1 ELSE 0 END),2) AS SLA_Compliance_Pct
FROM tickets WHERE SLA_Status IN ('Met','Breached')
GROUP BY Priority ORDER BY SLA_Compliance_Pct;

-- 12. Department ticket volume
SELECT d.Department_Name,COUNT(*) AS Tickets
FROM tickets t JOIN employees e ON e.Employee_ID=t.Employee_ID
JOIN departments d ON d.Department_ID=e.Department_ID
GROUP BY d.Department_Name ORDER BY Tickets DESC;

-- 13. Department SLA breach rate
SELECT d.Department_Name,COUNT(*) AS Measured_Tickets,SUM(t.SLA_Breached) AS Breaches,
       ROUND(100*AVG(t.SLA_Breached),2) AS Breach_Rate_Pct
FROM tickets t JOIN employees e ON e.Employee_ID=t.Employee_ID
JOIN departments d ON d.Department_ID=e.Department_ID
WHERE t.SLA_Status IN ('Met','Breached')
GROUP BY d.Department_Name ORDER BY Breach_Rate_Pct DESC;

-- 14. Monthly ticket volume
SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m') AS Month,COUNT(*) AS Tickets
FROM tickets GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m') ORDER BY Month;

-- 15. Yearly ticket volume
SELECT YEAR(Created_Timestamp) AS Year,COUNT(*) AS Tickets,
       SUM(SLA_Breached) AS SLA_Breaches
FROM tickets GROUP BY YEAR(Created_Timestamp) ORDER BY Year;

-- 16. Monthly SLA trend
SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m') AS Month,
       ROUND(100*AVG(CASE WHEN SLA_Status='Met' THEN 1 ELSE 0 END),2) AS SLA_Compliance_Pct,
       SUM(SLA_Breached) AS SLA_Breaches
FROM tickets WHERE SLA_Status IN ('Met','Breached')
GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m') ORDER BY Month;

-- 17. Monthly growth using LAG
WITH m AS (
  SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m-01') AS Month,COUNT(*) AS Tickets
  FROM tickets GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m-01')
), x AS (
  SELECT Month,Tickets,LAG(Tickets) OVER (ORDER BY Month) AS Previous_Month_Tickets FROM m
)
SELECT Month,Tickets,Previous_Month_Tickets,
       ROUND(100*(Tickets-Previous_Month_Tickets)/NULLIF(Previous_Month_Tickets,0),2) AS MoM_Growth_Pct
FROM x ORDER BY Month;

-- 18. Running ticket total
WITH m AS (
  SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m-01') AS Month,COUNT(*) AS Tickets
  FROM tickets GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m-01')
)
SELECT Month,Tickets,SUM(Tickets) OVER (ORDER BY Month) AS Running_Total
FROM m ORDER BY Month;

-- 19. Rolling three-month ticket average
WITH m AS (
  SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m-01') AS Month,COUNT(*) AS Tickets
  FROM tickets GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m-01')
)
SELECT Month,Tickets,
       ROUND(AVG(Tickets) OVER (ORDER BY Month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS Rolling_3M_Avg
FROM m ORDER BY Month;

-- 20. Resolution-time statistics
SELECT ROUND(AVG(Resolution_Time_Hours),2) AS Avg_Resolution_Hours,
       ROUND(MIN(Resolution_Time_Hours),2) AS Min_Resolution_Hours,
       ROUND(MAX(Resolution_Time_Hours),2) AS Max_Resolution_Hours
FROM tickets WHERE Resolution_Time_Hours IS NOT NULL;

-- 21. Approximate median resolution using window functions
WITH r AS (
 SELECT Resolution_Time_Hours,
        ROW_NUMBER() OVER (ORDER BY Resolution_Time_Hours) AS rn,
        COUNT(*) OVER () AS cnt
 FROM tickets WHERE Resolution_Time_Hours IS NOT NULL
)
SELECT ROUND(AVG(Resolution_Time_Hours),2) AS Median_Resolution_Hours
FROM r WHERE rn IN (FLOOR((cnt+1)/2), FLOOR((cnt+2)/2));

-- 22. Approximate 95th percentile resolution time
WITH r AS (
 SELECT Resolution_Time_Hours,
        ROW_NUMBER() OVER (ORDER BY Resolution_Time_Hours) AS rn,
        COUNT(*) OVER () AS cnt
 FROM tickets WHERE Resolution_Time_Hours IS NOT NULL
)
SELECT MIN(Resolution_Time_Hours) AS Approx_P95_Resolution_Hours
FROM r WHERE rn >= CEIL(cnt*0.95);

-- 23. Resolution time by category
SELECT c.Category,ROUND(AVG(t.Resolution_Time_Hours),2) AS Avg_Resolution_Hours,
       ROUND(MAX(t.Resolution_Time_Hours),2) AS Max_Resolution_Hours
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
GROUP BY c.Category ORDER BY Avg_Resolution_Hours DESC;

-- 24. Resolution-time bands
SELECT Resolution_Time_Band,COUNT(*) AS Tickets,
       ROUND(100*COUNT(*)/(SELECT COUNT(*) FROM tickets WHERE Resolution_Time_Hours IS NOT NULL),2) AS Share_Pct
FROM tickets WHERE Resolution_Time_Hours IS NOT NULL
GROUP BY Resolution_Time_Band ORDER BY MIN(Resolution_Time_Hours);

-- 25. Current backlog by priority
SELECT Priority,COUNT(*) AS Backlog,ROUND(AVG(Ticket_Age_Hours),2) AS Avg_Age_Hours
FROM tickets WHERE Status IN ('Open','Assigned','In Progress','Pending','Reopened')
GROUP BY Priority ORDER BY Backlog DESC;

-- 26. Current backlog by category
SELECT c.Category,COUNT(*) AS Backlog,ROUND(AVG(t.Ticket_Age_Hours),2) AS Avg_Age_Hours
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
WHERE t.Status IN ('Open','Assigned','In Progress','Pending','Reopened')
GROUP BY c.Category ORDER BY Backlog DESC;

-- 27. Aging tickets over 7 days
SELECT t.Ticket_ID,c.Category,t.Priority,t.Status,t.Ticket_Age_Hours,tech.Technician_Name
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
LEFT JOIN technicians tech ON tech.Technician_ID=t.Technician_ID
WHERE t.Status IN ('Open','Assigned','In Progress','Pending','Reopened') AND t.Ticket_Age_Hours>168
ORDER BY t.Ticket_Age_Hours DESC;

-- 28. Technician workload and performance
SELECT tech.Technician_Name,tech.Team,COUNT(t.Ticket_ID) AS Tickets_Assigned,
       SUM(CASE WHEN t.Resolution_Time_Hours IS NOT NULL THEN 1 ELSE 0 END) AS Tickets_Resolved,
       ROUND(AVG(t.Resolution_Time_Hours),2) AS Avg_Resolution_Hours,
       ROUND(AVG(t.First_Response_Minutes),2) AS Avg_Response_Minutes,
       SUM(t.SLA_Breached) AS SLA_Breaches,
       ROUND(AVG(t.Customer_Satisfaction),2) AS Avg_CSAT
FROM technicians tech LEFT JOIN tickets t ON t.Technician_ID=tech.Technician_ID
GROUP BY tech.Technician_ID,tech.Technician_Name,tech.Team
ORDER BY Tickets_Assigned DESC;

-- 29. Technician SLA compliance
SELECT tech.Technician_Name,
       COUNT(t.Ticket_ID) AS Measured_Tickets,
       ROUND(100*AVG(CASE WHEN t.SLA_Status='Met' THEN 1 ELSE 0 END),2) AS SLA_Compliance_Pct
FROM technicians tech JOIN tickets t ON t.Technician_ID=tech.Technician_ID
WHERE t.SLA_Status IN ('Met','Breached')
GROUP BY tech.Technician_ID,tech.Technician_Name
ORDER BY SLA_Compliance_Pct DESC;

-- 30. Technician workload rank (descriptive, not a 'best technician' score)
WITH x AS (
 SELECT Technician_ID,COUNT(*) Tickets_Assigned
 FROM tickets GROUP BY Technician_ID
)
SELECT tech.Technician_Name,x.Tickets_Assigned,
       DENSE_RANK() OVER (ORDER BY x.Tickets_Assigned DESC) AS Workload_Rank
FROM x JOIN technicians tech ON tech.Technician_ID=x.Technician_ID
ORDER BY Workload_Rank;

-- 31. Reopened ticket percentage
SELECT COUNT(*) AS Total_Tickets,
       SUM(CASE WHEN Reopened='Yes' THEN 1 ELSE 0 END) AS Reopened_Tickets,
       ROUND(100*AVG(CASE WHEN Reopened='Yes' THEN 1 ELSE 0 END),2) AS Reopen_Rate_Pct
FROM tickets;

-- 32. Reopen rate by category
SELECT c.Category,COUNT(*) Tickets,SUM(t.Reopened='Yes') Reopened,
       ROUND(100*AVG(t.Reopened='Yes'),2) Reopen_Rate_Pct
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
GROUP BY c.Category ORDER BY Reopen_Rate_Pct DESC;

-- 33. Customer satisfaction by category
SELECT c.Category,COUNT(t.Customer_Satisfaction) Responses,
       ROUND(AVG(t.Customer_Satisfaction),2) Avg_CSAT
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
GROUP BY c.Category HAVING Responses>0 ORDER BY Avg_CSAT;

-- 34. Customer satisfaction by resolution-time band
SELECT Resolution_Time_Band,COUNT(Customer_Satisfaction) Responses,
       ROUND(AVG(Customer_Satisfaction),2) Avg_CSAT
FROM tickets WHERE Customer_Satisfaction IS NOT NULL
GROUP BY Resolution_Time_Band ORDER BY MIN(Resolution_Time_Hours);

-- 35. Channel usage
SELECT Channel,COUNT(*) Tickets,ROUND(AVG(First_Response_Minutes),2) Avg_Response_Minutes,
       ROUND(AVG(Resolution_Time_Hours),2) Avg_Resolution_Hours
FROM tickets GROUP BY Channel ORDER BY Tickets DESC;

-- 36. Day-of-week pattern
SELECT DAYNAME(Created_Timestamp) Day_Name,COUNT(*) Tickets,
       SUM(SLA_Breached) SLA_Breaches
FROM tickets GROUP BY DAYNAME(Created_Timestamp)
ORDER BY FIELD(DAYNAME(Created_Timestamp),'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');

-- 37. Hourly ticket pattern
SELECT HOUR(Created_Timestamp) Created_Hour,COUNT(*) Tickets
FROM tickets GROUP BY HOUR(Created_Timestamp) ORDER BY Created_Hour;

-- 38. Pareto category analysis
WITH c AS (
 SELECT tc.Category,COUNT(*) Tickets
 FROM tickets t JOIN ticket_categories tc ON tc.Category_ID=t.Category_ID
 GROUP BY tc.Category
), p AS (
 SELECT Category,Tickets,
        100*Tickets/SUM(Tickets) OVER () AS Share_Pct,
        100*SUM(Tickets) OVER (ORDER BY Tickets DESC)/SUM(Tickets) OVER () AS Cumulative_Pct
 FROM c
)
SELECT * FROM p ORDER BY Tickets DESC;

-- 39. Asset-linked incidents by type and OS
SELECT a.Asset_Type,a.Operating_System,COUNT(*) Tickets,
       SUM(t.SLA_Breached) SLA_Breaches,
       ROUND(AVG(t.Resolution_Time_Hours),2) Avg_Resolution_Hours
FROM tickets t JOIN assets a ON a.Asset_ID=t.Asset_ID
GROUP BY a.Asset_Type,a.Operating_System ORDER BY Tickets DESC;

-- 40. Tickets without a CSAT response
SELECT COUNT(*) AS Tickets_Without_CSAT
FROM tickets WHERE Customer_Satisfaction IS NULL AND Status IN ('Resolved','Closed');

-- 41. SLA breaches during high-volume months vs overall monthly volume
WITH m AS (
 SELECT DATE_FORMAT(Created_Timestamp,'%Y-%m') Month,COUNT(*) Tickets,SUM(SLA_Breached) Breaches
 FROM tickets GROUP BY DATE_FORMAT(Created_Timestamp,'%Y-%m')
)
SELECT Month,Tickets,Breaches,
       RANK() OVER (ORDER BY Tickets DESC) AS Volume_Rank,
       RANK() OVER (ORDER BY Breaches DESC) AS Breach_Count_Rank
FROM m ORDER BY Month;

-- 42. Latest ticket per employee using ROW_NUMBER
WITH x AS (
 SELECT t.*,ROW_NUMBER() OVER (PARTITION BY Employee_ID ORDER BY Created_Timestamp DESC) rn
 FROM tickets t
)
SELECT Employee_ID,Ticket_ID,Created_Timestamp,Status,Priority FROM x WHERE rn=1;

-- 43. Technician comparison with COALESCE for no survey responses
SELECT tech.Technician_Name,COUNT(t.Ticket_ID) Tickets_Assigned,
       COALESCE(ROUND(AVG(t.Customer_Satisfaction),2),0) Avg_CSAT,
       COALESCE(SUM(t.SLA_Breached),0) SLA_Breaches
FROM technicians tech LEFT JOIN tickets t ON t.Technician_ID=tech.Technician_ID
GROUP BY tech.Technician_ID,tech.Technician_Name ORDER BY Tickets_Assigned DESC;

-- 44. Categories whose breach rate is above the overall breach rate (subquery)
SELECT c.Category,ROUND(100*AVG(t.SLA_Breached),2) Category_Breach_Rate
FROM tickets t JOIN ticket_categories c ON c.Category_ID=t.Category_ID
WHERE t.SLA_Status IN ('Met','Breached')
GROUP BY c.Category
HAVING AVG(t.SLA_Breached) > (
    SELECT AVG(SLA_Breached) FROM tickets WHERE SLA_Status IN ('Met','Breached')
)
ORDER BY Category_Breach_Rate DESC;
