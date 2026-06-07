ALTER TABLE students
ADD puc_year TINYINT;

ALTER TABLE lecturers
ADD employee_type VARCHAR(30);

ALTER TABLE student_payments
ADD due_date DATE;

ALTER TABLE students
ADD student_status varchar(10);



Upadated and chnaged the forigen key vilations use this for that 

-- Step 1: Temporarily turn off foreign key checks so MySQL lets us clear the table
SET FOREIGN_KEY_CHECKS = 0;

-- Step 2: Wipe the table and completely reset the auto-increment counter back to 1
TRUNCATE TABLE courses;

-- Step 3: Turn foreign key checks back on
SET FOREIGN_KEY_CHECKS = 1;

-- Step 4: Re-run your stream inserts (They will now get IDs 1, 2, and 3)
INSERT INTO courses (course_name) VALUES 
('Science'),  -- Will be ID 1
('Commerce'), -- Will be ID 2
('Arts');     -- Will be ID 3

-- Step 1: Temporarily turn off foreign key checks 
SET FOREIGN_KEY_CHECKS = 0;

-- Step 2: Wipe the sections table and reset its auto-increment counter to 1
TRUNCATE TABLE sections;

-- Step 3: Turn foreign key checks back on
SET FOREIGN_KEY_CHECKS = 1;

-- Step 4: Re-insert the sections using your clean Course IDs (1 = Science, 2 = Commerce, 3 = Arts)
INSERT INTO sections (course_id, section_name, capacity) VALUES
(1, 'PCMC', 200), -- Science
(1, 'PCMB', 160), -- Science
(2, 'CEBA', 220), -- Commerce
(2, 'SEBA', 140), -- Commerce
(3, 'HEPS', 80),  -- Arts
(3, 'HESP', 80);  -- Arts

-- View global operational income grouped by academic year and transaction methods
SELECT 
    academic_year,
    payment_mode,
    COUNT(*) as transaction_count,
    SUM(amount_paid) as total_revenue_collected
FROM student_payments
GROUP BY academic_year, payment_mode
ORDER BY academic_year;

organized teaching staff grouped by their respective departments:

SELECT 
    department, 
    designation, 
    lecturer_name, 
    employee_no, 
    email 
FROM lecturers
ORDER BY department, FIELD(designation, 'HOD', 'Senior Lecturer', 'Lecturer');

To check the size of the db table change the name of table just 

SELECT 
    table_name AS 'Table',
    ROUND(((data_length) / 1024 / 1024), 2) AS 'Data Size (MB)',
    ROUND(((index_length) / 1024 / 1024), 2) AS 'Index Size (MB)',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Total Physical Disk Size (MB)'
FROM 
    information_schema.tables
WHERE 
    table_schema = 'college_management'
    AND table_name = 'attendance';

this shows total attendance percentage and numbers for all 4 yers 

USE college_management;

SELECT 
    s.academic_year AS 'Academic Year Batch',
    SUM(summary.total_attended) AS 'Total Classes Attended',
    SUM(summary.total_lectures) AS 'Total Tracked Lectures',
    ROUND((SUM(summary.total_attended) / SUM(summary.total_lectures)) * 100, 2) AS 'Institutional Attendance Rate (%)'
FROM students s
JOIN (
    -- This inner block shrinks 3 million rows into 2,330 rows instantly using indexes
    SELECT 
        admission_no,
        COUNT(CASE WHEN status = 'Present' THEN 1 END) AS total_attended,
        COUNT(*) AS total_lectures
    FROM attendance
    GROUP BY admission_no
) summary ON s.admission_no = summary.admission_no
GROUP BY s.academic_year
ORDER BY s.academic_year ASC;

creating a index 
CREATE INDEX idx_attendance_status ON attendance(admission_no, status);


BUSINESS DASHBOARD 
USE college_management;

SELECT 
    revenue.financial_year AS 'Academic Financial Year',
    CONCAT('₹', FORMAT(COALESCE(revenue.total_revenue, 0), 2)) AS 'Gross Tuition Income (Revenue)',
    CONCAT('₹', FORMAT(COALESCE(expenses.total_outflow, 0), 2)) AS 'Operating Expenditures (Expenses)',
    CONCAT('₹', FORMAT(COALESCE(revenue.total_revenue, 0) - COALESCE(expenses.total_outflow, 0), 2)) AS 'Net Institutional Profit',
    ROUND((COALESCE(revenue.total_revenue, 0) - COALESCE(expenses.total_outflow, 0)) / NULLIF(revenue.total_revenue, 0) * 100, 2) AS 'Profit Margin (%)'
FROM (
    -- Subquery 1: Grabs tuition income straight from your ledger
    SELECT 
        academic_year AS financial_year,
        SUM(amount_paid) AS total_revenue
    FROM student_payments
    GROUP BY academic_year
) revenue
LEFT JOIN (
    -- Subquery 2: Groups raw expense dates into matching start-year blocks
    SELECT 
        CASE 
            WHEN expense_date BETWEEN '2022-06-01' AND '2023-05-31' THEN '2022'
            WHEN expense_date BETWEEN '2023-06-01' AND '2024-05-31' THEN '2023'
            WHEN expense_date BETWEEN '2024-06-01' AND '2025-05-31' THEN '2024'
            WHEN expense_date BETWEEN '2025-06-01' AND '2026-05-31' THEN '2025'
            ELSE 'Other'
        END AS financial_year,
        SUM(amount) AS total_outflow
    FROM expenses
    GROUP BY financial_year
) expenses ON LEFT(revenue.financial_year, 4) = expenses.financial_year
ORDER BY revenue.financial_year ASC;







