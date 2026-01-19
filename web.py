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
# MENÚ PRINCIPAL (Actualizado)
# ===============================
menu = st.sidebar.selectbox(
    "Menú principal",
    [
        "🏠 Inicio",
        "📊 Historial de Producción",
        "📈 Potencial del Yacimiento (IPR)",
        "🔧 Análisis Nodal"
    ]
)

# ==========================================================
# SECCIÓN INICIO – PRESENTACIÓN
# ==========================================================
if menu == "🏠 Inicio":
    st.title("¡Bienvenido a ProdFlow!")

    st.markdown("""
    ### La Plataforma Integral para Ingeniería de Producción
    **ProdFlow** es una herramienta diseñada para optimizar el análisis y la toma de decisiones en el sector de petróleo y gas. 
    A través de esta aplicación, puedes gestionar datos complejos de yacimientos y pozos de manera visual e intuitiva.
    """)

    # Imagen descriptiva del flujo de producción
    #

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 🚀 Nuestra Misión")
        st.write("""
        Facilitar a ingenieros y estudiantes las herramientas de cálculo necesarias para:
        * Monitorear el historial de producción de campos reales.
        * Evaluar el potencial de entrega del yacimiento (IPR).
        * Realizar optimizaciones mediante Análisis Nodal.
        """)

    with col2:
        st.success("### 🛠️ Herramientas Disponibles")
        st.write("""
        1. **Historial de Producción:** Visualización de Qo y Qw con datos del Campo Volve.
        2. **Análisis IPR:** Modelado de curvas Darcy y Vogel para pozos saturados y subsaturados.
        3. **Análisis Nodal:** Evaluación del sistema completo (VLP vs IPR) y cálculo de presión del sistema.
        """)

    st.divider()

    with st.expander("📌 Instrucciones de uso"):
        st.write("""
        Para comenzar, selecciona una de las opciones en el **Menú Principal** situado a la izquierda:
        - Utiliza los filtros en cada sección para seleccionar pozos específicos.
        - Puedes descargar los datos procesados directamente desde las tablas generadas.
        - Los gráficos son interactivos: puedes hacer zoom y guardar capturas de pantalla.
        """)

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
        "Resources/Field_Volve.mp4",
        width=300
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



        fig.update_xaxes(
            title="Qo (bpd)"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tabla de Caudales y Presiones")
        st.dataframe(ipr_df)






# ==========================================================
# SECCIÓN 3 – ANÁLISIS NODAL
# ==========================================================
elif menu == "🔧 Análisis Nodal":
    st.header("🔧 Análisis Nodal")

    # --- PARÁMETROS DE ENTRADA (Basados en el documento) ---
    st.subheader("Configuración del Sistema (VLP)")
    col1, col2 = st.columns(2)

    with col1:
        thp = st.number_input("Presión de cabezal (THP) [psia]", value=360.0)
        wc = st.number_input("Corte de agua (WC)", value=0.9, min_value=0.0,
                             max_value=1.0)
        api = st.number_input("Gravedad API del crudo", value=20.0)
        sg_h2o = st.number_input("Gravedad específica del agua (SGw)", value=1.09)

    with col2:
        id_tubing = st.number_input("Diámetro interno (ID) [in]", value=3.5)
        tvd = st.number_input("Profundidad TVD [ft]", value=9000.0)
        md = st.number_input("Profundidad MD [ft]", value=10500.0)
        c_hw = st.number_input("Constante de rugosidad (C)", value=120.0)

    st.subheader("Parámetros del Yacimiento (IPR)")
    col3, col4 = st.columns(2)
    with col3:
        pr_n = st.number_input("Presión del yacimiento (Pr) [psia]", value=3000.0,
                               key="pr_n")
        pb_n = st.number_input("Presión de burbuja (Pb) [psia]", value=2300.0,
                               key="pb_n")
    with col4:
        q_test_n = st.number_input("Caudal de prueba (q_test) [bpd]", value=1500.0,
                                   key="qt_n")
        pwf_test_n = st.number_input("Pwf de prueba (psia)", value=2400.0, key="pwft_n")

    if st.button("Ejecutar Análisis Nodal"):
        import plotly.graph_objects as go


        # ---------------------------------------------------------
        # FUNCIONES EXTRAÍDAS DEL DOCUMENTO (Celdas 8, 9, 10, 11)
        # ---------------------------------------------------------
        def sg_oil(API):
            return 141.5 / (131.5 + API)


        def sg_avg(API, wc, sg_h2o):
            return wc * sg_h2o + (1 - wc) * sg_oil(API)


        def gradient_avg(API, wc, sg_h2o):
            return sg_avg(API, wc, sg_h2o) * 0.433


        def f_darcy(Q, ID, C=120):
            if Q <= 0: return 0
            return (2.083 * (
                        ((100 * Q) / (34.3 * C)) ** 1.85 * (1 / ID) ** 4.8655)) / 1000


        # Funciones de IPR (Basadas en celdas 6 y 7)
        # Reutilizamos j y aof definidas previamente o las calculamos aquí
        def j_local(q_test, pwf_test, pr, pb):
            if pwf_test >= pb:
                return q_test / (pr - pwf_test)
            else:
                return q_test / ((pr - pb) + (pb / 1.8) * (
                            1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))


        def pwf_darcy(q_test, pwf_test, q, pr, pb):
            j_val = j_local(q_test, pwf_test, pr, pb)
            return pr - (q / j_val) if j_val != 0 else pr


        # ---------------------------------------------------------
        # CÁLCULOS PARA EL DATAFRAME (Lógica Celda 50 y 59)
        # ---------------------------------------------------------
        # Definimos un rango de caudales (de 0 a un valor estimado de AOF)
        j_val = j_local(q_test_n, pwf_test_n, pr_n, pb_n)
        q_max_est = j_val * pr_n * 1.2  # Estimación para el rango del gráfico
        q_steps = np.linspace(0, q_max_est, 15)

        g_avg = gradient_avg(api, wc, sg_h2o)
        p_gravity = g_avg * tvd

        data_rows = []
        for q in q_steps:
            p_wf_ipr = pwf_darcy(q_test_n, pwf_test_n, q, pr_n, pb_n)

            f_val = f_darcy(q, id_tubing, c_hw)
            f_ft = f_val * md
            p_friction = f_ft * g_avg
            p_o_vlp = thp + p_gravity + p_friction

            p_sys = p_o_vlp - p_wf_ipr  # Presión del sistema (Celda 50)

            data_rows.append({
                "Q(bpd)": round(q, 2),
                "Pwf(psia)": round(p_wf_ipr, 2),
                "Pgravity(psia)": round(p_gravity, 2),
                "f": round(f_val, 6),
                "Pf(psia)": round(p_friction, 2),
                "Po(psia)": round(p_o_vlp, 2),
                "Psys(psia)": round(p_sys, 2)
            })

        df_nodal = pd.DataFrame(data_rows)

        # ---------------------------------------------------------
        # GRÁFICA DE ANÁLISIS NODAL (Basada en Celda 54)
        # ---------------------------------------------------------
        fig = go.Figure()

        # Curva IPR
        fig.add_trace(go.Scatter(x=df_nodal["Q(bpd)"], y=df_nodal["Pwf(psia)"],
                                 name="IPR (Oferta)", line=dict(color='red', width=3)))

        # Curva VLP
        fig.add_trace(go.Scatter(x=df_nodal["Q(bpd)"], y=df_nodal["Po(psia)"],
                                 name="VLP (Demanda)",
                                 line=dict(color='green', width=3)))

        # Curva del Sistema
        fig.add_trace(go.Scatter(x=df_nodal["Q(bpd)"], y=df_nodal["Psys(psia)"],
                                 name="System Curve (Psys)",
                                 line=dict(color='blue', dash='dash')))

        fig.update_layout(
            title="Análisis Nodal del Sistema",
            xaxis_title="Caudal Q (bpd)",
            yaxis_title="Presión (psia)",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Ajuste de rango para visualizar el cruce
        fig.update_yaxes(range=[0, pr_n + 500])
        fig.update_xaxes(range=[0, q_max_est])

        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------
        # TABLA DE RESULTADOS
        # ---------------------------------------------------------
        st.subheader("Resultados del Sistema")
        st.dataframe(df_nodal, use_container_width=True)

        # Identificación del punto de cruce (opcional)
        interseccion = df_nodal.iloc[(df_nodal['Psys(psia)']).abs().argsort()[:1]]
        st.info(
            f"El punto de operación estimado es cercano a **{interseccion['Q(bpd)'].values[0]} bpd** "
            f"con una presión de fondo de **{interseccion['Po(psia)'].values[0]} psia**.")