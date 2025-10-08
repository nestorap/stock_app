# Imprtamos librerias
import numpy as np
import pandas as pd
import streamlit as st

# Librerías de stock
import yfinance as yf
from lightweight_charts import Chart
from lightweight_charts.widgets import StreamlitChart

def get_bar_data(symbol, start_date, end_date, interval):
    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    # Limpiamos el multiindex
    rename_columns = {'Open' : 'open', 
                    'High':  'high', 
                    'Low' : 'low', 
                    'Close' : 'close', 
                    'Adj Close' : 'adj close', 
                    'Volume' : 'volume'}
    df.rename(columns=rename_columns, inplace=True)
    df.columns = df.columns.droplevel('Ticker')
    return df
# RSI
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df['close'].diff()  # Calcula los cambios entre precios consecutivos
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()  # Promedio de ganancias
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  # Promedio de pérdidas

    rs = gain / loss  # Relative Strength
    rsi = 100 - (100 / (1 + rs))  # RSI fórmula

    return pd.DataFrame(
        {
            'time': df.index,
            'RSI': rsi
        }
    ).dropna()
if __name__ == '__main__':
# Descargamos los datos de apple mismo
    start_date = "2024-01-01"
    end_date = "2024-12-12"
    interval='1d'
    chart = StreamlitChart(width=1325, height=800, inner_width=1, inner_height=0.8)
    chart.time_scale(visible=False)

    chart2 = chart.create_subchart(width=1, height=0.8, sync=True)
    line = chart2.create_line('RSI', color='orange')
    
    chart.watermark(1)
    chart2.watermark(2)

    df = get_bar_data('AAPL', start_date, end_date, interval)
    rsi = calculate_rsi(df, 14)

    chart.set(df)
    line.set(rsi)

    chart.load()




