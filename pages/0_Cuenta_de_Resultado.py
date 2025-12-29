import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura económica real del negocio")

st.divider()

# =====================================================
# ARCHIVOS
# =====================================================

VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
INVENTARIO_FILE = Path("inventario.csv")
GASTOS_FILE = Path("gastos.csv")

# =====================================================
# SELECTOR DE PERIODO
# =====================================================

meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

col_sel_1, col_sel_2 = st.columns(2)

with col_sel_1:
    mes_sel = st.selectbox("Mes", meses, index=date.today().month - 1)

with col_sel_2:
    año_sel = st.selectbox(
        "Año",
        list(range(date.today().year - 3, date.today().year + 1)),
        index=3
    )

mes_num = meses.index(mes_sel) + 1
periodo = f"{año_sel}-{mes_num:02d}"

st.divider()

# =====================================================
# CARGA DE DATOS
# =====================================================

# --- Ventas ---
if VENTAS_FILE.exists():
    ventas = pd.read_csv(VENTAS_FILE, parse_dates=["fecha"])
    ventas["Mes"] = ventas["fecha"].dt.strftime("%Y-%m")
    ventas_mes = ventas[ventas["Mes"] == periodo]
    ventas_total = ventas_mes["ventas_total_eur"].sum()
else:
    ventas_total = 0.0

# --- Compras ---
if COMPRAS_FILE.exists():
    compras = pd.read_csv(COMPRAS_FILE)
    compras["Mes"] = pd.to_datetime(compras["Fecha"], dayfirst=True).dt.strftime("%Y-%m")
    compras_mes = compras[compras["Mes"] == periodo]

    compras_producto = compras_mes[
        compras_mes["Familia"].isin(["Materia prima", "Bebidas"])
    ]["Coste (€)"].sum()
else:
    compras_producto = 0.0

# --- Inventario ---
inventario_var = 0.0
if INVENTARIO_FILE.exists():
    inv = pd.read_csv(INVENTARIO_FILE)
    inv["Mes_key"] = inv["Año"].astype(str) + "-" + inv["Mes"]
    inv_mes = inv[inv["Mes_key"].str.contains(str(año_sel))]
    if len(inv_mes) >= 2:
        inventario_var = inv_mes.iloc[-1]["Inventario (€)"] - inv_mes.iloc[-2]["Inventario (€)"]

# --- Gastos ---
gastos_total = 0.0
gastos_por_categoria = {}

if GASTOS_FILE.exists():
    gastos = pd.read_csv(GASTOS_FILE)
    gastos_mes = gastos[gastos["Mes"] == periodo]

    gastos_total = gastos_mes["Coste (€)"].sum()
    gastos_por_categoria = (
        gastos_mes
        .groupby("Categoria")["Coste (€)"]
        .sum()
        .to_dict()
    )

# --- RRHH ---
coste_personal = 0.0
if "rrhh_coste_personal" in st.session_state:
    rrhh = st.session_state.rrhh_coste_personal
    if mes_sel in rrhh.columns:
        coste_personal = rrhh[mes_sel].sum()

# =====================================================
# CÁLCULOS
# =====================================================

margen_bruto = ventas_total - compras_producto + inventario_var
ebitda = margen_bruto - coste_personal - gastos_total

# =====================================================
# BLOQUE 1 · RESULTADO EJECUTIVO
# =====================================================

st.subheader("Resultado del periodo")

def fila_resultado(label, value, pct=None):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write(label)
    with c2:
        st.write(f"{value:,.2f} €")

fila_resultado("Ventas netas", ventas_total)
fila_resultado("Margen bruto", margen_bruto)
fila_resultado("EBITDA", ebitda)

st.divider()

# =====================================================
# BLOQUE 2 · CUENTA DE RESULTADOS
# =====================================================

st.subheader("Estructura contable")

def fila_concepto(concepto, importe):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write(concepto)
    with c2:
        st.write(f"{importe:,.2f} €")

# Ingresos
st.markdown("**Ingresos**")
fila_concepto("Ventas netas", ventas_total)

st.divider()

# COGS
st.markdown("**Coste de ventas (COGS)**")
fila_concepto("Compras de producto", -compras_producto)
fila_concepto("Variación de inventario", inventario_var)
fila_concepto("Margen bruto", margen_bruto)

st.divider()

# Personal
st.markdown("**Gastos de personal**")
fila_concepto("Coste de personal", -coste_personal)

st.divider()

# Gastos operativos
st.markdown("**Gastos operativos**")

for categoria, importe in gastos_por_categoria.items():
    fila_concepto(categoria, -importe)

st.divider()

# EBITDA final
st.subheader("EBITDA")
fila_concepto("Resultado operativo (EBITDA)", ebitda)

st.divider()

# =====================================================
# BLOQUE 3 · LECTURA OYKEN
# =====================================================

st.subheader("Lectura del periodo")

if ventas_total > 0:
    margen_pct = margen_bruto / ventas_total * 100
    personal_pct = coste_personal / ventas_total * 100
    ebitda_pct = ebitda / ventas_total * 100

    st.write(f"- Margen bruto del {margen_pct:.1f} %.")
    st.write(f"- Coste de personal del {personal_pct:.1f} % sobre ventas.")
    st.write(f"- EBITDA del {ebitda_pct:.1f} % sobre ventas.")
else:
    st.write("- No hay ventas suficientes para lectura.")

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.caption(
    "Datos consolidados desde Ventas · Compras · Inventario · Gastos · RRHH"
)
