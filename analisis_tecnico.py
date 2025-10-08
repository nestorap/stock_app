
# Imprtamos librerias
import numpy as np
import pandas as pd
import streamlit as st

# Librerías de stock
import yfinance as yf
from lightweight_charts.widgets import StreamlitChart

#### Funciones ######
# Media
def calculate_sma(df:pd.DataFrame, period:int=50)-> pd.DataFrame:
    return pd.DataFrame(
        {
            'time': df.index,
            f'SMA {period}' : df.loc[:,'close'].rolling(window=period).mean()
        }
    ).dropna()
def claculate_ema(df:pd.DataFrame, period:int=150) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'time' : df.index,
            f'EMA {period}' : df.loc[:,'close'].ewm(span=period, adjust=False).mean()
        }
    )
# RSI
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df['close'].diff()  # Calcula los cambios entre precios consecutivos
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()  # Promedio de ganancias
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  # Promedio de pérdidas

    rs = gain / loss  # Relative Strength
    rsi = 100 - (100 / (1 + rs))  # RSI fórmula
    df['rsi'] = rsi.fillna(method='bfill')
    return df

def create_chart(df:pd.DataFrame, rsi):
    chart = StreamlitChart(width=1325, height=800)
    chart.time_scale(visible=False)

    chart2 = chart.create_subchart(width=1325, height=200, sync=True)
    line = chart2.create_line()

    chart.set(df)
    line.set(rsi)

    return chart

if __name__ == "__main__":
# Iniciamos la app
    st.title("Análisis técnico")
    timeframes = ['1m', '5m', '30m', '1h', '1d', '5d', '1wk', '1mo']
# Ponemos la barra de búsqueda
    ticker = st.sidebar.text_input("Ticker")
    start_date = st.sidebar.date_input("Start date")
    end_date = st.sidebar.date_input("End date")
    #select_timeframe = st.selectbox('Temporalidad', timeframes, index=4)
# Descargamos la data
    df = yf.download(ticker, start=start_date, end=end_date, interval='1d')

# Limpiamos el df para quitar el multi index
    rename_columns = {'Open' : 'open', 
                      'High':  'high', 
                      'Low' : 'low', 
                      'Close' : 'close', 
                      'Adj Close' : 'adj close', 
                      'Volume' : 'volume'}
    df.rename(columns=rename_columns, inplace=True)
    df.columns = df.columns.droplevel('Ticker')

## Calculamos las medias
    sma50 = calculate_sma(df=df, period=50)
    sma200 = calculate_sma(df=df, period=200)
    ema150 = claculate_ema(df=df, period=150)

# Calculamos RSI
    df = calculate_rsi(df=df, period=14)

# Medias para el macd
    df['EMA12'] = df.loc[:,'close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df.loc[:,'close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df.loc[:,'EMA12'] - df.loc[:,'EMA26']
    df['signal_line'] = df.loc[:,'MACD'].ewm(span=9, adjust=False).mean()
    df['histogram'] = df.loc[:,'MACD'] - df.loc[:,'signal_line']


# Pintamos el gráfico
    chart = StreamlitChart(
        width=1325,
        height=800,
        inner_width=1,
        inner_height=0.8,
        toolbox=True)
    # Medias
    line50 = chart.create_line('SMA 50', color='green')
    line200 = chart.create_line('SMA 200', color='purple')
    line_ema_150 = chart.create_line('EMA 150', color='blue')
    line50.set(sma50)
    line200.set(sma200)
    line_ema_150.set(ema150)

    # Grafico para el RSI
    chart2 = chart.create_subchart(width=1, height=0.2, sync=True) # Grafico para el RSI

# Creamos la linea
    line = chart2.create_line('RSI', color='orange')

    chart.watermark(1)
    chart2.watermark(2)

    chart.set(df)
    line.set(df.loc[:,'rsi'].reset_index())

    chart.load()

