# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 15:42:59 2025

@author: acer
"""

import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Configuración de página
st.set_page_config(page_title="CRTL de DCO's", page_icon="📄", layout="wide")

# 1. AUTO-REFRESH EFECTIVO
# Al usar ttl=10 en el cache y refresh cada 10s, forzamos la lectura del CSV
st_autorefresh(interval=10000, key="refresh")

st.title("Dashboard de Actividades")

CSV_URL = "https://docs.google.com/spreadsheets/d/1usygK9pJTsMOkcvXFByrn0d0yqjJiJX9Vl715UIz1bY/export?format=csv&gid=1905231957"

# 2. CACHÉ DINÁMICO
# Agregamos ttl (Time To Live) para que el cache expire solo cada 10 segundos
@st.cache_data(ttl=10)
def cargar_datos(url):
    df = pd.read_csv(url)
    df = df.rename(columns={
        "Marca temporal": "timestamp",
        "Nombre de la Actividad": "actividad",
        "Descipcion": "descripcion",
        "Fecha": "fecha",
        "Linea": "linea",
        "Maquina": "maquina",
        "Agrega el archivo PDF o escaneado": "archivo"
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp", ascending=False)
    return df

df = cargar_datos(CSV_URL)

# Filtros
lineas = ["Todas"] + sorted(df["linea"].dropna().unique())
maquinas = ["Todas"] + sorted(df["maquina"].dropna().unique())

linea_sel = st.selectbox("Filtrar por Línea", lineas)
maquina_sel = st.selectbox("Filtrar por Máquina", maquinas)

df_filtrado = df.copy()
if linea_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["linea"] == linea_sel]
if maquina_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina_sel]

# ========================
# 3. LÓGICA DE AGRUPACIÓN (Única Card por Máquina)
# ========================
# Creamos un DataFrame que solo contenga la última actividad de cada máquina para la Card
df_cards = df_filtrado.drop_duplicates(subset=['linea', 'maquina'], keep='first')

st.caption(f"Mostrando {len(df_cards)} máquinas registradas")

@st.dialog("Historial de actualizaciones")
def ver_historial(linea, maquina):
    # Buscamos TODO el historial de esa máquina específica
    hist = df[ (df["linea"] == linea) & (df["maquina"] == maquina) ]
    hist = hist.sort_values("timestamp", ascending=False)

    st.subheader(f"Historial: {maquina} ({linea})")
    st.divider()

    if hist.empty:
        st.info("⚠️ No hay historial disponible.")
    else:
        for _, row in hist.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📅 {row['fecha']}**")
                    st.markdown(f"**Actividad:** {row['actividad']}")
                    st.write(f"{row['descripcion']}")
                with col2:
                    st.markdown(f"[⬇️ Descargar]({row['archivo']})")
                st.divider()

# ========================
# Visualización de Cards
# ========================
if len(df_cards) == 0:
    st.info("⚠️ No hay registros disponibles para los filtros seleccionados.")
else:
    n_cols = 3
    # Iteramos sobre las máquinas únicas
    for i in range(0, len(df_cards), n_cols):
        cols = st.columns(n_cols)
        for col, (_, row) in zip(cols, df_cards.iloc[i:i+n_cols].iterrows()):
            with col:
                with st.container(border=True):
                    st.subheader(row["maquina"])
                    st.write(f"📍 **Línea:** {row['linea']}")
                    st.write(f"⏱️ **Última act:** {row['actividad']}")
                    st.caption(f"Fecha: {row['fecha']}")

                    # El botón de historial ahora filtra por la máquina de esta card
                    if st.button("📄 Ver Historial Completo", key=f"btn_{row['linea']}_{row['maquina']}"):
                        ver_historial(row["linea"], row["maquina"])

# ========================
# Footer
# ========================
st.markdown(
    "<hr><p style='text-align:center; color:gray; font-size:14px;'>"
    "Gestión de Documentos de Soporte Electrico | Developed by Master Engineer Erik Armenta"
    "</p>",
    unsafe_allow_html=True
)







