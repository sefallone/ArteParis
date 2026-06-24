# pages/balance_diario.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
from utils.database import (
    get_balance_diario, guardar_balance_diario,
    get_tasa_cambio, guardar_tasa_cambio,
    get_ventas, get_compras
)
import uuid

# Categorías predefinidas
CATEGORIAS_GASTOS = {
    'Gastos Bancarios Operativos': ['Comisiones Bancos', 'Transferencias', 'Mantenimiento de Cuentas'],
    'Gastos Administrativos': ['Contabilidad', 'Alquiler', 'Impuestos Municipales', 'Impuestos Seniat', 'Seguros', 'Servicios Básicos'],
    'Gastos de Venta': ['Vasos', 'Envases', 'Servilletas', 'Publicidad', 'Marketing'],
    'Gastos de Nóminas': ['Sueldos', 'Bonos', 'Comisiones', 'Beneficios'],
    'Gastos de Mantenimiento': ['Mantenimiento Equipos', 'Reparaciones', 'Limpieza'],
    'Cuentas por Pagar': ['Proveedores', 'Servicios', 'Impuestos', 'Préstamos'],
    'Cuentas por Cobrar': ['Clientes', 'Deudores', 'Anticipos'],
    'Beneficios': ['Retiro de Beneficios', 'Distribución de Utilidades']
}

