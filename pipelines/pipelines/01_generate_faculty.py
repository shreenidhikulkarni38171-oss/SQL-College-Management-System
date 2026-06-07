import random
from datetime import datetime, timedelta

# 1. Define matching fee rules from our lookup table
fee_rules = {
    "2023 - 24": {1: 45000, 2: 43000, 3: 30000, 4: 28000, 5: 22000, 6: 22000},
    "2024 - 25": {1: 45000, 2: 43000, 3: 30000, 4: 28000, 5: 22000, 6: 22000},
    "2025 - 26": {1: 50000, 2: 48000, 3: 33000, 4: 30000, 5: 25000, 6: 25000},
    "2026 - 27": {1: 50000, 2: 48000, 3: 33000, 4: 30000, 5: 25000, 6: 25000}
}

# 2. Replicate historical enrolment matrix to target exact matching student IDs
lifecycle_matrix = {
    "2023 - 24": {1: (100, 0), 2: (90, 0), 3: (120, 0), 4: (80, 0), 5: (40, 0), 6: (40, 0)},
    "2024 - 25": {1: (102, 90), 2: (88, 81), 3: (122, 108), 4: (78, 72), 5: (42, 36), 6: (38, 36)},
    "2025 - 26": {1: (180, 92), 2: (150, 79), 3: (200, 110), 4: (130, 70), 5: (70, 38), 6: (70, 34)},
    "2026 - 27": {1: (130, 162), 2: (110, 135), 3: (150, 180), 4: (100, 117), 5: (50, 63), 6: (50, 63)}
}

puc1_pool = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
puc2_pool = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
receipt_counter = 100001

def generate_random_date(start_year, base_month_june):
    """Generates a random date progressing through the academic school year."""
    start_date = datetime(start_year, 6, 1) + timedelta(days=random.randint(0, 14))
    end_date = datetime(start_year + 1, 3, 15)
    time_between = end_date - start_date
    random_days = random.randint(0, time_between.days)
    return start_date + timedelta(days=random_days)

with open("populate_payments.sql", "w", encoding="utf-8") as f:
    f.write("-- SYSTEM GENERATED FINANCIAL LEDGER SEED FILE\n")
    f.write("USE college_management;\n\n")
    f.write("DROP TABLE IF EXISTS student_payments;\n")
    f.write("CREATE TABLE student_payments (\n"
            "    payment_id INT AUTO_INCREMENT PRIMARY KEY,\n"
            "    admission_no VARCHAR(30) NOT NULL,\n"
            "    academic_year VARCHAR(20) NOT NULL,\n"
            "    payment_date DATE NOT NULL,\n"
            "    amount_paid DECIMAL(10, 2) NOT NULL,\n"
            "    payment_mode ENUM('Cash', 'Card', 'UPI', 'Net Banking') NOT NULL,\n"
            "    receipt_number VARCHAR(50) UNIQUE NOT NULL,\n"
            "    FOREIGN KEY (admission_no) REFERENCES students(admission_no)\n"
            ");\n\n")

    for year in ["2023 - 24", "2024 - 25", "2025 - 26", "2026 - 27"]:
        f.write(f"\n-- ==========================================\n-- TRANSACTIONS FOR ACADEMIC YEAR: {year}\n-- ==========================================\n")
        base_calendar_year = int(year[:4])
        sections_config = lifecycle_matrix[year]
        
        for section_id, (target_1st, target_2nd) in sections_config.items():
            active_students_this_term = []
            
            # Carry over promotions to trace payments for 2nd PUC
            if target_2nd > 0 and puc1_pool[section_id]:
                available = list(puc1_pool[section_id])
                random.shuffle(available)
                to_promote = available[:target_2nd]
                active_students_this_term.extend([(adm, "2nd PUC") for adm in to_promote])
                puc2_pool[section_id] = to_promote
                puc1_pool[section_id] = []
            
            # Map fresh 1st PUC student records
            year_clean = year.replace(' ', '').replace('-', '')
            fresh_admissions = [f"ADM-{year_clean}-{section_id}-{str(i).zfill(3)}" for i in range(1, target_1st + 1)]
            active_students_this_term.extend([(adm, "1st PUC") for adm in fresh_admissions])
            puc1_pool[section_id] = fresh_admissions
            
            if not active_students_this_term:
                continue
                
            # Pick exactly 2 to 3 lucky students from this section for the 50% scholarship waiver
            scholarship_count = random.randint(2, 3)
            scholarship_students = set(random.sample([s[0] for s in active_students_this_term], min(scholarship_count, len(active_students_this_term))))
            
            base_fee = fee_rules[year][section_id]
            
            for admission_no, grade in active_students_this_term:
                # Rule: Apply 50% scholarship limit if flagged
                is_scholarship = admission_no in scholarship_students
                target_total = base_fee * 0.5 if is_scholarship else base_fee
                
                # Rule: Determine if paying full upfront vs breaking into installments
                pay_in_full = random.random() < 0.25 # 25% pay full, 75% use installments
                
                payment_chunks = []
                if pay_in_full:
                    payment_chunks.append(target_total)
                else:
                    # Break up total fee across 3 distinct custom installations
                    c1 = round(target_total * random.uniform(0.3, 0.45), 2)
                    c2 = round(target_total * random.uniform(0.3, 0.4), 2)
                    c3 = round(target_total - (c1 + c2), 2)
                    payment_chunks.extend([c1, c2, c3])
                
                # Write individual transaction ledger lines
                admission_date_offset = datetime(base_calendar_year, 6, random.randint(1, 10))
                
                for idx, amount in enumerate(payment_chunks):
                    mode = random.choice(['Cash', 'Card', 'UPI', 'Net Banking'])
                    
                    if pay_in_full:
                        pay_date = admission_date_offset + timedelta(days=random.randint(0, 5))
                    else:
                        # Space out payments chronologically (Installment 1, 2, 3)
                        pay_date = admission_date_offset + timedelta(days=idx * random.randint(60, 90) + random.randint(1, 15))
                    
                    # Safety check: Cap payment dates inside realistic school calendar borders
                    if pay_date > datetime(base_calendar_year + 1, 3, 31):
                        pay_date = datetime(base_calendar_year + 1, 3, random.randint(10, 25))
                        
                    formatted_date = pay_date.strftime('%Y-%m-%d')
                    comment = " -- 50% Scholarship Applied" if is_scholarship else ""
                    
                    sql_line = (
                        f"INSERT INTO student_payments (admission_no, academic_year, payment_date, amount_paid, payment_mode, receipt_number) "
                        f"VALUES ('{admission_no}', '{year}', '{formatted_date}', {amount}, '{mode}', 'RCPT-{receipt_counter}');{comment}\n"
                    )
                    f.write(sql_line)
                    receipt_counter += 1

print("Complete! Open and verify 'populate_payments.sql' directly within Workbench.")