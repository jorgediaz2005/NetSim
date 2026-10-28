import html
import json
import random
from datetime import datetime

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

import netsim_core as core
from netsim_core import COLORES, ICONOS, PLANTILLAS, SIMBOLOS, TIPOS

st.set_page_config(page_title="NetSim | Simulador de redes", page_icon="🌐",
                   layout="wide", initial_sidebar_state="expanded")

# =========================================================
# PALETA Y CONSTANTES VISUALES
# =========================================================
TEMAS = {  # nombre: (color principal, color secundario)
    "🌊 Océano": ("#4DA3FF", "#7C5CFF"),
    "🔮 Neón": ("#A78BFA", "#EC4899"),
    "🌅 Atardecer": ("#FB7185", "#F59E0B"),
    "🧊 Aurora": ("#2DD4BF", "#6366F1"),
}
_tema = st.session_state.get("tema_color", "🌊 Océano")
C_ACENTO, C_ACENTO2 = TEMAS.get(_tema, TEMAS["🌊 Océano"])

C_TEXTO = "#E6EDF3"
C_SUAVE = "#94A3B8"
C_RUTA = "#FFD166"
C_MAL = "#FF4D4F"

LAT_RAPIDO = 2   # ms: enlaces rápidos
LAT_LENTO = 6    # ms: enlaces lentos
COLOR_ENLACE = {"rapido": "#5EEAD4", "medio": "#94A3B8", "lento": "#C084FC"}
ANCHO_ENLACE = {"rapido": 3.2, "medio": 2.4, "lento": 1.8}

# =========================================================
# CONFIGURACIÓN Y ESTILO
# =========================================================

CSS = """
<style>
:root {
    --line: rgba(255,255,255,.09);
    --card: rgba(255,255,255,.04);
    --accent: #4DA3FF;
    --accent2: #7C5CFF;
    --ok: #2ECC71;
    --warn: #F5A623;
    --bad: #FF4D4F;
}
.stApp {
    background:
        radial-gradient(1100px 560px at 8% -8%, rgba(77,163,255,.14), transparent 60%),
        radial-gradient(900px 520px at 100% 0%, rgba(124,92,255,.12), transparent 55%),
        #0B0F1A;
}
.block-container {padding-top: 1.1rem; padding-bottom: 2.5rem; max-width: 1500px;}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* ---------- Barra lateral ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121A2B 0%, #0B0F1A 100%);
    border-right: 1px solid var(--line);
}
.brand {display:flex; align-items:center; gap:.7rem; margin: .2rem 0 .8rem 0;}
.brand-logo {
    width: 42px; height: 42px; border-radius: 12px; display:flex; align-items:center;
    justify-content:center; font-size: 1.4rem;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    box-shadow: 0 6px 20px rgba(77,163,255,.35);
}
.brand-name {font-weight: 800; font-size: 1.15rem; letter-spacing:.3px; line-height:1.1;}
.brand-sub {font-size:.75rem; opacity:.6; letter-spacing:.6px; text-transform:uppercase;}
.side-title {
    font-size:.72rem; font-weight:700; letter-spacing:1.2px; text-transform:uppercase;
    color: var(--accent); margin: .9rem 0 .35rem 0;
}

/* ---------- Cabecera ---------- */
.hero {
    position: relative; overflow: hidden; display:flex; justify-content:space-between; align-items:center;
    gap: 1rem; padding: 1.5rem 1.8rem; border-radius: 22px; margin-bottom: 1.1rem;
    background: linear-gradient(120deg, #101a33, #14213f 40%, #1a1740 70%, #101a33);
    background-size: 220% 220%; animation: shift 16s ease infinite;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 10px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
}
.hero::before {
    content:""; position:absolute; inset:0; pointer-events:none;
    background:
        radial-gradient(500px 220px at 12% 0%, rgba(77,163,255,.28), transparent 60%),
        radial-gradient(420px 220px at 95% 100%, rgba(124,92,255,.25), transparent 60%);
}
.hero-text {position: relative; z-index: 1;}
.hero-eyebrow {font-size:.72rem; letter-spacing:2px; opacity:.65; font-weight:600;}
.hero h1 {margin:.15rem 0 .1rem 0; font-size: 2.4rem; font-weight: 800; letter-spacing:.3px; padding:0;}
.hero h1 span {
    background: linear-gradient(90deg, #4DA3FF, #9B8CFF);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p {margin:.2rem 0 .8rem 0; opacity:.8;}
.hero-chips {display:flex; flex-wrap:wrap; gap:.5rem; align-items:center;}
.chip {
    padding:.28rem .75rem; border-radius:999px; font-size:.8rem; font-weight:600;
    background: rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12);
}
.status {
    display:inline-flex; align-items:center; gap:.45rem; padding:.28rem .8rem; border-radius:999px;
    font-size:.8rem; font-weight:700; letter-spacing:.5px;
}
.status .dot {width:9px; height:9px; border-radius:50%; display:inline-block; animation: pulse-dot 1.8s ease-in-out infinite;}
.status-ok   {background:rgba(46,204,113,.15); color:#2ECC71; border:1px solid rgba(46,204,113,.45);}
.status-ok .dot {background:#2ECC71; box-shadow:0 0 0 0 rgba(46,204,113,.7);}
.status-warn {background:rgba(245,166,35,.15); color:#F5A623; border:1px solid rgba(245,166,35,.45);}
.status-warn .dot {background:#F5A623; box-shadow:0 0 0 0 rgba(245,166,35,.7);}
.status-bad  {background:rgba(255,77,79,.15); color:#FF6B6D; border:1px solid rgba(255,77,79,.5);}
.status-bad .dot {background:#FF4D4F; box-shadow:0 0 0 0 rgba(255,77,79,.7);}
.hero-art {position: relative; z-index:1; width: 260px; height: 140px; flex-shrink:0;}
.hero-art line {stroke-dasharray: 4 6; animation: flow 3s linear infinite;}
.hero-art circle {transform-box: fill-box; transform-origin: center; animation: node-pulse 3s ease-in-out infinite;}
.hero-art circle:nth-of-type(2n) {animation-delay: .8s;}
.hero-art circle:nth-of-type(3n) {animation-delay: 1.6s;}

@keyframes shift {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}
@keyframes flow {to {stroke-dashoffset: -20;}}
@keyframes node-pulse {0%,100%{transform:scale(1); opacity:.95} 50%{transform:scale(1.25); opacity:1}}
@keyframes pulse-dot {
    0%   {box-shadow:0 0 0 0 currentColor; opacity:1;}
    70%  {box-shadow:0 0 0 9px rgba(0,0,0,0); opacity:.85;}
    100% {box-shadow:0 0 0 0 rgba(0,0,0,0); opacity:1;}
}
@keyframes rise {from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:none;}}

/* ---------- Tarjetas KPI ---------- */
.kpi {
    display:flex; align-items:center; gap:.9rem; padding: 1rem 1.1rem; border-radius: 18px;
    background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid var(--line); position: relative; overflow:hidden;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
    animation: rise .5s ease both;
}
.kpi::before {content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background: var(--k);}
.kpi:hover {transform: translateY(-3px); border-color: var(--k); box-shadow: 0 10px 28px rgba(0,0,0,.35);}
.kpi-info {--k:#4DA3FF;} .kpi-ok {--k:#2ECC71;} .kpi-warn {--k:#F5A623;} .kpi-bad {--k:#FF4D4F;}
.kpi-ico {
    width:46px; height:46px; border-radius:14px; display:flex; align-items:center; justify-content:center;
    font-size:1.45rem; flex-shrink:0; background: color-mix(in srgb, var(--k) 18%, transparent);
}
.kpi-label {font-size:.76rem; opacity:.7; text-transform:uppercase; letter-spacing:.8px; font-weight:600;}
.kpi-value {font-size:1.7rem; font-weight:800; line-height:1.15;}
.kpi-sub {font-size:.78rem; opacity:.65;}

/* ---------- Métricas nativas de Streamlit ---------- */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid var(--line); padding: 14px 16px; border-radius: 16px;
    transition: transform .2s ease, border-color .2s ease;
}
div[data-testid="stMetric"]:hover {transform: translateY(-2px); border-color: rgba(77,163,255,.5);}
div[data-testid="stMetricLabel"] p {opacity:.75; font-size:.85rem;}

/* ---------- Pestañas ---------- */
div[data-baseweb="tab-list"] {gap: .35rem; flex-wrap: wrap;}
button[data-baseweb="tab"] {
    border-radius: 999px; padding: .45rem 1.05rem; background: var(--card);
    border: 1px solid var(--line); height: auto; transition: all .2s ease;
}
button[data-baseweb="tab"]:hover {border-color: rgba(77,163,255,.55); background: rgba(77,163,255,.10);}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(77,163,255,.38), rgba(124,92,255,.38));
    border-color: rgba(77,163,255,.7); box-shadow: 0 4px 16px rgba(77,163,255,.22);
}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {display:none;}

/* ---------- Botones y expanders ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 12px; border: 1px solid var(--line); transition: all .18s ease;
    background: rgba(255,255,255,.04);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px); border-color: var(--accent); background: rgba(77,163,255,.14);
    box-shadow: 0 6px 18px rgba(77,163,255,.18);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4DA3FF, #7C5CFF); border: none; font-weight:700; color:white;
}
div[data-testid="stExpander"] {
    border-radius: 14px; border: 1px solid var(--line); background: var(--card); overflow:hidden;
}
div[data-testid="stDataFrame"] {border-radius: 14px; overflow:hidden; border:1px solid var(--line);}

/* ---------- Leyenda, ruta y títulos ---------- */
.legend {display:flex; flex-wrap:wrap; gap:.45rem .5rem; margin:.4rem 0 1rem 0;}
.lg {
    display:inline-flex; align-items:center; gap:.4rem; font-size:.76rem; padding:.22rem .65rem;
    border-radius: 999px; background: var(--card); border:1px solid var(--line); color:#CBD5E1;
}
.lg i {width:10px; height:10px; border-radius:50%; display:inline-block;}
.lg b {width:18px; height:4px; border-radius:3px; display:inline-block;}
.route {display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; margin:.4rem 0 1rem 0;}
.hop {
    padding:.45rem .85rem; border-radius:12px; font-weight:700;
    background: linear-gradient(135deg, rgba(255,209,102,.20), rgba(255,209,102,.06));
    border:1px solid rgba(255,209,102,.55);
}
.hop-link {font-size:.8rem; opacity:.85; color:#FFD166; font-weight:600;}
.sec {
    font-size:1.05rem; font-weight:700; margin: 1.2rem 0 .5rem 0; display:flex; align-items:center; gap:.5rem;
}
.sec::after {content:""; flex:1; height:1px; background: linear-gradient(90deg, var(--line), transparent);}
.scenario {margin: .2rem 0 1rem 0; font-size:.88rem; opacity:.9;}
.tag {
    display:inline-block; padding:.12rem .6rem; border-radius:999px; font-size:.78rem; margin:.1rem .25rem .1rem 0;
    background: rgba(255,77,79,.14); border:1px solid rgba(255,77,79,.4); color:#FF8A8C;
}

/* ---------- Ficha del inspector ---------- */
.ficha {
    padding: 1.1rem 1.2rem; border-radius: 20px; margin: .4rem 0 1rem 0;
    background: linear-gradient(145deg, rgba(77,163,255,.10), rgba(255,255,255,.02));
    border: 1px solid rgba(77,163,255,.35); animation: rise .4s ease both;
}
.ficha-head {display:flex; align-items:center; gap:.9rem; margin-bottom:.9rem;}
.ficha-ico {
    width:56px; height:56px; border-radius:16px; display:flex; align-items:center; justify-content:center;
    font-size:1.8rem; background: linear-gradient(135deg, var(--accent), var(--accent2));
    box-shadow: 0 8px 22px rgba(77,163,255,.3);
}
.ficha-name {font-size:1.35rem; font-weight:800; line-height:1.15;}
.ficha-type {font-size:.85rem; opacity:.8; display:flex; align-items:center; gap:.5rem; flex-wrap:wrap;}
.ficha-grid {display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:.7rem; margin-bottom:.9rem;}
.nbs-title {font-size:.74rem; letter-spacing:1px; text-transform:uppercase; opacity:.65; margin-bottom:.4rem; font-weight:700;}
.nb {
    display:inline-block; padding:.3rem .75rem; margin:.15rem .3rem .15rem 0; border-radius:999px;
    font-size:.82rem; background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.14);
}
.nb-off {opacity:.5; text-decoration: line-through; border-color: rgba(255,77,79,.5);}

@media (max-width: 900px) {.hero-art {display:none;} .hero h1 {font-size:1.9rem;}}
</style>
"""
def _rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