def show():
    st.markdown("""
        <div class="main-header">
            <h1>📋 Balance Diario - Libro Mayor</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ver Balance", "➕ Registrar Transacción", "⚙️ Configurar Categorías", "📈 Reportes"])
    
    with tab1:
        mostrar_balance()
    
    with tab2:
        registrar_transaccion()
    
    with tab3:
        configurar_categorias()
    
    with tab4:
        reportes_balance()

def mostrar_balance():
    """Muestra el balance diario en formato contable"""
    
    # Selector de fecha
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        fecha_seleccionada = st.date_input("Fecha del Balance", value=date.today())
    with col2:
        if st.button("🔄 Generar Balance del Día"):
            generar_balance_diario(fecha_seleccionada)
    with col3:
        if st.button("📋 Ver Balance"):
            st.rerun()
    
    fecha_str = fecha_seleccionada.isoformat()
    balance = get_balance_diario(fecha_str)
    tasa = get_tasa_cambio(fecha_str)
    
    # Configurar tasa del día
    with st.expander("💱 Configurar Tasa de Cambio del Día", expanded=not balance):
        col1, col2 = st.columns([3, 1])
        with col1:
            tasa_nueva = st.number_input("Tasa de Cambio (Bs/$)", value=float(tasa), step=0.01, format="%.2f")
        with col2:
            if st.button("Guardar Tasa", use_container_width=True):
                guardar_tasa_cambio(tasa_nueva, fecha_str)
                st.success(f"✅ Tasa guardada: {tasa_nueva:,.2f} Bs/$")
                st.rerun()
    
    if not balance:
        st.info(f"📝 No hay balance registrado para {fecha_seleccionada.strftime('%d/%m/%Y')}")
        return
    
    # Mostrar el balance en formato contable
    mostrar_libro_mayor(balance, tasa, fecha_seleccionada)

def mostrar_libro_mayor(balance, tasa, fecha):
    """Muestra el balance en formato de libro mayor"""
    
    # Cabecera del balance
    st.markdown(f"""
        <div style="background-color: #2C1810; color: #F5DEB3; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
            <h3 style="text-align: center; margin: 0;">📋 BALANCE DIARIO - {fecha.strftime('%d/%m/%Y')}</h3>
            <p style="text-align: center; margin: 0;">Tasa de Cambio: {tasa:,.2f} Bs/$</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Resumen de saldos
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Balance Inicial", f"${balance.get('balance_inicial', 0):,.2f}")
    with col2:
        total_ingresos = balance.get('total_ingresos', 0)
        st.metric("Total Ingresos", f"${total_ingresos:,.2f}", delta=f"Bs. {total_ingresos * tasa:,.2f}")
    with col3:
        total_egresos = balance.get('total_egresos', 0)
        st.metric("Total Egresos", f"${total_egresos:,.2f}", delta=f"Bs. {total_egresos * tasa:,.2f}")
    with col4:
        balance_final = balance.get('balance_final', 0)
        st.metric("Balance Final", f"${balance_final:,.2f}", delta=f"Bs. {balance_final * tasa:,.2f}")
    
    st.markdown("---")
    
    # Tabla del libro mayor
    transacciones = balance.get('transacciones', [])
    
    if not transacciones:
        st.info("No hay transacciones registradas para este día")
        return
    
    # Crear DataFrame para el libro mayor
    df = pd.DataFrame(transacciones)
    
    # Ordenar por categoría y fecha
    df = df.sort_values(['categoria', 'fecha'])
    
    # Mostrar el libro mayor
    st.subheader("📊 Libro Mayor")
    
    # Agrupar por categoría
    categorias = df['categoria'].unique()
    
    for categoria in categorias:
        df_categoria = df[df['categoria'] == categoria]
        
        with st.expander(f"📁 {categoria} (${df_categoria['monto_usd'].sum():,.2f})", expanded=True):
            
            # Mostrar como tabla
            display_df = df_categoria[['fecha', 'descripcion', 'detalle', 'monto_usd', 'debe', 'haber', 'saldo']].copy()
            display_df['fecha'] = pd.to_datetime(display_df['fecha']).dt.strftime('%d/%m/%Y')
            display_df['monto_usd'] = display_df['monto_usd'].apply(lambda x: f"${x:,.2f}")
            display_df['debe'] = display_df['debe'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
            display_df['haber'] = display_df['haber'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
            display_df['saldo'] = display_df['saldo'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                display_df,
                column_config={
                    "fecha": "Fecha",
                    "descripcion": "Descripción",
                    "detalle": "Detalle",
                    "monto_usd": "Monto $",
                    "debe": "DEBE $",
                    "haber": "HABER $",
                    "saldo": "SALDO $"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Mostrar subtotal de la categoría
            col1, col2, col3 = st.columns(3)
            total_categoria = df_categoria['monto_usd'].sum()
            debe_categoria = df_categoria['debe'].sum()
            haber_categoria = df_categoria['haber'].sum()
            
            with col1:
                st.metric("Total Categoría", f"${total_categoria:,.2f}")
            with col2:
                st.metric("Total Debe", f"${debe_categoria:,.2f}")
            with col3:
                st.metric("Total Haber", f"${haber_categoria:,.2f}")
    
    # Gráfico de distribución
    st.markdown("---")
    st.subheader("📊 Distribución de Ingresos y Egresos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ingresos por categoría
        ingresos_df = df[df['tipo'] == 'ingreso'].groupby('categoria')['monto_usd'].sum().reset_index()
        if not ingresos_df.empty:
            fig = px.pie(ingresos_df, values='monto_usd', names='categoria',
                         title='Distribución de Ingresos',
                         color_discrete_sequence=['#2ECC40', '#39CCCC', '#0074D9'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Egresos por categoría
        egresos_df = df[df['tipo'] == 'egreso'].groupby('categoria')['monto_usd'].sum().reset_index()
        if not egresos_df.empty:
            fig = px.pie(egresos_df, values='monto_usd', names='categoria',
                         title='Distribución de Egresos',
                         color_discrete_sequence=['#FF4136', '#FF851B', '#FFDC00'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Exportar a Excel", use_container_width=True):
            exportar_excel(df, fecha)
    with col2:
        if st.button("🔄 Cerrar Día", use_container_width=True):
            cerrar_dia(fecha, balance)
    with col3:
        if st.button("📋 Copiar Balance", use_container_width=True):
            st.info("Balance copiado al portapapeles")

def registrar_transaccion():
    """Registra una nueva transacción en el balance"""
    st.subheader("➕ Registrar Transacción")
    
    fecha = st.date_input("Fecha de la Transacción", value=date.today())
    tasa = get_tasa_cambio(fecha.isoformat())
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo = st.selectbox("Tipo de Transacción", ["ingreso", "egreso"])
        categoria = st.selectbox("Categoría", list(CATEGORIAS_GASTOS.keys()))
        
        # Subcategorías según categoría seleccionada
        subcategorias = CATEGORIAS_GASTOS.get(categoria, [])
        if subcategorias:
            subcategoria = st.selectbox("Subcategoría", subcategorias)
        else:
            subcategoria = st.text_input("Subcategoría")
            st.warning("Esta categoría no tiene subcategorías configuradas")
    
    with col2:
        descripcion = st.text_input("Descripción")
        detalle = st.text_area("Detalle (factura, proveedor, etc.)")
        monto_usd = st.number_input("Monto en $", min_value=0.01, step=0.01, format="%.2f")
        
        # Calcular en Bs
        monto_bs = monto_usd * tasa
        st.info(f"💱 Monto en Bs: {monto_bs:,.2f} (Tasa: {tasa:,.2f})")
    
    # Opciones adicionales
    with st.expander("📋 Opciones Avanzadas"):
        debe = st.number_input("DEBE $", min_value=0.0, step=0.01, format="%.2f")
        haber = st.number_input("HABER $", min_value=0.0, step=0.01, format="%.2f")
        saldo = st.number_input("SALDO $", min_value=0.0, step=0.01, format="%.2f")
    
    if st.button("💾 Guardar Transacción", use_container_width=True):
        if not descripcion:
            st.error("Por favor ingresa una descripción")
            return
        
        if monto_usd <= 0:
            st.error("El monto debe ser mayor a 0")
            return
        
        # Obtener balance actual
        balance_actual = get_balance_diario(fecha.isoformat())
        
        # Calcular saldos
        if balance_actual:
            transacciones = balance_actual.get('transacciones', [])
            ultimo_saldo = transacciones[-1].get('saldo', 0) if transacciones else balance_actual.get('balance_inicial', 0)
        else:
            ultimo_saldo = 0
        
        # Si es ingreso, se suma al saldo
        if tipo == 'ingreso':
            nuevo_saldo = ultimo_saldo + monto_usd
        else:
            nuevo_saldo = ultimo_saldo - monto_usd
        
        # Crear transacción
        transaccion = {
            'id': str(uuid.uuid4()),
            'fecha': fecha.isoformat(),
            'descripcion': descripcion,
            'categoria': categoria,
            'subcategoria': subcategoria if subcategoria else '',
            'detalle': detalle,
            'tipo': tipo,
            'monto_bs': monto_bs,
            'monto_usd': monto_usd,
            'debe': debe if debe > 0 else (monto_usd if tipo == 'ingreso' else 0),
            'haber': haber if haber > 0 else (monto_usd if tipo == 'egreso' else 0),
            'saldo': saldo if saldo > 0 else nuevo_saldo,
            'tasa': tasa,
            'usuario': st.session_state.user_data.get('nombre', '')
        }
        
        # Guardar en Firebase
        guardar_transaccion(fecha.isoformat(), transaccion)
        st.success(f"✅ Transacción registrada exitosamente")
        st.balloons()
        st.rerun()

def configurar_categorias():
    """Permite configurar las categorías de gastos"""
    st.subheader("⚙️ Configuración de Categorías")
    
    st.info("""
    📝 **Instrucciones:**
    - Agrega nuevas categorías de gastos
    - Configura las subcategorías para cada una
    - Las categorías se usan en el registro de transacciones
    """)
    
    # Mostrar categorías actuales
    st.markdown("### 📁 Categorías Actuales")
    
    for categoria, subcategorias in CATEGORIAS_GASTOS.items():
        with st.expander(f"📁 {categoria}"):
            st.write("**Subcategorías:**")
            for sub in subcategorias:
                st.write(f"- {sub}")
    
    # Agregar nueva categoría
    st.markdown("---")
    st.subheader("➕ Agregar Nueva Categoría")
    
    col1, col2 = st.columns(2)
    with col1:
        nueva_categoria = st.text_input("Nombre de la Categoría")
    with col2:
        nuevas_subcategorias = st.text_area("Subcategorías (una por línea)")
    
    if st.button("Agregar Categoría", use_container_width=True):
        if nueva_categoria:
            sub_list = [s.strip() for s in nuevas_subcategorias.split('\n') if s.strip()]
            CATEGORIAS_GASTOS[nueva_categoria] = sub_list
            st.success(f"✅ Categoría '{nueva_categoria}' agregada")
            # Guardar en Firebase
            guardar_categorias(CATEGORIAS_GASTOS)
            st.rerun()
        else:
            st.error("Por favor ingresa el nombre de la categoría")

def reportes_balance():
    """Muestra reportes del balance"""
    st.subheader("📈 Reportes y Análisis")
    
    # Selector de período
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    
    if st.button("Generar Reporte", use_container_width=True):
        # Obtener balances del período
        balances = obtener_balances_periodo(fecha_inicio, fecha_fin)
        
        if not balances:
            st.warning("No hay datos para este período")
            return
        
        # Mostrar resumen
        st.subheader("📊 Resumen del Período")
        
        # Calcular totales
        total_ingresos = sum(b.get('total_ingresos', 0) for b in balances)
        total_egresos = sum(b.get('total_egresos', 0) for b in balances)
        balance_total = total_ingresos - total_egresos
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Ingresos", f"${total_ingresos:,.2f}")
        with col2:
            st.metric("Total Egresos", f"${total_egresos:,.2f}")
        with col3:
            st.metric("Balance Total", f"${balance_total:,.2f}")
        with col4:
            st.metric("Días", len(balances))
        
        # Gráfico de evolución
        df_balance = pd.DataFrame(balances)
        df_balance['fecha'] = pd.to_datetime(df_balance['fecha'])
        df_balance = df_balance.sort_values('fecha')
        
        fig = px.line(df_balance, x='fecha', y='balance_final',
                      title='Evolución del Balance Diario',
                      color_discrete_sequence=['#8B4513'])
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Balance ($)"
        )
        st.plotly_chart(fig, use_container_width=True)

# Funciones auxiliares
def generar_balance_diario(fecha):
    """Genera el balance diario automáticamente desde ventas y compras"""
    fecha_str = fecha.isoformat()
    tasa = get_tasa_cambio(fecha_str)
    
    # Obtener ventas y compras del día
    ventas = get_ventas(fecha_str, fecha_str)
    compras = get_compras(fecha_str, fecha_str)
    
    # Obtener balance del día anterior
    fecha_anterior = (fecha - timedelta(days=1)).isoformat()
    balance_anterior = get_balance_diario(fecha_anterior)
    balance_inicial = balance_anterior.get('balance_final', 0) if balance_anterior else 0
    
    transacciones = []
    total_ingresos = 0
    total_egresos = 0
    
    # Agregar ventas como ingresos
    for venta in ventas:
        transaccion = {
            'id': str(uuid.uuid4()),
            'fecha': fecha_str,
            'descripcion': 'Venta',
            'categoria': 'Ventas',
            'subcategoria': venta.get('metodo_pago', 'General'),
            'detalle': venta.get('cliente', 'Cliente General'),
            'tipo': 'ingreso',
            'monto_bs': venta.get('total', 0),
            'monto_usd': venta.get('total', 0) / tasa if tasa > 0 else 0,
            'debe': venta.get('total', 0) / tasa if tasa > 0 else 0,
            'haber': 0,
            'saldo': 0,  # Se calculará después
            'tasa': tasa
        }
        transacciones.append(transaccion)
        total_ingresos += transaccion['monto_usd']
    
    # Agregar compras como egresos
    for compra in compras:
        transaccion = {
            'id': str(uuid.uuid4()),
            'fecha': fecha_str,
            'descripcion': 'Compra',
            'categoria': 'Cuentas por Pagar',
            'subcategoria': 'Proveedores',
            'detalle': compra.get('proveedor', 'Proveedor'),
            'tipo': 'egreso',
            'monto_bs': compra.get('total', 0),
            'monto_usd': compra.get('total', 0) / tasa if tasa > 0 else 0,
            'debe': 0,
            'haber': compra.get('total', 0) / tasa if tasa > 0 else 0,
            'saldo': 0,
            'tasa': tasa
        }
        transacciones.append(transaccion)
        total_egresos += transaccion['monto_usd']
    
    # Calcular saldos acumulados
    saldo_actual = balance_inicial
    for t in transacciones:
        if t['tipo'] == 'ingreso':
            saldo_actual += t['monto_usd']
        else:
            saldo_actual -= t['monto_usd']
        t['saldo'] = saldo_actual
    
    balance_final = balance_inicial + total_ingresos - total_egresos
    
    # Guardar balance
    data = {
        'fecha': fecha_str,
        'tasa_cambio': tasa,
        'balance_inicial': balance_inicial,
        'transacciones': transacciones,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance_final': balance_final,
        'generado_por': st.session_state.user_data.get('nombre', 'Sistema'),
        'fecha_generacion': datetime.now().isoformat()
    }
    
    guardar_balance_diario(data)
    st.success(f"✅ Balance generado para {fecha.strftime('%d/%m/%Y')}")
    st.balloons()

def guardar_transaccion(fecha, transaccion):
    """Guarda una transacción en el balance del día"""
    balance = get_balance_diario(fecha)
    
    if not balance:
        # Crear nuevo balance
        balance = {
            'fecha': fecha,
            'tasa_cambio': get_tasa_cambio(fecha),
            'balance_inicial': 0,
            'transacciones': [],
            'total_ingresos': 0,
            'total_egresos': 0,
            'balance_final': 0,
            'generado_por': st.session_state.user_data.get('nombre', ''),
            'fecha_generacion': datetime.now().isoformat()
        }
    
    # Agregar transacción
    balance['transacciones'].append(transaccion)
    
    # Recalcular totales
    balance['total_ingresos'] = sum(t['monto_usd'] for t in balance['transacciones'] if t['tipo'] == 'ingreso')
    balance['total_egresos'] = sum(t['monto_usd'] for t in balance['transacciones'] if t['tipo'] == 'egreso')
    balance['balance_final'] = balance['balance_inicial'] + balance['total_ingresos'] - balance['total_egresos']
    
    # Guardar en Firebase
    guardar_balance_diario(balance)

def obtener_balances_periodo(fecha_inicio, fecha_fin):
    """Obtiene todos los balances en un período"""
    balances = []
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        balance = get_balance_diario(fecha_actual.isoformat())
        if balance:
            balances.append(balance)
        fecha_actual += timedelta(days=1)
    
    return balances

def exportar_excel(df, fecha):
    """Exporta el balance a Excel"""
    try:
        # Crear archivo Excel en memoria
        import io
        from openpyxl import Workbook
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Balance', index=False)
        
        # Descargar
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name=f"Balance_{fecha.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Error al exportar: {e}")

def cerrar_dia(fecha, balance):
    """Cierra el día y prepara el siguiente"""
    if st.warning(f"⚠️ ¿Estás seguro de cerrar el día {fecha.strftime('%d/%m/%Y')}?"):
        # Marcar el día como cerrado
        balance['cerrado'] = True
        balance['fecha_cierre'] = datetime.now().isoformat()
        guardar_balance_diario(balance)
        st.success("✅ Día cerrado exitosamente")
        st.balloons()

def guardar_categorias(categorias):
    """Guarda las categorías configuradas en Firebase"""
    db = get_db()
    try:
        db.collection('configuracion').document('categorias').set(categorias)
    except Exception as e:
        st.error(f"Error guardando categorías: {e}")

def cargar_categorias():
    """Carga las categorías desde Firebase"""
    global CATEGORIAS_GASTOS
    db = get_db()
    try:
        doc = db.collection('configuracion').document('categorias').get()
        if doc.exists:
            CATEGORIAS_GASTOS = doc.to_dict()
    except Exception as e:
        st.error(f"Error cargando categorías: {e}")
