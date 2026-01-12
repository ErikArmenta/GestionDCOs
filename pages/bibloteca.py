# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from PIL import Image
import os

# Configuración de página
st.set_page_config(page_title="Biblioteca Soporte Eléctrico", page_icon="📚", layout="wide")

# --- ESTILO UNIFICADO PARA EL SIDEBAR ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] span {
            font-size: 20px !important;
            font-weight: bold !important;
            text-transform: capitalize;
        }
    </style>
""", unsafe_allow_html=True)

# Carga de Logo
try:
    # Al estar en /pages, subimos un nivel para buscar la imagen
    logo_path = os.path.join(os.path.dirname(__file__), "..", "EA_2.png")
    image = Image.open(logo_path)
    st.sidebar.image(image, use_container_width=True)
except:
    st.sidebar.error("Logo no encontrado")

st.sidebar.markdown("<h3 style='text-align: center;'>Soporte Eléctrico</h3>", unsafe_allow_html=True)
st.sidebar.divider()

CSV_URL_BIBLIOTECA = "https://docs.google.com/spreadsheets/d/1G6BpbdZ4Ve6MQpAA85I5Ya9Fz2MNH4i5YBSqbvrCNL4/export?format=csv&gid=1068115575"

@st.cache_data(ttl=60)
def cargar_datos_biblioteca(url):
    try:
        df = pd.read_csv(url)
        # 1. Estandarizar nombres de columnas a minúsculas
        df.columns = df.columns.str.strip().str.lower()

        # 2. Renombrar usando los nombres en minúscula
        df = df.rename(columns={
            "marca temporal": "timestamp",
            "nombre del documento": "nombre",
            "equipo o maquina relacionado": "equipo",
            "categoria del recurso": "categoria",
            "descripcion breve": "descripcion",
            "subir archivo_rec": "archivo"
        })

        # 3. Forzar mayúsculas para las etiquetas de las cards
        cols_to_upper = ["nombre", "equipo", "categoria"]
        for col in cols_to_upper:
            if col in df.columns:
                df[col] = df[col].astype(str).str.upper().str.strip()

        return df.sort_values("nombre", ascending=True)
    except Exception as e:
        st.error(f"Error en Biblioteca: {e}")
        return pd.DataFrame()

st.title("📚 Biblioteca Técnica de Soporte")
st.caption("Acceso rápido a manuales, programas de PLC y procedimientos.")

df_bib = cargar_datos_biblioteca(CSV_URL_BIBLIOTECA)

if not df_bib.empty:
    # --- Filtros ---
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        categorias = ["Todas"] + sorted(df_bib["categoria"].unique().tolist())
        cat_sel = st.selectbox("Filtrar por Categoría", categorias)
    with col_f2:
        equipos = ["Todos"] + sorted(df_bib["equipo"].unique().tolist())
        eq_sel = st.selectbox("Filtrar por Equipo", equipos)

    df_filtrado = df_bib.copy()
    if cat_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_sel]
    if eq_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["equipo"] == eq_sel]

    st.divider()

    # ==========================================
    # VISUALIZACIÓN EN CARDS (ESTILO PÁGINA 1)
    # ==========================================
    if len(df_filtrado) == 0:
        st.info("No se encontraron documentos con esos filtros.")
    else:
        n_cols = 3  # Número de tarjetas por fila
        for i in range(0, len(df_filtrado), n_cols):
            cols = st.columns(n_cols)
            for col, (_, row) in zip(cols, df_filtrado.iloc[i:i+n_cols].iterrows()):
                with col:
                    with st.container(border=True):
                        # Título del documento en negritas
                        st.subheader(row["nombre"])
                        st.write(f"⚙️ **EQUIPO:** {row['equipo']}")
                        st.write(f"📂 **CATEGORÍA:** {row['categoria']}")

                        # Descripción centrada dentro de la card
                        st.markdown(f"<p style='text-align: center; color: #555; font-size: 0.9rem;'><i>{row['descripcion']}</i></p>", unsafe_allow_html=True)

                        # Botón de acción
                        st.link_button("📂 DESCARGAR / VER", str(row['archivo']), use_container_width=True)

else:
    st.warning("⚠️ No hay datos disponibles.")

# Footer
st.markdown("<br><hr><p style='text-align:center; color:gray;'>Biblioteca Técnica | Developed by Erik Armenta</p>", unsafe_allow_html=True)
