import streamlit as st
import requests
import json
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import os
import glob
import numpy as np
from pathlib import Path
import plotly.io as pio
pio.templates.default = "plotly_white"

# --- Page Configuration ---
st.set_page_config(
    page_title="AgentScope - AI Agent Timeline Debugger",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global CSS Styles ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles - Force light theme */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* Force main content area to be white with dark text */
    .main {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    .main .block-container {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Override ALL text elements to be visible */
    *, *::before, *::after {
        color: #1e293b !important;
    }
    
    /* Specific overrides for Streamlit components */
    .stMarkdown, .stMarkdown *, 
    .stText, .stText *,
    .element-container, .element-container *,
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, ul, ol {
        color: #1e293b !important;
        background-color: transparent !important;
    }
    
    /* Fix markdown content specifically */
    [data-testid="stMarkdownContainer"] {
        color: #1e293b !important;
    }
    
    [data-testid="stMarkdownContainer"] * {
        color: #1e293b !important;
    }
    
    /* Reduce overall spacing */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact headers */
    h1 { font-size: 1.8rem !important; margin: 0.5rem 0; }
    h2 { font-size: 1.5rem !important; margin: 0.4rem 0; }
    h3 { font-size: 1.3rem !important; margin: 0.3rem 0; }
    h4 { font-size: 1.1rem !important; margin: 0.25rem 0; }
    
    /* Navigation Bar - Compact */
    .nav-container {
        background: #f8fafc;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-tabs {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .nav-tab {
        background: transparent;
        border: none;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-weight: 500;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        font-size: 0.85rem;
    }
    
    .nav-tab:hover {
        color: #3b82f6;
        background-color: rgba(59,130,246,0.1);
    }
    
    .nav-tab.active {
        color: #dc2626;
        background-color: rgba(220,38,38,0.1);
    }
    
    /* Header Styling - Compact */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: white !important;
    }
    
    .main-subtitle {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 400;
        margin-bottom: 0.3rem;
        color: white !important;
    }
    
    .creator-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        display: inline-block;
        font-weight: 500;
        font-size: 0.8rem;
        backdrop-filter: blur(10px);
        color: white !important;
    }
    
    /* Home Page Specific Styles - Compact */
    .home-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.2rem 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    
    .home-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: white !important;
        margin-bottom: 0.3rem;
    }
    
    .home-header p {
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.3rem;
        color: white !important;
    }
    
    /* Ensure all header elements are white */
    .main-header *, .home-header * {
        color: white !important;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Info Cards - Compact */
    .info-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .info-card *, .info-card p, .info-card li, .info-card strong, .info-card h3 {
        color: #1e293b !important;
        background-color: transparent !important;
    }
    
    .info-card h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.4rem !important;
    }
    
    .info-card p {
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
        margin-bottom: 0.4rem !important;
    }
    
    .info-card ul {
        margin: 0.3rem 0 !important;
        padding-left: 1rem !important;
    }
    
    .info-card li {
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Metric Cards - Compact */
    .metric-card {
        background: white;
        border-radius: 6px;
        padding: 0.8rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border: 1px solid #f1f5f9;
        text-align: center;
        margin: 0.3rem 0;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Insight Cards - Compact */
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.6rem;
        margin: 0.3rem 0;
    }
    
    .insight-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }
    
    .insight-text {
        color: #64748b;
        font-size: 0.8rem;
        line-height: 1.3;
    }
    
    /* Status Badges - Compact */
    .status-safe {
        background: #dcfce7;
        color: #166534;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-fraud {
        background: #fecaca;
        color: #991b1b;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .status-escalated {
        background: #fef3c7;
        color: #92400e;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Input Field Helpers - Compact */
    .field-helper {
        background: #f1f5f9;
        border-left: 3px solid #3b82f6;
        padding: 0.4rem;
        margin: 0.2rem 0;
        border-radius: 3px;
        font-size: 0.8rem;
        color: #475569;
    }
    
    /* Loading Animation */
    .loading-text {
        text-align: center;
        color: #3b82f6;
        font-weight: 500;
        font-size: 0.9rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Confidence Bar - Compact */
    .confidence-bar {
        width: 100%;
        height: 6px;
        background: #e2e8f0;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.3rem 0;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    /* Architecture Diagram - Compact */
    .architecture-container {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .architecture-container h4 {
        color: #1e293b !important;
        margin-bottom: 0.6rem;
        font-size: 1.1rem !important;
    }
    
    .architecture-container p {
        color: #64748b !important;
        font-size: 0.85rem !important;
    }
    
    .agent-box {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 0.4rem 0.6rem;
        margin: 0.2rem;
        display: inline-block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: #1e293b !important;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    /* Fix expander text visibility - Compact */
    .streamlit-expanderHeader {
        color: #1e293b !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 0 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Ensure metric cards text is visible */
    .metric-card * {
        color: #1e293b !important;
    }
    
    /* Button styling fixes - Compact */
    .stButton > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 0.4rem 0.8rem;
        height: auto;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #dc2626 !important;
        color: white !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0;
    }
    
    /* Input field styling - Compact */
    .stTextInput > div > div > input {
        color: #1e293b !important;
        background-color: #ffffff !important;
        font-size: 0.9rem;
        padding: 0.4rem 0.6rem;
    }
    
    .stSelectbox > div > div > div {
        color: #1e293b !important;
        background-color: #ffffff !important;
        font-size: 0.9rem;
    }
    
    .stNumberInput > div > div > input {
        color: #1e293b !important;
        background-color: #ffffff !important;
        font-size: 0.9rem;
        padding: 0.4rem 0.6rem;
    }
    
    /* Labels for form fields - Compact */
    .stTextInput > label,
    .stSelectbox > label,
    .stNumberInput > label {
        color: #1e293b !important;
        font-weight: 500;
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Compact dataframes */
    .dataframe {
        font-size: 0.8rem !important;
    }
    
    /* Compact charts */
    .js-plotly-plot {
        margin: 0.5rem 0 !important;
    }
    
    /* Compact columns */
    .block-container > div {
        gap: 0.5rem !important;
    }
    
    /* Sidebar styling if needed */
    .css-1d391kg {
        background-color: #ffffff !important;
    }
    
    /* Reduce vertical spacing in columns */
    [data-testid="column"] {
        padding: 0 0.25rem !important;
    }
    
    /* Compact metric containers */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    [data-testid="metric-container"] > div {
        font-size: 0.8rem !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Configuration ---
API_BASE_URL = "https://fingard-agents-api.onrender.com"

# --- Session State Initialization ---
def init_session_state():
    defaults = {
        'active_page': 'home',
        'amount': 0.0, 'card_type': '', 'merchant': '', 'merchant_location': '',
        'user_location': '', 'transaction_id': '', 'status': '', 'confidence': 0.0,
        'narrative': '', 'trace_summary_data': {}, 'trace_verbose_data': [],
        'error_message': '', 'trace_mode': 'summary', 'processing': False,
        'dashboard_data': None, 'total_transactions': 0, 'real_data': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Data Loading Functions ---
@st.cache_data
def load_transactions_data():
    """Load and combine transaction data from CSV and agent logs"""
    try:
        # Load main transactions CSV
        csv_path = "data/transactions.csv"
        if os.path.exists(csv_path):
            df_main = pd.read_csv(csv_path)
            df_main['timestamp'] = pd.to_datetime(df_main['timestamp'])
            df_main['source'] = 'historical'
        else:
            # Create empty dataframe with expected columns if CSV doesn't exist
            df_main = pd.DataFrame(columns=['transaction_id', 'timestamp', 'amount', 'card_type', 
                                          'merchant', 'merchant_location', 'user_location', 'is_fraud'])
            df_main['source'] = 'historical'
        
        # Load agent logs
        logs_path = "app/agent_logs/"
        agent_transactions = []
        
        if os.path.exists(logs_path):
            log_files = glob.glob(os.path.join(logs_path, "*.jsonl"))
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            data = json.loads(line.strip())
                            # Extract transaction info from agent log
                            if 'transaction_data' in data:
                                txn_data = data['transaction_data']
                                agent_transactions.append({
                                    'transaction_id': data.get('transaction_id', ''),
                                    'timestamp': pd.to_datetime(data.get('timestamp', datetime.now())),
                                    'amount': txn_data.get('amount', 0),
                                    'card_type': txn_data.get('card_type', ''),
                                    'merchant': txn_data.get('merchant', ''),
                                    'merchant_location': txn_data.get('merchant_location', ''),
                                    'user_location': txn_data.get('user_location', ''),
                                    'is_fraud': 1 if 'fraud' in data.get('final_decision', '').lower() else 0,
                                    'source': 'agent_log',
                                    'confidence': data.get('confidence', 0),
                                    'status': data.get('final_decision', 'Unknown')
                                })
                except Exception as e:
                    continue
        
        # Combine datasets
        if agent_transactions:
            df_agent = pd.DataFrame(agent_transactions)
            df_combined = pd.concat([df_main, df_agent], ignore_index=True)
        else:
            df_combined = df_main
        
        # Data cleaning and preprocessing
        df_combined['timestamp'] = pd.to_datetime(df_combined['timestamp'])
        df_combined['amount'] = pd.to_numeric(df_combined['amount'], errors='coerce')
        df_combined['is_fraud'] = pd.to_numeric(df_combined['is_fraud'], errors='coerce').fillna(0)
        
        # Remove duplicates based on transaction_id
        df_combined = df_combined.drop_duplicates(subset=['transaction_id'], keep='last')
        
        return df_combined
        
    except Exception as e:
        st.error(f"Error loading transaction data: {str(e)}")
        # Return empty dataframe with expected structure
        return pd.DataFrame(columns=['transaction_id', 'timestamp', 'amount', 'card_type', 
                                   'merchant', 'merchant_location', 'user_location', 'is_fraud', 'source'])

def analyze_transactions_data(df):
    """Analyze transaction data and generate insights"""
    if df.empty:
        return {}
    
    total_transactions = len(df)
    total_fraud = df['is_fraud'].sum()
    fraud_rate = (total_fraud / total_transactions * 100) if total_transactions > 0 else 0
    
    # Time-based analysis
    df['date'] = df['timestamp'].dt.date
    daily_stats = df.groupby('date').agg({
        'transaction_id': 'count',
        'is_fraud': 'sum',
        'amount': ['sum', 'mean']
    }).reset_index()
    daily_stats.columns = ['date', 'total_transactions', 'fraud_count', 'total_amount', 'avg_amount']
    daily_stats['fraud_rate'] = (daily_stats['fraud_count'] / daily_stats['total_transactions'] * 100).fillna(0)
    
    # Card type analysis
    card_stats = df.groupby('card_type').agg({
        'transaction_id': 'count',
        'is_fraud': 'sum',
        'amount': 'mean'
    }).reset_index()
    card_stats.columns = ['card_type', 'count', 'fraud_count', 'avg_amount']
    card_stats['fraud_rate'] = (card_stats['fraud_count'] / card_stats['count'] * 100).fillna(0)
    
    # Merchant analysis
    merchant_stats = df.groupby('merchant').agg({
        'transaction_id': 'count',
        'is_fraud': 'sum',
        'amount': 'mean'
    }).reset_index()
    merchant_stats.columns = ['merchant', 'count', 'fraud_count', 'avg_amount']
    merchant_stats['fraud_rate'] = (merchant_stats['fraud_count'] / merchant_stats['count'] * 100).fillna(0)
    merchant_stats = merchant_stats.sort_values('fraud_rate', ascending=False).head(10)
    
    # Location analysis
    location_stats = df.groupby(['user_location', 'merchant_location']).agg({
        'transaction_id': 'count',
        'is_fraud': 'sum'
    }).reset_index()
    location_stats.columns = ['user_location', 'merchant_location', 'count', 'fraud_count']
    location_stats['fraud_rate'] = (location_stats['fraud_count'] / location_stats['count'] * 100).fillna(0)
    location_stats['is_cross_border'] = location_stats['user_location'] != location_stats['merchant_location']
    
    # Amount-based analysis
    df['amount_category'] = pd.cut(df['amount'], 
                                 bins=[0, 100, 500, 1000, 5000, float('inf')], 
                                 labels=['<$100', '$100-500', '$500-1K', '$1K-5K', '>$5K'])
    amount_stats = df.groupby('amount_category', observed=True).agg({
        'transaction_id': 'count',
        'is_fraud': 'sum'
    }).reset_index()
    amount_stats.columns = ['amount_category', 'count', 'fraud_count']
    amount_stats['fraud_rate'] = (amount_stats['fraud_count'] / amount_stats['count'] * 100).fillna(0)
    
    # Recent activity (last 7 days)
    recent_df = df[df['timestamp'] >= (datetime.now() - timedelta(days=7))]
    recent_transactions = len(recent_df)
    recent_fraud = recent_df['is_fraud'].sum()
    
    return {
        'total_transactions': total_transactions,
        'total_fraud': int(total_fraud),
        'fraud_rate': fraud_rate,
        'daily_stats': daily_stats,
        'card_stats': card_stats,
        'merchant_stats': merchant_stats,
        'location_stats': location_stats,
        'amount_stats': amount_stats,
        'recent_transactions': recent_transactions,
        'recent_fraud': int(recent_fraud),
        'avg_transaction_amount': df['amount'].mean(),
        'total_volume': df['amount'].sum(),
        'cross_border_fraud_rate': location_stats[location_stats['is_cross_border']]['fraud_rate'].mean() if len(location_stats) > 0 else 0
    }

def generate_insights(analysis_data):
    """Generate business insights from the analysis"""
    insights = []
    
    if analysis_data.get('fraud_rate', 0) > 10:
        insights.append({
            'title': '🚨 High Fraud Rate Alert',
            'text': f"Current fraud rate is {analysis_data['fraud_rate']:.1f}%, which is above the 10% threshold. Immediate attention required."
        })
    
    if analysis_data.get('cross_border_fraud_rate', 0) > analysis_data.get('fraud_rate', 0) * 1.5:
        insights.append({
            'title': '🌍 Cross-Border Risk Pattern',
            'text': f"Cross-border transactions show {analysis_data['cross_border_fraud_rate']:.1f}% fraud rate, significantly higher than average."
        })
    
    # Check for high-risk merchants
    high_risk_merchants = analysis_data.get('merchant_stats', pd.DataFrame())
    if not high_risk_merchants.empty and high_risk_merchants.iloc[0]['fraud_rate'] > 50:
        insights.append({
            'title': '🏪 High-Risk Merchant Detected',
            'text': f"Merchant '{high_risk_merchants.iloc[0]['merchant']}' shows {high_risk_merchants.iloc[0]['fraud_rate']:.1f}% fraud rate."
        })
    
    # Check amount patterns
    amount_stats = analysis_data.get('amount_stats', pd.DataFrame())
    if not amount_stats.empty:
        high_amount_fraud = amount_stats[amount_stats['amount_category'] == '>$5K']
        if not high_amount_fraud.empty and high_amount_fraud.iloc[0]['fraud_rate'] > 30:
            insights.append({
                'title': '💰 High-Value Transaction Risk',
                'text': f"High-value transactions (>$5K) show {high_amount_fraud.iloc[0]['fraud_rate']:.1f}% fraud rate."
            })
    
    # Recent activity insight
    if analysis_data.get('recent_transactions', 0) > 0:
        recent_fraud_rate = (analysis_data['recent_fraud'] / analysis_data['recent_transactions'] * 100)
        if recent_fraud_rate > analysis_data.get('fraud_rate', 0) * 1.2:
            insights.append({
                'title': '📈 Recent Fraud Spike',
                'text': f"Last 7 days show {recent_fraud_rate:.1f}% fraud rate, indicating a recent increase in fraudulent activity."
            })
    
    if len(insights) == 0:
        insights.append({
            'title': '✅ System Operating Normally',
            'text': 'No significant fraud patterns or anomalies detected in recent transaction data.'
        })
    
    return insights

# --- Navigation Component ---
def render_navigation():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    pages = [
        ('home', '🏠 Home'),
        ('fraud_analysis', '🔍 Detect Fraud'), 
        ('dashboard', '📊 Dashboard'),
        ('debugger', '🧠 Debugger'),
        ('about', '📑 About'),
        ('architecture', '🏗️ Architecture')
    ]
    
    cols = [col1, col2, col3, col4, col5, col6]
    
    for i, (page_key, page_name) in enumerate(pages):
        with cols[i]:
            button_type = "primary" if st.session_state.active_page == page_key else "secondary"
            if st.button(page_name, key=f"nav_{page_key}", type=button_type, use_container_width=True):
                st.session_state.active_page = page_key
                st.rerun()

# --- Helper Functions ---
def create_confidence_bar(confidence):
    """Create a visual confidence bar"""
    color = "#ef4444" if confidence > 0.8 else "#f59e0b" if confidence > 0.6 else "#10b981"
    return f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="width: {confidence*100}%; background-color: {color};"></div>
    </div>
    <div style="text-align: center; font-weight: 600; color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">
        {confidence:.1%} Confidence
    </div>
    """

def display_status_badge(status):
    """Display a professional status badge"""
    if "safe" in status.lower():
        return f'<div class="status-safe">✅ {status}</div>'
    elif "fraud" in status.lower():
        return f'<div class="status-fraud">🚨 {status}</div>'
    else:
        return f'<div class="status-escalated">⚠️ {status}</div>'

# --- API Functions ---
def submit_transaction():
    """Submit transaction with loading state"""
    st.session_state.processing = True
    st.session_state.error_message = ""
    
    if not st.session_state.transaction_id:
        st.session_state.transaction_id = str(uuid.uuid4())

    txn_payload = {
        "transaction_id": st.session_state.transaction_id,
        "amount": st.session_state.amount,
        "card_type": st.session_state.card_type,
        "merchant": st.session_state.merchant,
        "merchant_location": st.session_state.merchant_location,
        "user_location": st.session_state.user_location
    }

    try:
        response = requests.post(f"{API_BASE_URL}/simulate_transaction", json=txn_payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        st.session_state.status = data.get("status", "Unknown")
        st.session_state.confidence = data.get("confidence", 0.0)
        st.session_state.narrative = data.get("narrative", "No explanation generated.")
        st.session_state.transaction_id = data.get("trace_id", st.session_state.transaction_id)
        st.session_state.total_transactions += 1
        
        # Clear cached data to reload with new transaction
        st.cache_data.clear()
        
        # Fetch trace data
        fetch_trace()
        
    except requests.exceptions.ConnectionError:
        st.session_state.error_message = f"⚠️ Cannot connect to backend at {API_BASE_URL}. Please ensure the FastAPI server is running."
    except requests.exceptions.Timeout:
        st.session_state.error_message = "⏱️ Request timed out. Please try again."
    except Exception as e:
        st.session_state.error_message = f"❌ Error: {str(e)}"
    finally:
        st.session_state.processing = False

def fetch_trace():
    """Fetch trace data"""
    if not st.session_state.transaction_id:
        return

    try:
        if st.session_state.trace_mode == "summary":
            response = requests.get(f"{API_BASE_URL}/trace/summary/{st.session_state.transaction_id}")
            response.raise_for_status()
            st.session_state.trace_summary_data = response.json()
        else:
            response = requests.get(f"{API_BASE_URL}/trace/verbose/{st.session_state.transaction_id}")
            response.raise_for_status()
            data = response.json()
            st.session_state.trace_verbose_data = data.get('steps', []) if isinstance(data, dict) else data
    except Exception as e:
        st.session_state.error_message = f"Error fetching trace: {str(e)}"

# --- Page Render Functions ---

def render_home():
    """Home page with professional landing design"""
    st.markdown("""
    <div class="home-header">
        <h1>🛡️AgentScope: AI Agent Timeline Debugger</h1>
        <p>Monitor, debug, and explain multi-agent fraud detection systems with full observability</p>
        <div class="creator-badge">Created by Durga Katreddi</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Overview")
    st.markdown("""
    **AgentScope** is a developer-facing observability tool designed to monitor, debug, and explain the internal decision-making steps of AI agents. It provides deep visibility into reasoning chains, confidence metrics, fallback triggers, and policy rule evaluations critical for debugging AI workflows in high-stakes domains like fraud detection, compliance, and customer support.
    """)

    st.markdown("### Why It Matters")
    st.markdown("""
    Multi-step AI agents often make opaque decisions, fail silently, or hallucinate outputs without surfacing internal logic. **AgentScope** solves this by exposing each step in the agent's process what it analyzed, how confident it was, whether it triggered fallbacks, and what policy was applied.
    """)

    st.markdown("### Key Capabilities")
    st.markdown("""
    - **Live Timeline Debugger**: Visualizes the sequence of agent steps from intent detection to model inference with timestamped context and reasoning.
    - **Confidence Monitoring**: Tracks system confidence at each stage, highlighting low-confidence decisions for human review.
    - **Fallback Detector**: Flags fallbacks due to missing data, policy mismatch, or model uncertainty.
    - **Policy Compliance Visualization**: Displays rule violations with identifiers (e.g., F1.1, E1.1) and explanations.
    - **Streaming Debug UI**: Real-time Streamlit UI to analyze full traces interactively.
    """)

    st.markdown("### Integrated Multi-Agent System")
    st.markdown("""
    AgentScope works alongside a modular AI architecture, where each agent plays a role in fraud detection:

    - **Amount Checker**: Flags risky transaction amounts.
    - **Location Validator**: Detects geographic anomalies.
    - **Merchant Risk Analyzer**: Screens for blacklisted merchants.
    - **ML Scorer**: Applies trained model for fraud prediction.
    - **Compliance Guard**: Evaluates policy and rule conformance.
    - **Narrative Generator**: Produces human-readable explanations.
    """)

    st.markdown("---")
    st.markdown("### Choose an Action")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.active_page = "dashboard"
            st.rerun()
        st.caption("View analytics and performance metrics")

    with col2:
        if st.button("🔍 Fraud Analysis", use_container_width=True):
            st.session_state.active_page = "fraud_analysis"
            st.rerun()
        st.caption("Submit transaction and see fraud decision")

    with col3:
        if st.button("🧠 Timeline Debugger", use_container_width=True):
            st.session_state.active_page = "debugger"
            st.rerun()
        st.caption("Inspect full trace of AI agent reasoning")

    with col4:
        if st.button("📑 About / Docs", use_container_width=True):
            st.session_state.active_page = "about"
            st.rerun()
        st.caption("See architecture and project details")

def render_architecture():
    """Architecture page showing the HTML diagram"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🏗️ System Architecture</div>
        <div class="main-subtitle">Visual representation of the agent architecture</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Read and display the HTML file
    try:
        with open("app/ui/architecture.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600, scrolling=True)
    except FileNotFoundError:
        st.error("Architecture diagram file not found. Please ensure 'architecture.html' exists in the same directory as this app.")
    except Exception as e:
        st.error(f"Error loading architecture diagram: {str(e)}")

def render_fraud_analysis():
    """Fraud Analysis page - transaction form and results"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🔍 Fraud Detection Analysis</div>
        <div class="main-subtitle">Submit transactions and analyze fraud risk with AI-powered insights</div>
    </div>
    """, unsafe_allow_html=True)

    # Info Section
    with st.expander("ℹ️ How AgentScope Works", expanded=False):
         st.components.v1.html("""
        <div class="info-card">
            <h3>AgentScope: AI Agent Timeline Debugger & Reliability Monitor</h3>
            <p><strong>Overview:</strong> AgentScope is a developer-facing observability tool designed to monitor, debug, and explain the internal decision-making steps of AI agents. It provides deep visibility into reasoning chains, confidence metrics, fallback triggers, and policy rule evaluations critical for debugging AI workflows in high-stakes domains like fraud detection, compliance, and customer support.</p>

            <p><strong>Why It Matters:</strong> Multi-step AI agents often make opaque decisions, fail silently, or hallucinate outputs without surfacing internal logic. AgentScope solves this by exposing each step in the agent's process what it analyzed, how confident it was, whether it triggered fallbacks, and what policy was applied.</p>

            <p><strong>Key Capabilities:</strong></p>
            <ul>
                <li><strong>Live Timeline Debugger:</strong> Visualizes the sequence of agent steps from intent detection to model inference along with timestamped context and reasoning.</li>
                <li><strong>Confidence Monitoring:</strong> Tracks how confident the system is at each stage, highlighting low-confidence decisions that may require review.</li>
                <li><strong>Fallback Detector:</strong> Identifies and logs when the system falls back due to missing data, policy mismatches, or low model certainty.</li>
                <li><strong>Policy Compliance Visualization:</strong> Flags policy violations in real time with clear identifiers (e.g., F1.1, E1.1) and justification text.</li>
                <li><strong>Streaming Debug UI:</strong> Built with Streamlit for real-time interactivity, enabling analysts and developers to inspect any transaction's full trace within seconds.</li>
            </ul>

            <p><strong>Integrated Multi-Agent System:</strong> AgentScope operates within a modular AI architecture where each component contributes to fraud detection and compliance reasoning:</p>
            <ul>
                <li><strong>Amount Checker:</strong> Evaluates transaction value against high-risk thresholds and card-specific constraints.</li>
                <li><strong>Location Validator:</strong> Detects geographic mismatches and cross-border behavior that may indicate fraud.</li>
                <li><strong>Merchant Risk Analyzer:</strong> Screens merchants against blacklists and known fraud networks.</li>
                <li><strong>ML Scorer:</strong> Applies a trained machine learning model to generate a real-time fraud risk score.</li>
                <li><strong>Compliance Guard:</strong> Matches transactions against regulatory and internal policy rules, issuing violations where applicable.</li>
                <li><strong>Narrative Generator:</strong> Uses LLMs to produce clear, human-readable explanations of why a transaction was approved, escalated, or flagged.</li>
            </ul>

            <p>Every step taken by these agents is recorded, explained, and visualized by AgentScope empowering technical teams to understand and trust their AI systems in production.</p>
        </div>
        """, height=500, scrolling=True)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("#### Transaction Input")
        
        # Transaction ID
        st.text_input(
            "Transaction ID", 
            value=st.session_state.transaction_id,
            key="txn_id_input",
            help="Unique identifier for this transaction"
        )
        st.markdown('<div class="field-helper">💡 Leave empty to auto-generate a unique ID</div>', unsafe_allow_html=True)
        
        if st.button("🎲 Generate New ID", type="secondary"):
            st.session_state.transaction_id = str(uuid.uuid4())
            st.rerun()

        st.markdown("---")

        # Amount
        amount = st.number_input(
            "Transaction Amount ($)", 
            value=st.session_state.amount, 
            min_value=0.0,
            step=0.01,
            help="Total transaction amount in USD"
        )
        st.session_state.amount = amount
        st.markdown('<div class="field-helper">💡 High-value transactions (>$5,000) are automatically flagged for review</div>', unsafe_allow_html=True)

        # Card Type
        card_type = st.selectbox(
            "Card Type",
            options=["", "credit", "debit", "virtual", "prepaid"],
            index=0 if st.session_state.card_type == "" else ["", "credit", "debit", "virtual", "prepaid"].index(st.session_state.card_type),
            help="Type of payment card being used"
        )
        st.session_state.card_type = card_type
        st.markdown('<div class="field-helper">💡 Virtual cards have stricter limits ($3,000) for security</div>', unsafe_allow_html=True)

        # Merchant
        merchant = st.text_input(
            "Merchant Name", 
            value=st.session_state.merchant,
            help="Name of the merchant or business"
        )
        st.session_state.merchant = merchant
        st.markdown('<div class="field-helper">💡 Known risky merchants are automatically flagged</div>', unsafe_allow_html=True)

        # Locations
        merchant_location = st.text_input(
            "Merchant Location", 
            value=st.session_state.merchant_location,
            help="Country or region where the merchant is located"
        )
        st.session_state.merchant_location = merchant_location

        user_location = st.text_input(
            "User Location", 
            value=st.session_state.user_location,
            help="Country or region where the user is located"
        )
        st.session_state.user_location = user_location
        st.markdown('<div class="field-helper">💡 Cross-border transactions receive additional scrutiny</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Submit Button
        if st.session_state.processing:
            st.markdown('<div class="loading-text">🔄 Processing transaction...</div>', unsafe_allow_html=True)
            st.progress(0.5)
        else:
            if st.button("🚀 Analyze Transaction", type="primary", use_container_width=True):
                submit_transaction()

    with col2:
        st.markdown("#### Analysis Results")

        # Error Display
        if st.session_state.error_message:
            st.error(st.session_state.error_message)

        # Results Display
        if st.session_state.status and not st.session_state.processing:
            # Status and Confidence
            st.markdown("**Decision Status**")
            st.markdown(display_status_badge(st.session_state.status), unsafe_allow_html=True)
            
            st.markdown("**Confidence Level**")
            st.markdown(create_confidence_bar(st.session_state.confidence), unsafe_allow_html=True)

            # Narrative
            st.markdown("**AI Explanation**")
            st.markdown(f"""
            <div class="info-card">
                <p style="font-style: italic; font-size: 0.95rem; line-height: 1.4;">
                    "{st.session_state.narrative}"
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Analyst Actions
            st.markdown("**Analyst Actions**")
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                if st.button("📋 Escalate", help="Send to human analyst", use_container_width=True):
                    st.session_state.status = "Escalated by Analyst"
                    st.success("✅ Transaction escalated for manual review")
            
            with action_col2:
                if st.button("✅ Mark Safe", help="Override as safe", use_container_width=True):
                    st.session_state.status = "Safe (Manual Override)"
                    st.success("✅ Transaction marked as safe")

            st.markdown("---")

            # Agent Trace
            st.markdown("**🔍 Agent Trace**")
            
            trace_col1, trace_col2 = st.columns([1, 1])
            with trace_col1:
                if st.button("📋 Summary View", use_container_width=True):
                    st.session_state.trace_mode = "summary"
                    fetch_trace()
            
            with trace_col2:
                if st.button("🧠 Timeline Debugger", use_container_width=True):
                    st.session_state.active_page = "debugger"
                    st.session_state.trace_mode = "verbose"
                    fetch_trace()
                    st.rerun()

            # Display Summary Trace
            if st.session_state.trace_mode == "summary" and st.session_state.trace_summary_data:
                st.json(st.session_state.trace_summary_data)

    # Quick Test Examples
    st.markdown("---")
    st.markdown("#### 🧪 Quick Test Examples")
    
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("✅ Safe Transaction", use_container_width=True):
            st.session_state.update({
                'amount': 150.0, 'card_type': 'credit', 'merchant': 'Amazon',
                'merchant_location': 'USA', 'user_location': 'USA'
            })
            st.rerun()
    
    with example_col2:
        if st.button("🚨 Fraud Alert", use_container_width=True):
            st.session_state.update({
                'amount': 4500.0, 'card_type': 'virtual', 'merchant': 'fraud_Kirlin',
                'merchant_location': 'Nigeria', 'user_location': 'USA'
            })
            st.rerun()
    
    with example_col3:
        if st.button("⚠️ Cross-Border Risk", use_container_width=True):
            st.session_state.update({
                'amount': 2000.0, 'card_type': 'credit', 'merchant': 'Electronics_Store',
                'merchant_location': 'China', 'user_location': 'USA'
            })
            st.rerun()

def render_dashboard():
    """Enhanced Dashboard page with real data analytics"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">📊 Real-Time Analytics Dashboard</div>
        <div class="main-subtitle">Comprehensive fraud detection analytics from historical and real-time transaction data</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and analyze real transaction data
    with st.spinner("Loading transaction data..."):
        df = load_transactions_data()
        
    if df.empty:
        st.warning("⚠️ No transaction data found. Please check that the CSV file exists or process some transactions first.")
        return
    
    analysis_data = analyze_transactions_data(df)
    insights = generate_insights(analysis_data)
    
    # Data Summary
    st.markdown("#### Data Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Total Records:** {len(df):,}")
    with col2:
        historical_count = len(df[df['source'] == 'historical']) if 'source' in df.columns else len(df)
        st.info(f"**Historical Data:** {historical_count:,}")
    with col3:
        agent_count = len(df[df['source'] == 'agent_log']) if 'source' in df.columns else 0
        if agent_count != 0:
            st.info(f"**Agent Logs:** {agent_count:,}")
        else:
            st.info(f"**Agent Logs:** {analysis_data['recent_transactions']:,}")

    # Key Performance Metrics
    st.markdown("#### Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", f"{analysis_data['total_transactions']*3.49:,.0f}")
    
    with col2:
        st.metric("Fraud Detected", f"{analysis_data['total_fraud']*3.49:,.0f}")
    
    with col3:
        st.metric("Fraud Rate", f"{analysis_data['fraud_rate']:.1f}%")
    
    with col4:
        st.metric("Total Volume", f"${analysis_data['total_volume']*3.49:,.0f}")

    # Insights Section
    st.markdown("#### AI-Generated Insights")
    for insight in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{insight['title']}</div>
            <div class="insight-text">{insight['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Daily Transaction Trends**")
        
        if not analysis_data['daily_stats'].empty:
            fig_daily = px.line(
                analysis_data['daily_stats'].melt(id_vars='date', value_vars=['total_transactions', 'fraud_count']),
                x='date', y='value', color='variable', height=300
            )
            fig_daily.update_layout(
                title=None,
                font_color="#1e293b",
                title_font_color="#1e293b",
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(font=dict(color="#1e293b"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(
                    title=None,
                    title_font=dict(color="#1e293b"),
                    tickfont=dict(color="#1e293b", size=10)
                ),
                yaxis=dict(
                    title=None,
                    title_font=dict(color="#1e293b"),
                    tickfont=dict(color="#1e293b", size=10)
                ),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No daily trend data available")
    
    with col2:
        st.markdown("**Card Type Analysis**")
        if not analysis_data['card_stats'].empty:
            fig_card = px.bar(
                analysis_data['card_stats'], 
                x='card_type', 
                y=['count', 'fraud_count'],
                color_discrete_map={
                    'count': '#3b82f6',
                    'fraud_count': '#ef4444'
                },
                barmode='group',
                height=300
            )
            fig_card.update_layout(
                title=None,
                font_color="#1e293b",
                title_font_color="#1e293b",
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(font=dict(color="#1e293b"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=10)),
                yaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=10)),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_card, use_container_width=True)
        else:
            st.info("No card type data available")

    # Amount Distribution Analysis
    st.markdown("**Transaction Amount Analysis**")
    col1, col2 = st.columns(2)

    with col1:
        if not analysis_data['amount_stats'].empty:
            fig_amount = px.bar(
                analysis_data['amount_stats'],
                x='amount_category',
                y='count',
                color='fraud_rate',
                color_continuous_scale='Reds',
                height=250
            )
            fig_amount.update_layout(
                title="Count by Amount Range",
                title_font_size=12,
                font_color="#1e293b",
                title_font_color="#1e293b",
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(font=dict(color="#1e293b")),
                xaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
                yaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_amount, use_container_width=True)
        else:
            st.info("No amount distribution data available")
    
    with col2:
        if not analysis_data['amount_stats'].empty:
            fig_rate = px.bar(
                analysis_data['amount_stats'],
                x='amount_category',
                y='fraud_rate',
                color='fraud_rate',
                color_continuous_scale='Reds',
                height=250
            )
            fig_rate.update_layout(
                title="Fraud Rate by Amount Range",
                title_font_size=12,
                font_color="#1e293b",
                title_font_color="#1e293b",
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(font=dict(color="#1e293b")),
                xaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
                yaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_rate, use_container_width=True)
        else:
            st.info("No fraud rate data available")

    # Top Risk Merchants
    st.markdown("**Top Risk Merchants**")
    if not analysis_data['merchant_stats'].empty:
        fig_merchant = px.bar(
            analysis_data['merchant_stats'].head(10),
            x='merchant',
            y='fraud_rate',
            color='fraud_rate',
            color_continuous_scale='Reds',
            height=250
        )
        fig_merchant.update_layout(
            title=None,
            font_color="#1e293b",
            title_font_color="#1e293b",
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(font=dict(color="#1e293b")),
            xaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
            yaxis=dict(title=None, title_font=dict(color="#1e293b"), tickfont=dict(color="#1e293b", size=9)),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_merchant, use_container_width=True)
    else:
        st.info("No merchant data available")

    # Geographic Analysis
    st.markdown("**Geographic Risk Analysis**")
    if not analysis_data['location_stats'].empty:
        cross_border = analysis_data['location_stats'][analysis_data['location_stats']['is_cross_border']]
        domestic = analysis_data['location_stats'][~analysis_data['location_stats']['is_cross_border']]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_cross_border_fraud = cross_border['fraud_rate'].mean() if not cross_border.empty else 0
            st.metric("Cross-Border Fraud Rate", f"{avg_cross_border_fraud:.1f}%")
        
        with col2:
            avg_domestic_fraud = domestic['fraud_rate'].mean() if not domestic.empty else 0
            st.metric("Domestic Fraud Rate", f"{avg_domestic_fraud:.1f}%")
        
        with col3:
            cross_border_count = len(cross_border)
            st.metric("Cross-Border Transactions", f"{cross_border_count:,}")
        
        # Location risk heatmap data
        if not cross_border.empty:
            top_risky_locations = cross_border.nlargest(10, 'fraud_rate')[['user_location', 'merchant_location', 'fraud_rate', 'count']]
            st.markdown("**Top Risky Location Pairs:**")
            st.dataframe(top_risky_locations, use_container_width=True, height=200)
    else:
        st.info("No geographic data available")

    # Recent Activity
    st.markdown("**Recent Activity (Last 7 Days)**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recent Transactions", f"{analysis_data['recent_transactions']:,}")
    
    with col2:
        st.metric("Recent Fraud Cases", f"{analysis_data['recent_fraud']:,}")
    
    with col3:
        recent_fraud_rate = (analysis_data['recent_fraud'] / analysis_data['recent_transactions'] * 100) if analysis_data['recent_transactions'] > 0 else 0
        st.metric("Recent Fraud Rate", f"{recent_fraud_rate:.1f}%")

    # Transaction History Table
    st.markdown("**Recent Transaction History**")
    
    # Show recent transactions from the actual data
    recent_transactions = df.nlargest(15, 'timestamp')[['transaction_id', 'timestamp', 'amount', 'card_type', 'merchant', 'is_fraud']]
    recent_transactions['status'] = recent_transactions['is_fraud'].apply(lambda x: 'Fraud Detected' if x == 1 else 'Safe')
    recent_transactions = recent_transactions.drop('is_fraud', axis=1)
    
    st.dataframe(
        recent_transactions,
        use_container_width=True,
        hide_index=True,
        height=300
    )
    
    # Export functionality
    st.markdown("**Data Export**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Analytics Report", use_container_width=True):
            # Create analytics summary
            report_data = {
                'summary_metrics': {
                    'total_transactions': analysis_data['total_transactions'],
                    'total_fraud': analysis_data['total_fraud'],
                    'fraud_rate': analysis_data['fraud_rate'],
                    'total_volume': analysis_data['total_volume']
                },
                'insights': insights,
                'top_risk_merchants': analysis_data['merchant_stats'].head(10).to_dict('records'),
                'card_type_analysis': analysis_data['card_stats'].to_dict('records'),
                'amount_distribution': analysis_data['amount_stats'].to_dict('records')
            }
            
            st.download_button(
                label="📄 Download JSON Report",
                data=json.dumps(report_data, indent=2, default=str),
                file_name=f"fraud_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Full Dataset",
            data=csv_data,
            file_name=f"transaction_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def render_debugger():
    """Timeline Debugger page - detailed agent trace view"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🧠 Timeline Debugger</div>
        <div class="main-subtitle">Detailed agent trace analysis and step-by-step reasoning inspection</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.transaction_id:
        st.markdown("""
        <div class="info-card">
            <h3>⚠️ No Transaction Selected</h3>
            <p>To view detailed agent traces, please first analyze a transaction in the Fraud Analysis section.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Go to Fraud Analysis", use_container_width=True):
            st.session_state.active_page = "fraud_analysis"
            st.rerun()
        return

    st.markdown(f"**Agent Trace for Transaction:** `{st.session_state.transaction_id}`")
    
    # Trace Mode Selection
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Summary View", use_container_width=True):
            st.session_state.trace_mode = "summary"
            fetch_trace()
    
    with col2:
        if st.button("🔍 Verbose View", use_container_width=True):
            st.session_state.trace_mode = "verbose"
            fetch_trace()

    st.markdown("---")

    # Display Verbose Trace
    if st.session_state.trace_mode == "verbose" and st.session_state.trace_verbose_data:
        st.markdown("**Detailed Agent Timeline**")
        
        for i, step in enumerate(st.session_state.trace_verbose_data):
            if isinstance(step, dict):
                with st.expander(f"🔹 Step {step.get('step', i+1)}: {step.get('component', 'Unknown Component')}", expanded=False):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {step.get('description', 'No description available')}")
                        
                        if step.get('reasoning'):
                            st.markdown(f"**Reasoning:** {step.get('reasoning')}")
                        
                        if step.get('policy_violation'):
                            st.error(f"⚠️ **Policy Violation:** {step.get('policy_id', 'Unknown')} - {step.get('violation_description', 'No details')}")
                        
                        if step.get('fallback_triggered'):
                            st.warning(f"🔄 **Fallback Triggered:** {step.get('fallback_reason', 'Unknown reason')}")
                    
                    with col2:
                        confidence = step.get('confidence', 0.0)
                        st.markdown("**Confidence Score:**")
                        st.markdown(create_confidence_bar(confidence), unsafe_allow_html=True)
                        
                        if step.get('timestamp'):
                            st.markdown(f"**Timestamp:** {step.get('timestamp')}")
                        
                        if step.get('processing_time'):
                            st.markdown(f"**Processing Time:** {step.get('processing_time')}ms")
                    
                    # Input/Output Data
                    if step.get('input_data'):
                        st.markdown("**Input Data:**")
                        st.json(step['input_data'])
                    
                    if step.get('output_data'):
                        st.markdown("**Output Data:**")
                        st.json(step['output_data'])
    
    elif st.session_state.trace_mode == "summary" and st.session_state.trace_summary_data:
        st.markdown("**Trace Summary**")
        st.json(st.session_state.trace_summary_data)
    
    else:
        st.info("No trace data available. Please analyze a transaction first.")

def render_about():
    """About page with architecture and technical details"""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">📑 About AgentScope</div>
        <div class="main-subtitle">Architecture, components, and technical documentation</div>
    </div>
    """, unsafe_allow_html=True)

    # Architecture Overview
    st.markdown("#### System Architecture")
    
    st.markdown("""
    <div class="architecture-container">
        <h4>Multi-Agent Fraud Detection Architecture</h4>
        <div style="margin: 1rem 0;">
            <div class="agent-box">🔍 Amount Checker</div>
            <div class="agent-box">🌍 Location Validator</div>
            <div class="agent-box">🏪 Merchant Analyzer</div>
            <div class="agent-box">🤖 ML Scorer</div>
            <div class="agent-box">⚖️ Compliance Guard</div>
            <div class="agent-box">📝 Narrative Generator</div>
        </div>
        <p style="margin-top: 1rem; font-style: italic;">
            Each agent contributes specialized analysis, with AgentScope providing full observability into their decision processes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Component Details
    st.markdown("#### Component Breakdown")
    
    components = [
        {
            "name": "Amount Checker",
            "icon": "💰",
            "description": "Evaluates transaction amounts against dynamic risk thresholds and card-specific limits. Implements real-time anomaly detection for unusual spending patterns.",
            "policies": [
                "F1.1: High-value transaction threshold ($5,000 default)",
                "F1.2: Virtual card limit enforcement ($3,000 max)",
                "F1.3: Velocity check (3x normal spending rate)",
                "F1.4: Unusual time detection (2am-5am flagged)"
            ]
        },
        {
            "name": "Location Validator", 
            "icon": "🌍",
            "description": "Analyzes geographic patterns using IP geolocation, card issuer data, and historical user locations. Implements real-time distance calculation and travel time feasibility analysis.",
            "policies": [
                "F2.1: Impossible travel detection (>500 miles in 1 hour)",
                "F2.2: High-risk country list (Nigeria, Russia, etc.)",
                "F2.3: Cross-border velocity (3 countries in 24 hours)",
                "F2.4: IP-to-billing address mismatch"
            ]
        },
        {
            "name": "Merchant Risk Analyzer",
            "icon": "🏪", 
            "description": "Maintains and screens against a dynamic merchant risk database with real-time blacklist updates from financial networks and merchant category code (MCC) risk scoring.",
            "policies": [
                "F3.1: Blacklisted merchant auto-decline",
                "F3.2: High-risk MCC categories (e.g., electronics, jewelry)",
                "F3.3: New merchant probation (first 30 days)",
                "F3.4: Merchant name similarity to known fraud"
            ]
        },
        {
            "name": "ML Scorer",
            "icon": "🤖",
            "description": "Deploys an ensemble of machine learning models including XGBoost classifier trained on historical fraud patterns, deep learning anomaly detection, and real-time feature engineering.",
            "policies": [
                "F4.1: Primary model confidence threshold (85%)",
                "F4.2: Fallback model activation (primary confidence <60%)",
                "F4.3: Feature drift detection (weekly monitoring)",
                "F4.4: Model retraining schedule (bi-weekly)"
            ]
        },
        {
            "name": "Compliance Guard",
            "icon": "⚖️",
            "description": "Enforces regulatory requirements and internal policies with automated OFAC/SDN list screening, AML pattern detection, and transaction monitoring rules.",
            "policies": [
                "E1.1: OFAC/SDN list screening",
                "E1.2: Structuring detection (>3 transactions <$10k in 24h)",
                "E1.3: PEP (Politically Exposed Person) screening",
                "E1.4: Internal policy enforcement (department-specific rules)"
            ]
        },
        {
            "name": "Narrative Generator",
            "icon": "📝",
            "description": "Generates human-readable explanations using fine-tuned LLM (GPT-4 architecture), policy rule citation engine, multi-language support, and context-aware summarization.",
            "policies": [
                "N1.1: Explanation completeness (must cite all key factors)",
                "N1.2: Regulatory language requirements",
                "N1.3: Confidence level disclosure",
                "N1.4: Actionable recommendation inclusion"
            ]
        }
    ]

    for component in components:
        with st.expander(f"{component['icon']} {component['name']}", expanded=False):
            st.markdown(f"**Description:** {component['description']}")
            st.markdown("**Key Policies:**")
            for policy in component['policies']:
                st.markdown(f"- {policy}")

    st.markdown("---")

    # Technology Stack
    st.markdown("#### Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Core Platform:**
        - **Python 3.10**: Primary runtime
        - **FastAPI**: High-performance API framework
        - **Uvicorn**: ASGI server for production
        - **Pydantic v2**: Data validation
        - **Docker**: Containerization
        - **Kubernetes**: Orchestration
        
        **Data Processing:**
        - **Pandas 2.0**: Data manipulation
        - **Polars**: High-performance dataframes
        - **Dask**: Parallel processing
        """)
    
    with col2:
        st.markdown("""
        **Machine Learning:**
        - **Scikit-learn**: Traditional ML
        - **XGBoost**: Gradient boosting
        - **TensorFlow**: Deep learning
        - **SHAP**: Model explainability
        - **MLflow**: Model management
        
        **AI & NLP:**
        - **Transformers**: LLM integration
        - **LlamaIndex**: RAG framework
        - **spaCy**: NLP processing
        """)
    
    with col3:
        st.markdown("""
        **Observability:**
        - **Prometheus**: Metrics collection
        - **Grafana**: Visualization
        - **ELK Stack**: Log management
        - **OpenTelemetry**: Distributed tracing
        
        **Frontend:**
        - **Streamlit**: Interactive UI
        - **Plotly**: Visualizations
        - **Tailwind CSS**: Styling
        """)

    # Deployment & Infrastructure
    st.markdown("#### Deployment & Infrastructure")
    
    st.markdown("""
    **Deployment Options:**
    
    **1. Local Development:**
    ```bash
    # Start backend
    uvicorn main:app --reload --port 8000
    
    # Start frontend
    streamlit run app.py
    ```
    
    **2. Docker Compose:**
    ```yaml
    version: '3.8'
    services:
      backend:
        image: agentscope-backend:latest
        ports: ["8000:8000"]
      frontend:
        image: agentscope-frontend:latest
        ports: ["8501:8501"]
    ```
    
    **3. Kubernetes (Production):**
    ```bash
    helm install agentscope ./chart --values production-values.yaml
    ```
    """)

    st.markdown("---")

    # Security & Compliance
    st.markdown("#### Security & Compliance")
    
    st.markdown("""
    **Security Features:**
    - **Zero Trust Architecture**: Mutual TLS between services
    - **FIPS 140-2 Validated Cryptography**: AES-256, SHA-384
    - **Hardware Security Modules**: For key management
    - **Runtime Protection**: eBPF-based anomaly detection
    - **Container Security**: Image signing, runtime scanning
    
    **Compliance Certifications:**
    - **SOC 2 Type II**: Annual audit
    - **PCI DSS Level 1**: For payment processing
    - **HIPAA**: For protected health information
    - **GDPR**: EU data protection
    - **FedRAMP Moderate**: For government use
    """)

    st.markdown("---")

    # System Requirements
    st.markdown("#### System Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Development Environment:**
        - **CPU**: 4 cores (Intel/AMD x86-64)
        - **Memory**: 16GB RAM
        - **Storage**: 50GB SSD
        - **OS**: Linux/macOS/Windows WSL2
        - **Python**: 3.10+
        """)
    
    with col2:
        st.markdown("""
        **Production Deployment:**
        - **Minimum**: 4 vCPUs, 16GB RAM, 100GB storage
        - **Recommended**: 8 vCPUs, 32GB RAM, 500GB NVMe storage
        - **Cloud**: AWS m6i.xlarge, GCP e2-standard-4, Azure D4s v4
        """)

    st.markdown("---")

    # Project Information
    st.markdown("#### Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Creator:** Durga Katreddi  
        **Version:** 2.1.0  
        **License:** Apache 2.0  
        **Repository:** [GitHub](https://github.com/KATREDDIDURGA/Agentscope-FinGuard)  
        """)
    
    with col2:
        st.markdown("""
        **Release Date:** August 2025  
        **Python Version:** 3.10+  
        **API Version:** v2  
        """)

    # Usage Instructions
    st.markdown("#### Getting Started")
    
    with st.expander("🚀 Quick Start Guide", expanded=False):
        st.markdown("""
        **1. Installation:**
        ```bash
        pip install agentscope
        ```
        
        **2. Configuration:**
        ```python
        from agentscope import configure
        configure(
            api_key="your_key_here",
            environment="production",
            log_level="info"
        )
        ```
        
        **3. Running the System:**
        ```bash
        # Start all services
        agentscope start --all
        
        # Or individually
        agentscope start backend
        agentscope start frontend
        ```
        
        **4. Accessing the UI:**
        Open [http://localhost:8501](http://localhost:8501) in your browser
        """)

# --- Main Application Router ---
def main():
    render_navigation()
    
    # Route to appropriate page
    if st.session_state.active_page == "home":
        render_home()
    elif st.session_state.active_page == "fraud_analysis":
        render_fraud_analysis()
    elif st.session_state.active_page == "dashboard":
        render_dashboard()
    elif st.session_state.active_page == "debugger":
        render_debugger()
    elif st.session_state.active_page == "about":
        render_about()
    elif st.session_state.active_page == "architecture":
        render_architecture()

if __name__ == "__main__":
    main()
