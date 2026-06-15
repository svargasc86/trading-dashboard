import streamlit as st

st.set_page_config(
    page_title="Nuevo Horizonte Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("📊 Trading Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Meta TopStep:** $10,000 USD")

st.title("📈 Nuevo Horizonte — Trading Dashboard")
st.markdown("Bienvenido a tu dashboard de trading. Selecciona una sección en el menú lateral.")

col1, col2 = st.columns(2)
with col1:
    st.info("🌐 **Market Overview** — Análisis de mercados en tiempo real: MNQ, S&P500, DJ30, DXY, VIX, Bonos 10Y, Desempleo/Inflación.")
with col2:
    st.info("📓 **Trading Journal** — Registro de operaciones, KPIs automáticos, curva de equity y progreso hacia tu meta.")