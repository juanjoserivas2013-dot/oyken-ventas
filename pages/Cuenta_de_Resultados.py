import streamlit as st
import pandas as pd
from pathlib import Path

st.title("OYKEN · Cuenta de Resultados")
st.caption("Verdad económica del negocio. Sin interpretación.")

# =========================
# ARCHIVOS
# =========================
VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
GASTOS_FILE = Path("gastos.csv")
INVENTARIO_FILE = Path("inventario.csv")
RRHH_FILE = Path("rrhh.csv")
MERMAS_FILE = Path("mermas.csv")

# =========================
# SELECCIÓN DE PERIODO
# =========================
periodo = st.selectbox(
    "Periodo",
    ["Marzo 2025"]  # luego será dinámico
)

# =========================
# INGRESOS
# =========================
ventas = pd.read_csv(VENTAS_FILE)
ingresos = ventas["ventas_total_eur"].sum()

# =========================
# COMPRAS
# =========================
compras = pd.read_csv(COMPRAS_FILE)
compras_total = compras["Coste (€)"].sum()

# =========================
# INVENTARIO
# =========================
inventario = pd.read_csv(INVENTARIO_FILE)

inv_inicial = inventario.iloc[-2]["Valor inventario (€)"]
inv_final = inventario.iloc[-1]["Valor inventario (€)"]

variacion_inventario = inv_final - inv_inicial

# =========================
# MERMAS
# =========================
mermas = pd.read_csv(MERMAS_FILE)
mermas_total = mermas["Valor merma (€)"].sum()

# =========================
# COSTE DE VENTAS
# =========================
coste_ventas = compras_total + (inv_inicial - inv_final) - mermas_total

# =========================
# MARGEN
# =========================
margen_bruto = ingresos - coste_ventas
margen_pct = (margen_bruto / ingresos) * 100 if ingresos > 0 else 0

# =========================
# PERSONAL
# =========================
rrhh = pd.read_csv(RRHH_FILE)
coste_personal = rrhh["Total personal (€)"].sum()

# =========================
# GASTOS
# =========================
gastos = pd.read_csv(GASTOS_FILE)
gastos_operativos = gastos["Importe (€)"].sum()

# =========================
# RESULTADO
# =========================
resultado_operativo = margen_bruto - coste_personal - gastos_operativos

# =========================
# VISUAL
# =========================
st.divider()
st.subheader("INGRESOS")
st.write(f"Ventas totales: **{ingresos:,.2f} €**")

st.divider()
st.subheader("COSTE DE VENTAS")
st.write(f"Compras imputadas: {compras_total:,.2f} €")
st.write(f"Variación de inventario: {variacion_inventario:,.2f} €")
st.write(f"Mermas: {mermas_total:,.2f} €")
st.write(f"**Coste de ventas total: {coste_ventas:,.2f} €**")

st.divider()
st.subheader("MARGEN BRUTO")
st.write(f"Margen bruto: {margen_bruto:,.2f} €")
st.write(f"Margen bruto %: {margen_pct:.1f} %")

st.divider()
st.subheader("COSTES DE PERSONAL")
st.write(f"Total personal: {coste_personal:,.2f} €")

st.divider()
st.subheader("GASTOS OPERATIVOS")
st.write(f"Gastos varios: {gastos_operativos:,.2f} €")

st.divider()
st.subheader("RESULTADO OPERATIVO")
st.write(f"**Resultado operativo: {resultado_operativo:,.2f} €**")
