# LLM-Powered Data Analyst Assistant - System Architecture

## Executive Summary

This document outlines the complete system architecture for a conversational data analyst platform that converts natural language queries to SQL, executes them securely, and provides insights with visualizations. The architecture is designed for scalability, security, and high availability while maintaining sub-10-second response times.

**Architecture Goals**:
- Handle 1000+ concurrent users
- 99.9% uptime with <3 second API response times
- Secure query execution with read-only database access
- Horizontal scaling for growing user base
- Cost-effective deployment starting with HuggingFace Spaces

---

## 1. Proven Workflow Pattern Architecture

### 1.1 Core Processing Pipeline

The system follows a validated 7-stage workflow pattern proven by successful implementations like ThoughtSpot and Microsoft Power BI Copilot:

```
User Query → Preprocessing → Schema Retrieval → LLM Processing → Validation → Execution → Visualization → NL Explanation
```

#### **Stage 1: User Query Preprocessing**
**Purpose**: Clean and prepare natural language input for optimal LLM processing

**Components**:
- Input sanitization and validation
- Query intent classification
- Context extraction from conversation history
- Ambiguity detection and clarification triggers

**Implementation**:
```python
class QueryPreprocessor:
    def preprocess(self, raw_query: str, context: ConversationContext) -> ProcessedQuery:
        # Sanitize input
        cleaned_query = self.sanitize_input(raw_query)
        
        # Extract intent
        intent = self.classify_intent(cleaned_query)
        
        # Add context
        contextualized_query = self.add_context(cleaned_query, context)
        
        # Detect ambiguity
        ambiguity_score = self.detect_ambiguity(contextualized_query)
        
        return ProcessedQuery(
            original=raw_query,
            cleaned=cleaned_query,
            intent=intent,
            context=contextualized_query,
            needs_clarification=ambiguity_score > 0.7
        )
```

#### **Stage 2: Schema Retrieval (RAG Pipeline)**
**Purpose**: Retrieve relevant database schema context to ground the LLM

**RAG Architecture**:
- Vector database (FAISS/Chroma) stores schema embeddings
- Semantic search retrieves relevant tables/columns
- Business context injection from company-specific metadata

**Implementation Flow**:
```
Query Embedding → Similarity Search → Context Ranking → Schema Assembly → Prompt Enhancement
```

#### **Stage 3: LLM Processing**
**Purpose**: Generate SQL query using retrieved schema context

**Configuration**:
- **Model**: GPT-4 (primary), Claude 3.5 (fallback)
- **Temperature**: 0 (deterministic output)
- **Max Tokens**: 1000 for SQL generation
- **Prompt Engineering**: Few-shot examples with error correction

#### **Stage 4: Query Validation**
**Purpose**: Ensure generated SQL is safe and syntactically correct

**Validation Layers**:
1. **Syntax Validation**: Parse SQL for syntax errors
2. **Security Validation**: Block DML operations (INSERT, UPDATE, DELETE)
3. **Performance Validation**: Estimate query complexity and execution time
4. **Schema Validation**: Verify tables and columns exist

#### **Stage 5: Secure Execution**
**Purpose**: Execute validated query in sandboxed environment

**Security Measures**:
- Read-only database connections
- Query timeout limits (30 seconds max)
- Result set size limits (10,000 rows max)
- Connection pooling with resource limits

#### **Stage 6: Visualization Generation**
**Purpose**: Automatically generate appropriate charts from query results

**Chart Selection Algorithm**:
```python
def select_visualization(result_data: DataFrame, query_intent: str) -> ChartType:
    if query_intent == "trend" and has_datetime_column(result_data):
        return ChartType.LINE
    elif query_intent == "comparison" and len(result_data) <= 10:
        return ChartType.BAR
    elif query_intent == "proportion" and is_categorical(result_data):
        return ChartType.PIE
    elif len(result_data) > 100:
        return ChartType.TABLE
    else:
        return ChartType.BAR  # Default
```

#### **Stage 7: Natural Language Explanation**
**Purpose**: Generate business insights in plain English

**Insight Categories**:
- Trend analysis ("Revenue increased 15% month-over-month")
- Anomaly detection ("Unusual spike detected on March 15th")
- Comparative analysis ("Premium products outperformed basic by 34%")
- Actionable recommendations ("Consider increasing inventory for top products")

---

## 2. Component Architecture

