# pages/inicio.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.database import (
    get_balance_diario, get_tasa_cambio,
    get_ventas, get_compras, get_productos
)
import plotly.express as px
import plotly.graph_objects as go

def show():
    # ==================== HEADER ====================
    st.markdown("""
        <div style="background: linear-gradient(135deg, #2C1810 0%, #4A2818 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h1 style="color: #F5DEB3; font-size: 2.5rem; margin: 0;">☕ DELICAFE</h1>
                    <p style="color: #D4A574; font-size: 1.1rem; margin: 0;">
                        Sistema Integral de Gestión Financiera y Administrativa
                    </p>
                </div>
                <div style="text-align: right;">
                    <p style="color: #F5DEB3; font-size: 0.9rem; margin: 0;">
                        Bienvenido, <strong>{}</strong>
                    </p>
                    <p style="color: #D4A574; font-size: 0.8rem; margin: 0;">
                        {} • Rol: {}
                    </p>
                </div>
            </div>
        </div>
    """.format(
        st.session_state.user_data.get('nombre', 'Usuario'),
        datetime.now().strftime('%d/%m/%Y'),
        st.session_state.user_data.get('rol', 'Usuario')
    ), unsafe_allow_html=True)

    # ==================== KPI CARDS ====================
    st.markdown("### 📊 Indicadores")
    
    # Obtener datos para los KPIs
    fecha_hoy = date.today().isoformat()
    tasa = get_tasa_cambio(fecha_hoy)
    balance_hoy = get_balance_diario(fecha_hoy)
    
    # Ventas del día
    ventas_hoy = get_ventas(fecha_hoy, fecha_hoy)
    total_ventas_bs = sum(v.get('total_bs', v.get('total', 0)) for v in ventas_hoy)
    total_ventas_usd = total_ventas_bs / tasa if tasa > 0 else 0
    
    # Productos en inventario
    productos = get_productos()
    total_productos = len(productos)
    
    # Compras del día
    compras_hoy = get_compras(fecha_hoy, fecha_hoy)
    total_compras_bs = sum(c.get('total_bs', c.get('total', 0)) for c in compras_hoy)
    total_compras_usd = total_compras_bs / tasa if tasa > 0 else 0
    
    # Balance del día
    balance_bs = balance_hoy.get('balance_final_bs', 0) if balance_hoy else 0
    balance_usd = balance_hoy.get('balance_final_usd', 0) if balance_hoy else 0
    
    # Usuarios activos (simulado)
    usuarios_activos = 1
    
    # KPIs en tarjetas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid #8B4513; text-align: center;">
                <p style="color: #666; font-size: 0.8rem; margin: 0;">Balance del Día</p>
                <p style="color: #2C1810; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    Bs. {balance_bs:,.0f}
                </p>
                <p style="color: #8B4513; font-size: 0.8rem; margin: 0;">
                    ${balance_usd:,.2f}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid #D2691E; text-align: center;">
                <p style="color: #666; font-size: 0.8rem; margin: 0;">Ventas Hoy</p>
                <p style="color: #2C1810; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    Bs. {total_ventas_bs:,.0f}
                </p>
                <p style="color: #D2691E; font-size: 0.8rem; margin: 0;">
                    ${total_ventas_usd:,.2f}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid #F5DEB3; text-align: center;">
                <p style="color: #666; font-size: 0.8rem; margin: 0;">Compras Hoy</p>
                <p style="color: #2C1810; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    Bs. {total_compras_bs:,.0f}
                </p>
                <p style="color: #D2691E; font-size: 0.8rem; margin: 0;">
                    ${total_compras_usd:,.2f}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid #2C1810; text-align: center;">
                <p style="color: #666; font-size: 0.8rem; margin: 0;">Productos</p>
                <p style="color: #2C1810; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    {total_productos}
                </p>
                <p style="color: #666; font-size: 0.8rem; margin: 0;">
                    en inventario
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid #8B4513; text-align: center;">
                <p style="color: #666; font-size: 0.8rem; margin: 0;">Usuarios</p>
                <p style="color: #2C1810; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    {usuarios_activos}
                </p>
                <p style="color: #666; font-size: 0.8rem; margin: 0;">
                    activos hoy
                </p>
            </div>
        """, unsafe_allow_html=True)

    # ==================== ACCESO RÁPIDO ====================
    st.markdown("---")
    st.markdown("### 🚀 Acceso Rápido")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📦 Registrar Venta", use_container_width=True):
            st.session_state['selected_page'] = "Ventas"
            st.rerun()
    
    with col2:
        if st.button("📝 Registrar Compra", use_container_width=True):
            st.session_state['selected_page'] = "Compras"
            st.rerun()
    
    with col3:
        if st.button("📊 Ver Balance", use_container_width=True):
            st.session_state['selected_page'] = "Balance Diario"
            st.rerun()
    
    with col4:
        if st.button("📦 Gestionar Inventario", use_container_width=True):
            st.session_state['selected_page'] = "Inventario"
            st.rerun()

    # ==================== GRÁFICOS ====================
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Ventas Últimos 7 Días")
        
        # Datos de ventas semanales
        fechas = [(date.today() - timedelta(days=i)).isoformat() for i in range(7, 0, -1)]
        ventas_semana = []
        
        for fecha in fechas:
            ventas = get_ventas(fecha, fecha)
            total = sum(v.get('total_bs', v.get('total', 0)) for v in ventas)
            ventas_semana.append({
                'fecha': datetime.fromisoformat(fecha).strftime('%d/%m'),
                'ventas_bs': total,
                'ventas_usd': total / tasa if tasa > 0 else 0
            })
        
        if ventas_semana and any(v['ventas_bs'] > 0 for v in ventas_semana):
            df = pd.DataFrame(ventas_semana)
            fig = px.bar(df, x='fecha', y='ventas_usd',
                        title='Ventas en USD',
                        color_discrete_sequence=['#8B4513'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2C1810',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay ventas registradas en los últimos 7 días")
    
    with col2:
        st.markdown("#### 💰 Balance Diario (Últimos 30 días)")
        
        # Datos de balance mensual
        balances = []
        for i in range(30, 0, -1):
            fecha = (date.today() - timedelta(days=i)).isoformat()
            balance = get_balance_diario(fecha)
            if balance:
                balances.append({
                    'fecha': datetime.fromisoformat(fecha).strftime('%d/%m'),
                    'balance_usd': balance.get('balance_final_usd', 0)
                })
        
        if balances:
            df = pd.DataFrame(balances)
            fig = px.line(df, x='fecha', y='balance_usd',
                         title='Evolución del Balance en USD',
                         color_discrete_sequence=['#D2691E'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2C1810',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay balances registrados en los últimos 30 días")

    # ==================== INFORMACIÓN ADICIONAL ====================
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style="background: #FFF8F0; padding: 1rem; border-radius: 10px; 
                        border: 1px solid #F5DEB3;">
                <p style="color: #2C1810; font-weight: bold; margin: 0;">💱 Tasa de Cambio</p>
                <p style="color: #8B4513; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    {tasa:,.2f} Bs/$
                </p>
                <p style="color: #666; font-size: 0.8rem; margin: 0;">
                    Actualizada: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background: #FFF8F0; padding: 1rem; border-radius: 10px; 
                        border: 1px solid #F5DEB3;">
                <p style="color: #2C1810; font-weight: bold; margin: 0;">📦 Inventario</p>
                <p style="color: #8B4513; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    {total_productos}
                </p>
                <p style="color: #666; font-size: 0.8rem; margin: 0;">
                    productos registrados
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Ventas del mes
        inicio_mes = date.today().replace(day=1).isoformat()
        ventas_mes = get_ventas(inicio_mes, fecha_hoy)
        total_mes_bs = sum(v.get('total_bs', v.get('total', 0)) for v in ventas_mes)
        total_mes_usd = total_mes_bs / tasa if tasa > 0 else 0
        
        st.markdown(f"""
            <div style="background: #FFF8F0; padding: 1rem; border-radius: 10px; 
                        border: 1px solid #F5DEB3;">
                <p style="color: #2C1810; font-weight: bold; margin: 0;">📊 Ventas del Mes</p>
                <p style="color: #8B4513; font-size: 1.5rem; font-weight: bold; margin: 5px 0;">
                    Bs. {total_mes_bs:,.0f}
                </p>
                <p style="color: #666; font-size: 0.8rem; margin: 0;">
                    ${total_mes_usd:,.2f} • {len(ventas_mes)} transacciones
                </p>
            </div>
        """, unsafe_allow_html=True)

    # ==================== ACTIVIDAD RECIENTE ====================
    st.markdown("---")
    st.markdown("### 📋 Actividad Reciente")
    
    # Obtener últimas 5 transacciones
    if balance_hoy:
        transacciones = balance_hoy.get('transacciones', [])[-5:]
        if transacciones:
            df_trans = pd.DataFrame(transacciones)
            df_trans['fecha'] = pd.to_datetime(df_trans['fecha']).dt.strftime('%d/%m/%Y')
            df_trans['monto'] = df_trans.apply(
                lambda x: f"Bs. {x['monto_bs']:,.2f} (${x['monto_usd']:,.2f})", 
                axis=1
            )
            df_trans['tipo_icon'] = df_trans['tipo'].apply(
                lambda x: '⬆️' if x == 'ingreso' else '⬇️'
            )
            
            st.dataframe(
                df_trans[['fecha', 'tipo_icon', 'descripcion', 'categoria', 'monto']],
                column_config={
                    "fecha": "Fecha",
                    "tipo_icon": "",
                    "descripcion": "Descripción",
                    "categoria": "Categoría",
                    "monto": "Monto"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay transacciones recientes")
    else:
        st.info("No hay balance registrado para hoy")
