import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# OYKEN · EBITDA (EXPERIMENTAL)
# =========================

st.set_page_config(page_title="OYKEN · EBITDA", layout="centered")
st.title("OYKEN · EBITDA")
st.caption("Lectura consolidada de rentabilidad operativa")

VENTAS_MENSUALES_FILE = Path("ventas_mensuales.csv")

# -------------------------
# CARGA DATOS
# -------------------------

if not VENTAS_MENSUALES_FILE.exists():
    st.warning("No hay datos consolidados de ventas todavía.")
    st.stop()

df = pd.read_csv(VENTAS_MENSUALES_FILE)

if df.empty:
    st.warning("El archivo de ventas mensuales está vacío.")
    st.stop()

df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
df["mes"] = pd.to_numeric(df["mes"], errors="coerce")
df["ventas_total_eur"] = pd.to_numeric(df["ventas_total_eur"], errors="coerce")
df = sort_values(["anio", "mes"])

# -------------------------
# SELECTORES
# -------------------------

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        sorted(df["anio"].dropna().unique()),
        index=len(sorted(df["anio"].dropna().unique())) - 1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x]
    )

# -------------------------
# FILTRADO
# -------------------------

df_f = df[df["anio"] == anio_sel]

if mes_sel != 0:
    df_f = df_f[df_f["mes"] == mes_sel]

df_f["Mes"] = df_f["mes"].map(MESES_ES)

# -------------------------
# KPIs EXPERIMENTALES
# -------------------------

ventas_periodo = df_f["ventas_total_eur"].sum()
meses_con_datos = df_f["mes"].nunique()
media_mensual = (
    ventas_periodo / meses_con_datos
    if meses_con_datos > 0 else 0
)

k1, k2, k3 = st.columns(3)

k1.metric("Ventas período", f"{ventas_periodo:,.2f} €")
k2.metric("Meses con datos", meses_con_datos)
k3.metric("Media mensual", f"{media_mensual:,.2f} €")

# -------------------------
# TABLA BASE
# -------------------------

st.divider()
st.subheader("Detalle de ventas consolidadas")

tabla = (
    df_f[["anio", "Mes", "ventas_total_eur"]]
    .rename(columns={
        "anio": "Año",
        "ventas_total_eur": "Ventas (€)"
    })
)

st.dataframe(
    tabla,
    hide_index=True,
    use_container_width=True
)

