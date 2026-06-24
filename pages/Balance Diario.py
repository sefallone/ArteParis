import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.database import (
    get_balance_diario, guardar_balance_diario,
    get_ventas, get_compras, get_tasa_cambio,
    convertir_moneda, get_productos
)
import plotly.express as px

def show():
    st.markdown("""
        <div class="main-header">
            <h1>📋 Balance Diario</h1>
        </div>
    """, unsafe_allow_html=True)
    
    tasa_actual = get_tasa_cambio()
    fecha_hoy = date.today().isoformat()
    
    # Mostrar balance del día actual
    balance_hoy = get_balance_diario(fecha_hoy)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"Balance del {date.today().strftime('%d/%m/%Y')}")
        
        if balance_hoy:
            mostrar_balance_resumen(balance_hoy, tasa_actual)
        else:
            st.info("No hay balance registrado para hoy. Genera uno nuevo.")
    
    with col2:
        st.subheader("⚙️ Acciones")
        if st.button("🔄 Generar Balance del Día", use_container_width=True):
            generar_balance_diario()
        
        # Seleccionar fecha para ver balance anterior
        fecha_antigua = st.date_input("Ver balance de:", value=date.today() - pd.Timedelta(days=1))
        if st.button("Ver Balance", use_container_width=True):
            balance_anterior = get_balance_diario(fecha_antigua.isoformat())
            if balance_anterior:
                st.session_state['balance_mostrar'] = balance_anterior
                st.session_state['fecha_mostrar'] = fecha_antigua.isoformat()
            else:
                st.warning("No hay balance para esa fecha")
    
    # Mostrar balance de fecha seleccionada
    if 'balance_mostrar' in st.session_state:
        st.markdown("---")
        st.subheader(f"Balance del {st.session_state['fecha_mostrar']}")
        mostrar_balance_resumen(st.session_state['balance_mostrar'], tasa_actual)

def mostrar_balance_resumen(balance, tasa):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Ingresos",
            f"Bs. {balance.get('ingresos', 0):,.2f}",
            delta=f"${balance.get('ingresos', 0) / tasa if tasa > 0 else 0:,.2f} USD"
        )
    with col2:
        st.metric(
            "Egresos",
            f"Bs. {balance.get('egresos', 0):,.2f}",
            delta=f"${balance.get('egresos', 0) / tasa if tasa > 0 else 0:,.2f} USD"
        )
    with col3:
        balance_bs = balance.get('balance', 0)
        st.metric(
            "Balance",
            f"Bs. {balance_bs:,.2f}",
            delta=f"${balance_bs / tasa if tasa > 0 else 0:,.2f} USD"
        )
    with col4:
        st.metric(
            "Tasa de Cambio",
            f"Bs. {balance.get('tasa_cambio', tasa):,.2f}",
            delta=f"${1:.2f} USD"
        )
    
    # Detalles del balance
    st.subheader("📊 Detalle del Balance")
    
    # Crear tablas para ingresos y egresos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Ingresos**")
        if 'ingresos_detalle' in balance:
            df_ingresos = pd.DataFrame(balance['ingresos_detalle'])
            if not df_ingresos.empty:
                st.dataframe(df_ingresos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ingresos registrados")
    
    with col2:
        st.markdown("**Egresos**")
        if 'egresos_detalle' in balance:
            df_egresos = pd.DataFrame(balance['egresos_detalle'])
            if not df_egresos.empty:
                st.dataframe(df_egresos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay egresos registrados")
    
    # Gráficos
    if 'ingresos_detalle' in balance or 'egresos_detalle' in balance:
        st.subheader("📈 Distribución de Ingresos y Egresos")
        
        # Preparar datos para gráfico
        datos_grafico = []
        if 'ingresos_detalle' in balance:
            for item in balance['ingresos_detalle']:
                datos_grafico.append({
                    'Concepto': item.get('concepto', 'Ingreso'),
                    'Monto Bs.': item.get('monto', 0),
                    'Tipo': 'Ingreso'
                })
        if 'egresos_detalle' in balance:
            for item in balance['egresos_detalle']:
                datos_grafico.append({
                    'Concepto': item.get('concepto', 'Egreso'),
                    'Monto Bs.': item.get('monto', 0),
                    'Tipo': 'Egreso'
                })
        
        if datos_grafico:
            df_grafico = pd.DataFrame(datos_grafico)
            fig = px.bar(df_grafico, x='Concepto', y='Monto Bs.', color='Tipo',
                         title='Distribución de Ingresos y Egresos',
                         color_discrete_sequence=['#2ECC40', '#FF4136'])
            st.plotly_chart(fig, use_container_width=True)

def generar_balance_diario():
    try:
        fecha_hoy = date.today().isoformat()
        tasa = get_tasa_cambio()
        
        # Obtener datos del día
        ventas_hoy = get_ventas(fecha_inicio=fecha_hoy, fecha_fin=fecha_hoy)
        compras_hoy = get_compras(fecha_inicio=fecha_hoy, fecha_fin=fecha_hoy)
        
        # Calcular ingresos (ventas)
        ingresos_total = sum(v.get('total', 0) for v in ventas_hoy)
        ingresos_detalle = [
            {
                'concepto': f"Venta - {v.get('cliente', 'General')}",
                'monto': v.get('total', 0),
                'metodo_pago': v.get('metodo_pago', '')
            }
            for v in ventas_hoy
        ]
        
        # Calcular egresos (compras)
        egresos_total = sum(c.get('total', 0) for c in compras_hoy)
        egresos_detalle = [
            {
                'concepto': f"Compra - {c.get('proveedor', '')}",
                'monto': c.get('total', 0),
                'tipo_materia': c.get('tipo_materia', '')
            }
            for c in compras_hoy
        ]
        
        # Calcular balance
        balance = ingresos_total - egresos_total
        
        # Guardar balance
        data = {
            'fecha': fecha_hoy,
            'tasa_cambio': tasa,
            'ingresos': ingresos_total,
            'egresos': egresos_total,
            'balance': balance,
            'ingresos_detalle': ingresos_detalle,
            'egresos_detalle': egresos_detalle,
            'generado_por': st.session_state.user_data.get('id', ''),
            'observaciones': f"Balance generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        }
        
        resultado = guardar_balance_diario(data)
        if resultado:
            st.success("✅ Balance del día generado exitosamente")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Error al generar el balance")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
