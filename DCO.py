# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from PIL import Image
import os

# Configuración de página
st.set_page_config(page_title="CRTL de DCO's", page_icon="📄", layout="wide")

# --- ESTILO UNIFICADO PARA EL SIDEBAR ---
st.markdown("""
    <style>
        /* Forzar tamaño de letra idéntico en el menú lateral */
        [data-testid="stSidebarNav"] span {
            font-size: 20px !important; /* Ajusta este número a tu gusto */
            font-weight: bold !important;
            text-transform: capitalize;
        }
    </style>
""", unsafe_allow_html=True)

# Carga de Logo
try:
    logo_path = os.path.join(os.path.dirname(__file__), "EA_2.png")
    image = Image.open(logo_path)
    st.sidebar.image(image, use_container_width=True)
except:
    st.sidebar.error("Logo no encontrado")

st.sidebar.markdown("<h3 style='text-align: center;'>Soporte Eléctrico</h3>", unsafe_allow_html=True)
st.sidebar.divider()

# Estilo para que los nombres en el sidebar se vean mejor
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] span { font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. GESTIÓN DE ESTADO (Para evitar cierres)
# ==========================================
if "maquina_seleccionada" not in st.session_state:
    st.session_state.maquina_seleccionada = None

if st.session_state.maquina_seleccionada is None:
    st_autorefresh(interval=10000, key="refresh_global")

st.title("📄 Panel de control de documentos")

# Fíjate que termina en &gid=989718143 (sin el símbolo #)
CSV_URL = "https://docs.google.com/spreadsheets/d/1G6BpbdZ4Ve6MQpAA85I5Ya9Fz2MNH4i5YBSqbvrCNL4/export?format=csv&gid=989718143"

@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        # 1. Limpiar espacios en blanco en los nombres de las columnas
        df.columns = df.columns.str.strip()

        # 2. Mapeo flexible: intenta renombrar todas las variantes posibles
        df = df.rename(columns={
            "Marca temporal": "timestamp",
            "Nombre de la actividad": "actividad",
            "Descripcion de la actividad": "descripcion",
            "Fecha": "fecha",
            "Linea": "linea",
            "Línea": "linea",
            "Maquina": "maquina",
            "Agrega el archivo PDF o escaneado": "archivo"
        })

        # 3. --- BLOQUE ANTI-KEYERROR ---
        # Si 'linea' no existe tras el rename, la creamos para que Streamlit no se cierre
        columnas_criticas = ["linea", "maquina", "actividad", "descripcion"]
        for col in columnas_criticas:
            if col not in df.columns:
                df[col] = "Columna no encontrada"

        # 4. Procesamiento de datos (ahora es seguro porque la columna ya existe)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

        df["linea"] = df["linea"].astype(str).str.upper().str.strip()
        df["maquina"] = df["maquina"].astype(str).str.upper().str.strip()

        return df.sort_values("timestamp", ascending=False)
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = cargar_datos(CSV_URL)

# --- Filtros ---
lineas = ["Todas"] + sorted(df["linea"].dropna().unique().tolist())
maquinas = ["Todas"] + sorted(df["maquina"].dropna().unique().tolist())

col_f1, col_f2 = st.columns(2)
with col_f1:
    linea_sel = st.selectbox("Filtrar por Línea", lineas)
with col_f2:
    maquina_sel = st.selectbox("Filtrar por Máquina", maquinas)

df_filtrado = df.copy()
if linea_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["linea"] == linea_sel]
if maquina_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["maquina"] == maquina_sel]

df_cards = df_filtrado.drop_duplicates(subset=['linea', 'maquina'], keep='first')

# ==========================================
# 2. DEFINICIÓN DEL DIÁLOGO
# ==========================================
@st.dialog("Historial de actualizaciones")
def mostrar_dialogo_historial():
    seleccion = st.session_state.maquina_seleccionada
    if seleccion:
        linea = seleccion["linea"]
        maquina = seleccion["maquina"]
        hist = df[(df["linea"] == linea) & (df["maquina"] == maquina)]
        hist = hist.sort_values("timestamp", ascending=False)

        st.subheader(f"Registro de: {maquina}")
        st.caption(f"Línea: {linea}")
        st.divider()

        if hist.empty:
            st.info("⚠️ No hay historial disponible.")
        else:
            for _, row in hist.iterrows():
                label = f"📅 {row['fecha']} - {row['actividad']}"
                with st.expander(label):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown("<p style='text-align: center;'><b>Descripción:</b></p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align: center;'>{row['descripcion']}</p>", unsafe_allow_html=True)
                    with c2:
                        st.link_button("📂 Ver Documento", str(row['archivo']))

        if st.button("Cerrar"):
            st.session_state.maquina_seleccionada = None
            st.rerun()

if st.session_state.maquina_seleccionada is not None:
    mostrar_dialogo_historial()

# ==========================================
# 3. VISUALIZACIÓN DE CARDS
# ==========================================
st.caption(f"Mostrando {len(df_cards)} máquinas registradas")

if len(df_cards) == 0:
    st.info("⚠️ No hay registros disponibles.")
else:
    n_cols = 3
    for i in range(0, len(df_cards), n_cols):
        cols = st.columns(n_cols)
        for col, (_, row) in zip(cols, df_cards.iloc[i:i+n_cols].iterrows()):
            with col:
                with st.container(border=True):
                    st.subheader(row["maquina"])
                    st.write(f"📍 **Línea:** {row['linea']}")
                    st.write(f"⏱️ **Última act:** {row['actividad']}")
                    st.caption(f"Fecha: {row['fecha']}")
                    if st.button("📄 Ver Historial", key=f"btn_{row['linea']}_{row['maquina']}"):
                        st.session_state.maquina_seleccionada = {"linea": row['linea'], "maquina": row['maquina']}
                        st.rerun()

st.markdown("<br><hr><p style='text-align:center; color:gray;'>Gestión de Documentos | Developed by Erik Armenta</p>", unsafe_allow_html=True)








