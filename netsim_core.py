"""Lógica de NetSim: topologías, criticidad, resiliencia y utilidades.

Separada de la interfaz (app.py) para que sea fácil de probar y de explicar
en la memoria del proyecto.
"""
from __future__ import annotations

from itertools import islice
from math import comb

import networkx as nx
import pandas as pd

TIPOS = ["Router", "Switch", "Servidor", "PC", "Firewall", "Punto de acceso", "Otro"]

PESOS_TIPO = {
    "Router": 1.00,
    "Firewall": 0.95,
    "Servidor": 0.90,
    "Switch": 0.70,
    "Punto de acceso": 0.55,
    "PC": 0.30,
    "Otro": 0.40,
}

ICONOS = {
    "Router": "🛜",
    "Firewall": "🛡️",
    "Servidor": "🗄️",
    "Switch": "🔀",
    "Punto de acceso": "📡",
    "PC": "💻",
    "Otro": "🔧",
}

SIMBOLOS = {
    "Router": "diamond",
    "Firewall": "square",
    "Servidor": "hexagon",
    "Switch": "circle",
    "Punto de acceso": "star",
    "PC": "triangle-up",
    "Otro": "pentagon",
}

COLORES = {"Baja": "#2ECC71", "Media": "#F5A623", "Alta": "#FF4D4F"}

UMBRAL_MEDIA = 0.30
UMBRAL_ALTA = 0.60


# ---------------------------------------------------------------------------
# Topologías
# ---------------------------------------------------------------------------
def _construir(dispositivos, conexiones) -> nx.Graph:
    g = nx.Graph()
    for nombre, tipo in dispositivos:
        g.add_node(nombre, tipo=tipo)
    for a, b, lat in conexiones:
        g.add_edge(a, b, weight=lat)
    return g


def red_oficina() -> nx.Graph:
    return _construir(
        [("Router", "Router"), ("Switch 1", "Switch"), ("Switch 2", "Switch"),
         ("Servidor", "Servidor"), ("PC 1", "PC"), ("PC 2", "PC"), ("Firewall", "Firewall")],
        [("Router", "Firewall", 1), ("Firewall", "Switch 1", 2), ("Router", "Switch 2", 5),
         ("Switch 1", "Switch 2", 1), ("Switch 1", "Servidor", 6), ("Switch 2", "Servidor", 2),
         ("Switch 1", "PC 1", 3), ("Switch 2", "PC 2", 4)],
    )


def red_estrella() -> nx.Graph:
    disp = [("Switch central", "Switch")] + [(f"PC {i}", "PC") for i in range(1, 6)] + [("Servidor", "Servidor")]
    con = [("Switch central", n, 2 + i) for i, (n, _) in enumerate(disp[1:])]
    return _construir(disp, con)


def red_anillo() -> nx.Graph:
    disp = [(f"Switch {i}", "Switch") for i in range(1, 6)] + [("Router", "Router")]
    con = [(f"Switch {i}", f"Switch {i % 5 + 1}", 2 + i % 3) for i in range(1, 6)]
    con.append(("Router", "Switch 1", 1))
    return _construir(disp, con)


def red_campus() -> nx.Graph:
    disp = [
        ("Router", "Router"), ("Firewall", "Firewall"),
        ("Núcleo A", "Switch"), ("Núcleo B", "Switch"),
        ("Acceso 1", "Switch"), ("Acceso 2", "Switch"), ("Acceso 3", "Switch"),
        ("Servidor web", "Servidor"), ("Servidor BD", "Servidor"),
        ("AP 1", "Punto de acceso"), ("PC 1", "PC"), ("PC 2", "PC"), ("PC 3", "PC"),
    ]
    con = [
        ("Router", "Firewall", 1), ("Firewall", "Núcleo A", 1), ("Firewall", "Núcleo B", 2),
        ("Núcleo A", "Núcleo B", 1),
        ("Núcleo A", "Acceso 1", 2), ("Núcleo A", "Acceso 2", 3),
        ("Núcleo B", "Acceso 2", 2), ("Núcleo B", "Acceso 3", 3),
        ("Núcleo A", "Servidor web", 2), ("Núcleo B", "Servidor BD", 2),
        ("Acceso 1", "AP 1", 4), ("Acceso 1", "PC 1", 5),
        ("Acceso 2", "PC 2", 4), ("Acceso 3", "PC 3", 5),
    ]
    return _construir(disp, con)


