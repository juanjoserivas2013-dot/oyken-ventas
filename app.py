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
# BLOQUE HOY — DEFINITIVO
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

# --- Venta HOY ---
venta_hoy = df[df["fecha"] == fecha_hoy]

if venta_hoy.empty:
    vm_h = vt_h = vn_h = total_h = 0.0
    cm_h = ct_h = cn_h = 0
    tm_h = tt_h = tn_h = 0
else:
    fila = venta_hoy.iloc[0]
    vm_h = fila["ventas_manana_eur"]
    vt_h = fila["ventas_tarde_eur"]
    vn_h = fila["ventas_noche_eur"]
    total_h = fila["ventas_total_eur"]

    cm_h = fila.get("comensales_manana", 0)
    ct_h = fila.get("comensales_tarde", 0)
    cn_h = fila.get("comensales_noche", 0)

    tm_h = fila.get("tickets_manana", 0)
    tt_h = fila.get("tickets_tarde", 0)
    tn_h = fila.get("tickets_noche", 0)

# --- DOW año anterior (misma semana ISO, mismo weekday) ---
iso_week = fecha_hoy.isocalendar().week
iso_year = fecha_hoy.year - 1

cand = df[
    (df["fecha"].dt.isocalendar().week == iso_week) &
    (df["fecha"].dt.weekday == fecha_hoy.weekday()) &
    (df["año"] == iso_year)
]

if cand.empty:
    fecha_a_txt = "Sin histórico comparable"
    vm_a = vt_a = vn_a = total_a = 0.0
    cm_a = ct_a = cn_a = 0
    tm_a = tt_a = tn_a = 0
else:
    comp = cand.iloc[0]
    fecha_a_txt = f"{DOW_ES[comp['fecha'].weekday()]} · {comp['fecha'].strftime('%d/%m/%Y')}"

    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

    cm_a = comp.get("comensales_manana", 0)
    ct_a = comp.get("comensales_tarde", 0)
    cn_a = comp.get("comensales_noche", 0)

    tm_a = comp.get("tickets_manana", 0)
    tt_a = comp.get("tickets_tarde", 0)
    tn_a = comp.get("tickets_noche", 0)

# =========================
# FUNCIONES
# =========================
def diff_pct(a, b):
    diff = a - b
    pct = (diff / b * 100) if b > 0 else 0
    return diff, pct

def signo(v):
    if v > 0:
        return f"+{v}"
    if v < 0:
        return f"{v}"
    return "0"

def pct_txt(p):
    return f"(+{p:.1f}%)" if p > 0 else f"({p:.1f}%)"

def color(v):
    return "green" if v > 0 else "red" if v < 0 else "gray"

def icono(p):
    if p >= 30:
        return " 👁️"
    if p >= 1:
        return " ↑"
    if p <= -30:
        return " ⚠️"
    if p <= -1:
        return " ↓"
    return ""

# =========================
# VARIACIONES
# =========================
d_vm, p_vm = diff_pct(vm_h, vm_a)
d_vt, p_vt = diff_pct(vt_h, vt_a)
d_vn, p_vn = diff_pct(vn_h, vn_a)
d_tot, p_tot = diff_pct(total_h, total_a)

d_cm, p_cm = diff_pct(cm_h, cm_a)
d_ct, p_ct = diff_pct(ct_h, ct_a)
d_cn, p_cn = diff_pct(cn_h, cn_a)

d_tm, p_tm = diff_pct(tm_h, tm_a)
d_tt, p_tt = diff_pct(tt_h, tt_a)
d_tn, p_tn = diff_pct(tn_h, tn_a)

# =========================
# DISPOSICIÓN VISUAL
# =========================
c1, c2, c3 = st.columns(3)

# --- HOY ---
with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")

    st.markdown("**Mañana**")
    st.write(f"{vm_h:,.2f} €")
    st.caption(f"{cm_h} com · {tm_h} tickets")

    st.markdown("**Tarde**")
    st.write(f"{vt_h:,.2f} €")
    st.caption(f"{ct_h} com · {tt_h} tickets")

    st.markdown("**Noche**")
    st.write(f"{vn_h:,.2f} €")
    st.caption(f"{cn_h} com · {tn_h} tickets")

    st.markdown("---")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")

# --- DOW ---
with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)

    st.markdown("**Mañana**")
    st.write(f"{vm_a:,.2f} €")
    st.caption(f"{cm_a} com · {tm_a} tickets")

    st.markdown("**Tarde**")
    st.write(f"{vt_a:,.2f} €")
    st.caption(f"{ct_a} com · {tt_a} tickets")

    st.markdown("**Noche**")
    st.write(f"{vn_a:,.2f} €")
    st.caption(f"{cn_a} com · {tn_a} tickets")

    st.markdown("---")
    st.markdown(f"### TOTAL DOW\n{total_a:,.2f} €")

# --- VARIACIÓN ---
with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")

    st.markdown(
        f"**Mañana** "
        f"<span style='color:{color(d_vm)}'>"
        f"{signo(d_vm):} € {pct_txt(p_vm)}{icono(p_vm)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"Comensales: {signo(d_cm)} {pct_txt(p_cm)} · Tickets: {signo(d_tm)} {pct_txt(p_tm)}")

    st.markdown(
        f"**Tarde** "
        f"<span style='color:{color(d_vt)}'>"
        f"{signo(d_vt)} € {pct_txt(p_vt)}{icono(p_vt)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"Comensales: {signo(d_ct)} {pct_txt(p_ct)} · Tickets: {signo(d_tt)} {pct_txt(p_tt)}")

    st.markdown(
        f"**Noche** "
        f"<span style='color:{color(d_vn)}'>"
        f"{signo(d_vn)} € {pct_txt(p_vn)}{icono(p_vn)}</span>",
        unsafe_allow_html=True
    )
    st.caption(f"Comensales: {signo(d_cn)} {pct_txt(p_cn)} · Tickets: {signo(d_tn)} {pct_txt(p_tn)}")

    st.markdown("---")
    st.markdown(
        f"### TOTAL "
        f"<span style='color:{color(d_tot)}'>"
        f"{signo(d_tot)} € {pct_txt(p_tot)}</span>",
        unsafe_allow_html=True
    )

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
