# app.py
# Dashboard Type: Analytical
# This is an analytical dashboard designed for QA supervisors to explore historical
# performance patterns, identify underperforming agents, and uncover non-obvious trends
# across shifts, call categories, and time periods.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="QA Call Center Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    np.random.seed(42)
    n = 600

    agentes = {
        "AG01": {"nombre": "Carlos Mendez",   "experiencia_meses": 36},
        "AG02": {"nombre": "Laura Rios",       "experiencia_meses": 24},
        "AG03": {"nombre": "Jorge Castillo",   "experiencia_meses": 6},
        "AG04": {"nombre": "Valentina Cruz",   "experiencia_meses": 18},
        "AG05": {"nombre": "Andres Morales",   "experiencia_meses": 48},
        "AG06": {"nombre": "Sofia Herrera",    "experiencia_meses": 12},
        "AG07": {"nombre": "Miguel Torres",    "experiencia_meses": 30},
        "AG08": {"nombre": "Daniela Vargas",   "experiencia_meses": 3},
    }

    categorias = ["Venta Nueva", "Renovacion", "Queja", "Soporte Tecnico", "Cancelacion"]
    turnos = ["Manana", "Tarde", "Noche"]

    fecha_inicio = datetime(2024, 1, 1)
    fechas = [fecha_inicio + timedelta(days=int(np.random.randint(0, 365))) for _ in range(n)]
    dia_semana = [f.weekday() for f in fechas]
    mes = [f.month for f in fechas]

    ids_agentes = np.random.choice(list(agentes.keys()), n)
    nombres_agentes = [agentes[a]["nombre"] for a in ids_agentes]
    experiencia = [agentes[a]["experiencia_meses"] for a in ids_agentes]
    turno_asignado = np.random.choice(turnos, n, p=[0.45, 0.40, 0.15])

    llamadas_base = np.random.randint(10, 30, n)
    bonus_dia = np.where(np.isin(dia_semana, [0, 4]), np.random.randint(4, 9, n), 0)
    bonus_dic = np.where(np.array(mes) == 12, np.random.randint(3, 7, n), 0)
    llamadas_por_turno = llamadas_base + bonus_dia + bonus_dic

    categoria_llamada = np.random.choice(categorias, n, p=[0.30, 0.25, 0.15, 0.20, 0.10])
    duracion_base = np.random.normal(8, 2, n)
    bonus_cancelacion = np.where(categoria_llamada == "Cancelacion", np.random.uniform(5, 10, n), 0)
    duracion_promedio = np.clip(duracion_base + bonus_cancelacion, 3, 25).round(1)

    score_base = 5 + (duracion_promedio * 0.15) + (np.array(experiencia) * 0.03)
    ruido = np.random.normal(0, 0.8, n)
    pen_sat = np.where(llamadas_por_turno > 25, -1.2, 0)
    pen_can = np.where(categoria_llamada == "Cancelacion", -1.5, 0)
    pen_noche = np.where((np.array(turno_asignado) == "Noche") & (np.array(mes) == 3), -2.0, 0)
    score_satisfaccion = np.clip(score_base + ruido + pen_sat + pen_can + pen_noche, 1, 10).round(1)

    score_qa_base = 60 + (np.array(experiencia) * 0.5) + np.random.normal(0, 8, n)
    pen_qa = np.where(llamadas_por_turno > 25, -8, 0)
    score_qa = np.clip(score_qa_base + pen_qa, 40, 100).round(1)

    tasa_base = np.clip(20 - (np.array(experiencia) * 0.2) + np.random.normal(0, 3, n), 2, 40)
    tasa_error = np.where(ids_agentes == "AG04", tasa_base * 1.8, tasa_base).round(1)

    prob_res = np.clip(0.4 + (np.array(experiencia) * 0.01), 0.4, 0.85)
    resolucion = [np.random.choice(["Si", "No"], p=[p, 1-p]) for p in prob_res]

    dias_nombres = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

    df = pd.DataFrame({
        "fecha":                 [f.strftime("%Y-%m-%d") for f in fechas],
        "mes":                   mes,
        "dia_semana":            [dias_nombres[d] for d in dia_semana],
        "id_agente":             ids_agentes,
        "nombre_agente":         nombres_agentes,
        "experiencia_meses":     experiencia,
        "turno":                 turno_asignado,
        "categoria_llamada":     categoria_llamada,
        "llamadas_por_turno":    llamadas_por_turno,
        "duracion_promedio_min": duracion_promedio,
        "score_satisfaccion":    score_satisfaccion,
        "score_qa":              score_qa,
        "tasa_error_pct":        tasa_error,
        "resolucion_primera":    resolucion,
    })
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