# El tema elegido sustituye los colores principales del CSS
CSS = (CSS.replace("rgba(77,163,255,", f"rgba({_rgb(C_ACENTO)},")
          .replace("rgba(124,92,255,", f"rgba({_rgb(C_ACENTO2)},")
          .replace("#4DA3FF", C_ACENTO).replace("#7C5CFF", C_ACENTO2).replace("#9B8CFF", C_ACENTO2))
st.markdown("\n".join(linea for linea in CSS.splitlines() if linea.strip()), unsafe_allow_html=True)


# =========================================================
# UTILIDADES DE DISEÑO
# =========================================================
def _h(texto):
    """Colapsa HTML en una línea (evita que Markdown lo interprete como bloque de código)."""
    return "".join(linea.strip() for linea in texto.splitlines())


def esc(x):
    return html.escape(str(x))


def rgba(color_hex, alpha):
    h = color_hex.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def kpi(icono, etiqueta, valor, sub="", tono="info", tip=""):
    return _h(f'<div class="kpi kpi-{tono}" title="{esc(tip)}"><div class="kpi-ico">{icono}</div>'
              f'<div><div class="kpi-label">{esc(etiqueta)}</div><div class="kpi-value">{esc(valor)}</div>'
              f'<div class="kpi-sub">{esc(sub)}</div></div></div>')


def seccion(titulo):
    st.markdown(f'<div class="sec">{esc(titulo)}</div>', unsafe_allow_html=True)


def estilo_fig(fig, alto=None, margen=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"), hoverlabel=dict(font_size=13, bgcolor="#111827", bordercolor="#334155"),
        margin=margen or dict(l=10, r=10, t=10, b=10))
    if alto:
        fig.update_layout(height=alto)
    return fig


