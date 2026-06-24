# pages/Balance_Diario.py - Versión corregida
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
from utils.database import (
    get_balance_diario, guardar_balance_diario,
    get_tasa_cambio, guardar_tasa_cambio,
    get_ventas, get_compras,
    clear_cache
)
import uuid

# Configuración inicial
MONEDA_BS = "Bs."
MONEDA_USD = "$"

# Categorías de transacciones
CATEGORIAS = {
    'Ventas': {
        'subcategorias': ['Venta Efectivo Bs', 'Venta Efectivo $', 'Venta Transferencia Bs', 'Venta Zelle $', 'Venta Punto de Venta'],
        'tipo': 'ingreso'
    },
    'Gastos Bancarios': {
        'subcategorias': ['Comisiones', 'Transferencias', 'Mantenimiento'],
        'tipo': 'egreso'
    },
    'Gastos Administrativos': {
        'subcategorias': ['Contabilidad', 'Alquiler', 'Impuestos Municipales', 'Impuestos SENIAT', 'Seguros'],
        'tipo': 'egreso'
    },
    'Gastos Operativos': {
        'subcategorias': ['Insumos', 'Mantenimiento', 'Servicios Básicos', 'Vasos/Envases'],
        'tipo': 'egreso'
    },
    'Gastos de Nómina': {
        'subcategorias': ['Sueldos', 'Bonos', 'Comisiones', 'Beneficios'],
        'tipo': 'egreso'
    },
    'Cuentas por Pagar': {
        'subcategorias': ['Proveedores Bs', 'Proveedores $', 'Servicios Bs', 'Servicios $'],
        'tipo': 'egreso'
    },
    'Cuentas por Cobrar': {
        'subcategorias': ['Clientes Bs', 'Clientes $'],
        'tipo': 'ingreso'
    },
    'Ajustes Cambiarios': {
        'subcategorias': ['Ganancia Cambiaria', 'Pérdida Cambiaria'],
        'tipo': 'ajuste'
    }
}

