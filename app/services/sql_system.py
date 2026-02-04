"""
SQL System for Student Queries
Handles natural language queries about student data
"""
import sqlite3
import pandas as pd
import re

class SQLSystem:
    def __init__(self, db_path='app/database/students.db'):
        """Initialize SQL system with student database"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # Get table schema
        self.columns = self._get_columns()
    
    def _get_columns(self):
        """Get list of columns in students table"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]
        return columns
    
    def extract_entities(self, query):
        """Extract entities from natural language query"""
        query_lower = query.lower()
        entities = {}
        
        # Extract roll number (student ID)
        roll_match = re.search(r'\b(\d{2}[A-Z]\d{2}[A-Z]\d{4})\b', query) or re.search(r'\b(\d{5,10})\b', query)
        if roll_match:
            entities['roll_no'] = roll_match.group(1)
        
        # Extract branch (department)
        branches = ['ce', 'cse', 'ece', 'eee', 'me', 'it']
        for branch in branches:
            if branch in query_lower:
                entities['branch'] = branch.upper()
                break
        
        # Extract name (capitalized words)
        name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', query)
        if name_match:
            entities['name'] = name_match.group(1)
        
        # Extract CGPA condition
        cgpa_match = re.search(r'cgpa\s*([><=]+)\s*(\d+\.?\d*)', query_lower)
        if cgpa_match:
            entities['cgpa_operator'] = cgpa_match.group(1)
            entities['cgpa_value'] = float(cgpa_match.group(2))
        
        # Extract placement status - check negatives FIRST
        if 'not placed' in query_lower or 'unplaced' in query_lower or "didn't" in query_lower or "didnt" in query_lower:
            entities['placed'] = False
        elif 'placed' in query_lower:
            entities['placed'] = True
        
        return entities
    
    def build_sql_query(self, entities):
        """Build SQL query from extracted entities"""
        base_query = "SELECT * FROM students"
        conditions = []
        
        if 'roll_no' in entities:
            conditions.append(f"\"ROLL NO\" = '{entities['roll_no']}'")
        
        if 'branch' in entities:
            conditions.append(f"UPPER(BRANCH) = '{entities['branch']}'")
        
        if 'name' in entities:
            conditions.append(f"NAME LIKE '%{entities['name']}%'")
        
        if 'cgpa_operator' in entities:
            op = entities['cgpa_operator']
            val = entities['cgpa_value']
            conditions.append(f"CGPA {op} {val}")
        
        if 'placed' in entities:
            if entities['placed']:
                conditions.append("\"COMPANY PLACED\" IS NOT NULL AND \"COMPANY PLACED\" != 'Not Placed'")
            else:
                conditions.append("(\"COMPANY PLACED\" IS NULL OR \"COMPANY PLACED\" = 'Not Placed')")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " LIMIT 50"  # Limit results
        return base_query
    
    def query_students(self, query):
        """
        Execute natural language query on student database
        
        Examples:
        - "What is the CGPA of student 12345?"
        - "List all students in CSE department"
        - "Show students with CGPA > 8.5"
        - "Find student named John Doe"
        - "How many students got placed?"
        """
        query_lower = query.lower()
        
        # Special case: "how many students placed" - aggregate query
        if 'how many' in query_lower and 'placed' in query_lower:
            try:
                # Get all placed students
                df = pd.read_sql_query(
                    """SELECT * FROM students 
                       WHERE "COMPANY PLACED" IS NOT NULL AND "COMPANY PLACED" != 'Not Placed'""", 
                    self.conn
                )
                
                if len(df) == 0:
                    return "No placement data available in the database."
                
                total_placed = len(df)
                
                # Calculate statistics
                response = f"Placement Statistics (from Student DB):\n\n"
                response += f"• Total students placed: {total_placed}\n"
                
                # Top companies
                if not df['COMPANY PLACED'].empty:
                    companies = df['COMPANY PLACED'].value_counts().head(5)
                    response += f"• Top recruiters: {', '.join(companies.index.tolist())}\n"
                
                # Average CGPA
                if 'CGPA' in df.columns and not df['CGPA'].isnull().all():
                    avg_cgpa = df['CGPA'].mean()
                    response += f"• Average CGPA of placed students: {avg_cgpa:.2f}\n"
                
                # Branch-wise distribution
                if 'BRANCH' in df.columns:
                    branch_counts = df['BRANCH'].value_counts().to_dict()
                    response += f"\nBranch-wise placement:\n"
                    for branch, count in sorted(branch_counts.items(), key=lambda x: x[1], reverse=True):
                        response += f"  • {branch}: {count} students\n"
                
                return response.strip()
            except Exception as e:
                print(f"SQL Error in placement stats: {e}")
                return f"Error fetching placement data: {e}"
        
        # Special case: top companies query
        query_lower = query.lower()
        if 'companies' in query_lower or 'recruiter' in query_lower:
            try:
                df = pd.read_sql_query(
                    """SELECT "COMPANY PLACED", COUNT(*) as count 
                       FROM students 
                       WHERE "COMPANY PLACED" IS NOT NULL AND "COMPANY PLACED" != 'Not Placed'
                       GROUP BY "COMPANY PLACED"
                       ORDER BY count DESC
                       LIMIT 10""", 
                    self.conn
                )
                if len(df) == 0:
                    return "No placement data available."
                
                response = "Top Recruiting Companies:\n\n"
                for _, row in df.iterrows():
                    response += f"• {row['COMPANY PLACED']}: {row['count']} students\n"
                return response
            except Exception as e:
                return f"Error fetching company data: {e}"
        
        # Extract entities from query
        entities = self.extract_entities(query)
        
        if not entities:
            return "I couldn't understand the student query. Please specify student ID, name, department, or conditions."
        
        # Build SQL query
        sql_query = self.build_sql_query(entities)
        
        try:
            # Execute query
            result_df = pd.read_sql_query(sql_query, self.conn)
            
            if len(result_df) == 0:
                return "No students found matching your criteria."
            
            # PRIVACY: Only show aggregate data for general queries
            # Individual records only for specific student lookup
            if len(result_df) == 1 and 'roll_no' in entities:
                # Specific student lookup - show limited details
                student = result_df.iloc[0]
                response = f"Student Information:\n"
                safe_cols = ['NAME', 'BRANCH', 'CGPA', 'COMPANY PLACED']
                for col in safe_cols:
                    if col in result_df.columns:
                        response += f"  {col}: {student[col]}\n"
                return response.strip()
            else:
                # General query - show ONLY aggregate summary (PRIVACY)
                total = len(result_df)
                
                # Calculate statistics
                response = f"Summary ({total} students found):\n\n"
                
                # Placement stats
                if 'COMPANY PLACED' in result_df.columns:
                    placed = result_df[result_df['COMPANY PLACED'].notna() & (result_df['COMPANY PLACED'] != 'Not Placed')]
                    response += f"• Placed students: {len(placed)} out of {total}\n"
                    
                    # Top companies
                    if len(placed) > 0:
                        companies = placed['COMPANY PLACED'].value_counts().head(3)
                        response += f"• Top recruiters: {', '.join(companies.index.tolist())}\n"
                
                # CGPA stats
                if 'CGPA' in result_df.columns:
                    avg_cgpa = result_df['CGPA'].mean()
                    max_cgpa = result_df['CGPA'].max()
                    response += f"• Average CGPA: {avg_cgpa:.2f}\n"
                    response += f"• Highest CGPA: {max_cgpa:.2f}\n"
                
                # Branch distribution
                if 'BRANCH' in result_df.columns:
                    branches = result_df['BRANCH'].value_counts().to_dict()
                    response += f"• Branch-wise: {', '.join([f'{k}: {v}' for k, v in branches.items()])}\n"
                
                response += "\n(Individual student data is protected. Please contact administration for specific records.)"
                return response
        
        except Exception as e:
            return f"Error querying database: {str(e)}"
    
    def __call__(self, query):
        """Make class callable"""
        return self.query_students(query)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__ == "__main__":
    # Test the SQL system
    sql_system = SQLSystem()
    
    print("Testing SQL System...")
    print("="*70)
    
    # Test queries
    test_queries = [
        "What is the CGPA of student 12345?",
        "List all students in CSE department",
        "Show students with CGPA > 8.5",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*70)
        result = sql_system(query)
        print(result)
        print()
    
    sql_system.close()
