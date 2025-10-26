# LLM-Powered Data Analyst Assistant - MVP Development Plan

## Project Overview
Building a chat-based data analyst that converts natural language queries to SQL, executes them, and returns insights with visualizations. This MVP focuses on core functionality with simple queries initially.

## Core Files to Create (Max 8 files - HARD LIMIT)

### 1. **app.py** - Main Streamlit Application
- Chat interface for natural language queries
- Display SQL generation, execution results, and visualizations
- Handle user sessions and conversation history
- Integration with all backend components

### 2. **database_manager.py** - Database Operations
- SQLite database setup with sample e-commerce data (orders, products, customers)
- Schema introspection and metadata extraction
- Safe query execution (read-only)
- Connection management

### 3. **sql_generator.py** - LLM-Powered SQL Generation
- LangChain integration with OpenAI GPT-4
- Natural language to SQL conversion
- Query validation and error handling
- Schema-aware prompt engineering

### 4. **visualization_engine.py** - Auto Visualization
- Plotly chart generation based on SQL results
- Chart type detection (bar, line, pie) from data structure
- Dynamic visualization rendering

### 5. **insight_generator.py** - AI Insights
- GPT-powered insight summarization
- Plain English explanations of data patterns
- Business context interpretation

### 6. **schema_retriever.py** - RAG for Schema Awareness
- FAISS vector store for table/column embeddings
- Semantic search for relevant schema components
- Business-friendly metadata management

### 7. **sample_data.py** - Sample Database Setup
- Create SQLite database with realistic e-commerce data
- Sample tables: customers, orders, products, order_items
- Populate with meaningful test data

### 8. **config.py** - Configuration Management
- API keys and model settings
- Database connection strings
- Application constants and prompts

## Implementation Strategy

### Phase 1: Core MVP (Simple Queries Only)
1. Basic chat interface in Streamlit
2. Simple SELECT queries without JOINs
3. SQLite with 3-5 tables maximum
4. Basic visualization (bar/line charts)
5. Query validation before execution

### Phase 2: Enhanced Features
1. Multi-table JOIN queries
2. Insight summarization with GPT
3. RAG-based schema retrieval
4. Advanced visualizations

### Success Metrics
- Query accuracy: >85% for simple queries
- Time to insight: <10 seconds
- User retry rate: <20%
- SQL validation pass rate: >90%

## Tech Stack Validation
- ✅ Core: Python, LangChain, OpenAI GPT-4
- ✅ Database: SQLite (MVP) → PostgreSQL (production)
- ✅ Embeddings: FAISS for vector search
- ✅ Backend: Streamlit (integrated)
- ✅ Frontend: Streamlit interface
- ✅ Visualization: Plotly for dynamic charts

## Key Constraints
- Start with simple SELECT queries only
- Maximum 5 database tables
- Read-only database operations
- Focus on e-commerce use case for niche positioning
- Progressive complexity based on user feedback