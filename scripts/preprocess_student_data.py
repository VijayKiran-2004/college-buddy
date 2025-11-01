import pandas as pd
import json

def preprocess_student_data():
    """Preprocess student data and convert to structured format for the chatbot"""
    
    print("Loading student data...")
    df = pd.read_csv('data/student/student_data.csv')
    
    # 1. Handle missing values in COMPANY PLACED
    df['COMPANY PLACED'] = df['COMPANY PLACED'].fillna('Not Placed')
    
    # 2. Clean column names (lowercase, remove spaces)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # 3. Standardize branch names
    branch_mapping = {
        'CE': 'Civil Engineering',
        'EEE': 'Electrical and Electronics Engineering',
        'MECH': 'Mechanical Engineering',
        'CSE': 'Computer Science and Engineering',
        'IT': 'Information Technology',
        'CSE (AI&ML)': 'Computer Science and Engineering (AI & ML)',
        'CSE (DS)': 'Computer Science and Engineering (Data Science)'
    }
    df['branch_full'] = df['branch'].map(branch_mapping)
    
    # 4. Create structured text descriptions for each student
    student_records = []
    
    for _, row in df.iterrows():
        # Create a detailed text description
        description = f"""Student Record:
Roll Number: {row['roll_no']}
Name: {row['name']}
Gender: {row['gender']}
Branch: {row['branch_full']} ({row['branch']})
Degree: {row['degree_name']}
CGPA: {row['cgpa']}
Credits: {row['credits']}
Result: {row['result']}
Email: {row['email_id']}
Joining Year: {row['joining_year']}
Passed Year: {row['passed_year']}
Admission Type: {row['admission']}
Placement Status: {row['status']}
Company Placed: {row['company_placed']}
"""
        
        student_records.append({
            'roll_no': row['roll_no'],
            'name': row['name'],
            'branch': row['branch'],
            'branch_full': row['branch_full'],
            'description': description.strip()
        })
    
    # 5. Create aggregated statistics per branch
    branch_stats = []
    for branch in df['branch'].unique():
        branch_data = df[df['branch'] == branch]
        placed_students = branch_data[branch_data['status'] == 'Placed']
        
        stats = f"""Branch Statistics for {branch_mapping.get(branch, branch)}:
Total Students: {len(branch_data)}
Male: {len(branch_data[branch_data['gender'] == 'MALE'])}
Female: {len(branch_data[branch_data['gender'] == 'FEMALE'])}
Average CGPA: {branch_data['cgpa'].mean():.2f}
Highest CGPA: {branch_data['cgpa'].max():.2f}
Lowest CGPA: {branch_data['cgpa'].min():.2f}
Students Placed: {len(placed_students)}
Placement Percentage: {(len(placed_students) / len(branch_data) * 100):.2f}%
Joining Years: {', '.join(map(str, sorted(branch_data['joining_year'].unique())))}
"""
        
        branch_stats.append({
            'branch': branch,
            'branch_full': branch_mapping.get(branch, branch),
            'description': stats.strip()
        })
    
    # 6. Save processed data
    print("\nSaving processed data...")
    
    # Save individual student records
    with open('data/student/students_processed.json', 'w', encoding='utf-8') as f:
        json.dump(student_records, f, indent=2, ensure_ascii=False)
    
    # Save branch statistics
    with open('data/student/branch_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(branch_stats, f, indent=2, ensure_ascii=False)
    
    # Save cleaned CSV
    df.to_csv('data/student/student_data_cleaned.csv', index=False)
    
    print(f"✅ Processed {len(student_records)} student records")
    print(f"✅ Generated statistics for {len(branch_stats)} branches")
    print(f"✅ Files created:")
    print(f"   - Student data/students_processed.json")
    print(f"   - Student data/branch_statistics.json")
    print(f"   - Student data/student_data_cleaned.csv")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"Total Students: {len(df)}")
    print(f"Branches: {', '.join(df['branch'].unique())}")
    print(f"Placed Students: {len(df[df['status'] == 'Placed'])}")
    print(f"Not Placed: {len(df[df['status'] == 'Not Placed'])}")
    print(f"Average CGPA: {df['cgpa'].mean():.2f}")
    
    return df, student_records, branch_stats

if __name__ == "__main__":
    preprocess_student_data()
