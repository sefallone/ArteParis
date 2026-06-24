# pages/Inicio.py - VERSIÓN COMPLETA CON FORMULARIOS VISIBLES
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px

# Importar funciones de la base de datos
from utils.database import (
    get_balance_diario,
    get_tasa_cambio,
    get_ventas,
    get_compras,
    get_productos,
    guardar_producto,
    guardar_venta,
    guardar_compra,
    guardar_tasa_cambio,
    guardar_balance_diario
)

def show():
    """Función principal que se ejecuta cuando se selecciona la página Inicio"""
    
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

    # ==================== TABS PRINCIPALES ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "📦 Inventario",
        "💰 Ventas",
        "🛒 Compras",
        "📋 Balance Diario"
    ])
    
    with tab1:
        mostrar_dashboard()
    
    with tab2:
        mostrar_inventario()
    
    with tab3:
        mostrar_ventas()
    
    with tab4:
        mostrar_compras()
    
    with tab5:
        mostrar_balance_diario()

# ==================== TAB 1: DASHBOARD ====================
def mostrar_dashboard():
    """Muestra el dashboard con KPIs y gráficos"""
    
    st.markdown("### 📊 Panel de Control")
    
    # Obtener datos
    fecha_hoy = date.today().isoformat()
    tasa = get_tasa_cambio(fecha_hoy)
    balance = get_balance_diario(fecha_hoy)
    ventas = get_ventas(fecha_hoy, fecha_hoy)
    compras = get_compras(fecha_hoy, fecha_hoy)
    productos = get_productos()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        balance_bs = balance.get('balance_final_bs', 0) if balance else 0
        st.metric(
            "Balance del Día",
            f"Bs. {balance_bs:,.2f}",
            delta=f"${balance_bs / tasa:,.2f}" if tasa > 0 else ""
        )
    
    with col2:
        total_ventas = sum(v.get('total', 0) for v in ventas)
        st.metric(
            "Ventas Hoy",
            f"Bs. {total_ventas:,.2f}",
            delta=f"${total_ventas / tasa:,.2f}" if tasa > 0 else ""
        )
    
    with col3:
        total_compras = sum(c.get('total', 0) for c in compras)
        st.metric(
            "Compras Hoy",
            f"Bs. {total_compras:,.2f}",
            delta=f"${total_compras / tasa:,.2f}" if tasa > 0 else ""
        )
    
    with col4:
        st.metric(
            "Productos",
            len(productos),
            delta=f"{len([p for p in productos if p.get('tipo') == 'materia_prima'])} MP"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Ventas Últimos 7 Días")
        try:
            fechas = [(date.today() - timedelta(days=i)).isoformat() for i in range(7, 0, -1)]
            datos = []
            for fecha in fechas:
                ventas_dia = get_ventas(fecha, fecha)
                total = sum(v.get('total', 0) for v in ventas_dia)
                datos.append({
                    'fecha': datetime.fromisoformat(fecha).strftime('%d/%m'),
                    'ventas': total / tasa if tasa > 0 else 0
                })
            
            if datos and any(d['ventas'] > 0 for d in datos):
                df = pd.DataFrame(datos)
                fig = px.bar(df, x='fecha', y='ventas',
                            title='Ventas en USD',
                            color_discrete_sequence=['#8B4513'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de ventas disponibles")
        except Exception as e:
            st.info("No hay datos suficientes para mostrar el gráfico")
    
    with col2:
        st.subheader("💱 Tasa de Cambio")
        st.metric(
            "Tasa Actual",
            f"{tasa:,.2f} Bs/$",
            delta="Actualizada hoy" if tasa > 0 else "No configurada"
        )
        
        # Información adicional
        st.info("""
            **💡 Consejo:**
            - Ve a la pestaña **Balance Diario** para configurar la tasa
            - Registra tus primeras ventas en la pestaña **Ventas**
            - Agrega productos en la pestaña **Inventario**
        """)

# ==================== TAB 2: INVENTARIO ====================
def mostrar_inventario():
    """Muestra el formulario y lista de inventario"""
    
    st.markdown("### 📦 Gestión de Inventario")
    
    # Formulario para agregar producto
    with st.expander("➕ Agregar Nuevo Producto", expanded=True):
        with st.form("form_agregar_producto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del Producto*")
                tipo = st.selectbox(
                    "Tipo de Inventario*",
                    options=['materia_prima', 'semi_terminado', 'terminado'],
                    format_func=lambda x: {
                        'materia_prima': '📦 Materia Prima',
                        'semi_terminado': '🔄 Semi-terminado',
                        'terminado': '✅ Terminado'
                    }[x]
                )
                cantidad = st.number_input("Cantidad*", min_value=0.0, step=1.0)
            
            with col2:
                precio = st.number_input("Precio Unitario (Bs.)*", min_value=0.0, step=100.0)
                unidad = st.text_input("Unidad de Medida", placeholder="ej: kg, l, unidad")
                observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("💾 Guardar Producto", use_container_width=True)
            
            if submitted:
                if not nombre or cantidad <= 0 or precio <= 0:
                    st.error("❌ Por favor complete todos los campos obligatorios (*)")
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
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar el producto")
    
    # Lista de productos
    st.markdown("### 📋 Productos Registrados")
    
    productos = get_productos()
    
    if productos:
        df = pd.DataFrame(productos)
        
        # Mostrar tabla
        display_cols = ['nombre', 'tipo', 'cantidad', 'precio_unitario', 'unidad']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            df_display['tipo'] = df_display['tipo'].apply(
                lambda x: {
                    'materia_prima': '📦 Materia Prima',
                    'semi_terminado': '🔄 Semi-terminado',
                    'terminado': '✅ Terminado'
                }.get(x, x)
            )
            
            st.dataframe(
                df_display,
                column_config={
                    "nombre": "Producto",
                    "tipo": "Tipo",
                    "cantidad": "Cantidad",
                    "precio_unitario": "Precio (Bs.)",
                    "unidad": "Unidad"
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📝 No hay productos registrados. Agrega tu primer producto usando el formulario de arriba.")

# ==================== TAB 3: VENTAS ====================
def mostrar_ventas():
    """Muestra el formulario y lista de ventas"""
    
    st.markdown("### 💰 Gestión de Ventas")
    
    tasa_actual = get_tasa_cambio()
    
    # Formulario para nueva venta
    with st.expander("➕ Registrar Nueva Venta", expanded=True):
        st.info(f"💱 Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
        
        with st.form("form_nueva_venta"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Cliente (opcional)")
                metodo_pago = st.selectbox(
                    "Método de Pago*",
                    options=['Efectivo', 'Transferencia', 'Pago Móvil', 'Tarjeta', 'Zelle']
                )
            
            with col2:
                tipo_venta = st.selectbox(
                    "Tipo de Venta",
                    options=['Normal', 'Mayorista', 'Especial']
                )
            
            # Productos
            st.subheader("🛒 Productos Vendidos")
            num_productos = st.number_input("Número de productos", min_value=1, max_value=10, value=1)
            
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
            
            submitted = st.form_submit_button("💾 Registrar Venta", use_container_width=True)
            
            if submitted:
                if not productos:
                    st.error("❌ Por favor agregue al menos un producto")
                    return
                
                if not metodo_pago:
                    st.error("❌ Por favor seleccione un método de pago")
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
                    st.rerun()
                else:
                    st.error("❌ Error al registrar la venta")
    
    # Lista de ventas
    st.markdown("### 📋 Ventas Registradas")
    
    fecha_hoy = date.today().isoformat()
    ventas = get_ventas(fecha_hoy, fecha_hoy)
    
    if ventas:
        df = pd.DataFrame(ventas)
        
        # Mostrar tabla simplificada
        display_cols = ['fecha', 'cliente', 'metodo_pago', 'total']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            df_display['total'] = df_display['total'].apply(lambda x: f"Bs. {x:,.2f}")
            
            st.dataframe(
                df_display,
                column_config={
                    "fecha": "Fecha",
                    "cliente": "Cliente",
                    "metodo_pago": "Método de Pago",
                    "total": "Total"
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📝 No hay ventas registradas hoy. Registra tu primera venta usando el formulario de arriba.")

# ==================== TAB 4: COMPRAS ====================
def mostrar_compras():
    """Muestra el formulario y lista de compras"""
    
    st.markdown("### 🛒 Gestión de Compras")
    
    tasa_actual = get_tasa_cambio()
    
    # Formulario para nueva compra
    with st.expander("➕ Generar Nueva Orden de Compra", expanded=True):
        st.info(f"💱 Tasa de cambio actual: {tasa_actual:,.2f} Bs/$")
        
        with st.form("form_nueva_compra"):
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
            
            # Productos
            st.subheader("📦 Productos")
            num_productos = st.number_input("Número de productos", min_value=1, max_value=10, value=1)
            
            productos = []
            for i in range(num_productos):
                with st.container():
                    st.markdown(f"**Producto {i+1}**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        nombre = st.text_input(f"Nombre", key=f"compra_nom_{i}")
                    with col2:
                        cantidad = st.number_input(f"Cantidad", min_value=0.0, step=1.0, key=f"compra_cant_{i}")
                    with col3:
                        precio = st.number_input(f"Precio Unitario", min_value=0.0, step=100.0, key=f"compra_precio_{i}")
                    with col4:
                        unidad = st.text_input(f"Unidad", key=f"compra_unid_{i}")
                    
                    if nombre and cantidad > 0 and precio > 0:
                        productos.append({
                            'nombre': nombre,
                            'cantidad': cantidad,
                            'precio_unitario': precio,
                            'unidad': unidad or 'unidad'
                        })
            
            observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("💾 Generar Orden de Compra", use_container_width=True)
            
            if submitted:
                if not proveedor or not numero_orden:
                    st.error("❌ Por favor complete los campos obligatorios")
                    return
                
                if not productos:
                    st.error("❌ Por favor agregue al menos un producto")
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
                    st.rerun()
                else:
                    st.error("❌ Error al generar la orden de compra")
    
    # Lista de compras
    st.markdown("### 📋 Compras Registradas")
    
    fecha_hoy = date.today().isoformat()
    compras = get_compras(fecha_hoy, fecha_hoy)
    
    if compras:
        df = pd.DataFrame(compras)
        
        # Mostrar tabla simplificada
        display_cols = ['numero_orden', 'proveedor', 'tipo_materia', 'total']
        if all(col in df.columns for col in display_cols):
            df_display = df[display_cols].copy()
            df_display['total'] = df_display['total'].apply(lambda x: f"Bs. {x:,.2f}")
            df_display['tipo_materia'] = df_display['tipo_materia'].apply(
                lambda x: {
                    'basica': '🥩 Básica',
                    'intermedia': '🧂 Intermedia',
                    'extra': '🧁 Extra'
                }.get(x, x)
            )
            
            st.dataframe(
                df_display,
                column_config={
                    "numero_orden": "N° Orden",
                    "proveedor": "Proveedor",
                    "tipo_materia": "Tipo",
                    "total": "Total"
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📝 No hay compras registradas. Genera tu primera orden de compra usando el formulario de arriba.")

# ==================== TAB 5: BALANCE DIARIO ====================
def mostrar_balance_diario():
    """Muestra el balance diario y configuración de tasa"""
    
    st.markdown("### 📋 Balance Diario")
    
    fecha_hoy = date.today().isoformat()
    tasa_actual = get_tasa_cambio(fecha_hoy)
    balance = get_balance_diario(fecha_hoy)
    
    # Configurar tasa de cambio
    with st.expander("💱 Configurar Tasa de Cambio", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            nueva_tasa = st.number_input(
                "Tasa de Cambio (Bs/$)",
                value=float(tasa_actual) if tasa_actual > 0 else 621.52,
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            if st.button("💾 Guardar Tasa", use_container_width=True):
                guardar_tasa_cambio(nueva_tasa, fecha_hoy)
                st.success(f"✅ Tasa guardada: {nueva_tasa:,.2f} Bs/$")
                st.rerun()
    
    # Iniciar balance del día
    if not balance:
        with st.expander("🚀 Iniciar Balance del Día", expanded=True):
            st.warning("⚠️ No hay balance iniciado para hoy")
            
            col1, col2 = st.columns(2)
            with col1:
                balance_inicial_bs = st.number_input(
                    "Balance Inicial en Bolívares (Bs)",
                    value=0.0,
                    step=10000.0,
                    format="%.2f"
                )
            
            with col2:
                if tasa_actual > 0:
                    equivalente_usd = balance_inicial_bs / tasa_actual
                    st.metric("Equivalente en Dólares", f"${equivalente_usd:,.2f}")
            
            if st.button("🚀 Iniciar Balance", use_container_width=True):
                balance_data = {
                    'fecha': fecha_hoy,
                    'tasa_cambio': tasa_actual,
                    'balance_inicial_bs': balance_inicial_bs,
                    'balance_inicial_usd': balance_inicial_bs / tasa_actual if tasa_actual > 0 else 0,
                    'transacciones': [],
                    'total_ingresos_bs': 0,
                    'total_egresos_bs': 0,
                    'total_ingresos_usd': 0,
                    'total_egresos_usd': 0,
                    'balance_final_bs': balance_inicial_bs,
                    'balance_final_usd': balance_inicial_bs / tasa_actual if tasa_actual > 0 else 0,
                    'detalle_monedas': {
                        'efectivo_bs': balance_inicial_bs,
                        'efectivo_usd': 0,
                        'banco_bs': 0,
                        'banco_usd': 0
                    },
                    'ajuste_cambiario_bs': 0,
                    'ajuste_cambiario_usd': 0,
                    'generado_por': st.session_state.user_data.get('nombre', 'Sistema'),
                    'fecha_generacion': datetime.now().isoformat()
                }
                
                guardar_balance_diario(balance_data)
                st.success("✅ Balance iniciado exitosamente")
                st.balloons()
                st.rerun()
    else:
        # Mostrar balance actual
        st.success(f"✅ Balance iniciado para hoy")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Balance Inicial",
                f"Bs. {balance.get('balance_inicial_bs', 0):,.2f}"
            )
        with col2:
            st.metric(
                "Ingresos",
                f"Bs. {balance.get('total_ingresos_bs', 0):,.2f}"
            )
        with col3:
            st.metric(
                "Balance Final",
                f"Bs. {balance.get('balance_final_bs', 0):,.2f}"
            )
        
        # Mostrar transacciones recientes
        transacciones = balance.get('transacciones', [])
        if transacciones:
            st.subheader("📋 Últimas Transacciones")
            df = pd.DataFrame(transacciones[-5:])
            st.dataframe(
                df[['fecha', 'descripcion', 'categoria', 'monto_bs']],
                column_config={
                    "fecha": "Fecha",
                    "descripcion": "Descripción",
                    "categoria": "Categoría",
                    "monto_bs": "Monto (Bs.)"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay transacciones registradas hoy")

# ==================== PUNTO DE ENTRADA ====================
# Esta función show() es la que se llama desde app.py
# Ya está definida al inicio del archivo
