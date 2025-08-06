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

pio.templates.default = "plotly_white"  # or "ggplot2", "seaborn"

 

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

        padding-top: 1rem;

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

   

    /* Navigation Bar */

    .nav-container {

        background: #f8fafc;

        padding: 1rem 0;

        margin-bottom: 2rem;

        border-bottom: 1px solid #e2e8f0;

        position: sticky;

        top: 0;

        z-index: 100;

    }

   

    .nav-tabs {

        display: flex;

        justify-content: center;

        gap: 2rem;

        flex-wrap: wrap;

    }

   

    .nav-tab {

        background: transparent;

        border: none;

        padding: 0.75rem 1.5rem;

        border-radius: 8px;

        font-weight: 600;

        color: #64748b;

        cursor: pointer;

        transition: all 0.3s ease;

        text-decoration: none;

        font-size: 1rem;

    }

   

    .nav-tab:hover {

        color: #3b82f6;

        background-color: rgba(59,130,246,0.1);

    }

   

    .nav-tab.active {

        color: #dc2626;

        background-color: rgba(220,38,38,0.1);

    }

   

    /* Header Styling */

    .main-header {

        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);

        padding: 1.25rem 1rem;

        margin-bottom: 1rem;

        border-radius: 100px;

        color: white;

        text-align: center;

        box-shadow: 0 4px 20px rgba(0,0,0,0.1);

    }

   

    .main-title {

        font-size: 2.5rem;

        font-weight: 700;

        margin-bottom: 0.5rem;

        text-shadow: 0 2px 4px rgba(0,0,0,0.1);

        color: white !important;

    }

   

    .main-subtitle {

        font-size: 1.1rem;

        opacity: 0.9;

        font-weight: 400;

        margin-bottom: 1rem;

        color: white !important;

    }

   

    .creator-badge {

        background: rgba(255,255,255,0.2);

        padding: 0.5rem 1rem;

        border-radius: 20px;

        display: inline-block;

        font-weight: 500;

        backdrop-filter: blur(10px);

        color: white !important;

    }

   

    /* Home Page Specific Styles */

    .home-header {

        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);

        padding: 2rem 1rem;

        border-radius: 12px;

        color: white;

        text-align: center;

        margin-bottom: 2rem;

    }

   

    .home-header h1 {

        font-size: 2.5rem;

        font-weight: 700;

        color: white !important;

    }

   

    .home-header p {

        font-size: 1rem;

        font-weight: 400;

        margin-top: 0.5rem;

        color: white !important;

    }

   

    /* Ensure all header elements are white */

    .main-header *, .home-header * {

        color: white !important;

    }

   

    .section-title {

        font-size: 1.4rem;

        font-weight: 600;

        margin-top: 2rem;

    }

   

    /* Info Cards - ensure visibility */

    .info-card {

        background: #ffffff !important;

        border: 1px solid #e2e8f0;

        border-radius: 12px;

        padding: 1.5rem;

        margin: 1rem 0;

        box-shadow: 0 2px 8px rgba(0,0,0,0.05);

    }

 

    .info-card *, .info-card p, .info-card li, .info-card strong, .info-card h3 {

        color: #1e293b !important;

        background-color: transparent !important;

    }

   

    /* Metric Cards */

    .metric-card {

        background: white;

        border-radius: 12px;

        padding: 1.5rem;

        box-shadow: 0 2px 12px rgba(0,0,0,0.08);

        border: 1px solid #f1f5f9;

        text-align: center;

        margin: 0.5rem 0;

    }

   

    .metric-value {

        font-size: 2rem;

        font-weight: 700;

        margin-bottom: 0.5rem;

    }

   

    .metric-label {

        color: #64748b;

        font-size: 0.9rem;

        font-weight: 500;

    }

   

    /* Insight Cards */

    .insight-card {

        background: #f8fafc;

        border: 1px solid #e2e8f0;

        border-radius: 8px;

        padding: 1rem;

        margin: 0.5rem 0;

    }

   

    .insight-title {

        font-weight: 600;

        color: #1e293b;

        margin-bottom: 0.5rem;

    }

   

    .insight-text {

        color: #64748b;

        font-size: 0.9rem;

    }

   

    /* Status Badges */

    .status-safe {

        background: #dcfce7;

        color: #166534;

        padding: 0.5rem 1rem;

        border-radius: 20px;

        font-weight: 600;

        display: inline-block;

    }

   

    .status-fraud {

        background: #fecaca;

        color: #991b1b;

        padding: 0.5rem 1rem;

        border-radius: 20px;

        font-weight: 600;

        display: inline-block;

    }

   

    .status-escalated {

        background: #fef3c7;

        color: #92400e;

        padding: 0.5rem 1rem;

        border-radius: 20px;

        font-weight: 600;

        display: inline-block;

    }

   

    /* Input Field Helpers */

    .field-helper {

        background: #f1f5f9;

        border-left: 4px solid #3b82f6;

        padding: 0.75rem;

        margin: 0.5rem 0;

        border-radius: 4px;

        font-size: 0.9rem;

        color: #475569;

    }

   

    /* Loading Animation */

    .loading-text {

        text-align: center;

        color: #3b82f6;

        font-weight: 500;

        animation: pulse 2s infinite;

    }

   

    @keyframes pulse {

        0% { opacity: 1; }

        50% { opacity: 0.5; }

        100% { opacity: 1; }

    }

   

    /* Confidence Bar */

    .confidence-bar {

        width: 100%;

        height: 8px;

        background: #e2e8f0;

        border-radius: 4px;

        overflow: hidden;

        margin: 0.5rem 0;

    }

   

    .confidence-fill {

        height: 100%;

        border-radius: 4px;

        transition: width 0.5s ease;

    }

   

    /* Architecture Diagram */

    .architecture-container {

        background: #f8fafc;

        border: 2px solid #e2e8f0;

        border-radius: 12px;

        padding: 2rem;

        margin: 2rem 0;

        text-align: center;

    }

   

    .architecture-container h4 {

        color: #1e293b !important;

        margin-bottom: 1rem;

    }

   

    .architecture-container p {

        color: #64748b !important;

    }

   

    .agent-box {

        background: #ffffff;

        border: 1px solid #cbd5e1;

        border-radius: 8px;

        padding: 1rem;

        margin: 0.5rem;

        display: inline-block;

        box-shadow: 0 2px 4px rgba(0,0,0,0.1);

        color: #1e293b !important;

        font-weight: 600;

    }

   

    /* Fix expander text visibility */

    .streamlit-expanderHeader {

        color: #1e293b !important;

    }

   

    .streamlit-expanderContent {

        background-color: #ffffff !important;

        color: #1e293b !important;

    }

   

    /* Ensure metric cards text is visible */

    .metric-card * {

        color: #1e293b !important;

    }

   

    /* Button styling fixes */

    .stButton > button {

        background-color: #3b82f6 !important;

        color: white !important;

        border: none;

        border-radius: 8px;

        font-weight: 600;

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

   

    /* Input field styling */

    .stTextInput > div > div > input {

        color: #1e293b !important;

        background-color: #ffffff !important;

    }

   

    .stSelectbox > div > div > div {

        color: #1e293b !important;

        background-color: #ffffff !important;

    }

   

    .stNumberInput > div > div > input {

        color: #1e293b !important;

        background-color: #ffffff !important;

    }

   

    /* Labels for form fields */

    .stTextInput > label,

    .stSelectbox > label,

    .stNumberInput > label {

        color: #1e293b !important;

        font-weight: 500;

    }

   

    /* Sidebar styling if needed */

    .css-1d391kg {

        background-color: #ffffff !important;

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

        ('fraud_analysis', '🔍 Detect Fraud Transaction'),

        ('dashboard', '📊 Dashboard'),

        ('debugger', '🧠 Timeline Debugger'),

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

    <div style="text-align: center; font-weight: 600; color: {color};">

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

        st.session_state.error_message = f"