def mostrar(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


def tramo_enlace(lat):
    return "rapido" if lat <= LAT_RAPIDO else ("medio" if lat < LAT_LENTO else "lento")


def cadena_ruta(ruta, g):
    partes = []
    for i, n in enumerate(ruta):
        tipo = g.nodes[n].get("tipo", "Otro")
        partes.append(f'<span class="hop">{ICONOS.get(tipo, "")} {esc(n)}</span>')
        if i < len(ruta) - 1:
            lat = g[n][ruta[i + 1]].get("weight", 1)
            partes.append(f'<span class="hop-link">— {lat:g} ms ➜</span>')
    return _h('<div class="route">' + "".join(partes) + "</div>")


def leyenda_mapa():
    return _h(f"""<div class="legend">
<span class="lg"><i style="background:{COLORES['Baja']}"></i>Criticidad baja</span>
<span class="lg"><i style="background:{COLORES['Media']}"></i>Media</span>
<span class="lg"><i style="background:{COLORES['Alta']}"></i>Alta</span>
<span class="lg"><b style="background:{COLOR_ENLACE['rapido']}"></b>Enlace rápido (≤ {LAT_RAPIDO} ms)</span>
<span class="lg"><b style="background:{COLOR_ENLACE['medio']}"></b>Medio</span>
<span class="lg"><b style="background:{COLOR_ENLACE['lento']}"></b>Lento (≥ {LAT_LENTO} ms)</span>
<span class="lg"><b style="background:{C_RUTA}"></b>Ruta calculada</span>
<span class="lg"><b style="background:{C_MAL};opacity:.6"></b>Enlace interrumpido</span>
<span class="lg" style="color:{C_MAL}">✖ Dispositivo caído</span>
</div>""")


# =========================================================
# ESTADO
# =========================================================
if "red" not in st.session_state:
    st.session_state.red = core.crear_red_inicial()
for clave, valor in {"sel_fallos": [], "sel_enlaces": [], "posiciones": None, "firma_pos": None}.items():
    st.session_state.setdefault(clave, valor)

G = st.session_state.red


def clave_enlace(u, v):
    return tuple(sorted((u, v)))


def reiniciar_escenario():
    st.session_state.sel_fallos = []
    st.session_state.sel_enlaces = []


def cambiar_red(nueva):
    st.session_state.red = nueva
    reiniciar_escenario()
    st.session_state.posiciones = None
    for k in ("ruta_origen", "ruta_destino", "inspector"):
        st.session_state.pop(k, None)


# Limpia selecciones que ya no existen (tras borrar elementos)
st.session_state.sel_fallos = [n for n in st.session_state.sel_fallos if n in G]
st.session_state.sel_enlaces = [e for e in st.session_state.sel_enlaces
                                if len(e) == 2 and G.has_edge(*e)]


# ---- callbacks de acciones rápidas ----
def _limpiar():
    reiniciar_escenario()
    st.toast("Escenario limpiado: todos los elementos activos", icon="🧹")


def _fallo_aleatorio():
    if G.number_of_nodes():
        elegido = random.choice(list(G.nodes))
        st.session_state.sel_fallos = [elegido]
        st.toast(f"Fallo aleatorio: {elegido}", icon="🎲")


def _peor_caso():
    df = core.impacto_dispositivos(G)
    if not df.empty:
        peor = df.iloc[0]["Dispositivo"]
        st.session_state.sel_fallos = [peor]
        st.toast(f"Peor caso: cae {peor}", icon="💥")


# Los cambios de red se hacen en callbacks: así se ejecutan ANTES de dibujar los
# selectores de fallos y Streamlit permite modificar su estado.
def _cargar_plantilla():
    nombre = st.session_state.plantilla_sel
    cambiar_red(PLANTILLAS[nombre]())
    st.toast(f"Plantilla «{nombre}» cargada", icon="📐")


def _importar():
    archivo = st.session_state.get("archivo_json")
    if archivo is None:
        st.session_state.msg_import = ("error", "Primero selecciona un archivo JSON.")
        return
    try:
        cambiar_red(core.red_desde_dict(json.load(archivo)))
        st.session_state.msg_import = ("ok", "Topología importada correctamente.")
        st.toast("Topología importada", icon="📂")
    except Exception as e:  # noqa: BLE001
        st.session_state.msg_import = ("error", f"No se pudo importar el archivo: {e}")


def _aplicar_mejora(u, v, lat):
    st.session_state.red.add_edge(u, v, weight=int(lat))
    st.session_state.posiciones = None
    st.toast(f"Enlace añadido: {u} ↔ {v}", icon="🛠️")


@st.cache_data(show_spinner=False)
def _sugerencias(clave):
    return core.sugerir_enlaces(core.red_desde_dict(json.loads(clave)), 3)


@st.cache_data(show_spinner=False)
def _plantillas():
    return core.comparar_plantillas()


# =========================================================
# BARRA LATERAL
# =========================================================
def titulo_lateral(texto):
    st.markdown(f'<div class="side-title">{texto}</div>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown(_h('<div class="brand"><div class="brand-logo">🌐</div><div>'
                   '<div class="brand-name">NetSim</div><div class="brand-sub">Panel de control</div>'
                   '</div></div>'), unsafe_allow_html=True)

    titulo_lateral("⚠️ Escenario de fallos")
    st.multiselect("Dispositivos desactivados", sorted(G.nodes()), key="sel_fallos",
                   help="Se aplican al instante; la topología base no se modifica.")
    opciones_enlaces = [clave_enlace(u, v) for u, v in G.edges()]
    st.multiselect("Enlaces interrumpidos", opciones_enlaces, key="sel_enlaces",
                   format_func=lambda e: f"{e[0]} ↔ {e[1]} ({G[e[0]][e[1]].get('weight', 1)} ms)")
    b1, b2, b3 = st.columns(3)
    b1.button("🧹 Limpiar", on_click=_limpiar, use_container_width=True)
    b2.button("🎲 Aleatorio", on_click=_fallo_aleatorio, use_container_width=True,
              help="Desactiva un dispositivo al azar")
    b3.button("💥 Peor caso", on_click=_peor_caso, use_container_width=True,
              help="Desactiva el dispositivo cuya caída incomunica a más pares")

    titulo_lateral("🏗️ Construir red")

    with st.expander("📐 Plantillas de topología"):
        st.selectbox("Plantilla (se carga al elegirla)", list(PLANTILLAS), key="plantilla_sel",
                     on_change=_cargar_plantilla)
        st.button("Recargar plantilla", on_click=_cargar_plantilla, use_container_width=True,
                  help="Vuelve a cargar la plantilla elegida, descartando los cambios hechos")

    with st.expander("➕ Añadir dispositivo"):
        with st.form("agregar_dispositivo", clear_on_submit=True):
            nombre_nuevo = st.text_input("Nombre", placeholder="Ej. PC 3")
            tipo_nuevo = st.selectbox("Tipo", TIPOS, index=3, format_func=lambda t: f"{ICONOS[t]} {t}")
            ok_disp = st.form_submit_button("Añadir", use_container_width=True)
        if ok_disp:
            nombre_nuevo = nombre_nuevo.strip()
            if not nombre_nuevo:
                st.error("Escribe un nombre.")
            elif nombre_nuevo in G:
                st.warning("Ya existe un dispositivo con ese nombre.")
            else:
                G.add_node(nombre_nuevo, tipo=tipo_nuevo)
                st.session_state.posiciones = None
                st.rerun()

    with st.expander("🔗 Añadir / editar conexión"):
        nodos = sorted(G.nodes())
        if len(nodos) < 2:
            st.info("Añade al menos dos dispositivos.")
        else:
            with st.form("conexion"):
                a = st.selectbox("Origen", nodos, key="con_a")
                b = st.selectbox("Destino", nodos, index=1, key="con_b")
                lat = st.number_input("Latencia (ms)", min_value=1, max_value=10000, value=5, step=1)
                ok_con = st.form_submit_button("Guardar conexión", use_container_width=True)
            st.caption("Si la conexión ya existe, se actualiza su latencia.")
            if ok_con:
                if a == b:
                    st.error("Origen y destino deben ser distintos.")
                else:
                    G.add_edge(a, b, weight=int(lat))
                    st.session_state.posiciones = None
                    st.rerun()

    with st.expander("🗑️ Eliminar elementos"):
        if G.number_of_nodes():
            nodo_borrar = st.selectbox("Dispositivo", sorted(G.nodes()), key="del_nodo")
            if st.button("Eliminar dispositivo", use_container_width=True):
                G.remove_node(nodo_borrar)
                st.session_state.posiciones = None
                st.rerun()
        if G.number_of_edges():
            enlace_borrar = st.selectbox("Conexión", opciones_enlaces, key="del_enlace",
                                         format_func=lambda e: f"{e[0]} ↔ {e[1]}")
            if st.button("Eliminar conexión", use_container_width=True):
                G.remove_edge(*enlace_borrar)
                st.session_state.posiciones = None
                st.rerun()

    titulo_lateral("🎨 Vista del mapa")
    layout_nombre = st.selectbox("Disposición del mapa",
                                 ["Resorte", "Circular", "Kamada-Kawai", "Capas (shell)"])
    mostrar_lat = st.toggle("Mostrar latencias", value=True)
    mostrar_ruta = st.toggle("Resaltar ruta calculada", value=True)
    mostrar_halo = st.toggle("Efecto de brillo en nodos", value=True)
    st.selectbox("Tema de color", list(TEMAS), key="tema_color")

# =========================================================
# ESCENARIO ACTIVO
# =========================================================
fallos = list(st.session_state.sel_fallos)
enlaces_fallidos = list(st.session_state.sel_enlaces)
G_sim = core.simular(G, fallos, enlaces_fallidos)
df_crit = core.criticidad_dispositivos(G_sim)

n_activos = G_sim.number_of_nodes()
n_enlaces = G_sim.number_of_edges()
comp_act = nx.number_connected_components(G_sim) if n_activos else 0
comp_orig = nx.number_connected_components(G) if G.number_of_nodes() else 0
pares_perdidos = core.pares_incomunicados(G, G_sim) if G.number_of_nodes() else []
clave_red = json.dumps(core.red_a_dict(G), sort_keys=True)  # identifica la topología para las cachés


# ---- ruta actual (se calcula antes de dibujar el mapa) ----
def ruta_actual():
    o, d = st.session_state.get("ruta_origen"), st.session_state.get("ruta_destino")
    if o is not None and d is not None and o in G_sim and d in G_sim and o != d \
            and nx.has_path(G_sim, o, d):
        r = nx.shortest_path(G_sim, o, d, weight="weight")
        return r, nx.shortest_path_length(G_sim, o, d, weight="weight")
    return [], None


ruta, ruta_lat = ruta_actual()

# =========================================================
# CABECERA DINÁMICA
# =========================================================
if n_activos == 0:
    estado, tono = "SIN DISPOSITIVOS ACTIVOS", "bad"
elif not (fallos or enlaces_fallidos):
    estado, tono = "RED OPERATIVA", "ok"
elif pares_perdidos:
    estado, tono = "RED FRAGMENTADA", "bad"
else:
    estado, tono = "RED DEGRADADA", "warn"

