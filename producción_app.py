import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from PIL import Image

# 1. Configuración de la página
try:
    icon = Image.open("Resources/mi_logo.png")  # Asegúrate de tener esta ruta
    st.set_page_config(page_title="Production Eng App", page_icon=icon, layout="wide")
except:
    st.set_page_config(page_title="Production Eng App", layout="wide")

# 2. Estilo personalizado (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    h1 {
        color: #1E3A8A;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Barra lateral y Logo
with st.sidebar:
    try:
        logo = Image.open("Resources/mi_logo.png")
        st.image(logo, use_container_width=True)
    except:
        st.info("Sube tu logo en la carpeta Resources")

    st.title("Navegación")
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Inicio", "Historial de Producción", "Potencial del Yacimiento",
                 "Análisis Nodal"],
        icons=["house", "graph-up", "droplet-half", "bezier2"],
        menu_icon="cast",
        default_index=0,
    )

# --- SECCIÓN: INICIO ---
if selected == "Inicio":
    st.title("Software para Ingeniería en Petróleo")
    st.subheader("Proyecto Segundo Parcial - Ingeniería de Producción")
    st.write("""
    Esta aplicación permite realizar análisis detallados de pozos del campo VOLVE, 
    cálculos de potencial de yacimiento y análisis nodal monofásico.
    """)
    st.info("Desarrollado con la metodología Scrum/Jira.")

# --- SECCIÓN: HISTORIAL DE PRODUCCIÓN ---
elif selected == "Historial de Producción":
    st.title("Historial de Producción - Campo VOLVE")
    uploaded_file = st.file_uploader("Cargar archivo Excel del campo VOLVE",
                                     type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())

        # Ejemplo de gráfico Qo vs t
        st.subheader("Gráfico de Producción de Petróleo (Qo vs t)")
        # Asumiendo que las columnas se llaman 'Fecha' y 'Qo'
        if 'Fecha' in df.columns and 'Qo' in df.columns:
            fig = px.line(df, x='Fecha', y='Qo',
                          title="Producción de Petróleo en el tiempo")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("El archivo debe contener las columnas 'Fecha' y 'Qo'")

# --- SECCIÓN: POTENCIAL DEL YACIMIENTO ---
elif selected == "Potencial del Yacimiento":
    st.title("Cálculos de Potencial (IPR)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos de Entrada")
        p_res = st.number_input("Presión del Yacimiento (Pr) [psi]", value=3000.0)
        p_wf = st.number_input("Presión de Fondo Fluyente (Pwf) [psi]", value=2000.0)
        q_test = st.number_input("Caudal de prueba (q) [bpd]", value=500.0)

    # Lógica simple de Índice de Productividad (J)
    if p_res > p_wf:
        j_index = q_test / (p_res - p_wf)
        aof = j_index * p_res

        with col2:
            st.subheader("Resultados")
            st.success(f"Índice de Productividad (J): {j_index:.2f} bpd/psi")
            st.success(f"Potencial Máximo (AOF): {aof:.2f} bpd")

        # Generar Curva IPR simple (Darcy)
        st.subheader("Curva IPR")
        pressures = [p for p in range(0, int(p_res) + 100, 100)]
        flow_rates = [j_index * (p_res - p) for p in pressures]

        fig_ipr = px.line(x=flow_rates, y=pressures,
                          labels={'x': 'Caudal (q)', 'y': 'Pwf'},
                          title="Curva IPR Lineal")
        fig_ipr.update_yaxes(
            autorange="reversed")  # Las presiones suelen ir de mayor a menor en el eje Y
        st.plotly_chart(fig_ipr)

# --- SECCIÓN: ANÁLISIS NODAL ---
elif selected == "Análisis Nodal":
    st.title("Análisis Nodal Monofásico")
    st.write(
        "Cálculo del punto de operación entre la oferta del yacimiento (IPR) y la demanda de la tubería (VLP).")
    # Aquí puedes añadir las fórmulas de flujo monofásico (Poettman-Carpenter, etc.)
    st.warning("Sección en desarrollo: Implementar curvas VLP aquí.")