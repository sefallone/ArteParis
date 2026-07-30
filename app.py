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
        [data-testid="stSidebar"] .stSelectbox label {
            color: #d4a574 !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox select {
            background: #2c1810 !important;
            color: #f5deb3 !important;
            border: 1px solid #5c3324 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ============ INICIALIZACIÓN ============
def init_session_state():
    """Inicializa las variables de sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'tasa_actual' not in st.session_state:
        st.session_state.tasa_actual = 0
    if 'necesita_tasa' not in st.session_state:
        st.session_state.necesita_tasa = False

# ============ MAIN ============
def main():
    # Inicializar
    init_session_state()
    
    # Inicializar Firebase
    FirebaseService()
    
    # ============ LOGIN ============
    if not st.session_state.authenticated:
        # Página de login
        st.markdown("""
            <div style="max-width: 400px; margin: 3rem auto; text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">☕</div>
                <h1 style="color: #3d2218; font-family: 'Georgia', serif;">Arte París</h1>
                <p style="color: #8b5a3c; font-weight: 300; letter-spacing: 2px;">DELICAFE</p>
                <p style="color: #5c3324; font-size: 0.8rem; margin-bottom: 2rem;">Gestión Administrativa</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
                submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                
                if submitted:
                    if username and password:
                        auth_service = AuthService()
                        if auth_service.login(username, password):
                            st.rerun()
                    else:
                        st.error("❌ Por favor ingresa usuario y contraseña")
        
        return
    
    # ============ VERIFICAR TASA DEL DÍA ============
    if not render_tasa_modal():
        return
    
    # ============ APLICACIÓN PRINCIPAL ============
    # Renderizar header
    render_header()
    
    # Renderizar sidebar y obtener página seleccionada
    pagina = render_sidebar()
    
    # ============ CARGAR PÁGINA ============
    if pagina == "Inicio":
        from pages.inicio import show
        show()
    elif pagina == "Inventario":
        from pages.inventario import show
        show()
    elif pagina == "Ventas":
        from pages.ventas import show
        show()
    elif pagina == "Compras":
        from pages.compras import show
        show()
    elif pagina == "Balance Diario":
        from pages.balance import show
        show()
    elif pagina == "Nómina":
        st.info("📋 Módulo de Nómina en construcción")
    elif pagina == "Proveedores":
        st.info("📋 Módulo de Proveedores en construcción")
    elif pagina == "Clientes":
        st.info("📋 Módulo de Clientes en construcción")
    elif pagina == "Gerencia":
        st.info("📋 Módulo de Gerencia en construcción")
    else:
        from pages.inicio import show
        show()

if __name__ == "__main__":
    main()