def show():
    st.markdown("""
        <div class="main-header">
            <h1>📋 Balance Diario - Control Dual</h1>
            <p style="text-align: center; color: #F5DEB3; margin: 0;">
                Bolívares 💰 ↔ Dólares 💵 | Tasa de Cambio Diaria
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Balance del Día", 
        "➕ Registrar Transacción", 
        "💱 Configurar Tasa",
        "📈 Reportes"
    ])
    
    with tab1:
        mostrar_balance()
    
    with tab2:
        registrar_transaccion()
    
    with tab3:
        configurar_tasa()
    
    with tab4:
        reportes_balance()

def mostrar_balance():
    """Muestra el balance del día en ambas monedas"""
    
    # Selector de fecha
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        fecha_seleccionada = st.date_input("Fecha del Balance", value=date.today())
    with col2:
        if st.button("🔄 Generar Balance"):
            generar_balance_diario(fecha_seleccionada)
    with col3:
        if st.button("📋 Actualizar"):
            clear_cache()
            st.rerun()
    
    fecha_str = fecha_seleccionada.isoformat()
    balance = get_balance_diario(fecha_str)
    tasa = get_tasa_cambio(fecha_str)
    
    # Si no hay balance, mostrar estado inicial
    if not balance:
        st.info(f"📝 No hay balance para {fecha_seleccionada.strftime('%d/%m/%Y')}")
        
        # Botón para iniciar balance
        with st.expander("🚀 Iniciar Balance del Día", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                balance_inicial_bs = st.number_input("Balance Inicial en Bs", value=0.0, step=10000.0)
            with col2:
                if tasa > 0:
                    st.metric("Equivalente en $", f"${balance_inicial_bs / tasa:,.2f}")
            
            if st.button("Confirmar Inicio", use_container_width=True):
                nuevo_balance = crear_balance_inicial(fecha_str, tasa, balance_inicial_bs, balance_inicial_bs / tasa if tasa > 0 else 0)
                guardar_balance_diario(nuevo_balance)
                st.success("✅ Balance iniciado")
                clear_cache()
                st.rerun()
        return
    
    # Mostrar balance
    mostrar_resumen_dual(balance, tasa)
    mostrar_libro_mayor_dual(balance)

def mostrar_resumen_dual(balance, tasa):
    """Muestra el resumen en ambas monedas"""
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2C1810 0%, #4A2818 100%); 
                    color: #F5DEB3; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
            <h3 style="text-align: center; margin: 0;">
                📊 Balance del {datetime.fromisoformat(balance['fecha']).strftime('%d/%m/%Y')}
            </h3>
            <p style="text-align: center; margin: 5px 0;">
                Tasa de Cambio: <strong>{tasa:,.2f} Bs/$</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tarjetas de resumen en ambas monedas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Bolívares")
        col1a, col1b, col1c = st.columns(3)
        
        with col1a:
            st.metric(
                "Balance Inicial",
                f"Bs. {balance.get('balance_inicial_bs', 0):,.2f}"
            )
        with col1b:
            total_ingresos_bs = balance.get('total_ingresos_bs', 0)
            st.metric(
                "Ingresos",
                f"Bs. {total_ingresos_bs:,.2f}",
                delta=f"+{total_ingresos_bs:,.2f} Bs"
            )
        with col1c:
            total_egresos_bs = balance.get('total_egresos_bs', 0)
            st.metric(
                "Egresos",
                f"Bs. {total_egresos_bs:,.2f}",
                delta=f"-{total_egresos_bs:,.2f} Bs"
            )
        
        # Balance final en Bs
        balance_final_bs = balance.get('balance_final_bs', 0)
        st.metric(
            "**Balance Final**",
            f"Bs. {balance_final_bs:,.2f}",
            delta=f"${balance_final_bs / tasa:,.2f}" if tasa > 0 else "",
            delta_color="normal"
        )
    
    with col2:
        st.markdown("### 💵 Dólares")
        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            st.metric(
                "Balance Inicial",
                f"${balance.get('balance_inicial_usd', 0):,.2f}"
            )
        with col2b:
            total_ingresos_usd = balance.get('total_ingresos_usd', 0)
            st.metric(
                "Ingresos",
                f"${total_ingresos_usd:,.2f}",
                delta=f"+{total_ingresos_usd:,.2f} $"
            )
        with col2c:
            total_egresos_usd = balance.get('total_egresos_usd', 0)
            st.metric(
                "Egresos",
                f"${total_egresos_usd:,.2f}",
                delta=f"-{total_egresos_usd:,.2f} $"
            )
        
        # Balance final en USD
        balance_final_usd = balance.get('balance_final_usd', 0)
        st.metric(
            "**Balance Final**",
            f"${balance_final_usd:,.2f}",
            delta=f"Bs. {balance_final_usd * tasa:,.2f}" if tasa > 0 else "",
            delta_color="normal"
        )
    
    # Mostrar ajuste cambiario si existe
    ajuste = balance.get('ajuste_cambiario_usd', 0)
    if ajuste != 0:
        st.info(f"""
            💱 **Ajuste por Tasa de Cambio**
            
            El valor en dólares ha cambiado debido a la fluctuación del tipo de cambio.
            {f'Ganancia: ${abs(ajuste):,.2f}' if ajuste > 0 else f'Pérdida: ${abs(ajuste):,.2f}'}
        """)
    
    # Desglose por tipo de moneda
    with st.expander("📊 Desglose por Moneda", expanded=False):
        detalle = balance.get('detalle_monedas', {})
        
        if detalle:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**💰 Bolívares**")
                st.write(f"Efectivo Bs: {detalle.get('efectivo_bs', 0):,.2f}")
                st.write(f"Banco Bs: {detalle.get('banco_bs', 0):,.2f}")
            with col2:
                st.write("**💵 Dólares**")
                st.write(f"Efectivo $: {detalle.get('efectivo_usd', 0):,.2f}")
                st.write(f"Banco $: {detalle.get('banco_usd', 0):,.2f}")
            with col3:
                st.write("**📊 Totales**")
                total_bs = detalle.get('efectivo_bs', 0) + detalle.get('banco_bs', 0)
                total_usd = detalle.get('efectivo_usd', 0) + detalle.get('banco_usd', 0)
                st.write(f"Total Bs: {total_bs:,.2f}")
                st.write(f"Total $: {total_usd:,.2f}")
                st.write(f"Equivalente: ${total_bs / tasa:,.2f}" if tasa > 0 else "")

def mostrar_libro_mayor_dual(balance):
    """Muestra el libro mayor en formato dual - CORREGIDO"""
    
    st.markdown("---")
    st.subheader("📋 Libro Mayor (Dual)")
    
    transacciones = balance.get('transacciones', [])
    
    if not transacciones:
        st.info("No hay transacciones registradas")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(transacciones)
    
    # ✅ VERIFICAR Y COMPLETAR CAMPOS FALTANTES
    # Si no existe la columna 'moneda', crearla con valor por defecto
    if 'moneda' not in df.columns:
        df['moneda'] = 'Mixto'  # Valor por defecto
    
    # Asegurar que todas las columnas necesarias existan
    columnas_requeridas = ['fecha', 'descripcion', 'moneda', 'monto_bs', 'monto_usd', 'tasa_aplicada', 'saldo_bs', 'saldo_usd']
    for col in columnas_requeridas:
        if col not in df.columns:
            if col in ['monto_bs', 'saldo_bs']:
                df[col] = 0.0
            elif col in ['monto_usd', 'saldo_usd']:
                df[col] = 0.0
            elif col == 'tasa_aplicada':
                df[col] = balance.get('tasa_cambio', 621.52)
            else:
                df[col] = 'N/A'
    
    # Ordenar por categoría
    df = df.sort_values(['categoria', 'fecha'])
    
    # Agrupar por categoría
    categorias = df['categoria'].unique()
    
    for categoria in categorias:
        df_cat = df[df['categoria'] == categoria]
        
        # Calcular totales de la categoría
        total_bs = df_cat['monto_bs'].sum()
        total_usd = df_cat['monto_usd'].sum()
        
        with st.expander(f"📁 {categoria} (Bs. {total_bs:,.2f} | ${total_usd:,.2f})", expanded=True):
            
            # Mostrar tabla - usando solo columnas que existen
            columnas_display = ['fecha', 'descripcion', 'moneda', 'monto_bs', 'monto_usd', 'tasa_aplicada', 'saldo_bs', 'saldo_usd']
            columnas_existentes = [col for col in columnas_display if col in df_cat.columns]
            
            if columnas_existentes:
                display_df = df_cat[columnas_existentes].copy()
                display_df['fecha'] = pd.to_datetime(display_df['fecha']).dt.strftime('%d/%m/%Y')
                
                # Formatear
                for col in ['monto_bs', 'saldo_bs']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"Bs. {x:,.2f}" if pd.notna(x) else "Bs. 0.00")
                
                for col in ['monto_usd', 'saldo_usd']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
                
                if 'tasa_aplicada' in display_df.columns:
                    display_df['tasa_aplicada'] = display_df['tasa_aplicada'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "0.00")
                
                if 'moneda' in display_df.columns:
                    display_df['moneda'] = display_df['moneda'].fillna('Mixto')
                
                st.dataframe(
                    display_df,
                    column_config={
                        "fecha": "Fecha",
                        "descripcion": "Descripción",
                        "moneda": "Moneda",
                        "monto_bs": "Monto Bs",
                        "monto_usd": "Monto $",
                        "tasa_aplicada": "Tasa",
                        "saldo_bs": "Saldo Bs",
                        "saldo_usd": "Saldo $"
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write("No hay datos para mostrar")

def registrar_transaccion():
    """Registra una transacción en ambas monedas"""
    
    st.subheader("➕ Registrar Transacción")
    
    # Tasa actual
    fecha = st.date_input("Fecha", value=date.today())
    tasa = get_tasa_cambio(fecha.isoformat())
    
    st.info(f"💱 Tasa de Cambio: {tasa:,.2f} Bs/$")
    
    with st.form("registrar_transaccion"):
        col1, col2 = st.columns(2)
        
        with col1:
            categoria = st.selectbox("Categoría", list(CATEGORIAS.keys()))
            subcategoria = st.selectbox("Subcategoría", CATEGORIAS[categoria]['subcategorias'])
            
            # Determinar tipo de moneda según la categoría
            moneda_opciones = ['Bolívares (Bs)', 'Dólares ($)', 'Mixto (Bs + $)']
            moneda = st.selectbox("Moneda de la Transacción", moneda_opciones)
        
        with col2:
            descripcion = st.text_input("Descripción")
            detalle = st.text_area("Detalle (factura, proveedor, etc.)")
        
        # Campos según moneda
        if moneda == 'Bolívares (Bs)':
            monto_bs = st.number_input("Monto en Bolívares (Bs)", min_value=0.01, step=100.0, format="%.2f")
            monto_usd = monto_bs / tasa if tasa > 0 else 0
            st.info(f"💵 Equivalente en $: {monto_usd:,.2f}")
            
        elif moneda == 'Dólares ($)':
            monto_usd = st.number_input("Monto en Dólares ($)", min_value=0.01, step=1.0, format="%.2f")
            monto_bs = monto_usd * tasa
            st.info(f"💰 Equivalente en Bs: {monto_bs:,.2f}")
            
        else:  # Mixto
            col1, col2 = st.columns(2)
            with col1:
                monto_bs = st.number_input("Parte en Bs", min_value=0.0, step=100.0, format="%.2f")
            with col2:
                monto_usd = st.number_input("Parte en $", min_value=0.0, step=1.0, format="%.2f")
            
            if monto_bs > 0 or monto_usd > 0:
                st.info(f"💱 Total: Bs. {monto_bs:,.2f} + ${monto_usd:,.2f} = Bs. {(monto_usd * tasa) + monto_bs:,.2f}")
        
        # Tipo de transacción
        tipo = CATEGORIAS[categoria]['tipo']
        if tipo == 'ingreso':
            st.success("💰 Esta es una transacción de INGRESO")
        elif tipo == 'egreso':
            st.error("💸 Esta es una transacción de EGRESO")
        else:
            st.warning("⚖️ Esta es una transacción de AJUSTE")
        
        # Botón de guardar
        submitted = st.form_submit_button("💾 Guardar Transacción", use_container_width=True)
        
        if submitted:
            if not descripcion:
                st.error("Por favor ingresa una descripción")
                return
            
            if monto_bs == 0 and monto_usd == 0:
                st.error("El monto debe ser mayor a 0")
                return
            
            # Guardar transacción
            guardar_transaccion_dual(fecha, {
                'categoria': categoria,
                'subcategoria': subcategoria,
                'descripcion': descripcion,
                'detalle': detalle,
                'moneda': moneda,
                'monto_bs': monto_bs,
                'monto_usd': monto_usd,
                'tipo': tipo,
                'tasa_aplicada': tasa
            })
            
            st.success("✅ Transacción registrada exitosamente")
            st.balloons()
            clear_cache()
            st.rerun()

def configurar_tasa():
    """Configura la tasa de cambio del día"""
    
    st.subheader("💱 Configuración de Tasa de Cambio")
    
    fecha = st.date_input("Fecha", value=date.today())
    fecha_str = fecha.isoformat()
    tasa_actual = get_tasa_cambio(fecha_str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Tasa Actual", f"{tasa_actual:,.2f} Bs/$")
        
        nueva_tasa = st.number_input(
            "Nueva Tasa de Cambio",
            value=float(tasa_actual),
            min_value=0.01,
            step=0.01,
            format="%.2f"
        )
        
        if st.button("💾 Guardar Tasa", use_container_width=True):
            guardar_tasa_cambio(nueva_tasa, fecha_str)
            st.success(f"✅ Tasa guardada: {nueva_tasa:,.2f} Bs/$")
            
            # Registrar ajuste cambiario
            registrar_ajuste_cambiario(fecha_str, nueva_tasa)
            clear_cache()
            st.rerun()
    
    with col2:
        st.info("""
            📝 **Historial de Tasas**
            
            Puedes ver el historial de tasas de cambio en la sección de Reportes.
        """)
        
        # Mostrar historial rápido
        if st.button("📊 Ver Historial"):
            mostrar_historial_tasas()

def guardar_transaccion_dual(fecha, transaccion_data):
    """Guarda una transacción en el balance del día"""
    
    fecha_str = fecha.isoformat()
    balance = get_balance_diario(fecha_str)
    
    # Obtener balance del día anterior para continuidad
    if not balance:
        fecha_anterior = (fecha - timedelta(days=1)).isoformat()
        balance_anterior = get_balance_diario(fecha_anterior)
        
        balance = {
            'fecha': fecha_str,
            'tasa_cambio': get_tasa_cambio(fecha_str),
            'balance_inicial_bs': balance_anterior.get('balance_final_bs', 0) if balance_anterior else 0,
            'balance_inicial_usd': balance_anterior.get('balance_final_usd', 0) if balance_anterior else 0,
            'transacciones': [],
            'total_ingresos_bs': 0,
            'total_egresos_bs': 0,
            'total_ingresos_usd': 0,
            'total_egresos_usd': 0,
            'balance_final_bs': 0,
            'balance_final_usd': 0,
            'detalle_monedas': {
                'efectivo_bs': 0,
                'efectivo_usd': 0,
                'banco_bs': 0,
                'banco_usd': 0
            },
            'ajuste_cambiario_bs': 0,
            'ajuste_cambiario_usd': 0
        }
    
    # Calcular saldos actuales
    transacciones = balance.get('transacciones', [])
    ultimo_saldo_bs = transacciones[-1].get('saldo_bs', balance.get('balance_inicial_bs', 0)) if transacciones else balance.get('balance_inicial_bs', 0)
    ultimo_saldo_usd = transacciones[-1].get('saldo_usd', balance.get('balance_inicial_usd', 0)) if transacciones else balance.get('balance_inicial_usd', 0)
    
    # Crear transacción
    monto_bs = transaccion_data['monto_bs']
    monto_usd = transaccion_data['monto_usd']
    tipo = transaccion_data['tipo']
    
    # Actualizar saldos
    if tipo == 'ingreso':
        nuevo_saldo_bs = ultimo_saldo_bs + monto_bs
        nuevo_saldo_usd = ultimo_saldo_usd + monto_usd
    elif tipo == 'egreso':
        nuevo_saldo_bs = ultimo_saldo_bs - monto_bs
        nuevo_saldo_usd = ultimo_saldo_usd - monto_usd
    else:  # ajuste
        nuevo_saldo_bs = ultimo_saldo_bs + monto_bs
        nuevo_saldo_usd = ultimo_saldo_usd + monto_usd
    
    # ✅ Incluir el campo 'moneda' en la transacción
    transaccion = {
        'id': str(uuid.uuid4()),
        'fecha': fecha_str,
        'descripcion': transaccion_data['descripcion'],
        'detalle': transaccion_data.get('detalle', ''),
        'categoria': transaccion_data['categoria'],
        'subcategoria': transaccion_data['subcategoria'],
        'tipo': tipo,
        'moneda': transaccion_data['moneda'],  # ✅ Campo agregado
        'monto_bs': monto_bs,
        'monto_usd': monto_usd,
        'tasa_aplicada': transaccion_data['tasa_aplicada'],
        'saldo_bs': nuevo_saldo_bs,
        'saldo_usd': nuevo_saldo_usd,
        'usuario': st.session_state.user_data.get('nombre', 'Sistema'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Agregar transacción
    balance['transacciones'].append(transaccion)
    
    # Recalcular totales
    balance['total_ingresos_bs'] = sum(t['monto_bs'] for t in balance['transacciones'] if t['tipo'] == 'ingreso')
    balance['total_egresos_bs'] = sum(t['monto_bs'] for t in balance['transacciones'] if t['tipo'] == 'egreso')
    balance['total_ingresos_usd'] = sum(t['monto_usd'] for t in balance['transacciones'] if t['tipo'] == 'ingreso')
    balance['total_egresos_usd'] = sum(t['monto_usd'] for t in balance['transacciones'] if t['tipo'] == 'egreso')
    
    balance['balance_final_bs'] = balance['balance_inicial_bs'] + balance['total_ingresos_bs'] - balance['total_egresos_bs']
    balance['balance_final_usd'] = balance['balance_inicial_usd'] + balance['total_ingresos_usd'] - balance['total_egresos_usd']
    
    # Guardar en Firebase
    guardar_balance_diario(balance)

def registrar_ajuste_cambiario(fecha_str, nueva_tasa):
    """Registra el ajuste por cambio de tasa"""
    
    balance = get_balance_diario(fecha_str)
    
    if not balance:
        return
    
    tasa_anterior = balance.get('tasa_cambio', nueva_tasa)
    
    if tasa_anterior == nueva_tasa:
        return
    
    # Calcular ajuste en dólares
    balance_bs = balance.get('balance_final_bs', 0)
    nuevo_balance_usd = balance_bs / nueva_tasa if nueva_tasa > 0 else 0
    balance_usd_anterior = balance.get('balance_final_usd', 0)
    
    ajuste_usd = nuevo_balance_usd - balance_usd_anterior
    
    if ajuste_usd != 0:
        # Registrar ajuste como transacción
        transaccion_ajuste = {
            'categoria': 'Ajustes Cambiarios',
            'subcategoria': 'Ganancia Cambiaria' if ajuste_usd > 0 else 'Pérdida Cambiaria',
            'descripcion': f'Ajuste por tasa de cambio',
            'detalle': f'Tasa anterior: {tasa_anterior:.2f} → Nueva: {nueva_tasa:.2f}',
            'moneda': 'Ajuste',
            'monto_bs': ajuste_usd * nueva_tasa,
            'monto_usd': ajuste_usd,
            'tipo': 'ajuste',
            'tasa_aplicada': nueva_tasa
        }
        
        guardar_transaccion_dual(datetime.fromisoformat(fecha_str).date(), transaccion_ajuste)

def crear_balance_inicial(fecha_str, tasa, balance_bs, balance_usd):
    """Crea el balance inicial del día"""
    
    return {
        'fecha': fecha_str,
        'tasa_cambio': tasa,
        'balance_inicial_bs': balance_bs,
        'balance_inicial_usd': balance_usd,
        'transacciones': [],
        'total_ingresos_bs': 0,
        'total_egresos_bs': 0,
        'total_ingresos_usd': 0,
        'total_egresos_usd': 0,
        'balance_final_bs': balance_bs,
        'balance_final_usd': balance_usd,
        'detalle_monedas': {
            'efectivo_bs': balance_bs,
            'efectivo_usd': balance_usd,
            'banco_bs': 0,
            'banco_usd': 0
        },
        'ajuste_cambiario_bs': 0,
        'ajuste_cambiario_usd': 0,
        'generado_por': st.session_state.user_data.get('nombre', 'Sistema'),
        'fecha_generacion': datetime.now().isoformat()
    }

def generar_balance_diario(fecha):
    """Genera el balance diario automáticamente"""
    
    fecha_str = fecha.isoformat()
    tasa = get_tasa_cambio(fecha_str)
    
    # Obtener balance del día anterior
    fecha_anterior = (fecha - timedelta(days=1)).isoformat()
    balance_anterior = get_balance_diario(fecha_anterior)
    
    balance_inicial_bs = balance_anterior.get('balance_final_bs', 0) if balance_anterior else 0
    balance_inicial_usd = balance_anterior.get('balance_final_usd', 0) if balance_anterior else 0
    
    # Crear balance inicial
    balance = crear_balance_inicial(fecha_str, tasa, balance_inicial_bs, balance_inicial_usd)
    
    # Obtener ventas y compras del día
    ventas = get_ventas(fecha_str, fecha_str)
    compras = get_compras(fecha_str, fecha_str)
    
    # Procesar ventas
    for venta in ventas:
        transaccion = {
            'categoria': 'Ventas',
            'subcategoria': venta.get('metodo_pago', 'General'),
            'descripcion': 'Venta del día',
            'detalle': f"Cliente: {venta.get('cliente', 'General')}",
            'moneda': 'Mixto',
            'monto_bs': venta.get('total_bs', 0),
            'monto_usd': venta.get('total_usd', 0),
            'tipo': 'ingreso',
            'tasa_aplicada': tasa
        }
        guardar_transaccion_dual(fecha, transaccion)
    
    # Procesar compras
    for compra in compras:
        transaccion = {
            'categoria': 'Cuentas por Pagar',
            'subcategoria': 'Proveedores',
            'descripcion': 'Compra del día',
            'detalle': f"Proveedor: {compra.get('proveedor', 'General')}",
            'moneda': 'Mixto',
            'monto_bs': compra.get('total_bs', 0),
            'monto_usd': compra.get('total_usd', 0),
            'tipo': 'egreso',
            'tasa_aplicada': tasa
        }
        guardar_transaccion_dual(fecha, transaccion)
    
    st.success(f"✅ Balance generado para {fecha.strftime('%d/%m/%Y')}")
    st.balloons()
    clear_cache()
    st.rerun()

def reportes_balance():
    """Muestra reportes y análisis"""
    
    st.subheader("📈 Reportes y Análisis")
    
    # Selector de período
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    
    if st.button("📊 Generar Reporte", use_container_width=True):
        # Obtener balances del período
        balances = obtener_balances_periodo(fecha_inicio, fecha_fin)
        
        if not balances:
            st.warning("No hay datos para este período")
            return
        
        # Crear DataFrame
        df = pd.DataFrame(balances)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Mostrar evolución
        st.subheader("📊 Evolución del Balance")
        
        # Gráfico en Bolívares
        fig_bs = px.line(df, x='fecha', y='balance_final_bs',
                         title='Evolución del Balance en Bolívares',
                         color_discrete_sequence=['#8B4513'])
        fig_bs.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Bolívares (Bs)"
        )
        st.plotly_chart(fig_bs, use_container_width=True)
        
        # Gráfico en Dólares
        fig_usd = px.line(df, x='fecha', y='balance_final_usd',
                          title='Evolución del Balance en Dólares',
                          color_discrete_sequence=['#D2691E'])
        fig_usd.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Dólares ($)"
        )
        st.plotly_chart(fig_usd, use_container_width=True)
        
        # Tabla resumen
        st.subheader("📋 Resumen del Período")
        
        resumen = df[['fecha', 'balance_inicial_bs', 'balance_final_bs', 
                     'balance_inicial_usd', 'balance_final_usd']].copy()
        
        resumen['fecha'] = resumen['fecha'].dt.strftime('%d/%m/%Y')
        resumen['balance_inicial_bs'] = resumen['balance_inicial_bs'].apply(lambda x: f"Bs. {x:,.2f}")
        resumen['balance_final_bs'] = resumen['balance_final_bs'].apply(lambda x: f"Bs. {x:,.2f}")
        resumen['balance_inicial_usd'] = resumen['balance_inicial_usd'].apply(lambda x: f"${x:,.2f}")
        resumen['balance_final_usd'] = resumen['balance_final_usd'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            resumen,
            column_config={
                "fecha": "Fecha",
                "balance_inicial_bs": "Balance Inicial Bs",
                "balance_final_bs": "Balance Final Bs",
                "balance_inicial_usd": "Balance Inicial $",
                "balance_final_usd": "Balance Final $"
            },
            use_container_width=True,
            hide_index=True
        )

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

def mostrar_historial_tasas():
    """Muestra el historial de tasas de cambio"""
    
    st.info("📈 Historial de Tasas de Cambio")
    
    # Obtener tasas de los últimos 30 días
    fechas = [(date.today() - timedelta(days=i)).isoformat() for i in range(30, -1, -1)]
    
    tasas = []
    for fecha in fechas:
        tasa = get_tasa_cambio(fecha)
        if tasa:
            tasas.append({'fecha': fecha, 'tasa': tasa})
    
    if tasas:
        df_tasas = pd.DataFrame(tasas)
        df_tasas['fecha'] = pd.to_datetime(df_tasas['fecha'])
        
        fig = px.line(df_tasas, x='fecha', y='tasa',
                      title='Evolución de la Tasa de Cambio',
                      color_discrete_sequence=['#2C1810'])
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Bs/$"
        )
        st.plotly_chart(fig, use_container_width=True)
