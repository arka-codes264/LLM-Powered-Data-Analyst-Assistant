import sqlite3
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from config import DATABASE_PATH, MAX_QUERY_RESULTS

class DatabaseManager:
    """Manages database connections and operations for the data analyst assistant."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        except sqlite3.Error as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_schema_info(self) -> str:
        """Get comprehensive schema information for all tables."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        schema_info = []
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            schema_info.append(f"\nTable: {table_name}")
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                col_name = column[1]
                col_type = column[2]
                is_nullable = "NOT NULL" if column[3] else "NULL"
                schema_info.append(f"  - {col_name}: {col_type} ({is_nullable})")
            
            # Get sample values for better context
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            if sample_rows:
                schema_info.append("  Sample data:")
                for i, row in enumerate(sample_rows):
                    if i == 0:  # Show column names for first row
                        col_names = [description[0] for description in cursor.description]
                        schema_info.append(f"    {dict(zip(col_names, row))}")
                    else:
                        schema_info.append(f"    {dict(zip(col_names, row))}")
        
        return "\n".join(schema_info)
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, str]:
        """
        Execute SQL query safely and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (DataFrame with results, error message if any)
        """
        if not self.connection:
            self.connect()
        
        try:
            # Security check - only allow SELECT queries
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT'):
                return pd.DataFrame(), "Error: Only SELECT queries are allowed for security reasons."
            
            # Add LIMIT if not present
            if 'LIMIT' not in query_upper:
                query += f" LIMIT {MAX_QUERY_RESULTS}"
            
            # Execute query
            df = pd.read_sql_query(query, self.connection)
            
            if df.empty:
                return df, "Query executed successfully but returned no results."
            
            return df, ""
            
        except sqlite3.Error as e:
            return pd.DataFrame(), f"SQL Error: {str(e)}"
        except Exception as e:
            return pd.DataFrame(), f"Unexpected error: {str(e)}"
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Validate SQL query without executing it.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic security checks
            query_upper = query.strip().upper()
            
            forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
            for keyword in forbidden_keywords:
                if keyword in query_upper:
                    return False, f"Forbidden keyword '{keyword}' detected. Only SELECT queries are allowed."
            
            if not query_upper.startswith('SELECT'):
                return False, "Query must start with SELECT."
            
            # Try to parse the query (without executing)
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            
            return True, "Query is valid."
            
        except sqlite3.Error as e:
            return False, f"SQL syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]
    
    def get_column_names(self, table_name: str) -> List[str]:
        """Get column names for a specific table."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()