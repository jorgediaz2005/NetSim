"""NetSim · interfaz Streamlit del laboratorio de redes con teoría de grafos.

Orden del archivo (es también el orden de ejecución):
  1. Página y tema         5. Pestañas (una función por pestaña)
  2. Utilidades visuales   6. Ejecución de la página: panel lateral, escenario, cabecera y pestañas
  3. Estado y callbacks
  4. Componentes

Lógica de redes: netsim_core · Textos didácticos: netsim_edu · ML: netsim_ml · Informe: netsim_informe
Estilos y scripts: netsim_estilos, netsim_js
"""
import json
import random

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

import netsim_core as core
import netsim_edu as edu
import netsim_informe
import netsim_js
import netsim_ml
from netsim_core import ICONOS, PLANTILLAS, SIMBOLOS, TIPOS
from netsim_estilos import ARTE_HERO, colapsar_html, css_completo, esc, rgba

st.set_page_config(page_title="NetSim | Laboratorio de redes", page_icon="🌐",
                   layout="wide", initial_sidebar_state="expanded")


# =========================================================
# 1. PÁGINA Y TEMA
# =========================================================
# Un único tema de color (azul/violeta); lo que cambia es el modo claro u oscuro.
MODO_DIA = bool(st.session_state.get("modo_dia", False))  # por defecto: modo noche
C_ACENTO, C_ACENTO2 = "#4DA3FF", "#7C5CFF"

# Colores del mapa y los gráficos Plotly (en modo día se ajustan para conservar el contraste)
if MODO_DIA:
    C_TEXTO, C_SUAVE, C_ETQ, C_RUTA = "#0F172A", "#475569", "#334155", "#B45309"
    C_GRID, C_FONDO, C_TIP_BG, C_TIP_BORDE = "rgba(15,23,42,.10)", "#F3F6FB", "#FFFFFF", "#CBD5E1"
    C_MAL = "#B91C1C"
    COLORES = {"Baja": "#15803D", "Media": "#C2650A", "Alta": "#DC2626"}
    COLOR_ENLACE = {"rapido": "#0F766E", "medio": "#475569", "lento": "#7C3AED"}
    ESCALA_CALOR = [[0, "#EAF2FF"], [0.5, "#7FB2F5"], [1, "#1D5FD1"]]
    C_BORDE_NODO, C_PAQUETE, C_GAUGE_BG = "#1E293B", "#0F172A", "rgba(15,23,42,.07)"
    ALFA_ENLACE, ALFA_HALO = 0.95, 0.30
else:
    C_TEXTO, C_SUAVE, C_ETQ, C_RUTA = "#E6EDF3", "#94A3B8", "#CBD5E1", "#FFD166"
    C_GRID, C_FONDO, C_TIP_BG, C_TIP_BORDE = "rgba(255,255,255,.06)", "#0B0F1A", "#111827", "#334155"
    C_MAL = "#FF4D4F"
    COLORES = core.COLORES
    COLOR_ENLACE = {"rapido": "#5EEAD4", "medio": "#94A3B8", "lento": "#C084FC"}
    ESCALA_CALOR = [[0, "#10233f"], [0.5, "#2563eb"], [1, "#7DD3FC"]]
    C_BORDE_NODO, C_PAQUETE, C_GAUGE_BG = C_FONDO, "#FFFFFF", "rgba(255,255,255,.04)"
    ALFA_ENLACE, ALFA_HALO = 0.75, 0.16

LAT_RAPIDO = 2   # ms: enlaces rápidos
LAT_LENTO = 6    # ms: enlaces lentos
ANCHO_ENLACE = {"rapido": 3.2, "medio": 2.4, "lento": 1.8}


def _tema_base():
    """Tema con el que Streamlit pinta sus propios widgets (tablas, etc.)."""
    try:
        tipo = st.context.theme.type
        if tipo in ("light", "dark"):
            return tipo
    except Exception:  # noqa: BLE001  (versiones antiguas de Streamlit)
        pass
    try:  # en la primera ejecución el navegador aún no informa del tema: se usa el de config.toml
        base = st.get_option("theme.base")
        if base in ("light", "dark"):
            return base
    except Exception:  # noqa: BLE001
        pass
    return "dark"


INVERTIR_TABLAS = _tema_base() != ("light" if MODO_DIA else "dark")
st.markdown(css_completo(MODO_DIA, INVERTIR_TABLAS), unsafe_allow_html=True)


# =========================================================
# 2. UTILIDADES VISUALES
# =========================================================
def kpi(etiqueta, valor, sub="", tono="info", tip=""):
    return colapsar_html(f'<div class="kpi kpi-{tono}" title="{esc(tip)}">'
              f'<div><div class="kpi-label">{esc(etiqueta)}</div><div class="kpi-value">{esc(valor)}</div>'
              f'<div class="kpi-sub">{esc(sub)}</div></div></div>')


def seccion(titulo):
    st.markdown(f'<div class="sec">{esc(titulo)}</div>', unsafe_allow_html=True)


def nota_edu(clave):
    """Cuadro desplegable con una explicación didáctica; se oculta desde Configuración."""
    if not st.session_state.get("modo_edu", True):
        return
    titulo, texto = edu.EXPLICACIONES[clave]
    with st.expander(titulo):
        st.markdown(texto)


def _estilo_ejes(fig):
    for actualizar in (fig.update_xaxes, fig.update_yaxes):
        actualizar(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_GRID,
                   tickfont=dict(color=C_ETQ), title_font=dict(color=C_ETQ))


def estilo_fig(fig, alto=None, margen=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C_ETQ),
        hoverlabel=dict(font=dict(size=13, color=C_TEXTO), bgcolor=C_TIP_BG, bordercolor=C_TIP_BORDE),
        margin=margen or dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(color=C_ETQ)),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=C_SUAVE, activecolor=C_ACENTO))
    _estilo_ejes(fig)
    if alto:
        fig.update_layout(height=alto)
    return fig


