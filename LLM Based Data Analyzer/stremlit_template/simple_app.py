#!/usr/bin/env python3
"""
Simplified version of the app for debugging.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page config first
st.set_page_config(
    page_title="AI Data Analyst Assistant",
    page_icon="🤖",
    layout="wide"
)

def main():
    """Simple main function to test basic functionality."""
    
    st.title("🤖 AI Data Analyst Assistant")
    st.write("Testing basic functionality...")
    
    # Test imports
    try:
        from database_manager import DatabaseManager
        from config import DATABASE_PATH, SAMPLE_QUERIES
        
        st.success("✓ All modules imported successfully")
        
        # Test database
        if os.path.exists(DATABASE_PATH):
            st.success(f"✓ Database file exists: {DATABASE_PATH}")
            
            # Test database connection
            db = DatabaseManager()
            with db:
                tables = db.get_table_names()
                st.success(f"✓ Database connected. Tables: {tables}")
                
                # Test simple query
                df, error = db.execute_query("SELECT COUNT(*) as count FROM customers")
                if error:
                    st.error(f"Query error: {error}")
                else:
                    st.success(f"✓ Query successful. Customer count: {df.iloc[0]['count']}")
        else:
            st.error(f"✗ Database file not found: {DATABASE_PATH}")
        
        # Show sample queries
        st.subheader("Sample Queries")
        for query in SAMPLE_QUERIES:
            st.write(f"• {query}")
            
        # Simple query interface
        st.subheader("Test Query Interface")
        query = st.text_input("Enter a simple SQL query:", "SELECT * FROM customers LIMIT 5")
        
        if st.button("Execute Query"):
            db = DatabaseManager()
            with db:
                df, error = db.execute_query(query)
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success("Query executed successfully!")
                    st.dataframe(df)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()