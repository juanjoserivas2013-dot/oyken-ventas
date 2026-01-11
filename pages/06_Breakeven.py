import streamlit as st
import pandas as pd
from pathlib import Path

st.subheader("OYKEN · Breakeven Operativo")
st.caption("Punto de equilibrio básico del negocio")

st.divider()

# =====================================================
# ARCHIVOS CANÓNICOS
# =====================================================
COSTE_PRODUCTO_FILE = Path("coste_producto.csv")
RRHH_FILE = Path("rrhh_mensual.csv")

# =====================================================
# SELECTOR TEMPORAL LOCAL
# =====================================================
c1, c2 = st.columns(2)

with c1:
    anio_sel = st.number_input(
        "Año",
        min_value=2020,
        max_value=2100,
        value=2026
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=list(range(1, 13)),
        format_func=lambda x: [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

st.divider()

# =====================================================
# MARGEN BRUTO (DESDE COMPRAS)
# =====================================================
if not COSTE_PRODUCTO_FILE.exists():
    st.error("No existe el coste de producto.")
    st.stop()

df_cp = pd.read_csv(COSTE_PRODUCTO_FILE)

row_cp = df_cp[
    (df_cp["anio"] == anio_sel) &
    (df_cp["mes"] == mes_sel)
]

if row_cp.empty:
    st.warning("No hay coste de producto para el período seleccionado.")
    st.stop()

coste_producto_pct = float(row_cp.iloc[0]["coste_producto_pct"])
margen_bruto = 1 - coste_producto_pct

st.metric("Margen bruto", f"{margen_bruto:.2%}")

st.divider()

# =====================================================
# COSTES FIJOS · RRHH
# =====================================================
if not RRHH_FILE.exists():
    st.error("No existen datos de RRHH.")
    st.stop()

df_rrhh = pd.read_csv(RRHH_FILE)

row_rrhh = df_rrhh[
    (df_rrhh["anio"] == anio_sel) &
    (df_rrhh["mes"] == mes_sel)
]

if row_rrhh.empty:
    st.warning("No hay costes de RRHH para el período seleccionado.")
    st.stop()

coste_rrhh = float(row_rrhh.iloc[0]["rrhh_total_eur"])

st.metric("Coste RRHH", f"{coste_rrhh:,.2f} €")

st.divider()

# =====================================================
# BREAKEVEN
# =====================================================
breakeven = coste_rrhh / margen_bruto

st.markdown("### Punto de equilibrio operativo")

st.metric(
    "Breakeven (sin IVA)",
    f"{breakeven:,.2f} €"
)

st.caption(
    "Breakeven calculado solo con RRHH como coste fijo."
)

