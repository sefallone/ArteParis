import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
import altair as alt # Necesario para los gráficos en el módulo de reportes

# --- 0. Inicialización de Firebase (Caché para ejecutar una sola vez) ---
@st.cache_resource
# --- 0. Inicialización de Firebase (Caché para ejecutar una sola vez) ---
@st.cache_resource
@st.cache_resource
def initialize_firebase():
    try:
        # Verificar si ya está inicializado
        if not firebase_admin._apps:
            # Obtener configuración del secret
            if "firebase" not in st.secrets:
                st.error("No se encontró la configuración de Firebase en secrets.toml")
                return None, None
            
            # Configuración para Service Account
            sa_info = {
                "type": st.secrets.firebase.type,
                "project_id": st.secrets.firebase.project_id,
                "private_key_id": st.secrets.firebase.private_key_id,
                "private_key": st.secrets.firebase.private_key.replace('\\n', '\n'),
                "client_email": st.secrets.firebase.client_email,
                "client_id": st.secrets.firebase.client_id,
                "auth_uri": st.secrets.firebase.auth_uri,
                "token_uri": st.secrets.firebase.token_uri,
                "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
                "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url
            }
            
            # Crear credencial
            cred = credentials.Certificate(sa_info)
            
            # Inicializar Firebase
            firebase_admin.initialize_app(cred)
            
            st.success("Firebase inicializado correctamente con Service Account")
        
        return firestore.client(), None
    
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {str(e)}")
        return None, None

# Uso en tu aplicación
db, _ = initialize_firebase()
if db is None:
    st.error("No se pudo conectar a Firestore. Verifica tus credenciales.")
    st.stop()
# Configuración inicial de Streamlit
st.set_page_config(page_title="Pastelería-Café", layout="wide")

# --- Funciones de base de datos (Firestore) ---

@st.cache_resource
def get_firestore_db():
    # Esta función asegura que el cliente de Firestore se obtenga y se cachee.
    # La inicialización de Firebase se maneja en initialize_firebase()
    if db is None: # Usa la variable global 'db'
        st.error("Firestore no está disponible. Asegúrate de que Firebase se inicializó correctamente.")
        st.stop() # Detiene la ejecución si Firestore no está disponible
    return db

# Funciones para productos
def agregar_producto(nombre, categoria, precio, costo, stock, sucursal):
    db_client = get_firestore_db()
    product_id = str(uuid.uuid4())
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    product_data = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": float(precio),
        "costo": float(costo),
        "stock": int(stock),
        "sucursal": sucursal,
        "fecha_creacion": fecha_actual,
        "fecha_actualizacion": fecha_actual
    }
    
    try:
        db_client.collection("productos").document(product_id).set(product_data)
        return True
    except Exception as e:
        st.error(f"Error al agregar producto: {e}")
        return False

def actualizar_producto(product_id, nombre, categoria, precio, costo, stock):
    db_client = get_firestore_db()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    product_data = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": float(precio),
        "costo": float(costo),
        "stock": int(stock),
        "fecha_actualizacion": fecha_actual
    }
    
    try:
        db_client.collection("productos").document(product_id).update(product_data)
        return True
    except Exception as e:
        st.error(f"Error al actualizar producto: {e}")
        return False

def eliminar_producto(product_id):
    db_client = get_firestore_db()
    try:
        db_client.collection("productos").document(product_id).delete()
        return True
    except Exception as e:
        st.error(f"Error al eliminar producto: {e}")
        return False

# --- MODIFICACIÓN CLAVE AQUÍ ---
@st.cache_data(ttl=600)
def obtener_productos(sucursal):
    db_client = get_firestore_db()
    productos_list = []
    try:
        # Usamos .stream() que es eficiente para grandes colecciones
        productos_ref = db_client.collection("productos").where("sucursal", "==", sucursal).stream()
        for doc in productos_ref:
            prod_data = doc.to_dict()
            prod_data['id'] = doc.id # Añadir el ID del documento al diccionario
            productos_list.append(prod_data)
    except Exception as e:
        # Capturamos cualquier error, incluyendo posibles timeouts
        st.error(f"Error al obtener productos: {e}")
        # En caso de error, devolvemos un DataFrame vacío
        return pd.DataFrame(columns=['id', 'nombre', 'precio', 'costo', 'stock', 'sucursal'])
        
    # Si la lista está vacía (no hay productos), también devolvemos un DataFrame vacío
    if not productos_list:
        return pd.DataFrame(columns=['id', 'nombre', 'precio', 'costo', 'stock', 'sucursal'])
        
    return pd.DataFrame(productos_list)

def obtener_producto_por_id(product_id):
    db_client = get_firestore_db()
    try:
        doc = db_client.collection("productos").document(product_id).get()
        if doc.exists:
            prod_data = doc.to_dict()
            prod_data['id'] = doc.id
            return prod_data
        return None
    except Exception as e:
        st.error(f"Error al obtener producto por ID: {e}")
        return None

