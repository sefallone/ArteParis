import sqlite3

DB_PATH = "inventario.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def crear_tabla_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_costo REAL,
            precio_venta REAL
        );
    """)
    conn.commit()
    conn.close()

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos;")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def agregar_producto(nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, cantidad, precio_costo, precio_venta)
        VALUES (?, ?, ?, ?)
    """, (nombre, cantidad, precio_costo, precio_venta))
    conn.commit()
    conn.close()
