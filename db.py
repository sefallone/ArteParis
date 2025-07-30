import sqlite3
import os

DB_PATH = "productos.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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
    conn.close()

def agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (sucursal, nombre, cantidad, precio_costo, precio_venta) VALUES (?, ?, ?, ?, ?)",
                   (sucursal, nombre, cantidad, precio_costo, precio_venta))
    conn.commit()
    conn.close()

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE sucursal = ?", (sucursal,))
    productos = cursor.fetchall()
    conn.close()
    return productos

def actualizar_producto(producto_id, nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre = ?, cantidad = ?, precio_costo = ?, precio_venta = ?
        WHERE id = ?;
    """, (nombre, cantidad, precio_costo, precio_venta, producto_id))
    conn.commit()
    conn.close()

def eliminar_producto(producto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()
