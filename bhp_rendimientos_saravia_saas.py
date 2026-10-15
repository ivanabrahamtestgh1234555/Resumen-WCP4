import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BHP ENC-3430 | Cálculo de Rendimientos BHP para Área de Estudios COX",
    page_icon="👷‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados
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
    .stMetric label {
        font-weight: 600 !important;
        color: #374151 !important;
    }
    .highlight-card {
        background-color: #F3F4F6;
        border-left: 5px solid #2563EB;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CARGA DE DATOS DE RENDIMIENTOS (SARAVIA'S BOOK & CUBICACIONES)
# -----------------------------------------------------------------------------
@st.cache_data
def load_saravia_rendimientos_data():
    # 1. Tabla Paramétrica de Rendimientos de Saravia's Book
    saravia_table = [
        {"Codigo": "EXC-ROCA", "Disciplina": "Civil", "Actividad": "Excavación Estructural en Roca (S1/S2)", "Rendimiento_HH_Unit": 0.92, "Unidad": "HH / m³", "Ref_Saravia": "Excavación Estructural < 5 m³ en Roca / Roca Agrietada"},
        {"Codigo": "EXC-SUELO", "Disciplina": "Civil", "Actividad": "Excavación Estructural en Suelo (S3/S4)", "Rendimiento_HH_Unit": 0.41, "Unidad": "HH / m³", "Ref_Saravia": "Excavación Estructural < 50 m³ en Suelo Blando / Grava"},
        {"Codigo": "RELL-ESTR", "Disciplina": "Civil", "Actividad": "Rellenos Compactados Estructurales", "Rendimiento_HH_Unit": 0.91, "Unidad": "HH / m³", "Ref_Saravia": "Rellenos Estructurales Mayores Compactados"},
        {"Codigo": "HORM-MED", "Disciplina": "Hormigones", "Actividad": "Hormigón Estructural Fundaciones Medianas (4 - 25 m³)", "Rendimiento_HH_Unit": 4.40, "Unidad": "HH / m³", "Ref_Saravia": "Hormigón H-35 / G35 Fundaciones Medianas"},
        {"Codigo": "HORM-GRAN", "Disciplina": "Hormigones", "Actividad": "Hormigón Estructural Fundaciones Grandes / Losas", "Rendimiento_HH_Unit": 3.80, "Unidad": "HH / m³", "Ref_Saravia": "Hormigón H-35 / G35 Fundaciones Grandes / Losas"},
        {"Codigo": "HORM-MURO", "Disciplina": "Hormigones", "Actividad": "Hormigón Estructural Muros Cortafuego", "Rendimiento_HH_Unit": 5.28, "Unidad": "HH / m³", "Ref_Saravia": "Hormigón H-35 / G35 Muros y Tabiques"},
        {"Codigo": "HORM-EMP", "Disciplina": "Hormigones", "Actividad": "Hormigón de Emplantillado (G10)", "Rendimiento_HH_Unit": 4.69, "Unidad": "HH / m³", "Ref_Saravia": "Hormigón H-10 / G10 Emplantillados e=10cm"},
        {"Codigo": "ACERO-REFD", "Disciplina": "Estructuras/Enfierradura", "Actividad": "Armadura Acero de Refuerzo (A630-420H)", "Rendimiento_HH_Unit": 0.06, "Unidad": "HH / kg", "Ref_Saravia": "Colocación Armadura (60 HH / Tonelada)"},
        {"Codigo": "MALLA-ACMA", "Disciplina": "Estructuras/Enfierradura", "Actividad": "Malla Electrosoldada ACMA", "Rendimiento_HH_Unit": 0.06, "Unidad": "HH / kg", "Ref_Saravia": "Colocación Malla Acma (60 HH / Tonelada)"},
        {"Codigo": "ESTR-PES", "Disciplina": "Estructuras/Enfierradura", "Actividad": "Estructura de Acero Pesada / Soportería", "Rendimiento_HH_Unit": 0.0389, "Unidad": "HH / kg", "Ref_Saravia": "Montaje Estructura Pesada (38.89 HH / Tonelada)"},
        {"Codigo": "TORRE-LAT", "Disciplina": "Estructuras/Enfierradura", "Actividad": "Montaje Torres Reticuladas A36/A572 LAT", "Rendimiento_HH_Unit": 0.0450, "Unidad": "HH / kg", "Ref_Saravia": "Montaje Torres Reticuladas (45 HH / Tonelada)"},
        {"Codigo": "TRAFO-PODER", "Disciplina": "Electromecánica", "Actividad": "Transformadores de Poder 125 MVA (220/33 kV)", "Rendimiento_HH_Unit": 1200.00, "Unidad": "HH / c/u", "Ref_Saravia": "Montaje Trafo Poder 125 MVA Integrado"},
        {"Codigo": "GIS-220KV", "Disciplina": "Electromecánica", "Actividad": "Switchgear GIS 245 kV (Suministro y Montaje)", "Rendimiento_HH_Unit": 15000.00, "Unidad": "HH / Gl", "Ref_Saravia": "Montaje Subestación GIS 220 kV Integrada"},
        {"Codigo": "INTR-SF6", "Disciplina": "Electromecánica", "Actividad": "Interruptor Tanque Muerto SF6 220 kV 3150A", "Rendimiento_HH_Unit": 136.62, "Unidad": "HH / c/u", "Ref_Saravia": "Montaje Interruptor Poder SF6 220 kV"},
        {"Codigo": "TPC-220KV", "Disciplina": "Electromecánica", "Actividad": "Transformador de Potencial TPC 220 kV", "Rendimiento_HH_Unit": 111.34, "Unidad": "HH / c/u", "Ref_Saravia": "Montaje Trafo Potencial Capacitivo 220 kV"},
        {"Codigo": "DESC-220KV", "Disciplina": "Electromecánica", "Actividad": "Desconectador Tripolar 220 kV", "Rendimiento_HH_Unit": 342.75, "Unidad": "HH / c/u", "Ref_Saravia": "Montaje Desconectador Tripolar 220 kV"},
        {"Codigo": "PARAR-220KV", "Disciplina": "Electromecánica", "Actividad": "Pararrayos y Aisladores Pedestal 220 kV", "Rendimiento_HH_Unit": 107.55, "Unidad": "HH / c/u", "Ref_Saravia": "Montaje Pararrayos y Pedestales"},
        {"Codigo": "CABLE-XLPE", "Disciplina": "Electromecánica", "Actividad": "Cable XLPE 220 kV 3000 mm² (Cruce Subterráneo)", "Rendimiento_HH_Unit": 1.25, "Unidad": "HH / m", "Ref_Saravia": "Tendido Cable XLPE Alta Tensión"},
        {"Codigo": "TEND-AAAC", "Disciplina": "Electromecánica", "Actividad": "Tendido Conductor AAAC Flint 740.8 MCM", "Rendimiento_HH_Unit": 140.00, "Unidad": "HH / km", "Ref_Saravia": "Tendido Conductor AAAC Alta Tensión"},
        {"Codigo": "TEND-OPGW", "Disciplina": "Electromecánica", "Actividad": "Tendido Cable OPGW / Guardia 24FO", "Rendimiento_HH_Unit": 110.00, "Unidad": "HH / km", "Ref_Saravia": "Tendido Cable OPGW / Guardia"},
        {"Codigo": "AISL-CADENA", "Disciplina": "Electromecánica", "Actividad": "Montaje Cadenas Aisladores y Herrajes", "Rendimiento_HH_Unit": 8.50, "Unidad": "HH / juego", "Ref_Saravia": "Montaje Cadenas y Herrajes LAT"}
    ]
    saravia_df = pd.DataFrame(saravia_table)

    # 2. Detalle de Cálculo de HH por partida
    detalle_data = [
        # SE EGP
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Civil", "Item": "Excavación Suelo Tipo 2 (Roca Agrietada/H-3)", "Cantidad": 2673.5, "Unidad": "m³", "Rendimiento_HH": 0.92, "Ref_Saravia": "Excavación Estructural < 5 m³ en Roca Agrietada"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Civil", "Item": "Excavación Suelo Tipo 3 (Grava Densa/H-1)", "Cantidad": 2673.5, "Unidad": "m³", "Rendimiento_HH": 0.41, "Ref_Saravia": "Excavación Estructural < 50 m³ en Grava"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Civil", "Item": "Excavación Suelo Tipo 4 (Suelo Fino/H-2)", "Cantidad": 1145.8, "Unidad": "m³", "Rendimiento_HH": 0.41, "Ref_Saravia": "Excavación Estructural < 50 m³ en Suelo Fino"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Civil", "Item": "Rellenos Compactados Estructurales", "Cantidad": 3190.2, "Unidad": "m³", "Rendimiento_HH": 0.91, "Ref_Saravia": "Rellenos Estructurales Mayores"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Hormigones", "Item": "Hormigón Estructural G35 Pedestales", "Cantidad": 286.0, "Unidad": "m³", "Rendimiento_HH": 4.40, "Ref_Saravia": "Hormigón H-35 Fundaciones Medianas"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Hormigones", "Item": "Hormigón Estructural G35 Muros Cortafuego", "Cantidad": 512.8, "Unidad": "m³", "Rendimiento_HH": 5.28, "Ref_Saravia": "Hormigón H-35 Muros y Tabiques"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Hormigones", "Item": "Hormigón Estructural G35 Zapatas / Losas / Edificios", "Cantidad": 2453.9, "Unidad": "m³", "Rendimiento_HH": 3.80, "Ref_Saravia": "Hormigón H-35 Fundaciones Grandes / Losas"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Hormigones", "Item": "Hormigón Emplantillado G10", "Cantidad": 292.0, "Unidad": "m³", "Rendimiento_HH": 4.69, "Ref_Saravia": "Hormigón H-10 Emplantillados"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Estructuras/Enfierradura", "Item": "Armadura Acero de Refuerzo A630-420H", "Cantidad": 252183.0, "Unidad": "kg", "Rendimiento_HH": 0.060, "Ref_Saravia": "Colocación Armadura (60 HH/TON)"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Estructuras/Enfierradura", "Item": "Malla Electrosoldada ACMA C-188", "Cantidad": 11539.0, "Unidad": "kg", "Rendimiento_HH": 0.060, "Ref_Saravia": "Colocación Malla Acma (60 HH/TON)"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Estructuras/Enfierradura", "Item": "Estructuras de Acero Soporte y Galpón GIS", "Cantidad": 139500.0, "Unidad": "kg", "Rendimiento_HH": 0.0389, "Ref_Saravia": "Montaje Estructura Pesada (38.89 HH/TON)"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Electromecánica", "Item": "Transformadores de Poder 125 MVA (220/33 kV)", "Cantidad": 3.0, "Unidad": "c/u", "Rendimiento_HH": 1200.0, "Ref_Saravia": "Montaje Trafo Poder 125 MVA"},
        {"Area": "S/E EGP 220/33 kV (GIS)", "Disciplina": "Electromecánica", "Item": "Switchgear GIS 245 kV (Suministro y Montaje)", "Cantidad": 1.0, "Unidad": "Gl", "Rendimiento_HH": 15000.0, "Ref_Saravia": "Montaje Subestación GIS 220 kV Integrada"},

        # SE Monte Mina
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Civil", "Item": "Excavación Patio AIS y Patios Mufas", "Cantidad": 2100.0, "Unidad": "m³", "Rendimiento_HH": 0.41, "Ref_Saravia": "Excavación Estructural Patio"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Hormigones", "Item": "Hormigón Estructural Fundaciones AIS", "Cantidad": 450.0, "Unidad": "m³", "Rendimiento_HH": 4.40, "Ref_Saravia": "Hormigón H-35 Fundaciones AIS"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Electromecánica", "Item": "Interruptores Tanque Muerto SF6 220 kV 3150A", "Cantidad": 3.0, "Unidad": "c/u", "Rendimiento_HH": 136.62, "Ref_Saravia": "Montaje Interruptor Poder SF6 220 kV"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Electromecánica", "Item": "Transformadores de Potencial TPC 220 kV", "Cantidad": 10.0, "Unidad": "c/u", "Rendimiento_HH": 111.34, "Ref_Saravia": "Montaje Trafo Potencial Capacitivo 220 kV"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Electromecánica", "Item": "Desconectadores Tripolares SPT/CPT 220 kV", "Cantidad": 10.0, "Unidad": "c/u", "Rendimiento_HH": 342.75, "Ref_Saravia": "Montaje Desconectador Tripolar 220 kV"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Electromecánica", "Item": "Pararrayos 220 kV y Aisladores Pedestal", "Cantidad": 12.0, "Unidad": "c/u", "Rendimiento_HH": 107.55, "Ref_Saravia": "Montaje Pararrayos y Pedestales"},
        {"Area": "S/E Monte Mina 220 kV (AIS)", "Disciplina": "Electromecánica", "Item": "Cable XLPE 220 kV 3000 mm² (Cruce Subterráneo)", "Cantidad": 1800.0, "Unidad": "m", "Rendimiento_HH": 1.25, "Ref_Saravia": "Tendido Cable XLPE Alta Tensión"},

        # Linea Transmision
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Civil", "Item": "Excavación Estructural Suelo 1 (Roca Sana)", "Cantidad": 53.5, "Unidad": "m³", "Rendimiento_HH": 0.92, "Ref_Saravia": "Excavación Fundación Torre en Roca"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Civil", "Item": "Excavación Estructural Suelo 2 (Unidad H-3)", "Cantidad": 645.6, "Unidad": "m³", "Rendimiento_HH": 0.92, "Ref_Saravia": "Excavación Fundación Torre Roca Agrietada"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Civil", "Item": "Excavación Estructural Suelo 3 (Unidad H-1)", "Cantidad": 3402.7, "Unidad": "m³", "Rendimiento_HH": 0.41, "Ref_Saravia": "Excavación Fundación Torre Grava"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Civil", "Item": "Excavación Estructural Suelo 4 (Unidad H-2)", "Cantidad": 2358.8, "Unidad": "m³", "Rendimiento_HH": 0.41, "Ref_Saravia": "Excavación Fundación Torre Suelo Fino"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Civil", "Item": "Relleno Compactado Fundaciones Torres", "Cantidad": 5271.0, "Unidad": "m³", "Rendimiento_HH": 0.91, "Ref_Saravia": "Relleno Compactado Fundaciones Torres"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Hormigones", "Item": "Hormigón Estructural G35 Fundaciones LAT", "Cantidad": 1210.8, "Unidad": "m³", "Rendimiento_HH": 4.40, "Ref_Saravia": "Hormigón Fundaciones Torres LAT"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Hormigones", "Item": "Hormigón Emplantillado G10 Fundaciones", "Cantidad": 98.7, "Unidad": "m³", "Rendimiento_HH": 4.69, "Ref_Saravia": "Hormigón Emplantillado G10 LAT"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Estructuras/Enfierradura", "Item": "Armadura Acero A630-420H Fundaciones LAT", "Cantidad": 126737.0, "Unidad": "kg", "Rendimiento_HH": 0.060, "Ref_Saravia": "Colocación Armadura (60 HH/TON)"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Estructuras/Enfierradura", "Item": "Montaje Torres Reticuladas A36/A572 (84 Torres)", "Cantidad": 1229600.0, "Unidad": "kg", "Rendimiento_HH": 0.045, "Ref_Saravia": "Montaje Torres Reticuladas (45 HH/TON)"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Electromecánica", "Item": "Tendido Conductor AAAC Flint (312 km cto equiv)", "Cantidad": 312.0, "Unidad": "km", "Rendimiento_HH": 140.0, "Ref_Saravia": "Tendido Conductor AAAC Alta Tensión"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Electromecánica", "Item": "Tendido Cable OPGW / Guardia (54.7 km equiv)", "Cantidad": 54.7, "Unidad": "km", "Rendimiento_HH": 110.0, "Ref_Saravia": "Tendido Cable OPGW / Guardia"},
        {"Area": "Línea Transmisión 2x220 kV", "Disciplina": "Electromecánica", "Item": "Montaje Cadenas Aisladores y Herrajes", "Cantidad": 504.0, "Unidad": "Juego", "Rendimiento_HH": 8.50, "Ref_Saravia": "Montaje Cadenas y Herrajes LAT"}
    ]
    detalle_df = pd.DataFrame(detalle_data)
    detalle_df["Total_HH"] = detalle_df["Cantidad"] * detalle_df["Rendimiento_HH"]

    return saravia_df, detalle_df

