import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BHP ENC-3430 | App de Resúmenes Ejecutivos del Proyecto",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .info-card {
        background-color: #F8FAFC;
        border-left: 5px solid #2563EB;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .scope-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .stMetric label {
        font-weight: 600 !important;
        color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CARGA DE DATOS GROUNDED EN FUENTES
# -----------------------------------------------------------------------------
@st.cache_data
def load_summary_data():
    # 1. Datos Generales del Proyecto ENC-3430 VWP04
    project_info = {
        "Nombre": "Proyecto Escondida New Concentrator (ENC) - VWP04",
        "Titular": "Minera Escondida Ltda. (MEL / BHP)",
        "Ingeniería": "Fluor / Esinel Ingenieros (Fase SPS / Clase 3)",
        "Objetivo": "Suministro de energía eléctrica en 220 kV y 33 kV para la nueva planta concentradora que reemplaza a la Planta Los Colorados.",
        "Capacidad_Transmision": "900 MVA",
        "Trazado_LAT": "25,72 km (2x220 kV S/E Monte Mina - S/E EGP)",
        "Subestacion_Principal": "S/E EGP 220/33 kV (GIS Interior en Galpón)",
        "Ampliacion_Barra": "S/E Monte Mina 220 kV (Transelec, 2 medias diagonales AIS)",
        "Monto_Costo_Directo_Base": 160900356.0,
        "Monto_CAPEX_Total_Clase3": 211681174.0,
        "Horas_Hombre_Directas": 1781112
    }

    # 2. Desglose de Alcance por Instalación
    scope_data = [
        {
            "Instalacion": "S/E EGP 220/33 kV (GIS)",
            "Tipo": "Subestación Digital de Distribución Principal",
            "Configuracion": "Interruptor y Medio en 220 kV (SF6 / GIS)",
            "Equipos_Clave": "Switchgear GIS 245 kV, (3) Transformadores de Poder 125 MVA 220/33 kV, Ductos GIL 220 kV, Galpón prefabricado con Puente Grúa, Sala Eléctrica ERoom 33 kV, NGR y Grupo Electrógeno 2.750 kVA.",
            "Limite_Bateria": "Barras de 33 kV aisladas en resina hasta conexión con Switchgear GIS 33 kV en Sala Eléctrica 3841-ER-00002."
        },
        {
            "Instalacion": "S/E Monte Mina 220 kV (AIS)",
            "Tipo": "Ampliación de Subestación Existente (Transelec)",
            "Configuracion": "Interruptor y Medio (2 medias diagonales NUP 5521 y NUP 5816)",
            "Equipos_Clave": "(3) Interruptores Tanque Muerto SF6 220 kV 3150A 50kA, (10) TPC 220 kV, Desconectadores tripolares, Trampas de onda, Patios de Mufas.",
            "Limite_Bateria": "Cruce subterráneo de 375 m en cable XLPE 220 kV 3000 mm² bajo línea existente Jadresic hacia primera torre de LAT."
        },
        {
            "Instalacion": "Línea de Transmisión 2x220 kV",
            "Tipo": "Línea de Alta Tensión de Doble Circuito",
            "Configuracion": "2x220 kV, Capacidad 900 MVA (Monte Mina - S/E EGP)",
            "Equipos_Clave": "84 Torres Reticuladas de Acero (66 Suspensión 22AD.1M3, 18 Anclaje/Remate 22CD/22DD), Conductor AAAC Flint 740.8 MCM (2 subcond/fase), Cable OPGW 24FO, Cable Guardia EHS 3/8\".",
            "Limite_Bateria": "Desde marco de línea S/E Monte Mina hasta marco de entrada en S/E EGP (25,72 km de trazado)."
        }
    ]

    # 3. Precommitments (Compras Anticipadas de MEL)
    precommitments_data = [
        {"Paquete": "Switchgear GIS 220 kV & GIL", "Descripcion": "Suministro de SWG GIS 220 kV, Ductos GIL, Galpón prefabricado c/puente grúa, detección de incendios, CCTV y paneles de protección/control.", "Estado": "Precommitment MEL / Transferencia a EPC", "Fecha_OC_Estimada": "10 Agosto 2026"},
        {"Paquete": "Transformadores de Poder", "Descripcion": " (3) Transformadores de Poder 220/33 kV de 75/100/125 MVA ONAN/ONAF1/ONAF2 con cambiador de taps en carga (LTC).", "Estado": "Precommitment MEL / Transferencia a EPC", "Fecha_OC_Estimada": "Agosto 2026"},
        {"Paquete": "Salas Eléctricas & GIS 33 kV", "Descripcion": "Sala Eléctrica Prefabricada ERoom, Switchgear GIS 33 kV y Sala de Servicios Generales.", "Estado": "Precommitment MEL / Transferencia a EPC", "Fecha_OC_Estimada": "Septiembre 2026"}
    ]

    # 4. Resumen Estimación de Costos Directos Clase 3 (Figura 10-1 de Memoria Descriptiva)
    capex_class3 = [
        {"Categoria_WBS": "A - Earthworks (Movimiento de Tierras)", "Unidad": "m³", "Cantidad": 724186, "Horas_Hombre": 377030, "Mano_Obra_USD": 7739008, "Equipos_USD": 6900572, "Materiales_USD": 3356025, "Costo_Directo_USD": 26542801, "Pct_Directo": 12.5},
        {"Categoria_WBS": "C - Concrete (Hormigones Estructurales)", "Unidad": "m³", "Cantidad": 6715, "Horas_Hombre": 179620, "Mano_Obra_USD": 3726967, "Equipos_USD": 1221698, "Materiales_USD": 4206695, "Costo_Directo_USD": 13503790, "Pct_Directo": 6.4},
        {"Categoria_WBS": "D - Structural Steel (Estructuras Acero)", "Unidad": "t", "Cantidad": 347, "Horas_Hombre": 201975, "Mano_Obra_USD": 4485156, "Equipos_USD": 5060430, "Materiales_USD": 6538224, "Costo_Directo_USD": 23722979, "Pct_Directo": 11.2},
        {"Categoria_WBS": "N - Mechanical Equipment (Equipos Mecánicos)", "Unidad": "Ea", "Cantidad": 4, "Horas_Hombre": 4867, "Mano_Obra_USD": 111406, "Equipos_USD": 130402, "Materiales_USD": 0, "Costo_Directo_USD": 391771, "Pct_Directo": 0.2},
        {"Categoria_WBS": "T - Electrical Equipment (Equipos Eléctricos)", "Unidad": "Ea", "Cantidad": 30820, "Horas_Hombre": 775579, "Mano_Obra_USD": 17928842, "Equipos_USD": 12546754, "Materiales_USD": 21906707, "Costo_Directo_USD": 131847515, "Pct_Directo": 62.3},
        {"Categoria_WBS": "U - Raceway (Canalizaciones Eléctricas)", "Unidad": "m", "Cantidad": 11147, "Horas_Hombre": 14880, "Mano_Obra_USD": 343984, "Equipos_USD": 138814, "Materiales_USD": 514760, "Costo_Directo_USD": 1471359, "Pct_Directo": 0.7},
        {"Categoria_WBS": "W - Electrical Cable (Cables Eléctricos)", "Unidad": "m", "Cantidad": 81693, "Horas_Hombre": 227161, "Mano_Obra_USD": 5251207, "Equipos_USD": 2147878, "Materiales_USD": 2228943, "Costo_Directo_USD": 14200959, "Pct_Directo": 6.7}
    ]

    # 5. Entregables de Ingeniería por Especialidad
    engineering_deliverables = [
        {"Especialidad": "Civil - Geotecnia", "Fase": "Clase 3 / SPS", "Documento_Clave": "Criterio de Diseño Civil y Mecánica de Suelos", "Codigo": "ENC-3430-CL-DES-21901", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Civil - Cubicaciones", "Fase": "Clase 3 / SPS", "Documento_Clave": "Listado de Materiales Civil / Cubicaciones", "Codigo": "ENC-3430-CL-MTO-21902", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Estructural - Subestación", "Fase": "Clase 3 / SPS", "Documento_Clave": "Memoria de Cálculo Fundaciones S/E EGP", "Codigo": "ENC-3430-ST-CFD-21901", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Estructural - Línea 220 kV", "Fase": "Clase 3 / SPS", "Documento_Clave": "Criterio de Diseño Estructuras de LAT", "Codigo": "ENC-3430-EL-REG-21901", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Electromecánica - S/E EGP", "Fase": "Clase 3 / SPS", "Documento_Clave": "Disposición de Equipos Sala GIS 220 kV", "Codigo": "ENC-3430-EL-GGA-21908", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Electromecánica - S/E Monte Mina", "Fase": "Clase 3 / SPS", "Documento_Clave": "Memoria Descriptiva Ampliación Monte Mina", "Codigo": "ENC-3430-EL-TRE-21902", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Línea Alta Tensión - Trazado", "Fase": "Clase 3 / SPS", "Documento_Clave": "Plano de Perfil Longitudinal y Estructuras LAT", "Codigo": "ENC-3430-EL-OPL-21911@21928", "Aprobacion": "Emitido para Uso"},
        {"Especialidad": "Control & Protecciones", "Fase": "Clase 3 / SPS", "Documento_Clave": "Arquitectura Básica Sistema Control & SCADA", "Codigo": "ENC-3430-IC-CSA-21901", "Aprobacion": "Emitido para Uso"}
    ]

    return project_info, pd.DataFrame(scope_data), pd.DataFrame(precommitments_data), pd.DataFrame(capex_class3), pd.DataFrame(engineering_deliverables)

