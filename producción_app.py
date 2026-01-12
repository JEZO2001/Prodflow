import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from PIL import Image

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Producción App - Volve", layout="wide")


# --- FUNCIONES MATEMÁTICAS (Tus fórmulas integradas) ---

def j(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    if ef == 1:  # Darcy & Vogel
        if pwf_test >= pb:  # Subsaturado
            return q_test / (pr - pwf_test)
        else:  # Saturado
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))

    elif ef != 1 and ef2 is None:  # Darcy & Standing
        if pwf_test >= pb:
            return q_test / (pr - pwf_test)
        else:
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1.8 * (1 - pwf_test / pb) - 0.8 * ef * (
                            1 - pwf_test / pb) ** 2))
    return q_test / (pr - pwf_test)  # Fallback simple


def Qb(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    return j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)


def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    # Lógica simplificada basada en tus condiciones de saturación
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


# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("Producción App")
    selected = option_menu(
        "Menú", ["Inicio", "Historial VOLVE", "Potencial Yacimiento", "Análisis Nodal"],
        icons=["house", "table", "graph-up", "bezier2"], default_index=2
    )

# --- SECCIÓN: POTENCIAL DEL YACIMIENTO ---
if selected == "Potencial Yacimiento":
    st.header("Cálculos de Potencial y Curvas IPR")

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

    # Cálculos en tiempo real
    j_val = j(q_test, pwf_test, pr, pb, ef)
    qb_val = Qb(q_test, pwf_test, pr, pb, ef)
    aof_val = aof(q_test, pwf_test, pr, pb, ef)

    with col2:
        st.subheader("Resultados del Análisis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Índice J", f"{j_val:.2f}")
        c2.metric("Qb @ Pb", f"{qb_val:.0f} bpd")
        c3.metric("AOF (Max)", f"{aof_val:.0f} bpd")

        # Generar datos para la curva IPR
        pwf_values = np.linspace(0, pr, 100)
        qo_values = [Qo(q_test, pwf_test, pr, p, pb, ef) for p in pwf_values]

        # Gráfico interactivo con Plotly
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=qo_values, y=pwf_values, mode='lines', name='Curva IPR',
                       line=dict(color='green', width=3)))

        # Línea de Presión de Burbuja
        fig.add_hline(y=pb, line_dash="dash", line_color="red", annotation_text="Pb")

        fig.update_layout(
            title="Curva IPR (Inflow Performance Relationship)",
            xaxis_title="Caudal de Petróleo (Qo) [bpd]",
            yaxis_title="Presión de Fondo (Pwf) [psi]",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

# (Las demás secciones se mantienen como cascarones para que tú las completes)
elif selected == "Inicio":
    st.title("Bienvenido al Software de Producción")
    st.info("Utilice el menú lateral para navegar por las secciones del proyecto.")

elif selected == "Historial VOLVE":
    st.title("Historial de Producción - Campo VOLVE")
    st.warning(
        "Aquí debes cargar el Excel de VOLVE y usar px.line() para los gráficos Qo, Qw, etc.")