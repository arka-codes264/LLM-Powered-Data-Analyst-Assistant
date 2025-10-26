import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Tuple
import streamlit as st

class VisualizationEngine:
    """Automatically generates appropriate visualizations based on query results."""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_visualization(self, df: pd.DataFrame, query: str) -> Optional[go.Figure]:
        """
        Automatically create appropriate visualization based on data characteristics.
        
        Args:
            df: DataFrame with query results
            query: Original SQL query for context
            
        Returns:
            Plotly figure or None if visualization not suitable
        """
        if df.empty or len(df.columns) < 1:
            return None
        
        try:
            # Determine the best chart type based on data characteristics
            chart_type = self._determine_chart_type(df, query)
            
            if chart_type == "bar":
                return self._create_bar_chart(df)
            elif chart_type == "line":
                return self._create_line_chart(df)
            elif chart_type == "pie":
                return self._create_pie_chart(df)
            elif chart_type == "scatter":
                return self._create_scatter_plot(df)
            elif chart_type == "table":
                return self._create_table_visualization(df)
            else:
                return None
                
        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")
            return None
    
    def _determine_chart_type(self, df: pd.DataFrame, query: str) -> str:
        """Determine the most appropriate chart type for the data."""
        
        num_cols = len(df.columns)
        num_rows = len(df)
        
        # Analyze column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        date_cols = []
        
        # Check for date columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].iloc[0])
                    date_cols.append(col)
                except:
                    pass
        
        # Decision logic for chart type
        if num_rows > 50:
            return "table"  # Too many rows for effective visualization
        
        if len(numeric_cols) == 0:
            return "table"  # No numeric data to visualize
        
        # Time series data
        if date_cols and len(numeric_cols) >= 1:
            return "line"
        
        # Single numeric column with categories
        if len(numeric_cols) == 1 and len(text_cols) >= 1:
            if num_rows <= 10:
                # Check if it's suitable for pie chart (percentages, parts of whole)
                query_lower = query.lower()
                if any(keyword in query_lower for keyword in ['percentage', 'share', 'proportion', 'distribution']):
                    return "pie"
                return "bar"
            else:
                return "bar"
        
        # Two numeric columns
        if len(numeric_cols) >= 2:
            return "scatter"
        
        # Default to table for complex data
        return "table"
    
    def _create_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a bar chart from the data."""
        
        # Find the best columns for x and y
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if not numeric_cols:
            return self._create_table_visualization(df)
        
        y_col = numeric_cols[0]  # First numeric column for y-axis
        x_col = text_cols[0] if text_cols else df.columns[0]  # First text column or first column for x-axis
        
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col,
            title=f"{y_col} by {x_col}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=False
        )
        
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a line chart for time series data."""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Try to find date column
        date_col = None
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].iloc[0])
                    date_col = col
                    break
                except:
                    continue
        
        if not date_col:
            date_col = df.columns[0]  # Use first column as x-axis
        
        y_col = numeric_cols[0] if numeric_cols else df.columns[1]
        
        fig = px.line(
            df,
            x=date_col,
            y=y_col,
            title=f"{y_col} over {date_col}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            xaxis_title=date_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a pie chart for categorical data with values."""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if not numeric_cols or not text_cols:
            return self._create_bar_chart(df)
        
        labels_col = text_cols[0]
        values_col = numeric_cols[0]
        
        fig = px.pie(
            df,
            names=labels_col,
            values=values_col,
            title=f"Distribution of {values_col} by {labels_col}",
            color_discrete_sequence=self.color_palette
        )
        
        return fig
    
    def _create_scatter_plot(self, df: pd.DataFrame) -> go.Figure:
        """Create a scatter plot for two numeric variables."""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return self._create_bar_chart(df)
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=f"{y_col} vs {x_col}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _create_table_visualization(self, df: pd.DataFrame) -> go.Figure:
        """Create a formatted table visualization."""
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='lightblue',
                align='left',
                font=dict(size=12, color='white')
            ),
            cells=dict(
                values=[df[col].tolist() for col in df.columns],
                fill_color='white',
                align='left',
                font=dict(size=11)
            )
        )])
        
        fig.update_layout(
            title="Query Results",
            height=min(400, 50 + len(df) * 30)  # Dynamic height based on rows
        )
        
        return fig
    
    def get_chart_summary(self, df: pd.DataFrame, chart_type: str) -> str:
        """Generate a summary of what the chart shows."""
        
        if df.empty:
            return "No data to display."
        
        num_rows = len(df)
        num_cols = len(df.columns)
        
        summaries = {
            "bar": f"Bar chart showing {num_rows} categories with their corresponding values.",
            "line": f"Line chart displaying trends across {num_rows} data points.",
            "pie": f"Pie chart showing the distribution across {num_rows} categories.",
            "scatter": f"Scatter plot comparing two variables across {num_rows} data points.",
            "table": f"Data table with {num_rows} rows and {num_cols} columns."
        }
        
        return summaries.get(chart_type, f"Visualization of {num_rows} data points.")