df = load_data()

st.title("QA Call Center Performance Dashboard")
st.markdown(
    "**Para:** Supervisores de Calidad | "
    "**Pregunta central:** Que patrones de desempeno, riesgo y saturacion existen en el equipo de agentes?"
)
st.divider()

st.sidebar.header("Filtros")
fecha_min = df["fecha"].min()
fecha_max = df["fecha"].max()
rango_fechas = st.sidebar.date_input("Rango de fechas", value=(fecha_min, fecha_max), min_value=fecha_min, max_value=fecha_max)

turnos_disponibles = ["Todos"] + sorted(df["turno"].unique().tolist())
turno_sel = st.sidebar.selectbox("Turno", turnos_disponibles)

cats_disponibles = ["Todas"] + sorted(df["categoria_llamada"].unique().tolist())
cat_sel = st.sidebar.selectbox("Categoria", cats_disponibles)

agentes_disponibles = ["Todos"] + sorted(df["nombre_agente"].unique().tolist())
agente_sel = st.sidebar.selectbox("Agente", agentes_disponibles)

df_f = df[(df["fecha"] >= pd.to_datetime(rango_fechas[0])) & (df["fecha"] <= pd.to_datetime(rango_fechas[1]))]
if turno_sel != "Todos":
    df_f = df_f[df_f["turno"] == turno_sel]
if cat_sel != "Todas":
    df_f = df_f[df_f["categoria_llamada"] == cat_sel]
if agente_sel != "Todos":
    df_f = df_f[df_f["nombre_agente"] == agente_sel]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Registros", f"{len(df_f):,}")
col2.metric("Score QA Promedio", f"{df_f['score_qa'].mean():.1f} / 100")
col3.metric("Satisfaccion Promedio", f"{df_f['score_satisfaccion'].mean():.1f} / 10")
col4.metric("Tasa de Error Promedio", f"{df_f['tasa_error_pct'].mean():.1f}%")
st.divider()

st.subheader("Score QA promedio por agente")
qa_ag = df_f.groupby("nombre_agente")["score_qa"].mean().reset_index().sort_values("score_qa", ascending=False)
fig1 = px.bar(qa_ag, x="nombre_agente", y="score_qa", color="score_qa", color_continuous_scale="teal", text_auto=".1f", labels={"nombre_agente": "Agente", "score_qa": "Score QA"})
fig1.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white", coloraxis_showscale=False)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Tasa de error vs Score QA por agente")
sc_data = df_f.groupby("nombre_agente").agg(score_qa=("score_qa","mean"), tasa_error=("tasa_error_pct","mean"), llamadas=("llamadas_por_turno","sum")).reset_index()
fig2 = px.scatter(sc_data, x="score_qa", y="tasa_error", size="llamadas", color="nombre_agente", text="nombre_agente", labels={"score_qa":"Score QA","tasa_error":"Tasa de Error (%)","nombre_agente":"Agente"})
fig2.update_traces(textposition="top center")
fig2.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Volumen de llamadas por mes")
meses_nombre = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
vol_mes = df_f.groupby("mes")["llamadas_por_turno"].sum().reset_index()
vol_mes["mes_nombre"] = vol_mes["mes"].map(meses_nombre)
fig3 = px.line(vol_mes, x="mes_nombre", y="llamadas_por_turno", markers=True, labels={"mes_nombre":"Mes","llamadas_por_turno":"Total Llamadas"})
fig3.update_traces(line_color="#00b4d8", marker_color="#90e0ef")
fig3.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Satisfaccion promedio por turno y categoria")
heat = df_f.pivot_table(values="score_satisfaccion", index="turno", columns="categoria_llamada", aggfunc="mean").round(1)
fig4 = px.imshow(heat, color_continuous_scale="RdYlGn", aspect="auto", text_auto=True, labels={"color":"Score"})
fig4.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Distribucion de Score QA por dia de la semana")
fig5 = px.box(df_f, x="dia_semana", y="score_qa", color="dia_semana", category_orders={"dia_semana":["Lun","Mar","Mie","Jue","Vie","Sab","Dom"]}, labels={"dia_semana":"Dia","score_qa":"Score QA"})
fig5.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white", showlegend=False)
st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("Dashboard generado con datos sinteticos | Maestria en Modelos Analiticos | 2026")
