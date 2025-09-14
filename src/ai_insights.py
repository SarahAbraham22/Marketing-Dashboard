
import google.generativeai as genai
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from config import GEMINI_API_KEY

# Setup Gemini AI model once at module load
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    _gemini_model = None

def ask_ai(question, marketing_data, business_data):
    if not _gemini_model:
        return "AI not available. Please add GEMINI_API_KEY to config.py"

    # Prepare data context
    context = f"""
    MARKETING DATA SUMMARY:
    - Total Spend: ${marketing_data['spend'].sum():,.0f}
    - Total Revenue: ${marketing_data['attributed revenue'].sum():,.0f}
    - Average ROAS: {marketing_data['roas'].mean():.2f}x
    - Best Platform: {marketing_data.groupby('platform')['roas'].mean().idxmax()}
    - Best State: {marketing_data.groupby('state')['roas'].mean().idxmax()}
    - Platforms: {', '.join(marketing_data['platform'].unique())}
    - States: {', '.join(marketing_data['state'].unique())}
    - Tactics: {', '.join(marketing_data['tactic'].unique())}

    BUSINESS DATA SUMMARY:
    - Total Orders: {business_data['# of orders'].sum():,}
    - Total Revenue: ${business_data['total revenue'].sum():,.0f}
    - New Customers: {business_data['new customers'].sum():,}
    - Avg Order Value: ${business_data['avg_order_value'].mean():.2f}
    """

    prompt = f"CONTEXT:{context}\n\nQUESTION: {question}\n\nProvide a concise, actionable answer to the question based on the context above."

    try:
        response = _gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"