### 2.1 Microservices Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│   (JWT/OAuth)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query Engine  │◄──►│   LLM Service   │◄──►│   Vector Store  │
│   (Core Logic)  │    │   (LangChain)   │    │   (FAISS/Chroma)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DB Executor   │    │   Viz Service   │    │   Cache Layer   │
│   (SQLAlchemy)  │    │   (Plotly)      │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (PostgreSQL)  │
└─────────────────┘
```

### 2.2 Core Components

#### **API Gateway (FastAPI)**
**Responsibilities**:
- Request routing and load balancing
- Rate limiting and throttling
- Authentication and authorization
- Request/response logging
- Error handling and circuit breaking

**Key Endpoints**:
```python
@app.post("/api/v1/query")
async def process_query(request: QueryRequest, user: User = Depends(get_current_user)):
    """Main query processing endpoint"""
    
@app.get("/api/v1/databases/{db_id}/schema")
async def get_schema(db_id: str, user: User = Depends(get_current_user)):
    """Retrieve database schema information"""
    
@app.post("/api/v1/visualizations/generate")
async def generate_visualization(data: VisualizationRequest):
    """Generate chart from query results"""
```

#### **Query Engine (Core Service)**
**Architecture Pattern**: Command Pattern with Pipeline Processing

```python
class QueryEngine:
    def __init__(self):
        self.preprocessor = QueryPreprocessor()
        self.schema_retriever = SchemaRetriever()
        self.llm_service = LLMService()
        self.validator = QueryValidator()
        self.executor = QueryExecutor()
        self.visualizer = VisualizationService()
        self.insight_generator = InsightGenerator()
    
    async def process_query(self, query: str, context: Context) -> QueryResult:
        # Pipeline execution
        processed = await self.preprocessor.process(query, context)
        schema = await self.schema_retriever.retrieve(processed)
        sql = await self.llm_service.generate_sql(processed, schema)
        validated_sql = await self.validator.validate(sql)
        results = await self.executor.execute(validated_sql)
        visualization = await self.visualizer.create_chart(results)
        insights = await self.insight_generator.generate(results, query)
        
        return QueryResult(
            sql=validated_sql,
            data=results,
            visualization=visualization,
            insights=insights
        )
```

#### **LangChain Integration Service**
**Purpose**: Orchestrate LLM interactions with proper prompt engineering

```python
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_openai import ChatOpenAI

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.fallback_llm = ChatOpenAI(model="claude-3-5-sonnet", temperature=0)
        
    async def generate_sql(self, query: ProcessedQuery, schema: SchemaContext) -> str:
        # Create chain with schema context
        chain = create_sql_query_chain(
            llm=self.llm, 
            db=schema.database,
            prompt_template=self.get_enhanced_prompt(schema)
        )
        
        try:
            sql = await chain.ainvoke({"question": query.contextualized})
            return sql
        except Exception as e:
            # Fallback to alternative model
            return await self._fallback_generation(query, schema)
```

### 2.3 Database Layer Architecture

#### **Multi-Database Support**
```python
class DatabaseManager:
    def __init__(self):
        self.connections = {}
        self.connection_pools = {}
    
    def get_connection(self, db_config: DatabaseConfig) -> DatabaseConnection:
        """Get read-only connection with proper security"""
        if db_config.type == "postgresql":
            return PostgreSQLConnection(
                host=db_config.host,
                database=db_config.database,
                user=db_config.readonly_user,  # Read-only user
                password=db_config.readonly_password,
                options={"default_transaction_isolation": "read_only"}
            )
        elif db_config.type == "mysql":
            return MySQLConnection(...)
        elif db_config.type == "sqlite":
            return SQLiteConnection(...)
```

#### **Connection Security**
- **Read-Only Users**: Dedicated database users with SELECT-only permissions
- **Connection Pooling**: SQLAlchemy with connection limits
- **Query Timeouts**: 30-second maximum execution time
- **Resource Limits**: Maximum result set size of 10,000 rows

### 2.4 RAG Pipeline with FAISS/Chroma

#### **Vector Store Architecture**
```python
class SchemaVectorStore:
    def __init__(self, vector_db_type: str = "faiss"):
        if vector_db_type == "faiss":
            self.vector_store = FAISS.from_documents(
                documents=self.load_schema_documents(),
                embedding=OpenAIEmbeddings()
            )
        else:
            self.vector_store = Chroma.from_documents(
                documents=self.load_schema_documents(),
                embedding=OpenAIEmbeddings(),
                persist_directory="./chroma_db"
            )
    
    async def retrieve_relevant_schema(self, query: str, k: int = 5) -> List[SchemaElement]:
        """Retrieve most relevant schema elements"""
        docs = await self.vector_store.asimilarity_search(query, k=k)
        return [self.parse_schema_element(doc) for doc in docs]
