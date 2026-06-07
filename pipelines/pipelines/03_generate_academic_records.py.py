import mysql.connector
from datetime import datetime, timedelta
import random

# Database Configuration Setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shree@2000',  # 💡 Change this to your exact MySQL password
    'database': 'college_management'
}

# Stream curriculum subject maps matching our previous structural schema
section_subject_map = {
    1: [1, 2, 3, 4, 9, 10],   # PCMC
    2: [1, 2, 3, 5, 9, 10],   # PCMB
    3: [6, 7, 8, 4, 9, 10],   # CEBA
    4: [6, 7, 8, 3, 9, 10],   # SEBA
    5: [11, 8, 12, 13, 9, 10],# HEPS
    6: [11, 8, 13, 12, 9, 10] # HESP
}

# Strict Indian Holiday Registry (MM-DD)
INDIAN_HOLIDAYS = [
    (1, 26),  # Republic Day
    (8, 15),  # Independence Day
    (10, 2),  # Gandhi Jayanti
    (11, 1)   # Karnataka Rajyotsava
]

def generate_working_days(academic_year_str):
    """Generates all valid academic working days excluding weekends, summers, and national holidays."""
    start_year = int(academic_year_str[:4])
    end_year = start_year + 1
    
    start_date = datetime(start_year, 6, 1).date()
    end_date = datetime(end_year, 3, 31).date()
    
    working_days = []
    current_date = start_date
    
    while current_date <= end_date:
        # 1. Skip Summer Vacation (April and May)
        if current_date.month in [4, 5]:
            current_date += timedelta(days=1)
            continue
            
        # 2. Skip Weekends (Saturday = 5, Sunday = 6)
        if current_date.weekday() in [5, 6]:
            current_date += timedelta(days=1)
            continue
            
        # 3. Skip Strict National/State Holidays
        if (current_date.month, current_date.day) in INDIAN_HOLIDAYS:
            current_date += timedelta(days=1)
            continue
            
        working_days.append(current_date)
        current_date += timedelta(days=1)
        
    return working_days

def run_attendance_pipeline():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Connected to database. Clearing out old attendance records...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE attendance;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        print("Fetching active student registration mapping...")
        cursor.execute("SELECT admission_no, section_id, academic_year FROM students;")
        students = cursor.fetchall()
        
        if not students:
            print("Error: No student profiles found to process! Build the student directory first.")
            return

        print(f"Loaded {len(students)} active student records. Pre-calculating calendar metrics...")
        
        # Pre-cache operational working days per academic batch to boost performance speed
        unique_years = set([s[2] for s in students])
        academic_calendars = {yr: generate_working_days(yr) for yr in unique_years}
        
        attendance_batch = []
        total_inserted = 0
        BATCH_SIZE = 50000  # Pushes 50,000 records at a time to optimize system RAM
        
        print("\n--- Commencing Massive 4-Year Attendance Generation Pipeline ---")
        
        for index, (adm_no, section_id, acad_year) in enumerate(students):
            working_days = academic_calendars.get(acad_year, [])
            mapped_subjects = section_subject_map.get(section_id, [])
            
            for day in working_days:
                for sub_id in mapped_subjects:
                    # 92% chance of being Present, 8% chance of being Absent
                    status = 'Present' if random.random() < 0.92 else 'Absent'
                    
                    attendance_batch.append((adm_no, sub_id, day, status))
                    
                    # When chunk hits capacity limits, execute a mass save to database
                    if len(attendance_batch) >= BATCH_SIZE:
                        insert_query = """
                            INSERT IGNORE INTO attendance (admission_no, subject_id, attendance_date, status)
                            VALUES (%s, %s, %s, %s);
                        """
                        cursor.executemany(insert_query, attendance_batch)
                        conn.commit()
                        total_inserted += len(attendance_batch)
                        print(f" Saved {total_inserted:,} transaction records successfully...")
                        attendance_batch = [] # Flush local memory block
            
            if (index + 1) % 500 == 0:
                print(f"Processed tracking profiles for {index + 1}/{len(students)} students...")

        # Clear out remaining residual records left in the array array
        if attendance_batch:
            insert_query = """
                INSERT IGNORE INTO attendance (admission_no, subject_id, attendance_date, status)
                VALUES (%s, %s, %s, %s);
            """
            cursor.executemany(insert_query, attendance_batch)
            conn.commit()
            total_inserted += len(attendance_batch)

        print("-----------------------------------------------------------------")
        print(f" Success! Pipeline Complete. Total Logged Rows: {total_inserted:,}")
        
    except mysql.connector.Error as err:
        print(f"Pipeline Interrupted by Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database channel disconnected cleanly. Systems synchronized.")

if __name__ == "__main__":
    run_attendance_pipeline()