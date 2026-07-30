# components/header.py
import streamlit as st
import os
from datetime import datetime
from config import Config

def render_header():
    """Renderiza el header de la aplicación con logo y razón social"""
    
    # Verificar si existe el logo
    logo_path = Config.LOGO_PATH
    
    # Estilo CSS para el header
    st.markdown("""
        <style>
        .header-container {
            background: linear-gradient(135deg, #1a0e0a 0%, #3d2218 50%, #5c3324 100%);
            padding: 0.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid #8b5a3c;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        .header-logo {
            max-height: 60px;
            border-radius: 8px;
            border: 1px solid #8b5a3c;
        }
        .header-title {
            color: #f5deb3;
            font-family: 'Georgia', serif;
        }
        .header-title h1 {
            margin: 0;
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: 1px;
            color: #f5deb3;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        .header-title .subtitle {
            margin: 0;
            font-size: 0.8rem;
            color: #d4a574;
            letter-spacing: 2px;
            font-weight: 300;
        }
        .header-right {
            text-align: right;
            color: #d4a574;
            font-size: 0.85rem;
            border-left: 1px solid #5c3324;
            padding-left: 1.5rem;
        }
        .header-right .date {
            font-weight: 600;
            color: #f5deb3;
        }
        .header-right .user-info {
            color: #d4a574;
            font-size: 0.75rem;
        }
        .header-right .role-badge {
            display: inline-block;
            background: #8b5a3c;
            color: #f5deb3;
            padding: 0.1rem 0.8rem;
            border-radius: 20px;
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Obtener datos del usuario
    user_data = st.session_state.get('user_data', {})
    nombre_usuario = user_data.get('nombre', 'Visitante')
    rol_usuario = user_data.get('rol', '')
    
    # Formatear fecha
    fecha_actual = datetime.now().strftime('%A, %d de %B de %Y')
    # Capitalizar primera letra del día y mes
    dias = {'monday': 'Lunes', 'tuesday': 'Martes', 'wednesday': 'Miércoles', 
            'thursday': 'Jueves', 'friday': 'Viernes', 'saturday': 'Sábado', 'sunday': 'Domingo'}
    meses = {'january': 'Enero', 'february': 'Febrero', 'march': 'Marzo', 'april': 'Abril',
             'may': 'Mayo', 'june': 'Junio', 'july': 'Julio', 'august': 'Agosto',
             'september': 'Septiembre', 'october': 'Octubre', 'november': 'Noviembre', 'december': 'Diciembre'}
    
    fecha_actual = datetime.now()
    dia_nombre = dias.get(fecha_actual.strftime('%A').lower(), fecha_actual.strftime('%A'))
    mes_nombre = meses.get(fecha_actual.strftime('%B').lower(), fecha_actual.strftime('%B'))
    fecha_formateada = f"{dia_nombre}, {fecha_actual.day} de {mes_nombre} de {fecha_actual.year}"
    
    # Construir header
    col_logo, col_titulo, col_info = st.columns([1, 4, 2])
    
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=False, width=70)
        else:
            st.markdown(f"<div style='font-size: 2.5rem; text-align: center;'>☕</div>", unsafe_allow_html=True)
    
    with col_titulo:
        st.markdown(f"""
            <div class="header-title">
                <h1>Arte París - DELICAFE</h1>
                <p class="subtitle">{Config.APP_SUBTITLE}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_info:
        st.markdown(f"""
            <div class="header-right">
                <div class="date">📅 {fecha_formateada}</div>
                <div class="user-info">
                    {nombre_usuario}
                    {f'<span class="role-badge">{rol_usuario}</span>' if rol_usuario else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Línea separadora
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border: 1px solid #3d2218;'>", unsafe_allow_html=True)