```

#### **Schema Enhancement Pipeline**
```python
class SchemaEnhancer:
    def enhance_schema(self, raw_schema: DatabaseSchema) -> EnhancedSchema:
        """Add business context to raw database schema"""
        enhanced_tables = []
        
        for table in raw_schema.tables:
            # Add business descriptions
            business_description = self.get_business_description(table.name)
            
            # Enhance column metadata
            enhanced_columns = []
            for column in table.columns:
                enhanced_columns.append(EnhancedColumn(
                    name=column.name,
                    type=column.type,
                    description=self.get_column_description(table.name, column.name),
                    business_meaning=self.get_business_meaning(column.name),
                    sample_values=self.get_sample_values(table.name, column.name)
                ))
            
            enhanced_tables.append(EnhancedTable(
                name=table.name,
                description=business_description,
                columns=enhanced_columns
            ))
        
        return EnhancedSchema(tables=enhanced_tables)
```

---

## 3. Security Design

### 3.1 Multi-Layer Security Architecture

#### **Layer 1: API Security**
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: 100 requests per minute per user
- **Input Validation**: Comprehensive sanitization of all inputs

#### **Layer 2: Query Security**
- **SQL Injection Prevention**: Parameterized queries only
- **DML Operation Blocking**: Reject INSERT, UPDATE, DELETE, DROP
- **Query Complexity Analysis**: Block queries with high computational cost
- **Timeout Protection**: 30-second maximum execution time

#### **Layer 3: Database Security**
- **Read-Only Connections**: Dedicated users with SELECT-only permissions
- **Network Isolation**: Database in private subnet
- **Connection Encryption**: TLS 1.3 for all database connections
- **Audit Logging**: Complete query execution logs

#### **Layer 4: Infrastructure Security**
- **Container Isolation**: Each service in separate containers
- **Secret Management**: AWS Secrets Manager / HashiCorp Vault
- **Network Policies**: Kubernetes network policies for service isolation
- **Regular Security Scans**: Automated vulnerability scanning

### 3.2 Sandbox Execution Environment

```python
class SecureQueryExecutor:
    def __init__(self, db_connection: DatabaseConnection):
        self.connection = db_connection
        self.validator = QueryValidator()
        self.monitor = QueryMonitor()
    
    async def execute_query(self, sql: str) -> QueryResult:
        # Pre-execution validation
        validation_result = await self.validator.validate(sql)
        if not validation_result.is_safe:
            raise SecurityError(f"Unsafe query detected: {validation_result.reason}")
        
        # Execute with monitoring
        with self.monitor.track_execution():
            try:
                # Set connection to read-only mode
                await self.connection.execute("SET TRANSACTION READ ONLY")
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self.connection.execute(sql),
                    timeout=30.0
                )
                
                # Limit result size
                if len(result) > 10000:
                    result = result[:10000]
                    warnings.append("Result truncated to 10,000 rows")
                
                return QueryResult(data=result, warnings=warnings)
                
            except asyncio.TimeoutError:
                raise QueryTimeoutError("Query execution exceeded 30 seconds")
            except Exception as e:
                raise QueryExecutionError(f"Query failed: {str(e)}")
```

### 3.3 Data Privacy & Compliance

#### **GDPR Compliance**
- **Data Minimization**: Only store necessary query metadata
- **Right to Erasure**: Complete user data deletion capability
- **Data Portability**: Export user data in standard formats
- **Consent Management**: Clear opt-in/opt-out mechanisms

#### **SOC 2 Type II Preparation**
- **Access Controls**: Multi-factor authentication required
- **Audit Trails**: Comprehensive logging of all system activities
- **Data Encryption**: At-rest and in-transit encryption
- **Incident Response**: Automated alerting and response procedures

---

## 4. Scalability Considerations

### 4.1 Horizontal Scaling Architecture

#### **Auto-Scaling Configuration**
```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: query-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: query-engine
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### **Load Balancing Strategy**
- **API Gateway**: NGINX with round-robin load balancing
- **Database Connections**: Connection pooling with read replicas
- **Cache Distribution**: Redis Cluster for distributed caching
- **Geographic Distribution**: Multi-region deployment for global users

