# app.py - Punto de entrada de la aplicación
import streamlit as st
from config import Config
from services.firebase_service import FirebaseService
from services.auth_service import AuthService
from components.header import render_header
from components.sidebar import render_sidebar
from components.tasa_modal import render_tasa_modal

# ============ CONFIGURACIÓN DE PÁGINA ============
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CSS GLOBAL ============
st.markdown("""
    <style>
        /* Reset y estilos globales */
        .stApp {
            background-color: #faf6f0;
        }
        
        /* Contenedor principal */
        .main {
            padding: 0 1rem;
        }
        
        /* Estilo para tarjetas */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e8ddd0;
            margin-bottom: 1rem;
        }
        
        .card-title {
            color: #3d2218;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Sidebar personalizado */
        [data-testid="stSidebar"] {
            background-color: #1a0e0a;
            border-right: 1px solid #3d2218;
        }
        
        [data-testid="stSidebar"] .stRadio label {
            color: #d4a574 !important;
            font-size: 0.9rem !important;
            padding: 0.4rem 0.8rem !important;
            border-radius: 6px !important;
            transition: all 0.2s !important;
        }
        
        [data-testid="stSidebar"] .stRadio label:hover {
            background: #2c1810 !important;
        }
        
        [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] {
            color: #f5deb3 !important;
        }
        
        /* Botones */
        .stButton > button {
            background: #8b5a3c !important;
            color: #f5deb3 !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s !important;
        }
        
        .stButton > button:hover {
            background: #a06b4a !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(139, 90, 60, 0.3) !important;
        }
        
        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #3d2218 !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #8b5a3c !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        /* Inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select {
            border: 1px solid #d4c5b8 !important;
            border-radius: 8px !important;
            background: white !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #8b5a3c !important;
            box-shadow: 0 0 0 2px rgba(139, 90, 60, 0.2) !important;
        }
        
        /* Tablas */
        .stDataFrame {
            border-radius: 8px !important;
            border: 1px solid #e8ddd0 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #f5ede6 !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 0.5rem 1.2rem !important;
            color: #5c3324 !important;
            font-weight: 500 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: #8b5a3c !important;
            color: #f5deb3 !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: #f5ede6 !important;
            border-radius: 8px !important;
            color: #3d2218 !important;
            font-weight: 600 !important;
        }
        
        .streamlit-expanderContent {
            border: 1px solid #e8ddd0 !important;
            border-radius: 0 0 8px 8px !important;
            padding: 1rem !important;
        }
        
        /* Alerts */
        .stAlert {
            border-radius: 8px !important;
            border-left: 4px solid #8b5a3c !important;
        }
        
        /* Selectbox en sidebar */
        [data-testid="stSidebar"] .stSelect
