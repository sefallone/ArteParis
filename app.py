import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import uuid

# Configuración inicial
st.set_page_config(page_title="Pastelería-Café", layout="wide")

# Base de datos SQLite
# Usamos st.cache_resource para asegurar que la base de datos se inicialice solo una vez
@st.cache_resource
def init_db():
    conn = sqlite3.connect('pasteleria.db')
    c = conn.cursor()
    
    # Tabla de productos (ahora con sucursal)
    c.execute('''CREATE TABLE IF NOT EXISTS productos
                 (id TEXT PRIMARY KEY, 
                  nombre TEXT, 
                  categoria TEXT, 
                  precio REAL, 
                  costo REAL, 
                  stock INTEGER,
                  sucursal TEXT,
                  fecha_creacion TEXT,
                  fecha_actualizacion TEXT)''')
    
    # Tabla de ventas
    c.execute('''CREATE TABLE IF NOT EXISTS ventas
                 (id TEXT PRIMARY KEY,
                  sucursal TEXT,
                  producto_id TEXT,
                  cantidad INTEGER,
                  precio_unitario REAL,
                  impuesto REAL,
                  total REAL,
                  forma_pago TEXT,
                  fecha TEXT,
                  FOREIGN KEY(producto_id) REFERENCES productos(id))''')
    
    conn.commit()
    conn.close()
    st.success("Base de datos inicializada correctamente.") # Mensaje de confirmación

# Llamar a la función de inicialización de la base de datos
init_db()

# Funciones de base de datos
def get_db_connection():
    return sqlite3.connect('pasteleria.db')

# Funciones para productos
def agregar_producto(nombre, categoria, precio, costo, stock, sucursal):
    conn = get_db_connection()
    c = conn.cursor()
    product_id = str(uuid.uuid4())
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (product_id, nombre, categoria, precio, costo, stock, sucursal, fecha_actual, fecha_actual))
    conn.commit()
    conn.close()

