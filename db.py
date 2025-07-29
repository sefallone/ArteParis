import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",           # Cambia si usas otro servidor
        user="tu_usuario_mysql",    # Cambia por tu usuario
        password="tu_contraseña",   # Cambia por tu contraseña
        database="arte_paris"
    )

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario WHERE sucursal = %s", (sucursal,))
    productos = cursor.fetchall()
    conn.close()
    return productos

def agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inventario (sucursal, nombre_producto, cantidad, precio_costo, precio_venta)
        VALUES (%s, %s, %s, %s, %s)
    """, (sucursal, nombre, cantidad, precio_costo, precio_venta))
    conn.commit()
    conn.close()
