import os
from typing import Dict, Any

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
MODEL_NAME = "gpt-4"
TEMPERATURE = 0  # Deterministic SQL generation

# Database Configuration
DATABASE_PATH = "data_analyst.db"
MAX_QUERY_RESULTS = 100

# Application Settings
APP_TITLE = "🤖 AI Data Analyst Assistant"
APP_DESCRIPTION = """
Transform your data questions into instant insights! 
Ask me anything about your business data in plain English.
"""

# Sample queries for user guidance
SAMPLE_QUERIES = [
    "Show me total sales by month",
    "Which products have the highest revenue?",
    "How many customers do we have?",
    "What's the average order value?",
    "Show me top 5 customers by total purchases"
]

# SQL Generation Prompts
SYSTEM_PROMPT = """You are an expert SQL analyst. Convert natural language questions to SQL queries.

IMPORTANT RULES:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE)
2. Always use proper SQL syntax for SQLite
3. Include appropriate WHERE, GROUP BY, ORDER BY clauses as needed
4. Limit results to 100 rows maximum
5. Use table and column names exactly as provided in the schema

Available Tables and Schema:
{schema_info}

Generate only the SQL query without explanations or markdown formatting."""

INSIGHT_PROMPT = """Analyze the following SQL query results and provide business insights in plain English.

Query: {query}
Results: {results}

Provide:
1. A summary of what the data shows
2. Key insights or patterns
3. Business implications (if any)

Keep the response concise and actionable."""