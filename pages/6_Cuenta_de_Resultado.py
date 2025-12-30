import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="OYKEN · Cuenta de Resultados",
    layout="centered"
)

st.title("OYKEN · Cuenta de Resultados")

# =====================================================
# ARCHIVOS
# =====================================================

VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
GASTOS_FILE = Path("gastos.csv")
RRHH_FILE = Path("rrhh_coste_mensual.csv")

# =====================================================
# SELECTORES DE PERIODO
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

mes_sel = st.selectbox("Mes", MESES, index=11)
anio_sel = st.selectbox("Año", list(range(2022, 2031)), index=3)

mes_num = MESES.index(mes_sel) + 1

st.divider()

# =====================================================
# INGRESOS · VENTAS
# =====================================================

ventas_mes = 0.0

if VENTAS_FILE.exists():
    df_v = pd.read_csv(VENTAS_FILE)
    df_v["fecha"] = pd.to_datetime(df_v["fecha"])

    ventas_mes = df_v[
        (df_v["fecha"].dt.month == mes_num) &
        (df_v["fecha"].dt.year == anio_sel)
    ]["ventas_total_eur"].sum()

st.subheader("Ingresos")
st.write("Ventas netas")
st.write(f"{ventas_mes:,.2f} €")

st.divider()

# =====================================================
# COSTE DE VENTAS (COGS)
# =====================================================

compras_producto = 0.0

if COMPRAS_FILE.exists():
    df_c = pd.read_csv(COMPRAS_FILE)
    df_c["fecha"] = pd.to_datetime(df_c["fecha"])

    compras_producto = df_c[
        (df_c["fecha"].dt.month == mes_num) &
        (df_c["fecha"].dt.year == anio_sel)
    ]["importe_eur"].sum()

margen_bruto = ventas_mes - compras_producto

st.subheader("Coste de ventas (COGS)")
st.write("Compras de producto")
st.write(f"-{compras_producto:,.2f} €")

st.write("Variación de inventario")
st.write("0.00 €")

st.markdown("**MARGEN BRUTO**")
st.markdown(f"**{margen_bruto:,.2f} €**")

st.divider()

# =====================================================
# GASTOS DE PERSONAL (RRHH)
# =====================================================

coste_personal = 0.0

if RRHH_FILE.exists():
    df_rrhh = pd.read_csv(RRHH_FILE)

    fila = df_rrhh[
        (df_rrhh["Año"] == anio_sel) &
        (df_rrhh["Mes"] == mes_sel)
    ]

    if not fila.empty:
        coste_personal = float(fila.iloc[0]["Coste Empresa (€)"])

st.subheader("Gastos de personal")
st.write("Coste de personal")
st.write(f"-{coste_personal:,.2f} €")

st.divider()

# =====================================================
# GASTOS OPERATIVOS
# =====================================================

gastos_operativos = 0.0

if GASTOS_FILE.exists():
    df_g = pd.read_csv(GASTOS_FILE)
    df_g["fecha"] = pd.to_datetime(df_g["fecha"])

    gastos_operativos = df_g[
        (df_g["fecha"].dt.month == mes_num) &
        (df_g["fecha"].dt.year == anio_sel)
    ]["importe_eur"].sum()

st.subheader("Gastos operativos")
st.write("Alquiler y otros gastos")
st.write(f"-{gastos_operativos:,.2f} €")

st.divider()

# =====================================================
# EBITDA
# =====================================================

ebitda = margen_bruto - coste_personal - gastos_operativos

st.subheader("Resultado del periodo")
st.markdown("**EBITDA**")
st.markdown(f"### **{ebitda:,.2f} €**")

st.caption(
    "La cuenta de resultados se construye a partir de datos reales "
    "de ventas, compras, RRHH y gastos."
)
