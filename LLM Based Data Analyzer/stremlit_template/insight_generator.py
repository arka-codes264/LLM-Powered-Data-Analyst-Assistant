import openai
import pandas as pd
from typing import List
from config import OPENAI_API_KEY, MODEL_NAME, INSIGHT_PROMPT

class InsightGenerator:
    """Generates business insights from query results using AI."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY != "your-openai-api-key-here" else None
    
    def generate_insights(self, query: str, df: pd.DataFrame) -> str:
        """
        Generate business insights from SQL query results.
        
        Args:
            query: The SQL query that was executed
            df: DataFrame containing the query results
            
        Returns:
            AI-generated insights in plain English
        """
        if not self.client:
            return self._generate_basic_insights(df)
        
        if df.empty:
            return "No data returned from the query. Consider adjusting your question or checking if the data exists."
        
        try:
            # Prepare data summary for the AI
            data_summary = self._prepare_data_summary(df)
            
            # Create the prompt
            prompt = INSIGHT_PROMPT.format(
                query=query,
                results=data_summary
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a business analyst who provides actionable insights from data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating AI insights: {str(e)}\n\n{self._generate_basic_insights(df)}"
    
    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare a concise summary of the data for AI analysis."""
        
        if len(df) == 0:
            return "No data"
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset contains {len(df)} rows and {len(df.columns)} columns.")
        
        # Column information
        summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Show first few rows (limit to avoid token overflow)
        if len(df) <= 10:
            summary_parts.append("All data:")
            summary_parts.append(df.to_string(index=False))
        else:
            summary_parts.append("Sample data (first 5 rows):")
            summary_parts.append(df.head().to_string(index=False))
        
        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary_parts.append("\nNumeric column statistics:")
            for col in numeric_cols:
                stats = df[col].describe()
                summary_parts.append(f"{col}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}")
        
        return "\n".join(summary_parts)
    
    def _generate_basic_insights(self, df: pd.DataFrame) -> str:
        """Generate basic insights without AI when API is not available."""
        
        if df.empty:
            return "📊 **Basic Analysis**: No data returned from your query."
        
        insights = ["📊 **Basic Data Analysis**:"]
        
        # Row count insight
        row_count = len(df)
        if row_count == 1:
            insights.append(f"• Found exactly 1 result")
        else:
            insights.append(f"• Found {row_count} results")
        
        # Analyze numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            col_data = df[col]
            if not col_data.empty:
                total = col_data.sum()
                avg = col_data.mean()
                max_val = col_data.max()
                min_val = col_data.min()
                
                insights.append(f"• **{col.replace('_', ' ').title()}**: Total = {total:,.2f}, Average = {avg:,.2f}")
                
                if max_val != min_val:
                    insights.append(f"  - Range: {min_val:,.2f} to {max_val:,.2f}")
        
        # Analyze categorical columns
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in text_cols:
            unique_count = df[col].nunique()
            if unique_count > 1:
                insights.append(f"• **{col.replace('_', ' ').title()}**: {unique_count} unique values")
                
                # Show top categories if reasonable number
                if unique_count <= 5:
                    top_values = df[col].value_counts().head(3)
                    insights.append(f"  - Most common: {', '.join([f'{k} ({v})' for k, v in top_values.items()])}")
        
        # Data quality insights
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            insights.append(f"• ⚠️ Found {missing_data} missing values in the dataset")
        
        return "\n".join(insights)
    
    def generate_query_suggestions(self, current_query: str, df: pd.DataFrame) -> List[str]:
        """Generate follow-up query suggestions based on current results."""
        
        suggestions = []
        
        if df.empty:
            return ["Try a different time period", "Check if the data exists", "Verify table and column names"]
        
        # Analyze the data to suggest relevant follow-ups
        numeric_cols = df.select_dtypes(include=['number']).columns
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        
        # Suggest aggregations
        if len(df) > 1 and len(numeric_cols) > 0:
            suggestions.append(f"Show average {numeric_cols[0]} by category")
            suggestions.append(f"Find the top 5 highest {numeric_cols[0]} values")
        
        # Suggest filtering
        if len(text_cols) > 0:
            unique_vals = df[text_cols[0]].unique()
            if len(unique_vals) > 1:
                suggestions.append(f"Filter results by {text_cols[0]}")
        
        # Suggest time-based analysis if date columns exist
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                suggestions.append("Show trends over time")
                suggestions.append("Compare this month vs last month")
                break
        
        # Generic useful suggestions
        suggestions.extend([
            "Show me the total count",
            "Group results by category",
            "Find the minimum and maximum values"
        ])
        
        return suggestions[:5]  # Return top 5 suggestions