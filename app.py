import json
import random

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

# =========================================================
# CONFIGURACIÓN Y ESTILO
# =========================================================
st.set_page_config(page_title="NetSim | Simulador de redes", page_icon="🌐",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}
    #MainMenu, footer {visibility: hidden;}
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(77,163,255,.10), rgba(255,255,255,.02));
        border: 1px solid rgba(255,255,255,.09);
        padding: 14px 16px; border-radius: 14px;
    }
    div[data-testid="stMetricLabel"] p {opacity:.75; font-size:.85rem;}
    .hero {
        padding: 1.3rem 1.6rem; border-radius: 18px; margin-bottom: 1rem;
        background: radial-gradient(circle at 12% 0%, rgba(77,163,255,.30), transparent 55%),
                    radial-gradient(circle at 95% 100%, rgba(46,204,113,.20), transparent 50%),
                    #131a2a;
        border: 1px solid rgba(255,255,255,.10);
    }
    .hero h1 {margin: 0; font-size: 2rem; letter-spacing: .3px;}
    .hero p {margin: .35rem 0 0 0; opacity: .8;}
    .badge {display:inline-block; padding:.18rem .65rem; border-radius:999px; font-size:.8rem;
            font-weight:600; margin-right:.4rem;}
    .b-ok {background:rgba(46,204,113,.16); color:#2ECC71; border:1px solid rgba(46,204,113,.4);}
    .b-warn {background:rgba(245,166,35,.16); color:#F5A623; border:1px solid rgba(245,166,35,.4);}
    .b-bad {background:rgba(255,77,79,.16); color:#FF4D4F; border:1px solid rgba(255,77,79,.4);}
    .card {padding: .9rem 1.1rem; border-radius: 14px; border: 1px solid rgba(255,255,255,.09);
           background: rgba(255,255,255,.03); margin-bottom: .6rem;}
    .small-note {font-size:.85rem; opacity:.75;}
    button[kind="primary"] {font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>🌐 NetSim</h1>'
    '<p>Simulador de redes informáticas · topología, fallos, rutas de menor latencia, '
    'criticidad y resiliencia.</p></div>', unsafe_allow_html=True)

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
    for k in ("ruta_origen", "ruta_destino"):
        st.session_state.pop(k, None)


# Limpia selecciones que ya no existen (tras borrar elementos)
st.session_state.sel_fallos = [n for n in st.session_state.sel_fallos if n in G]
st.session_state.sel_enlaces = [e for e in st.session_state.sel_enlaces
                                if len(e) == 2 and G.has_edge(*e)]


# ---- callbacks de acciones rápidas ----
def _limpiar():
    reiniciar_escenario()


def _fallo_aleatorio():
    if G.number_of_nodes():
        st.session_state.sel_fallos = [random.choice(list(G.nodes))]


def _peor_caso():
    df = core.impacto_dispositivos(G)
    if not df.empty:
        st.session_state.sel_fallos = [df.iloc[0]["Dispositivo"]]


# Los cambios de red se hacen en callbacks: así se ejecutan ANTES de dibujar los
# selectores de fallos y Streamlit permite modificar su estado.
def _cargar_plantilla():
    cambiar_red(PLANTILLAS[st.session_state.plantilla_sel]())


def _importar():
    archivo = st.session_state.get("archivo_json")
    if archivo is None:
        st.session_state.msg_import = ("error", "Primero selecciona un archivo JSON.")
        return
    try:
        cambiar_red(core.red_desde_dict(json.load(archivo)))
        st.session_state.msg_import = ("ok", "Topología importada correctamente.")
    except Exception as e:  # noqa: BLE001
        st.session_state.msg_import = ("error", f"No se pudo importar el archivo: {e}")


# =========================================================
# BARRA LATERAL
# =========================================================
with st.sidebar:
    st.markdown("## 🧰 Panel de control")

    st.markdown("### ⚠️ Escenario de fallos")
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

    st.divider()
    st.markdown("### 🏗️ Construir red")

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

    st.divider()
    st.markdown("### 🎨 Vista")
    layout_nombre = st.selectbox("Disposición del mapa",
                                 ["Resorte", "Circular", "Kamada-Kawai", "Capas (shell)"])
    mostrar_lat = st.toggle("Mostrar latencias", value=True)
    mostrar_ruta = st.toggle("Resaltar ruta calculada", value=True)

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


def dibujar_mapa(original, simulada, crit, ruta, mostrar_lat):
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

    normales = [(u, v) for u, v in simulada.edges if frozenset((u, v)) not in aristas_ruta]
    trazo(normales, color="rgba(160,174,192,.55)", width=2)
    trazo([(u, v) for u, v in simulada.edges if frozenset((u, v)) in aristas_ruta], color="#FFD166", width=5)
    trazo([(u, v) for u, v in original.edges if not simulada.has_edge(u, v)],
          color="rgba(255,77,79,.55)", width=1.6, dash="dot")

    if simulada.number_of_edges():
        mx = [(pos[u][0] + pos[v][0]) / 2 for u, v in simulada.edges]
        my = [(pos[u][1] + pos[v][1]) / 2 for u, v in simulada.edges]
        etq = [f"{a.get('weight', 1)} ms" for _, _, a in simulada.edges(data=True)]
        hov = [f"{u} ↔ {v}<br>Latencia: {a.get('weight', 1)} ms" for u, v, a in simulada.edges(data=True)]
        fig.add_trace(go.Scatter(
            x=mx, y=my, mode="text" if mostrar_lat else "markers", text=etq if mostrar_lat else None,
            textfont=dict(size=11, color="#C9D1D9"),
            marker=dict(size=14, color="rgba(0,0,0,0)"), hovertext=hov, hoverinfo="text", showlegend=False))

    nivel_de = dict(zip(crit["Dispositivo"], crit["Criticidad"])) if not crit.empty else {}
    puntos = dict(zip(crit["Dispositivo"], crit["Puntuación"])) if not crit.empty else {}
    activos = list(simulada.nodes())
    if activos:
        en_ruta = set(ruta)
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in activos], y=[pos[n][1] for n in activos],
            mode="markers+text", text=[f"{ICONOS.get(simulada.nodes[n].get('tipo'), '')} {n}" for n in activos],
            textposition="top center", textfont=dict(size=13, color="#E6EDF3"),
            marker=dict(
                size=[36 if n in en_ruta else 30 for n in activos],
                symbol=[SIMBOLOS.get(simulada.nodes[n].get("tipo", "Otro"), "circle") for n in activos],
                color=[COLORES.get(nivel_de.get(n, "Baja"), "#777") for n in activos],
                line=dict(width=[3 if n in en_ruta else 1.5 for n in activos],
                          color=["#FFD166" if n in en_ruta else "#0E1117" for n in activos]),
            ),
            customdata=[[simulada.nodes[n].get("tipo", "Otro"), nivel_de.get(n, "—"),
                         puntos.get(n, 0), simulada.degree[n]] for n in activos],
            hovertemplate=("<b>%{text}</b><br>Tipo: %{customdata[0]}<br>Criticidad: %{customdata[1]} "
                           "(%{customdata[2]})<br>Conexiones: %{customdata[3]}<extra></extra>"),
            showlegend=False))
    caidos = [n for n in original.nodes if n not in simulada]
    if caidos:
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in caidos], y=[pos[n][1] for n in caidos],
            mode="markers+text", text=caidos, textposition="bottom center",
            textfont=dict(size=12, color="#FF4D4F"),
            marker=dict(size=26, symbol="x", color="#FF4D4F", line=dict(width=2, color="#FF4D4F")),
            hovertemplate="<b>%{text}</b><br>Estado: desactivado<extra></extra>", showlegend=False))
    fig.update_layout(
        height=600, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", hoverlabel=dict(font_size=13))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.caption("Color = criticidad (🟢 baja · 🟠 media · 🔴 alta) · Forma = tipo de dispositivo · "
               "Línea amarilla = ruta calculada · Línea roja punteada = enlace interrumpido · ✖ = dispositivo caído.")