def red_malla() -> nx.Graph:
    disp = [(f"Router {i}", "Router") for i in range(1, 5)] + [("Servidor", "Servidor"), ("PC 1", "PC")]
    con = [("Router 1", "Router 2", 3), ("Router 2", "Router 3", 4), ("Router 3", "Router 4", 2),
           ("Router 4", "Router 1", 5), ("Router 1", "Router 3", 6),
           ("Router 3", "Servidor", 1), ("Router 1", "PC 1", 2)]
    return _construir(disp, con)


PLANTILLAS = {
    "Oficina pequeña": red_oficina,
    "Estrella (1 switch)": red_estrella,
    "Anillo de switches": red_anillo,
    "Campus con redundancia": red_campus,
    "Malla de routers": red_malla,
}


def crear_red_inicial() -> nx.Graph:
    return red_oficina()


# ---------------------------------------------------------------------------
# Importar / exportar topología
# ---------------------------------------------------------------------------
def red_a_dict(g: nx.Graph) -> dict:
    return {
        "nodos": [{"nombre": n, "tipo": a.get("tipo", "Otro")} for n, a in g.nodes(data=True)],
        "enlaces": [{"origen": u, "destino": v, "latencia": a.get("weight", 1)} for u, v, a in g.edges(data=True)],
    }


def red_desde_dict(datos: dict) -> nx.Graph:
    if not isinstance(datos, dict) or "nodos" not in datos or "enlaces" not in datos:
        raise ValueError("El JSON debe contener las claves 'nodos' y 'enlaces'.")
    g = nx.Graph()
    for n in datos["nodos"]:
        nombre = str(n["nombre"]).strip()
        if not nombre:
            raise ValueError("Hay un dispositivo sin nombre.")
        tipo = n.get("tipo", "Otro")
        g.add_node(nombre, tipo=tipo if tipo in TIPOS else "Otro")
    for e in datos["enlaces"]:
        u, v = str(e["origen"]), str(e["destino"])
        if u not in g or v not in g:
            raise ValueError(f"El enlace {u} - {v} usa un dispositivo inexistente.")
        if u == v:
            raise ValueError("No se permiten enlaces de un dispositivo consigo mismo.")
        lat = float(e.get("latencia", 1))
        if lat <= 0:
            raise ValueError("Las latencias deben ser positivas.")
        g.add_edge(u, v, weight=int(lat) if lat == int(lat) else lat)
    return g


# ---------------------------------------------------------------------------
# Simulación y métricas
# ---------------------------------------------------------------------------
def simular(g: nx.Graph, nodos_fallidos, enlaces_fallidos) -> nx.Graph:
    s = g.copy()
    s.remove_nodes_from([n for n in nodos_fallidos if n in s])
    for u, v in enlaces_fallidos:
        if s.has_edge(u, v):
            s.remove_edge(u, v)
    return s


def pares_conectados(g: nx.Graph) -> int:
    return sum(comb(len(c), 2) for c in nx.connected_components(g))


def pares_incomunicados(original: nx.Graph, simulada: nx.Graph) -> list[tuple[str, str]]:
    comp_orig = {n: i for i, c in enumerate(nx.connected_components(original)) for n in c}
    comp_sim = {n: i for i, c in enumerate(nx.connected_components(simulada)) for n in c}
    nodos = list(original.nodes())
    out = []
    for i, a in enumerate(nodos):
        for b in nodos[i + 1:]:
            antes = comp_orig[a] == comp_orig[b]
            despues = a in comp_sim and b in comp_sim and comp_sim[a] == comp_sim[b]
            if antes and not despues:
                out.append((a, b))
    return out


def nivel(score: float) -> str:
    return "Baja" if score < UMBRAL_MEDIA else ("Media" if score < UMBRAL_ALTA else "Alta")


