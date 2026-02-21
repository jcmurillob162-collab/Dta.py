# app.py
# Dashboard Type: Analytical
# This is an analytical dashboard designed for QA supervisors to explore historical
# performance patterns, identify underperforming agents, and uncover non-obvious trends
# across shifts, call categories, and time periods.

import streamlit as st
import pandas as pd
import plotly.express as px
import os                          # ← aquí, junto a los demás imports

# ============================================================
# CARGA DE DATOS
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "call_center_data.csv"))
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

df = load_data()

# ============================================================
# TÍTULO Y DESCRIPCIÓN
# ============================================================
st.title("📊 QA Call Center Performance Dashboard")
st.markdown(
    "**Para:** Supervisores de Calidad | "
    "**Pregunta central:** ¿Qué patrones de desempeño, riesgo y saturación existen en el equipo de agentes?"
)
st.divider()

# ============================================================
# SIDEBAR — FILTROS INTERACTIVOS
# ============================================================
st.sidebar.header("🔎 Filtros")

# Filtro de rango de fechas
fecha_min = df["fecha"].min()
fecha_max = df["fecha"].max()
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtro de turno
turnos_disponibles = ["Todos"] + sorted(df["turno"].unique().tolist())
turno_seleccionado = st.sidebar.selectbox("Turno", turnos_disponibles)

# Filtro de categoría de llamada
categorias_disponibles = ["Todas"] + sorted(df["categoria_llamada"].unique().tolist())
categoria_seleccionada = st.sidebar.selectbox("Categoría de llamada", categorias_disponibles)

# Filtro de agente
agentes_disponibles = ["Todos"] + sorted(df["nombre_agente"].unique().tolist())
agente_seleccionado = st.sidebar.selectbox("Agente", agentes_disponibles)

# ============================================================
# APLICAR FILTROS AL DATAFRAME
# ============================================================
df_filtrado = df[
    (df["fecha"] >= pd.to_datetime(rango_fechas[0])) &
    (df["fecha"] <= pd.to_datetime(rango_fechas[1]))
]

if turno_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["turno"] == turno_seleccionado]

if categoria_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["categoria_llamada"] == categoria_seleccionada]

if agente_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nombre_agente"] == agente_seleccionado]

# ============================================================
# KPI CARDS — FILA SUPERIOR
# ============================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Registros", f"{len(df_filtrado):,}")
col2.metric("Score QA Promedio", f"{df_filtrado['score_qa'].mean():.1f} / 100")
col3.metric("Satisfacción Promedio", f"{df_filtrado['score_satisfaccion'].mean():.1f} / 10")
col4.metric("Tasa de Error Promedio", f"{df_filtrado['tasa_error_pct'].mean():.1f}%")

st.divider()

# ============================================================
# GRÁFICA 1: Score QA por Agente (Bar Chart)
# Pregunta: ¿Qué agentes tienen mejor y peor desempeño?
# ============================================================
st.subheader("📌 Score QA promedio por agente")

qa_por_agente = (
    df_filtrado.groupby("nombre_agente")["score_qa"]
    .mean()
    .reset_index()
    .sort_values("score_qa", ascending=False)
)

fig1 = px.bar(
    qa_por_agente,
    x="nombre_agente",
    y="score_qa",
    color="score_qa",
    color_continuous_scale="teal",
    labels={"nombre_agente": "Agente", "score_qa": "Score QA Promedio"},
    text_auto=".1f"
)
fig1.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white",
    coloraxis_showscale=False
)
st.plotly_chart(fig1, use_container_width=True)

# ============================================================
# GRÁFICA 2: Tasa de Error vs Score QA (Scatter Plot)
# Pregunta: ¿Existe algún agente con score alto pero error alto? (Anomalía AG04)
# ============================================================
st.subheader("🔍 Tasa de error vs Score QA por agente (detección de anomalías)")

scatter_data = df_filtrado.groupby("nombre_agente").agg(
    score_qa=("score_qa", "mean"),
    tasa_error=("tasa_error_pct", "mean"),
    llamadas=("llamadas_por_turno", "sum")
).reset_index()

fig2 = px.scatter(
    scatter_data,
    x="score_qa",
    y="tasa_error",
    size="llamadas",
    color="nombre_agente",
    labels={
        "score_qa": "Score QA Promedio",
        "tasa_error": "Tasa de Error Promedio (%)",
        "nombre_agente": "Agente"
    },
    text="nombre_agente"
)
fig2.update_traces(textposition="top center")
fig2.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white"
)
st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# GRÁFICA 3: Volumen de llamadas por mes (Line Chart)
# Pregunta: ¿Existe estacionalidad? ¿Cuándo hay más carga?
# ============================================================
st.subheader("📅 Volumen de llamadas por mes")

meses_nombre = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

volumen_mes = (
    df_filtrado.groupby("mes")["llamadas_por_turno"]
    .sum()
    .reset_index()
)
volumen_mes["mes_nombre"] = volumen_mes["mes"].map(meses_nombre)

fig3 = px.line(
    volumen_mes,
    x="mes_nombre",
    y="llamadas_por_turno",
    markers=True,
    labels={"mes_nombre": "Mes", "llamadas_por_turno": "Total Llamadas"},
)
fig3.update_traces(line_color="#00b4d8", marker_color="#90e0ef")
fig3.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white"
)
st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# GRÁFICA 4: Satisfacción promedio por categoría y turno (Heatmap)
# Pregunta: ¿En qué combinación de turno + categoría baja más la satisfacción?
# ============================================================
st.subheader("🌡️ Satisfacción promedio por turno y categoría de llamada")

heatmap_data = df_filtrado.pivot_table(
    values="score_satisfaccion",
    index="turno",
    columns="categoria_llamada",
    aggfunc="mean"
).round(1)

fig4 = px.imshow(
    heatmap_data,
    color_continuous_scale="RdYlGn",
    aspect="auto",
    labels={"color": "Score Satisfacción"},
    text_auto=True
)
fig4.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white"
)
st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# GRÁFICA 5: Score QA por día de la semana (Box Plot)
# Pregunta: ¿Hay días donde la calidad cae sistemáticamente?
# ============================================================
st.subheader("📆 Distribución de Score QA por día de la semana")

orden_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

fig5 = px.box(
    df_filtrado,
    x="dia_semana",
    y="score_qa",
    category_orders={"dia_semana": orden_dias},
    labels={"dia_semana": "Día de la semana", "score_qa": "Score QA"},
    color="dia_semana"
)
fig5.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="white",
    showlegend=False
)
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("Dashboard generado con datos sintéticos | Maestría en Modelos Analíticos | 2026")
