import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="OYKEN · Ventas",
    layout="centered"
)

st.title("OYKEN · Ventas")
st.caption("Registro diario de ventas · Prototipo privado")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=[
        "fecha",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
    ])

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input("Fecha", value=date.today())

    st.caption("Desglose por franja (€)")
    col1, col2, col3 = st.columns(3)

    with col1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f")
    with col2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f")
    with col3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f")

    # Total automático
    ventas_total = vm + vt + vn
    st.caption("Total del día (automático)")
    st.number_input(
        "Total (€)",
        value=ventas_total,
        disabled=True,
        format="%.2f"
    )

    guardar = st.form_submit_button("Guardar")

# =========================
# GUARDADO
# =========================
if guardar:
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": ventas_total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Venta guardada correctamente")
    st.rerun()

st.divider()

# =========================
# VISTA MENSUAL
# =========================
st.subheader("Vista mensual")

if df.empty:
    st.info("Aún no hay datos registrados.")
else:
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day

    # Día de la semana SIN locale (estable en Streamlit Cloud)
    dias_es = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    df["dow"] = df["fecha"].dt.day_name().map(dias_es)

    col1, col2 = st.columns(2)

    with col1:
        años = sorted(df["año"].unique())
        año_sel = st.selectbox("Año", años, index=len(años)-1)

    with col2:
        mes_sel = st.selectbox(
            "Mes",
            list(range(1, 13)),
            format_func=lambda m: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][m - 1]
        )

    mensual = (
        df[(df["año"] == año_sel) & (df["mes"] == mes_sel)]
        .sort_values("fecha")
        [[
            "fecha",
            "dia",
            "dow",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur"
        ]]
    )

    st.dataframe(mensual, use_container_width=True, hide_index=True)

    # =========================
    # TOTALES
    # =========================
    tot_m = mensual["ventas_manana_eur"].sum()
    tot_t = mensual["ventas_tarde_eur"].sum()
    tot_n = mensual["ventas_noche_eur"].sum()
    tot_mes = mensual["ventas_total_eur"].sum()
    prom = mensual["ventas_total_eur"].mean() if not mensual.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total mes (€)", f"{tot_mes:,.2f}")
    c2.metric("Promedio diario (€)", f"{prom:,.2f}")
    c3.metric("Mañana (€)", f"{tot_m:,.2f}")
    c4.metric("Tarde (€)", f"{tot_t:,.2f}")
    c5.metric("Noche (€)", f"{tot_n:,.2f}")
    st.divider()
st.subheader("Comparable diario · Mismo día año anterior")

if df.empty:
    st.info("Aún no hay datos suficientes para comparaciones.")
else:
    # Fecha por defecto: último día con datos
    fecha_base = df["fecha"].max().date()

    fecha_sel = st.date_input(
        "Selecciona el día a analizar",
        value=fecha_base,
        key="fecha_comparable"
    )

    fecha_actual = pd.to_datetime(fecha_sel)
    fecha_anterior = fecha_actual.replace(year=fecha_actual.year - 1)

    # Datos día actual
    actual = df[df["fecha"] == fecha_actual]
    anterior = df[df["fecha"] == fecha_anterior]

    col_a, col_b, col_c = st.columns(3)

    # =========================
    # BLOQUE A · DÍA ACTUAL
    # =========================
    with col_a:
        st.markdown("**Día actual**")

        if actual.empty:
            st.warning("No hay datos para este día.")
        else:
            r = actual.iloc[0]
            st.write(f"Fecha: {fecha_actual.date()}")
            st.write(f"Mañana: {r['ventas_manana_eur']:.2f} €")
            st.write(f"Tarde: {r['ventas_tarde_eur']:.2f} €")
            st.write(f"Noche: {r['ventas_noche_eur']:.2f} €")
            st.write(f"**Total: {r['ventas_total_eur']:.2f} €**")

    # =========================
    # BLOQUE B · AÑO ANTERIOR
    # =========================
    with col_b:
        st.markdown("**Mismo día · Año anterior**")

        if anterior.empty:
            st.warning("No existe histórico comparable.")
        else:
            r_prev = anterior.iloc[0]
            st.write(f"Fecha: {fecha_anterior.date()}")
            st.write(f"Mañana: {r_prev['ventas_manana_eur']:.2f} €")
            st.write(f"Tarde: {r_prev['ventas_tarde_eur']:.2f} €")
            st.write(f"Noche: {r_prev['ventas_noche_eur']:.2f} €")
            st.write(f"**Total: {r_prev['ventas_total_eur']:.2f} €**")

    # =========================
    # BLOQUE C · VARIACIÓN
    # =========================
    with col_c:
        st.markdown("**Variación**")

        if actual.empty or anterior.empty:
            st.info("No se puede calcular variación.")
        else:
            dif_total = r["ventas_total_eur"] - r_prev["ventas_total_eur"]
            dif_pct = (dif_total / r_prev["ventas_total_eur"] * 100) if r_prev["ventas_total_eur"] > 0 else 0

            st.metric(
                "Total (€)",
                f"{dif_total:+.2f} €",
                f"{dif_pct:+.1f} %"
            )

            st.write("**Por franja:**")

            for franja in ["manana", "tarde", "noche"]:
                act = r[f"ventas_{franja}_eur"]
                prev = r_prev[f"ventas_{franja}_eur"]
                dif = act - prev
                pct = (dif / prev * 100) if prev > 0 else 0

                st.write(
                    f"{franja.capitalize()}: "
                    f"{dif:+.2f} € ({pct:+.1f} %)"
                )

