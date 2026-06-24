import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.database import guardar_compra, get_compras, get_tasa_cambio, convertir_moneda
import plotly.express as px

def show():
    st.markdown("""
        <div class="main-header">
            <h1>🛒 Gestión de Compras</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Pestañas para tipos de materia prima
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Todas", "🥩 Básica", "🧂 Intermedia", "🧁 Extra"])
    
    tasa_actual = get_tasa_cambio()
    
    with tab1:
        mostrar_compras(tipo=None, tasa=tasa_actual)
    with tab2:
        mostrar_compras(tipo='basica', tasa=tasa_actual)
    with tab3:
        mostrar_compras(tipo='intermedia', tasa=tasa_actual)
    with tab4:
        mostrar_compras(tipo='extra', tasa=tasa_actual)
    
    # Formulario para nueva compra
    st.markdown("---")
    with st.expander("➕ Generar Nueva Orden de Compra", expanded=False):
        generar_orden_compra()

def mostrar_compras(tipo, tasa):
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - pd.Timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    
    compras = get_compras(
        fecha_inicio=fecha_inicio.isoformat() if fecha_inicio else None,
        fecha_fin=fecha_fin.isoformat() if fecha_fin else None
    )
    
    # Filtrar por tipo
    if tipo:
        compras = [c for c in compras if c.get('tipo_materia') == tipo]
    
    if not compras:
        st.info("No hay compras registradas en este período.")
        return
    
    # Resumen
    total_compras = sum(c.get('total', 0) for c in compras)
    total_usd = total_compras / tasa if tasa > 0 else 0
    num_ordenes = len(set(c.get('numero_orden', '') for c in compras))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Órdenes", num_ordenes)
    with col2:
        st.metric("Total Compras (Bs.)", f"{total_compras:,.2f}")
    with col3:
        st.metric("Total Compras ($)", f"{total_usd:,.2f}")
    
    # Tabla de compras
    df = pd.DataFrame(compras)
    if not df.empty:
        # Seleccionar columnas
        display_cols = ['numero_orden', 'fecha', 'proveedor', 'tipo_materia', 'total', 'tasa_cambio']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            
            # Agregar columna USD
            df_display['total_usd'] = df_display.apply(
                lambda row: row['total'] / row['tasa_cambio'] if row['tasa_cambio'] > 0 else 0,
                axis=1
            )
            
            # Formatear
            df_display['total'] = df_display['total'].apply(lambda x: f"{x:,.2f}")
            df_display['total_usd'] = df_display['total_usd'].apply(lambda x: f"{x:,.2f}")
            df_display['tasa_cambio'] = df_display['tasa_cambio'].apply(lambda x: f"{x:,.2f}")
            
            st.dataframe(
                df_display,
                column_config={
                    "numero_orden": "N° Orden",
                    "fecha": "Fecha",
                    "proveedor": "Proveedor",
                    "tipo_materia": "Tipo de Materia",
                    "total": "Total (Bs.)",
                    "total_usd": "Total ($)",
                    "tasa_cambio": "Tasa de Cambio"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Gráficos
            col1, col2 = st.columns(2)
            with col1:
                # Compras por proveedor
                df_proveedor = df.groupby('proveedor')['total'].sum().reset_index()
                fig = px.pie(df_proveedor, values='total', names='proveedor',
                             title='Compras por Proveedor',
                             color_discrete_sequence=['#8B4513', '#D2691E', '#F5DEB3', '#2C1810'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Compras por tipo de materia
                df_tipo = df.groupby('tipo_materia')['total'].sum().reset_index()
                fig = px.bar(df_tipo, x='tipo_materia', y='total',
                             title='Compras por Tipo de Materia',
                             color_discrete_sequence=['#8B4513'])
                st.plotly_chart(fig, use_container_width=True)

def generar_orden_compra():
    st.subheader("Nueva Orden de Compra")
    
    tasa_actual = get_tasa_cambio()
    st.info(f"💱 Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
    
    with st.form("orden_compra"):
        col1, col2 = st.columns(2)
        with col1:
            proveedor = st.text_input("Proveedor*")
            tipo_materia = st.selectbox(
                "Tipo de Materia Prima*",
                options=['basica', 'intermedia', 'extra'],
                format_func=lambda x: {
                    'basica': '🥩 Básica',
                    'intermedia': '🧂 Intermedia',
                    'extra': '🧁 Extra'
                }[x]
            )
        with col2:
            numero_orden = st.text_input("Número de Orden*")
            fecha_entrega = st.date_input("Fecha de Entrega Estimada")
        
        # Productos en la orden
        st.subheader("Productos")
        num_productos = st.number_input("Número de productos", min_value=1, max_value=20, value=1)
        
        productos = []
        for i in range(num_productos):
            with st.container():
                st.markdown(f"**Producto {i+1}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    nombre = st.text_input(f"Nombre", key=f"prod_nom_{i}")
                with col2:
                    cantidad = st.number_input(f"Cantidad", min_value=0.0, step=1.0, key=f"prod_cant_{i}")
                with col3:
                    precio_unitario = st.number_input(f"Precio Unitario", min_value=0.0, step=100.0, key=f"prod_precio_{i}")
                with col4:
                    unidad = st.text_input(f"Unidad", key=f"prod_unid_{i}")
                
                if nombre and cantidad > 0 and precio_unitario > 0:
                    productos.append({
                        'nombre': nombre,
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario,
                        'unidad': unidad or 'unidad'
                    })
        
        observaciones = st.text_area("Observaciones")
        
        submitted = st.form_submit_button("Generar Orden de Compra")
        
        if submitted:
            if not proveedor or not numero_orden:
                st.error("Por favor complete los campos obligatorios")
                return
            
            if not productos:
                st.error("Por favor agregue al menos un producto")
                return
            
            # Calcular total
            total = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
            
            data = {
                'numero_orden': numero_orden,
                'proveedor': proveedor,
                'tipo_materia': tipo_materia,
                'fecha_entrega': fecha_entrega.isoformat() if fecha_entrega else None,
                'productos': productos,
                'total': total,
                'observaciones': observaciones,
                'usuario_creacion': st.session_state.user_data.get('id', ''),
                'estado': 'pendiente'
            }
            
            resultado = guardar_compra(data)
            if resultado:
                st.success(f"✅ Orden de compra {numero_orden} generada exitosamente")
                st.balloons()
            else:
                st.error("❌ Error al generar la orden de compra")
