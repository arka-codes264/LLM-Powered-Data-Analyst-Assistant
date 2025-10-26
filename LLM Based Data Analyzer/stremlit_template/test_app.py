#!/usr/bin/env python3
"""
Simple test script to verify all components work correctly.
"""

def test_imports():
    """Test all imports."""
    try:
        import streamlit as st
        print("✓ Streamlit import successful")
        
        from database_manager import DatabaseManager
        print("✓ DatabaseManager import successful")
        
        from sql_generator import SQLGenerator
        print("✓ SQLGenerator import successful")
        
        from visualization_engine import VisualizationEngine
        print("✓ VisualizationEngine import successful")
        
        from insight_generator import InsightGenerator
        print("✓ InsightGenerator import successful")
        
        from config import APP_TITLE, APP_DESCRIPTION, SAMPLE_QUERIES, DATABASE_PATH
        print("✓ Config import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database functionality."""
    try:
        from database_manager import DatabaseManager
        
        db = DatabaseManager()
        db.connect()
        
        # Test schema info
        schema = db.get_schema_info()
        print(f"✓ Schema info retrieved ({len(schema)} characters)")
        
        # Test query execution
        df, error = db.execute_query("SELECT COUNT(*) as total_customers FROM customers")
        if error:
            print(f"✗ Query error: {error}")
            return False
        else:
            print(f"✓ Query executed successfully, result: {df.iloc[0]['total_customers']} customers")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_generator():
    """Test SQL generator (without API key)."""
    try:
        from sql_generator import SQLGenerator
        
        sql_gen = SQLGenerator()
        print("✓ SQL Generator initialized")
        
        if sql_gen.client:
            print("✓ OpenAI client available")
        else:
            print("⚠ OpenAI client not available (API key not set) - this is expected")
        
        return True
        
    except Exception as e:
        print(f"✗ SQL Generator error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=== Testing LLM Data Analyst Assistant Components ===\n")
    
    print("1. Testing imports...")
    if not test_imports():
        return False
    
    print("\n2. Testing database...")
    if not test_database():
        return False
    
    print("\n3. Testing SQL generator...")
    if not test_sql_generator():
        return False
    
    print("\n=== All tests passed! ===")
    print("The application should work correctly.")
    print("Note: OpenAI features will be limited without API key, but basic functionality should work.")
    return True

if __name__ == "__main__":
    main()