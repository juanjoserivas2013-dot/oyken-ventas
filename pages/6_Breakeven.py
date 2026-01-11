# =====================================================
# MARGEN BRUTO (DESDE COMPRAS + VENTAS)
# =====================================================

COMPRAS_MENSUALES_FILE = Path("compras_mensuales.csv")
VENTAS_MENSUALES_FILE = Path("ventas_mensuales.csv")

# ---------- Validaciones ----------
if not COMPRAS_MENSUALES_FILE.exists():
    st.error("No existen datos de Compras mensuales.")
    st.stop()

if not VENTAS_MENSUALES_FILE.exists():
    st.error("No existen datos de Ventas mensuales.")
    st.stop()

# ---------- Cargar datos ----------
df_compras = pd.read_csv(COMPRAS_MENSUALES_FILE)
df_ventas = pd.read_csv(VENTAS_MENSUALES_FILE)

# ---------- Normalizar tipos (CRÍTICO) ----------
for df in (df_compras, df_ventas):
    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)

df_compras["compras_total_eur"] = pd.to_numeric(
    df_compras["compras_total_eur"], errors="coerce"
).fillna(0)

df_ventas["ventas_total_eur"] = pd.to_numeric(
    df_ventas["ventas_total_eur"], errors="coerce"
).fillna(0)

# ---------- Filtrar período ----------
row_compras = df_compras[
    (df_compras["anio"] == int(anio_sel)) &
    (df_compras["mes"] == int(mes_sel))
]

row_ventas = df_ventas[
    (df_ventas["anio"] == int(anio_sel)) &
    (df_ventas["mes"] == int(mes_sel))
]

# ---------- Validación semántica ----------
if row_compras.empty or row_ventas.empty:
    st.warning(
        "No hay datos suficientes de Compras o Ventas "
        "para el período seleccionado."
    )
    st.stop()

compras = float(row_compras.iloc[0]["compras_total_eur"])
ventas = float(row_ventas.iloc[0]["ventas_total_eur"])

if ventas <= 0:
    st.warning("Las ventas del período son 0 €. No se puede calcular margen.")
    st.stop()

# ---------- Cálculo estructural ----------
coste_producto_pct = compras / ventas
margen_bruto = 1 - coste_producto_pct

# ---------- Visualización ----------
st.markdown("### Margen bruto estructural")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Ventas (€)", f"{ventas:,.2f}")
with c2:
    st.metric("Compras (€)", f"{compras:,.2f}")
with c3:
    st.metric("Coste producto", f"{coste_producto_pct:.2%}")

st.metric("Margen bruto", f"{margen_bruto:.2%}")

st.caption(
    "Fuente: Compras y Ventas mensuales · "
    "Cálculo directo (sin CSV intermedio)"
)

st.divider()
