import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import our custom modules
from database_manager import DatabaseManager
from sql_generator import SQLGenerator
from visualization_engine import VisualizationEngine
from insight_generator import InsightGenerator
from sample_data import create_sample_database
from config import APP_TITLE, APP_DESCRIPTION, SAMPLE_QUERIES, DATABASE_PATH

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    .success-message {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .error-message {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
</style>
""", unsafe_allow_html=True)

class DataAnalystApp:
    """Main application class for the AI Data Analyst Assistant."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.sql_generator = SQLGenerator()
        self.viz_engine = VisualizationEngine()
        self.insight_generator = InsightGenerator()
        
        # Initialize session state
        self._initialize_session_state()
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'query_count' not in st.session_state:
            st.session_state.query_count = 0
    
    def _initialize_database(self):
        """Initialize the sample database if it doesn't exist."""
        if not os.path.exists(DATABASE_PATH):
            with st.spinner("Setting up sample database..."):
                create_sample_database(DATABASE_PATH)
                st.success("Sample database created successfully!")
    
    def run(self):
        """Main application entry point."""
        
        # Header
        st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)
        st.markdown(APP_DESCRIPTION)
        
        # Sidebar
        self._render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_chat_interface()
        
        with col2:
            self._render_info_panel()
    
    def _render_sidebar(self):
        """Render the sidebar with database info and settings."""
        
        st.sidebar.header("🗄️ Database Information")
        
        # Database schema
        with st.sidebar.expander("View Database Schema", expanded=False):
            try:
                schema_info = self.db_manager.get_schema_info()
                st.code(schema_info, language="sql")
            except Exception as e:
                st.error(f"Error loading schema: {e}")
        
        # Sample queries
        st.sidebar.header("💡 Sample Questions")
        st.sidebar.markdown("Try asking these questions:")
        
        for i, query in enumerate(SAMPLE_QUERIES):
            if st.sidebar.button(f"📊 {query}", key=f"sample_{i}"):
                st.session_state.current_query = query
                st.rerun()
        
        # Settings
        st.sidebar.header("⚙️ Settings")
        
        # API Key status
        api_key_status = "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Not Set"
        st.sidebar.markdown(f"**OpenAI API:** {api_key_status}")
        
        if api_key_status == "❌ Not Set":
            st.sidebar.warning("Set OPENAI_API_KEY environment variable for AI features")
        
        # Clear chat history
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.query_count = 0
            st.rerun()
    
    def _render_chat_interface(self):
        """Render the main chat interface."""
        
        st.header("💬 Ask Your Data Questions")
        
        # Display chat history
        self._display_chat_history()
        
        # Query input
        query_input = st.text_input(
            "What would you like to know about your data?",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., Show me total sales by month",
            key="query_input"
        )
        
        # Process query button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 Analyze Data", type="primary"):
                if query_input.strip():
                    self._process_query(query_input.strip())
                    # Clear the current_query from session state
                    if 'current_query' in st.session_state:
                        del st.session_state.current_query
                else:
                    st.warning("Please enter a question about your data.")
        
        with col2:
            if st.button("🔄 Generate SQL Only"):
                if query_input.strip():
                    self._generate_sql_only(query_input.strip())
        
        with col3:
            if st.button("📋 Example"):
                st.session_state.current_query = SAMPLE_QUERIES[0]
                st.rerun()
    
    def _display_chat_history(self):
        """Display the chat history."""
        
        if not st.session_state.chat_history:
            st.info("👋 Welcome! Ask me anything about your data. I'll convert your questions to SQL and provide insights.")
            return
        
        # Display messages in reverse order (newest first)
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            timestamp = message.get('timestamp', 'Unknown time')
            
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message">
                    <strong>🧑 You ({timestamp}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            
            elif message['type'] == 'assistant':
                success_class = "success-message" if message.get('success', True) else "error-message"
                st.markdown(f"""
                <div class="chat-message {success_class}">
                    <strong>🤖 AI Assistant ({timestamp}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Display SQL query if available
                if 'sql' in message:
                    st.code(message['sql'], language='sql')
                
                # Display visualization if available
                if 'figure' in message:
                    st.plotly_chart(message['figure'], use_container_width=True)
                
                # Display data table if available
                if 'dataframe' in message and not message['dataframe'].empty:
                    with st.expander("📊 View Raw Data", expanded=False):
                        st.dataframe(message['dataframe'], use_container_width=True)
    
    def _process_query(self, user_query: str):
        """Process a user query end-to-end."""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add user message to chat history
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_query,
            'timestamp': timestamp
        })
        
        # Generate SQL
        with st.spinner("🧠 Converting your question to SQL..."):
            sql_query, sql_error = self.sql_generator.generate_sql(user_query)
        
        if sql_error:
            # Handle SQL generation error
            error_message = f"❌ **Error generating SQL:** {sql_error}"
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': error_message,
                'timestamp': timestamp,
                'success': False
            })
            st.rerun()
            return
        
        # Execute SQL
        with st.spinner("📊 Executing query..."):
            df, exec_error = self.db_manager.execute_query(sql_query)
        
        if exec_error:
            # Try to improve the query
            with st.spinner("🔧 Attempting to fix the query..."):
                improved_sql, improve_error = self.sql_generator.improve_query(sql_query, exec_error, user_query)
            
            if not improve_error:
                df, exec_error = self.db_manager.execute_query(improved_sql)
                if not exec_error:
                    sql_query = improved_sql  # Use the improved query
        
        if exec_error:
            error_message = f"❌ **Query execution failed:** {exec_error}"
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': error_message,
                'sql': sql_query,
                'timestamp': timestamp,
                'success': False
            })
            st.rerun()
            return
        
        # Generate visualization
        with st.spinner("📈 Creating visualization..."):
            figure = self.viz_engine.create_visualization(df, sql_query)
        
        # Generate insights
        with st.spinner("🔍 Analyzing results..."):
            insights = self.insight_generator.generate_insights(sql_query, df)
        
        # Prepare response message
        response_parts = []
        
        if not df.empty:
            response_parts.append(f"✅ **Query executed successfully!** Found {len(df)} result(s).")
        else:
            response_parts.append("✅ **Query executed successfully** but returned no results.")
        
        # Add query explanation
        query_explanation = self.sql_generator.explain_query(sql_query)
        response_parts.append(f"\n**What this query does:** {query_explanation}")
        
        # Add insights
        response_parts.append(f"\n**📊 Insights:**\n{insights}")
        
        # Add suggestions for follow-up queries
        suggestions = self.insight_generator.generate_query_suggestions(sql_query, df)
        if suggestions:
            response_parts.append(f"\n**💡 Suggested follow-up questions:**")
            for suggestion in suggestions[:3]:
                response_parts.append(f"• {suggestion}")
        
        # Add assistant message to chat history
        assistant_message = {
            'type': 'assistant',
            'content': '\n'.join(response_parts),
            'sql': sql_query,
            'timestamp': timestamp,
            'success': True
        }
        
        if figure:
            assistant_message['figure'] = figure
        
        if not df.empty:
            assistant_message['dataframe'] = df
        
        st.session_state.chat_history.append(assistant_message)
        st.session_state.query_count += 1
        
        st.rerun()
    
    def _generate_sql_only(self, user_query: str):
        """Generate SQL without executing it."""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add user message
        st.session_state.chat_history.append({
            'type': 'user',
            'content': f"[SQL Only] {user_query}",
            'timestamp': timestamp
        })
        
        # Generate SQL
        with st.spinner("🧠 Converting your question to SQL..."):
            sql_query, sql_error = self.sql_generator.generate_sql(user_query)
        
        if sql_error:
            error_message = f"❌ **Error generating SQL:** {sql_error}"
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': error_message,
                'timestamp': timestamp,
                'success': False
            })
        else:
            # Validate the SQL
            is_valid, validation_message = self.db_manager.validate_query(sql_query)
            
            if is_valid:
                response = f"✅ **SQL generated successfully:**\n\n**Explanation:** {self.sql_generator.explain_query(sql_query)}"
            else:
                response = f"⚠️ **SQL generated but validation failed:** {validation_message}"
            
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': response,
                'sql': sql_query,
                'timestamp': timestamp,
                'success': is_valid
            })
        
        st.rerun()
    
    def _render_info_panel(self):
        """Render the information panel."""
        
        st.header("📈 Session Stats")
        
        # Query statistics
        st.metric("Queries Processed", st.session_state.query_count)
        st.metric("Chat Messages", len(st.session_state.chat_history))
        
        # Database info
        st.header("🗄️ Database Overview")
        
        try:
            with self.db_manager:
                table_names = self.db_manager.get_table_names()
                
                st.markdown("**Available Tables:**")
                for table in table_names:
                    st.markdown(f"• {table}")
                
                # Show sample data from first table
                if table_names:
                    st.markdown(f"\n**Sample from {table_names[0]}:**")
                    sample_df, _ = self.db_manager.execute_query(f"SELECT * FROM {table_names[0]} LIMIT 3")
                    if not sample_df.empty:
                        st.dataframe(sample_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading database info: {e}")
        
        # Tips and help
        st.header("💡 Tips")
        
        tips = [
            "Start with simple questions like 'How many customers do we have?'",
            "Use specific time periods: 'Show sales from last month'",
            "Ask for comparisons: 'Which product category sells the most?'",
            "Request visualizations: 'Show me a chart of monthly revenue'",
            "Be specific about what you want to see"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

# Main application entry point
def main():
    """Main function to run the Streamlit app."""
    app = DataAnalystApp()
    app.run()

if __name__ == "__main__":
    main()