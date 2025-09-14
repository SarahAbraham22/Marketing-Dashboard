import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_and_process_data
from ai_insights import ask_ai

st.set_page_config(page_title="Marketing Intelligence Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Font & Layout ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif !important;
    }
    
    .header-container {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .main-title {
        color: #1f2937;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
    }
    .sub-title {
        color: #6b7280;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Style the top control panel */
    .st-emotion-cache-1c9v96r { /* A specific class for top-level columns */
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process data, with caching to prevent re-running on every interaction."""
    return load_and_process_data()

def create_chart(data, chart_type, x, y, title, **kwargs):
    """
    Dynamically creates Plotly charts based on a specified type.
    """
    if chart_type == "bar":
        fig = px.bar(data, x=x, y=y, title=title, **kwargs)
    elif chart_type == "scatter":
        fig = px.scatter(data, x=x, y=y, title=title, **kwargs)
    fig.update_layout(
        title_font_size=20,
        title_font_color="#333",
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        legend_title_font_size=14,
        font_family="Roboto",  # Ensure chart fonts also match
    )
    return fig

def format_compact(num):
    """Formats large numbers into a compact, human-readable string (e.g., 1.2M)."""
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.2f}K"
    return f"{num:.0f}"

def show_header():
    """Displays a clean, centered header for the dashboard."""
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Marketing Intelligence Dashboard</h1>
        <p class="sub-title">AI-Powered Marketing Analytics</p>
    </div>
    """, unsafe_allow_html=True)

def show_executive_summary(filtered_marketing, filtered_business):
    """Displays key metrics in a visually appealing card layout."""
    st.subheader("Executive Summary")
    st.divider()

    total_spend = filtered_marketing['spend'].sum()
    total_revenue = filtered_marketing['attributed revenue'].sum()
    roas = total_revenue / total_spend if total_spend > 0 else 0
    total_orders = filtered_business['# of orders'].sum() if len(filtered_business) > 0 else 0
    new_customers = filtered_business['new customers'].sum() if len(filtered_business) > 0 else 0
    cac = total_spend / new_customers if new_customers > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Marketing Spend", f"${format_compact(total_spend)}")
    with col2:
        st.metric("Attributed Revenue", f"${format_compact(total_revenue)}")
    with col3:
        st.metric("ROAS", f"{roas:.2f}x")
    with col4:
        st.metric("Total Orders", f"{format_compact(total_orders)}")
    with col5:
        st.metric("CAC", f"${format_compact(cac)}")

def show_channel_performance(filtered_marketing):
    """Renders the Channel Performance section."""
    st.subheader("Channel Performance")
    st.divider()
    if not filtered_marketing.empty:
        channel_analysis = filtered_marketing.groupby('platform').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean'}).round(2)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_chart(channel_analysis.reset_index(), "bar", 'platform', 'roas', "ROAS by Platform", color='roas', color_continuous_scale='RdYlGn'), use_container_width=True)
        with col2:
            st.plotly_chart(create_chart(channel_analysis.reset_index(), "scatter", 'spend', 'attributed revenue', "Marketing Efficiency", size='roas', color='platform', color_discrete_map={'Facebook': '#1877F2', 'Google': '#4285F4', 'TikTok': '#000000'}), use_container_width=True)
    else:
        st.info("No marketing data available for the selected filters.")

def show_geographic_analysis(filtered_marketing):
    """Renders the Geographic Analysis section."""
    st.subheader("Geographic Analysis")
    st.divider()
    if not filtered_marketing.empty:
        state_analysis = filtered_marketing.groupby('state').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean'}).round(2)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_chart(state_analysis.reset_index(), "bar", 'state', 'roas', "ROAS by State", color='roas', color_continuous_scale='RdYlGn'), use_container_width=True)
        with col2:
            st.plotly_chart(create_chart(state_analysis.reset_index(), "scatter", 'spend', 'attributed revenue', "Market Opportunity", size='roas', color='state', color_discrete_map={'CA': '#FF6B6B', 'NY': '#4ECDC4'}), use_container_width=True)
    else:
        st.info("No geographic data available for the selected filters.")

def show_performance_trends(filtered_marketing):
    """Renders the Performance Trends section."""
    st.subheader("Performance Trends")
    st.divider()
    if not filtered_marketing.empty:
        daily_data = filtered_marketing.groupby('date').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean'}).reset_index()
        daily_data['spend_growth'] = daily_data['spend'].pct_change() * 100
        
        # Plotly Subplots for a unified trend view
        fig = make_subplots(rows=2, cols=2, subplot_titles=('Marketing Spend', 'Revenue Generation', 'ROAS Performance', 'Growth Rate'))
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['spend'], name='Spend', line=dict(color='#1f77b4')), row=1, col=1)
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['attributed revenue'], name='Revenue', line=dict(color='#2ca02c')), row=1, col=2)
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['roas'], name='ROAS', line=dict(color='#ff7f0e')), row=2, col=1)
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['spend_growth'], name='Growth', line=dict(color='#d62728')), row=2, col=2)
        
        fig.update_layout(height=600, showlegend=False, font_family="Roboto")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available for the selected filters.")

