import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.database import guardar_venta, get_ventas, get_tasa_cambio, convertir_moneda
import plotly.express as px

def show():
    st.write("✅ Página de Ventas cargada correctamente")
    st.markdown("""
        <div class="main-header">
            <h1>💰 Gestión de Ventas</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Pestañas
    tab1, tab2 = st.tabs(["📊 Registro de Ventas", "➕ Nueva Venta"])
    
    tasa_actual = get_tasa_cambio()
    
    with tab1:
        mostrar_ventas(tasa=tasa_actual)
    
    with tab2:
        nueva_venta(tasa=tasa_actual)

def mostrar_ventas(tasa):
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - pd.Timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    with col3:
        metodo_pago = st.selectbox(
            "Método de Pago",
            options=['Todos', 'Efectivo', 'Transferencia', 'Pago Móvil', 'Tarjeta']
        )
    
    ventas = get_ventas(
        fecha_inicio=fecha_inicio.isoformat() if fecha_inicio else None,
        fecha_fin=fecha_fin.isoformat() if fecha_fin else None
    )
    
    # Filtrar por método de pago
    if metodo_pago != 'Todos':
        ventas = [v for v in ventas if v.get('metodo_pago') == metodo_pago]
    
    if not ventas:
        st.info("No hay ventas registradas en este período.")
        return
    
    # Resumen
    total_ventas = sum(v.get('total', 0) for v in ventas)
    total_usd = total_ventas / tasa if tasa > 0 else 0
    num_ventas = len(ventas)
    
    # Calcular IVA (asumiendo 16%)
    iva_total = sum(v.get('total', 0) * 0.16 for v in ventas)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ventas (Bs.)", f"{total_ventas:,.2f}")
    with col2:
        st.metric("Total Ventas ($)", f"{total_usd:,.2f}")
    with col3:
        st.metric("Número de Ventas", num_ventas)
    with col4:
        st.metric("IVA Total (16%)", f"{iva_total:,.2f}")
    
    # Detalle de ventas
    df = pd.DataFrame(ventas)
    if not df.empty:
        # Seleccionar columnas
        display_cols = ['fecha', 'cliente', 'productos', 'metodo_pago', 'total', 'tasa_cambio']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            
            # Agregar columnas
            df_display['total_usd'] = df_display.apply(
                lambda row: row['total'] / row['tasa_cambio'] if row['tasa_cambio'] > 0 else 0,
                axis=1
            )
            df_display['iva'] = df_display['total'] * 0.16
            
            # Formatear
            df_display['total'] = df_display['total'].apply(lambda x: f"{x:,.2f}")
            df_display['total_usd'] = df_display['total_usd'].apply(lambda x: f"{x:,.2f}")
            df_display['iva'] = df_display['iva'].apply(lambda x: f"{x:,.2f}")
            df_display['tasa_cambio'] = df_display['tasa_cambio'].apply(lambda x: f"{x:,.2f}")
            
            # Formatear productos para mostrar
            df_display['productos'] = df_display['productos'].apply(
                lambda x: ', '.join([f"{p.get('nombre', '')} (x{p.get('cantidad', 0)})" for p in x]) if isinstance(x, list) else str(x)
            )
            
            st.dataframe(
                df_display,
                column_config={
                    "fecha": "Fecha",
                    "cliente": "Cliente",
                    "productos": "Productos",
                    "metodo_pago": "Método de Pago",
                    "total": "Total (Bs.)",
                    "total_usd": "Total ($)",
                    "iva": "IVA (16%)",
                    "tasa_cambio": "Tasa"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Gráficos
            col1, col2 = st.columns(2)
            with col1:
                # Ventas por método de pago
                df_pago = df.groupby('metodo_pago')['total'].sum().reset_index()
                fig = px.pie(df_pago, values='total', names='metodo_pago',
                             title='Ventas por Método de Pago',
                             color_discrete_sequence=['#8B4513', '#D2691E', '#F5DEB3', '#2C1810'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Ventas diarias
                df_dia = df.groupby('fecha')['total'].sum().reset_index()
                fig = px.line(df_dia, x='fecha', y='total',
                              title='Tendencia de Ventas',
                              color_discrete_sequence=['#8B4513'])
                fig.update_layout(
                    xaxis_title="Fecha",
                    yaxis_title="Total (Bs.)"
                )
                st.plotly_chart(fig, use_container_width=True)

def nueva_venta(tasa):
    st.subheader("Registrar Nueva Venta")
    
    st.info(f"💱 Tasa de cambio actual: {tasa:,.2f} Bs/$")
    
    with st.form("nueva_venta"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Cliente (opcional)")
            metodo_pago = st.selectbox(
                "Método de Pago*",
                options=['Efectivo', 'Transferencia', 'Pago Móvil', 'Tarjeta']
            )
        with col2:
            tipo_venta = st.selectbox(
                "Tipo de Venta",
                options=['Normal', 'Mayorista', 'Especial']
            )
        
        # Productos
        st.subheader("Productos Vendidos")
        num_productos = st.number_input("Número de productos", min_value=1, max_value=20, value=1)
        
        productos = []
        for i in range(num_productos):
            with st.container():
                st.markdown(f"**Producto {i+1}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    nombre = st.text_input(f"Nombre", key=f"venta_prod_{i}")
                with col2:
                    cantidad = st.number_input(f"Cantidad", min_value=0.0, step=1.0, key=f"venta_cant_{i}")
                with col3:
                    precio = st.number_input(f"Precio Unitario", min_value=0.0, step=100.0, key=f"venta_precio_{i}")
                
                if nombre and cantidad > 0 and precio > 0:
                    productos.append({
                        'nombre': nombre,
                        'cantidad': cantidad,
                        'precio_unitario': precio
                    })
        
        # Mostrar subtotal
        if productos:
            subtotal = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
            iva = subtotal * 0.16
            total = subtotal + iva
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Subtotal", f"Bs. {subtotal:,.2f}")
            with col2:
                st.metric("IVA (16%)", f"Bs. {iva:,.2f}")
            with col3:
                st.metric("Total", f"Bs. {total:,.2f}")
        
        observaciones = st.text_area("Observaciones")
        
        submitted = st.form_submit_button("Registrar Venta")
        
        if submitted:
            if not productos:
                st.error("Por favor agregue al menos un producto")
                return
            
            if not metodo_pago:
                st.error("Por favor seleccione un método de pago")
                return
            
            # Calcular totales
            subtotal = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
            iva = subtotal * 0.16
            total = subtotal + iva
            
            data = {
                'cliente': cliente or 'Cliente General',
                'metodo_pago': metodo_pago,
                'tipo_venta': tipo_venta,
                'productos': productos,
                'subtotal': subtotal,
                'iva': iva,
                'total': total,
                'observaciones': observaciones,
                'usuario_creacion': st.session_state.user_data.get('id', '')
            }
            
            resultado = guardar_venta(data)
            if resultado:
                st.success(f"✅ Venta registrada exitosamente")
                st.balloons()
                # Mostrar resumen
                st.info(f"""
                    **Resumen de Venta**
                    - Total: Bs. {total:,.2f} (${total/tasa:,.2f})
                    - IVA: Bs. {iva:,.2f}
                    - Método de Pago: {metodo_pago}
                """)
            else:
                st.error("❌ Error al registrar la venta")
