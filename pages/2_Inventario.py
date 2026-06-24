import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import get_productos, guardar_producto, get_tasa_cambio, convertir_moneda
import plotly.express as px

def show():
    st.markdown("""
        <div class="main-header">
            <h1>📦 Gestión de Inventario</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Pestañas para los tipos de inventario
    tab1, tab2, tab3 = st.tabs(["📦 Materia Prima", "🔄 Semi-terminado", "✅ Terminado"])
    
    tasa_actual = get_tasa_cambio()
    
    with tab1:
        st.subheader("Inventario de Materia Prima")
        mostrar_inventario(tipo='materia_prima', tasa=tasa_actual)
        agregar_producto_form(tipo='materia_prima')
    
    with tab2:
        st.subheader("Inventario de Productos Semi-terminados")
        mostrar_inventario(tipo='semi_terminado', tasa=tasa_actual)
        agregar_producto_form(tipo='semi_terminado')
    
    with tab3:
        st.subheader("Inventario de Productos Terminados")
        mostrar_inventario(tipo='terminado', tasa=tasa_actual)
        agregar_producto_form(tipo='terminado')

def mostrar_inventario(tipo, tasa):
    productos = get_productos(tipo=tipo)
    
    if not productos:
        st.info(f"No hay productos en este inventario.")
        return
    
    # Crear DataFrame para mostrar
    df = pd.DataFrame(productos)
    
    # Mostrar resumen
    total_cantidad = df['cantidad'].sum()
    total_valor = sum(p['cantidad'] * p.get('precio_unitario', 0) for p in productos)
    total_valor_usd = total_valor / tasa if tasa > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cantidad Total", total_cantidad)
    with col2:
        st.metric("Valor Total (Bs.)", f"{total_valor:,.2f}")
    with col3:
        st.metric("Valor Total ($)", f"{total_valor_usd:,.2f}")
    
    # Tabla de productos
    if not df.empty:
        # Seleccionar columnas para mostrar
        display_columns = ['nombre', 'cantidad', 'precio_unitario', 'fecha_actualizacion']
        df_display = df[display_columns].copy()
        
        # Agregar columna de valor
        df_display['valor_bs'] = df['cantidad'] * df['precio_unitario']
        df_display['valor_usd'] = df_display['valor_bs'] / tasa if tasa > 0 else 0
        
        # Formatear
        df_display['precio_unitario'] = df_display['precio_unitario'].apply(lambda x: f"{x:,.2f}")
        df_display['valor_bs'] = df_display['valor_bs'].apply(lambda x: f"{x:,.2f}")
        df_display['valor_usd'] = df_display['valor_usd'].apply(lambda x: f"{x:,.2f}")
        df_display['fecha_actualizacion'] = pd.to_datetime(df_display['fecha_actualizacion']).dt.strftime('%d/%m/%Y %H:%M')
        
        st.dataframe(
            df_display,
            column_config={
                "nombre": "Producto",
                "cantidad": "Cantidad",
                "precio_unitario": "Precio Unitario (Bs.)",
                "valor_bs": "Valor Total (Bs.)",
                "valor_usd": "Valor Total ($)",
                "fecha_actualizacion": "Última Actualización"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de distribución por valor
        if len(df) > 1:
            fig = px.pie(df, values='cantidad', names='nombre', 
                         title='Distribución por Cantidad',
                         color_discrete_sequence=['#8B4513', '#D2691E', '#F5DEB3'])
            st.plotly_chart(fig, use_container_width=True)

def agregar_producto_form(tipo):
    with st.expander("➕ Agregar Nuevo Producto"):
        with st.form(f"form_{tipo}"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Producto*")
                cantidad = st.number_input("Cantidad*", min_value=0.0, step=1.0)
            with col2:
                precio = st.number_input("Precio Unitario (Bs.)*", min_value=0.0, step=100.0)
                unidad = st.text_input("Unidad de Medida (ej: kg, l, unidad)")
            
            observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("Guardar Producto")
            
            if submitted:
                if not nombre or not cantidad or not precio:
                    st.error("Por favor complete todos los campos obligatorios (*)")
                else:
                    data = {
                        'nombre': nombre,
                        'tipo': tipo,
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'unidad': unidad or 'unidad',
                        'observaciones': observaciones,
                        'usuario_creacion': st.session_state.user_data.get('id', '')
                    }
                    
                    resultado = guardar_producto(data)
                    if resultado:
                        st.success(f"✅ Producto '{nombre}' agregado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar el producto")