ARTE_HERO = """<svg class="hero-art" viewBox="0 0 260 140" xmlns="http://www.w3.org/2000/svg">
<g stroke="rgba(148,163,184,.55)" stroke-width="1.6" fill="none">
<line x1="30" y1="70" x2="100" y2="28"/><line x1="100" y1="28" x2="180" y2="52"/>
<line x1="30" y1="70" x2="110" y2="112"/><line x1="110" y1="112" x2="180" y2="52"/>
<line x1="180" y1="52" x2="232" y2="96"/><line x1="100" y1="28" x2="110" y2="112"/>
<line x1="180" y1="52" x2="226" y2="22"/></g>
<circle cx="30" cy="70" r="9" fill="#4DA3FF"/><circle cx="100" cy="28" r="8" fill="#7C5CFF"/>
<circle cx="180" cy="52" r="10" fill="#2ECC71"/><circle cx="110" cy="112" r="8" fill="#F5A623"/>
<circle cx="232" cy="96" r="7" fill="#4DA3FF"/><circle cx="226" cy="22" r="6" fill="#9B8CFF"/>
</svg>"""

st.markdown(_h(f"""<div class="hero"><div class="hero-text">
<div class="hero-eyebrow">SIMULADOR DE REDES · TEORÍA DE GRAFOS</div>
<h1>🌐 Net<span>Sim</span></h1>
<p>Construye una red, provoca fallos y observa su impacto: rutas de menor latencia, criticidad y resiliencia.</p>
<div class="hero-chips">
<span class="status status-{tono}"><i class="dot"></i>{estado}</span>
<span class="chip">🖥️ {n_activos}/{G.number_of_nodes()} dispositivos</span>
<span class="chip">🔗 {n_enlaces}/{G.number_of_edges()} enlaces</span>
<span class="chip">🧩 {comp_act} componente{'s' if comp_act != 1 else ''}</span>
</div></div>{ARTE_HERO}</div>"""), unsafe_allow_html=True)


# =========================================================
# MAPA
# =========================================================
def calcular_posiciones(g, nombre):
    firma = (nombre, tuple(sorted(g.nodes)), tuple(sorted(clave_enlace(u, v) for u, v in g.edges)))
    if st.session_state.posiciones is not None and st.session_state.firma_pos == firma:
        return st.session_state.posiciones
    try:
        if nombre == "Circular":
            pos = nx.circular_layout(g)
        elif nombre == "Kamada-Kawai" and g.number_of_nodes() > 1:
            pos = nx.kamada_kawai_layout(g, weight=None)
        elif nombre == "Capas (shell)":
            por_tipo = {}
            for n, a in g.nodes(data=True):
                por_tipo.setdefault(a.get("tipo"), []).append(n)
            capas = [por_tipo[t] for t in TIPOS if t in por_tipo]
            pos = nx.shell_layout(g, nlist=capas)
        else:
            pos = nx.spring_layout(g, seed=17, k=0.9)
    except Exception:
        pos = nx.spring_layout(g, seed=17, k=0.9)
    st.session_state.posiciones = pos
    st.session_state.firma_pos = firma
    return pos


def puntos_paquete(ruta, pos, pasos=14):
    """Puntos intermedios a lo largo de la ruta para animar un paquete viajando por ella."""
    xs, ys = [], []
    for u, v in zip(ruta[:-1], ruta[1:]):
        for i in range(pasos):
            t = i / pasos
            xs.append(pos[u][0] + (pos[v][0] - pos[u][0]) * t)
            ys.append(pos[u][1] + (pos[v][1] - pos[u][1]) * t)
    xs.append(pos[ruta[-1]][0])
    ys.append(pos[ruta[-1]][1])
    return xs, ys


def dibujar_mapa(original, simulada, crit, ruta, mostrar_lat, halo=True, foco=None):
    if original.number_of_nodes() == 0:
        st.info("La topología está vacía. Añade dispositivos o carga una plantilla desde el panel lateral.")
        return
    pos = calcular_posiciones(original, layout_nombre)
    fig = go.Figure()
    aristas_ruta = {frozenset(p) for p in zip(ruta[:-1], ruta[1:])} if len(ruta) > 1 else set()

    def trazo(aristas, **linea):
        xs, ys = [], []
        for u, v in aristas:
            xs += [pos[u][0], pos[v][0], None]
            ys += [pos[u][1], pos[v][1], None]
        if xs:
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=linea,
                                     hoverinfo="none", showlegend=False))

    # Enlaces interrumpidos (por fallo de enlace o de dispositivo)
    trazo([(u, v) for u, v in original.edges if not simulada.has_edge(u, v)],
          color="rgba(255,77,79,.55)", width=1.6, dash="dot")

    # Enlaces activos agrupados por velocidad (color y grosor según latencia)
    grupos = {"rapido": [], "medio": [], "lento": []}
    for u, v, a in simulada.edges(data=True):
        if frozenset((u, v)) not in aristas_ruta:
            grupos[tramo_enlace(a.get("weight", 1))].append((u, v))
    for clave, aristas in grupos.items():
        trazo(aristas, color=rgba(COLOR_ENLACE[clave], 0.75), width=ANCHO_ENLACE[clave])

    # Ruta calculada: estela de brillo + línea sólida
    en_ruta_aristas = [(u, v) for u, v in simulada.edges if frozenset((u, v)) in aristas_ruta]
    trazo(en_ruta_aristas, color=rgba(C_RUTA, 0.22), width=14)
    trazo(en_ruta_aristas, color=C_RUTA, width=4.5)

    if simulada.number_of_edges():
        mx = [(pos[u][0] + pos[v][0]) / 2 for u, v in simulada.edges]
        my = [(pos[u][1] + pos[v][1]) / 2 for u, v in simulada.edges]
        etq = [f"{a.get('weight', 1)} ms" for _, _, a in simulada.edges(data=True)]
        hov = [f"{u} ↔ {v}<br>Latencia: {a.get('weight', 1)} ms" for u, v, a in simulada.edges(data=True)]
        fig.add_trace(go.Scatter(
            x=mx, y=my, mode="text" if mostrar_lat else "markers", text=etq if mostrar_lat else None,
            textfont=dict(size=11, color="#CBD5E1"),
            marker=dict(size=14, color="rgba(0,0,0,0)"), hovertext=hov, hoverinfo="text", showlegend=False))

    nivel_de = dict(zip(crit["Dispositivo"], crit["Criticidad"])) if not crit.empty else {}
    puntos = dict(zip(crit["Dispositivo"], crit["Puntuación"])) if not crit.empty else {}
    activos = list(simulada.nodes())
    en_ruta = set(ruta)
    if activos:
        colores = [COLORES.get(nivel_de.get(n, "Baja"), "#777777") for n in activos]
        if halo:
            fig.add_trace(go.Scatter(
                x=[pos[n][0] for n in activos], y=[pos[n][1] for n in activos], mode="markers",
                marker=dict(size=[58 if n in en_ruta else 50 for n in activos],
                            color=[rgba(c, 0.16) for c in colores]),
                hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in activos], y=[pos[n][1] for n in activos],
            mode="markers+text", text=[f"{ICONOS.get(simulada.nodes[n].get('tipo'), '')} {n}" for n in activos],
            textposition="top center", textfont=dict(size=13, color=C_TEXTO),
            marker=dict(
                size=[36 if n in en_ruta else 30 for n in activos],
                symbol=[SIMBOLOS.get(simulada.nodes[n].get("tipo", "Otro"), "circle") for n in activos],
                color=colores,
                line=dict(width=[3 if n in en_ruta else 1.5 for n in activos],
                          color=[C_RUTA if n in en_ruta else "#0E1117" for n in activos]),
            ),
            customdata=[[simulada.nodes[n].get("tipo", "Otro"), nivel_de.get(n, "—"),
                         puntos.get(n, 0), simulada.degree[n]] for n in activos],
            hovertemplate=("<b>%{text}</b><br>Tipo: %{customdata[0]}<br>Criticidad: %{customdata[1]} "
                           "(%{customdata[2]})<br>Conexiones: %{customdata[3]}<extra></extra>"),
            showlegend=False))
    caidos = [n for n in original.nodes if n not in simulada]
    if caidos:
        if halo:
            fig.add_trace(go.Scatter(
                x=[pos[n][0] for n in caidos], y=[pos[n][1] for n in caidos], mode="markers",
                marker=dict(size=50, color=rgba(C_MAL, 0.14)), hoverinfo="none", showlegend=False))
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in caidos], y=[pos[n][1] for n in caidos],
            mode="markers+text", text=caidos, textposition="bottom center",
            textfont=dict(size=12, color=C_MAL),
            marker=dict(size=26, symbol="x", color=C_MAL, line=dict(width=2, color=C_MAL)),
            hovertemplate="<b>%{text}</b><br>Estado: desactivado<extra></extra>", showlegend=False))

    # Anillo de enfoque sobre el dispositivo elegido en el inspector
    if foco is not None and foco in original and foco in pos:
        fig.add_trace(go.Scatter(
            x=[pos[foco][0]], y=[pos[foco][1]], mode="markers", hoverinfo="none", showlegend=False,
            marker=dict(size=60, symbol="circle-open", color=C_ACENTO, line=dict(width=3, color=C_ACENTO))))

    # Paquete animado que viaja por la ruta (botón ▶ dentro del mapa)
    if len(ruta) > 1:
        px, py = puntos_paquete(ruta, pos)
        fig.add_trace(go.Scatter(
            x=[px[0]], y=[py[0]], mode="markers", hoverinfo="none", showlegend=False,
            marker=dict(size=15, color="#FFFFFF", line=dict(width=3, color=C_RUTA))))
        idx = len(fig.data) - 1
        fig.frames = [go.Frame(data=[go.Scatter(x=[px[i]], y=[py[i]])], traces=[idx], name=str(i))
                      for i in range(len(px))]
        fig.update_layout(updatemenus=[dict(
            type="buttons", showactive=False, direction="left", x=0.01, y=0.99,
            xanchor="left", yanchor="top", bgcolor="#1E293B", bordercolor=C_RUTA,
            font=dict(color=C_TEXTO),
            buttons=[dict(label="▶ Enviar paquete", method="animate",
                          args=[None, dict(frame=dict(duration=45, redraw=False),
                                           transition=dict(duration=0), fromcurrent=False,
                                           mode="immediate")])])])

    estilo_fig(fig, alto=620)
    fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    mostrar(fig)
    st.markdown(leyenda_mapa(), unsafe_allow_html=True)