# =========================================================
# ESTADO GENERAL + MÉTRICAS
# =========================================================
if fallos or enlaces_fallidos:
    partes = []
    if fallos:
        partes.append("dispositivos caídos: " + ", ".join(fallos))
    if enlaces_fallidos:
        partes.append("enlaces cortados: " + ", ".join(f"{u} ↔ {v}" for u, v in enlaces_fallidos))
    st.markdown('<span class="badge b-warn">ESCENARIO DE FALLO</span> ' + " · ".join(partes),
                unsafe_allow_html=True)
else:
    st.markdown('<span class="badge b-ok">RED NORMAL</span> Todos los dispositivos y enlaces están activos.',
                unsafe_allow_html=True)
st.write("")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Dispositivos activos", f"{n_activos}/{G.number_of_nodes()}",
          delta=f"-{len(fallos)}" if fallos else None, delta_color="inverse")
m2.metric("Enlaces activos", f"{n_enlaces}/{G.number_of_edges()}",
          delta=f"-{G.number_of_edges() - n_enlaces}" if n_enlaces != G.number_of_edges() else None,
          delta_color="inverse")
m3.metric("Componentes conectados", comp_act,
          delta=f"{comp_act - comp_orig:+d} vs. base" if comp_act != comp_orig else None, delta_color="inverse")
