import openai
from typing import Tuple, Optional
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, SYSTEM_PROMPT
from database_manager import DatabaseManager

class SQLGenerator:
    """Generates SQL queries from natural language using OpenAI GPT."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY != "your-openai-api-key-here" else None
        self.db_manager = DatabaseManager()
        
    def generate_sql(self, natural_language_query: str) -> Tuple[str, str]:
        """
        Convert natural language query to SQL.
        
        Args:
            natural_language_query: User's question in natural language
            
        Returns:
            Tuple of (generated_sql, error_message)
        """
        if not self.client:
            return "", "Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Get database schema for context
            schema_info = self.db_manager.get_schema_info()
            
            # Prepare the prompt
            system_message = SYSTEM_PROMPT.format(schema_info=schema_info)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": natural_language_query}
                ],
                temperature=TEMPERATURE,
                max_tokens=500
            )
            
            generated_sql = response.choices[0].message.content.strip()
            
            # Clean up the SQL (remove markdown formatting if present)
            if generated_sql.startswith('```sql'):
                generated_sql = generated_sql.replace('```sql', '').replace('```', '').strip()
            elif generated_sql.startswith('```'):
                generated_sql = generated_sql.replace('```', '').strip()
            
            # Validate the generated SQL
            is_valid, validation_error = self.db_manager.validate_query(generated_sql)
            if not is_valid:
                return "", f"Generated SQL validation failed: {validation_error}"
            
            return generated_sql, ""
            
        except Exception as e:
            return "", f"Error generating SQL: {str(e)}"
    
    def improve_query(self, original_query: str, error_message: str, natural_language_query: str) -> Tuple[str, str]:
        """
        Attempt to fix a failed SQL query based on the error message.
        
        Args:
            original_query: The SQL query that failed
            error_message: The error message from execution
            natural_language_query: Original user question
            
        Returns:
            Tuple of (improved_sql, error_message)
        """
        if not self.client:
            return "", "Error: OpenAI API key not configured."
        
        try:
            schema_info = self.db_manager.get_schema_info()
            
            improvement_prompt = f"""
            The following SQL query failed with an error. Please fix it.
            
            Original question: {natural_language_query}
            Failed SQL: {original_query}
            Error: {error_message}
            
            Database Schema:
            {schema_info}
            
            Generate a corrected SQL query that addresses the error:
            """
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert SQL developer. Fix the provided SQL query based on the error message."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=500
            )
            
            improved_sql = response.choices[0].message.content.strip()
            
            # Clean up the SQL
            if improved_sql.startswith('```sql'):
                improved_sql = improved_sql.replace('```sql', '').replace('```', '').strip()
            elif improved_sql.startswith('```'):
                improved_sql = improved_sql.replace('```', '').strip()
            
            return improved_sql, ""
            
        except Exception as e:
            return "", f"Error improving query: {str(e)}"

    def explain_query(self, sql_query: str) -> str:
        """
        Generate a human-readable explanation of what the SQL query does.
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            Plain English explanation of the query
        """
        if not self.client:
            return "Cannot explain query: OpenAI API key not configured."
        
        try:
            explanation_prompt = f"""
            Explain what this SQL query does in simple, business-friendly language:
            
            {sql_query}
            
            Provide a clear, concise explanation that a non-technical person would understand.
            """
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a data analyst who explains SQL queries in simple business terms."},
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error explaining query: {str(e)}"