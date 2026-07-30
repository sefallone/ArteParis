# pages/inicio.py - Dashboard inicial
import streamlit as st
from datetime import date, datetime
from services.tasa_service import TasaService

def show():
    """Página de inicio / Dashboard"""
    
    st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 2rem; border: 1px solid #e8ddd0; margin-bottom: 1.5rem;">
            <h2 style="color: #3d2218; margin: 0;">📊 Panel de Control</h2>
            <p style="color: #8b5a3c; margin: 0.3rem 0 0 0;">Bienvenido al sistema de gestión de Arte París</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener datos
    tasa_service = TasaService()
    tasa = st.session_state.get('tasa_actual', tasa_service.get_tasa())
    
    # Información del día
    hoy = date.today()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">📅 Fecha</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #3d2218;">
                    {hoy.strftime('%d/%m/%Y')}
                </div>
                <div style="color: #8b5a3c; font-size: 0.9rem;">
                    {hoy.strftime('%A')}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">💱 Tasa de Cambio</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #3d2218;">
                    1 $ = {tasa:,.2f} Bs
                </div>
                <div style="color: #8b5a3c; font-size: 0.9rem;">
                    Actualizada hoy
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        usuario = st.session_state.get('usuario', None)
        st.markdown(f"""
            <div class="card">
                <div class="card-title">👤 Usuario</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #3d2218;">
                    {usuario.nombre if usuario else 'Usuario'}
                </div>
                <div style="color: #8b5a3c; font-size: 0.9rem;">
                    Rol: {usuario.rol.capitalize() if usuario else 'Invitado'}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Guía rápida
    st.markdown("""
        <div style="background: #f5ede6; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; border: 1px solid #e8ddd0;">
            <h3 style="color: #3d2218; margin: 0 0 0.5rem 0;">🚀 Comienza aquí</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <strong style="color: #8b5a3c;">1.</strong>
                    <span style="color: #3d2218;">Configura la tasa del día en el modal inicial</span>
                </div>
                <div>
                    <strong style="color: #8b5a3c;">2.</strong>
                    <span style="color: #3d2218;">Registra tus productos en <strong>Inventario</strong></span>
                </div>
                <div>
                    <strong style="color: #8b5a3c;">3.</strong>
                    <span style="color: #3d2218;">Crea ventas en el módulo <strong>Ventas</strong></span>
                </div>
                <div>
                    <strong style="color: #8b5a3c;">4.</strong>
                    <span style="color: #3d2218;">Gestiona compras en <strong>Compras</strong></span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
