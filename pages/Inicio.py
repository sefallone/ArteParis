import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import (
    get_ventas, get_compras, get_tasa_cambio, convertir_moneda,
    get_productos, get_balance_diario
)

def show():
    st.markdown("""
        <div class="main-header">
            <h1>☕ Dashboard DELICAFE</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener tasa de cambio actual
    tasa_actual = get_tasa_cambio()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    # Ventas del día
    hoy = datetime.now().date().isoformat()
    ventas_hoy = get_ventas(fecha_inicio=hoy, fecha_fin=hoy)
    total_ventas_hoy = sum(v.get('total', 0) for v in ventas_hoy)
    total_ventas_usd = total_ventas_hoy / tasa_actual if tasa_actual > 0 else 0
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Ventas Hoy</div>
                <div class="metric-value">${total_ventas_usd:,.2f}</div>
                <div style="font-size:0.8rem; color:#666;">Bs. {total_ventas_hoy:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Compras del día
    compras_hoy = get_compras(fecha_inicio=hoy, fecha_fin=hoy)
    total_compras_hoy = sum(c.get('total', 0) for c in compras_hoy)
    total_compras_usd = total_compras_hoy / tasa_actual if tasa_actual > 0 else 0
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Compras Hoy</div>
                <div class="metric-value">${total_compras_usd:,.2f}</div>
                <div style="font-size:0.8rem; color:#666;">Bs. {total_compras_hoy:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Balance del día
    balance = get_balance_diario(hoy)
    if balance:
        balance_bs = balance.get('balance', 0)
        balance_usd = balance_bs / tasa_actual if tasa_actual > 0 else 0
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Balance del Día</div>
                    <div class="metric-value">${balance_usd:,.2f}</div>
                    <div style="font-size:0.8rem; color:#666;">Bs. {balance_bs:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Inventario
    productos = get_productos()
    total_inventario = sum(p.get('cantidad', 0) * p.get('precio_unitario', 0) for p in productos)
    total_inventario_usd = total_inventario / tasa_actual if tasa_actual > 0 else 0
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Valor Inventario</div>
                <div class="metric-value">${total_inventario_usd:,.2f}</div>
                <div style="font-size:0.8rem; color:#666;">{len(productos)} productos</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Ventas Últimos 7 Días")
        # Datos de ventas semanales
        fechas = [(datetime.now() - timedelta(days=i)).date().isoformat() for i in range(7, 0, -1)]
        ventas_semana = []
        
        for fecha in fechas:
            ventas_dia = get_ventas(fecha_inicio=fecha, fecha_fin=fecha)
            total_dia = sum(v.get('total', 0) for v in ventas_dia)
            ventas_semana.append({
                'fecha': fecha,
                'total_bs': total_dia,
                'total_usd': total_dia / tasa_actual if tasa_actual > 0 else 0
            })
        
        df_semana = pd.DataFrame(ventas_semana)
        
        if not df_semana.empty:
            fig = px.bar(df_semana, x='fecha', y='total_usd', 
                        title='Ventas en USD',
                        color_discrete_sequence=['#8B4513'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2C1810'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribución de Ventas por Método de Pago")
        # Datos de métodos de pago
        formas_pago = {}
        for venta in ventas_hoy:
            metodo = venta.get('metodo_pago', 'Otro')
            formas_pago[metodo] = formas_pago.get(metodo, 0) + venta.get('total', 0)
        
        if formas_pago:
            df_pagos = pd.DataFrame([
                {'Método': k, 'Monto USD': v / tasa_actual if tasa_actual > 0 else 0}
                for k, v in formas_pago.items()
            ])
            
            fig = px.pie(df_pagos, values='Monto USD', names='Método',
                        color_discrete_sequence=['#8B4513', '#D2691E', '#F5DEB3', '#2C1810'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2C1810'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Información adicional
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
            **💱 Tasa de Cambio Actual**
            
            {tasa_actual:,.2f} Bs / $
            
            *Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}*
        """)
    
    with col2:
        st.info(f"""
            **📦 Productos en Inventario**
            
            Total: {len(productos)}
            
            *Materia Prima: {len([p for p in productos if p.get('tipo') == 'materia_prima'])}*
            *Semi-terminado: {len([p for p in productos if p.get('tipo') == 'semi_terminado'])}*
            *Terminado: {len([p for p in productos if p.get('tipo') == 'terminado'])}*
        """)
    
    with col3:
        ventas_mes = get_ventas(
            fecha_inicio=(datetime.now().replace(day=1)).date().isoformat(),
            fecha_fin=hoy
        )
        total_mes = sum(v.get('total', 0) for v in ventas_mes)
        
        st.info(f"""
            **📊 Ventas del Mes**
            
            Total: ${total_mes / tasa_actual if tasa_actual > 0 else 0:,.2f}
            
            *Promedio diario: ${(total_mes / max(1, len(set(v.get('fecha', '') for v in ventas_mes)))) / tasa_actual if tasa_actual > 0 else 0:,.2f}*
            *Número de ventas: {len(ventas_mes)}*
        """)
