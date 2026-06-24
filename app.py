import streamlit as st
from streamlit_option_menu import option_menu
from utils.auth import init_auth, login, logout
from firebase_config import init_firebase
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="DELICAFE - Sistema de Gestión",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Firebase
init_firebase()

# Inicializar autenticación
init_auth()

# CSS personalizado con colores del logo
st.markdown("""
    <style>
        /* Colores basados en el logo */
        :root {
            --primary-color: #8B4513;
            --secondary-color: #D2691E;
            --accent-color: #F5DEB3;
            --dark-color: #2C1810;
            --light-color: #FFF8F0;
        }
        
        /* Estilos generales */
        .stApp {
            background-color: var(--light-color);
        }
        
        .main-header {
            background-color: var(--dark-color);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            color: var(--accent-color);
            font-family: 'Georgia', serif;
            text-align: center;
        }
        
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid var(--primary-color);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .metric-label {
            color: var(--dark-color);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Botones personalizados */
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
        }
        
        /* Sidebar personalizada */
        .css-1d391kg {
            background-color: var(--dark-color);
        }
        
        .css-1d391kg .stSelectbox label {
            color: var(--accent-color);
        }
    </style>
""", unsafe_allow_html=True)

def main():
    # Mostrar logo en sidebar
    if os.path.exists("assets/logo_nuevo.jpg"):
        st.sidebar.image("assets/logo_nuevo.jpg", use_column_width=True)
    
    # Estado de autenticación
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Mostrar login
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                    <div style="text-align: center; padding: 2rem;">
                        <h1 style="color: #8B4513;">☕ DELICAFE</h1>
                        <h3 style="color: #2C1810;">Sistema de Gestión</h3>
                        <hr>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form("login_form"):
                    username = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                    
                    if submit:
                        if login(username, password):
                            st.rerun()
                        else:
                            st.error("Credenciales inválidas")
    else:
        # Menú de navegación
        with st.sidebar:
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <p style="color: #F5DEB3;">Bienvenido, {st.session_state.user_data.get('nombre', 'Usuario')}</p>
                    <p style="color: #F5DEB3; font-size: 0.8rem;">Rol: {st.session_state.user_data.get('rol', '')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            selected = option_menu(
                menu_title=None,
                options=["Inicio", "Inventario", "Compras", "Ventas", "Balance Diario"],
                icons=["house", "box", "cart", "cash", "clipboard-data"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#2C1810"},
                    "icon": {"color": "#F5DEB3", "font-size": "20px"},
                    "nav-link": {"color": "#F5DEB3", "font-size": "16px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#8B4513"},
                }
            )
            
            if st.button("Cerrar Sesión", use_container_width=True):
                logout()
                st.rerun()
        
        # ==================== IMPORTACIONES CORREGIDAS ====================
        # Cargar página seleccionada con los nombres exactos de los archivos
        if selected == "Inicio":
            from pages.Inicio import show
            show()
        elif selected == "Inventario":
            from pages.Inventario import show
            show()
        elif selected == "Compras":
            from pages.Compras import show
            show()
        elif selected == "Ventas":
            from pages.Ventas import show
            show()
        elif selected == "Balance Diario":
            from pages.Balance_Diario import show
            show()

if __name__ == "__main__":
    main()
    