# =========================================================
# ESTADO GENERAL + MÉTRICAS
# =========================================================
if fallos or enlaces_fallidos:
    etiquetas = "".join(f'<span class="tag">🖥️ {esc(n)}</span>' for n in fallos)
    etiquetas += "".join(f'<span class="tag">🔗 {esc(u)} ↔ {esc(v)}</span>' for u, v in enlaces_fallidos)
    st.markdown(f'<div class="scenario"><b>Escenario de fallo activo:</b> {etiquetas}</div>',
                unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
enl_perdidos = G.number_of_edges() - n_enlaces
m1.markdown(kpi("🖥️", "Dispositivos activos", f"{n_activos}/{G.number_of_nodes()}",
                f"{len(fallos)} desactivado{'s' if len(fallos) != 1 else ''}" if fallos else "Todos operativos",
                "bad" if fallos else "ok"), unsafe_allow_html=True)
m2.markdown(kpi("🔗", "Enlaces activos", f"{n_enlaces}/{G.number_of_edges()}",
                f"{enl_perdidos} interrumpido{'s' if enl_perdidos != 1 else ''}" if enl_perdidos
                else "Todos operativos", "bad" if enl_perdidos else "ok"), unsafe_allow_html=True)
m3.markdown(kpi("🧩", "Componentes conectados", comp_act,
                 f"{comp_act - comp_orig:+d} respecto a la base" if comp_act != comp_orig else "Sin cambios",
                 "ok" if comp_act <= comp_orig else "bad"), unsafe_allow_html=True)
m4.markdown(kpi("🚫", "Pares activos sin comunicación", len(pares_perdidos),
                "Comunicación íntegra" if not pares_perdidos else "Parejas que perdieron el camino",
                "ok" if not pares_perdidos else "bad",
                tip="Parejas de dispositivos que siguen activos y ya no pueden comunicarse entre sí."),
                unsafe_allow_html=True)
st.write("")

def ficha_dispositivo(nombre):
    tipo = G.nodes[nombre].get("tipo", "Otro")
    caido = nombre in fallos
    fila = df_crit[df_crit["Dispositivo"] == nombre] if not df_crit.empty else df_crit
    if len(fila):
        nivel_c = fila.iloc[0]["Criticidad"]
        crit_txt, crit_tono = f'{nivel_c} · {fila.iloc[0]["Puntuación"]}', {"Alta": "bad", "Media": "warn", "Baja": "ok"}[nivel_c]
    else:
        crit_txt, crit_tono = "—", "info"
    es_spof = nombre in set(nx.articulation_points(G))
    impactos = core.impacto_dispositivos(G).set_index("Dispositivo")["Pares que pierden comunicación"]
    pares_si_cae = int(impactos.get(nombre, 0))
    vecinos = []
    for v in sorted(G.neighbors(nombre)):
        lat = G[nombre][v].get("weight", 1)
        apagado = v in fallos or not G_sim.has_edge(nombre, v)
        vecinos.append(f'<span class="nb{" nb-off" if apagado else ""}">'
                       f'{ICONOS.get(G.nodes[v].get("tipo"), "")} {esc(v)} · {lat:g} ms</span>')
    estado_txt, estado_tono = ("DESACTIVADO", "bad") if caido else ("ACTIVO", "ok")
    return _h(
        f'<div class="ficha"><div class="ficha-head"><div class="ficha-ico">{ICONOS.get(tipo, "🔧")}</div>'
        f'<div><div class="ficha-name">{esc(nombre)}</div><div class="ficha-type">{esc(tipo)} '
        f'<span class="status status-{estado_tono}"><i class="dot"></i>{estado_txt}</span></div></div></div>'
        f'<div class="ficha-grid">'
        + kpi("🔌", "Conexiones", G.degree[nombre], "Enlaces directos en la red base", "info")
        + kpi("🚦", "Criticidad", crit_txt, "En el escenario actual", crit_tono)
        + kpi("⚠️", "Punto único de fallo", "Sí" if es_spof else "No",
              "Su caída separa la red" if es_spof else "La red resiste su caída", "bad" if es_spof else "ok")
        + kpi("💥", "Si cae…", f"{pares_si_cae} pares", "Pares ajenos que pierden comunicación",
              "bad" if pares_si_cae else "ok")
        + '</div><div class="nbs-title">Conexiones directas</div>'
        + ("".join(vecinos) if vecinos else '<span class="nb">Sin conexiones</span>') + '</div>')


INFORME_CSS = (
    "body{font-family:Segoe UI,Arial,sans-serif;background:#0B0F1A;color:#E6EDF3;max-width:1000px;margin:0 auto;"
    "padding:2rem 1.2rem}h1{margin:.2rem 0}h2{margin-top:2rem;border-bottom:1px solid #26324a;padding-bottom:.3rem;"
    "color:#7DB8FF}.sub{opacity:.7}.t{border-collapse:collapse;width:100%;font-size:.88rem;margin:.6rem 0}"
    ".t th{background:#17213a;text-align:left;padding:.45rem .6rem}.t td{padding:.4rem .6rem;"
    "border-top:1px solid #1f2a44}.kpis{display:flex;flex-wrap:wrap;gap:.7rem}.k{flex:1;min-width:170px;"
    "background:#121a2e;border:1px solid #26324a;border-radius:12px;padding:.8rem 1rem}.k b{display:block;"
    "font-size:1.5rem}.k span{font-size:.75rem;opacity:.7;text-transform:uppercase}.ok{color:#2ECC71}"
    ".bad{color:#FF6B6D}.warn{color:#F5A623}.nota{opacity:.7;font-size:.85rem}@media print{body{background:#fff;"
    "color:#000}.k,.t th{background:#eee}h2{color:#036}}")


def generar_informe():
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    base = core.metricas_topologia(G)

    def tabla(df):
        if df is None or df.empty:
            return '<p class="nota">Sin datos para mostrar.</p>'
        return df.to_html(index=False, border=0, escape=True, classes="t")

    def caja(valor, etiqueta, tono=""):
        return f'<div class="k"><span>{esc(etiqueta)}</span><b class="{tono}">{esc(valor)}</b></div>'

    if fallos or enlaces_fallidos:
        escenario = ("<p><b>Dispositivos desactivados:</b> " + (esc(", ".join(fallos)) or "ninguno") +
                     "<br><b>Enlaces interrumpidos:</b> " +
                     (esc(", ".join(f"{u} ↔ {v}" for u, v in enlaces_fallidos)) or "ninguno") + "</p>")
    else:
        escenario = "<p>Escenario normal: todos los elementos están activos.</p>"
    res_nodos = core.impacto_dispositivos(G) if G.number_of_nodes() > 1 else pd.DataFrame()
    res_enl = core.impacto_enlaces(G) if G.number_of_edges() else pd.DataFrame()
    sugs = _sugerencias(clave_red) if G.number_of_nodes() >= 3 else []
    if sugs:
        lista_sug = "<ul>" + "".join(
            f"<li><b>{esc(x['origen'])} ↔ {esc(x['destino'])}</b>: reduce el riesgo en {x['reduccion']} elemento(s); "
            f"resiliencia resultante {x['indice_despues']:.0f} %.</li>" for x in sugs) + "</ul>"
    else:
        lista_sug = '<p class="nota">No hay mejoras estructurales que sugerir.</p>'
    crit_vista = df_crit.drop(columns=["Interpretación"], errors="ignore")
    ind = base["Índice de resiliencia (%)"]
    return (
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Informe NetSim</title>'
        f'<style>{INFORME_CSS}</style></head><body>'
        f'<h1>🌐 Informe de simulación · NetSim</h1><p class="sub">Generado el {ahora}</p>'
        f'<h2>1. Topología base</h2><div class="kpis">'
        + caja(base["Dispositivos"], "Dispositivos") + caja(base["Enlaces"], "Enlaces")
        + caja(base["Puntos únicos de fallo"], "Puntos únicos de fallo", "bad" if base["Puntos únicos de fallo"] else "ok")
        + caja(base["Enlaces puente"], "Enlaces puente", "bad" if base["Enlaces puente"] else "ok")
        + caja(f"{ind:.0f} %" if ind is not None else "—", "Índice de resiliencia")
        + f'</div><h2>2. Escenario simulado</h2>{escenario}<div class="kpis">'
        + caja(f"{n_activos}/{G.number_of_nodes()}", "Dispositivos activos")
        + caja(f"{n_enlaces}/{G.number_of_edges()}", "Enlaces activos")
        + caja(comp_act, "Componentes conectados")
        + caja(len(pares_perdidos), "Pares activos sin comunicación", "bad" if pares_perdidos else "ok")
        + f'</div><h2>3. Criticidad de los dispositivos activos</h2>{tabla(crit_vista)}'
        f'<h2>4. Resiliencia: caída individual</h2><h3>Dispositivos</h3>{tabla(res_nodos)}'
        f'<h3>Enlaces</h3>{tabla(res_enl)}<h2>5. Mejoras sugeridas</h2>{lista_sug}'
        '<h2>6. Limitaciones</h2><ul><li>Simulación académica: no se conecta a equipos reales ni mide tráfico.</li>'
        '<li>La criticidad es una regla heurística, no una medición validada de riesgo.</li>'
        '<li>Las latencias son valores de ejemplo definidos por el usuario.</li>'
        '<li>El módulo de ML usa datos sintéticos y solo demuestra el flujo de clasificación.</li></ul>'
        '<p class="nota">Consejo: imprime esta página (Ctrl + P) para guardarla como PDF.</p></body></html>')


tab_red, tab_rutas, tab_crit, tab_res, tab_ml, tab_top = st.tabs([
    "🗺️ Mapa", "🧭 Rutas", "🚦 Criticidad", "🛡️ Resiliencia", "🤖 Machine Learning", "📋 Topología y exportación"])

# ---------------------------------------------------------
with tab_red:
    dibujar_mapa(G, G_sim, df_crit, ruta if mostrar_ruta else [], mostrar_lat, mostrar_halo,
                 st.session_state.get("inspector"))
    c1, c2 = st.columns([1, 1])
    with c1:
        if n_activos == 0:
            st.error("No quedan dispositivos activos.")
        elif comp_act == 1:
            st.success("La red activa permanece conectada.")
        else:
            st.error(f"La red está fragmentada en {comp_act} componentes.")
            for i, comp in enumerate(nx.connected_components(G_sim), 1):
                st.write(f"**Grupo {i}:** " + ", ".join(sorted(comp)))
    with c2:
        if pares_perdidos:
            st.warning(f"El escenario deja sin comunicación a {len(pares_perdidos)} pares de dispositivos "
                       "activos que estaban conectados en la base.")
            with st.expander("Ver pares afectados"):
                st.dataframe(pd.DataFrame(pares_perdidos, columns=["Origen", "Destino"]),
                             use_container_width=True, hide_index=True)
        else:
            st.success("Los dispositivos activos siguen comunicados entre sí como en la base.")

    seccion("🔎 Inspector de dispositivos")
    opciones_insp = [None] + sorted(G.nodes())
    if st.session_state.get("inspector") not in opciones_insp:
        st.session_state["inspector"] = None
    st.selectbox("Elige un dispositivo para ver su ficha y resaltarlo en el mapa", opciones_insp, key="inspector",
                 format_func=lambda x: "— ninguno —" if x is None else f"{ICONOS.get(G.nodes[x].get('tipo'), '')} {x}")
    if st.session_state.inspector is not None:
        st.markdown(ficha_dispositivo(st.session_state.inspector), unsafe_allow_html=True)

# ---------------------------------------------------------
with tab_rutas:
    seccion("🧭 Ruta de menor latencia (Dijkstra)")
    activos = sorted(G_sim.nodes())
    if len(activos) < 2:
        st.info("Se necesitan al menos dos dispositivos activos.")
    else:
        opciones_ruta = [None] + activos
        for k_ruta in ("ruta_origen", "ruta_destino"):
            if st.session_state.get(k_ruta) not in opciones_ruta:
                st.session_state[k_ruta] = None
        c1, c2 = st.columns(2)
        c1.selectbox("Origen", opciones_ruta, key="ruta_origen",
                     format_func=lambda x: "— elegir —" if x is None else x)
        c2.selectbox("Destino", opciones_ruta, key="ruta_destino",
                     format_func=lambda x: "— elegir —" if x is None else x)
        o, d = st.session_state.ruta_origen, st.session_state.ruta_destino
        if o is None or d is None:
            st.info("Elige origen y destino para calcular y resaltar una ruta en el mapa.")
        elif o == d:
            st.warning("Selecciona dos dispositivos distintos.")
        else:
            alternativas = core.rutas_alternativas(G_sim, o, d, 3)
            if not alternativas:
                st.error("No existe ruta entre esos dispositivos en el escenario actual.")
            else:
                mejor, lat = alternativas[0]
                k1, k2, k3 = st.columns(3)
                k1.markdown(kpi("⏱️", "Latencia total", f"{lat:g} ms", "Suma de los tramos", "info"),
                            unsafe_allow_html=True)
                k2.markdown(kpi("🦘", "Saltos", len(mejor) - 1, "Enlaces recorridos", "info"),
                            unsafe_allow_html=True)
                k3.markdown(kpi("🔁", "Rutas posibles", len(alternativas),
                                "Hay redundancia" if len(alternativas) > 1 else "Sin redundancia",
                                "ok" if len(alternativas) > 1 else "warn"), unsafe_allow_html=True)
                seccion("Camino óptimo")
                st.markdown(cadena_ruta(mejor, G_sim), unsafe_allow_html=True)
                tabla = pd.DataFrame([{"Tramo": f"{u} → {v}", "Latencia (ms)": G_sim[u][v].get("weight", 1)}
                                      for u, v in zip(mejor[:-1], mejor[1:])])
                st.dataframe(tabla, use_container_width=True, hide_index=True)
                if len(alternativas) > 1:
                    seccion("Rutas alternativas")
                    st.dataframe(pd.DataFrame([
                        {"Opción": i, "Ruta": " → ".join(r), "Latencia (ms)": l, "Saltos": len(r) - 1,
                         "Sobrecoste (ms)": round(l - lat, 2)}
                        for i, (r, l) in enumerate(alternativas, 1)]),
                        use_container_width=True, hide_index=True)
                else:
                    st.info("No hay rutas alternativas: esta ruta no tiene redundancia.")
                st.caption("La ruta se resalta en amarillo en el mapa; allí puedes pulsar «▶ Enviar paquete» "
                           "para ver el recorrido animado.")
        with st.expander("🔥 Matriz de latencias mínimas entre dispositivos activos"):
            mat = core.matriz_latencias(G_sim)
            fig = go.Figure(go.Heatmap(z=mat.values, x=mat.columns, y=mat.index,
                                       colorscale=[[0, "#10233f"], [0.5, "#2563eb"], [1, "#7DD3FC"]],
                                       text=mat.round(1).astype(str).values, texttemplate="%{text}",
                                       hoverongaps=False, colorbar=dict(title="ms")))
            estilo_fig(fig, alto=440)
            fig.update_layout(yaxis=dict(autorange="reversed"))
            mostrar(fig)
            st.caption("Las celdas vacías indican dispositivos sin ruta entre sí.")

# ---------------------------------------------------------
with tab_crit:
    seccion("🚦 Criticidad de dispositivos")
    st.write("Puntuación = 35 % centralidad de grado + 35 % intermediación + 30 % importancia del tipo.")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        cuenta = df_crit["Criticidad"].value_counts()
        a, b, c = st.columns(3)
        a.markdown(kpi("🔴", "Criticidad alta", int(cuenta.get("Alta", 0)), "Dispositivos clave", "bad"),
                   unsafe_allow_html=True)
        b.markdown(kpi("🟠", "Criticidad media", int(cuenta.get("Media", 0)), "Relevancia moderada", "warn"),
                   unsafe_allow_html=True)
        c.markdown(kpi("🟢", "Criticidad baja", int(cuenta.get("Baja", 0)), "Menor influencia", "ok"),
                   unsafe_allow_html=True)
        st.write("")
        cd, cb = st.columns([1, 2])
        with cd:
            niveles = ["Alta", "Media", "Baja"]
            fig = go.Figure(go.Pie(
                labels=niveles, values=[int(cuenta.get(n, 0)) for n in niveles], hole=0.62, sort=False,
                marker=dict(colors=[COLORES[n] for n in niveles], line=dict(color="#0B0F1A", width=3)),
                textinfo="percent", hovertemplate="%{label}: %{value} dispositivo(s)<extra></extra>"))
            estilo_fig(fig, alto=max(280, 38 * len(df_crit)))
            fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
                              annotations=[dict(text=f"<b>{len(df_crit)}</b><br>equipos", showarrow=False,
                                                x=0.5, y=0.5, xref="paper", yref="paper",
                                                font=dict(size=16, color=C_TEXTO))])
            mostrar(fig)
        with cb:
            orden = df_crit.sort_values("Puntuación")
            fig = go.Figure(go.Bar(x=orden["Puntuación"], y=orden["Dispositivo"], orientation="h",
                                   marker=dict(color=[COLORES[n] for n in orden["Criticidad"]],
                                               line=dict(color="rgba(255,255,255,.25)", width=1)),
                                   text=orden["Puntuación"], textposition="outside"))
            estilo_fig(fig, alto=max(280, 38 * len(orden)), margen=dict(l=10, r=40, t=10, b=10))
            fig.update_layout(xaxis=dict(range=[0, 1], title="Puntuación", gridcolor="rgba(255,255,255,.06)"))
            mostrar(fig)
        vista = df_crit.copy()
        vista["Criticidad"] = vista["Criticidad"].map({"Alta": "🔴 Alta", "Media": "🟠 Media", "Baja": "🟢 Baja"})
        st.dataframe(vista, use_container_width=True, hide_index=True,
                     column_config={"Puntuación": st.column_config.ProgressColumn(
                         "Puntuación", min_value=0.0, max_value=1.0, format="%.3f")})
        st.caption("Umbrales: baja < 0.30 · media 0.30–0.60 · alta ≥ 0.60. Regla heurística académica, "
                   "no una medición de riesgo real.")
        st.download_button("⬇️ Descargar criticidad (CSV)", df_crit.to_csv(index=False).encode("utf-8-sig"),
                           file_name="criticidad_netsim.csv", mime="text/csv")

