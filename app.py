import streamlit as st

st.set_page_config(
    page_title="OYKEN",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.sidebar.title("OYKEN")

dominio = st.sidebar.selectbox(
    "Dominio",
    ["Inicio", "Ventas"]
)

st.title("OYKEN")
st.caption("Sistema operativo de gestión")

if dominio == "Inicio":
    st.markdown("Selecciona un dominio en el menú lateral")

elif dominio == "Ventas":

    submodulo = st.sidebar.radio(
        "Ventas",
        [
            "Control Operativo",
            "Tendencias",
            "Comparables",
            "Comportamiento"
        ]
    )

    if submodulo == "Control Operativo":
        from ventas_control import ventas_control_page
        ventas_control_page()

    elif submodulo == "Tendencias":
        from ventas_tendencias import ventas_tendencias_page
        ventas_tendencias_page()

    elif submodulo == "Comparables":
        from ventas_comparables import ventas_comparables_page
        ventas_comparables_page()

    elif submodulo == "Comportamiento":
        from ventas_comportamiento import ventas_comportamiento_page
        ventas_comportamiento_page()