m4.metric("Pares sin comunicación", len(pares_perdidos),
          delta=f"+{len(pares_perdidos)}" if pares_perdidos else None, delta_color="inverse")

tab_red, tab_rutas, tab_crit, tab_res, tab_ml, tab_top = st.tabs([
    "🗺️ Mapa", "🧭 Rutas", "🚦 Criticidad", "🛡️ Resiliencia", "🤖 Machine Learning", "📋 Topología y exportación"])

# ---------------------------------------------------------
with tab_red:
    dibujar_mapa(G, G_sim, df_crit, ruta if mostrar_ruta else [], mostrar_lat)
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
            st.warning(f"El escenario deja sin comunicación a {len(pares_perdidos)} pares de dispositivos activos que estaban conectados en la base.")
            with st.expander("Ver pares afectados"):
                st.dataframe(pd.DataFrame(pares_perdidos, columns=["Origen", "Destino"]),
                             use_container_width=True, hide_index=True)
        else:
            st.success("Los dispositivos activos siguen comunicados entre sí como en la base.")

# ---------------------------------------------------------
with tab_rutas:
    st.subheader("Ruta de menor latencia (Dijkstra)")
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
                k1, k2 = st.columns(2)
                k1.metric("Latencia total", f"{lat:g} ms")
                k2.metric("Saltos", len(mejor) - 1)
                st.success("Ruta óptima: " + " → ".join(mejor))
                tabla = pd.DataFrame([{"Tramo": f"{u} → {v}", "Latencia (ms)": G_sim[u][v].get("weight", 1)}
                                      for u, v in zip(mejor[:-1], mejor[1:])])
                st.dataframe(tabla, use_container_width=True, hide_index=True)
                if len(alternativas) > 1:
                    st.markdown("**Rutas alternativas**")
                    st.dataframe(pd.DataFrame([
                        {"Opción": i, "Ruta": " → ".join(r), "Latencia (ms)": l, "Saltos": len(r) - 1,
                         "Sobrecoste (ms)": round(l - lat, 2)}
                        for i, (r, l) in enumerate(alternativas, 1)]),
                        use_container_width=True, hide_index=True)
                else:
                    st.info("No hay rutas alternativas: esta ruta no tiene redundancia.")
                st.caption("La ruta se resalta en amarillo en el mapa (activa «Resaltar ruta» en el panel).")
        with st.expander("🔥 Matriz de latencias mínimas entre dispositivos activos"):
            mat = core.matriz_latencias(G_sim)
            fig = go.Figure(go.Heatmap(z=mat.values, x=mat.columns, y=mat.index, colorscale="Blues",
                                       text=mat.round(1).astype(str).values, texttemplate="%{text}",
                                       hoverongaps=False, colorbar=dict(title="ms")))
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
            st.caption("Las celdas vacías indican dispositivos sin ruta entre sí.")

# ---------------------------------------------------------
with tab_crit:
    st.subheader("Criticidad de dispositivos")
    st.write("Puntuación = 35 % centralidad de grado + 35 % intermediación + 30 % importancia del tipo.")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        cuenta = df_crit["Criticidad"].value_counts()
        a, b, c = st.columns(3)
        a.metric("🔴 Alta", int(cuenta.get("Alta", 0)))
        b.metric("🟠 Media", int(cuenta.get("Media", 0)))
        c.metric("🟢 Baja", int(cuenta.get("Baja", 0)))
        orden = df_crit.sort_values("Puntuación")
        fig = go.Figure(go.Bar(x=orden["Puntuación"], y=orden["Dispositivo"], orientation="h",
                               marker_color=[COLORES[n] for n in orden["Criticidad"]],
                               text=orden["Puntuación"], textposition="outside"))
        fig.update_layout(height=max(280, 38 * len(orden)), margin=dict(l=10, r=40, t=10, b=10),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(range=[0, 1], title="Puntuación"))
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        st.dataframe(df_crit, use_container_width=True, hide_index=True,
                     column_config={"Puntuación": st.column_config.ProgressColumn(
                         "Puntuación", min_value=0.0, max_value=1.0, format="%.3f")})
        st.caption("Umbrales: baja < 0.30 · media 0.30–0.60 · alta ≥ 0.60. Regla heurística académica, "
                   "no una medición de riesgo real.")
        st.download_button("⬇️ Descargar criticidad (CSV)", df_crit.to_csv(index=False).encode("utf-8-sig"),
                           file_name="criticidad_netsim.csv", mime="text/csv")

