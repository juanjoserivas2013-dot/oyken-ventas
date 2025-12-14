import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")
st.caption("Control operativo diario · Lectura inmediata")

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
    fecha = st.date_input(
        "Fecha (dd/mm/aaaa)",
        value=date.today(),
        min_value=date(2015, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY"
    )

    st.caption("Ventas por turno (€)")
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana", min_value=0.0, step=10.0, format="%.2f")
    with c2:
        vt = st.number_input("Tarde", min_value=0.0, step=10.0, format="%.2f")
    with c3:
        vn = st.number_input("Noche", min_value=0.0, step=10.0, format="%.2f")

    total = vm + vt + vn
    st.metric("Total del día (€)", f"{total:,.2f}")

    guardar = st.form_submit_button("Guardar")

if guardar:
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df = df.sort_values("fecha")
    df.to_csv(DATA_FILE, index=False)

    st.success(f"Venta guardada ({fecha.strftime('%d/%m/%Y')})")
    st.rerun()

st.divider()

# =========================
# LISTADO DE VENTAS
# =========================
st.subheader("Listado de ventas")

if df.empty:
    st.info("Aún no hay ventas registradas.")
else:
    df_listado = df.sort_values("fecha", ascending=False).copy()
    df_listado["Fecha"] = df_listado["fecha"].dt.strftime("%d/%m/%Y")
    df_listado["Día"] = df_listado["fecha"].dt.day_name()

    st.dataframe(
        df_listado[[
            "Fecha",
            "Día",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur"
        ]].rename(columns={
            "ventas_manana_eur": "Mañana (€)",
            "ventas_tarde_eur": "Tarde (€)",
            "ventas_noche_eur": "Noche (€)",
            "ventas_total_eur": "Total (€)"
        }),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# =========================
# RESUMEN MENSUAL (AUTOMÁTICO)
# =========================
st.subheader("Resumen mensual · Acumulado vs mes anterior")

if not df.empty:
    fecha_ref = df["fecha"].max()
    mes_actual = fecha_ref.month
    año_actual = fecha_ref.year

    if mes_actual == 1:
        mes_anterior = 12
        año_anterior = año_actual - 1
    else:
        mes_anterior = mes_actual - 1
        año_anterior = año_actual

    df_mes_actual = df[
        (df["fecha"].dt.year == año_actual) &
        (df["fecha"].dt.month == mes_actual)
    ]

    df_mes_anterior = df[
        (df["fecha"].dt.year == año_anterior) &
        (df["fecha"].dt.month == mes_anterior)
    ]

    total_actual = df_mes_actual["ventas_total_eur"].sum()
    dias_actual = df_mes_actual["fecha"].nunique()
    prom_actual = total_actual / dias_actual if dias_actual > 0 else 0

    total_anterior = df_mes_anterior["ventas_total_eur"].sum()
    dias_anterior = df_mes_anterior["fecha"].nunique()
    prom_anterior = total_anterior / dias_anterior if dias_anterior > 0 else 0

    dif_eur = total_actual - total_anterior
    dif_pct = (dif_eur / total_anterior * 100) if total_anterior > 0 else 0

    meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"**Mes actual · {meses[mes_actual-1]} {año_actual}**")
        st.write(f"Total acumulado: **{total_actual:,.2f} €**")
        st.write(f"Días con venta: {dias_actual}")
        st.write(f"Promedio diario: {prom_actual:,.2f} €")

    with c2:
        st.markdown(f"**Mes anterior · {meses[mes_anterior-1]} {año_anterior}**")
        st.write(f"Total mes: **{total_anterior:,.2f} €**")
        st.write(f"Días con venta: {dias_anterior}")
        st.write(f"Promedio diario: {prom_anterior:,.2f} €")

    with c3:
        st.markdown("**Diferencia**")
        st.metric("€ vs mes anterior", f"{dif_eur:+,.2f} €", f"{dif_pct:+.1f} %")

st.divider()

# =========================
# COMPARABLE AUTOMÁTICO POR DOW
# =========================
st.subheader("Lectura automática · Comparativa por día de la semana")

if not df.empty:
    fecha_actual = df["fecha"].max()
    dow_actual = fecha_actual.weekday()

    actual = df[df["fecha"] == fecha_actual].iloc[0]
    fecha_objetivo = fecha_actual.replace(year=fecha_actual.year - 1)

    candidatos = df[
        (df["fecha"].dt.year == fecha_objetivo.year) &
        (df["fecha"].dt.weekday == dow_actual)
    ].copy()

    if not candidatos.empty:
        candidatos["dist"] = (candidatos["fecha"] - fecha_objetivo).abs()
        comparable = candidatos.sort_values("dist").iloc[0]
    else:
        comparable = None

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Día actual**")
        st.write(f"Fecha: {fecha_actual.strftime('%d/%m/%Y')}")
        st.write(f"Total: {actual['ventas_total_eur']:.2f} €")

    with c2:
        st.markdown("**Mismo DOW · Año anterior**")
        if comparable is None:
            st.warning("No existe histórico comparable.")
        else:
            st.write(f"Fecha: {comparable['fecha'].strftime('%d/%m/%Y')}")
            st.write(f"Total: {comparable['ventas_total_eur']:.2f} €")

    with c3:
        st.markdown("**Variación**")
        if comparable is None:
            st.info("Sin base histórica suficiente.")
        else:
            dif = actual["ventas_total_eur"] - comparable["ventas_total_eur"]
            pct = (dif / comparable["ventas_total_eur"] * 100) if comparable["ventas_total_eur"] > 0 else 0
            st.metric("Total", f"{dif:+.2f} €", f"{pct:+.1f} %")