# ---------------------------------------------------------
with tab_res:
    seccion("🛡️ Análisis de resiliencia de la topología base")
    st.write("Evalúa qué ocurre si **cada** dispositivo o enlace falla de forma individual. "
             "Un *punto único de fallo* es un dispositivo cuya caída separa la red en partes.")
    if G.number_of_nodes() < 2:
        st.info("Añade más dispositivos para analizar la resiliencia.")
    else:
        indice = core.indice_resiliencia(G)
        df_nodos = core.impacto_dispositivos(G)
        df_enl = core.impacto_enlaces(G) if G.number_of_edges() else pd.DataFrame()
        n_spof = int((df_nodos["Punto único de fallo"] == "Sí").sum())
        n_puentes = int((df_enl["Enlace crítico (puente)"] == "Sí").sum()) if not df_enl.empty else 0
        g1, g2 = st.columns([1.3, 1])
        with g1:
            if indice is not None:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=round(indice, 1), number=dict(suffix=" %", font=dict(size=44)),
                    title=dict(text="Índice de resiliencia", font=dict(size=15, color=C_SUAVE)),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickcolor=C_SUAVE),
                        bar=dict(color=C_ACENTO, thickness=0.28), bgcolor="rgba(255,255,255,.04)",
                        borderwidth=0,
                        steps=[dict(range=[0, 50], color=rgba(C_MAL, 0.35)),
                               dict(range=[50, 80], color=rgba("#F5A623", 0.35)),
                               dict(range=[80, 100], color=rgba("#2ECC71", 0.35))])))
                estilo_fig(fig, alto=260, margen=dict(l=30, r=30, t=50, b=10))
                mostrar(fig)
                st.caption("Porcentaje de dispositivos cuya caída individual no separa a otros dispositivos.")
            else:
                st.info("El índice de resiliencia requiere al menos 3 dispositivos.")
        with g2:
            st.markdown(kpi("⚠️", "Puntos únicos de fallo", n_spof,
                            "Su caída fragmenta la red" if n_spof else "Ninguno", "bad" if n_spof else "ok"),
                        unsafe_allow_html=True)
            st.write("")
            st.markdown(kpi("🌉", "Enlaces críticos (puentes)", n_puentes,
                            "Sin ellos la red se parte" if n_puentes else "Ninguno", "bad" if n_puentes else "ok"),
                        unsafe_allow_html=True)
        if n_spof == 0 and n_puentes == 0 and nx.is_connected(G):
            st.success("La red base es redundante: ninguna caída individual la fragmenta.")
        else:
            st.warning("Hay elementos cuya caída individual fragmenta la red. Considera añadir enlaces redundantes.")
        cA, cB = st.columns(2)
        with cA:
            seccion("Impacto por dispositivo")
            vista_n = df_nodos.copy()
            vista_n["Punto único de fallo"] = vista_n["Punto único de fallo"].map({"Sí": "🔴 Sí", "No": "🟢 No"})
            st.dataframe(vista_n, use_container_width=True, hide_index=True, column_config={
                "Pares que pierden comunicación": st.column_config.ProgressColumn(
                    "Pares que pierden comunicación", min_value=0,
                    max_value=max(1, int(df_nodos["Pares que pierden comunicación"].max())), format="%d")})
        with cB:
            seccion("Impacto por enlace")
            if df_enl.empty:
                st.info("No hay enlaces.")
            else:
                vista_e = df_enl.copy()
                vista_e["Enlace crítico (puente)"] = vista_e["Enlace crítico (puente)"].map(
                    {"Sí": "🔴 Sí", "No": "🟢 No"})
                st.dataframe(vista_e, use_container_width=True, hide_index=True, column_config={
                    "Pares que pierden comunicación": st.column_config.ProgressColumn(
                        "Pares que pierden comunicación", min_value=0,
                        max_value=max(1, int(df_enl["Pares que pierden comunicación"].max())), format="%d")})
        st.caption("«Pares que pierden comunicación» cuenta parejas de dispositivos que dejan de poder "
                   "comunicarse (sin contar el propio dispositivo caído).")

        seccion("🛠️ Mejoras sugeridas")
        if not nx.is_connected(G):
            st.info("La red base no está conectada: primero conecta todos sus componentes.")
        else:
            sugs = _sugerencias(clave_red)
            if not sugs:
                st.success("No hay puntos únicos de fallo ni enlaces puente que corregir.")
            else:
                st.write("Enlaces nuevos que más reducen los puntos únicos de fallo y los puentes "
                         "(se supone una latencia de 5 ms):")
                for i, sg in enumerate(sugs):
                    ca, cb_, cc_ = st.columns([3, 3, 1])
                    ca.markdown(kpi("🔗", f"Opción {i + 1}", f"{sg['origen']} ↔ {sg['destino']}",
                                    f"Reduce el riesgo en {sg['reduccion']} elemento(s)", "info"),
                                unsafe_allow_html=True)
                    cb_.markdown(kpi("🛡️", "Resiliencia resultante", f"{sg['indice_despues']:.0f} %",
                                     f"{sg['spof_despues']} puntos únicos · {sg['puentes_despues']} puentes", "ok"),
                                 unsafe_allow_html=True)
                    cc_.button("➕ Aplicar", key=f"aplicar_mejora_{i}", on_click=_aplicar_mejora,
                               args=(sg["origen"], sg["destino"], sg["latencia"]), use_container_width=True)
                st.caption("Heurística estructural: prueba cada enlace posible y mide cuánto baja el riesgo. "
                           "No distingue qué equipos pueden reenviar tráfico en una red real.")

        with st.expander("📊 Comparar con las plantillas de topología"):
            comp_df = pd.concat([pd.DataFrame([{"Topología": "⭐ Tu red actual", **core.metricas_topologia(G)}]),
                                 _plantillas()], ignore_index=True)
            vals = comp_df["Índice de resiliencia (%)"].fillna(0)
            fig = go.Figure(go.Bar(
                x=comp_df["Topología"], y=vals, text=vals.round(0).astype(int).astype(str) + " %",
                textposition="outside",
                marker=dict(color=[C_ACENTO2 if t.startswith("⭐") else C_ACENTO for t in comp_df["Topología"]])))
            estilo_fig(fig, alto=330, margen=dict(l=10, r=10, t=30, b=10))
            fig.update_layout(yaxis=dict(range=[0, 115], title="Índice de resiliencia (%)",
                                         gridcolor="rgba(255,255,255,.06)"))
            mostrar(fig)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def entrenar_modelo():
    rng = np.random.default_rng(42)
    n = 1800
    g_, i_, imp_ = rng.random(n), rng.random(n), rng.uniform(0.2, 1.0, n)
    s = 0.35 * g_ + 0.35 * i_ + 0.30 * imp_
    y = pd.Series(np.where(s < 0.30, "Baja", np.where(s < 0.60, "Media", "Alta")))
    X = pd.DataFrame({"Centralidad de grado": g_, "Centralidad de intermediación": i_,
                      "Importancia del tipo": imp_})
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    modelo = DecisionTreeClassifier(max_depth=5, min_samples_leaf=8, random_state=42).fit(Xtr, ytr)
    pred = modelo.predict(Xte)
    clases = ["Baja", "Media", "Alta"]
    return {
        "modelo": modelo, "clases": clases, "acc": accuracy_score(yte, pred),
        "cm": confusion_matrix(yte, pred, labels=clases),
        "informe": classification_report(yte, pred, labels=clases, output_dict=True, zero_division=0),
        "imp": pd.DataFrame({"Variable": X.columns, "Importancia": modelo.feature_importances_})
        .sort_values("Importancia", ascending=False), "vars": list(X.columns),
    }