### 4.2 Performance Optimization

#### **Caching Strategy**
```python
class QueryCache:
    def __init__(self):
        self.redis_client = Redis(
            host='redis-cluster',
            port=6379,
            decode_responses=True
        )
        self.ttl_seconds = 3600  # 1 hour cache
    
    async def get_cached_result(self, query_hash: str) -> Optional[QueryResult]:
        """Retrieve cached query result"""
        cached_data = await self.redis_client.get(f"query:{query_hash}")
        if cached_data:
            return QueryResult.from_json(cached_data)
        return None
    
    async def cache_result(self, query_hash: str, result: QueryResult):
        """Cache query result with TTL"""
        await self.redis_client.setex(
            f"query:{query_hash}",
            self.ttl_seconds,
            result.to_json()
        )
```

#### **Database Optimization**
- **Read Replicas**: Route queries to read-only database replicas
- **Connection Pooling**: SQLAlchemy with optimized pool sizes
- **Query Optimization**: Automatic EXPLAIN plan analysis
- **Index Recommendations**: Suggest database indexes for common queries

### 4.3 Resource Management

#### **Memory Management**
```python
class ResourceManager:
    def __init__(self):
        self.max_concurrent_queries = 100
        self.memory_limit_mb = 512
        self.semaphore = asyncio.Semaphore(self.max_concurrent_queries)
    
    async def execute_with_limits(self, query_func):
        """Execute query with resource limits"""
        async with self.semaphore:
            # Monitor memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            try:
                result = await query_func()
                
                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024
                if current_memory - initial_memory > self.memory_limit_mb:
                    raise ResourceLimitError("Query exceeded memory limit")
                
                return result
            finally:
                # Cleanup resources
                gc.collect()
```

---

## 5. API Design

### 5.1 RESTful API Architecture

#### **Core API Endpoints**

**Query Processing**
```
POST /api/v1/query
Content-Type: application/json

{
  "question": "Show me top 5 products by revenue this month",
  "database_id": "db_123",
  "context": {
    "conversation_id": "conv_456",
    "previous_queries": ["..."]
  },
  "options": {
    "include_sql": true,
    "chart_type": "auto",
    "explain_insights": true
  }
}

Response:
{
  "query_id": "q_789",
  "sql": "SELECT product_name, SUM(revenue) FROM...",
  "data": [...],
  "visualization": {
    "type": "bar_chart",
    "config": {...},
    "url": "https://charts.api.com/chart_123.png"
  },
  "insights": [
    {
      "type": "trend",
      "message": "Revenue increased 15% compared to last month",
      "confidence": 0.95
    }
  ],
  "execution_time_ms": 1250,
  "cached": false
}
```

**Database Management**
```
POST /api/v1/databases
{
  "name": "E-commerce Production",
  "type": "postgresql",
  "connection": {
    "host": "db.company.com",
    "port": 5432,
    "database": "ecommerce",
    "username": "readonly_user",
    "password": "encrypted_password"
  }
}

GET /api/v1/databases/{db_id}/schema
Response:
{
  "tables": [
    {
      "name": "orders",
      "description": "Customer order records",
      "columns": [
        {
          "name": "order_id",
          "type": "integer",
          "description": "Unique order identifier",
          "sample_values": [1001, 1002, 1003]
        }
      ]
    }
  ]
}
```

#### **WebSocket API for Real-time Interaction**
```javascript
// WebSocket connection for real-time query processing
const ws = new WebSocket('wss://api.databot.com/ws/query');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'query',
    question: 'Show me daily sales trends',
    database_id: 'db_123'
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  
  switch(response.type) {
    case 'processing':
      console.log('Status:', response.status);
      break;
    case 'result':
      displayResults(response.data);
      break;
    case 'error':
      handleError(response.error);
      break;
  }
};
```

### 5.2 GraphQL API (Advanced)

```graphql
type Query {
  processQuery(
    question: String!
    databaseId: ID!
    options: QueryOptions
  ): QueryResult!
  
  databases: [Database!]!
  database(id: ID!): Database
}

type QueryResult {
  id: ID!
  sql: String!
  data: JSON!
  visualization: Visualization
  insights: [Insight!]!
  executionTimeMs: Int!
  cached: Boolean!
}

type Visualization {
  type: ChartType!
  config: JSON!
  imageUrl: String
  interactiveUrl: String
}

enum ChartType {
  BAR_CHART
  LINE_CHART
  PIE_CHART
  TABLE
  KPI_CARD
}
```

