import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import date

st.set_page_config(page_title="Trading Journal", page_icon="📓", layout="wide")

st.title("📓 Trading Journal")

DATA_FILE = "journal_data.json"
GOAL = 10000.0

# ---------------------------------------------------------
# PERSISTENCIA (JSON local)
# ---------------------------------------------------------
st.info(
    "⚠️ Los datos se guardan en un archivo JSON local del servidor de Streamlit Cloud. "
    "Si la app se reinicia o se re-despliega, el historial puede perderse. "
    "Para persistencia permanente a futuro, se puede migrar a Google Sheets o una base de datos.",
    icon="💾",
)


def load_journal():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_journal(entries):
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2, default=str)


if "journal" not in st.session_state:
    st.session_state.journal = load_journal()

# ---------------------------------------------------------
# FORMULARIO DE NUEVO REGISTRO
# ---------------------------------------------------------
st.markdown("### ➕ Nuevo registro diario")

with st.form("new_entry_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    entry_date = c1.date_input("Fecha", value=date.today())
    pnl = c2.number_input("PnL del día (USD)", value=0.0, step=10.0, format="%.2f")
    tp_count = c3.number_input("Trades TP (ganadores)", min_value=0, step=1, value=0)
    sl_count = c4.number_input("Trades SL (perdedores)", min_value=0, step=1, value=0)

    c5, c6 = st.columns(2)
    be_count = c5.number_input("Trades BE (breakeven)", min_value=0, step=1, value=0)
    notes = c6.text_input("Notas", value="")

    submitted = st.form_submit_button("Guardar registro")
    if submitted:
        st.session_state.journal.append({
            "date": str(entry_date),
            "pnl": pnl,
            "tp": int(tp_count),
            "sl": int(sl_count),
            "be": int(be_count),
            "notes": notes,
        })
        save_journal(st.session_state.journal)
        st.success("✅ Registro guardado")
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# SI NO HAY DATOS, PARAR AQUÍ
# ---------------------------------------------------------
if not st.session_state.journal:
    st.warning("Aún no hay registros. Agrega tu primer día de trading arriba ☝️")
    st.stop()

df = pd.DataFrame(st.session_state.journal)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["cum_pnl"] = df["pnl"].cumsum()

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
st.markdown("### 📈 KPIs automáticos")

total_tp = df["tp"].sum()
total_sl = df["sl"].sum()
total_be = df["be"].sum()
total_decisive_trades = total_tp + total_sl  # BE no cuenta como win ni loss

win_rate = (total_tp / total_decisive_trades * 100) if total_decisive_trades > 0 else 0.0

gross_profit = df.loc[df["pnl"] > 0, "pnl"].sum()
gross_loss = abs(df.loc[df["pnl"] < 0, "pnl"].sum())
profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

avg_win = df.loc[df["pnl"] > 0, "pnl"].mean() if (df["pnl"] > 0).any() else 0.0
avg_loss = abs(df.loc[df["pnl"] < 0, "pnl"].mean()) if (df["pnl"] < 0).any() else 0.0
wl_ratio = (avg_win / avg_loss) if avg_loss > 0 else float("inf")

# Max drawdown sobre la curva de equity acumulada
running_max = df["cum_pnl"].cummax()
drawdown = df["cum_pnl"] - running_max
max_drawdown = drawdown.min()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Win Rate", f"{win_rate:.1f}%")
k2.metric("Profit Factor", f"{profit_factor:.2f}" if profit_factor != float("inf") else "∞")
k3.metric("Ratio W/L", f"{wl_ratio:.2f}" if wl_ratio != float("inf") else "∞")
k4.metric("Max Drawdown", f"${max_drawdown:,.2f}")
k5.metric("PnL Total", f"${df['pnl'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# CURVA DE EQUITY + LÍNEA DE META
# ---------------------------------------------------------
st.markdown("### 💰 Curva de Equity")

fig_equity = go.Figure()
fig_equity.add_trace(
    go.Scatter(
        x=df["date"], y=df["cum_pnl"],
        mode="lines+markers", name="Equity acumulada",
        line=dict(color="#2ca02c", width=3),
    )
)
fig_equity.add_hline(
    y=GOAL, line_dash="dash", line_color="gold",
    annotation_text=f"Meta: ${GOAL:,.0f}", annotation_position="top left",
)
fig_equity.update_layout(
    height=400,
    margin=dict(l=0, r=0, t=20, b=0),
    yaxis_title="USD",
)
st.plotly_chart(fig_equity, use_container_width=True)

# ---------------------------------------------------------
# PROGRESO HACIA LA META
# ---------------------------------------------------------
st.markdown("### 🎯 Progreso hacia meta de $10,000 USD")
current_total = df["pnl"].sum()
progress_pct = max(0.0, min(current_total / GOAL, 1.0))
st.progress(progress_pct)
st.caption(f"${current_total:,.2f} de ${GOAL:,.0f} ({progress_pct*100:.1f}%)")

st.markdown("---")

# ---------------------------------------------------------
# RESUMEN SEMANAL
# ---------------------------------------------------------
st.markdown("### 📅 Resumen semanal")

df["week"] = df["date"].dt.to_period("W").astype(str)
weekly = df.groupby("week").agg(
    pnl_semana=("pnl", "sum"),
    trades=("pnl", "count"),
    tp=("tp", "sum"),
    sl=("sl", "sum"),
).reset_index()

fig_weekly = go.Figure()
fig_weekly.add_trace(
    go.Bar(
        x=weekly["week"], y=weekly["pnl_semana"],
        marker_color=["#2ca02c" if v >= 0 else "#d62728" for v in weekly["pnl_semana"]],
    )
)
fig_weekly.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), yaxis_title="PnL semanal (USD)")
st.plotly_chart(fig_weekly, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# HISTORIAL EDITABLE
# ---------------------------------------------------------
st.markdown("### 📋 Historial completo (editable)")

edited_df = st.data_editor(
    df[["date", "pnl", "tp", "sl", "be", "notes"]],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "date": st.column_config.DateColumn("Fecha"),
        "pnl": st.column_config.NumberColumn("PnL (USD)", format="%.2f"),
        "tp": st.column_config.NumberColumn("TP"),
        "sl": st.column_config.NumberColumn("SL"),
        "be": st.column_config.NumberColumn("BE"),
        "notes": st.column_config.TextColumn("Notas"),
    },
    key="journal_editor",
)

if st.button("💾 Guardar cambios del historial"):
    new_entries = edited_df.to_dict("records")
    st.session_state.journal = new_entries
    save_journal(new_entries)
    st.success("✅ Historial actualizado")
    st.rerun()