def mostrar(fig):
    # Se aplica al final, cuando ya no se van a reemplazar títulos ni ejes, para que la plantilla
    # de Streamlit (pensada para fondo oscuro) no deje textos casi invisibles en modo día.
    _estilo_ejes(fig)
    fig.update_traces(colorbar_tickfont_color=C_ETQ, colorbar_title_font_color=C_ETQ,
                      selector=dict(type="heatmap"))
    fig.update_layout(legend=dict(font=dict(color=C_ETQ)))
    st.plotly_chart(fig, config={"displaylogo": False})


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
    return colapsar_html('<div class="route">' + "".join(partes) + "</div>")


def leyenda_mapa():
    return colapsar_html(f"""<div class="legend">
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
# 3. ESTADO Y CALLBACKS
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


# ---- callbacks ----
def _limpiar():
    reiniciar_escenario()
    st.toast("Escenario limpiado: todos los elementos activos")


def _fallo_aleatorio():
    if G.number_of_nodes():
        elegido = random.choice(list(G.nodes))
        st.session_state.sel_fallos = [elegido]
        st.toast(f"Fallo aleatorio: {elegido}")


def _peor_caso():
    df = core.impacto_dispositivos(G)
    if not df.empty:
        peor = df.iloc[0]["Dispositivo"]
        st.session_state.sel_fallos = [peor]
        st.toast(f"Peor caso: cae {peor}")


# Los cambios de red se hacen en callbacks: así se ejecutan ANTES de dibujar los
# selectores de fallos y Streamlit permite modificar su estado.
def _cargar_plantilla(nombre=None, ir_al_mapa=False):
    """Carga una plantilla; sin `nombre` usa la elegida en el selector del panel lateral."""
    nombre = nombre or st.session_state.plantilla_sel
    cambiar_red(PLANTILLAS[nombre]())
    aviso = ". Míralo en la pestaña Mapa" if ir_al_mapa else ""
    st.toast(f"Plantilla «{nombre}» cargada{aviso}")


def _importar():
    archivo = st.session_state.get("archivo_json")
    if archivo is None:
        st.session_state.msg_import = ("error", "Primero selecciona un archivo JSON.")
        return
    try:
        cambiar_red(core.red_desde_dict(json.load(archivo)))
        st.session_state.msg_import = ("ok", "Topología importada correctamente.")
        st.toast("Topología importada")
    except Exception as e:  # noqa: BLE001
        st.session_state.msg_import = ("error", f"No se pudo importar el archivo: {e}")


def _aplicar_mejora(u, v, lat):
    st.session_state.red.add_edge(u, v, weight=int(lat))
    st.session_state.posiciones = None
    st.toast(f"Enlace añadido: {u} ↔ {v}")


def _cargar_reto(i):
    r = edu.RETOS[i]
    cambiar_red(PLANTILLAS[r["plantilla"]]())
    st.session_state.sel_fallos = list(r["fallos"])
    st.session_state.sel_enlaces = [tuple(sorted(e)) for e in r["enlaces"]]
    if r["ruta"]:
        st.session_state.ruta_origen, st.session_state.ruta_destino = r["ruta"]
    st.toast("Reto cargado. Abre la pestaña Mapa para resolverlo")


def _reiniciar_quiz():
    for i in range(len(edu.QUIZ)):
        st.session_state.pop(f"quiz_{i}", None)


def _restaurar_red():
    cambiar_red(core.crear_red_inicial())
    st.toast("Red inicial restaurada")


@st.cache_data(show_spinner=False)
def _sugerencias(clave):
    return core.sugerir_enlaces(core.red_desde_dict(json.loads(clave)), 3)


@st.cache_data(show_spinner=False)
def _plantillas():
    return core.comparar_plantillas()


@st.cache_data(show_spinner=False)
def _modelo_ml():
    return netsim_ml.entrenar_modelo()


# =========================================================
# 4. COMPONENTES
# =========================================================
# Estas funciones leen el escenario activo (G, G_sim, fallos, df_crit...) que se calcula en la sección 6.


def titulo_lateral(texto):
    st.markdown(f'<div class="side-title">{texto}</div>', unsafe_allow_html=True)


def barra_lateral():
    """Panel de control. Devuelve las opciones de vista del mapa."""
    with st.sidebar:
        st.markdown(colapsar_html('<div class="brand"><div class="brand-logo">🌐</div><div>'
                                  '<div class="brand-name">NetSim</div><div class="brand-sub">Laboratorio de redes</div>'
                                  '</div></div>'), unsafe_allow_html=True)

        titulo_lateral("Escenario de fallos")
        st.multiselect("Dispositivos desactivados", sorted(G.nodes()), key="sel_fallos",
                       placeholder="Elige dispositivos…",
                       help="Se aplican al instante; la topología base no se modifica.")
        opciones_enlaces = [clave_enlace(u, v) for u, v in G.edges()]
        st.multiselect("Enlaces interrumpidos", opciones_enlaces, key="sel_enlaces",
                       placeholder="Elige enlaces…",
                       help="Simula cortes de cable o fallos de conexión entre dos dispositivos.",
                       format_func=lambda e: f"{e[0]} ↔ {e[1]} ({G[e[0]][e[1]].get('weight', 1)} ms)")
        st.button("Limpiar", on_click=_limpiar, width="stretch")
        b2, b3 = st.columns(2)
        b2.button("Aleatorio", on_click=_fallo_aleatorio, width="stretch",
                  help="Desactiva un dispositivo al azar")
        b3.button("Peor caso", on_click=_peor_caso, width="stretch",
                  help="Desactiva el dispositivo cuya caída incomunica a más pares")

        titulo_lateral("Construir red")

        with st.expander("Plantillas de topología"):
            st.selectbox("Plantilla (se carga al elegirla)", list(PLANTILLAS), key="plantilla_sel",
                         on_change=_cargar_plantilla)
            st.button("Recargar plantilla", on_click=_cargar_plantilla, width="stretch",
                      help="Vuelve a cargar la plantilla elegida, descartando los cambios hechos")

        with st.expander("Añadir dispositivo"):
            with st.form("agregar_dispositivo", clear_on_submit=True):
                nombre_nuevo = st.text_input("Nombre", placeholder="Ej. PC 3")
                tipo_nuevo = st.selectbox("Tipo", TIPOS, index=3, format_func=lambda t: f"{ICONOS[t]} {t}")
                ok_disp = st.form_submit_button("Añadir", width="stretch")
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

        with st.expander("Añadir / editar conexión"):
            nodos = sorted(G.nodes())
            if len(nodos) < 2:
                st.info("Añade al menos dos dispositivos.")
            else:
                with st.form("conexion"):
                    a = st.selectbox("Origen", nodos, key="con_a")
                    b = st.selectbox("Destino", nodos, index=1, key="con_b")
                    lat = st.number_input("Latencia (ms)", min_value=1, max_value=10000, value=5, step=1)
                    ok_con = st.form_submit_button("Guardar conexión", width="stretch")
                st.caption("Si la conexión ya existe, se actualiza su latencia.")
                if ok_con:
                    if a == b:
                        st.error("Origen y destino deben ser distintos.")
                    else:
                        G.add_edge(a, b, weight=int(lat))
                        st.session_state.posiciones = None
                        st.rerun()

        with st.expander("Eliminar elementos"):
            if G.number_of_nodes():
                nodo_borrar = st.selectbox("Dispositivo", sorted(G.nodes()), key="del_nodo")
                if st.button("Eliminar dispositivo", width="stretch"):
                    G.remove_node(nodo_borrar)
                    st.session_state.posiciones = None
                    st.rerun()
            if G.number_of_edges():
                enlace_borrar = st.selectbox("Conexión", opciones_enlaces, key="del_enlace",
                                             format_func=lambda e: f"{e[0]} ↔ {e[1]}")
                if st.button("Eliminar conexión", width="stretch"):
                    G.remove_edge(*enlace_borrar)
                    st.session_state.posiciones = None
                    st.rerun()

        titulo_lateral("Vista del mapa")
        layout_nombre = st.selectbox("Disposición del mapa",
                                     ["Resorte", "Circular", "Kamada-Kawai", "Capas (shell)"])
        mostrar_lat = st.toggle("Mostrar latencias", value=True)
        mostrar_ruta = st.toggle("Resaltar ruta calculada", value=True)
        mostrar_halo = st.toggle("Efecto de brillo en nodos", value=True)

        with st.expander("Configuración"):
            with st.expander("Apariencia"):
                st.toggle("Modo día", key="modo_dia",
                          help="Activado: modo día. Desactivado: modo noche (por defecto).")
                st.toggle("Explicaciones didácticas", value=True, key="modo_edu",
                          help="Muestra u oculta los cuadros de explicación de cada pestaña.")
            with st.expander("Ayuda"):
                st.markdown("**Cómo empezar**\n" +
                            "\n".join(f"{n}. {paso}" for n, paso in enumerate(edu.AYUDA_PASOS, 1)))
                st.divider()
                for preg, resp in edu.AYUDA_FAQ:
                    st.markdown(f"**{preg}**\n\n{resp}")
            with st.expander("Acerca de NetSim"):
                st.markdown("""
- Laboratorio para **estudiantes de redes** que empiezan con teoría de grafos.
- **Modelo:** grafo no dirigido (NetworkX); cada enlace tiene una latencia en ms y los fallos se aplican sobre una copia.
- **Rutas:** Dijkstra por latencia total. Criticidad y machine learning usan reglas heurísticas y datos sintéticos.
- **Límites:** no se conecta a equipos reales, no mide tráfico y no es una auditoría de seguridad.
""")
            st.button("Restaurar la red inicial", on_click=_restaurar_red, width="stretch",
                      help="Vuelve a la oficina pequeña y limpia el escenario de fallos")
    return layout_nombre, mostrar_lat, mostrar_ruta, mostrar_halo


def ruta_actual():
    """Ruta de menor latencia elegida en la pestaña Rutas (se calcula antes de dibujar el mapa)."""
    o, d = st.session_state.get("ruta_origen"), st.session_state.get("ruta_destino")
    if o is not None and d is not None and o in G_sim and d in G_sim and o != d \
            and nx.has_path(G_sim, o, d):
        r = nx.shortest_path(G_sim, o, d, weight="weight")
        return r, nx.shortest_path_length(G_sim, o, d, weight="weight")
    return [], None


def calcular_posiciones(g, nombre):
    """Posiciones de los nodos; se conservan entre ejecuciones mientras no cambie la red ni la disposición."""
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


def dibujar_mapa(original, simulada, crit, ruta, disposicion, mostrar_lat, halo=True, foco=None):
    if original.number_of_nodes() == 0:
        st.info("La topología está vacía. Añade dispositivos o carga una plantilla desde el panel lateral.")
        return
    pos = calcular_posiciones(original, disposicion)
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
          color=rgba(C_MAL, 0.65), width=1.8, dash="dot")

    # Enlaces activos agrupados por velocidad (color y grosor según latencia)
    grupos = {"rapido": [], "medio": [], "lento": []}
    for u, v, a in simulada.edges(data=True):
        if frozenset((u, v)) not in aristas_ruta:
            grupos[tramo_enlace(a.get("weight", 1))].append((u, v))
    for clave, aristas in grupos.items():
        trazo(aristas, color=rgba(COLOR_ENLACE[clave], ALFA_ENLACE), width=ANCHO_ENLACE[clave])

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
            textfont=dict(size=11, color=C_ETQ),
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
                            color=[rgba(c, ALFA_HALO) for c in colores]),
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
                          color=[C_RUTA if n in en_ruta else C_BORDE_NODO for n in activos]),
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
            marker=dict(size=15, color=C_PAQUETE, line=dict(width=3, color=C_RUTA))))
        idx = len(fig.data) - 1
        fig.frames = [go.Frame(data=[go.Scatter(x=[px[i]], y=[py[i]])], traces=[idx], name=str(i))
                      for i in range(len(px))]
        fig.update_layout(updatemenus=[dict(
            type="buttons", showactive=False, direction="left", x=0.01, y=0.99,
            xanchor="left", yanchor="top", bgcolor=C_TIP_BG, bordercolor=C_RUTA,
            font=dict(color=C_TEXTO),
            buttons=[dict(label="▶ Enviar paquete", method="animate",
                          args=[None, dict(frame=dict(duration=45, redraw=False),
                                           transition=dict(duration=0), fromcurrent=False,
                                           mode="immediate")])])])

    estilo_fig(fig, alto=620)
    fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    mostrar(fig)
    st.markdown(leyenda_mapa(), unsafe_allow_html=True)


def ficha_dispositivo(nombre):
    """Ficha HTML de un dispositivo en el escenario activo."""
    tipo = G.nodes[nombre].get("tipo", "Otro")
    caido = nombre in fallos
    fila = df_crit[df_crit["Dispositivo"] == nombre] if not df_crit.empty else df_crit
    if len(fila):
        nivel_c = fila.iloc[0]["Criticidad"]
        crit_txt = f'{nivel_c} · {fila.iloc[0]["Puntuación"]}'
        crit_tono = {"Alta": "bad", "Media": "warn", "Baja": "ok"}[nivel_c]
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
    return colapsar_html(
        f'<div class="ficha"><div class="ficha-head"><div class="ficha-ico">{ICONOS.get(tipo, "🔧")}</div>'
        f'<div><div class="ficha-name">{esc(nombre)}</div><div class="ficha-type">{esc(tipo)} '
        f'<span class="status status-{estado_tono}"><i class="dot"></i>{estado_txt}</span></div></div></div>'
        f'<div class="ficha-grid">'
        + kpi("Conexiones", G.degree[nombre], "Enlaces directos en la red base", "info")
        + kpi("Criticidad", crit_txt, "En el escenario actual", crit_tono)
        + kpi("Punto único de fallo", "Sí" if es_spof else "No",
              "Su caída separa la red" if es_spof else "La red resiste su caída", "bad" if es_spof else "ok")
        + kpi("Si cae…", f"{pares_si_cae} pares", "Pares ajenos que pierden comunicación",
              "bad" if pares_si_cae else "ok")
        + '</div><div class="nbs-title">Conexiones directas</div>'
        + ("".join(vecinos) if vecinos else '<span class="nb">Sin conexiones</span>') + '</div>')


def explicar_escenario():
    """Explica con palabras sencillas lo que ocurre en el escenario actual."""
    if not (fallos or enlaces_fallidos):
        return ("Ahora mismo todo está operativo: es la **red base**. Apaga un dispositivo o corta un enlace en el "
                "panel lateral (*Escenario de fallos*) y aquí verás qué significa lo que ocurre.")
    partes = []
    if fallos:
        partes.append(f"Has apagado **{', '.join(fallos)}**. Al caer un dispositivo se pierden también todos sus enlaces.")
    if enlaces_fallidos:
        partes.append("Has cortado " + ", ".join(f"**{u} ↔ {v}**" for u, v in enlaces_fallidos) + ".")
    if n_activos == 0:
        partes.append("No queda ningún dispositivo activo.")
    elif pares_perdidos:
        partes.append(f"La red activa se ha dividido en **{comp_act} grupos** y **{len(pares_perdidos)} pares** de equipos "
                      "encendidos ya no pueden comunicarse. Es lo que pasa cuando cae un *punto único de fallo* o un "
                      "*puente*: no había un camino alternativo.")
    else:
        partes.append("Aun así, **todos los equipos activos siguen pudiendo comunicarse**: la red tiene redundancia "
                      "suficiente para este fallo. Quizá algunas rutas ahora sean más largas; compruébalo en *Rutas*.")
    return "\n\n".join(partes)


def informe_html():
    sugerencias = _sugerencias(clave_red) if G.number_of_nodes() >= 3 else []
    return netsim_informe.generar_informe(G, G_sim, fallos, enlaces_fallidos, pares_perdidos, df_crit,
                                          sugerencias, MODO_DIA)


# =========================================================
# 5. PESTAÑAS
# =========================================================
def pestana_mapa():
    """Mapa de la red, estado del escenario e inspector de dispositivos."""
    dibujar_mapa(G, G_sim, df_crit, ruta if mostrar_ruta else [], layout_nombre, mostrar_lat, mostrar_halo,
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
                st.dataframe(pd.DataFrame(pares_perdidos, columns=["Origen", "Destino"]), hide_index=True)
        else:
            st.success("Los dispositivos activos siguen comunicados entre sí como en la base.")

    if st.session_state.get("modo_edu", True):
        with st.expander("¿Qué está pasando en este escenario?", expanded=bool(fallos or enlaces_fallidos)):
            st.markdown(explicar_escenario())
    nota_edu("mapa")

    seccion("Inspector de dispositivos")
    opciones_insp = [None] + sorted(G.nodes())
    if st.session_state.get("inspector") not in opciones_insp:
        st.session_state["inspector"] = None
    st.selectbox("Elige un dispositivo para ver su ficha y resaltarlo en el mapa", opciones_insp, key="inspector",
                 format_func=lambda x: "— ninguno —" if x is None else f"{ICONOS.get(G.nodes[x].get('tipo'), '')} {x}")
    if st.session_state.inspector is not None:
        st.markdown(ficha_dispositivo(st.session_state.inspector), unsafe_allow_html=True)


def pestana_rutas():
    """Ruta de menor latencia (Dijkstra), alternativas y matriz de latencias."""
    seccion("Ruta de menor latencia (Dijkstra)")
    nota_edu("rutas")
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
                k1.markdown(kpi("Latencia total", f"{lat:g} ms", "Suma de los tramos", "info"),
                            unsafe_allow_html=True)
                k2.markdown(kpi("Saltos", len(mejor) - 1, "Enlaces recorridos", "info"),
                            unsafe_allow_html=True)
                k3.markdown(kpi("Rutas posibles", len(alternativas),
                                "Hay redundancia" if len(alternativas) > 1 else "Sin redundancia",
                                "ok" if len(alternativas) > 1 else "warn"), unsafe_allow_html=True)
                seccion("Camino óptimo")
                st.markdown(cadena_ruta(mejor, G_sim), unsafe_allow_html=True)
                tabla = pd.DataFrame([{"Tramo": f"{u} → {v}", "Latencia (ms)": G_sim[u][v].get("weight", 1)}
                                      for u, v in zip(mejor[:-1], mejor[1:])])
                st.dataframe(tabla, hide_index=True)
                if len(alternativas) > 1:
                    seccion("Rutas alternativas")
                    st.dataframe(pd.DataFrame([
                        {"Opción": i, "Ruta": " → ".join(r), "Latencia (ms)": l, "Saltos": len(r) - 1,
                         "Sobrecoste (ms)": round(l - lat, 2)}
                        for i, (r, l) in enumerate(alternativas, 1)]), hide_index=True)
                else:
                    st.info("No hay rutas alternativas: esta ruta no tiene redundancia.")
                st.caption("La ruta se resalta en amarillo en el mapa; allí puedes pulsar «▶ Enviar paquete» "
                           "para ver el recorrido animado.")
        with st.expander("Matriz de latencias mínimas entre dispositivos activos"):
            mat = core.matriz_latencias(G_sim)
            fig = go.Figure(go.Heatmap(z=mat.values, x=mat.columns, y=mat.index,
                                       colorscale=ESCALA_CALOR,
                                       text=mat.round(1).astype(str).values, texttemplate="%{text}",
                                       hoverongaps=False, colorbar=dict(title="ms")))
            estilo_fig(fig, alto=440)
            fig.update_layout(yaxis=dict(autorange="reversed"))
            mostrar(fig)
            st.caption("Las celdas vacías indican dispositivos sin ruta entre sí.")


def pestana_criticidad():
    """Puntuación de criticidad de los dispositivos activos."""
    seccion("Criticidad de dispositivos")
    st.write(f"Puntuación = {core.PESO_GRADO * 100:.0f} % centralidad de grado + "
             f"{core.PESO_INTERMEDIACION * 100:.0f} % intermediación + {core.PESO_TIPO * 100:.0f} % importancia del tipo.")
    nota_edu("criticidad")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        cuenta = df_crit["Criticidad"].value_counts()
        a, b, c = st.columns(3)
        a.markdown(kpi("Criticidad alta", int(cuenta.get("Alta", 0)), "Dispositivos clave", "bad"),
                   unsafe_allow_html=True)
        b.markdown(kpi("Criticidad media", int(cuenta.get("Media", 0)), "Relevancia moderada", "warn"),
                   unsafe_allow_html=True)
        c.markdown(kpi("Criticidad baja", int(cuenta.get("Baja", 0)), "Menor influencia", "ok"),
                   unsafe_allow_html=True)
        st.write("")
        cd, cb = st.columns([1, 2])
        with cd:
            niveles = ["Alta", "Media", "Baja"]
            color_texto_pie = ["#FFFFFF", "#0B0F1A", "#FFFFFF"] if MODO_DIA else "#0B0F1A"
            fig = go.Figure(go.Pie(
                labels=niveles, values=[int(cuenta.get(n, 0)) for n in niveles], hole=0.62, sort=False,
                marker=dict(colors=[COLORES[n] for n in niveles], line=dict(color=C_FONDO, width=3)),
                textinfo="percent", insidetextfont=dict(color=color_texto_pie, size=13),
                hovertemplate="%{label}: %{value} dispositivo(s)<extra></extra>"))
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
                                               line=dict(color=C_GRID, width=1)),
                                   text=orden["Puntuación"], textposition="outside"))
            estilo_fig(fig, alto=max(280, 38 * len(orden)), margen=dict(l=10, r=40, t=10, b=10))
            fig.update_layout(xaxis=dict(range=[0, 1], title="Puntuación", gridcolor=C_GRID))
            mostrar(fig)
        vista = df_crit.copy()
        vista["Criticidad"] = vista["Criticidad"].map({"Alta": "🔴 Alta", "Media": "🟠 Media", "Baja": "🟢 Baja"})
        st.dataframe(vista, hide_index=True,
                     column_config={"Puntuación": st.column_config.ProgressColumn(
                         "Puntuación", min_value=0.0, max_value=1.0, format="%.3f")})
        st.caption(f"Umbrales: baja < {core.UMBRAL_MEDIA:.2f} · media {core.UMBRAL_MEDIA:.2f}–{core.UMBRAL_ALTA:.2f} · "
                   f"alta ≥ {core.UMBRAL_ALTA:.2f}. Regla heurística académica, no una medición de riesgo real.")
        st.download_button("Descargar criticidad (CSV)", df_crit.to_csv(index=False).encode("utf-8-sig"),
                           file_name="criticidad_netsim.csv", mime="text/csv")


def pestana_resiliencia():
    """Puntos únicos de fallo, puentes, mejoras sugeridas y comparación con plantillas."""
    seccion("Análisis de resiliencia de la topología base")
    nota_edu("resiliencia")
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
                    mode="gauge+number", value=round(indice, 1), number=dict(suffix=" %", font=dict(size=44, color=C_TEXTO)),
                    title=dict(text="Índice de resiliencia", font=dict(size=15, color=C_SUAVE)),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickcolor=C_SUAVE),
                        bar=dict(color=C_ACENTO, thickness=0.28), bgcolor=C_GAUGE_BG,
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
            st.markdown(kpi("Puntos únicos de fallo", n_spof,
                            "Su caída fragmenta la red" if n_spof else "Ninguno", "bad" if n_spof else "ok"),
                        unsafe_allow_html=True)
            st.write("")
            st.markdown(kpi("Enlaces críticos (puentes)", n_puentes,
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
            st.dataframe(vista_n, hide_index=True, column_config={
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
                st.dataframe(vista_e, hide_index=True, column_config={
                    "Pares que pierden comunicación": st.column_config.ProgressColumn(
                        "Pares que pierden comunicación", min_value=0,
                        max_value=max(1, int(df_enl["Pares que pierden comunicación"].max())), format="%d")})
        st.caption("«Pares que pierden comunicación» cuenta parejas de dispositivos que dejan de poder "
                   "comunicarse (sin contar el propio dispositivo caído).")

        seccion("Mejoras sugeridas")
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
                    ca.markdown(kpi(f"Opción {i + 1}", f"{sg['origen']} ↔ {sg['destino']}",
                                    f"Reduce el riesgo en {sg['reduccion']} elemento(s)", "info"),
                                unsafe_allow_html=True)
                    cb_.markdown(kpi("Resiliencia resultante", f"{sg['indice_despues']:.0f} %",
                                     f"{sg['spof_despues']} puntos únicos · {sg['puentes_despues']} puentes", "ok"),
                                 unsafe_allow_html=True)
                    cc_.button("Aplicar", key=f"aplicar_mejora_{i}", on_click=_aplicar_mejora,
                               args=(sg["origen"], sg["destino"], sg["latencia"]), width="stretch")
                st.caption("Heurística estructural: prueba cada enlace posible y mide cuánto baja el riesgo. "
                           "No distingue qué equipos pueden reenviar tráfico en una red real.")

        with st.expander("Comparar con las plantillas de topología"):
            comp_df = pd.concat([pd.DataFrame([{"Topología": "Tu red actual", **core.metricas_topologia(G)}]),
                                 _plantillas()], ignore_index=True)
            vals = comp_df["Índice de resiliencia (%)"].fillna(0)
            fig = go.Figure(go.Bar(
                x=comp_df["Topología"], y=vals, text=vals.round(0).astype(int).astype(str) + " %",
                textposition="outside",
                marker=dict(color=[C_ACENTO2] + [C_ACENTO] * (len(comp_df) - 1))))
            estilo_fig(fig, alto=330, margen=dict(l=10, r=10, t=30, b=10))
            fig.update_layout(yaxis=dict(range=[0, 115], title="Índice de resiliencia (%)",
                                         gridcolor=C_GRID))
            mostrar(fig)
            st.dataframe(comp_df, hide_index=True)


def pestana_ml():
    """Demostración de clasificación con árbol de decisión."""
    seccion("Clasificación demostrativa con árbol de decisión")
    nota_edu("ml")
    st.write("Se entrena con datos **sintéticos** (escala 0–1) etiquetados con la misma regla heurística de "
             "criticidad. Sirve para demostrar el flujo de clasificación, no para predecir averías reales.")
    ml = _modelo_ml()
    informe, clases = ml["informe"], ml["clases"]
    k = st.columns(4)
    k[0].markdown(kpi("Exactitud (test)", f"{ml['acc'] * 100:.1f}%", "Aciertos / total", "info"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Precisión macro", f"{informe['macro avg']['precision'] * 100:.1f}%",
                      "Promedio por clase", "info"), unsafe_allow_html=True)
    k[2].markdown(kpi("Recall macro", f"{informe['macro avg']['recall'] * 100:.1f}%",
                      "Promedio por clase", "info"), unsafe_allow_html=True)
    k[3].markdown(kpi("F1 macro", f"{informe['macro avg']['f1-score'] * 100:.1f}%",
                      "Equilibrio precisión/recall", "info"), unsafe_allow_html=True)
    st.caption("Las métricas miden cuánto reproduce el árbol una regla artificial; no son validación sobre una red real.")
    cA, cB = st.columns(2)
    with cA:
        seccion("Matriz de confusión")
        fig = go.Figure(go.Heatmap(z=ml["cm"], x=[f"Pred. {c}" for c in clases], y=[f"Real {c}" for c in clases],
                                   colorscale=ESCALA_CALOR,
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
        fig.update_layout(xaxis=dict(gridcolor=C_GRID))
        mostrar(fig)
    seccion("Métricas por clase")
    st.dataframe(pd.DataFrame([{
        "Clase": c, "Precisión": round(informe[c]["precision"], 3), "Recall": round(informe[c]["recall"], 3),
        "F1": round(informe[c]["f1-score"], 3), "Muestras de prueba": int(informe[c]["support"])}
        for c in clases]), hide_index=True)
    seccion("Predicción para los dispositivos activos")
    if df_crit.empty:
        st.info("No hay dispositivos activos.")
    else:
        dfp = df_crit[["Dispositivo", "Tipo", "Criticidad"] + ml["vars"]].copy()
        dfp["Criticidad predicha por ML"] = ml["modelo"].predict(dfp[ml["vars"]])
        dfp["Coincide"] = np.where(dfp["Criticidad"] == dfp["Criticidad predicha por ML"], "✅", "⚠️")
        st.dataframe(dfp, hide_index=True)


def pestana_topologia():
    """Inventario, exportación (JSON/CSV/HTML) e importación de topologías."""
    seccion("Inventario")
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
            st.dataframe(inventario, hide_index=True)
        else:
            st.info("Sin dispositivos.")
    with cB:
        st.markdown("#### Conexiones")
        if not conexiones.empty:
            st.dataframe(conexiones, hide_index=True)
        else:
            st.info("Sin conexiones.")

    seccion("Guardar y cargar topologías")
    nota_edu("topologia")
    resumen = {
        "dispositivos_totales": G.number_of_nodes(), "dispositivos_activos": n_activos,
        "enlaces_totales": G.number_of_edges(), "enlaces_activos": n_enlaces,
        "componentes_originales": comp_orig, "componentes_actuales": comp_act,
        "pares_que_perdieron_comunicacion": [list(p) for p in pares_perdidos],
        "dispositivos_desactivados": fallos, "enlaces_interrumpidos": [list(e) for e in enlaces_fallidos],
        "nota": "Simulación académica: no representa mediciones de una red real.",
    }
    e1, e2, e3 = st.columns(3)
    e1.download_button("Topología (JSON)", json.dumps(core.red_a_dict(G), ensure_ascii=False, indent=2),
                       file_name="topologia_netsim.json", mime="application/json", width="stretch")
    e2.download_button("Enlaces (CSV)",
                       (conexiones.to_csv(index=False) if not conexiones.empty
                        else "Origen,Destino,Latencia (ms),Estado\n").encode("utf-8-sig"),
                       file_name="enlaces_netsim.csv", mime="text/csv", width="stretch")
    e3.download_button("Escenario (JSON)", json.dumps(resumen, ensure_ascii=False, indent=2),
                       file_name="escenario_netsim.json", mime="application/json", width="stretch")
    st.download_button("Informe completo del escenario (HTML, imprimible a PDF)", informe_html(),
                       file_name="informe_netsim.html", mime="text/html", width="stretch")
    st.file_uploader("Cargar una topología guardada (JSON de NetSim)", type=["json"], key="archivo_json")
    st.button("Importar topología", type="primary", on_click=_importar)
    with st.expander("Formato del archivo JSON"):
        st.write("El campo `latencia` es opcional (por defecto 1) y un tipo no reconocido se convierte en «Otro».")
        st.code(edu.JSON_EJEMPLO, language="json")
        st.download_button("Descargar este ejemplo", edu.JSON_EJEMPLO, file_name="ejemplo_netsim.json",
                           mime="application/json")
    estado_import = st.session_state.pop("msg_import", None)
    if estado_import:
        (st.success if estado_import[0] == "ok" else st.error)(estado_import[1])


def pestana_aprende():
    """Lecciones, topologías, retos, glosario y test."""
    seccion("Aprende redes con NetSim")
    st.write(f"Material pensado para {edu.PUBLICO}. Sigue el orden o salta a lo que necesites: cada lección "
             "termina con algo que puedes **probar en la app**.")
    sub_lec, sub_top, sub_ret, sub_glo, sub_quiz = st.tabs(
        ["Lecciones", "Topologías", "Retos", "Glosario", "Test"])
    clase_nivel = {"Básico": "ok", "Intermedio": "warn", "Avanzado": "bad"}

    with sub_lec:
        for lec in edu.LECCIONES:
            with st.expander(f"{lec['titulo']}  ·  {lec['nivel']}"):
                st.markdown(lec["texto"])

    with sub_top:
        nombre_top = st.selectbox("Elige una topología", list(PLANTILLAS), key="edu_top")
        ficha_top = edu.TOPOLOGIAS[nombre_top]
        fila_top = _plantillas().set_index("Topología").loc[nombre_top]
        st.markdown(f"**Idea:** {ficha_top['idea']}")
        ca, cb = st.columns(2)
        ca.markdown("**Ventajas**\n" + "\n".join(f"- {x}" for x in ficha_top["pros"]))
        cb.markdown("**Inconvenientes**\n" + "\n".join(f"- {x}" for x in ficha_top["contras"]))
        st.caption(f"Uso típico: {ficha_top['uso']}")
        indice_top = fila_top["Índice de resiliencia (%)"]
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(kpi("Dispositivos", int(fila_top["Dispositivos"]), "", "info"), unsafe_allow_html=True)
        k2.markdown(kpi("Enlaces", int(fila_top["Enlaces"]), "", "info"), unsafe_allow_html=True)
        n_sp = int(fila_top["Puntos únicos de fallo"])
        k3.markdown(kpi("Puntos únicos de fallo", n_sp, "", "bad" if n_sp else "ok"), unsafe_allow_html=True)
        k4.markdown(kpi("Índice de resiliencia", f"{indice_top:.0f} %" if pd.notna(indice_top) else "—",
                        f"{int(fila_top['Enlaces puente'])} enlaces puente", "info"), unsafe_allow_html=True)
        st.write("")
        st.button("Cargar esta topología en el mapa", key="edu_cargar", on_click=_cargar_plantilla,
                  args=(nombre_top, True), type="primary")
        seccion("Compara las cinco plantillas")
        st.dataframe(_plantillas(), hide_index=True)
        st.caption("Fíjate en que un índice alto no lo es todo: la estrella tiene un solo punto único de fallo, "
                   "pero todos sus enlaces son puentes.")

    with sub_ret:
        st.write("Cada reto **carga una red y un escenario**. Resuélvelo mirando la app y comprueba tu respuesta.")
        for i, reto in enumerate(edu.RETOS):
            with st.container(border=True):
                st.markdown(f'<b>{esc(reto["titulo"])}</b><span class="nv nv-{clase_nivel[reto["nivel"]]}">'
                            f'{esc(reto["nivel"])}</span>', unsafe_allow_html=True)
                st.write(reto["objetivo"])
                b1, b2, b3 = st.columns([1.3, 1, 1])
                b1.button("Cargar reto", key=f"reto_cargar_{i}", on_click=_cargar_reto, args=(i,),
                          width="stretch")
                ver_pista = b2.toggle("Pistas", key=f"reto_pista_{i}")
                ver_sol = b3.toggle("Solución", key=f"reto_sol_{i}")
                if ver_pista:
                    st.info("\n".join(f"- {x}" for x in reto["pistas"]))
                if ver_sol:
                    st.success(reto["solucion"])

    with sub_glo:
        consulta = st.text_input("Buscar un término", key="glo_q",
                                 placeholder="Ej. puente, latencia, Dijkstra…").strip().lower()
        items = [g for g in edu.GLOSARIO if consulta in " ".join(g[1:]).lower()]
        if not items:
            st.info("No hay términos que coincidan con la búsqueda.")
        cols = st.columns(2)
        for i, (term, defin, en) in enumerate(items):
            cols[i % 2].markdown(
                colapsar_html(f'<div class="gl"><b>{esc(term)}</b><p>{esc(defin)}</p>'
                   f'<small>En NetSim: {esc(en)}</small></div>'), unsafe_allow_html=True)

    with sub_quiz:
        st.write(f"{len(edu.QUIZ)} preguntas para comprobar lo aprendido. Se corrigen todas a la vez.")
        with st.form("quiz_form"):
            for i, (preg, ops, _ok, _ex) in enumerate(edu.QUIZ):
                st.radio(f"**{i + 1}. {preg}**", ops, index=None, key=f"quiz_{i}")
            enviado = st.form_submit_button("Corregir", type="primary")
        if enviado:
            resp = [st.session_state.get(f"quiz_{i}") for i in range(len(edu.QUIZ))]
            if any(r is None for r in resp):
                st.warning("Responde todas las preguntas antes de corregir.")
            else:
                aciertos = sum(r == q[1][q[2]] for r, q in zip(resp, edu.QUIZ))
                total = len(edu.QUIZ)
                if aciertos == total:
                    msg, tono = "¡Perfecto! Dominas lo básico.", "ok"
                elif aciertos >= total * 0.6:
                    msg, tono = "Bien. Repasa las que has fallado.", "warn"
                else:
                    msg, tono = "Repasa las lecciones y vuelve a intentarlo.", "bad"
                st.markdown(kpi("Resultado", f"{aciertos}/{total}", msg, tono), unsafe_allow_html=True)
                st.write("")
                for i, (r, q) in enumerate(zip(resp, edu.QUIZ)):
                    if r == q[1][q[2]]:
                        st.success(f"**{i + 1}. Correcto.** {q[3]}")
                    else:
                        st.error(f"**{i + 1}. Incorrecto.** {q[3]}  \nRespuesta correcta: **{q[1][q[2]]}**")
                if aciertos == total:
                    st.balloons()
        st.button("Repetir el test", on_click=_reiniciar_quiz)


# =========================================================
# 6. EJECUCIÓN DE LA PÁGINA
# =========================================================
layout_nombre, mostrar_lat, mostrar_ruta, mostrar_halo = barra_lateral()

# ---- escenario activo ----
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


ruta, ruta_lat = ruta_actual()

# ---- cabecera ----
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

st.markdown(colapsar_html(f"""<div class="hero"><div class="hero-text">
<div class="hero-eyebrow">LABORATORIO DE REDES PARA ESTUDIANTES · TEORÍA DE GRAFOS</div>
<h1>Net<span>Sim</span></h1>
<p>Aprende cómo se comporta una red: construye una topología, apaga equipos, corta enlaces y descubre por qué importa la redundancia.</p>
<div class="hero-chips">
<span class="status status-{tono}"><i class="dot"></i>{estado}</span>
<span class="chip">{n_activos}/{G.number_of_nodes()} dispositivos</span>
<span class="chip">{n_enlaces}/{G.number_of_edges()} enlaces</span>
<span class="chip">{comp_act} componente{'s' if comp_act != 1 else ''}</span>
<span class="chip">Nivel: iniciación</span>
</div></div>{ARTE_HERO}</div>"""), unsafe_allow_html=True)


# ---- estado general y métricas ----
if fallos or enlaces_fallidos:
    etiquetas = "".join(f'<span class="tag">{esc(n)}</span>' for n in fallos)
    etiquetas += "".join(f'<span class="tag">{esc(u)} ↔ {esc(v)}</span>' for u, v in enlaces_fallidos)
    st.markdown(f'<div class="scenario"><b>Escenario de fallo activo:</b> {etiquetas}</div>',
                unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
enl_perdidos = G.number_of_edges() - n_enlaces
m1.markdown(kpi("Dispositivos activos", f"{n_activos}/{G.number_of_nodes()}",
                f"{len(fallos)} desactivado{'s' if len(fallos) != 1 else ''}" if fallos else "Todos operativos",
                "bad" if fallos else "ok"), unsafe_allow_html=True)
m2.markdown(kpi("Enlaces activos", f"{n_enlaces}/{G.number_of_edges()}",
                f"{enl_perdidos} interrumpido{'s' if enl_perdidos != 1 else ''}" if enl_perdidos
                else "Todos operativos", "bad" if enl_perdidos else "ok"), unsafe_allow_html=True)
m3.markdown(kpi("Componentes conectados", comp_act,
                 f"{comp_act - comp_orig:+d} respecto a la base" if comp_act != comp_orig else "Sin cambios",
                 "ok" if comp_act <= comp_orig else "bad"), unsafe_allow_html=True)
m4.markdown(kpi("Pares activos sin comunicación", len(pares_perdidos),
                "Comunicación íntegra" if not pares_perdidos else "Parejas que perdieron el camino",
                "ok" if not pares_perdidos else "bad",
                tip="Parejas de dispositivos que siguen activos y ya no pueden comunicarse entre sí."),
                unsafe_allow_html=True)
st.write("")

# ---- pestañas ----
tab_red, tab_rutas, tab_crit, tab_res, tab_edu, tab_ml, tab_top = st.tabs([
    "Mapa", "Rutas", "Criticidad", "Resiliencia", "Aprende", "Machine Learning",
    "Topología y exportación"])

for pestana_ui, dibujar in ((tab_red, pestana_mapa), (tab_rutas, pestana_rutas), (tab_crit, pestana_criticidad),
                            (tab_res, pestana_resiliencia), (tab_ml, pestana_ml), (tab_top, pestana_topologia),
                            (tab_edu, pestana_aprende)):
    with pestana_ui:
        dibujar()

# ---- pie ----
st.divider()
st.caption("NetSim · Laboratorio educativo de redes con teoría de grafos · Proyecto académico.")

# Animaciones de la página (ver netsim_js). El tema se resuelve solo con CSS, así que el script
# no depende del modo. Se inyecta UNA vez: el iframe de respaldo solo se usa si esta Streamlit
# no admite ya el JavaScript directo en la página.
_JS_PAGINA = netsim_js.script_animaciones()
try:  # Streamlit reciente: el script se ejecuta directamente en la página
    st.html(_JS_PAGINA, unsafe_allow_javascript=True)
except TypeError:  # noqa: BLE001  (versiones sin unsafe_allow_javascript)
    try:  # respaldo: iframe oculto con acceso a la página
        components.html(_JS_PAGINA, height=0)
    except Exception:  # noqa: BLE001  (si no se puede inyectar, el CSS sigue funcionando)
        pass