# Funciones para ventas
def registrar_venta(sucursal, producto_id, cantidad, forma_pago):
    db_client = get_firestore_db()
    producto_info = obtener_producto_por_id(producto_id)
    
    if not producto_info:
        st.error("Producto no encontrado.")
        return False
    
    if producto_info['sucursal'] != sucursal:
        st.error(f"El producto '{producto_info['nombre']}' no pertenece a la sucursal '{sucursal}'.")
        return False
    
    if producto_info['stock'] < cantidad:
        st.error(f"Stock insuficiente para '{producto_info['nombre']}'. Stock disponible: {producto_info['stock']}")
        return False

    precio_unitario = producto_info['precio']
    impuesto_unitario = precio_unitario * 0.16
    total_venta = (precio_unitario + impuesto_unitario) * cantidad
    
    # Usar una transacción para actualizar el stock y registrar la venta de forma atómica
    try:
        transaction = db_client.transaction()
        product_doc_ref = db_client.collection("productos").document(producto_id)

        @firestore.transactional
        def update_product_and_add_sale(transaction, product_ref, prod_info, qty, branch, payment_method):
            snapshot = product_ref.get(transaction=transaction)
            if not snapshot.exists:
                raise ValueError("El producto no existe o fue eliminado durante la transacción.")
            
            current_stock = snapshot.get("stock")
            if current_stock < qty:
                raise ValueError(f"Stock insuficiente para '{prod_info['nombre']}'. Disponible: {current_stock}")

            new_stock = current_stock - qty
            transaction.update(product_ref, {"stock": new_stock, "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            venta_id = str(uuid.uuid4())
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sale_data = {
                "sucursal": branch,
                "producto_id": prod_info['id'],
                "nombre_producto": prod_info['nombre'], # Añadir nombre para facilitar reportes
                "cantidad": qty,
                "precio_unitario": prod_info['precio'],
                "impuesto": impuesto_unitario * qty,
                "total": total_venta,
                "forma_pago": payment_method,
                "fecha": fecha
            }
            db_client.collection("ventas").document(venta_id).set(sale_data, transaction=transaction)
            return True

        update_product_and_add_sale(transaction, product_doc_ref, producto_info, cantidad, sucursal, forma_pago)
        return True
    except ValueError as ve:
        st.error(f"Error de stock/producto: {ve}")
        return False
    except Exception as e:
        st.error(f"Error al registrar la venta (transacción): {e}")
        return False

@st.cache_data(ttl=600)
def obtener_ventas(sucursal):
    db_client = get_firestore_db()
    ventas_list = []
    try:
        ventas_ref = db_client.collection("ventas").where("sucursal", "==", sucursal).stream()
        for doc in ventas_ref:
            sale_data = doc.to_dict()
            sale_data['id'] = doc.id # Añadir el ID del documento
            ventas_list.append(sale_data)
    except Exception as e:
        st.error(f"Error al obtener ventas: {e}")
        return pd.DataFrame(columns=['id', 'sucursal', 'producto_id', 'nombre_producto', 'cantidad', 'precio_unitario', 'impuesto', 'total', 'forma_pago', 'fecha'])

    if not ventas_list:
        return pd.DataFrame(columns=['id', 'sucursal', 'producto_id', 'nombre_producto', 'cantidad', 'precio_unitario', 'impuesto', 'total', 'forma_pago', 'fecha'])
    return pd.DataFrame(ventas_list)

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
                    if agregar_producto(nombre, categoria, precio, costo, stock, sucursal):
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
            selected_product_name = producto_seleccionado_display.split(" (Stock:")[0]
            producto_id = productos[productos['nombre'] == selected_product_name]['id'].values[0]
            producto_data = obtener_producto_por_id(producto_id) # Obtener el diccionario de datos del producto
            
            if producto_data:
                current_nombre = producto_data.get('nombre', '')
                current_categoria = producto_data.get('categoria', 'Otro')
                current_precio = producto_data.get('precio', 0.0)
                current_costo = producto_data.get('costo', 0.0)
                current_stock = producto_data.get('stock', 0)

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
                            if actualizar_producto(
                                producto_id, nuevo_nombre, nueva_categoria, 
                                nuevo_precio, nuevo_costo, nuevo_stock
                            ):
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
                if eliminar_producto(producto_id):
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
            st.metric("Precio Unitario", f"${producto_info['precio']:,.2f}")
        
        with col2:
            st.metric("Stock Disponible", producto_info['stock'])
        
        with col3:
            st.metric("Impuesto (16%) por unidad", f"${producto_info['precio'] * 0.16:,.2f}")
        
        # Formulario de venta
        with st.form("venta_form"):
            cantidad = st.number_input("Cantidad", min_value=1, max_value=producto_info['stock'], value=1)
            forma_pago = st.selectbox("Forma de Pago", ["Efectivo", "Tarjeta Crédito", "Tarjeta Débito", "Transferencia"])
            
            # Calcular total antes de enviar
            precio_calc = producto_info['precio']
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
        # Si 'nombre_producto' se añadió en la venta, también se puede mostrar
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
                # Ya no es necesario obtener productos_df de SQLite, el nombre_producto ya está en ventas
                ventas_por_producto = ventas_filtradas.groupby('nombre_producto')['total'].sum().nlargest(5).reset_index()
                st.subheader("Top 5 Productos más Vendidos")
                chart_top_productos = alt.Chart(ventas_por_producto).mark_bar().encode(
                    x=alt.X('total:Q', title='Ventas Totales ($)'),
                    y=alt.Y('nombre_producto:N', sort='-x', title='Producto'),
                    tooltip=['nombre_producto', alt.Tooltip('total', format='$,.2f')]
                ).properties(
                    title='Top 5 Productos más Vendidos'
                )
                st.altair_chart(chart_top_productos, use_container_width=True)

                # Detalle de ventas
                st.subheader("Detalle de Ventas")
                # Asegurarse de que las columnas existan antes de intentar eliminarlas
                cols_to_drop = ['id', 'producto_id', 'sucursal'] # 'id_producto' ya no existe del merge
                cols_to_display = [col for col in ventas_filtradas.columns if col not in cols_to_drop]
                st.dataframe(ventas_filtradas[cols_to_display], use_container_width=True)
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


