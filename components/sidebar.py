# components/sidebar.py
import streamlit as st
from config import Config

def render_sidebar():
    """Renderiza el menú lateral sin iconos"""
    
    with st.sidebar:
        # Logo pequeño en el sidebar
        if st.session_state.get('authenticated', False):
            st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem 0; border-bottom: 1px solid #3d2218; margin-bottom: 1rem;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #8b5a3c;">☕</div>
                    <div style="color: #f5deb3; font-size: 0.8rem;">{Config.APP_NAME}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Menú de navegación (sin iconos)
            opciones = [
                "Inicio",
                "Inventario",
                "Ventas",
                "Compras",
                "Balance Diario"
            ]
            
            # Opciones adicionales según rol
            usuario = st.session_state.get('usuario', None)
            if usuario and usuario.tiene_permiso('gerente'):
                opciones.extend(["Nómina", "Proveedores", "Clientes"])
            
            if usuario and usuario.es_admin():
                opciones.append("Gerencia")
            
            selected = st.radio(
                "Navegación",
                opciones,
                index=0,
                key="menu_principal"
            )
            
            # Línea separadora
            st.markdown("---")
            
            # Mostrar tasa del día
            tasa = st.session_state.get('tasa_actual', 0)
            if tasa > 0:
                st.markdown(f"""
                    <div style="background: #2c1810; padding: 0.5rem 1rem; border-radius: 8px; text-align: center; border: 1px solid #5c3324;">
                        <span style="color: #d4a574; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Tasa del día</span>
                        <div style="color: #f5deb3; font-size: 1.1rem; font-weight: 600;">1 $ = {tasa:,.2f} Bs</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botón de cerrar sesión (sin icono)
            if st.button("Cerrar Sesión", use_container_width=True):
                from services.auth_service import AuthService
                AuthService().logout()
                st.rerun()
            
            return selected
        
        return None
