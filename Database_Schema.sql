CREATE DATABASE college_management;
USE college_management;

-- 1. Courses Table (Unchanged, solid structure)
CREATE TABLE courses ( 
    course_id INT PRIMARY KEY AUTO_INCREMENT, 
    course_name VARCHAR(20) NOT NULL UNIQUE
);

-- 2. Sections Table (Added capacity checking safeguard)
CREATE TABLE sections ( 
    section_id INT PRIMARY KEY AUTO_INCREMENT, 
    course_id INT NOT NULL, 
    section_name VARCHAR(20) NOT NULL, 
    capacity INT CHECK (capacity > 0),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 3. Students Table (Optimized with Status Tracking for Progression/Attrition Analysis)
CREATE TABLE students ( 
    student_id INT PRIMARY KEY AUTO_INCREMENT, 
    admission_no VARCHAR(20) UNIQUE NOT NULL, 
    student_name VARCHAR(100) NOT NULL, 
    gender VARCHAR(10), 
    dob DATE, 
    phone VARCHAR(15), 
    city VARCHAR(50), 
    admission_date DATE NOT NULL, 
    section_id INT,
    current_status ENUM('1st PUC', '2nd PUC', 'Passed Out', 'Discontinued') NOT NULL DEFAULT '1st PUC',
    academic_year VARCHAR(20) NOT NULL, 
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE SET NULL
);

-- 4. Subjects Table
CREATE TABLE subjects ( 
    subject_id INT PRIMARY KEY AUTO_INCREMENT, 
    course_id INT NOT NULL, 
    subject_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 5. Lecturers Table (Optimized for evaluating Year 3 premium hiring/salary tracking)
CREATE TABLE lecturers ( 
    lecturer_id INT PRIMARY KEY AUTO_INCREMENT, 
    lecturer_name VARCHAR(100) NOT NULL, 
    qualification VARCHAR(100), 
    experience_years INT CHECK (experience_years >= 0), 
    joining_date DATE NOT NULL, 
    monthly_salary DECIMAL(10,2) CHECK (monthly_salary > 0), 
    subject_id INT,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE SET NULL
);

-- 6. Attendance Table
CREATE TABLE attendance ( 
    attendance_id INT PRIMARY KEY AUTO_INCREMENT, 
    student_id INT NOT NULL, 
    attendance_date DATE NOT NULL, 
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 7. Marks Table (Added defensive CHECK constraint to prevent improper grade logging)
CREATE TABLE marks ( 
    mark_id INT PRIMARY KEY AUTO_INCREMENT, 
    student_id INT NOT NULL, 
    subject_id INT NOT NULL, 
    exam_name VARCHAR(50) NOT NULL, 
    marks_obtained DECIMAL(5,2) NOT NULL, 
    max_marks DECIMAL(5,2) NOT NULL,
    CONSTRAINT chk_marks_limit CHECK (marks_obtained <= max_marks),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

-- 8. Fee Structure Table (Streams like PCMC/PCMB can now accurately reflect higher laboratory allocations)
CREATE TABLE fee_structure ( 
    fee_structure_id INT PRIMARY KEY AUTO_INCREMENT, 
    course_id INT NOT NULL, 
    academic_year VARCHAR(20) NOT NULL, 
    annual_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00, 
    admission_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00, 
    lab_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00, 
    exam_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 9. Student Payments Table
CREATE TABLE student_payments ( 
    payment_id INT PRIMARY KEY AUTO_INCREMENT, 
    student_id INT NOT NULL, 
    payment_date DATE NOT NULL, 
    amount_paid DECIMAL(10,2) NOT NULL CHECK (amount_paid > 0), 
    payment_mode VARCHAR(20) NOT NULL, 
    receipt_no VARCHAR(30) UNIQUE NOT NULL,
    academic_year VARCHAR(20) NOT NULL, -- Allows clean pairing with fee terms
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 10. Expenses Table (Includes explicit tracking of Academic Year to easily isolate the Year 3 boom)
CREATE TABLE expenses ( 
    expense_id INT PRIMARY KEY AUTO_INCREMENT, 
    expense_date DATE NOT NULL, 
    academic_year VARCHAR(20) NOT NULL, -- Tie directly back to operational cycles
    expense_category ENUM('Salary Expense', 'Marketing Expense', 'Utility Expense', 'Other Expense') NOT NULL, 
    description VARCHAR(255), 
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0)
);
