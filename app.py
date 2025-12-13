import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from io import BytesIO

st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")

DATA_FILE = Path("ventas.csv")

# --- Cargar datos ---
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
# REGISTRO / EDICIÓN DIARIA
# =========================
st.subheader("Registro / Edición diaria")

fecha_sel = st.date_input("Fecha", value=date.today())

row = df[df["fecha"].dt.date == fecha_sel]
vm0 = float(row["ventas_manana_eur"].iloc[0]) if not row.empty else 0.0
vt0 = float(row["ventas_tarde_eur"].iloc[0]) if not row.empty else 0.0
vn0 = float(row["ventas_noche_eur"].iloc[0]) if not row.empty else 0.0
tot0 = float(row["ventas_total_eur"].iloc[0]) if not row.empty else 0.0

with st.form("form_editar"):
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f", value=vm0)
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f", value=vt0)
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f", value=vn0)

    total_manual = st.number_input("Total del día (€)", min_value=0.0, step=10.0, format="%.2f", value=tot0)
    guardar = st.form_submit_button("Guardar cambios")

if guardar:
    total_calc = vm + vt + vn
    ventas_total = total_calc if total_calc > 0 else total_manual
    df = df[df["fecha"].dt.date != fecha_sel]
    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha_sel),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": ventas_total
    }])
    df = pd.concat([df, nueva], ignore_index=True).sort_values("fecha")
    df.to_csv(DATA_FILE, index=False)
    st.success("Día guardado correctamente")

st.divider()

# =========================
# VISTA MENSUAL + EXPORT
# =========================
st.subheader("Vista mensual")

if not df.empty:
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dow"] = df["fecha"].dt.day_name(locale="es_ES")

    col1, col2 = st.columns(2)
    with col1:
        años = sorted(df["año"].unique())
        año_sel = st.selectbox("Año", años, index=len(años)-1)
    with col2:
        mes_sel = st.selectbox(
            "Mes",
            list(range(1,13)),
            format_func=lambda m: ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                                    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1]
        )

    mensual = (
        df[(df["año"] == año_sel) & (df["mes"] == mes_sel)]
        .sort_values("fecha")
        [["fecha","dow","ventas_manana_eur","ventas_tarde_eur","ventas_noche_eur","ventas_total_eur"]]
    )

    st.dataframe(mensual, use_container_width=True, hide_index=True)

    # --- Export mensual ---
    def export_mensual(dfm):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dfm.to_excel(writer, sheet_name="Datos", index=False)
            resumen = pd.DataFrame({
                "Métrica": ["Total mes", "Promedio diario"],
                "Valor (€)": [dfm["ventas_total_eur"].sum(), dfm["ventas_total_eur"].mean()]
            })
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
        return output.getvalue()

    st.download_button(
        "Descargar Excel del mes",
        data=export_mensual(mensual),
        file_name=f"oyken_ventas_{año_sel}_{mes_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Aún no hay datos.")

st.divider()

# =========================
# VISTA SEMANAL + EXPORT
# =========================
st.subheader("Vista semanal")

if not df.empty:
    ref = st.date_input("Semana que contiene", value=date.today(), key="week_ref")
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)

    semanal = (
        df[(df["fecha"] >= pd.to_datetime(monday)) & (df["fecha"] <= pd.to_datetime(sunday))]
        .sort_values("fecha")
        [["fecha","ventas_manana_eur","ventas_tarde_eur","ventas_noche_eur","ventas_total_eur"]]
    )

    st.dataframe(semanal, use_container_width=True, hide_index=True)

    def export_semanal(dfs):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dfs.to_excel(writer, sheet_name="Datos", index=False)
            resumen = pd.DataFrame({
                "Métrica": ["Total semana", "Promedio diario"],
                "Valor (€)": [dfs["ventas_total_eur"].sum(), dfs["ventas_total_eur"].mean()]
            })
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
        return output.getvalue()

    st.download_button(
        "Descargar Excel de la semana",
        data=export_semanal(semanal),
        file_name=f"oyken_ventas_semana_{monday}_{sunday}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Aún no hay datos.")