project_info, scope_df, precommitments_df, capex_df, eng_df = load_summary_data()

# -----------------------------------------------------------------------------
# BARRA LATERAL Y NAVEGACIÓN DE MÓDULOS
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚡ BHP ENC-3430")
st.sidebar.markdown("**App de Resúmenes del Proyecto**")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Seleccionar Resumen:",
    [
        "📌 Resumen Ejecutivo General",
        "🛠️ Alcance y Límites de Batería",
        "📜 Precommitments (Compras Anticipadas)",
        "📊 Resumen Presupuestario (CAPEX Clase 3)",
        "📁 Entregables de Ingeniería (SPS)",
        "📤 Exportación de Resúmenes"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Minera Escondida Ltda. | Proyecto VWP04")

# -----------------------------------------------------------------------------
# MÓDULO 1: RESUMEN EJECUTIVO GENERAL
# -----------------------------------------------------------------------------
if menu == "📌 Resumen Ejecutivo General":
    st.markdown('<div class="main-header">Resumen Ejecutivo General del Proyecto</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Proyecto Escondida New Concentrator (ENC) - Paquete de Trabajo VWP04</div>', unsafe_allow_html=True)

    # Tarjetas Métricas Superiores
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Capacidad de Transmisión", project_info["Capacidad_Transmision"], delta="2x220 kV")
    with m2:
        st.metric("Longitud Trazado LAT", project_info["Trazado_LAT"].split()[0] + " km", delta="84 Torres Reticuladas")
    with m3:
        st.metric("Costo Directo Construcción", f"${project_info['Monto_Costo_Directo_Base']/1e6:.1f}M USD", delta="Clase 3 Estimación")
    with m4:
        st.metric("Total Horas Hombre Directas", f"{project_info['Horas_Hombre_Directas']:,} HH", delta="Fase Ejecución")

    st.markdown("---")

    # Ficha Descriptiva Principal
    col_a, col_b = st.columns([6, 4])

    with col_a:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("🎯 Objetivo y Ficha Técnica del Proyecto")
        st.write(f"**Nombre Oficial:** {project_info['Nombre']}")
        st.write(f"**Titular:** {project_info['Titular']}")
        st.write(f"**Ingeniería de Desarrollo:** {project_info['Ingeniería']}")
        st.write(f"**Propósito del Proyecto:** {project_info['Objetivo']}")
        st.write(f"**S/E Principal de Distribución:** {project_info['Subestacion_Principal']}")
        st.write(f"**S/E Interconexión Externa:** {project_info['Ampliacion_Barra']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.subheader("💡 Pilares del Alcance VWP04")
        st.info("""
        1. **Subestación EGP 220/33 kV**: Subestación GIS digital de alta tecnología dentro de galpón prefabricado con puente grúa.
        2. **Línea de Transmisión 2x220 kV**: Conexión de 25,72 km en doble circuito capaz de transportar 900 MVA hacia la nueva concentradora.
        3. **Ampliación S/E Monte Mina**: Dos medias diagonales en tecnología AIS (esquema interruptor y medio) con cruce subterráneo XLPE.
        """)

    # Gráfico Resumen Distribución de Costo Directo WBS
    st.subheader("📊 Distribución del Costo Directo por Categoria WBS (USD)")
    fig_wbs = px.bar(
        capex_df,
        x="Categoria_WBS",
        y="Costo_Directo_USD",
        text_auto=".2s",
        color="Categoria_WBS",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Costo_Directo_USD": "Costo Directo (USD)", "Categoria_WBS": "Categoría WBS"}
    )
    fig_wbs.update_layout(showlegend=False, height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_wbs, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 2: ALCANCE Y LÍMITES DE BATERÍA
# -----------------------------------------------------------------------------
elif menu == "🛠️ Alcance y Límites de Batería":
    st.markdown('<div class="main-header">Resumen de Alcance por Instalación y Límites de Batería</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Definición de Obras, Infraestructura y Puntos de Interconexión Térmica/Eléctrica</div>', unsafe_allow_html=True)

    for idx, row in scope_df.iterrows():
        st.markdown(f'<div class="scope-card">', unsafe_allow_html=True)
        st.markdown(f"### 🏗️ {row['Instalacion']}")
        st.markdown(f"**Tipo de Infraestructura:** {row['Tipo']} | **Configuración:** {row['Configuracion']}")
        st.write(f"**Equipos y Obras Clave:** {row['Equipos_Clave']}")
        st.warning(f"🔒 **Límite de Batería:** {row['Limite_Bateria']}")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MÓDULO 3: PRECOMMITMENTS (COMPRAS ANTICIPADAS)
# -----------------------------------------------------------------------------
elif menu == "📜 Precommitments (Compras Anticipadas)":
    st.markdown('<div class="main-header">Resumen de Precommitments de Equipos Principales</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Estrategia de Adquisición Anticipada por MEL para Equipos de Largo Plazo (Long Lead)</div>', unsafe_allow_html=True)

    st.markdown("""
    Como parte de la estrategia de adquisiciones del proyecto ENC, Minera Escondida (MEL) inició directamente la gestión de compra de los equipos críticos de mayor plazo de fabricación (**Precommitments**). 
    Las órdenes de compra de estos paquetes serán novadas y transferidas al Adjudicatario EPC.
    """)

    st.dataframe(
        precommitments_df.style.set_properties(**{'background-color': '#F8FAFC', 'border-color': '#E2E8F0'}),
        use_container_width=True
    )

    st.subheader("⏱️ Cronograma Estimado de Órdenes de Compra (Precommitments)")
    fig_timeline = px.timeline(
        pd.DataFrame([
            {"Paquete": "Switchgear GIS 220 kV & GIL", "Inicio": "2026-01-15", "Fin": "2026-08-10", "Estado": "Fase Final Licitación"},
            {"Paquete": "Transformadores de Poder (3x125 MVA)", "Inicio": "2026-02-01", "Fin": "2026-08-20", "Estado": "Evaluación Ofertas"},
            {"Paquete": "Salas Eléctricas ERoom & GIS 33 kV", "Inicio": "2026-03-01", "Fin": "2026-09-15", "Estado": "Especificación Técnica"}
        ]),
        x_start="Inicio",
        x_end="Fin",
        y="Paquete",
        color="Estado",
        title="Ventana de Adjudicación y Novación a Contratista EPC"
    )
    fig_timeline.update_layout(height=300)
    st.plotly_chart(fig_timeline, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 4: RESUMEN PRESUPUESTARIO (CAPEX CLASE 3)
# -----------------------------------------------------------------------------
elif menu == "📊 Resumen Presupuestario (CAPEX Clase 3)":
    st.markdown('<div class="main-header">Resumen Presupuestario de Costos Directos (Clase 3)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Estimación de Costos de Construcción, Mano de Obra, Equipos y Materiales (Documento ENC-3430-EL-TRE-21902)</div>', unsafe_allow_html=True)

    # Resumen de totales
    total_hh = capex_df["Horas_Hombre"].sum()
    total_mo = capex_df["Mano_Obra_USD"].sum()
    total_eq = capex_df["Equipos_USD"].sum()
    total_mat = capex_df["Materiales_USD"].sum()
    total_dir = capex_df["Costo_Directo_USD"].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Mano de Obra", f"${total_mo/1e6:.2f}M USD")
    with k2:
        st.metric("Total Uso Equipos", f"${total_eq/1e6:.2f}M USD")
    with k3:
        st.metric("Total Materiales", f"${total_mat/1e6:.2f}M USD")
    with k4:
        st.metric("Total Costo Directo", f"${total_dir/1e6:.2f}M USD")

    st.markdown("---")

    # Tabla Presupuestaria Formateada
    st.subheader("📋 Tabla Resumen Estimación de Costos Directos - Clase 3")
    st.dataframe(
        capex_df.style.format({
            "Cantidad": "{:,.0f}",
            "Horas_Hombre": "{:,.0f}",
            "Mano_Obra_USD": "${:,.0f}",
            "Equipos_USD": "${:,.0f}",
            "Materiales_USD": "${:,.0f}",
            "Costo_Directo_USD": "${:,.0f}",
            "Pct_Directo": "{:.1f}%"
        }),
        use_container_width=True,
        height=320
    )

    # Gráfico de Torta de Estructura de Costos Directos
    st.subheader("🥧 Distribución Porcentual del Costo Directo")
    fig_pie = px.pie(
        capex_df,
        values="Costo_Directo_USD",
        names="Categoria_WBS",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 5: ENTREGABLES DE INGENIERÍA (SPS)
# -----------------------------------------------------------------------------
elif menu == "📁 Entregables de Ingeniería (SPS)":
    st.markdown('<div class="main-header">Resumen de Entregables de Ingeniería (Fase SPS / Clase 3)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Listado de Documentos, Memorias de Cálculo, Planos y Criterios de Diseño por Especialidad</div>', unsafe_allow_html=True)

    spec_filter = st.multiselect("Filtrar por Especialidad:", options=eng_df["Especialidad"].unique(), default=eng_df["Especialidad"].unique())
    
    filtered_eng = eng_df[eng_df["Especialidad"].isin(spec_filter)]

    st.dataframe(
        filtered_eng,
        use_container_width=True,
        height=350
    )

# -----------------------------------------------------------------------------
# MÓDULO 6: EXPORTACIÓN DE RESÚMENES
# -----------------------------------------------------------------------------
elif menu == "📤 Exportación de Resúmenes":
    st.markdown('<div class="main-header">Centro de Exportación de Resúmenes y Fichas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Descarga de Reportes Ejecutivos en Formato CSV / Excel</div>', unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.subheader("📥 Exportar Presupuesto Clase 3 (CSV)")
        csv_capex = capex_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CAPEX Clase 3 (CSV)",
            data=csv_capex,
            file_name="BHP_ENC3430_Resumen_CAPEX_Clase3.csv",
            mime="text/csv"
        )

    with col_e2:
        st.subheader("📋 Exportar Alcance y Entregables (CSV)")
        csv_eng = eng_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Listado Entregables Ingeniería (CSV)",
            data=csv_eng,
            file_name="BHP_ENC3430_Entregables_Ingenieria.csv",
            mime="text/csv"
        )

st.sidebar.markdown("---")
st.sidebar.caption("SPS Engineering Phase | Project ENC-3430")
