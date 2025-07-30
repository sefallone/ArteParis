import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import uuid

# Configuración inicial
st.set_page_config(page_title="Pastelería-Café", layout="wide")

# Base de datos SQLite
def init_db():
    conn = sqlite3.connect('pasteleria.db')
    c = conn.cursor()
    
    # Tabla de productos
    c.execute('''CREATE TABLE IF NOT EXISTS productos
                 (id TEXT PRIMARY KEY, 
                  nombre TEXT, 
                  categoria TEXT, 
                  precio REAL, 
                  costo REAL, 
                  stock_centro INTEGER, 
                  stock_unicentro INTEGER,
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

init_db()

# Funciones de base de datos
def get_db_connection():
    return sqlite3.connect('pasteleria.db')

# Funciones para productos
def agregar_producto(nombre, categoria, precio, costo, stock_centro, stock_unicentro):
    conn = get_db_connection()
    c = conn.cursor()
    product_id = str(uuid.uuid4())
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (product_id, nombre, categoria, precio, costo, stock_centro, stock_unicentro, fecha_actual, fecha_actual))
    conn.commit()
    conn.close()

def actualizar_producto(product_id, nombre, categoria, precio, costo, stock_centro, stock_unicentro):
    conn = get_db_connection()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''UPDATE productos SET 
                 nombre=?, categoria=?, precio=?, costo=?, 
                 stock_centro=?, stock_unicentro=?, fecha_actualizacion=?
                 WHERE id=?''',
              (nombre, categoria, precio, costo, stock_centro, stock_unicentro, fecha_actual, product_id))
    conn.commit()
    conn.close()

def eliminar_producto(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM productos", conn)
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
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return False
    
    precio_unitario = producto[3]
    impuesto = precio_unitario * 0.16
    total = (precio_unitario + impuesto) * cantidad
    
    # Actualizar stock
    conn = get_db_connection()
    c = conn.cursor()
    
    if sucursal == "Centro":
        c.execute("UPDATE productos SET stock_centro = stock_centro - ? WHERE id=?", (cantidad, producto_id))
    else:
        c.execute("UPDATE productos SET stock_unicentro = stock_unicentro - ? WHERE id=?", (cantidad, producto_id))
    
    # Registrar venta
    venta_id = str(uuid.uuid4())
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (venta_id, sucursal, producto_id, cantidad, precio_unitario, impuesto, total, forma_pago, fecha))
    
    conn.commit()
    conn.close()
    return True

def obtener_ventas():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ventas", conn)
    conn.close()
    return df

