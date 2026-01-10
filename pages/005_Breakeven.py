import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CABECERA
# =====================================================
st.subheader("OYKEN · Breakeven operativo")
st.caption(
    "Cálculo del punto de equilibrio a partir del margen bruto "
    "y de los costes fijos estructurales del negocio."
)

st.divider()

# =====================================================
# SELECTOR TEMPORAL (GOBIERNA TODO)
# =====================================================
c1, c2 = st.columns(2)

with c1:
    anio_sel = st.selectbox(
        "Año",
        options=[2024, 2025, 2026],
        index=1
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        format_func=lambda x: "Todos los meses" if x == 0 else x
    )

# =====================================================
# MARGEN BRUTO
# Fuente: Compras · Coste de producto sobre ventas
# =====================================================
st.divider()
st.markdown("### Margen bruto")

MARGEN_FILE = Path("coste_producto_pct.csv")
margen_bruto = None

if MARGEN_FILE.exists():
    df_margen = pd.read_csv(MARGEN_FILE)

    fila = df_margen[
        (df_margen["anio"] == anio_sel) &
        ((df_margen["mes"] == mes_sel) if mes_sel != 0 else True)
    ]

    if not fila.empty:
        pct_coste = fila.iloc[-1]["coste_producto_pct"]
        margen_bruto = round(1 - pct_coste, 4)

if margen_bruto is None or margen_bruto <= 0:
    st.warning("No hay margen bruto válido para el período seleccionado.")
    st.stop()

st.metric("Margen bruto operativo", f"{margen_bruto:.2%}")

# =====================================================
# COSTES FIJOS ESTRUCTURALES
# =====================================================
st.divider()
st.markdown("### Costes fijos estructurales")

# -----------------------------------------------------
# RRHH · FUENTE CANÓNICA
# -----------------------------------------------------
RRHH_MENSUAL_FILE = Path("rrhh_mensual.csv")
coste_rrhh = 0.0

if RRHH_MENSUAL_FILE.exists():
    df_rrhh = pd.read_csv(RRHH_MENSUAL_FILE)

    df_rrhh_filtrado = df_rrhh[
        (df_rrhh["anio"] == anio_sel) &
        ((df_rrhh["mes"] == mes_sel) if mes_sel != 0 else True)
    ]

    if not df_rrhh_filtrado.empty:
        coste_rrhh = df_rrhh_filtrado["rrhh_total_eur"].sum()

# -----------------------------------------------------
# GASTOS FIJOS ESTRUCTURALES
# -----------------------------------------------------
GASTOS_FILE = Path("gastos.csv")
coste_gastos_fijos = 0.0
detalle_gastos = []

if GASTOS_FILE.exists():
    df_gastos = pd.read_csv(GASTOS_FILE)

    df_gastos["Fecha"] = pd.to_datetime(
        df_gastos["Fecha"],
        dayfirst=True,
        errors="coerce"
    )

    df_gastos = df_gastos[
        df_gastos["Fecha"].dt.year == anio_sel
    ]

    if mes_sel != 0:
        df_gastos = df_gastos[
            df_gastos["Fecha"].dt.month == mes_sel
        ]

    # Aquí asumimos que la clasificación estructural
    # ya está correctamente definida en el módulo Gastos
    df_fijos = df_gastos[
        df_gastos["Tipo"] == "Fijo"
    ] if "Tipo" in df_gastos.columns else df_gastos

    coste_gastos_fijos = df_fijos["Coste (€)"].sum()

    detalle_gastos = (
        df_fijos
        .groupby("Categoria")["Coste (€)"]
        .sum()
        .reset_index()
    )

# -----------------------------------------------------
# TOTAL COSTES FIJOS
# -----------------------------------------------------
total_costes_fijos = coste_rrhh + coste_gastos_fijos

st.metric(
    "Total costes fijos",
    f"{total_costes_fijos:,.2f} €",
    help="Incluye RRHH + gastos fijos estructurales"
)

# -----------------------------------------------------
# DESGLOSE
# -----------------------------------------------------
st.markdown("#### Desglose de costes fijos")

desglose = [
    {"Concepto": "Recursos Humanos", "Coste (€)": round(coste_rrhh, 2)}
]

for _, row in detalle_gastos.iterrows():
    desglose.append({
        "Concepto": row["Categoria"],
        "Coste (€)": round(row["Coste (€)"], 2)
    })

df_desglose = pd.DataFrame(desglose)

st.dataframe(
    df_desglose,
    hide_index=True,
    use_container_width=True
)

# =====================================================
# PUNTO DE EQUILIBRIO
# =====================================================
st.divider()
st.markdown("### Punto de equilibrio")

breakeven = total_costes_fijos / margen_bruto

st.metric(
    "Breakeven (sin IVA)",
    f"{breakeven:,.2f} €"
)

st.caption(
    "Facturación mínima necesaria para cubrir la estructura fija del negocio."
)
