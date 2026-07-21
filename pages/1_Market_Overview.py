import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Market Overview", page_icon="🌐", layout="wide")

st.title("🌐 Market Overview")
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------------------------------------------------
# CONFIG DE INSTRUMENTOS
# ---------------------------------------------------------
INSTRUMENTS = {
    "MNQ (Micro Nasdaq Futures)": "MNQ=F",
    "S&P 500 (ES Futures)": "ES=F",
    "Dow Jones 30 (YM Futures)": "YM=F",
    "Índice del Dólar (DXY)": "DX-Y.NYB",
    "VIX (Volatilidad S&P)": "^VIX",
    "VXN (Volatilidad Nasdaq)": "^VXN",
    "Bonos Tesoro USA 10Y": "^TNX",
}


@st.cache_data(ttl=120)
def fetch_quote(ticker: str):
    """Descarga precio actual + histórico intradía de un ticker."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d", interval="15m")
        if hist.empty:
            return None, None, None
        last_price = hist["Close"].iloc[-1]
        prev_close = tk.history(period="2d", interval="1d")["Close"].iloc[0]
        change_pct = ((last_price - prev_close) / prev_close) * 100
        return last_price, change_pct, hist
    except Exception:
        return None, None, None


def render_instrument_card(name: str, ticker: str, col):
    with col:
        price, change_pct, hist = fetch_quote(ticker)
        if price is None:
            st.warning(f"⚠️ No se pudo cargar {name} ({ticker})")
            return
        st.metric(
            label=name,
            value=f"{price:,.2f}",
            delta=f"{change_pct:+.2f}%",
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                line=dict(width=2, color="#2ca02c" if change_pct >= 0 else "#d62728"),
                fill="tozeroy",
            )
        )
        fig.update_layout(
            height=180,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


st.markdown("### 📊 Cotizaciones en tiempo real")
st.caption("Datos con ~15 min de delay vía Yahoo Finance. Se refrescan cada 2 min (caché).")

names = list(INSTRUMENTS.keys())
cols = st.columns(4)
for i, name in enumerate(names):
    render_instrument_card(name, INSTRUMENTS[name], cols[i % 4])

if st.button("🔄 Refrescar datos ahora"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# GRÁFICO COMPARATIVO MNQ vs DXY vs VIX (correlación visual)
# ---------------------------------------------------------
st.markdown("### 🔗 Comparativo: MNQ vs DXY vs VIX (normalizado)")
st.caption("Normalizado a base 100 para comparar tendencias relativas, no valores absolutos.")

try:
    tickers_compare = ["MNQ=F", "DX-Y.NYB", "^VIX"]
    data_compare = yf.download(tickers_compare, period="1mo", interval="1d", progress=False)["Close"]
    data_norm = (data_compare / data_compare.iloc[0]) * 100

    fig_compare = go.Figure()
    label_map = {"MNQ=F": "MNQ", "DX-Y.NYB": "DXY", "^VIX": "VIX"}
    for col_name in data_norm.columns:
        fig_compare.add_trace(
            go.Scatter(
                x=data_norm.index,
                y=data_norm[col_name],
                mode="lines",
                name=label_map.get(col_name, col_name),
            )
        )
    fig_compare.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Base 100",
    )
    st.plotly_chart(fig_compare, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ No se pudo cargar el comparativo: {e}")

st.markdown("---")

# ---------------------------------------------------------
# DATOS MACRO FRED — Desempleo vs Inflación
# ---------------------------------------------------------
st.markdown("### 🏛️ Desempleo vs Inflación (USA — FRED)")

FRED_API_KEY = st.secrets.get("FRED_API_KEY", "")

if not FRED_API_KEY:
    st.info(
        "ℹ️ Para ver esta gráfica, agrega tu `FRED_API_KEY` en "
        "**Settings → Secrets** de tu app en Streamlit Cloud. "
        "Regístrate gratis en fred.stlouisfed.org/docs/api/api_key.html"
    )
else:
    @st.cache_data(ttl=3600)
    def fetch_fred_series(series_id: str, api_key: str, years_back: int = 5):
        start_date = (datetime.now() - timedelta(days=365 * years_back)).strftime("%Y-%m-%d")
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={api_key}&file_type=json"
            f"&observation_start={start_date}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        obs = r.json()["observations"]
        df = pd.DataFrame(obs)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna(subset=["value"])[["date", "value"]]

    try:
        unemployment = fetch_fred_series("UNRATE", FRED_API_KEY)   # Tasa de desempleo
        inflation = fetch_fred_series("CPIAUCSL", FRED_API_KEY)    # CPI (índice, no % var.)
        inflation["yoy_pct"] = inflation["value"].pct_change(12) * 100

        fig_macro = go.Figure()
        fig_macro.add_trace(
            go.Scatter(
                x=unemployment["date"], y=unemployment["value"],
                name="Desempleo (%)", mode="lines", line=dict(color="#1f77b4"),
            )
        )
        fig_macro.add_trace(
            go.Scatter(
                x=inflation["date"], y=inflation["yoy_pct"],
                name="Inflación CPI (% interanual)", mode="lines", line=dict(color="#ff7f0e"),
            )
        )
        fig_macro.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="%",
        )
        st.plotly_chart(fig_macro, use_container_width=True)

        col_a, col_b = st.columns(2)
        col_a.metric("Desempleo actual", f"{unemployment['value'].iloc[-1]:.1f}%")
        col_b.metric("Inflación CPI (YoY)", f"{inflation['yoy_pct'].iloc[-1]:.1f}%")

    except Exception as e:
        st.error(f"⚠️ Error cargando datos de FRED: {e}")