# Interfaz de usuario
def modulo_inventario():
    st.header("Gestión de Inventario")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Agregar Producto", "Modificar Producto", "Eliminar Producto", "Ver Inventario"])
    
    with tab1:
        with st.form("agregar_producto"):
            st.subheader("Agregar Nuevo Producto")
            nombre = st.text_input("Nombre del Producto")
            categoria = st.selectbox("Categoría", ["Pastel", "Pan", "Café", "Bebida", "Otro"])
            precio = st.number_input("Precio de Venta", min_value=0.0, step=0.1)
            costo = st.number_input("Costo", min_value=0.0, step=0.1)
            stock_centro = st.number_input("Stock Centro", min_value=0, step=1)
            stock_unicentro = st.number_input("Stock Unicentro", min_value=0, step=1)
            
            if st.form_submit_button("Agregar Producto"):
                agregar_producto(nombre, categoria, precio, costo, stock_centro, stock_unicentro)
                st.success("Producto agregado correctamente!")
    
    with tab2:
        st.subheader("Modificar Producto Existente")
        productos = obtener_productos()
        
        if not productos.empty:
            producto_seleccionado = st.selectbox(
                "Seleccione un producto para modificar",
                productos['nombre'],
                key="modificar_producto"
            )
            
            producto_id = productos[productos['nombre'] == producto_seleccionado]['id'].values[0]
            producto = obtener_producto_por_id(producto_id)
            
            with st.form("modificar_producto_form"):
                nuevo_nombre = st.text_input("Nombre", value=producto[1])
                nueva_categoria = st.selectbox(
                    "Categoría", 
                    ["Pastel", "Pan", "Café", "Bebida", "Otro"],
                    index=["Pastel", "Pan", "Café", "Bebida", "Otro"].index(producto[2])
                nuevo_precio = st.number_input("Precio", value=producto[3], min_value=0.0, step=0.1)
                nuevo_costo = st.number_input("Costo", value=producto[4], min_value=0.0, step=0.1)
                nuevo_stock_centro = st.number_input("Stock Centro", value=producto[5], min_value=0, step=1)
                nuevo_stock_unicentro = st.number_input("Stock Unicentro", value=producto[6], min_value=0, step=1)
                )
                if st.form_submit_button("Actualizar Producto"):
                    actualizar_producto(
                        producto_id, nuevo_nombre, nueva_categoria, 
                        nuevo_precio, nuevo_costo, nuevo_stock_centro, nuevo_stock_unicentro
                    )
                    st.success("Producto actualizado correctamente!")
        else:
            st.warning("No hay productos registrados.")
    
    with tab3:
        st.subheader("Eliminar Producto")
        productos = obtener_productos()
        
        if not productos.empty:
            producto_seleccionado = st.selectbox(
                "Seleccione un producto para eliminar",
                productos['nombre'],
                key="eliminar_producto"
            )
            
            producto_id = productos[productos['nombre'] == producto_seleccionado]['id'].values[0]
            
            if st.button("Eliminar Producto"):
                eliminar_producto(producto_id)
                st.success("Producto eliminado correctamente!")
        else:
            st.warning("No hay productos registrados.")
    
    with tab4:
        st.subheader("Inventario Actual")
        productos = obtener_productos()
        
        if not productos.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                categoria_filtro = st.selectbox(
                    "Filtrar por categoría",
                    ["Todas"] + list(productos['categoria'].unique())
                )
            with col2:
                sucursal_filtro = st.selectbox(
                    "Filtrar por sucursal",
                    ["Ambas", "Centro", "Unicentro"]
                )
            
            # Aplicar filtros
            if categoria_filtro != "Todas":
                productos = productos[productos['categoria'] == categoria_filtro]
            
            if sucursal_filtro != "Ambas":
                columna_stock = f"stock_{sucursal_filtro.lower()}"
                productos = productos[productos[columna_stock] > 0]
            
            # Mostrar inventario
            st.dataframe(productos.drop(columns=['id', 'fecha_creacion', 'fecha_actualizacion']), 
            
            # Resumen de inventario
            st.subheader("Resumen de Inventario")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Valor Total Inventario Centro", 
                         f"${productos['precio'].multiply(productos['stock_centro']).sum():,.2f}")
            
            with col2:
                st.metric("Valor Total Inventario Unicentro", 
                         f"${productos['precio'].multiply(productos['stock_unicentro']).sum():,.2f}")
        else:
            st.warning("No hay productos registrados.")

def modulo_ventas():
    st.header("Módulo de Ventas")
    
    sucursal = st.radio("Sucursal", ["Centro", "Unicentro"], horizontal=True)
    
    productos = obtener_productos()
    
    if not productos.empty:
        # Selección de productos
        producto_seleccionado = st.selectbox(
            "Seleccione un producto",
            productos['nombre']
        )
        
        producto_id = productos[productos['nombre'] == producto_seleccionado]['id'].values[0]
        producto = obtener_producto_por_id(producto_id)
        
        # Mostrar información del producto
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Precio", f"${producto[3]:,.2f}")
        
        with col2:
            stock = producto[5] if sucursal == "Centro" else producto[6]
            st.metric("Stock Disponible", stock)
        
        with col3:
            st.metric("Impuesto (16%)", f"${producto[3] * 0.16:,.2f}")
        
        # Formulario de venta
        with st.form("venta_form"):
            cantidad = st.number_input("Cantidad", min_value=1, max_value=stock, value=1)
            forma_pago = st.selectbox("Forma de Pago", ["Efectivo", "Tarjeta Crédito", "Tarjeta Débito", "Transferencia"])
            
            if st.form_submit_button("Registrar Venta"):
                if registrar_venta(sucursal, producto_id, cantidad, forma_pago):
                    st.success("Venta registrada correctamente!")
                else:
                    st.error("Error al registrar la venta")
    else:
        st.warning("No hay productos registrados para vender.")
    
    # Historial de ventas
    st.subheader("Historial de Ventas Recientes")
    ventas = obtener_ventas()
    
    if not ventas.empty:
        ventas_recientes = ventas.sort_values('fecha', ascending=False).head(10)
        st.dataframe(ventas_recientes.drop(columns=['id', 'producto_id']))
    else:
        st.warning("No hay ventas registradas.")

