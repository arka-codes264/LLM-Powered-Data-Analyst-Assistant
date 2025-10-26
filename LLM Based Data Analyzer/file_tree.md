# LLM-Powered Data Analyst Assistant - File Structure

```
llm-data-analyst/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Configuration settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── query.py            # Query processing endpoints
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── schema.py           # Schema exploration endpoints
│   │   │   └── history.py          # Query history endpoints
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py             # Authentication middleware
│   │       ├── rate_limit.py       # Rate limiting middleware
│   │       └── logging.py          # Request logging middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── query_processor.py      # Main query processing logic
│   │   ├── langchain_orchestrator.py  # LangChain integration
│   │   ├── rag_pipeline.py         # RAG implementation
│   │   ├── sql_validator.py        # SQL validation and sanitization
│   │   └── conversation_memory.py  # Session context management
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py          # LLM API integration
│   │   ├── database_service.py     # Database connection and queries
│   │   ├── visualization_service.py # Chart generation
│   │   ├── insight_service.py      # AI insight generation
│   │   └── cache_service.py        # Redis caching
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLModel database models
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   └── enums.py                # Enum definitions
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py             # Security utilities
│   │   ├── validators.py           # Input validation
│   │   ├── embeddings.py           # Vector embedding utilities
│   │   └── logger.py               # Logging configuration
│   │
│   └── database/
│       ├── __init__.py
│       ├── connection.py           # Database connection setup
│       ├── migrations/             # Database migrations
│       │   └── versions/
│       └── seed_data/              # Sample data for testing
│           ├── sample_schema.sql
│           └── sample_data.sql
│
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py            # Main Streamlit application
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chat_interface.py       # Chat UI component
│   │   ├── query_results.py        # Results display component
│   │   ├── schema_explorer.py      # Schema browser component
│   │   ├── query_history.py        # History component
│   │   └── settings.py             # Settings component
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py           # API communication
│   │   ├── chart_renderer.py       # Chart rendering utilities
│   │   └── session_state.py        # Streamlit session management
│   └── assets/
│       ├── styles.css              # Custom CSS
│       └── images/                 # UI images and icons
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration
│   ├── unit/
│   │   ├── test_query_processor.py
│   │   ├── test_rag_pipeline.py
│   │   ├── test_sql_validator.py
│   │   └── test_visualization.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_service.py
│   │   └── test_llm_integration.py
│   └── e2e/
│       ├── test_complete_flow.py
│       └── test_streamlit_ui.py
│
├── scripts/
│   ├── setup_database.py           # Database initialization
│   ├── create_embeddings.py        # Generate schema embeddings
│   ├── benchmark_queries.py        # Performance testing
│   └── deploy.py                   # Deployment script
│
├── data/
│   ├── sample_databases/           # Sample SQLite databases
│   │   ├── ecommerce.db
│   │   ├── hr_analytics.db
│   │   └── sales_data.db
│   ├── embeddings/                 # FAISS vector stores
│   │   └── schema_embeddings.faiss
│   └── query_templates/            # Example queries
│       ├── ecommerce_queries.json
│       └── analytics_queries.json
│
├── docs/
│   ├── README.md
│   ├── api_documentation.md        # API endpoint documentation
│   ├── deployment_guide.md         # Deployment instructions
│   ├── user_guide.md              # End-user documentation
│   ├── architecture/               # Architecture diagrams
│   │   ├── system_architecture.png
│   │   ├── data_flow.png
│   │   └── security_model.png
│   └── examples/                   # Usage examples
│       ├── basic_queries.md
│       └── advanced_features.md
│
├── deployment/
│   ├── kubernetes/                 # K8s deployment files
│   │   ├── namespace.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   ├── docker/                     # Docker configurations
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.frontend
│   │   └── docker-compose.prod.yml
│   └── terraform/                  # Infrastructure as code
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
└── monitoring/
    ├── prometheus/                 # Monitoring configuration
    │   └── prometheus.yml
    ├── grafana/                    # Dashboard configurations
    │   └── dashboards/
    └── logs/                       # Log configurations
        └── logstash.conf
```

## Key File Descriptions

### Core Application Files

- **app/main.py**: FastAPI application entry point with middleware setup
- **app/core/query_processor.py**: Main orchestrator handling complete query lifecycle
- **app/core/rag_pipeline.py**: RAG implementation with FAISS vector store
- **app/services/llm_service.py**: LLM API integration with error handling and retry logic

### Frontend Components

- **frontend/streamlit_app.py**: Main Streamlit application with navigation
- **frontend/components/chat_interface.py**: Core chat UI with query input and results
- **frontend/components/query_results.py**: Results display with charts and insights

### Database and Models

- **app/models/database.py**: SQLModel definitions for all database entities
- **app/database/connection.py**: Database connection pooling and configuration
- **data/sample_databases/**: SQLite databases for testing and demonstration

### Testing Structure

- **tests/unit/**: Unit tests for individual components
- **tests/integration/**: Integration tests for API endpoints and services
- **tests/e2e/**: End-to-end tests including UI automation

### Deployment and Operations

- **deployment/kubernetes/**: Production Kubernetes deployment configurations
- **monitoring/**: Observability stack with Prometheus and Grafana
- **scripts/**: Utility scripts for setup, deployment, and maintenance

This structure supports:
- **Scalable Architecture**: Clear separation between API, frontend, and services
- **Testing**: Comprehensive test coverage at all levels
- **Deployment**: Multiple deployment options (Docker, Kubernetes, cloud)
- **Monitoring**: Production-ready observability and logging
- **Documentation**: Complete documentation for users and developers