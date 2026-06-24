import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.graph_objects as go

def format_currency(amount, currency='Bs'):
    """Formatea un monto como moneda"""
    if currency == 'Bs':
        return f"Bs. {amount:,.2f}"
    elif currency == '$':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f}"

def get_fecha_rango(dias=30):
    """Obtiene rango de fechas para los últimos N días"""
    end_date = date.today()
    start_date = end_date - pd.Timedelta(days=dias)
    return start_date.isoformat(), end_date.isoformat()

def crear_grafico_indicador(valor, titulo, color='#8B4513'):
    """Crea un gráfico de indicador simple"""
    fig = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = valor,
        title = {'text': titulo},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, valor * 1.5]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, valor * 0.5], 'color': "lightgray"},
                {'range': [valor * 0.5, valor * 0.8], 'color': "gray"}
            ]
        }
    ))
    fig.update_layout(height=200)
    return fig

def validar_jerarquia(jerarquia_requerida):
    """Valida si el usuario tiene la jerarquía requerida"""
    if 'user_data' not in st.session_state:
        return False
    return st.session_state.user_data.get('jerarquia', 0) >= jerarquia_requerida

def get_nombre_mes(numero):
    """Obtiene el nombre del mes en español"""
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    return meses.get(numero, '')
