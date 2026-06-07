import random
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# Target enrollment distributions directly from your spreadsheets
lifecycle_matrix = {
    "2023 - 24": {1: (100, 0), 2: (90, 0), 3: (120, 0), 4: (80, 0), 5: (40, 0), 6: (40, 0)},
    "2024 - 25": {1: (102, 90), 2: (88, 81), 3: (122, 108), 4: (78, 72), 5: (42, 36), 6: (38, 36)},
    "2025 - 26": {1: (180, 92), 2: (150, 79), 3: (200, 110), 4: (130, 70), 5: (70, 38), 6: (70, 34)},
    "2026 - 27": {1: (130, 162), 2: (110, 135), 3: (150, 180), 4: (100, 117), 5: (50, 63), 6: (50, 63)}
}

# In-memory pools tracking student IDs to manage promotions accurately
puc1_pool = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
puc2_pool = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

with open("production_student_lifecycle.sql", "w", encoding="utf-8") as f:
    f.write("-- PRODUCTION GRADE STUDENT LIFECYCLE SEED DATA\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\nTRUNCATE TABLE students;\nSET FOREIGN_KEY_CHECKS = 1;\n\n")

    for year in ["2023 - 24", "2024 - 25", "2025 - 26", "2026 - 27"]:
        f.write(f"\n-- ==========================================\n-- ACADEMIC YEAR TIMELINE: {year}\n-- ==========================================\n")
        sections_config = lifecycle_matrix[year]
        
        for section_id, (target_1st, target_2nd) in sections_config.items():
            f.write(f"\n-- Section ID: {section_id} ({year}) operations\n")
            
            # PHASE A: Graduate the previous year's 2nd PUC students to 'Passed Out'
            if puc2_pool[section_id]:
                f.write(f"-- Status Update: Graduating {len(puc2_pool[section_id])} senior students\n")
                for student_adm in puc2_pool[section_id]:
                    f.write(f"UPDATE students SET current_status = 'Passed Out' WHERE admission_no = '{student_adm}';\n")
                puc2_pool[section_id] = [] # Clear out graduated students from active pool
            
            # PHASE B: Promote active 1st PUC students to 2nd PUC & isolate dropouts
            if target_2nd > 0 and puc1_pool[section_id]:
                available_students = puc1_pool[section_id]
                random.shuffle(available_students)
                
                to_promote = available_students[:target_2nd]
                to_dropout = available_students[target_2nd:]
                
                f.write(f"-- Status Update: Promoting {len(to_promote)} students to 2nd PUC\n")
                for student_adm in to_promote:
                    f.write(f"UPDATE students SET current_status = '2nd PUC' WHERE admission_no = '{student_adm}';\n")
                    puc2_pool[section_id].append(student_adm) # Track them as current seniors
                    
                if to_dropout:
                    f.write(f"-- Status Update: Recording {len(to_dropout)} dropout/attrition anomalies\n")
                    for student_adm in to_dropout:
                        f.write(f"UPDATE students SET current_status = 'Dropped Out' WHERE admission_no = '{student_adm}';\n")
                
                puc1_pool[section_id] = [] # Clear out old 1st PUC roster
            
            # PHASE C: Fresh New Admissions (Pure Inserts with guaranteed unique keys)
            if target_1st > 0:
                f.write(f"-- Ledger Action: Inserting {target_1st} fresh 1st PUC registrations\n")
                for i in range(1, target_1st + 1):
                    gender = "Male" if random.random() > 0.5 else "Female"
                    name = fake.name_male() if gender == "Male" else fake.name_female()
                    
                    # Create completely distinct time-stamped unique keys
                    year_clean = year.replace(' ', '').replace('-', '')
                    adm = f"ADM-{year_clean}-{section_id}-{str(i).zfill(3)}"
                    
                    dob = fake.date_of_birth(minimum_age=15, maximum_age=17).strftime('%Y-%m-%d')
                    phone = f"{random.choice([7,8,9])}{''.join([str(random.randint(0,9)) for _ in range(9)])}"
                    city = random.choice(["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi"])
                    adm_date = f"{year[:4]}-06-{random.randint(1,15):02d}"
                    
                    clean_name = name.replace("'", "''")
                    f.write(f"INSERT INTO students (admission_no, student_name, gender, dob, phone, city, admission_date, section_id, current_status, academic_year) "
                            f"VALUES ('{adm}', '{clean_name}', '{gender}', '{dob}', '{phone}', '{city}', '{adm_date}', {section_id}, '1st PUC', '{year}');\n")
                    
                    puc1_pool[section_id].append(adm) # Cache registration number for upcoming timeline updates

print("Success! Your revised file 'production_student_lifecycle.sql' has been built safely.")
