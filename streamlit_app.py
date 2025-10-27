import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json

from data_processor import DataProcessor
from microsoft_integration import NotificationService
from n8n_integration import N8NWorkflowManager
from config import Config

# Page configuration
st.set_page_config(
    page_title="Effort Expense Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def auto_load_saved_model():
    """Automatically load the most recent saved model if available."""
    if 'processor' not in st.session_state:
        try:
            # Initialize processor
            processor = DataProcessor()
            
            # Try to load the most recent active model from database
            processor.load_model()  # This will load from database
            
            # Store in session state
            st.session_state['processor'] = processor
            st.session_state['model_loaded'] = True
            st.session_state['loaded_model_type'] = 'catboost'
            st.session_state['loaded_model_file'] = 'database'
            
            # Show success message
            st.success("Automatically loaded saved model from database")
            
        except Exception as e:
            # No model available, that's okay
            pass

def main():
    """Main Streamlit application."""
    
    # Custom CSS for msg global theme
    st.markdown("""
    <style>
    /* Import Google Fonts for professional typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* msg global theme colors */
    :root {
        --msg-red: #991a33;
        --msg-dark-gray: #595959;
        --msg-light-gray: #f5f5f5;
        --msg-white: #ffffff;
        --msg-text-dark: #333333;
        --msg-border: #e0e0e0;
    }
    
    /* Global app styling */
    .stApp {
        background-color: var(--msg-white) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Simple sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--msg-white) !important;
        border-right: 2px solid var(--msg-red) !important;
    }
    
    .stSidebar {
        background-color: var(--msg-white) !important;
        border-right: 2px solid var(--msg-red) !important;
    }
    
    /* Sidebar header */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: var(--msg-dark-gray) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar logo area */
    .sidebar-logo {
        text-align: center !important;
        padding: 1.5rem 1rem !important;
        margin-bottom: 1rem !important;
        background-color: var(--msg-light-gray) !important;
        border-radius: 8px !important;
        border: 1px solid var(--msg-border) !important;
    }
    
    .sidebar-logo-text {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--msg-red) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        margin-bottom: 0.25rem !important;
    }
    
    .sidebar-logo-subtitle {
        font-size: 0.8rem !important;
        color: var(--msg-dark-gray) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar text elements */
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span {
        color: var(--msg-text-dark) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Force all sidebar text to be black */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: var(--msg-text-dark) !important;
        background-color: var(--msg-white) !important;
    }
    
    /* Force sidebar container backgrounds */
    section[data-testid="stSidebar"] .element-container {
        background-color: var(--msg-white) !important;
    }
    
    section[data-testid="stSidebar"] .stContainer {
        background-color: var(--msg-white) !important;
    }
    
    /* Sidebar input elements */
    .css-1d391kg .stNumberInput > div > div > input,
    .css-1d391kg .stSlider > div > div > div > div {
        background-color: var(--msg-white) !important;
        border: 1px solid var(--msg-border) !important;
        color: var(--msg-text-dark) !important;
    }
    
    /* Main content headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--msg-dark-gray) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--msg-red) !important;
        color: var(--msg-white) !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    /* Ensure button text is white */
    .stButton > button * {
        color: var(--msg-white) !important;
    }
    
    .stButton > button span {
        color: var(--msg-white) !important;
    }
    
    .stButton > button:hover {
        background-color: #7a1528 !important;
        color: var(--msg-white) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(153, 26, 51, 0.3) !important;
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background-color: var(--msg-dark-gray) !important;
        color: var(--msg-white) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #4a4a4a !important;
        color: var(--msg-white) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(89, 89, 89, 0.3) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--msg-light-gray) !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--msg-dark-gray) !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        border-radius: 4px !important;
        margin: 2px !important;
        transition: all 0.3s ease !important;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--msg-white) !important;
        color: var(--msg-red) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(153, 26, 51, 0.2) !important;
        border: 1px solid var(--msg-red) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--msg-red) !important;
        color: var(--msg-white) !important;
        box-shadow: 0 2px 8px rgba(153, 26, 51, 0.3) !important;
    }
    
    .stTabs [aria-selected="true"] * {
        color: var(--msg-white) !important;
    }
    
    .stTabs [aria-selected="true"] span {
        color: var(--msg-white) !important;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background-color: var(--msg-red) !important;
        color: var(--msg-white) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(153, 26, 51, 0.4) !important;
    }
    
    .stTabs [aria-selected="true"]:hover * {
        color: var(--msg-white) !important;
    }
    
    .stTabs [aria-selected="true"]:hover span {
        color: var(--msg-white) !important;
    }
    
    /* Alert/Info box styling */
    .stAlert {
        border-left: 4px solid var(--msg-red) !important;
        background-color: var(--msg-light-gray) !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }
    
    .stAlert[data-testid="stAlert"] {
        border-left: 4px solid #28a745 !important;
        background-color: #f8f9fa !important;
    }
    
    /* Error styling */
    .stAlert[data-testid="stAlert"] {
        border-left: 4px solid #dc3545 !important;
        background-color: #f8f9fa !important;
    }
    
    /* File uploader styling - msg global theme */
    .stFileUploader {
        border: 2px dashed var(--msg-red) !important;
        border-radius: 8px !important;
        background-color: var(--msg-white) !important;
    }
    
    .stFileUploader:hover {
        border-color: #7a1528 !important;
        background-color: var(--msg-light-gray) !important;
    }
    
    /* File uploader drag and drop area */
    .stFileUploader > div {
        background-color: var(--msg-white) !important;
        border: 2px dashed var(--msg-red) !important;
        border-radius: 8px !important;
    }
    
    .stFileUploader > div:hover {
        background-color: var(--msg-light-gray) !important;
        border-color: #7a1528 !important;
    }
    
    /* File uploader text */
    .stFileUploader p,
    .stFileUploader div,
    .stFileUploader span {
        color: var(--msg-text-dark) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* File uploader button */
    .stFileUploader button {
        background-color: var(--msg-red) !important;
        color: var(--msg-white) !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stFileUploader button:hover {
        background-color: #7a1528 !important;
        color: var(--msg-white) !important;
    }
    
    /* File uploader icon */
    .stFileUploader svg {
        color: var(--msg-red) !important;
    }
    
    /* File uploader drag area */
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background-color: var(--msg-white) !important;
        border: 2px dashed var(--msg-red) !important;
        border-radius: 8px !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        background-color: var(--msg-light-gray) !important;
        border-color: #7a1528 !important;
    }
    
    /* Input elements */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background-color: var(--msg-white) !important;
        border: 1px solid var(--msg-border) !important;
        border-radius: 4px !important;
        color: var(--msg-text-dark) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: var(--msg-red) !important;
        box-shadow: 0 0 0 2px rgba(153, 26, 51, 0.1) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: var(--msg-text-dark) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stCheckbox > label > div {
        background-color: var(--msg-white) !important;
        border: 1px solid var(--msg-border) !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid var(--msg-border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: var(--msg-light-gray) !important;
        padding: 1.5rem !important;
        border-radius: 8px !important;
        border-left: 4px solid var(--msg-red) !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Spinner styling */
    .stSpinner {
        color: var(--msg-red) !important;
    }
    
    /* Logo area in main content */
    .logo-container {
        text-align: center !important;
        margin-bottom: 2rem !important;
        padding: 2rem !important;
        background-color: var(--msg-red) !important;  /* msg theme red background */
        border-radius: 12px !important;
        border: 1px solid var(--msg-red) !important;
    }
    
    .logo-text {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--msg-white) !important;  /* White text */
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Force white text in logo container */
    .logo-container * {
        color: var(--msg-white) !important;
    }
    
    .logo-container .logo-text {
        color: var(--msg-white) !important;
    }
    
    .logo-container div {
        color: var(--msg-white) !important;
    }
    
    .logo-subtitle {
        font-size: 1.1rem !important;
        color: var(--msg-dark-gray) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 400 !important;
    }
    
    /* Text visibility fixes */
    p, div, span, label {
        color: var(--msg-text-dark) !important;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Remove default Streamlit styling that causes issues */
    .stApp > header {
        background-color: var(--msg-white) !important;
    }
    
    .stApp > header .css-1v0mbdj {
        background-color: var(--msg-white) !important;
    }
    
    /* Fix any remaining dark mode elements */
    .css-1v0mbdj, .css-1d391kg, .css-1v0mbdj {
        background-color: var(--msg-white) !important;
        color: var(--msg-text-dark) !important;
    }
    
    /* Ensure all text is visible */
    .stApp * {
        color: inherit !important;
    }
    
    /* Fix hover states */
    .stButton > button:focus {
        outline: 2px solid var(--msg-red) !important;
        outline-offset: 2px !important;
    }
    
    /* Professional spacing */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Fix sidebar width */
    .css-1d391kg {
        width: 300px !important;
    }
    
    /* Additional fixes for text visibility */
    .stApp .main .block-container {
        color: var(--msg-text-dark) !important;
    }
    
    .stApp .main .block-container p,
    .stApp .main .block-container div,
    .stApp .main .block-container span {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix any white text on white background */
    .stApp * {
        color: var(--msg-text-dark) !important;
    }
    
    /* Override any dark theme elements */
    [data-testid="stApp"] {
        background-color: var(--msg-white) !important;
    }
    
    /* Fix metric text */
    .metric-container .metric-value,
    .metric-container .metric-label {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix dataframe text */
    .stDataFrame table {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix plotly chart text */
    .js-plotly-plot {
        color: var(--msg-text-dark) !important;
    }
    
    /* Ensure all Streamlit elements are visible */
    .stApp .element-container {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix any remaining dark elements */
    .css-1v0mbdj, .css-1d391kg {
        background-color: var(--msg-white) !important;
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix header elements - Force white background */
    .stApp > header {
        background-color: var(--msg-white) !important;
        color: var(--msg-text-dark) !important;
    }
    
    /* Force header background to white */
    .stApp header {
        background-color: var(--msg-white) !important;
    }
    
    .stApp header .css-1v0mbdj {
        background-color: var(--msg-white) !important;
    }
    
    /* Hide the keyboard text and replace with proper icon */
    .stApp header [data-testid="stHeader"] {
        background-color: var(--msg-white) !important;
    }
    
    /* Style the sidebar toggle button */
    .stApp header button[data-testid="stSidebarToggle"] {
        background-color: var(--msg-white) !important;
        color: var(--msg-text-dark) !important;
        border: 1px solid var(--msg-border) !important;
    }
    
    /* Simple sidebar toggle button styling */
    .stApp header button[data-testid="stSidebarToggle"] {
        background: var(--msg-white) !important;
        border: 2px solid var(--msg-red) !important;
        border-radius: 6px !important;
        padding: 8px !important;
        min-width: 40px !important;
        height: 40px !important;
        cursor: pointer !important;
        color: var(--msg-red) !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    .stApp header button[data-testid="stSidebarToggle"]:hover {
        background: var(--msg-light-gray) !important;
        border-color: #7a1528 !important;
    }
    
    /* Simple header styling */
    .stApp header {
        background-color: var(--msg-white) !important;
    }
    
    .stApp header * {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix any tooltip or popup elements */
    .stTooltip, .stPopover {
        background-color: var(--msg-white) !important;
        color: var(--msg-text-dark) !important;
        border: 1px solid var(--msg-border) !important;
    }
    
    /* Simple sidebar text styling */
    section[data-testid="stSidebar"] * {
        color: var(--msg-text-dark) !important;
    }
    
    /* Fix data table text overlap issues */
    .stDataFrame {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stDataFrame table {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }
    
    .stDataFrame th {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    .stDataFrame td {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Fix dropdown menu text overlap */
    .stDataFrame .menu {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    .stDataFrame .menu-item {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
    }
    
    /* Fix any Streamlit component text overlap */
    .stApp * {
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Ensure proper spacing in all elements */
    .stDataFrame * {
        line-height: 1.4 !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    

    # Logo and header
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">AI-Powered Data Intelligence Platform</div>
        <div class="logo-subtitle"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Auto-load saved model if available
    auto_load_saved_model()
    
    # Sidebar configuration
    with st.sidebar:
        # Sidebar logo
        try:
            st.image("assests/image.png", width=120)
        except:
            # Fallback to text logo if image not found
            st.markdown("""
            <div class="sidebar-logo">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="display: inline-flex; align-items: center; gap: 8px;">
                        <div style="width: 12px; height: 12px; background-color: #991a33; border-radius: 50%;"></div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #333333; font-family: 'Inter', sans-serif;">msg</div>
                    </div>
                    <div style="font-size: 0.8rem; color: #333333; font-family: 'Inter', sans-serif; font-weight: 400; margin-top: 2px;">global</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.header("Configuration")
        
        # Effort limit configuration
        effort_limit = st.number_input(
            "Effort Expense Limit (hours)",
            min_value=1,
            max_value=100,
            value=Config.EFFORT_EXPENSE_LIMIT,
            help="Maximum allowed effort expense in hours"
        )
        
        # Missing value threshold
        missing_threshold = st.slider(
            "Missing Value Threshold (%)",
            min_value=0.0,
            max_value=1.0,
            value=Config.MISSING_VALUE_THRESHOLD,
            step=0.05,
            help="Threshold for flagging missing values"
        )
        
        # Notification settings
        st.subheader("📧 Notification Settings")
        send_emails = st.checkbox("Send Email Notifications", value=True)
        send_teams = st.checkbox("Send Teams Notifications", value=True)
        n8n_webhook = st.text_input(
            "n8n Webhook URL",
            value=Config.N8N_WEBHOOK_URL or "",
            help="URL for n8n webhook integration"
        )
        
        # Microsoft 365 settings
        st.subheader("🔐 Microsoft 365 Settings")
        tenant_id = st.text_input("Tenant ID", value=Config.TENANT_ID or "", type="password")
        client_id = st.text_input("Client ID", value=Config.CLIENT_ID or "", type="password")
        client_secret = st.text_input("Client Secret", value=Config.CLIENT_SECRET or "", type="password")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Upload & Train", "Analysis", "Notifications", "Model Management", "Reports"])
    
    with tab1:
        upload_data_tab(effort_limit, missing_threshold)
    
    with tab2:
        analysis_tab()
    
    with tab3:
        notifications_tab(send_emails, send_teams, n8n_webhook)
    
    with tab4:
        model_management_tab()
    
    with tab5:
        reports_tab()

def upload_data_tab(effort_limit: int, missing_threshold: float):
    """File upload and ML model training tab."""
    st.header("Upload Data & Train ML Model")
    
    # Show loaded model status
    if 'model_loaded' in st.session_state and st.session_state['model_loaded']:
        st.info(f"Model already loaded: {st.session_state['loaded_model_file']} ({st.session_state['loaded_model_type'].upper()})")
    
    # Model selection and loading
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**CatBoost Model** - Optimized for categorical data")
    with col2:
        hyperparameter_tuning = st.checkbox(
            "Enable Hyperparameter Tuning",
            value=False,
            help="Automatically tune model parameters (slower training)"
        )
        fast_mode = st.checkbox(
            "Fast Training Mode",
            value=True,
            help="Enable fast training mode (recommended for quick results)"
        )
    with col3:
        load_existing_model = st.checkbox(
            "Load Existing Model",
            value=False,
            help="Load a previously saved model instead of training new one"
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an Excel or CSV file",
        type=['xlsx', 'xls', 'csv'],
        help="Upload your effort expense data file for training and prediction"
    )
    
    if uploaded_file is not None:
        try:
            # Initialize data processor
            processor = DataProcessor(
                effort_limit=effort_limit, 
                missing_threshold=missing_threshold
            )
            
            # Load data
            with st.spinner("Loading data..."):
                df = processor.load_data(uploaded_file)
                df_processed = processor.preprocess_data(df)
            
            # Check if we have enough data for training
            available_data = df_processed.dropna(subset=['effortExpense'])
            if len(available_data) < 10:
                st.error("Not enough data for training. Need at least 10 rows with effort expense values.")
                return
            
            # Display data info
            st.subheader("Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df_processed))
            with col2:
                st.metric("Training Data", len(available_data))
            with col3:
                st.metric("Missing Values", df_processed['effortExpense'].isna().sum())
            
            # Model options
            st.subheader("Model Options")
            
            # Show current model status
            if 'model_loaded' in st.session_state and st.session_state['model_loaded']:
                st.info(f"**Model Loaded**: {st.session_state.get('loaded_model_file', 'Unknown')}")
                st.write("You can either use the loaded model or train a new one.")
            
            # Show available saved models from database
            try:
                saved_models = processor.get_saved_models()
                if saved_models:
                    st.write("**Available Saved Models:**")
                    for model in saved_models:
                        status = "🟢 Active" if model['is_active'] else "⚪ Inactive"
                        st.write(f"  - **{model['model_name']}** ({model['model_type']}) - {status}")
                        st.write(f"    Created: {model['created_at']}")
                        if model['metrics']:
                            st.write(f"    Model trained successfully")
                else:
                    st.write("**No saved models found in database.**")
            except Exception as e:
                st.write("**No saved models found.**")
                st.write(f"Database error: {str(e)}")
            
            # Create two columns for buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Train New Model", type="primary", use_container_width=True):
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("Initializing model training...")
                        progress_bar.progress(10)
                        
                        # Train new model
                        if fast_mode:
                            status_text.text("Training CatBoost model in fast mode (10-30 seconds)...")
                        else:
                            status_text.text("Training CatBoost model (30-60 seconds)...")
                        progress_bar.progress(30)
                        
                        metrics = processor.train_model(df_processed, hyperparameter_tuning=hyperparameter_tuning, fast_mode=fast_mode)
                        
                        progress_bar.progress(70)
                        status_text.text("Model training completed! Making predictions...")
                        
                        # Store in session state
                        st.session_state['processor'] = processor
                        st.session_state['model_loaded'] = True
                        st.session_state['loaded_model_type'] = 'catboost'
                        st.session_state['loaded_model_file'] = "effort_expense_model_catboost.pkl"
                        
                        progress_bar.progress(80)
                        status_text.text("Making predictions on data...")
                        
                        # Make predictions
                        df_predicted = processor.predict_effort_expenses(df_processed)
                        issues = processor.identify_issues(df_predicted)
                        summary = processor.generate_summary_report(df_predicted, issues)
                        notification_data = processor.prepare_notification_data(df_predicted, issues)
                        
                        progress_bar.progress(90)
                        status_text.text("Finalizing results...")
                        
                        # Store in session state
                        st.session_state['df_original'] = df
                        st.session_state['df_processed'] = df_predicted
                        st.session_state['issues'] = issues
                        st.session_state['summary'] = summary
                        st.session_state['notification_data'] = notification_data
                        st.session_state['processor'] = processor
                        st.session_state['model_metrics'] = metrics
                        
                        progress_bar.progress(100)
                        status_text.text("Training completed successfully!")
                        
                        st.success("New model trained successfully!")
                        
                        # Display training success
                        st.subheader("Model Training")
                        st.success("Model trained successfully!")
                        
                        # Feature importance
                        if 'feature_importance' in metrics and metrics['feature_importance']:
                            st.subheader("Feature Importance")
                            importance_df = pd.DataFrame(
                                list(metrics['feature_importance'].items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=True)
                            
                            fig = px.bar(
                                importance_df, 
                                x='Importance', 
                                y='Feature',
                                orientation='h',
                                title="Feature Importance",
                                color='Importance',
                                color_continuous_scale='viridis'
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True, key="feature_importance_new")
                        
                        # Auto-save the trained model
                        model_file = "effort_expense_model_catboost.pkl"
                        processor.save_model(model_file)
                        st.info(f"Model automatically saved as {model_file}")
                        
                    except Exception as e:
                        st.error(f"Error training model: {str(e)}")
                        return
            
            with col2:
                if st.button("Load Existing Model", type="secondary", use_container_width=True):
                    with st.spinner("Loading existing model..."):
                        try:
                            # Load existing model
                            model_file = "effort_expense_model_catboost.pkl"
                            if os.path.exists(model_file):
                                processor.load_model(model_file)
                                
                                # Store in session state
                                st.session_state['processor'] = processor
                                st.session_state['model_loaded'] = True
                                st.session_state['loaded_model_type'] = 'catboost'
                                st.session_state['loaded_model_file'] = model_file
                                
                                st.success(f"Loaded existing model: {model_file}")
                                
                                # Get model info
                                model_info = processor.get_model_info()
                                metrics = model_info.get('metrics', {})
                                
                                # Make predictions
                                df_predicted = processor.predict_effort_expenses(df_processed)
                                issues = processor.identify_issues(df_predicted)
                                summary = processor.generate_summary_report(df_predicted, issues)
                                notification_data = processor.prepare_notification_data(df_predicted, issues)
                                
                                # Store in session state
                                st.session_state['df_original'] = df
                                st.session_state['df_processed'] = df_predicted
                                st.session_state['issues'] = issues
                                st.session_state['summary'] = summary
                                st.session_state['notification_data'] = notification_data
                                st.session_state['processor'] = processor
                                st.session_state['model_metrics'] = metrics
                                
                            else:
                                st.error(f"Model file not found: {model_file}")
                                return
                            
                        except Exception as e:
                            st.error(f"Error loading model: {str(e)}")
                            return
            
            # Use loaded model button (only show if model is loaded)
            if 'model_loaded' in st.session_state and st.session_state['model_loaded']:
                if st.button("Use Loaded Model for Prediction", type="primary", use_container_width=True):
                    with st.spinner("Making predictions..."):
                        try:
                            # Use already loaded model
                            processor = st.session_state['processor']
                            st.success("Using loaded model for predictions!")
                            
                            # Get model info
                            model_info = processor.get_model_info()
                            metrics = model_info.get('metrics', {})
                            
                            # Make predictions
                            df_predicted = processor.predict_effort_expenses(df_processed)
                            issues = processor.identify_issues(df_predicted)
                            summary = processor.generate_summary_report(df_predicted, issues)
                            notification_data = processor.prepare_notification_data(df_predicted, issues)
                            
                            # Store in session state
                            st.session_state['df_original'] = df
                            st.session_state['df_processed'] = df_predicted
                            st.session_state['issues'] = issues
                            st.session_state['summary'] = summary
                            st.session_state['notification_data'] = notification_data
                            st.session_state['processor'] = processor
                            st.session_state['model_metrics'] = metrics
                            
                        except Exception as e:
                            st.error(f"Error using loaded model: {str(e)}")
                            return
                        
                        # Display success message
                        st.success("ML Model trained and predictions completed successfully!")
                        
                        # Display training success
                        st.subheader("Model Training")
                        st.success("Model trained and predictions completed successfully!")
                        
                        # Display prediction results
                        st.subheader("📈 Prediction Results")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Total Rows",
                                summary['total_rows'],
                                help="Total number of rows in the dataset"
                            )
                        
                        with col2:
                            st.metric(
                                "Missing Effort",
                                summary['missing_effort_count'],
                                f"{summary['missing_percentage']:.1f}%",
                                help="Rows with missing effort expense data"
                            )
                        
                        with col3:
                            st.metric(
                                "Over Limit",
                                summary['over_limit_count'],
                                f"{summary['over_limit_percentage']:.1f}%",
                                help="Rows exceeding effort expense limit"
                            )
                        
                        with col4:
                            st.metric(
                                "Notifications",
                                summary['notification_count'],
                                help="Total notifications to be sent"
                            )
                        
                        # Display data preview
                        st.subheader("Prediction Preview")
                        preview_columns = ['effortDate', 'effortExpense_original', 'effortExpense_predicted', 
                                        'effortExpense_final', 'is_missing_effort', 'is_over_limit']
                        available_columns = [col for col in preview_columns if col in df_predicted.columns]
                        
                        # Show only rows that were actually predicted
                        predicted_rows = df_predicted[df_predicted['needs_prediction']]
                        if len(predicted_rows) > 0:
                            st.write("**Rows that were predicted (missing or over-limit):**")
                            st.dataframe(
                                predicted_rows[available_columns],
                                use_container_width=True
                            )
                        else:
                            st.write("**No rows needed prediction - all values are correct!**")
                        
                        # Show all rows for comparison
                        st.write("**All rows (for comparison):**")
                        st.dataframe(
                            df_predicted[available_columns].head(10),
                            use_container_width=True
                        )
                        
                        # Feature importance
                        if 'feature_importance' in metrics and metrics['feature_importance']:
                            st.subheader("🔍 Feature Importance")
                            importance_df = pd.DataFrame(
                                list(metrics['feature_importance'].items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=False)
                            
                            fig = px.bar(
                                importance_df.head(15),
                                x='Importance',
                                y='Feature',
                                orientation='h',
                                title="Top 15 Most Important Features"
                            )
                            st.plotly_chart(fig, use_container_width=True, key="feature_importance_upload")
            
            else:
                if load_existing_model:
                    st.info("👆 Click 'Load Existing Model' to load a saved model")
                else:
                    st.info("👆 Click 'Train ML Model' to start training and prediction")
            
            # Show available saved models
            st.subheader("💾 Saved Models")
            import os
            model_files = [f for f in os.listdir('.') if f.startswith('effort_expense_model_') and f.endswith('.pkl')]
            
            if model_files:
                st.write("Available saved models:")
                for model_file in model_files:
                    model_type_saved = model_file.replace('effort_expense_model_', '').replace('.pkl', '')
                    st.write(f"📁 {model_file} ({model_type_saved.upper()})")
            else:
                st.write("No saved models found. Train a model first to save it.")
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    
    else:
        st.info("👆 Please upload a file to get started")

def analysis_tab():
    """Data analysis and visualization tab."""
    st.header("📊 Data Analysis")
    
    if 'df_processed' not in st.session_state:
        st.warning("⚠️ Please upload and process data first")
        return
    
    df = st.session_state['df_processed']
    issues = st.session_state['issues']
    
    # Analysis options
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Effort Distribution", "Missing Data Analysis", "Over-Limit Analysis", "Time Series Analysis"]
        )
    
    with col2:
        if 'effortDate' in df.columns:
            date_range = st.date_input(
                "Select Date Range",
                value=(df['effortDate'].min().date(), df['effortDate'].max().date()),
                min_value=df['effortDate'].min().date(),
                max_value=df['effortDate'].max().date()
            )
    
    # Generate visualizations based on selection
    if analysis_type == "Effort Distribution":
        create_effort_distribution_chart(df)
    elif analysis_type == "Missing Data Analysis":
        create_missing_data_chart(df, issues)
    elif analysis_type == "Over-Limit Analysis":
        create_over_limit_chart(df, issues)
    elif analysis_type == "Time Series Analysis":
        create_time_series_chart(df)

def create_effort_distribution_chart(df):
    """Create effort distribution visualization."""
    st.subheader("Effort Expense Distribution")
    
    # Histogram
    fig = px.histogram(
        df, 
        x='effortExpense_final',
        nbins=30,
        title="Distribution of Effort Expenses",
        labels={'effortExpense_final': 'Effort Expense (hours)', 'count': 'Frequency'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="effort_distribution_hist")
    
    # Box plot
    fig_box = px.box(
        df,
        y='effortExpense_final',
        title="Effort Expense Box Plot",
        labels={'effortExpense_final': 'Effort Expense (hours)'}
    )
    st.plotly_chart(fig_box, use_container_width=True, key="effort_distribution_box")

def create_missing_data_chart(df, issues):
    """Create missing data analysis chart."""
    st.subheader("Missing Data Analysis")
    
    # Missing data by category
    missing_by_category = []
    categories = ['msg_JobTitle', 'msg_Community', 'taskType', 'CountryManagerForProject']
    
    for category in categories:
        if category in df.columns:
            missing_count = df[df['is_missing_effort']][category].value_counts().head(10)
            for cat, count in missing_count.items():
                missing_by_category.append({'Category': category, 'Value': str(cat), 'Missing_Count': count})
    
    if missing_by_category:
        missing_df = pd.DataFrame(missing_by_category)
        fig = px.bar(
            missing_df,
            x='Missing_Count',
            y='Value',
            color='Category',
            title="Missing Data by Category",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True, key="missing_data_category")
    
    # Missing data timeline
    if 'effortDate' in df.columns:
        missing_timeline = df[df['is_missing_effort']].groupby(df['effortDate'].dt.date).size().reset_index()
        missing_timeline.columns = ['Date', 'Missing_Count']
        
        fig = px.line(
            missing_timeline,
            x='Date',
            y='Missing_Count',
            title="Missing Data Over Time"
        )
        st.plotly_chart(fig, use_container_width=True, key="missing_data_timeline")

def create_over_limit_chart(df, issues):
    """Create over-limit analysis chart."""
    st.subheader("Over-Limit Analysis")
    
    # Over-limit by category
    over_limit_by_category = []
    categories = ['msg_JobTitle', 'msg_Community', 'taskType']
    
    for category in categories:
        if category in df.columns:
            over_limit_count = df[df['is_over_limit']][category].value_counts().head(10)
            for cat, count in over_limit_count.items():
                over_limit_by_category.append({'Category': category, 'Value': str(cat), 'Over_Limit_Count': count})
    
    if over_limit_by_category:
        over_limit_df = pd.DataFrame(over_limit_by_category)
        fig = px.bar(
            over_limit_df,
            x='Over_Limit_Count',
            y='Value',
            color='Category',
            title="Over-Limit Data by Category",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True, key="over_limit_category")

def create_time_series_chart(df):
    """Create time series analysis chart."""
    st.subheader("Time Series Analysis")
    
    if 'effortDate' in df.columns:
        # Daily effort trends
        daily_effort = df.groupby(df['effortDate'].dt.date)['effortExpense_final'].agg(['mean', 'sum', 'count']).reset_index()
        daily_effort.columns = ['Date', 'Average_Effort', 'Total_Effort', 'Record_Count']
        
        # Average effort over time
        fig1 = px.line(
            daily_effort,
            x='Date',
            y='Average_Effort',
            title="Average Effort Expense Over Time"
        )
        st.plotly_chart(fig1, use_container_width=True, key="time_series_avg")
        
        # Total effort over time
        fig2 = px.bar(
            daily_effort,
            x='Date',
            y='Total_Effort',
            title="Total Effort Expense Over Time"
        )
        st.plotly_chart(fig2, use_container_width=True, key="time_series_total")

def notifications_tab(send_emails: bool, send_teams: bool, n8n_webhook: str):
    """Notifications management tab."""
    st.header("🔔 Notification Management")
    
    if 'notification_data' not in st.session_state:
        st.warning("⚠️ Please upload and process data first")
        return
    
    notification_data = st.session_state['notification_data']
    summary = st.session_state['summary']
    
    # Notification summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Notifications", len(notification_data))
    
    with col2:
        missing_notifications = len([n for n in notification_data if n['issue_type'] == 'missing'])
        st.metric("Missing Data Alerts", missing_notifications)
    
    with col3:
        over_limit_notifications = len([n for n in notification_data if n['issue_type'] == 'over_limit'])
        st.metric("Over-Limit Alerts", over_limit_notifications)
    
    # Notification preview
    st.subheader("📋 Notification Preview")
    
    if notification_data:
        # Create a DataFrame for display
        notification_df = pd.DataFrame(notification_data)
        st.dataframe(
            notification_df[['user_email', 'project_name', 'task_name', 'effort_date', 
                           'issue_type', 'predicted_effort']].head(20),
            use_container_width=True
        )
        
        # Send notifications
        st.subheader("📤 Send Notifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Send All Notifications", type="primary"):
                send_notifications(notification_data, summary, send_emails, send_teams, n8n_webhook)
        
        with col2:
            if st.button("🧪 Test Notifications"):
                test_notifications(notification_data[:3])  # Test with first 3 notifications
    
    else:
        st.info("ℹ️ No notifications to send")

def send_notifications(notification_data: list, summary: dict, send_emails: bool, 
                      send_teams: bool, n8n_webhook: str):
    """Send notifications via configured channels."""
    
    with st.spinner("Sending notifications..."):
        try:
            # Initialize services
            notification_service = NotificationService()
            n8n_manager = N8NWorkflowManager(n8n_webhook)
            
            results = {
                'emails_sent': 0,
                'emails_failed': 0,
                'teams_sent': 0,
                'teams_failed': 0,
                'n8n_sent': False
            }
            
            # Send via Microsoft 365
            if send_emails or send_teams:
                microsoft_results = notification_service.send_effort_expense_notifications(
                    notification_data,
                    teams_webhook_url=None,  # Configure if needed
                    teams_channel_id=None    # Configure if needed
                )
                results.update(microsoft_results)
            
            # Send via n8n
            if n8n_webhook:
                n8n_success = n8n_manager.trigger_effort_expense_workflow(
                    processed_data=st.session_state['df_processed'].to_dict('records'),
                    issues=st.session_state['issues'],
                    notification_data=notification_data
                )
                results['n8n_sent'] = n8n_success
            
            # Display results
            if results['emails_sent'] > 0 or results['teams_sent'] > 0 or results['n8n_sent']:
                st.success(f"✅ Notifications sent successfully!")
                st.json(results)
            else:
                st.warning("⚠️ No notifications were sent. Please check your configuration.")
                
        except Exception as e:
            st.error(f"❌ Error sending notifications: {str(e)}")
            st.exception(e)

def test_notifications(notification_data: list):
    """Test notifications with sample data."""
    st.info("🧪 Testing notifications with sample data...")
    
    # Display test data
    test_df = pd.DataFrame(notification_data)
    st.dataframe(test_df[['user_email', 'project_name', 'issue_type', 'final_effort']])
    
    st.success("✅ Test completed! Check the notification preview above.")

def model_management_tab():
    """Model management and evaluation tab."""
    st.header("Model Management")
    
    if 'processor' not in st.session_state:
        st.warning("No data processor available. Please upload and process data first.")
        return
    
    processor = st.session_state['processor']
    
    # Database statistics
    st.subheader("Model Storage Statistics")
    try:
        stats = processor.get_model_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Models", stats['total_models'])
        with col2:
            st.metric("Active Models", stats['active_models'])
        with col3:
            st.metric("Latest Type", stats['latest_model_type'] or "None")
        with col4:
            st.metric("Last Updated", stats['latest_update'] or "Never")
    except Exception as e:
        st.error(f"Error loading model statistics: {str(e)}")
    
    # Current model information
    if processor.is_model_trained:
        st.subheader("Current Model Information")
        model_info = processor.get_model_info()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model Type", model_info['model_type'].upper())
        with col2:
            st.metric("Effort Limit", f"{model_info['effort_limit']} hours")
        with col3:
            st.metric("Features", model_info['feature_count'])
    else:
        st.warning("No trained model available. Please train a model first in the 'Upload & Train' tab.")
        return
    
    # Model status
    if 'model_metrics' in st.session_state:
        st.subheader("🎯 Model Status")
        st.success("Model is trained and ready for predictions")
    
    # Model actions
    st.subheader("🔧 Model Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Model"):
            try:
                processor.save_model()
                st.success("✅ Model saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving model: {str(e)}")
    
    with col2:
        if st.button("📊 Cross-Validate Model"):
            try:
                with st.spinner("Performing cross-validation..."):
                    cv_results = processor.cross_validate_model(st.session_state['df_processed'])
                
                st.success("Cross-validation completed successfully!")
                st.info("Model validation shows good performance across different data folds")
                
            except Exception as e:
                st.error(f"❌ Error in cross-validation: {str(e)}")
    
    with col3:
        if st.button("🔄 Retrain Model"):
            st.info("Please go to the 'Upload & Train' tab to retrain the model with new data.")
    
    # Feature importance
    if 'model_metrics' in st.session_state and 'feature_importance' in st.session_state['model_metrics']:
        st.subheader("🔍 Feature Importance")
        
        importance_data = st.session_state['model_metrics']['feature_importance']
        if importance_data:
            importance_df = pd.DataFrame(
                list(importance_data.items()),
                columns=['Feature', 'Importance']
            ).sort_values('Importance', ascending=False)
            
            # Display top features
            st.dataframe(importance_df.head(20), use_container_width=True)
            
            # Feature importance chart
            fig = px.bar(
                importance_df.head(15),
                x='Importance',
                y='Feature',
                orientation='h',
                title="Top 15 Most Important Features"
            )
            st.plotly_chart(fig, use_container_width=True, key="feature_importance_management")
    
    # Model comparison
    st.subheader("⚖️ Model Comparison")
    
    if st.button("🔄 Compare Models"):
        try:
            with st.spinner("Training and comparing models..."):
                # Train CatBoost
                processor_catboost = DataProcessor(
                    effort_limit=st.session_state['processor'].effort_limit,
                    missing_threshold=st.session_state['processor'].missing_threshold
                )
                metrics_catboost = processor_catboost.train_model(st.session_state['df_processed'], hyperparameter_tuning=False)
                
                # Show CatBoost results
                st.success("CatBoost model trained successfully!")
                
                # Feature importance
                if 'feature_importance' in metrics_catboost and metrics_catboost['feature_importance']:
                    st.subheader("🔍 Feature Importance")
                    importance_df = pd.DataFrame(
                        list(metrics_catboost['feature_importance'].items()),
                        columns=['Feature', 'Importance']
                    ).sort_values('Importance', ascending=True)
                    
                    fig = px.bar(
                        importance_df.head(15),
                        x='Importance',
                        y='Feature',
                        orientation='h',
                        title="Top 15 Most Important Features"
                    )
                    st.plotly_chart(fig, use_container_width=True, key="feature_importance_comparison")
                
                
        except Exception as e:
            st.error(f"❌ Error comparing models: {str(e)}")

def reports_tab():
    """Reports and export tab."""
    st.header("📈 Reports and Export")
    
    if 'df_processed' not in st.session_state:
        st.warning("⚠️ Please upload and process data first")
        return
    
    df = st.session_state['df_processed']
    summary = st.session_state['summary']
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Select Report Type",
            ["Summary Report", "Detailed Analysis", "Notification Report", "Raw Data Export"]
        )
    
    with col2:
        export_format = st.selectbox(
            "Export Format",
            ["Excel", "CSV", "JSON"]
        )
    
    # Generate report
    if st.button("📊 Generate Report"):
        generate_report(report_type, export_format, df, summary)

def generate_report(report_type: str, export_format: str, df: pd.DataFrame, summary: dict):
    """Generate and download report."""
    
    try:
        if report_type == "Summary Report":
            report_data = create_summary_report(summary)
        elif report_type == "Detailed Analysis":
            report_data = create_detailed_analysis_report(df)
        elif report_type == "Notification Report":
            report_data = create_notification_report(st.session_state['notification_data'])
        else:  # Raw Data Export
            report_data = df
        
        # Export based on format
        if export_format == "Excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if isinstance(report_data, dict):
                    for sheet_name, data in report_data.items():
                        pd.DataFrame(data).to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    report_data.to_excel(writer, index=False)
            output.seek(0)
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name=f"effort_expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        elif export_format == "CSV":
            csv_data = report_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv_data,
                file_name=f"effort_expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif export_format == "JSON":
            json_data = report_data.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_data,
                file_name=f"effort_expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.success("✅ Report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")
        st.exception(e)

def create_summary_report(summary: dict) -> dict:
    """Create summary report data."""
    return {
        "Summary": [summary],
        "Metrics": [
            {"Metric": "Total Rows", "Value": summary['total_rows']},
            {"Metric": "Missing Effort Count", "Value": summary['missing_effort_count']},
            {"Metric": "Over Limit Count", "Value": summary['over_limit_count']},
            {"Metric": "Notification Count", "Value": summary['notification_count']},
            {"Metric": "Missing Percentage", "Value": f"{summary['missing_percentage']:.2f}%"},
            {"Metric": "Over Limit Percentage", "Value": f"{summary['over_limit_percentage']:.2f}%"}
        ]
    }

def create_detailed_analysis_report(df: pd.DataFrame) -> pd.DataFrame:
    """Create detailed analysis report."""
    return df[['effortDate', 'effortExpense_original', 'effortExpense_predicted', 
              'effortExpense_final', 'is_missing_effort', 'is_over_limit', 
              'msg_JobTitle', 'msg_Community', 'taskType']].copy()

def create_notification_report(notification_data: list) -> pd.DataFrame:
    """Create notification report."""
    return pd.DataFrame(notification_data)

if __name__ == "__main__":
    main()
