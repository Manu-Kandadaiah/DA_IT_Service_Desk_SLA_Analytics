CREATE DATABASE IF NOT EXISTS pi_it_service_desk;
USE pi_it_service_desk;

CREATE TABLE IF NOT EXISTS departments (
    Department_ID VARCHAR(20) PRIMARY KEY,
    Department_Name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sla_policies (
    Priority VARCHAR(20) PRIMARY KEY,
    SLA_Target_Hours DECIMAL(8,2) NOT NULL CHECK (SLA_Target_Hours > 0)
);

CREATE TABLE IF NOT EXISTS technicians (
    Technician_ID VARCHAR(20) PRIMARY KEY,
    Technician_Name VARCHAR(100) NOT NULL,
    Team VARCHAR(80) NOT NULL,
    Experience_Level VARCHAR(30) NOT NULL,
    Location VARCHAR(60) NOT NULL,
    Joining_Date DATE NOT NULL,
    INDEX idx_technician_team (Team),
    INDEX idx_technician_location (Location)
);

CREATE TABLE IF NOT EXISTS employees (
    Employee_ID VARCHAR(20) PRIMARY KEY,
    Employee_Name VARCHAR(100) NOT NULL,
    Department_ID VARCHAR(20) NOT NULL,
    Location VARCHAR(60) NOT NULL,
    Job_Title VARCHAR(100),
    Joining_Date DATE NOT NULL,
    CONSTRAINT fk_employee_department FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID),
    INDEX idx_employee_department (Department_ID),
    INDEX idx_employee_location (Location)
);

CREATE TABLE IF NOT EXISTS assets (
    Asset_ID VARCHAR(20) PRIMARY KEY,
    Asset_Type VARCHAR(50) NOT NULL,
    Asset_Model VARCHAR(100),
    Operating_System VARCHAR(80),
    Department_ID VARCHAR(20),
    Assigned_Employee VARCHAR(20),
    Purchase_Date DATE,
    Warranty_End_Date DATE,
    Asset_Status VARCHAR(30),
    CONSTRAINT fk_asset_department FOREIGN KEY (Department_ID) REFERENCES departments(Department_ID),
    CONSTRAINT fk_asset_employee FOREIGN KEY (Assigned_Employee) REFERENCES employees(Employee_ID),
    INDEX idx_asset_type (Asset_Type),
    INDEX idx_asset_employee (Assigned_Employee),
    INDEX idx_asset_status (Asset_Status)
);

CREATE TABLE IF NOT EXISTS ticket_categories (
    Category_ID VARCHAR(20) PRIMARY KEY,
    Category VARCHAR(80) NOT NULL,
    Subcategory VARCHAR(100) NOT NULL,
    Default_Team VARCHAR(80),
    Baseline_Resolution_Hours DECIMAL(8,2),
    UNIQUE KEY uq_category_subcategory (Category, Subcategory),
    INDEX idx_category_name (Category)
);

CREATE TABLE IF NOT EXISTS tickets (
    Ticket_ID VARCHAR(20) PRIMARY KEY,
    Created_Date DATE NOT NULL,
    Created_Time TIME NOT NULL,
    Created_Timestamp DATETIME NOT NULL,
    Resolved_Date DATE NULL,
    Resolved_Timestamp DATETIME NULL,
    Closed_Date DATE NULL,
    Employee_ID VARCHAR(20) NOT NULL,
    Category_ID VARCHAR(20) NOT NULL,
    Priority VARCHAR(20) NOT NULL,
    Status VARCHAR(30) NOT NULL,
    Technician_ID VARCHAR(20) NULL,
    Channel VARCHAR(30) NOT NULL,
    Asset_ID VARCHAR(20) NULL,
    Description VARCHAR(500),
    First_Response_Minutes DECIMAL(10,2),
    Resolution_Time_Hours DECIMAL(10,2) NULL,
    SLA_Target_Hours DECIMAL(8,2) NOT NULL,
    SLA_Status VARCHAR(20) NOT NULL,
    SLA_Breached TINYINT NOT NULL,
    SLA_Remaining_Hours DECIMAL(12,2) NULL,
    Reopened VARCHAR(5) NOT NULL,
    Resolution_Code VARCHAR(100),
    Customer_Satisfaction DECIMAL(3,1) NULL,
    Resolution_Time_Band VARCHAR(30),
    Ticket_Age_Hours DECIMAL(12,2),
    Ticket_Age_Band VARCHAR(30),
    CONSTRAINT fk_ticket_employee FOREIGN KEY (Employee_ID) REFERENCES employees(Employee_ID),
    CONSTRAINT fk_ticket_category FOREIGN KEY (Category_ID) REFERENCES ticket_categories(Category_ID),
    CONSTRAINT fk_ticket_priority FOREIGN KEY (Priority) REFERENCES sla_policies(Priority),
    CONSTRAINT fk_ticket_technician FOREIGN KEY (Technician_ID) REFERENCES technicians(Technician_ID),
    CONSTRAINT fk_ticket_asset FOREIGN KEY (Asset_ID) REFERENCES assets(Asset_ID),
    INDEX idx_ticket_created (Created_Timestamp),
    INDEX idx_ticket_priority (Priority),
    INDEX idx_ticket_status (Status),
    INDEX idx_ticket_sla (SLA_Status),
    INDEX idx_ticket_technician (Technician_ID),
    INDEX idx_ticket_employee (Employee_ID),
    INDEX idx_ticket_category (Category_ID)
);

CREATE TABLE IF NOT EXISTS ticket_history (
    History_ID VARCHAR(30) PRIMARY KEY,
    Ticket_ID VARCHAR(20) NOT NULL,
    Event_Timestamp DATETIME NOT NULL,
    Event_Type VARCHAR(40) NOT NULL,
    Event_Detail VARCHAR(250),
    CONSTRAINT fk_history_ticket FOREIGN KEY (Ticket_ID) REFERENCES tickets(Ticket_ID),
    INDEX idx_history_ticket_time (Ticket_ID, Event_Timestamp),
    INDEX idx_history_event (Event_Type)
);

CREATE TABLE IF NOT EXISTS satisfaction (
    Survey_ID VARCHAR(30) PRIMARY KEY,
    Ticket_ID VARCHAR(20) NOT NULL UNIQUE,
    CSAT_Score TINYINT NOT NULL CHECK (CSAT_Score BETWEEN 1 AND 5),
    Survey_Date DATETIME,
    CONSTRAINT fk_satisfaction_ticket FOREIGN KEY (Ticket_ID) REFERENCES tickets(Ticket_ID),
    INDEX idx_satisfaction_score (CSAT_Score)
);