saravia_df, detalle_df = load_saravia_rendimientos_data()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.markdown("## BHP ENC-3430")
st.sidebar.markdown("**Cálculo de Rendimientos**")
st.sidebar.markdown("---")

module = st.sidebar.radio(
    "Seleccionar Módulo:",
    [
        "📊 Resumen Ejecutivo de HH",
        "📋 Cómputo de HH por Instalación y Disciplina",
        "📖 Tabla de Rendimientos (Saravia's Book)",
        "🧮 Calculadora & Simulador de Dotación",
        "📤 Exportar Informes (Excel / CSV)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros por Instalación:")
selected_areas = st.sidebar.multiselect(
    "Áreas del Proyecto:",
    options=detalle_df["Area"].unique(),
    default=detalle_df["Area"].unique()
)

filtered_df = detalle_df[detalle_df["Area"].isin(selected_areas)]

# -----------------------------------------------------------------------------
# MODULE 1: RESUMEN EJECUTIVO DE HH
# -----------------------------------------------------------------------------
if module == "📊 Resumen Ejecutivo de HH":
    st.markdown('<div class="main-header">Resumen Ejecutivo de Horas Hombre (HH) Directas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cómputo Total de Mano de Obra Directa según Rendimientos del Saravia Book</div>', unsafe_allow_html=True)

    # Key Metrics
    total_hh = filtered_df["Total_HH"].sum()
    avg_workers = total_hh / (12 * 180)
    peak_workers = avg_workers * 1.3
    top_disc = filtered_df.groupby("Disciplina")["Total_HH"].sum().idxmax()
    top_disc_hh = filtered_df.groupby("Disciplina")["Total_HH"].sum().max()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total HH Directas Calculadas", f"{total_hh:,.0f} HH")
    with c2:
        st.metric("Dotación Promedio Directa", f"{avg_workers:,.0f} Personas", delta="12 Meses @ 180 HH/mes")
    with c3:
        st.metric("Dotación Peak Estimada", f"{peak_workers:,.0f} Personas", delta="+30% Peak Mes")
    with c4:
        st.metric("Disciplina Principal", top_disc, delta=f"{top_disc_hh:,.0f} HH ({(top_disc_hh/total_hh)*100:.1f}%)")

    st.markdown("---")

    col_a, col_b = st.columns([6, 4])

    with col_a:
        st.subheader("Distribución de Horas Hombre por Instalación del Proyecto")
        area_hh = filtered_df.groupby("Area")["Total_HH"].sum().reset_index()
        fig_area = px.bar(
            area_hh,
            x="Area",
            y="Total_HH",
            text_auto=".3s",
            color="Area",
            color_discrete_sequence=["#1E3A8A", "#2563EB", "#60A5FA"],
            labels={"Total_HH": "Horas Hombre Directas (HH)", "Area": "Instalación"}
        )
        fig_area.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_area, use_container_width=True)

    with col_b:
        st.subheader("Distribución por Disciplina Técnica")
        disc_hh = filtered_df.groupby("Disciplina")["Total_HH"].sum().reset_index()
        fig_disc = px.pie(
            disc_hh,
            values="Total_HH",
            names="Disciplina",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_disc.update_layout(height=380)
        st.plotly_chart(fig_disc, use_container_width=True)

    st.subheader("Desglose Jerárquico de HH (Área → Disciplina → Partida)")
    fig_tree = px.treemap(
        filtered_df,
        path=["Area", "Disciplina", "Item"],
        values="Total_HH",
        color="Total_HH",
        color_continuous_scale="Viridis"
    )
    fig_tree.update_layout(height=450)
    st.plotly_chart(fig_tree, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 2: CÓMPUTO DE HH POR INSTALACIÓN Y DISCIPLINA
# -----------------------------------------------------------------------------
elif module == "📋 Cómputo de HH por Instalación y Disciplina":
    st.markdown('<div class="main-header">Matriz Detallada de Cómputo de Horas Hombre</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cálculo Línea por Línea: Cantidad (MTO) × Rendimiento Unitario (Saravia's Book) = Total HH</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([4, 4, 4])
    with f1:
        sel_disc = st.multiselect("Filtrar Disciplina:", options=detalle_df["Disciplina"].unique(), default=detalle_df["Disciplina"].unique())
    with f2:
        sel_un = st.multiselect("Filtrar Unidad:", options=detalle_df["Unidad"].unique(), default=detalle_df["Unidad"].unique())
    with f3:
        search_kw = st.text_input("🔍 Buscar Ítem o Partida:", "")

    df_view = filtered_df[
        (filtered_df["Disciplina"].isin(sel_disc)) &
        (filtered_df["Unidad"].isin(sel_un))
    ]
    if search_kw:
        df_view = df_view[df_view["Item"].str.contains(search_kw, case=False, na=False)]

    st.markdown(f"**Registros mostrados:** {len(df_view)}")

    st.dataframe(
        df_view[["Area", "Disciplina", "Item", "Cantidad", "Unidad", "Rendimiento_HH", "Total_HH", "Ref_Saravia"]].style.format({
            "Cantidad": "{:,.1f}",
            "Rendimiento_HH": "{:,.4f}",
            "Total_HH": "{:,.2f}"
        }),
        use_container_width=True,
        height=450
    )

    sub_hh = df_view["Total_HH"].sum()
    st.info(f"💡 **Subtotal Horas Hombre Seleccionadas:** {sub_hh:,.2f} HH")

# -----------------------------------------------------------------------------
# MODULE 3: TABLA DE RENDIMIENTOS (SARAVIA'S BOOK)
# -----------------------------------------------------------------------------
elif module == "📖 Tabla de Rendimientos (Saravia's Book)":
    st.markdown('<div class="main-header">Tabla de Parámetros de Rendimiento (Saravia Book)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Valores Base de Mano de Obra Directa para Construcción y Montaje Electromecánico</div>', unsafe_allow_html=True)

    r1, r2 = st.columns([5, 7])
    with r1:
        sel_sar_disc = st.multiselect("Disciplina Saravia:", options=saravia_df["Disciplina"].unique(), default=saravia_df["Disciplina"].unique())
    with r2:
        search_sar = st.text_input("🔍 Buscar Código / Tarea:", "")

    df_sar_view = saravia_df[saravia_df["Disciplina"].isin(sel_sar_disc)]
    if search_sar:
        df_sar_view = df_sar_view[df_sar_view["Actividad"].str.contains(search_sar, case=False, na=False) | df_sar_view["Codigo"].str.contains(search_sar, case=False, na=False)]

    st.dataframe(
        df_sar_view.style.format({
            "Rendimiento_HH_Unit": "{:,.4f}"
        }),
        use_container_width=True,
        height=450
    )

    st.markdown("""
    **Notas Técnicas del Saravia Book:**
    - Los rendimientos corresponden a **Horas Hombre Directas de Terreno** sin incluir supervisión indirecta.
    - Se consideran condiciones operativas normales de minería.
    """)

# -----------------------------------------------------------------------------
# MODULE 4: CALCULADORA & SIMULADOR DE DOTACIÓN DE PERSONAL
# -----------------------------------------------------------------------------
elif module == "🧮 Calculadora & Simulador de Dotación":
    st.markdown('<div class="main-header">Calculadora & Simulador de Dotación de Personal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Planificación de Mano de Obra, Factores de Altura Geográfica y Curva Teórica de Dotación</div>', unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([5, 5])

    with sim_col1:
        st.subheader("⚙️ Parámetros de Simulación de Terreno")
        base_hh_total = filtered_df["Total_HH"].sum()
        
        plazo_meses = st.slider("Plazo Estimado de Ejecución (Meses):", 6, 24, 12, step=1)
        jornada_hh = st.slider("Jornada Mensual por Trabajador (HH/mes/persona):", 140, 210, 180, step=5)
        
        st.markdown("**Factores de Ajuste Operativo:**")
        factor_altura = st.slider("Factor por Altura Geográfica / Clima (3.200 msnm):", 1.00, 1.35, 1.10, step=0.05, help="Incremento por menor oxigenación y clima en cordillera")
        factor_imprevistos = st.slider("Factor de Eficiencia / Imprevistos de Campo:", 0.90, 1.30, 1.00, step=0.05)
        factor_peak = st.slider("Factor de Peak de Personal en Mes Máximo:", 1.10, 1.60, 1.30, step=0.05)

    with sim_col2:
        st.subheader("📊 Resultados de Personal Requerido")

        hh_ajustadas = base_hh_total * factor_altura * factor_imprevistos
        dotacion_promedio = hh_ajustadas / (plazo_meses * jornada_hh)
        dotacion_peak = dotacion_promedio * factor_peak

        st.metric(
            "Horas Hombre Totales Ajustadas",
            f"{hh_ajustadas:,.0f} HH",
            delta=f"+{hh_ajustadas - base_hh_total:,.0f} HH (Factor Altura/Eficiencia)"
        )

        c_a, c_b = st.columns(2)
        with c_a:
            st.metric("Dotación Promedio Mensual", f"{dotacion_promedio:,.0f} Personas", delta=f"{plazo_meses} meses")
        with c_b:
            st.metric("Dotación Peak Estimada", f"{dotacion_peak:,.0f} Personas", delta=f"Mes de máxima carga")

        # Curva de Dotación Teórica (S-Curve Profile)
        meses = np.arange(1, plazo_meses + 1)
        # S-curve shape for monthly workforce
        norm_profile = np.sin(np.pi * (meses - 0.5) / plazo_meses) ** 1.8
        norm_profile = norm_profile / norm_profile.mean()
        workers_monthly = dotacion_promedio * norm_profile

        fig_curve = go.Figure()
        fig_curve.add_trace(go.Bar(
            x=meses,
            y=workers_monthly,
            name="Personal Directo (Personas)",
            marker_color="#2563EB"
        ))
        fig_curve.add_trace(go.Scatter(
            x=meses,
            y=np.cumsum(workers_monthly * jornada_hh),
            name="HH Acumuladas",
            yaxis="y2",
            line=dict(color="#10B981", width=3)
        ))

        fig_curve.update_layout(
            title="Curva Teórica de Dotación Mensual y HH Acumuladas",
            xaxis_title="Mes de Construcción",
            yaxis_title="Personal en Faena (Personas)",
            yaxis2=dict(title="HH Acumuladas", overlaying="y", side="right"),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_curve, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 5: EXPORTACIÓN DE INFORMES
# -----------------------------------------------------------------------------
elif module == "📤 Exportar Informes (Excel / CSV)":
    st.markdown('<div class="main-header">Centro de Exportación de Cálculos de Rendimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Descarga de Archivos de Datos para Programación de Obra y Control de Gestión</div>', unsafe_allow_html=True)

    d1, d2 = st.columns(2)

    with d1:
        st.subheader("📥 Descargar Cómputo de HH por Partida (CSV)")
        csv_det = detalle_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Matriz Detallada de HH (CSV)",
            data=csv_det,
            file_name="BHP_ENC3430_Calculo_HH_Detalle.csv",
            mime="text/csv"
        )

    with d2:
        st.subheader("📖 Descargar Tabla Saravia Book (CSV)")
        csv_sar = saravia_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Tabla Rendimientos Saravia (CSV)",
            data=csv_sar,
            file_name="Saravia_Book_Rendimientos_Referencia.csv",
            mime="text/csv"
        )

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 BHP | Cálculo de Rendimientos y Mano de Obra - Project ENC-3430")
