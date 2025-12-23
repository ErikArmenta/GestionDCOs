# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 15:42:59 2025

@author: acer
"""

import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# ========================
# Auto-refresh cada 10 segundos
# ========================
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="CRTL de DCO's", page_icon="📄", layout="wide")
st.title("Dashboard de Actividades")

CSV_URL = "https://docs.google.com/spreadsheets/d/1usygK9pJTsMOkcvXFByrn0d0yqjJiJX9Vl715UIz1bY/export?format=csv&gid=1905231957"

@st.cache_data
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

lineas = ["Todas"] + sorted(df["linea"].dropna().unique())
maquinas = ["Todas"] + sorted(df["maquina"].dropna().unique())

linea_sel = st.selectbox("Filtrar por Línea", lineas)
maquina_sel = st.selectbox("Filtrar por Máquina", maquinas)

df_filtrado = df.copy()
if linea_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["linea"] == linea_sel]
if maquina_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina_sel]

st.caption(f"Mostrando {len(df_filtrado)} registros")

# ========================
# Modal para ver historial
# ========================
@st.dialog("Historial de actualizaciones")
def ver_historial(linea, maquina):
    hist = df_filtrado.copy()
    hist = hist[(hist["linea"] == linea) & (hist["maquina"] == maquina)]
    hist = hist.sort_values("timestamp", ascending=False)

    if hist.empty:
        st.info("⚠️ No hay historial disponible para esta línea/máquina.")
    else:
        for _, row in hist.iterrows():
            st.markdown(f"**{row['timestamp'].strftime('%Y-%m-%d %H:%M')}** - {row['actividad']}")
            st.write(row["descripcion"])
            st.markdown(f"[Ver PDF]({row['archivo']}) 🔗")

# ========================
# Cards (solo info + links)
# ========================
if len(df_filtrado) == 0:
    st.info("⚠️ No hay registros disponibles para los filtros seleccionados.")
else:
    n_cols = 3
    rows = [df_filtrado.iloc[i:i+n_cols] for i in range(0, len(df_filtrado), n_cols)]

    for row_group in rows:
        cols = st.columns(n_cols)
        for col, (_, row) in zip(cols, row_group.iterrows()):
            with col:
                with st.container(border=True):
                    st.subheader(row["actividad"])
                    st.write(row["descripcion"])
                    st.write(f"📅 Fecha: {row['fecha']}")
                    st.write(f"🏭 Línea: {row['linea']} | ⚙️ Máquina: {row['maquina']}")

                    # Botón para abrir modal con historial
                    if st.button("📄 Historial", key=f"hist_{row.name}"):
                        ver_historial(row["linea"], row["maquina"])

                    # Link directo al PDF
                    st.markdown(f"[⬇️ Descargar PDF]({row['archivo']})")


# ========================
# Footer
# ========================
st.markdown(
    "<hr><p style='text-align:center; color:gray; font-size:14px;'>"
    "Gestión de Documentos de Soporte Electrico | Developed by Master Engineer Erik Armenta"
    "</p>",
    unsafe_allow_html=True
)







