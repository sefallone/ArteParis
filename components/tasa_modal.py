# components/tasa_modal.py
import streamlit as st
from services.tasa_service import TasaService
from config import Config

def render_tasa_modal():
    """Muestra un modal para configurar la tasa de cambio del día"""
    
    # Verificar si necesita mostrar la tasa
    if not st.session_state.get('necesita_tasa', False):
        return True
    
    # CSS para el modal
    st.markdown("""
        <style>
        .tasa-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tasa-modal-content {
            background: linear-gradient(135deg, #2c1810 0%, #4a2818 100%);
            padding: 2.5rem;
            border-radius: 16px;
            max-width: 450px;
            width: 90%;
            border: 2px solid #8b5a3c;
            box-shadow: 0 20px 60px rgba(0,0,0,0.8);
            text-align: center;
        }
        .tasa-modal-content h2 {
            color: #f5deb3;
            font-family: 'Georgia', serif;
            margin-bottom: 0.5rem;
        }
        .tasa-modal-content p {
            color: #d4a574;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        .tasa-modal-content .tasa-input {
            background: #1a0e0a;
            border: 2px solid #8b5a3c;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #f5deb3;
            font-size: 1.5rem;
            text-align: center;
            width: 100%;
            font-weight: 600;
        }
        .tasa-modal-content .tasa-input:focus {
            outline: none;
            border-color: #f5deb3;
        }
        .tasa-modal-content .btn-guardar {
            background: #8b5a3c;
            color: #f5deb3;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            transition: all 0.3s;
        }
        .tasa-modal-content .btn-guardar:hover {
            background: #a06b4a;
            transform: translateY(-2px);
        }
        .tasa-modal-content .info-text {
            color: #8b5a3c;
            font-size: 0.7rem;
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Contenido del modal
    st.markdown("""
        <div class="tasa-modal-overlay">
            <div class="tasa-modal-content">
                <div style="font-size: 2.5rem;">💱</div>
                <h2>Configurar Tasa del Día</h2>
                <p>Ingresa el valor de 1 Dólar (USD) en Bolívares (Bs.)</p>
    """, unsafe_allow_html=True)
    
    # Formulario dentro del modal
    with st.form("tasa_dia_form", clear_on_submit=True):
        tasa = st.number_input(
            "1 USD = ",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            value=Config.TASA_DEFAULT,
            key="tasa_dia_input",
            label_visibility="collapsed",
            placeholder="Ej: 780.00"
        )
        
        submitted = st.form_submit_button("Guardar Tasa del Día", use_container_width=True)
        
        if submitted:
            if tasa > 0:
                tasa_service = TasaService()
                if tasa_service.guardar_tasa(tasa):
                    st.session_state['tasa_actual'] = tasa
                    st.session_state['necesita_tasa'] = False
                    st.success(f"✅ Tasa guardada: 1 $ = {tasa:,.2f} Bs")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar la tasa")
            else:
                st.error("❌ La tasa debe ser mayor a 0")
    
    st.markdown("""
                <div class="info-text">Esta tasa se usará para todas las operaciones del día.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    return False