### 5.3 SDK Architecture

#### **Python SDK**
```python
from databot import DataBotClient

client = DataBotClient(
    api_key='your_api_key',
    base_url='https://api.databot.com'
)

# Simple query
result = await client.query(
    question="Show me top products",
    database_id="db_123"
)

# Advanced query with options
result = await client.query(
    question="Analyze sales trends",
    database_id="db_123",
    options={
        'chart_type': 'line',
        'include_insights': True,
        'cache_ttl': 3600
    }
)

print(f"SQL: {result.sql}")
print(f"Insights: {result.insights}")
result.visualization.save("chart.png")
```

#### **JavaScript SDK**
```javascript
import DataBot from '@databot/sdk';

const client = new DataBot({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.databot.com'
});

// Query with streaming results
const stream = client.queryStream({
  question: 'Show me revenue trends',
  databaseId: 'db_123'
});

stream.on('processing', (status) => {
  console.log('Processing:', status.message);
});

stream.on('result', (result) => {
  displayChart(result.visualization);
  showInsights(result.insights);
});

stream.on('error', (error) => {
  handleError(error);
});
```

---

## 6. Deployment Architecture

### 6.1 HuggingFace Spaces Deployment (MVP)

#### **Streamlit App Structure**
```
databot-spaces/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── packages.txt          # System packages
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── src/
│   ├── query_engine.py   # Core query processing
│   ├── llm_service.py    # LangChain integration
│   └── visualization.py  # Chart generation
└── data/
    └── sample_db.sqlite  # Sample e-commerce database
```

#### **Dockerfile for HuggingFace Spaces**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### **Environment Configuration**
```python
# config.py for HuggingFace Spaces
import os
import streamlit as st

class Config:
    # LLM Configuration
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    
    # Database Configuration
    DEFAULT_DB_PATH = "data/sample_db.sqlite"
    MAX_QUERY_TIME = 30
    MAX_RESULT_ROWS = 1000
    
    # Caching Configuration
    ENABLE_CACHING = True
    CACHE_TTL = 3600
    
    # UI Configuration
    PAGE_TITLE = "DataBot - AI Data Analyst"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
```

### 6.2 Production Deployment (Kubernetes)

#### **Microservices Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: databot-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: databot-api
  template:
    metadata:
      labels:
        app: databot-api
    spec:
      containers:
      - name: api
        image: databot/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: databot-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: databot-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: databot-api-service
spec:
  selector:
    app: databot-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### **Database Deployment**
```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: databot
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

### 6.3 CI/CD Pipeline

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/deploy.yml
name: Deploy DataBot

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t databot/api:${{ github.sha }} .
        docker tag databot/api:${{ github.sha }} databot/api:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push databot/api:${{ github.sha }}
        docker push databot/api:latest
    
    - name: Deploy to Kubernetes
      run: |
        echo ${{ secrets.KUBECONFIG }} | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/databot-api api=databot/api:${{ github.sha }}
        kubectl rollout status deployment/databot-api
```

### 6.4 Infrastructure as Code (Terraform)

#### **AWS Infrastructure**
```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "databot-cluster"
  cluster_version = "1.27"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  node_groups = {
    main = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1
      
      instance_types = ["t3.medium"]
      
      k8s_labels = {
        Environment = var.environment
        Application = "databot"
      }
    }
  }
}

# RDS Instance
resource "aws_db_instance" "postgres" {
  identifier = "databot-postgres"
  
  engine         = "postgres"
  engine_version = "14.9"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  
  db_name  = "databot"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  
  tags = {
    Name        = "databot-postgres"
    Environment = var.environment
  }
}

# Redis Cluster
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "databot-redis"
  description                = "Redis cluster for DataBot caching"
  
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name        = "databot-redis"
    Environment = var.environment
  }
}
```

---

## 7. Monitoring & Observability

### 7.1 Application Monitoring

#### **Metrics Collection**
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics definitions
query_counter = Counter('databot_queries_total', 'Total number of queries processed', ['status'])
query_duration = Histogram('databot_query_duration_seconds', 'Query processing time')
active_connections = Gauge('databot_active_connections', 'Number of active database connections')

