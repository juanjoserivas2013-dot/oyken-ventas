import streamlit as st

st.set_page_config(page_title="OYKEN · Calidad Operativa", layout="centered")

st.title("OYKEN · Calidad Operativa")
st.caption("Salud y estabilidad del sistema")

st.divider()

st.subheader("ESTADÍSTICAS DE CALIDAD OPERATIVA")
st.markdown("_Bloque avanzado_")

st.markdown("""
Estas conectan con **gestión real**:

- **Estabilidad del ticket medio**
- **Volatilidad por turno**
- **Dependencia de promociones**
- **Impacto de observaciones** (clima, eventos)
""")

st.info("Terreno natural de **Oyken Core**.")
