import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="OIKEN · Tendencias",
    layout="centered"
)

st.title("OIKEN · Tendencias")
st.caption("Estructura, estabilidad y robustez del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

hoy = df["fecha"].max()

# =========================
# UTILIDADES
# =========================
def rango_fechas(df):
    return f"{df['fecha'].min().strftime('%d/%m')} – {df['fecha'].max().strftime('%d/%m')}"

# Detección simple de modo móvil (placeholder)
is_mobile = st.session_state.get("is_mobile", False)

# =========================
# VARIABLES BASE
# =========================
df["tickets_total"] = (
    df["tickets_manana"] +
    df["tickets_tarde"] +
    df["tickets_noche"]
)

df["ticket_medio"] = np.where(
    df["tickets_total"] > 0,
    df["ventas_total_eur"] / df["tickets_total"],
    np.nan
)

# =========================
# VENTANAS TEMPORALES
# =========================
lunes_semana = hoy - pd.Timedelta(days=hoy.weekday())
df_semana = df[(df["fecha"] >= lunes_semana) & (df["fecha"] <= hoy)]

df_7  = df.tail(7)
df_10 = df.tail(10)
df_15 = df.tail(15)

# =========================
# IMPORTS CORE
# =========================
from oiken.core.oiken_core_wrappers import (
    core_direccion_negocio,
    core_consistencia_resultado,
    core_dias_fuertes,
    core_estabilidad_ticket,
    core_volatilidad_turnos,
    core_dependencia_picos
)

# =========================
# RENDER UNIFICADO
# =========================
def render_core_block(
    title: str,
    core: dict,
    main_metric_label: str,
    main_metric_value: str,
    period: str,
):
    st.subheader(title.upper())

    # Estado arriba en móvil
    if is_mobile:
        st.caption(f"Estado: {core['assessment']['state']}")

    # Métrica principal
    st.markdown(f"**{main_metric_label.upper()}**")
    st.markdown(f"### {main_metric_value}")

    # Periodo
    st.caption(f"Periodo analizado: {period}")

    # Texto Core
    st.markdown(core["narrative"]["text"])

    # Estado abajo en desktop
    if not is_mobile:
        st.caption(
            f"Estado estructural: {core['assessment']['state']} · "
            f"Severidad: {core['assessment']['severity']}"
        )
    else:
        st.caption(f"Severidad: {core['assessment']['severity']}")

    st.divider()

# =========================
# 1 · DIRECCIÓN DEL NEGOCIO
# =========================
if len(df_semana) >= 5:
    mm_actual = df_semana["ventas_total_eur"].mean()
    prev = df[df["fecha"] < lunes_semana].tail(len(df_semana))

    if len(prev) >= len(df_semana):
        mm_prev = prev["ventas_total_eur"].mean()
        var_mm = ((mm_actual - mm_prev) / mm_prev * 100) if mm_prev > 0 else 0
    else:
        var_mm = 0

    metrics = {
        "mean_current": mm_actual,
        "variation_pct": var_mm,
        "window_days": len(df_semana)
    }

    core = core_direccion_negocio(metrics)

    render_core_block(
        title="Dirección del negocio",
        core=core,
        main_metric_label="Media diaria",
        main_metric_value=f"{mm_actual:,.0f} €",
        period=rango_fechas(df_semana)
    )

# =========================
# 2 · CONSISTENCIA DEL RESULTADO
# =========================
if len(df_7) >= 7:
    cv_ventas = df_7["ventas_total_eur"].std() / df_7["ventas_total_eur"].mean() * 100

    metrics = {
        "cv_pct": cv_ventas,
        "window_days": 7
    }

    core = core_consistencia_resultado(metrics)

    render_core_block(
        title="Consistencia del resultado",
        core=core,
        main_metric_label="Coeficiente de variación",
        main_metric_value=f"{cv_ventas:.1f} %",
        period=rango_fechas(df_7)
    )

# =========================
# 3 · DÍAS FUERTES Y DÉBILES
# =========================
if len(df_15) >= 15:
    df_15 = df_15.copy()
    df_15["weekday"] = df_15["fecha"].dt.day_name()
    media_dia = df_15.groupby("weekday")["ventas_total_eur"].mean()
    media_global = df_15["ventas_total_eur"].mean()

    metrics = {
        "dia_fuerte": media_dia.idxmax(),
        "dia_debil": media_dia.idxmin(),
        "diff_fuerte_pct": (media_dia.max()/media_global - 1) * 100,
        "diff_debil_pct": (media_dia.min()/media_global - 1) * 100,
        "window_days": 15
    }

    core = core_dias_fuertes(metrics)

    render_core_block(
        title="Días fuertes y días débiles",
        core=core,
        main_metric_label="Día más fuerte / débil",
        main_metric_value=f"{metrics['dia_fuerte']} / {metrics['dia_debil']}",
        period=rango_fechas(df_15)
    )

# =========================
# 4 · ESTABILIDAD DEL TICKET MEDIO
# =========================
if len(df_7) >= 7:
    cv_ticket = df_7["ticket_medio"].std() / df_7["ticket_medio"].mean() * 100

    metrics = {
        "cv_pct": cv_ticket,
        "window_days": 7
    }

    core = core_estabilidad_ticket(metrics)

    render_core_block(
        title="Estabilidad del ticket medio",
        core=core,
        main_metric_label="CV ticket medio",
        main_metric_value=f"{cv_ticket:.1f} %",
        period=rango_fechas(df_7)
    )

# =========================
# 5 · VOLATILIDAD POR TURNOS
# =========================
def cv_turno(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm) / np.nanmean(tm) * 100

if len(df_7) >= 7:
    tabla_turnos = [
        {"Turno": "Mañana", "CV Ticket (%)": cv_turno(df_7["ventas_manana_eur"], df_7["tickets_manana"])},
        {"Turno": "Tarde",  "CV Ticket (%)": cv_turno(df_7["ventas_tarde_eur"], df_7["tickets_tarde"])},
        {"Turno": "Noche",  "CV Ticket (%)": cv_turno(df_7["ventas_noche_eur"], df_7["tickets_noche"])},
    ]

    metrics = {
        "tabla_cv": tabla_turnos,
        "window_days": 7
    }

    core = core_volatilidad_turnos(metrics)

    if not is_mobile:
        st.table(pd.DataFrame(tabla_turnos))

    render_core_block(
        title="Volatilidad por turnos",
        core=core,
        main_metric_label="Turno más volátil",
        main_metric_value=max(tabla_turnos, key=lambda x: x["CV Ticket (%)"])["Turno"],
        period=rango_fechas(df_7)
    )

# =========================
# 6 · DEPENDENCIA DE PICOS
# =========================
if len(df_10) >= 10:
    media = df_10["ventas_total_eur"].mean()
    desv = df_10["ventas_total_eur"].std()

    picos = df_10[df_10["ventas_total_eur"] > media + 2 * desv]
    pct_picos = picos["ventas_total_eur"].sum() / df_10["ventas_total_eur"].sum() * 100

    metrics = {
        "pct_picos": pct_picos,
        "window_days": 10
    }

    core = core_dependencia_picos(metrics)

    render_core_block(
        title="Dependencia de picos",
        core=core,
        main_metric_label="Ventas en días excepcionales",
        main_metric_value=f"{pct_picos:.1f} %",
        period=rango_fechas(df_10)
    )

# =========================
# NOTA FINAL
# =========================
st.caption(
    "Este módulo analiza tendencias estructurales del negocio. "
    "La lectura se prioriza sobre criterios de calidad operativa."
)
