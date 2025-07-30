import sqlite3

def get_connection():
    return sqlite3.connect("inventario.db", check_same_thread=False)

def crear_tabla_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sucursal TEXT NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_costo REAL,
            precio_venta REAL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (sucursal, nombre, cantidad, precio_costo, precio_venta)
        VALUES (?, ?, ?, ?, ?);
    """, (sucursal, nombre, cantidad, precio_costo, precio_venta))
    conn.commit()
    cursor.close()
    conn.close()

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE sucursal = ?;", (sucursal,))
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos

def buscar_producto(sucursal, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM productos WHERE sucursal = ? AND nombre = ?;
    """, (sucursal, nombre))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto

def modificar_producto(sucursal, nombre, nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET cantidad = ?, precio_costo = ?, precio_venta = ?
        WHERE sucursal = ? AND nombre = ?;
    """, (nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta, sucursal, nombre))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_producto(sucursal, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM productos WHERE sucursal = ? AND nombre = ?;
    """, (sucursal, nombre))
    conn.commit()
    cursor.close()
    conn.close()