with tab_ml:
    seccion("🤖 Clasificación demostrativa con árbol de decisión")
    st.write("Se entrena con datos **sintéticos** (escala 0–1) etiquetados con la misma regla heurística de "
             "criticidad. Sirve para demostrar el flujo de clasificación, no para predecir averías reales.")
    ml = entrenar_modelo()
    informe, clases = ml["informe"], ml["clases"]
    k = st.columns(4)
    k[0].markdown(kpi("🎯", "Exactitud (test)", f"{ml['acc'] * 100:.1f}%", "Aciertos / total", "info"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("🔍", "Precisión macro", f"{informe['macro avg']['precision'] * 100:.1f}%",
                      "Promedio por clase", "info"), unsafe_allow_html=True)
    k[2].markdown(kpi("📡", "Recall macro", f"{informe['macro avg']['recall'] * 100:.1f}%",
                      "Promedio por clase", "info"), unsafe_allow_html=True)
    k[3].markdown(kpi("⚖️", "F1 macro", f"{informe['macro avg']['f1-score'] * 100:.1f}%",
                      "Equilibrio precisión/recall", "info"), unsafe_allow_html=True)
    st.caption("Las métricas miden cuánto reproduce el árbol una regla artificial; no son validación sobre una red real.")
    cA, cB = st.columns(2)
    with cA:
        seccion("Matriz de confusión")
        fig = go.Figure(go.Heatmap(z=ml["cm"], x=[f"Pred. {c}" for c in clases], y=[f"Real {c}" for c in clases],
                                   colorscale=[[0, "#10233f"], [0.5, "#2563eb"], [1, "#7DD3FC"]],
                                   text=ml["cm"], texttemplate="%{text}", showscale=False,
                                   textfont=dict(size=16)))
        estilo_fig(fig, alto=330)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        mostrar(fig)
    with cB:
        seccion("Importancia de variables")
        imp = ml["imp"].sort_values("Importancia")
        fig = go.Figure(go.Bar(x=imp["Importancia"], y=imp["Variable"], orientation="h",
                               marker=dict(color=[C_ACENTO2, "#6C8BFF", C_ACENTO][:len(imp)]),
                               text=imp["Importancia"].round(3), textposition="outside"))
        estilo_fig(fig, alto=330, margen=dict(l=10, r=40, t=10, b=10))
        fig.update_layout(xaxis=dict(gridcolor="rgba(255,255,255,.06)"))
        mostrar(fig)
    seccion("Métricas por clase")
    st.dataframe(pd.DataFrame([{
        "Clase": c, "Precisión": round(informe[c]["precision"], 3), "Recall": round(informe[c]["recall"], 3),
        "F1": round(informe[c]["f1-score"], 3), "Muestras de prueba": int(informe[c]["support"])}
        for c in clases]), use_container_width=True, hide_index=True)
    seccion("Predicción para los dispositivos activos")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        dfp = df_crit[["Dispositivo", "Tipo", "Criticidad"] + ml["vars"]].copy()
        dfp["Criticidad predicha por ML"] = ml["modelo"].predict(dfp[ml["vars"]])
        dfp["Coincide"] = np.where(dfp["Criticidad"] == dfp["Criticidad predicha por ML"], "✅", "⚠️")
        st.dataframe(dfp, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
with tab_top:
    seccion("📋 Inventario")
    cA, cB = st.columns(2)
    inventario = pd.DataFrame([
        {"Dispositivo": n, "Tipo": f"{ICONOS.get(a.get('tipo'), '')} {a.get('tipo', 'Otro')}",
         "Conexiones": G.degree[n], "Estado": "🔴 Desactivado" if n in fallos else "🟢 Activo"}
        for n, a in G.nodes(data=True)]).sort_values("Dispositivo") if G.number_of_nodes() else pd.DataFrame()
    conexiones = pd.DataFrame([
        {"Origen": u, "Destino": v, "Latencia (ms)": a.get("weight", 1),
         "Estado": "🟢 Activa" if G_sim.has_edge(u, v) else "🔴 Interrumpida"}
        for u, v, a in G.edges(data=True)]).sort_values(["Origen", "Destino"]) if G.number_of_edges() else pd.DataFrame()
    with cA:
        st.markdown("#### Dispositivos")
        if not inventario.empty:
            st.dataframe(inventario, use_container_width=True, hide_index=True)
        else:
            st.info("Sin dispositivos.")
    with cB:
        st.markdown("#### Conexiones")
        if not conexiones.empty:
            st.dataframe(conexiones, use_container_width=True, hide_index=True)
        else:
            st.info("Sin conexiones.")

    seccion("💾 Guardar y cargar topologías")
    resumen = {
        "dispositivos_totales": G.number_of_nodes(), "dispositivos_activos": n_activos,
        "enlaces_totales": G.number_of_edges(), "enlaces_activos": n_enlaces,
        "componentes_originales": comp_orig, "componentes_actuales": comp_act,
        "pares_que_perdieron_comunicacion": [list(p) for p in pares_perdidos],
        "dispositivos_desactivados": fallos, "enlaces_interrumpidos": [list(e) for e in enlaces_fallidos],
        "nota": "Simulación académica: no representa mediciones de una red real.",
    }
    e1, e2, e3 = st.columns(3)
    e1.download_button("⬇️ Topología (JSON)", json.dumps(core.red_a_dict(G), ensure_ascii=False, indent=2),
                       file_name="topologia_netsim.json", mime="application/json", use_container_width=True)
    e2.download_button("⬇️ Enlaces (CSV)",
                       (conexiones.to_csv(index=False) if not conexiones.empty
                        else "Origen,Destino,Latencia (ms),Estado\n").encode("utf-8-sig"),
                       file_name="enlaces_netsim.csv", mime="text/csv", use_container_width=True)
    e3.download_button("⬇️ Escenario (JSON)", json.dumps(resumen, ensure_ascii=False, indent=2),
                       file_name="escenario_netsim.json", mime="application/json", use_container_width=True)
    st.download_button("📄 Informe completo del escenario (HTML, imprimible a PDF)", generar_informe(),
                       file_name="informe_netsim.html", mime="text/html", use_container_width=True)
    st.file_uploader("Cargar una topología guardada (JSON de NetSim)", type=["json"], key="archivo_json")
    st.button("📂 Importar topología", type="primary", on_click=_importar)
    estado_import = st.session_state.pop("msg_import", None)
    if estado_import:
        (st.success if estado_import[0] == "ok" else st.error)(estado_import[1])

st.divider()
with st.expander("ℹ️ Acerca del simulador y sus límites"):
    st.markdown("""
- **Modelo:** grafo no dirigido (NetworkX); cada enlace tiene una latencia en ms.
- **Fallos:** se aplican sobre una copia; la topología base no cambia.
- **Rutas:** Dijkstra minimiza la latencia total (no los saltos). Se muestran hasta 3 rutas alternativas.
- **Criticidad:** regla heurística (grado, intermediación, tipo). No es una auditoría de seguridad.
- **Resiliencia:** puntos de articulación y puentes del grafo base.
- **Machine Learning:** datos sintéticos etiquetados con la misma regla; es una demostración académica.
- **Alcance:** no se conecta a equipos reales ni mide tráfico real.
""")
st.caption("NetSim · Proyecto académico de representación de redes mediante grafos.")