# ---------------------------------------------------------
with tab_res:
    st.subheader("Análisis de resiliencia de la topología base")
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
        r1, r2, r3 = st.columns(3)
        r1.metric("Índice de resiliencia", f"{indice:.0f} %" if indice is not None else "—",
                  help="% de dispositivos cuya caída individual no separa a otros dispositivos.")
        r2.metric("Puntos únicos de fallo", n_spof)
        r3.metric("Enlaces críticos (puentes)", n_puentes)
        if n_spof == 0 and n_puentes == 0 and nx.is_connected(G):
            st.success("La red base es redundante: ninguna caída individual la fragmenta.")
        else:
            st.warning("Hay elementos cuya caída individual fragmenta la red. Considera añadir enlaces redundantes.")
        cA, cB = st.columns(2)
        with cA:
            st.markdown("#### Impacto por dispositivo")
            st.dataframe(df_nodos, use_container_width=True, hide_index=True)
        with cB:
            st.markdown("#### Impacto por enlace")
            if df_enl.empty:
                st.info("No hay enlaces.")
            else:
                st.dataframe(df_enl, use_container_width=True, hide_index=True)
        st.caption("«Pares que pierden comunicación» cuenta parejas de dispositivos que dejan de poder "
                   "comunicarse (sin contar el propio dispositivo caído).")


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
    st.subheader("Clasificación demostrativa con árbol de decisión")
    st.write("Se entrena con datos **sintéticos** (escala 0–1) etiquetados con la misma regla heurística de "
             "criticidad. Sirve para demostrar el flujo de clasificación, no para predecir averías reales.")
    ml = entrenar_modelo()
    informe, clases = ml["informe"], ml["clases"]
    k = st.columns(4)
    k[0].metric("Exactitud (test)", f"{ml['acc'] * 100:.1f}%")
    k[1].metric("Precisión macro", f"{informe['macro avg']['precision'] * 100:.1f}%")
    k[2].metric("Recall macro", f"{informe['macro avg']['recall'] * 100:.1f}%")
    k[3].metric("F1 macro", f"{informe['macro avg']['f1-score'] * 100:.1f}%")
    st.caption("Las métricas miden cuánto reproduce el árbol una regla artificial; no son validación sobre una red real.")
    cA, cB = st.columns(2)
    with cA:
        st.markdown("#### Matriz de confusión")
        fig = go.Figure(go.Heatmap(z=ml["cm"], x=[f"Pred. {c}" for c in clases], y=[f"Real {c}" for c in clases],
                                   colorscale="Blues", text=ml["cm"], texttemplate="%{text}", showscale=False))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(autorange="reversed"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    with cB:
        st.markdown("#### Importancia de variables")
        imp = ml["imp"].sort_values("Importancia")
        fig = go.Figure(go.Bar(x=imp["Importancia"], y=imp["Variable"], orientation="h", marker_color="#4DA3FF"))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.markdown("#### Métricas por clase")
    st.dataframe(pd.DataFrame([{
        "Clase": c, "Precisión": round(informe[c]["precision"], 3), "Recall": round(informe[c]["recall"], 3),
        "F1": round(informe[c]["f1-score"], 3), "Muestras de prueba": int(informe[c]["support"])}
        for c in clases]), use_container_width=True, hide_index=True)
    st.markdown("#### Predicción para los dispositivos activos")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        dfp = df_crit[["Dispositivo", "Tipo", "Criticidad"] + ml["vars"]].copy()
        dfp["Criticidad predicha por ML"] = ml["modelo"].predict(dfp[ml["vars"]])
        dfp["Coincide"] = np.where(dfp["Criticidad"] == dfp["Criticidad predicha por ML"], "✅", "⚠️")
        st.dataframe(dfp, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
with tab_top:
    st.subheader("Inventario")
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

    st.markdown("#### 💾 Guardar y cargar topologías")
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
st.caption("NetSim · Proyecto académico de redes como grafos.")
