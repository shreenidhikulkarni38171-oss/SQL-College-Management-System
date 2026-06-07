import mysql.connector
import random

# Database Configuration Setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shree@2000',  # 💡 Change this to your exact MySQL password
    'database': 'college_management'
}

# Stream curriculum subject maps matching previous structural schema
section_subject_map = {
    1: [1, 2, 3, 4, 9, 10],   # PCMC
    2: [1, 2, 3, 5, 9, 10],   # PCMB
    3: [6, 7, 8, 4, 9, 10],   # CEBA
    4: [6, 7, 8, 3, 9, 10],   # SEBA
    5: [11, 8, 12, 13, 9, 10],# HEPS
    6: [11, 8, 13, 12, 9, 10] # HESP
}

# Subjects that have an accompanying Lab component (Physics, Chemistry, CS, Biology)
LAB_SUBJECT_IDS = {1, 2, 4, 5}

def get_exam_configurations(subject_id, exam_type):
    """Returns (max_marks, passing_marks) based on standard PU board blueprints."""
    if exam_type == 'Unit Test':
        return 25, 9
    elif exam_type == 'Practical / Lab':
        return 30, 11
    elif exam_type == 'Midterm' or exam_type == 'Final Board':
        # If it's a science subject with a lab, theory paper is out of 70 marks. Otherwise, 100.
        if subject_id in LAB_SUBJECT_IDS:
            return 70, 25
        else:
            return 100, 35
    return 100, 35

def calculate_bracket_marks(tier, max_marks):
    """Calculates marks based on student bracket profile and guarantees a strict ceiling constraint."""
    if tier == 'High':
        # Top tier students score between 78% and 98%
        percentage = random.uniform(0.78, 0.98)
    elif tier == 'Medium':
        # Average tier students score between 48% and 77%
        percentage = random.uniform(0.48, 0.77)
    else:
        # Struggling tier students score between 28% and 47%
        percentage = random.uniform(0.28, 0.47)
        
    marks = int(round(max_marks * percentage))
    
    # CRITICAL SAFEGUARD: Ensure marks never cross max_marks or drop below 0
    return max(0, min(marks, max_marks))

def run_marks_pipeline():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Connected to database. Wiping out old grading tables...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE marks;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        print("Fetching student profiles...")
        cursor.execute("SELECT admission_no, section_id FROM students;")
        students = cursor.fetchall()
        
        if not students:
            print("Error: No student directory found! Populate your student profiles first.")
            return

        marks_batch = []
        total_inserted = 0
        BATCH_SIZE = 5000
        
        print(f"Loaded {len(students)} student profiles. Processing consistent academic profiles...")
        
        for index, (adm_no, section_id) in enumerate(students):
            # Assign a permanent academic performance tier to this student to ensure consistency across all subjects
            # Skewed heavily toward 'High' (65%) to mirror the college's rising admissions and prestige
            rand_val = random.random()
            if rand_val < 0.65:
                student_tier = 'High'
            elif rand_val < 0.90:
                student_tier = 'Medium'
            else:
                student_tier = 'Low'
                
            mapped_subjects = section_subject_map.get(section_id, [])
            
            for sub_id in mapped_subjects:
                # Core exam cycles
                exams_to_generate = ['Unit Test', 'Midterm', 'Final Board']
                
                # Dynamic Lab Injection: If subject is a science course, append lab evaluations
                if sub_id in LAB_SUBJECT_IDS:
                    exams_to_generate.append('Practical / Lab')
                    
                for exam in exams_to_generate:
                    max_m, pass_m = get_exam_configurations(sub_id, exam)
                    obtained_m = calculate_bracket_marks(student_tier, max_m)
                    
                    marks_batch.append((adm_no, sub_id, exam, obtained_m, max_m, pass_m))
                    
                    if len(marks_batch) >= BATCH_SIZE:
                        insert_query = """
                            INSERT IGNORE INTO marks (admission_no, subject_id, exam_type, marks_obtained, max_marks, passing_marks)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """
                        cursor.executemany(insert_query, marks_batch)
                        conn.commit()
                        total_inserted += len(marks_batch)
                        marks_batch = []
                        
            if (index + 1) % 500 == 0:
                print(f"Graded all semesters for {index + 1}/{len(students)} students...")

        if marks_batch:
            insert_query = """
                INSERT IGNORE INTO marks (admission_no, subject_id, exam_type, marks_obtained, max_marks, passing_marks)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.executemany(insert_query, marks_batch)
            conn.commit()
            total_inserted += len(marks_batch)

        print("\n-----------------------------------------------------------------")
        print(f" Success! Grading Engine Complete. Total Logged Mark Entries: {total_inserted:,}")
        
    except mysql.connector.Error as err:
        print(f"Pipeline Interrupted by Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database channel disconnected cleanly.")

if __name__ == "__main__":
    run_marks_pipeline()
