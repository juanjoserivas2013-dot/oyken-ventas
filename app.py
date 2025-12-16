import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")

st.title("OYKEN · Control Operativo")
st.markdown("**Entra en Oyken. En 30 segundos entiendes mejor tu negocio.**")
st.caption("Sistema automático basado en criterio operativo")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

COLUMNAS = [
    "fecha",
    "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur", "ventas_total_eur",
    "comensales_manana", "comensales_tarde", "comensales_noche",
    "tickets_manana", "tickets_tarde", "tickets_noche",
    "observaciones"
]

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = 0 if col not in ["fecha", "observaciones"] else ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    st.markdown("**Ventas (€)**")
    v1, v2, v3 = st.columns(3)
    with v1:
        vm = st.number_input("Mañana", min_value=0.0, step=10.0)
    with v2:
        vt = st.number_input("Tarde", min_value=0.0, step=10.0)
    with v3:
        vn = st.number_input("Noche", min_value=0.0, step=10.0)

    st.markdown("**Comensales**")
    c1, c2, c3 = st.columns(3)
    with c1:
        cm = st.number_input("Mañana ", min_value=0, step=1)
    with c2:
        ct = st.number_input("Tarde ", min_value=0, step=1)
    with c3:
        cn = st.number_input("Noche ", min_value=0, step=1)

    st.markdown("**Tickets**")
    t1, t2, t3 = st.columns(3)
    with t1:
        tm = st.number_input("Mañana  ", min_value=0, step=1)
    with t2:
        tt = st.number_input("Tarde  ", min_value=0, step=1)
    with t3:
        tn = st.number_input("Noche  ", min_value=0, step=1)

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Clima, eventos, incidencias, promociones, obras, festivos…",
        height=100
    )

    guardar = st.form_submit_button("Guardar venta")

if guardar:
    total = vm + vt + vn

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total,
        "comensales_manana": cm,
        "comensales_tarde": ct,
        "comensales_noche": cn,
        "tickets_manana": tm,
        "tickets_tarde": tt,
        "tickets_noche": tn,
        "observaciones": observaciones.strip()
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)
    st.success("Venta guardada correctamente")
    st.rerun()

if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN ISO (REGLA CORRECTA GRANDES CADENAS)
# =========================
df = df.sort_values("fecha")
iso = df["fecha"].dt.isocalendar()
df["iso_year"] = iso.year
df["iso_week"] = iso.week
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

# =========================
# BLOQUE HOY
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())

venta_hoy = df[df["fecha"] == fecha_hoy]

# --- Inicialización segura ---
vm_h = vt_h = vn_h = total_h = 0.0
cm_h = ct_h = cn_h = 0
tm_h = tt_h = tn_h = 0
hay_dato_hoy = False

# --- Si existe registro hoy, se cargan valores reales ---
if not venta_hoy.empty:
    fila = venta_hoy.iloc[0]
    hay_dato_hoy = True

    vm_h = fila["ventas_manana_eur"]
    vt_h = fila["ventas_tarde_eur"]
    vn_h = fila["ventas_noche_eur"]
    total_h = fila["ventas_total_eur"]

    cm_h = fila["comensales_manana"]
    ct_h = fila["comensales_tarde"]
    cn_h = fila["comensales_noche"]

    tm_h = fila["tickets_manana"]
    tt_h = fila["tickets_tarde"]
    tn_h = fila["tickets_noche"]

# =========================
# VISUAL HOY
# =========================
st.markdown("**HOY**")
st.caption(f"{DOW_ES[fecha_hoy.weekday()]} · {fecha_hoy.strftime('%d/%m/%Y')}")

if not hay_dato_hoy:
    st.info("Sin datos registrados hoy")
else:
    # MAÑANA
    st.write("**Mañana**")
    st.write(f"{vm_h:,.2f} €")
    st.caption(f"{cm_h} comensales · {tm_h} tickets")

    # TARDE
    st.write("**Tarde**")
    st.write(f"{vt_h:,.2f} €")
    st.caption(f"{ct_h} comensales · {tt_h} tickets")

    # NOCHE
    st.write("**Noche**")
    st.write(f"{vn_h:,.2f} €")
    st.caption(f"{cn_h} comensales · {tn_h} tickets")

    st.markdown("---")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")


# =========================
# BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[
    (df["fecha"].dt.month == fecha_hoy.month) &
    (df["fecha"].dt.year == fecha_hoy.year)
].copy()

df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️" if r["observaciones"].strip() else r["fecha_display"],
    axis=1
)

st.dataframe(
    df_mes[[
        "fecha_display", "dow",
        "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur",
        "ventas_total_eur",
        "comensales_manana", "comensales_tarde", "comensales_noche",
        "tickets_manana", "tickets_tarde", "tickets_noche",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
)
