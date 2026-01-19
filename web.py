import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="ProdFlow",
    page_icon="🛢️",
    layout="wide"
)

# ===============================
# LOGO
# ===============================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("Resources/logo.png", width=120)
with col2:
    st.title("ProdFlow")
    st.subheader("Aplicación de Ingeniería de Producción")

# ===============================
# MENÚ PRINCIPAL
# ===============================
menu = st.sidebar.selectbox(
    "Menú principal",
    [
        "📊 Historial de Producción",
        "📈 Potencial del Yacimiento (IPR)",
        "🔧 Análisis Nodal (Próximamente)"
    ]
)

# ===============================
# CARGA DE DATA
# ===============================
@st.cache_data
def load_data():
    file = "Data/Volve production data(1)(1).xlsx"
    daily = pd.read_excel(file, sheet_name="Daily Production Data")
    monthly = pd.read_excel(file, sheet_name="Monthly Production Data")
    return daily, monthly

daily_df, monthly_df = load_data()

# ==========================================================
# SECCIÓN 1 – HISTORIAL DE PRODUCCIÓN
# ==========================================================
if menu == "📊 Historial de Producción":

    st.header("📊 Historial de Producción – Campo Volve")

    well_list = daily_df["NPD_WELL_BORE_NAME"].dropna().unique()
    well = st.selectbox("Selecciona un pozo", well_list)

    df = daily_df[daily_df["NPD_WELL_BORE_NAME"] == well].copy()
    df["DATEPRD"] = pd.to_datetime(df["DATEPRD"])
    df["YEAR"] = df["DATEPRD"].dt.year

    prod_year = df.groupby("YEAR").agg({
        "BORE_OIL_VOL": "sum",
        "BORE_WAT_VOL": "sum"
    }).reset_index()

    tab1, tab2, tab3 = st.tabs(["Qo vs t", "Qw vs t", "Qo y Qw vs t"])

    with tab1:
        fig = px.line(
            prod_year,
            x="YEAR",
            y="BORE_OIL_VOL",
            labels={"BORE_OIL_VOL": "Qo (bbl)", "YEAR": "Año"},
            title="Producción de Aceite vs Tiempo"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.line(
            prod_year,
            x="YEAR",
            y="BORE_WAT_VOL",
            labels={"BORE_WAT_VOL": "Qw (bbl)", "YEAR": "Año"},
            title="Producción de Agua vs Tiempo"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.line(
            prod_year,
            x="YEAR",
            y=["BORE_OIL_VOL", "BORE_WAT_VOL"],
            labels={"value": "Producción (bbl)", "YEAR": "Año"},
            title="Producción de Aceite y Agua"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# SECCIÓN 2 – POTENCIAL DEL YACIMIENTO (IPR)
# ==========================================================
elif menu == "📈 Potencial del Yacimiento (IPR)":

    st.header("📈 Análisis del Potencial del Yacimiento")

    st.subheader("Parámetros de Entrada")

    col1, col2 = st.columns(2)

    with col1:
        q_test = st.number_input("q_test (bpd)", min_value=0.0)
        pwf_test = st.number_input("pwf_test (psia)", min_value=0.0)
        pr = st.number_input("Presión del yacimiento Pr (psia)", min_value=0.0)
        pb = st.number_input("Presión de burbuja Pb (psia)", min_value=0.0)

    with col2:
        pwf = st.number_input("Pwf de análisis (psia)", min_value=0.0)
        ef = st.number_input("Factor de daño / estimulación (ef)", value=1.0)
        use_ef2 = st.checkbox("Usar ef2")

        if use_ef2:
            ef2 = st.number_input("ef2", value=1.0)
        else:
            ef2 = None

    if st.button("Calcular IPR"):

        from math import pi

        # -----------------------------
        # FUNCIONES (COPIADAS DEL TXT)
        # -----------------------------
        def j(q_test, pwf_test, pr, pb, ef=1, ef2=None):
            if ef == 1:
                if pwf_test >= pb:
                    return q_test / (pr - pwf_test)
                else:
                    return q_test / ((pr - pb) + (pb / 1.8) *
                                     (1 - 0.2 * (pwf_test / pb) - 0.8 * (
                                                 pwf_test / pb) ** 2))
            else:
                return q_test / (pr - pwf_test)


        def Qb(q_test, pwf_test, pr, pb, ef=1, ef2=None):
            return j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)


        def AOF(q_test, pwf_test, pr, pb, ef=1, ef2=None):
            if pr > pb:
                return j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            else:
                return q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)


        def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
            if pwf >= pb:
                return j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pwf)
            else:
                return Qb(q_test, pwf_test, pr, pb, ef, ef2) + \
                    (j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * \
                    (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)


        # -----------------------------
        J = j(q_test, pwf_test, pr, pb, ef, ef2)
        qb = Qb(q_test, pwf_test, pr, pb, ef, ef2)
        aof = AOF(q_test, pwf_test, pr, pb, ef, ef2)

        st.subheader("Resultados")

        col1, col2, col3 = st.columns(3)
        col1.metric("Índice de productividad J", f"{J:.2f} bpd/psi")
        col2.metric("Caudal a Pb (Qb)", f"{qb:.2f} bpd")
        col3.metric("AOF", f"{aof:.2f} bpd")

        # -----------------------------
        # CURVA IPR
        # -----------------------------
        pwf_values = np.linspace(0, pr, 60)

        qo_values = [
            Qo(q_test, pwf_test, pr, p, pb, ef, ef2)
            for p in pwf_values
        ]

        ipr_df = pd.DataFrame({
            "Pwf (psia)": pwf_values,
            "Qo (bpd)": qo_values
        })

        fig = px.line(
            ipr_df,
            x="Qo (bpd)",
            y="Pwf (psia)",
            title="Curva IPR",
            markers=True
        )


        fig.update_xaxes(
            title="Qo (bpd)"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabla de Caudales y Presiones")
        st.dataframe(ipr_df)

# ==========================================================
# SECCIÓN 3 – ANÁLISIS NODAL
# ==========================================================
else:
    st.header("🔧 Análisis Nodal")
    st.warning("Esta sección será desarrollada próximamente.")
