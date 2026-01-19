import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="ProdFlow",
    page_icon="Resources/logo.png",
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

    st.video(
        "Resources/Field_Volve.mp4"
    )

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

    st.subheader("Parámetros de Diseño de Tubería (VLP)")

    col1, col2 = st.columns(2)

    with col1:
        thp = st.number_input("Presión de cabezal (THP) [psia]", value=250.0)
        depth = st.number_input("Profundidad vertical (TVD) [ft]", value=6000.0)
        gravity_grad = st.number_input("Gradiente estático [psi/ft]", value=0.433)

    with col2:
        id_tubing = st.selectbox("Diámetro interno de tubería (ID) [in]",
                                 [1.995, 2.441, 2.992])
        c_friction = st.number_input("Constante de fricción (simplificada)",
                                     value=0.000000002)

    # Reutilizamos parámetros del IPR para el cálculo del punto de flujo
    st.divider()
    st.subheader("Parámetros del Yacimiento (IPR)")
    col3, col4 = st.columns(2)
    with col3:
        pr_n = st.number_input("Presión del yacimiento (Pr) [psia]", value=3000.0,
                               key="pr_n")
        pb_n = st.number_input("Presión de burbuja (Pb) [psia]", value=1500.0,
                               key="pb_n")
    with col4:
        q_test_n = st.number_input("Caudal de prueba (q_test) [bpd]", value=1000.0,
                                   key="q_test_n")
        pwf_test_n = st.number_input("Pwf de prueba [psia]", value=2500.0,
                                     key="pwf_test_n")

    if st.button("Realizar Análisis Nodal"):

        # ---------------------------------------------------------
        # FUNCIONES BASADAS EN EL DOCUMENTO (Celdas 19-35, 55-59)
        # ---------------------------------------------------------

        # Función IPR (Vogel/Darcy combinada)
        def Qo_IPR(q_test, pwf_test, pr, pwf, pb):
            j_val = q_test / (pr - pwf_test)
            if pwf >= pb:
                return j_val * (pr - pwf)
            else:
                qb = j_val * (pr - pb)
                return qb + (j_val * pb / 1.8) * (
                            1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)


        # Función VLP simplificada (Basada en la lógica de las celdas 19 y 35)
        # Pwf = THP + Pgravity + Pfriction
        def Pwf_VLP(q, thp, depth, grad, c_fric, diam):
            p_gravity = depth * grad
            # Simplificación de la caída por fricción observada en el dataframe del documento
            p_friction = c_fric * (q ** 2) / (diam ** 5) * depth
            return thp + p_gravity + p_friction


        # -----------------------------
        # CÁLCULOS DE CURVAS
        # -----------------------------
        rates = np.linspace(0, Qo_IPR(q_test_n, pwf_test_n, pr_n, 0, pb_n), 50)

        ipr_pwf = [pr_n if r == 0 else (None) for r in rates]  # Inicializar
        # Invertimos el cálculo para graficar Pwf vs Q
        # Para simplificar, generamos puntos de Pwf y calculamos Q
        pwf_range = np.linspace(0, pr_n, 50)
        ipr_data = pd.DataFrame({
            "Q": [Qo_IPR(q_test_n, pwf_test_n, pr_n, p, pb_n) for p in pwf_range],
            "Pwf": pwf_range,
            "Tipo": "IPR"
        })

        vlp_data = pd.DataFrame({
            "Q": rates,
            "Pwf": [Pwf_VLP(q, thp, depth, gravity_grad, c_friction, id_tubing) for q in
                    rates],
            "Tipo": "VLP"
        })

        nodal_df = pd.concat([ipr_data, vlp_data])

        # -----------------------------
        # GRÁFICO
        # -----------------------------
        fig = px.line(
            nodal_df,
            x="Q",
            y="Pwf",
            color="Tipo",
            title=f"Análisis Nodal - Tubing {id_tubing} in",
            labels={"Q": "Caudal (bpd)", "Pwf": "Presión de Fondo (psia)"}
        )

        # Limitar el eje Y para mejor visibilidad
        fig.update_yaxes(range=[0, pr_n + 500])

        st.plotly_chart(fig, use_container_width=True)

        st.success(
            "El punto de intersección representa el caudal óptimo de producción para el diámetro seleccionado.")