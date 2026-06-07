import os
import random
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def run_expenses_pipeline():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE expenses;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        cursor.execute("SELECT lecturer_name, hire_date, designation FROM lecturers;")
        faculty_list = cursor.fetchall()
        
        expense_batch = []
        start_timeline = datetime(2022, 6, 1).date()
        end_timeline = datetime(2026, 5, 31).date()
        
        # Payroll distribution matching active records
        for name, hire_date, designation in faculty_list:
            if designation == 'HOD':
                base_salary = random.randint(75000, 90000)
            elif designation == 'Senior Lecturer':
                base_salary = random.randint(55000, 70000)
            else:
                base_salary = random.randint(40000, 52000)
                
            current_pay_date = max(start_timeline, hire_date)
            while current_pay_date <= end_timeline:
                desc = f"Monthly payroll disbursement for {name} ({designation})"
                expense_batch.append(('Staff Salary', float(base_salary), current_pay_date, desc))
                
                if current_pay_date.month == 12:
                    current_pay_date = datetime(current_pay_date.year + 1, 1, 1).date()
                else:
                    current_pay_date = datetime(current_pay_date.year, current_pay_date.month + 1, 1).date()

        # Generate structural utilities overhead tracks
        current_month = start_timeline
        while current_month <= end_timeline:
            utility_bill = random.randint(45000, 65000)
            expense_batch.append(('Utilities', float(utility_bill), current_month, f"Campus utility bill for {current_month.strftime('%B %Y')}"))
            
            maint_bill = random.randint(30000, 50000)
            expense_batch.append(('Maintenance', float(maint_bill), current_month, f"Monthly facility upkeep tracking line"))
            
            if current_month.month == 12:
                current_month = datetime(current_month.year + 1, 1, 1).date()
            else:
                current_month = datetime(current_month.year, current_month.month + 1, 1).date()

        cursor.executemany("INSERT INTO expenses (expense_category, amount, expense_date, description) VALUES (%s, %s, %s, %s);", expense_batch)
        conn.commit()
        print(f"📊 Financial Pipeline Complete: Logged {len(expense_batch)} business expense entries.")
        
    except mysql.connector.Error as err:
        print(f"Financial Ledger Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    run_expenses_pipeline()