import sqlite3

DB_FILE = "inventario.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def buscar_producto(sucursal, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM productos
        WHERE sucursal = ? AND LOWER(nombre) = LOWER(?)
        LIMIT 1;
    """, (sucursal, nombre))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado

def modificar_producto(id, nuevo_nombre, nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre = ?, cantidad = ?, precio_costo = ?, precio_venta = ?
        WHERE id = ?;
    """, (nuevo_nombre, nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta, id))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_producto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?;", (id,))
    conn.commit()
    cursor.close()
    conn.close()