def show_business_impact(filtered_marketing, filtered_business):
    """Renders the Business Impact section."""
    st.subheader("Business Impact")
    st.divider()
    if not filtered_business.empty and not filtered_marketing.empty:
        daily_marketing = filtered_marketing.groupby('date').agg({'spend': 'sum', 'attributed revenue': 'sum'}).reset_index()
        daily_business = filtered_business.groupby('date').agg({'# of orders': 'sum', 'total revenue': 'sum'}).reset_index()
        combined = daily_marketing.merge(daily_business, on='date', how='inner')

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_chart(combined, "scatter", 'spend', '# of orders', "Spend Impact on Orders", color='attributed revenue', color_continuous_scale='RdYlGn'), use_container_width=True)
        with col2:
            st.plotly_chart(create_chart(combined, "scatter", 'attributed revenue', 'total revenue', "Attributed vs Total Revenue", color_continuous_scale='RdYlGn'), use_container_width=True)

def show_strategic_recommendations(filtered_marketing):
    """Renders the Strategic Recommendations and Insights section."""
    st.subheader("Strategic Recommendations")
    st.divider()
    if not filtered_marketing.empty:
        total_spend = filtered_marketing['spend'].sum()
        total_revenue = filtered_marketing['attributed revenue'].sum()
        roas = total_revenue / total_spend if total_spend > 0 else 0

        channel_performance = filtered_marketing.groupby('platform').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean', 'ctr': 'mean', 'cpc': 'mean'}).round(2)
        state_performance = filtered_marketing.groupby('state').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean'}).round(2)
        tactic_performance = filtered_marketing.groupby('tactic').agg({'spend': 'sum', 'attributed revenue': 'sum', 'roas': 'mean'}).round(2)
        
        avg_roas = channel_performance['roas'].mean()
        avg_ctr = channel_performance['ctr'].mean()
        avg_cpc = channel_performance['cpc'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Growth Opportunities")
            if not channel_performance.empty:
                best_channel = channel_performance['roas'].idxmax()
                best_channel_roas = channel_performance['roas'].max()
                st.success(f"**Scale {best_channel} Campaigns**")
                st.write(f"• Current ROAS: {best_channel_roas:.2f}x (vs avg {avg_roas:.2f}x)")
            
            if not state_performance.empty:
                best_state = state_performance['roas'].idxmax()
                best_state_roas = state_performance['roas'].max()
                st.success(f"**Expand {best_state} Market**")
                st.write(f"• ROAS: {best_state_roas:.2f}x")
            
            if not tactic_performance.empty:
                best_tactic = tactic_performance['roas'].idxmax()
                best_tactic_roas = tactic_performance['roas'].max()
                st.success(f"**Optimize {best_tactic} Strategy**")
                st.write(f"• ROAS: {best_tactic_roas:.2f}x")
        
        with col2:
            st.markdown("#### Optimization Areas")
            underperforming = channel_performance[channel_performance['roas'] < avg_roas]
            if not underperforming.empty:
                worst_channel = underperforming['roas'].idxmin()
                worst_roas = underperforming.loc[worst_channel, 'roas']
                st.warning(f"**Improve {worst_channel} Performance**")
                st.write(f"• Current ROAS: {worst_roas:.2f}x (below avg {avg_roas:.2f}x)")
            
            high_cpc = channel_performance[channel_performance['cpc'] > avg_cpc * 1.2]
            if not high_cpc.empty:
                expensive_channel = high_cpc['cpc'].idxmax()
                expensive_cpc = high_cpc.loc[expensive_channel, 'cpc']
                st.warning(f"**Reduce {expensive_channel} Costs**")
                st.write(f"• Current CPC: ${expensive_cpc:.2f}")

        st.markdown("### Strategic Insights")
        col1, col2, col3 = st.columns(3)
        with col1:
            delta_text = "Above Target" if roas > 3.0 else "Needs Improvement"
            st.metric("Overall ROAS", f"{roas:.2f}x", delta=delta_text)
        with col2:
            efficiency_score = (roas / 4.0) * 100
            delta_text = "Excellent" if efficiency_score > 80 else "Good" if efficiency_score > 60 else "Needs Work"
            st.metric("Marketing Efficiency", f"{efficiency_score:.0f}/100", delta=delta_text)
        with col3:
            roas_range = channel_performance['roas'].max() - channel_performance['roas'].min()
            growth_potential = (roas_range / channel_performance['roas'].min()) * 100 if channel_performance['roas'].min() > 0 else 0
            delta_text = "High Opportunity" if growth_potential > 50 else "Moderate"
            st.metric("Growth Potential", f"{growth_potential:.0f}%", delta=delta_text)
    else:
        st.info("No marketing data available for strategic recommendations. Please adjust your filters to see insights.")

def show_ai_assistant(filtered_marketing, filtered_business):
    """Implements the AI Assistant feature."""
    st.subheader("AI Marketing Assistant")
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your marketing data below..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                response = ask_ai(prompt, filtered_marketing, filtered_business)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    show_header()
    
    marketing_data, business_data = load_data()

    # --- Top-level control panel using a container ---
    with st.container():
        st.header("Analysis Controls")
        col1, col2 = st.columns(2)
        with col1:
            min_date, max_date = marketing_data['date'].min(), marketing_data['date'].max()
            date_range = st.date_input("Select Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        with col2:
            platforms = st.multiselect("Select Platforms", marketing_data['platform'].unique(), default=marketing_data['platform'].unique())
    
    st.markdown("---")
    
    # Filter data based on controls
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_marketing = marketing_data[(marketing_data['date'] >= start_date) & (marketing_data['date'] <= end_date) & (marketing_data['platform'].isin(platforms))]
        filtered_business = business_data[(business_data['date'] >= start_date) & (business_data['date'] <= end_date)]
    else:
        filtered_marketing = marketing_data[marketing_data['platform'].isin(platforms)]
        filtered_business = business_data

    # Use tabs for a cleaner, more organized layout
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Summary", 
        "Channel Performance", 
        "Geographic Analysis", 
        "Performance Trends", 
        "Business Impact",
        "AI Assistant"
    ])

    with tab1:
        show_executive_summary(filtered_marketing, filtered_business)
        st.divider()
        show_strategic_recommendations(filtered_marketing)
    
    with tab2:
        show_channel_performance(filtered_marketing)

    with tab3:
        show_geographic_analysis(filtered_marketing)
    
    with tab4:
        show_performance_trends(filtered_marketing)
    
    with tab5:
        show_business_impact(filtered_marketing, filtered_business)

    with tab6:
        show_ai_assistant(filtered_marketing, filtered_business)

if __name__ == "__main__":
    main()