# Menú principal
def main():
    st.title("Sistema de Pastelería-Café")
    
    menu = st.sidebar.selectbox("Menú Principal", ["Inicio", "Inventario", "Ventas", "Reportes"])
    
    if menu == "Inicio":
        st.subheader("Bienvenido al Sistema de Gestión de Pastelería-Café")
        st.write("""
        **Sucursales:**
        - Centro
        - Unicentro
        
        **Funcionalidades:**
        - Gestión de inventario (agregar, modificar, eliminar productos)
        - Registro de ventas con impuestos (16%)
        - Reportes de ventas e inventario
        """)
    
    elif menu == "Inventario":
        modulo_inventario()
    
    elif menu == "Ventas":
        modulo_ventas()
    
    elif menu == "Reportes":
        st.header("Reportes")
        
        tab1, tab2 = st.tabs(["Reporte de Ventas", "Reporte de Inventario"])
        
        with tab1:
            st.subheader("Reporte de Ventas")
            ventas = obtener_ventas()
            
            if not ventas.empty:
                ventas['fecha'] = pd.to_datetime(ventas['fecha'])
                
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    fecha_inicio = st.date_input("Fecha de inicio", value=ventas['fecha'].min())
                with col2:
                    fecha_fin = st.date_input("Fecha de fin", value=ventas['fecha'].max())
                
                ventas_filtradas = ventas[
                    (ventas['fecha'].dt.date >= fecha_inicio) & 
                    (ventas['fecha'].dt.date <= fecha_fin)
                ]
                
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
                
                col1, col2 = st.columns(2)
                
                with col1:
                    ventas_por_sucursal = ventas_filtradas.groupby('sucursal')['total'].sum()
                    st.bar_chart(ventas_por_sucursal)
                
                with col2:
                    ventas_por_forma_pago = ventas_filtradas.groupby('forma_pago')['total'].sum()
                    st.bar_chart(ventas_por_forma_pago)
                
                # Detalle de ventas
                st.subheader("Detalle de Ventas")
                st.dataframe(ventas_filtradas.drop(columns=['id', 'producto_id']))
            else:
                st.warning("No hay ventas registradas.")
        
        with tab2:
            st.subheader("Reporte de Inventario")
            productos = obtener_productos()
            
            if not productos.empty:
                # Resumen por categoría
                st.subheader("Inventario por Categoría")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    inv_centro = productos.groupby('categoria')['stock_centro'].sum()
                    st.bar_chart(inv_centro)
                    st.write("**Centro**")
                
                with col2:
                    inv_unicentro = productos.groupby('categoria')['stock_unicentro'].sum()
                    st.bar_chart(inv_unicentro)
                    st.write("**Unicentro**")
                
                # Productos con bajo stock
                st.subheader("Productos con Bajo Stock (menos de 5 unidades)")
                
                bajo_stock_centro = productos[productos['stock_centro'] < 5]
                bajo_stock_unicentro = productos[productos['stock_unicentro'] < 5]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Centro**")
                    if not bajo_stock_centro.empty:
                        st.dataframe(bajo_stock_centro[['nombre', 'categoria', 'stock_centro']])
                    else:
                        st.info("No hay productos con bajo stock en Centro")
                
                with col2:
                    st.write("**Unicentro**")
                    if not bajo_stock_unicentro.empty:
                        st.dataframe(bajo_stock_unicentro[['nombre', 'categoria', 'stock_unicentro']])
                    else:
                        st.info("No hay productos con bajo stock en Unicentro")
            else:
                st.warning("No hay productos registrados.")

if __name__ == "__main__":
    main()
