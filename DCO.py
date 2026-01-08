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

st.title("Panel de control de documentos")

CSV_URL = "https://docs.google.com/spreadsheets/d/1usygK9pJTsMOkcvXFByrn0d0yqjJiJX9Vl715UIz1bY/export?format=csv&gid=1905231957"

# 2. CACHÉ DINÁMICO
# Agregamos ttl (Time To Live) para que el cache expire solo cada 10 segundos
@st.cache_data(ttl=60)
def cargar_datos(url):
    df = pd.read_csv(url)
    
    # Limpiamos espacios en blanco accidentales en los nombres de las columnas
    df.columns = df.columns.str.strip()
    
    # Renombrado basado en tus nuevos encabezados
    # Nota: Asegúrate de que las mayúsculas coincidan exactamente con tu hoja
    df = df.rename(columns={
        "Marca temporal": "timestamp",
        "Nombre de la actividad": "actividad",
        "Descripcion de la actividad": "descripcion",
        "Fecha": "fecha",
        "Linea": "linea",
        "Maquina": "maquina",
        "Agrega el archivo PDF o escaneado": "archivo"
    })
    
    # Convertir fecha de registro
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Asegurarnos de que las columnas usadas en filtros existan para evitar errores
    for col in ["linea", "maquina", "actividad", "descripcion"]:
        if col not in df.columns:
            # Si una columna no se renombró bien, creamos una vacía para que no truene el dashboard
            df[col] = "No disponible"
            
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
    # Buscamos todo el historial de esa máquina específica
    hist = df[(df["linea"] == linea) & (df["maquina"] == maquina)]
    hist = hist.sort_values("timestamp", ascending=False)

    st.subheader(f"Registro de: {maquina}")
    st.caption(f"Línea: {linea}")
    st.divider()

    if hist.empty:
        st.info("⚠️ No hay historial disponible.")
    else:
        for _, row in hist.iterrows():
            # Creamos un expander por cada registro
            # El título del expander muestra la fecha y la actividad principal
            label = f"📅 {row['fecha']} - {row['actividad']}"

            with st.expander(label):
                col_info, col_doc = st.columns([1, 1])

                with col_info:
                    st.markdown("**Descripción:**")
                    st.write(row["descripcion"])
                    st.markdown(f"[⬇️ Descargar Documento]({row['archivo']})")

                with col_doc:
                    # Intentar visualizar el PDF si el navegador lo permite
                    # Nota: Algunos navegadores bloquean el embed de Drive por seguridad
                    st.markdown("**Vista previa rápida:**")
                    st.info("Haz clic en descargar para ver el archivo completo.")
                    # Si quieres intentar mostrarlo (opcional):
                    # st.markdown(f'<iframe src="{row["archivo"]}" width="100%" height="300px"></iframe>', unsafe_allow_html=True)

    if st.button("Cerrar"):
        st.rerun()

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











