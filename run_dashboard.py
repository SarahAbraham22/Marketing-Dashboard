#!/usr/bin/env python3
"""
Run the Marketing Intelligence Dashboard with AI Insights
Deployment-ready for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------
# Page Configuration
# ---------------------
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------
# Header / Messages
# ---------------------
st.title("🚀 Marketing Intelligence Dashboard with AI Insights")
st.info("📊 Explore the impact of marketing campaigns on business performance")
st.write("🤖 AI insights powered by Google Gemini (if configured)")
st.markdown("---")

# ---------------------
# Load datasets
# ---------------------
dataset_path = "dataset"

try:
    facebook_df = pd.read_csv(os.path.join(dataset_path, "Facebook.csv"))
    google_df   = pd.read_csv(os.path.join(dataset_path, "Google.csv"))
    tiktok_df   = pd.read_csv(os.path.join(dataset_path, "TikTok.csv"))
    business_df = pd.read_csv(os.path.join(dataset_path, "business.csv"))
    st.success("✅ All datasets loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load datasets: {e}")

# ---------------------
# Sidebar Filters
# ---------------------
st.sidebar.header("Filters")

# Example: Select a marketing platform
platform = st.sidebar.selectbox("Choose platform:", ["Facebook", "Google", "TikTok"])

if platform == "Facebook":
    df = facebook_df
elif platform == "Google":
    df = google_df
else:
    df = tiktok_df

# Example: Select date range
if "date" in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input("Select date range:", [min_date, max_date])
    start_date, end_date = date_range
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# ---------------------
# Example Chart
# ---------------------
st.header(f"{platform} Campaign Impressions Over Time")

if "impression" in df.columns:
    fig = px.line(df, x="date", y="impression", title=f"{platform} Impressions")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"No 'impression' column found in {platform} dataset")

# ---------------------
# Business Metrics
# ---------------------
st.header("Business Performance Overview")

if not business_df.empty:
    st.dataframe(business_df.head())
    fig_rev = px.line(business_df, x="date", y="total_revenue", title="Total Revenue Over Time")
    st.plotly_chart(fig_rev, use_container_width=True)
else:
    st.warning("Business dataset is empty or not loaded")

# ---------------------
# Footer / AI Insights placeholder
# ---------------------
st.markdown("---")
st.info("💡 AI Insights will appear here once Google Gemini integration is configured")
