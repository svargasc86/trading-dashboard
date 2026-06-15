# 📈 TIC — Trading Dashboard

Dashboard web de trading con Market Overview en tiempo real y Trading Journal con KPIs automáticos.

---

## 🚀 Cómo desplegarlo en Streamlit Cloud (paso a paso)

### Paso 1 — Crear cuenta en GitHub
1. Ve a [github.com](https://github.com) → Sign up
2. Crea un repositorio nuevo: `trading-dashboard` (público)

### Paso 2 — Subir el código
Opción A — Subir archivos manualmente (más fácil):
1. En tu repositorio en GitHub, haz clic en **"Add file" → "Upload files"**
2. Sube todos los archivos de esta carpeta manteniendo la estructura:
   ```
   app.py
   requirements.txt
   .streamlit/config.toml
   pages/1_Market_Overview.py
   pages/2_Trading_Journal.py
   ```

Opción B — Con Git (si tienes Git instalado):
```bash
git init
git add .
git commit -m "Trading dashboard inicial"
git remote add origin https://github.com/TU_USUARIO/trading-dashboard.git
git push -u origin main
```

### Paso 3 — Desplegar en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en **"New app"**
3. Conecta con tu cuenta de GitHub
4. Selecciona el repositorio `trading-dashboard`
5. En "Main file path" escribe: `app.py`
6. Haz clic en **"Deploy"**

¡En 2-3 minutos tendrás tu URL pública!

### Paso 4 — API Key de FRED (para gráfica Desempleo/Inflación)
1. Regístrate gratis en [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)
2. En Streamlit Cloud, ve a tu app → **"Settings" → "Secrets"**
3. Agrega:
```toml
FRED_API_KEY = "tu_api_key_aqui"
```

---

## 📊 Módulos

### 🌐 Market Overview
- MNQ (Micro Nasdaq Futures)
- S&P 500 (ES Futures)
- Dow Jones 30 (YM Futures)
- Índice del Dólar (DXY)
- VIX — Volatilidad del mercado
- Volatilidad NQ (VXN)
- Bonos del Tesoro USA 10 años
- Desempleo vs Inflación USA (FRED)

### 📓 Trading Journal
- Ingreso diario: fecha, PnL, trades (SL/TP/BE), notas
- KPIs automáticos: win rate, profit factor, max drawdown, ratio W/L
- Curva de equity con línea de meta
- Resumen semanal
- Progreso hacia meta de $10,000 USD
- Historial completo editable

---

## 🛠 Stack técnico
- Python + Streamlit
- yfinance (datos de mercado)
- Plotly (gráficas)
- FRED API (macro USA)
- JSON local (persistencia del journal)
