# pages/Ventas.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.database import (
    guardar_venta, get_ventas, get_tasa_cambio, 
    get_balance_diario, guardar_balance_diario,
    clear_cache, get_db
)
import plotly.express as px
import uuid

def show():
    st.markdown("""
        <div class="main-header">
            <h1>💰 Gestión de Ventas</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Pestañas
    tab1, tab2 = st.tabs(["📊 Resumen de Ventas", "📝 Registrar Ventas del Día"])
    
    with tab1:
        mostrar_resumen_ventas()
    
    with tab2:
        registrar_ventas_dia()

def mostrar_resumen_ventas():
    """Muestra el resumen de ventas con gráficos"""
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    
    ventas = get_ventas(
        fecha_inicio=fecha_inicio.isoformat() if fecha_inicio else None,
        fecha_fin=fecha_fin.isoformat() if fecha_fin else None
    )
    
    if not ventas:
        st.info("No hay ventas registradas en este período.")
        return
    
    # Resumen
    total_ventas = sum(v.get('total_bs', 0) for v in ventas)
    tasa = get_tasa_cambio()
    total_usd = total_ventas / tasa if tasa > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Ventas", f"Bs. {total_ventas:,.2f}")
    with col2:
        st.metric("Total en $", f"${total_usd:,.2f}")
    
    # Gráfico de evolución por tipo de ingreso
    st.subheader("📈 Evolución de Ventas por Método de Pago")
    
    df = pd.DataFrame(ventas)
    
    if 'metodo_pago' in df.columns and 'fecha' in df.columns:
        # Agrupar por fecha y método de pago
        df_evolucion = df.groupby(['fecha', 'metodo_pago'])['total_bs'].sum().reset_index()
        df_evolucion['fecha'] = pd.to_datetime(df_evolucion['fecha'])
        df_evolucion = df_evolucion.sort_values('fecha')
        
        # Crear gráfico de barras apiladas o líneas
        fig = px.line(df_evolucion, x='fecha', y='total_bs', color='metodo_pago',
                      title='Evolución de Ventas por Método de Pago',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Total (Bs.)",
            legend_title="Método de Pago"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de distribución por método de pago (últimos 30 días)
        st.subheader("📊 Distribución por Método de Pago")
        
        # Filtrar últimos 30 días
        fecha_limite = date.today() - timedelta(days=30)
        df_reciente = df[pd.to_datetime(df['fecha']) >= pd.to_datetime(fecha_limite)]
        
        if not df_reciente.empty:
            df_metodos = df_reciente.groupby('metodo_pago')['total_bs'].sum().reset_index()
            
            fig_pie = px.pie(df_metodos, values='total_bs', names='metodo_pago',
                             title='Distribución de Ventas por Método (Últimos 30 días)',
                             color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabla detallada
    st.subheader("📋 Detalle de Ventas")
    
    # Seleccionar columnas para mostrar
    display_cols = ['fecha', 'metodo_pago', 'total_bs', 'tasa_cambio']
    if all(col in df.columns for col in display_cols):
        df_display = df[display_cols].copy()
        
        # Formatear
        df_display['total_bs'] = df_display['total_bs'].apply(lambda x: f"Bs. {x:,.2f}")
        df_display['tasa_cambio'] = df_display['tasa_cambio'].apply(lambda x: f"{x:,.2f}")
        df_display['fecha'] = pd.to_datetime(df_display['fecha']).dt.strftime('%d/%m/%Y')
        
        # Renombrar columnas
        df_display.columns = ['Fecha', 'Método de Pago', 'Total (Bs.)', 'Tasa']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

def registrar_ventas_dia():
    """Registra las ventas del día por método de pago"""
    
    st.subheader("📝 Registrar Ventas del Día")
    
    # Seleccionar fecha
    fecha_venta = st.date_input("Fecha de la Venta", value=date.today())
    fecha_str = fecha_venta.isoformat()
    
    # Obtener tasa del día
    tasa = get_tasa_cambio(fecha_str)
    
    # Verificar si ya hay ventas para esta fecha
    ventas_existentes = get_ventas(fecha_str, fecha_str)
    
    if ventas_existentes:
        st.warning(f"⚠️ Ya existen ventas registradas para {fecha_venta.strftime('%d/%m/%Y')}")
        
        # Mostrar ventas existentes
        df_existente = pd.DataFrame(ventas_existentes)
        st.dataframe(
            df_existente[['metodo_pago', 'total_bs']],
            column_config={
                "metodo_pago": "Método de Pago",
                "total_bs": "Total (Bs.)"
            },
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("🗑️ Eliminar ventas de esta fecha y volver a registrar"):
            # Eliminar ventas de esta fecha
            db = get_db()
            for venta in ventas_existentes:
                db.collection('ventas').document(venta['id']).delete()
            
            # Limpiar caché
            clear_cache()
            st.success("✅ Ventas eliminadas. Puedes registrar nuevamente.")
            st.rerun()
        
        st.markdown("---")
        st.info("Si deseas agregar más ventas a esta fecha, continúa con el formulario.")
    
    st.info(f"💱 Tasa de cambio para {fecha_venta.strftime('%d/%m/%Y')}: {tasa:,.2f} Bs/$")
    
    # ============ FORMULARIO CON ACTUALIZACIÓN EN TIEMPO REAL ============
    
    # Crear contenedor para el resumen dinámico
    contenedor_resumen = st.container()
    
    # Contenedor para el formulario
    with st.form("registro_ventas_dia"):
        st.markdown("### 💰 Ingresos del Día")
        st.markdown("Ingresa los totales por cada método de pago:")
        
        # Métodos de pago
        col1, col2 = st.columns(2)
        
        with col1:
            total_punto1 = st.number_input(
                "Total Punto de Venta 1 (Bs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="punto1",
                value=0.0
            )
            
            total_punto2 = st.number_input(
                "Total Punto de Venta 2 (Bs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="punto2",
                value=0.0
            )
            
            total_biopago = st.number_input(
                "Total Biopago (Bs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="biopago",
                value=0.0
            )
            
            total_efectivo_bs = st.number_input(
                "Total Efectivo en Bs.",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="efectivo_bs",
                value=0.0
            )
        
        with col2:
            total_efectivo_usd = st.number_input(
                "Total Efectivo en $",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="efectivo_usd",
                value=0.0
            )
            
            total_pago_movil = st.number_input(
                "Total Pago Móvil (Bs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="pago_movil",
                value=0.0
            )
            
            total_zelle = st.number_input(
                "Total Zelle ($)",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="zelle",
                value=0.0
            )
            
            total_transferencia = st.number_input(
                "Total Transferencia (Bs.)",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="transferencia",
                value=0.0
            )
        
        # Observaciones
        observaciones = st.text_area("Observaciones (opcional)")
        
        # Botón para guardar
        submitted = st.form_submit_button("💾 Guardar Ventas del Día", use_container_width=True)
        
        # ============ PROCESAR EL FORMULARIO ============
        
        # Calcular totales (dentro del form, pero se actualiza al hacer submit)
        total_bs = (
            total_punto1 + total_punto2 + total_biopago + 
            total_efectivo_bs + total_pago_movil + total_transferencia
        )
        
        total_usd = total_efectivo_usd + total_zelle
        
        # Mostrar resumen DENTRO del formulario (se actualiza al hacer submit)
        st.markdown("---")
        st.markdown("### 📊 Resumen de Ventas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total en Bolívares", f"Bs. {total_bs:,.2f}")
        with col2:
            st.metric("Total en Dólares", f"${total_usd:,.2f}")
        with col3:
            total_usd_bs = total_usd * tasa if tasa > 0 else 0
            total_general = total_bs + total_usd_bs
            st.metric("Total General", f"Bs. {total_general:,.2f}")
        
        if submitted:
            if total_bs == 0 and total_usd == 0:
                st.error("❌ Por favor ingresa al menos un monto")
            else:
                # Guardar cada método de pago como una venta
                ventas_guardadas = []
                
                def guardar_venta_individual(metodo, monto_bs, monto_usd=0):
                    if monto_bs > 0 or monto_usd > 0:
                        venta_data = {
                            'fecha': fecha_str,
                            'metodo_pago': metodo,
                            'total_bs': monto_bs,
                            'total_usd': monto_usd,
                            'total': monto_bs + (monto_usd * tasa if tasa > 0 else 0),
                            'tasa_cambio': tasa,
                            'usuario_creacion': st.session_state.user_data.get('id', ''),
                            'observaciones': observaciones
                        }
                        resultado = guardar_venta(venta_data)
                        if resultado:
                            ventas_guardadas.append(metodo)
                        return resultado
                    return None
                
                # Guardar cada método
                guardar_venta_individual("Punto de Venta 1", total_punto1)
                guardar_venta_individual("Punto de Venta 2", total_punto2)
                guardar_venta_individual("Biopago", total_biopago)
                guardar_venta_individual("Efectivo Bs", total_efectivo_bs)
                guardar_venta_individual("Efectivo $", 0, total_efectivo_usd)
                guardar_venta_individual("Pago Móvil", total_pago_movil)
                guardar_venta_individual("Zelle", 0, total_zelle)
                guardar_venta_individual("Transferencia", total_transferencia)
                
                if ventas_guardadas:
                    st.success(f"✅ Ventas registradas exitosamente para {fecha_venta.strftime('%d/%m/%Y')}")
                    st.balloons()
                    
                    # Actualizar balance automáticamente
                    actualizar_balance_con_ventas(fecha_str, total_general, tasa)
                    
                    # Limpiar caché
                    clear_cache()
                    
                    # ✅ LIMPIAR EL FORMULARIO - Usar rerun para resetear
                    st.rerun()
                else:
                    st.error("❌ Error al guardar las ventas")

def actualizar_balance_con_ventas(fecha_str, total_ventas, tasa):
    """Actualiza el balance con las ventas del día"""
    
    try:
        # Obtener balance del día
        balance = get_balance_diario(fecha_str)
        
        if not balance:
            # Si no hay balance, crear uno
            balance = {
                'fecha': fecha_str,
                'tasa_cambio': tasa,
                'balance_inicial_bs': 0,
                'balance_inicial_usd': 0,
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
        
        # Actualizar balance con las ventas
        total_ventas_usd = total_ventas / tasa if tasa > 0 else 0
        
        balance['total_ingresos_bs'] = balance.get('total_ingresos_bs', 0) + total_ventas
        balance['total_ingresos_usd'] = balance.get('total_ingresos_usd', 0) + total_ventas_usd
        balance['balance_final_bs'] = balance.get('balance_final_bs', 0) + total_ventas
        balance['balance_final_usd'] = balance.get('balance_final_usd', 0) + total_ventas_usd
        
        # Agregar transacción de venta
        transaccion = {
            'id': str(uuid.uuid4()),
            'fecha': fecha_str,
            'descripcion': 'Ventas del día',
            'categoria': 'Ventas',
            'subcategoria': 'Múltiples métodos',
            'tipo': 'ingreso',
            'monto_bs': total_ventas,
            'monto_usd': total_ventas_usd,
            'saldo_bs': balance['balance_final_bs'],
            'saldo_usd': balance['balance_final_usd'],
            'tasa_aplicada': tasa,
            'detalle': 'Ventas registradas desde el formulario'
        }
        
        if 'transacciones' not in balance:
            balance['transacciones'] = []
        balance['transacciones'].append(transaccion)
        
        # Guardar balance actualizado
        guardar_balance_diario(balance)
        
    except Exception as e:
        st.error(f"❌ Error al actualizar el balance: {e}")