def criticidad_dispositivos(g: nx.Graph) -> pd.DataFrame:
    cols = ["Dispositivo", "Tipo", "Conexiones", "Centralidad de grado",
            "Centralidad de intermediación", "Importancia del tipo", "Puntuación",
            "Criticidad", "Interpretación"]
    if g.number_of_nodes() == 0:
        return pd.DataFrame(columns=cols)
    grado = nx.degree_centrality(g) if g.number_of_nodes() > 1 else {n: 0.0 for n in g}
    inter = nx.betweenness_centrality(g, weight="weight", normalized=True)
    textos = {
        "Alta": "Conecta o articula una parte importante de la red",
        "Media": "Tiene relevancia moderada para la estructura",
        "Baja": "Tiene menor influencia estructural según la regla",
    }
    filas = []
    for n, a in g.nodes(data=True):
        imp = PESOS_TIPO.get(a.get("tipo", "Otro"), 0.40)
        score = 0.35 * grado[n] + 0.35 * inter[n] + 0.30 * imp
        nv = nivel(score)
        filas.append({
            "Dispositivo": n, "Tipo": a.get("tipo", "Otro"), "Conexiones": int(g.degree[n]),
            "Centralidad de grado": round(grado[n], 3),
            "Centralidad de intermediación": round(inter[n], 3),
            "Importancia del tipo": round(imp, 2), "Puntuación": round(score, 3),
            "Criticidad": nv, "Interpretación": textos[nv],
        })
    return (pd.DataFrame(filas).sort_values(["Puntuación", "Dispositivo"], ascending=[False, True])
            .reset_index(drop=True))


def impacto_dispositivos(g: nx.Graph) -> pd.DataFrame:
    """Qué pasa si cada dispositivo cae por separado (sobre la red base)."""
    total = pares_conectados(g)
    arts = set(nx.articulation_points(g))
    filas = []
    for n in g.nodes:
        h = g.copy()
        h.remove_node(n)
        tam_comp = len(nx.node_connected_component(g, n))
        perdidos = total - pares_conectados(h) - (tam_comp - 1)
        extra = (nx.number_connected_components(h) if h.number_of_nodes() else 0) - nx.number_connected_components(g)
        if tam_comp == 1:  # nodo aislado: al quitarlo desaparece un componente
            extra = 0
        filas.append({
            "Dispositivo": n, "Tipo": g.nodes[n].get("tipo", "Otro"),
            "Punto único de fallo": "Sí" if n in arts else "No",
            "Pares que pierden comunicación": int(perdidos),
            "Componentes adicionales": int(max(extra, 0)),
        })
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    return df.sort_values(["Pares que pierden comunicación", "Dispositivo"],
                          ascending=[False, True]).reset_index(drop=True)


def impacto_enlaces(g: nx.Graph) -> pd.DataFrame:
    total = pares_conectados(g)
    puentes = {frozenset(e) for e in nx.bridges(g)}
    filas = []
    for u, v, a in g.edges(data=True):
        h = g.copy()
        h.remove_edge(u, v)
        filas.append({
            "Enlace": f"{u} ↔ {v}", "Latencia (ms)": a.get("weight", 1),
            "Enlace crítico (puente)": "Sí" if frozenset((u, v)) in puentes else "No",
            "Pares que pierden comunicación": int(total - pares_conectados(h)),
        })
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    return df.sort_values(["Pares que pierden comunicación", "Enlace"],
                          ascending=[False, True]).reset_index(drop=True)


def indice_resiliencia(g: nx.Graph) -> float | None:
    """% de dispositivos cuya caída individual no separa a otros dispositivos."""
    if g.number_of_nodes() < 3:
        return None
    arts = set(nx.articulation_points(g))
    return 100.0 * (1 - len(arts) / g.number_of_nodes())


def matriz_latencias(g: nx.Graph) -> pd.DataFrame:
    nodos = sorted(g.nodes())
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight="weight"))
    datos = [[dist.get(a, {}).get(b, float("nan")) for b in nodos] for a in nodos]
    return pd.DataFrame(datos, index=nodos, columns=nodos)


def rutas_alternativas(g: nx.Graph, origen: str, destino: str, k: int = 3):
    """Hasta k rutas simples ordenadas por latencia total."""
    if origen == destino or origen not in g or destino not in g or not nx.has_path(g, origen, destino):
        return []
    rutas = list(islice(nx.shortest_simple_paths(g, origen, destino, weight="weight"), k))
    return [(r, sum(g[a][b].get("weight", 1) for a, b in zip(r[:-1], r[1:]))) for r in rutas]