def actualizar_producto(product_id, nombre, categoria, precio, costo, stock):
    conn = get_db_connection()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''UPDATE productos SET 
                  nombre=?, categoria=?, precio=?, costo=?, 
                  stock=?, fecha_actualizacion=?
                  WHERE id=?''',
              (nombre, categoria, precio, costo, stock, fecha_actual, product_id))
    conn.commit()
    conn.close()

def eliminar_producto(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def obtener_productos(sucursal):
    conn = get_db_connection()
    query = "SELECT * FROM productos WHERE sucursal=?"
    df = pd.read_sql_query(query, conn, params=(sucursal,))
    conn.close()
    return df

def obtener_producto_por_id(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM productos WHERE id=?", (product_id,))
    producto = c.fetchone()
    conn.close()
    return producto

# Funciones para ventas
def registrar_venta(sucursal, producto_id, cantidad, forma_pago):
    producto_info = obtener_producto_por_id(producto_id)
    if not producto_info:
        st.error("Producto no encontrado.")
        return False
    
    # Los índices de la tupla producto_info corresponden a las columnas de la tabla productos
    # id=0, nombre=1, categoria=2, precio=3, costo=4, stock=5, sucursal=6, fecha_creacion=7, fecha_actualizacion=8
    
    if producto_info[6] != sucursal:  # Verificar que el producto pertenezca a la sucursal
        st.error(f"El producto '{producto_info[1]}' no pertenece a la sucursal '{sucursal}'.")
        return False
    
    if producto_info[5] < cantidad: # Verificar stock
        st.error(f"Stock insuficiente para '{producto_info[1]}'. Stock disponible: {producto_info[5]}")
        return False

    precio_unitario = producto_info[3]
    impuesto_unitario = precio_unitario * 0.16
    total = (precio_unitario + impuesto_unitario) * cantidad
    
    # Actualizar stock
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, producto_id))
    
    # Registrar venta
    venta_id = str(uuid.uuid4())
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (venta_id, sucursal, producto_id, cantidad, precio_unitario, impuesto_unitario * cantidad, total, forma_pago, fecha))
    
    conn.commit()
    conn.close()
    return True

def obtener_ventas(sucursal):
    conn = get_db_connection()
    query = "SELECT * FROM ventas WHERE sucursal=?"
    df = pd.read_sql_query(query, conn, params=(sucursal,))
    conn.close()
    return df

# Interfaz de usuario
def mostrar_seleccion_sucursal():
    st.sidebar.title("Configuración")
    sucursal = st.sidebar.selectbox("Seleccione la sucursal", ["Centro", "Unicentro"])
    return sucursal

def modulo_inventario(sucursal):
    st.header(f"Gestión de Inventario - Sucursal {sucursal}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Agregar Producto", "Modificar Producto", "Eliminar Producto", "Ver Inventario"])
    
    with tab1:
        with st.form("agregar_producto"):
            st.subheader("Agregar Nuevo Producto")
            nombre = st.text_input("Nombre del Producto")
            categoria = st.selectbox("Categoría", ["Pastel", "Pan", "Café", "Bebida", "Otro"])
            precio = st.number_input("Precio de Venta", min_value=0.0, step=0.1, format="%.2f")
            costo = st.number_input("Costo", min_value=0.0, step=0.1, format="%.2f")
            stock = st.number_input("Stock", min_value=0, step=1)
            
            if st.form_submit_button("Agregar Producto"):
                if nombre and precio >= 0 and costo >= 0 and stock >= 0:
                    agregar_producto(nombre, categoria, precio, costo, stock, sucursal)
                    st.success("Producto agregado correctamente!")
                    st.experimental_rerun() # Recargar para ver los cambios
                else:
                    st.error("Por favor, complete todos los campos y asegúrese de que los valores sean válidos.")
    
    with tab2:
        st.subheader("Modificar Producto Existente")
        productos = obtener_productos(sucursal)
        
        if not productos.empty:
            # Crear una lista de opciones con el nombre y el stock para facilitar la selección
            producto_options = productos.apply(lambda row: f"{row['nombre']} (Stock: {row['stock']})", axis=1).tolist()
            
            producto_seleccionado_display = st.selectbox(
                "Seleccione un producto para modificar",
                producto_options,
                key="modificar_producto_select" # Clave única para este selectbox
            )
            
            # Obtener el ID del producto seleccionado a partir del nombre en display
            # Se asume que los nombres de productos son únicos para esta lógica simple
            selected_product_name = producto_seleccionado_display.split(" (Stock:")[0]
            producto_id = productos[productos['nombre'] == selected_product_name]['id'].values[0]
            producto_data = obtener_producto_por_id(producto_id) # Obtener la tupla de datos del producto
            
            if producto_data:
                # Mapear la tupla a nombres de columnas para facilitar el acceso
                # (id, nombre, categoria, precio, costo, stock, sucursal, fecha_creacion, fecha_actualizacion)
                current_nombre, current_categoria, current_precio, current_costo, current_stock = \
                    producto_data[1], producto_data[2], producto_data[3], producto_data[4], producto_data[5]

                with st.form("modificar_producto_form"):
                    nuevo_nombre = st.text_input("Nombre", value=current_nombre)
                    nueva_categoria = st.selectbox(
                        "Categoría", 
                        ["Pastel", "Pan", "Café", "Bebida", "Otro"],
                        index=["Pastel", "Pan", "Café", "Bebida", "Otro"].index(current_categoria) if current_categoria in ["Pastel", "Pan", "Café", "Bebida", "Otro"] else 0
                    )
                    nuevo_precio = st.number_input("Precio", value=float(current_precio), min_value=0.0, step=0.1, format="%.2f")
                    nuevo_costo = st.number_input("Costo", value=float(current_costo), min_value=0.0, step=0.1, format="%.2f")
                    nuevo_stock = st.number_input("Stock", value=int(current_stock), min_value=0, step=1)
                    
                    if st.form_submit_button("Actualizar Producto"):
                        if nuevo_nombre and nuevo_precio >= 0 and nuevo_costo >= 0 and nuevo_stock >= 0:
                            actualizar_producto(
                                producto_id, nuevo_nombre, nueva_categoria, 
                                nuevo_precio, nuevo_costo, nuevo_stock
                            )
                            st.success("Producto actualizado correctamente!")
                            st.experimental_rerun() # Recargar para ver los cambios
                        else:
                            st.error("Por favor, complete todos los campos y asegúrese de que los valores sean válidos.")
            else:
                st.error("Error: No se pudo cargar la información del producto seleccionado.")
        else:
            st.warning("No hay productos registrados en esta sucursal para modificar.")
    
    with tab3:
        st.subheader("Eliminar Producto")
        productos = obtener_productos(sucursal)
        
        if not productos.empty:
            producto_seleccionado = st.selectbox(
                "Seleccione un producto para eliminar",
                productos['nombre'],
                key="eliminar_producto_select" # Clave única para este selectbox
            )
            
            producto_id = productos[productos['nombre'] == producto_seleccionado]['id'].values[0]
            
            if st.button("Eliminar Producto"):
                eliminar_producto(producto_id)
                st.success("Producto eliminado correctamente!")
                st.experimental_rerun() # Recargar para ver los cambios
        else:
            st.warning("No hay productos registrados en esta sucursal para eliminar.")
    
    with tab4:
        st.subheader(f"Inventario Actual - {sucursal}")
        productos = obtener_productos(sucursal)
        
        if not productos.empty:
            # Filtros
            categoria_filtro = st.selectbox(
                "Filtrar por categoría",
                ["Todas"] + list(productos['categoria'].unique()),
                key="inventario_categoria_filtro"
            )
            
            # Aplicar filtros
            if categoria_filtro != "Todas":
                productos = productos[productos['categoria'] == categoria_filtro]
            
            # Mostrar inventario
            # Asegurarse de que las columnas existan antes de intentar eliminarlas
            cols_to_drop = ['id', 'sucursal', 'fecha_creacion', 'fecha_actualizacion']
            cols_to_display = [col for col in productos.columns if col not in cols_to_drop]
            st.dataframe(productos[cols_to_display], use_container_width=True)
            
            # Resumen de inventario
            st.subheader("Resumen de Inventario")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Número Total de Productos", len(productos))
            
            with col2:
                # Asegurarse de que 'precio' y 'stock' son numéricos antes de la multiplicación
                productos['precio'] = pd.to_numeric(productos['precio'], errors='coerce').fillna(0)
                productos['stock'] = pd.to_numeric(productos['stock'], errors='coerce').fillna(0)
                st.metric("Valor Total Inventario", 
                          f"${(productos['precio'] * productos['stock']).sum():,.2f}")
            
            # Productos con bajo stock
            st.subheader("Productos con Bajo Stock (menos de 5 unidades)")
            bajo_stock = productos[productos['stock'] < 5]
            
            if not bajo_stock.empty:
                st.dataframe(bajo_stock[['nombre', 'categoria', 'stock']], use_container_width=True)
            else:
                st.info("No hay productos con bajo stock.")
        else:
            st.warning("No hay productos registrados en esta sucursal.")

def modulo_ventas(sucursal):
    st.header(f"Módulo de Ventas - Sucursal {sucursal}")
    
    productos = obtener_productos(sucursal)
    
    if not productos.empty:
        # Filtrar productos con stock > 0 para la venta
        productos_disponibles = productos[productos['stock'] > 0]

        if productos_disponibles.empty:
            st.warning("No hay productos disponibles para la venta en esta sucursal. Agregue stock en el módulo de Inventario.")
            return

        # Selección de productos
        producto_seleccionado_nombre = st.selectbox(
            "Seleccione un producto",
            productos_disponibles['nombre']
        )
        
        producto_id = productos_disponibles[productos_disponibles['nombre'] == producto_seleccionado_nombre]['id'].values[0]
        producto_info = obtener_producto_por_id(producto_id)
        
        # Mostrar información del producto
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Precio Unitario", f"${producto_info[3]:,.2f}")
        
        with col2:
            st.metric("Stock Disponible", producto_info[5])
        
        with col3:
            st.metric("Impuesto (16%) por unidad", f"${producto_info[3] * 0.16:,.2f}")
        
        # Formulario de venta
        with st.form("venta_form"):
            cantidad = st.number_input("Cantidad", min_value=1, max_value=producto_info[5], value=1)
            forma_pago = st.selectbox("Forma de Pago", ["Efectivo", "Tarjeta Crédito", "Tarjeta Débito", "Transferencia"])
            
            # Calcular total antes de enviar
            precio_calc = producto_info[3]
            impuesto_calc = precio_calc * 0.16
            total_calc = (precio_calc + impuesto_calc) * cantidad
            st.info(f"Total a pagar: ${total_calc:,.2f}")

            if st.form_submit_button("Registrar Venta"):
                if registrar_venta(sucursal, producto_id, cantidad, forma_pago):
                    st.success("Venta registrada correctamente!")
                    st.experimental_rerun() # Recargar para ver los cambios
                else:
                    # El mensaje de error ya se muestra dentro de registrar_venta
                    pass
    else:
        st.warning("No hay productos registrados para vender en esta sucursal. Agregue productos en el módulo de Inventario.")
    
    # Historial de ventas
    st.subheader(f"Historial de Ventas Recientes - {sucursal}")
    ventas = obtener_ventas(sucursal)
    
    if not ventas.empty:
        # Asegurarse de que 'fecha' sea datetime para ordenar
        ventas['fecha'] = pd.to_datetime(ventas['fecha'])
        ventas_recientes = ventas.sort_values('fecha', ascending=False).head(10)
        # Asegurarse de que las columnas existan antes de intentar eliminarlas
        cols_to_drop = ['id', 'producto_id', 'sucursal']
        cols_to_display = [col for col in ventas_recientes.columns if col not in cols_to_drop]
        st.dataframe(ventas_recientes[cols_to_display], use_container_width=True)
    else:
        st.info("No hay ventas registradas en esta sucursal.")

def modulo_reportes(sucursal):
    st.header(f"Reportes - Sucursal {sucursal}")
    
    tab1, tab2 = st.tabs(["Reporte de Ventas", "Reporte de Inventario"])
    
    with tab1:
        st.subheader("Reporte de Ventas")
        ventas = obtener_ventas(sucursal)
        
        if not ventas.empty:
            ventas['fecha'] = pd.to_datetime(ventas['fecha'])
            
            # Filtros de fecha
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha de inicio", value=ventas['fecha'].min().date())
            with col2:
                fecha_fin = st.date_input("Fecha de fin", value=ventas['fecha'].max().date())
            
            ventas_filtradas = ventas[
                (ventas['fecha'].dt.date >= fecha_inicio) & 
                (ventas['fecha'].dt.date <= fecha_fin)
            ]
            
            if ventas_filtradas.empty:
                st.warning("No hay ventas para el rango de fechas seleccionado.")
            else:
                # Resumen
                st.subheader("Resumen de Ventas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Ventas Totales", f"${ventas_filtradas['total'].sum():,.2f}")
                
                with col2:
                    st.metric("Impuestos Totales", f"${ventas_filtradas['impuesto'].sum():,.2f}")
                
                with col3:
                    st.metric("Número de Ventas", len(ventas_filtradas))
                
                # Gráficos
                st.subheader("Análisis de Ventas")
                
                # Gráfico: Ventas por Forma de Pago
                ventas_por_forma_pago = ventas_filtradas.groupby('forma_pago')['total'].sum().reset_index()
                chart_forma_pago = alt.Chart(ventas_por_forma_pago).mark_bar().encode(
                    x=alt.X('forma_pago:N', title='Forma de Pago'),
                    y=alt.Y('total:Q', title='Ventas Totales ($)'),
                    tooltip=['forma_pago', alt.Tooltip('total', format='$,.2f')]
                ).properties(
                    title='Ventas por Forma de Pago'
                )
                st.altair_chart(chart_forma_pago, use_container_width=True)

                # Gráfico: Ventas por Producto (Top N)
                # Unir ventas con productos para obtener nombres de productos
                conn = get_db_connection()
                productos_df = pd.read_sql_query("SELECT id, nombre FROM productos", conn)
                conn.close()
                
                ventas_con_nombres = pd.merge(ventas_filtradas, productos_df, left_on='producto_id', right_on='id', suffixes=('_venta', '_producto'))
                
                ventas_por_producto = ventas_con_nombres.groupby('nombre')['total'].sum().nlargest(5).reset_index()
                st.subheader("Top 5 Productos más Vendidos")
                chart_top_productos = alt.Chart(ventas_por_producto).mark_bar().encode(
                    x=alt.X('total:Q', title='Ventas Totales ($)'),
                    y=alt.Y('nombre:N', sort='-x', title='Producto'),
                    tooltip=['nombre', alt.Tooltip('total', format='$,.2f')]
                ).properties(
                    title='Top 5 Productos más Vendidos'
                )
                st.altair_chart(chart_top_productos, use_container_width=True)

                # Detalle de ventas
                st.subheader("Detalle de Ventas")
                # Asegurarse de que las columnas existan antes de intentar eliminarlas
                cols_to_drop = ['id_venta', 'producto_id', 'sucursal', 'id_producto'] # id_producto es del merge
                cols_to_display = [col for col in ventas_con_nombres.columns if col not in cols_to_drop]
                st.dataframe(ventas_con_nombres[cols_to_display], use_container_width=True)
        else:
            st.info("No hay ventas registradas en esta sucursal para generar reportes.")
    
    with tab2:
        st.subheader("Reporte de Inventario")
        productos = obtener_productos(sucursal)
        
        if not productos.empty:
            # Resumen por categoría
            st.subheader("Inventario por Categoría")
            
            inv_categoria = productos.groupby('categoria')['stock'].sum().reset_index()
            chart_inv_categoria = alt.Chart(inv_categoria).mark_bar().encode(
                x=alt.X('categoria:N', title='Categoría'),
                y=alt.Y('stock:Q', title='Stock Total'),
                tooltip=['categoria', 'stock']
            ).properties(
                title='Stock por Categoría de Producto'
            )
            st.altair_chart(chart_inv_categoria, use_container_width=True)
            
            # Productos con bajo stock
            st.subheader("Productos con Bajo Stock (menos de 5 unidades)")
            
            bajo_stock = productos[productos['stock'] < 5]
            
            if not bajo_stock.empty:
                st.dataframe(bajo_stock[['nombre', 'categoria', 'stock']], use_container_width=True)
            else:
                st.info("No hay productos con bajo stock.")
        else:
            st.warning("No hay productos registrados en esta sucursal para generar reportes de inventario.")

# Menú principal
def main():
    st.title("Sistema de Pastelería-Café")
    
    # Selección de sucursal (siempre visible)
    sucursal = mostrar_seleccion_sucursal()
    
    # Menú de opciones
    menu = st.sidebar.selectbox("Menú Principal", ["Inicio", "Inventario", "Ventas", "Reportes"])
    
    if menu == "Inicio":
        st.subheader(f"Bienvenido al Sistema de Gestión - Sucursal {sucursal}")
        st.write("""
        **Funcionalidades:**
        - Gestión de inventario (agregar, modificar, eliminar productos)
        - Registro de ventas con impuestos (16%)
        - Reportes de ventas e inventario
        
        **Nota:** Todos los datos mostrados corresponden a la sucursal seleccionada.
        """)
    
    elif menu == "Inventario":
        modulo_inventario(sucursal)
    
    elif menu == "Ventas":
        modulo_ventas(sucursal)
    
    elif menu == "Reportes":
        modulo_reportes(sucursal)

if __name__ == "__main__":
    main()

