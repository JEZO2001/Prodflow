import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from PIL import Image

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Producción App - Volve", layout="wide", page_icon="🛢️")

# Estilo CSS personalizado para mejorar la estética
st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# --- FUNCIONES MATEMÁTICAS ---
def j(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    if ef == 1:
        if pwf_test >= pb:
            return q_test / (pr - pwf_test)
        else:
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is None:
        if pwf_test >= pb:
            return q_test / (pr - pwf_test)
        else:
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1.8 * (1 - pwf_test / pb) - 0.8 * ef * (
                            1 - pwf_test / pb) ** 2))
    return q_test / (pr - pwf_test)


def Qb(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    return j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)


def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    productivity_index = j(q_test, pwf_test, pr, pb, ef, ef2)
    if pwf >= pb:
        return productivity_index * (pr - pwf)
    else:
        q_at_pb = Qb(q_test, pwf_test, pr, pb, ef, ef2)
        if ef == 1:
            return q_at_pb + ((productivity_index * pb) / 1.8) * (
                        1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)
        else:
            return q_at_pb + ((productivity_index * pb) / 1.8) * (
                        1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb) ** 2)


def aof(q_test, pwf_test, pr, pb, ef=1):
    return Qo(q_test, pwf_test, pr, 0, pb, ef)


# --- NAVEGACIÓN Y LOGO ---
with st.sidebar:
    # URL de ejemplo para LOGO (Puedes cambiarlo por una ruta local: "assets/logo.png")
    logo_url = "https://cdn-icons-png.flaticon.com/512/3017/3017158.png"
    st.image(logo_url, width=100)

    st.title("Producción App")
    selected = option_menu(
        "Menú Principal",
        ["Inicio", "Historial VOLVE", "Potencial Yacimiento", "Análisis Nodal"],
        icons=["house", "table", "graph-up", "bezier2"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#007bff", "font-size": "20px"},
            "nav-link-selected": {"background-color": "#007bff", "color": "white"},
        }
    )
    st.divider()
    st.info("**Usuario:** Ingeniero de Reservorios\n\n**Campo:** Volve (Mar del Norte)")

# --- SECCIÓN: INICIO ---
if selected == "Inicio":
    # Banner Principal (Puedes cambiar la URL por una imagen de un campo petrolero)
    banner_url = "https://images.unsplash.com/photo-1516192535944-07fb50221491?q=80&w=2000&auto=format&fit=crop"
    st.image(banner_url, use_container_width=True)

    st.title("🚀 Software de Optimización de Producción")

    col_intro, col_img = st.columns([2, 1])

    with col_intro:
        st.markdown("""
        ### Bienvenid@ al Sistema de Análisis del Campo Volve
        Esta plataforma interactiva permite realizar un análisis integral de la producción de pozos, 
        facilitando la toma de decisiones técnicas mediante:

        * **Visualización de Históricos:** Exploración de datos reales del dataset de Equinor (Volve).
        * **Curvas IPR:** Modelado del potencial del yacimiento usando métodos de Darcy, Vogel y Standing.
        * **Análisis Nodal:** Optimización de la completación y el sistema de levantamiento.

        *Seleccione una opción en el menú de la izquierda para comenzar.*
        """)

    with col_img:
        # Una imagen secundaria o estadística rápida
        st.success("✅ Sistema Conectado")
        st.metric(label="Estado del Campo", value="Activo", delta="Optimizado")

# --- SECCIÓN: POTENCIAL DEL YACIMIENTO ---
elif selected == "Potencial Yacimiento":
    st.header("📊 Cálculos de Potencial y Curvas IPR")
    # ... (Tu código de cálculos se mantiene igual aquí) ...
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Datos de Entrada")
        pr = st.number_input("Presión de Reservorio (Pr) [psi]", value=4000.0)
        pb = st.number_input("Presión de Burbuja (Pb) [psi]", value=2500.0)
        ef = st.slider("Eficiencia de Flujo (EF)", 0.5, 1.5, 1.0, 0.1)

        st.divider()
        st.write("**Datos de la Prueba de Producción**")
        q_test = st.number_input("Caudal de prueba (q) [bpd]", value=800.0)
        pwf_test = st.number_input("Pwf de la prueba [psi]", value=3200.0)

    j_val = j(q_test, pwf_test, pr, pb, ef)
    qb_val = Qb(q_test, pwf_test, pr, pb, ef)
    aof_val = aof(q_test, pwf_test, pr, pb, ef)

    with col2:
        st.subheader("Resultados del Análisis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Índice J", f"{j_val:.2f}")
        c2.metric("Qb @ Pb", f"{qb_val:.0f} bpd")
        c3.metric("AOF (Max)", f"{aof_val:.0f} bpd")

        pwf_values = np.linspace(0, pr, 100)
        qo_values = [Qo(q_test, pwf_test, pr, p, pb, ef) for p in pwf_values]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=qo_values, y=pwf_values, mode='lines', name='Curva IPR',
                       line=dict(color='#007bff', width=3)))
        fig.add_hline(y=pb, line_dash="dash", line_color="#dc3545",
                      annotation_text="Presión de Burbuja (Pb)")
        fig.update_layout(title="Curva IPR (Inflow Performance Relationship)",
                          xaxis_title="Caudal de Petróleo (Qo) [bpd]",
                          yaxis_title="Presión de Fondo (Pwf) [psi]", height=500,
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN: HISTORIAL VOLVE ---
elif selected == "Historial VOLVE":
    st.title("📈 Historial de Producción - Campo VOLVE")
    st.info("Cargue el archivo CSV o Excel con los datos de producción históricos.")
    uploaded_file = st.file_uploader("Subir dataset de producción",
                                     type=["csv", "xlsx"])
    if uploaded_file:
        st.success("Archivo cargado correctamente (Simulación)")

# --- SECCIÓN: ANÁLISIS NODAL ---
elif selected == "Análisis Nodal":
    st.title("🔗 Análisis Nodal")
    st.markdown(
        "> **Próximamente:** Integración de curvas VLP para determinar el punto de operación.")