class MetricsMiddleware:
    def __init__(self):
        self.start_time = time.time()
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            query_counter.labels(status='success').inc()
            return response
        except Exception as e:
            query_counter.labels(status='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            query_duration.observe(duration)
```

#### **Logging Configuration**
```python
import structlog
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/databot/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        'databot': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Structured logging
logger = structlog.get_logger("databot.query_engine")

async def process_query(query: str, user_id: str):
    logger.info(
        "query_started",
        query_id=generate_query_id(),
        user_id=user_id,
        query_length=len(query)
    )
    
    try:
        result = await execute_query(query)
        logger.info(
            "query_completed",
            query_id=result.query_id,
            execution_time_ms=result.execution_time_ms,
            result_rows=len(result.data)
        )
        return result
    except Exception as e:
        logger.error(
            "query_failed",
            query_id=query_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### 7.2 Performance Monitoring

#### **APM Integration (New Relic/DataDog)**
```python
import newrelic.agent

@newrelic.agent.function_trace()
async def generate_sql(query: str, schema: SchemaContext) -> str:
    """Generate SQL with performance tracking"""
    
    # Add custom attributes
    newrelic.agent.add_custom_attribute('query_length', len(query))
    newrelic.agent.add_custom_attribute('schema_tables', len(schema.tables))
    
    with newrelic.agent.BackgroundTask(application, 'sql_generation'):
        sql = await llm_service.generate_sql(query, schema)
        
        # Track SQL complexity
        complexity_score = calculate_sql_complexity(sql)
        newrelic.agent.add_custom_attribute('sql_complexity', complexity_score)
        
        return sql
```

#### **Health Check Endpoints**
```python
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/ready")
async def readiness_check():
    """Readiness check with dependency verification"""
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "llm_service": await check_llm_service(),
        "vector_store": await check_vector_store()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 7.3 Alerting & Incident Response

#### **Prometheus Alerting Rules**
```yaml
# alerts.yml
groups:
- name: databot.rules
  rules:
  - alert: HighErrorRate
    expr: rate(databot_queries_total{status="error"}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: SlowQueryResponse
    expr: histogram_quantile(0.95, rate(databot_query_duration_seconds_bucket[5m])) > 10
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Slow query response times"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionFailure
    expr: up{job="postgres"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database connection failure"
      description: "PostgreSQL database is not responding"
```

---

## 8. Disaster Recovery & Business Continuity

### 8.1 Backup Strategy

#### **Database Backups**
```bash
#!/bin/bash
# backup.sh - Automated database backup script

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="databot_backup_${DATE}.sql"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://databot-backups/postgres/

# Cleanup local backups older than 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

# Cleanup S3 backups older than 30 days
aws s3api list-objects-v2 --bucket databot-backups --prefix postgres/ \
  --query 'Contents[?LastModified<=`2023-01-01`].Key' --output text | \
  xargs -I {} aws s3 rm s3://databot-backups/{}
```

#### **Application State Backup**
```python
class StateBackupManager:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'databot-state-backups'
    
    async def backup_vector_store(self):
        """Backup FAISS/Chroma vector store"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Create vector store snapshot
        vector_store_path = f"/tmp/vector_store_{timestamp}"
        await self.vector_store.save(vector_store_path)
        
        # Upload to S3
        s3_key = f"vector_store/backup_{timestamp}.tar.gz"
        await self.upload_to_s3(vector_store_path, s3_key)
        
        # Cleanup local files
        shutil.rmtree(vector_store_path)
    
    async def backup_user_sessions(self):
        """Backup active user sessions and conversation history"""
        sessions = await self.session_manager.get_all_active_sessions()
        
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'sessions': sessions
        }
        
        s3_key = f"sessions/backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        await self.upload_json_to_s3(backup_data, s3_key)
```

### 8.2 High Availability Setup

#### **Multi-Region Deployment**
```yaml
# multi-region-config.yml
regions:
  primary:
    name: us-east-1
    services:
      - api-gateway
      - query-engine
      - database-primary
      - redis-primary
  
  secondary:
    name: us-west-2
    services:
      - api-gateway
      - query-engine
      - database-replica
      - redis-replica
  
  disaster_recovery:
    name: eu-west-1
    services:
      - database-backup
      - cold-storage

failover:
  automatic: true
  health_check_interval: 30s
  failover_threshold: 3
  recovery_time_objective: 5m
  recovery_point_objective: 1h
```

#### **Circuit Breaker Pattern**
```python
import asyncio
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def generate_sql_with_circuit_breaker(query, schema):
    try:
        return await llm_circuit_breaker.call(llm_service.generate_sql, query, schema)
    except Exception:
        # Fallback to template-based SQL generation
        return await template_sql_generator.generate(query, schema)
```

---

## 9. Cost Optimization

### 9.1 Resource Optimization

#### **LLM Cost Management**
```python
class LLMCostOptimizer:
    def __init__(self):
        self.cache = QueryCache()
        self.token_tracker = TokenUsageTracker()
        
    async def optimize_query_processing(self, query: str, context: Context) -> str:
        # Check cache first
        cache_key = self.generate_cache_key(query, context)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Optimize prompt to reduce tokens
        optimized_prompt = self.optimize_prompt(query, context)
        
        # Use cheaper model for simple queries
        if self.is_simple_query(query):
            model = "gpt-3.5-turbo"
        else:
            model = "gpt-4"
        
        # Track token usage
        with self.token_tracker.track_usage(model):
            result = await self.llm_service.generate(optimized_prompt, model)
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=3600)
        
        return result
    
    def optimize_prompt(self, query: str, context: Context) -> str:
        """Reduce prompt tokens while maintaining accuracy"""
        # Remove unnecessary schema information
        relevant_tables = self.identify_relevant_tables(query, context.schema)
        
        # Use abbreviated column descriptions
        abbreviated_schema = self.abbreviate_schema(relevant_tables)
        
        # Construct minimal prompt
        return self.build_minimal_prompt(query, abbreviated_schema)
```

#### **Database Connection Pooling**
```python
from sqlalchemy.pool import QueuePool

class OptimizedDatabaseManager:
    def __init__(self):
        self.engines = {}
    
    def get_engine(self, db_config: DatabaseConfig):
        """Get optimized database engine with connection pooling"""
        if db_config.id not in self.engines:
            self.engines[db_config.id] = create_engine(
                db_config.connection_string,
                poolclass=QueuePool,
                pool_size=5,          # Base number of connections
                max_overflow=10,      # Additional connections when needed
                pool_pre_ping=True,   # Verify connections before use
                pool_recycle=3600,    # Recycle connections every hour
                echo=False            # Disable SQL logging in production
            )
        
        return self.engines[db_config.id]
```

### 9.2 Infrastructure Cost Management

#### **Auto-Scaling Configuration**
```yaml
# cost-optimized-hpa.yml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: databot-cost-optimized-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: databot-api
  minReplicas: 1          # Minimum for cost savings
  maxReplicas: 20         # Scale up for demand
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80  # Higher threshold for cost optimization
  - type: Pods
    pods:
      metric:
        name: active_queries_per_pod
      target:
        type: AverageValue
        averageValue: "10"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 minutes before scaling down
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60   # Quick scale up for demand
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

## 10. Conclusion

This system architecture provides a robust, scalable, and secure foundation for the LLM-Powered Data Analyst Assistant. The design emphasizes:

### **Key Architectural Strengths**

1. **Proven Workflow Pattern**: Based on successful implementations like ThoughtSpot and Microsoft Power BI Copilot
2. **Security-First Design**: Multi-layer security with read-only database access and query validation
3. **Scalable Architecture**: Microservices with auto-scaling capabilities
4. **Cost-Optimized**: Intelligent caching and resource management
5. **High Availability**: Circuit breakers, failover mechanisms, and disaster recovery

### **Technical Excellence**

- **Query Accuracy**: Target >85% through RAG pipeline and schema awareness
- **Performance**: <10 second response times with intelligent caching
- **Security**: Comprehensive protection against SQL injection and data breaches
- **Scalability**: Handle 1000+ concurrent users with horizontal scaling

### **Implementation Readiness**

The architecture is designed for phased implementation:
- **Phase 1**: HuggingFace Spaces deployment for MVP validation
- **Phase 2**: Kubernetes deployment for production scaling
- **Phase 3**: Multi-region deployment for global availability

### **Business Value Delivery**

- **Time to Market**: Rapid deployment with proven technologies
- **Cost Efficiency**: Optimized resource usage and auto-scaling
- **Market Differentiation**: E-commerce focus with API-first approach
- **Enterprise Ready**: SOC 2 compliance preparation and enterprise security

**Next Steps**: This architecture document provides the technical foundation for Alex to implement the core LLM-Powered Data Analyst Assistant, with clear guidance on security, scalability, and deployment strategies.