"""Lógica de NetSim: topologías, criticidad, resiliencia y utilidades.

Separada de la interfaz (app.py) para que sea fácil de probar y de explicar
en la memoria del proyecto.
"""
from __future__ import annotations

from itertools import combinations, islice
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

# Fórmula de criticidad: PESO_GRADO * grado + PESO_INTERMEDIACION * intermediación + PESO_TIPO * tipo
PESO_GRADO = 0.35
PESO_INTERMEDIACION = 0.35
PESO_TIPO = 0.30

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
        ("Núcleo B", "Acceso 1", 3), ("Núcleo A", "Acceso 3", 3),
        ("Núcleo B", "Servidor web", 3), ("Núcleo A", "Servidor BD", 3),
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
# Simulación de fallos
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
    """Pares de dispositivos ACTIVOS que estaban comunicados en la red base y ya no.

    Los dispositivos caídos se excluyen: un equipo apagado no se comunica con nadie
    y eso ya se sabe, así que contarlo solo infla el número y contradice el estado
    de la red activa. Solo cuentan los pares donde ambos extremos siguen encendidos
    pero ya no tienen camino entre sí (por la caída de otros equipos o de enlaces).
    """
    comp_orig = {n: i for i, c in enumerate(nx.connected_components(original)) for n in c}
    comp_sim = {n: i for i, c in enumerate(nx.connected_components(simulada)) for n in c}
    activos = [n for n in original.nodes() if n in simulada]
    out = []
    for i, a in enumerate(activos):
        for b in activos[i + 1:]:
            if comp_orig[a] == comp_orig[b] and comp_sim[a] != comp_sim[b]:
                out.append((a, b))
    return out


# ---------------------------------------------------------------------------
# Criticidad de dispositivos
# ---------------------------------------------------------------------------
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
        score = PESO_GRADO * grado[n] + PESO_INTERMEDIACION * inter[n] + PESO_TIPO * imp
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


# ---------------------------------------------------------------------------
# Resiliencia: puntos únicos de fallo, puentes e impacto de cada caída
# ---------------------------------------------------------------------------
def _n_spof(g: nx.Graph) -> int:
    return sum(1 for _ in nx.articulation_points(g))


def _n_puentes(g: nx.Graph) -> int:
    return sum(1 for _ in nx.bridges(g))


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


# ---------------------------------------------------------------------------
# Latencias y rutas
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Mejoras sugeridas
# ---------------------------------------------------------------------------
def _riesgo(g: nx.Graph) -> int:
    """Puntos únicos de fallo + enlaces puente (menos es mejor)."""
    return _n_spof(g) + _n_puentes(g)


def sugerir_enlaces(g: nx.Graph, k: int = 3, latencia: int = 5) -> list[dict]:
    """Enlaces nuevos que más reducen los puntos únicos de fallo y los puentes.

    Prueba cada pareja de dispositivos aún sin enlace y mide cuánto baja el riesgo.
    En caso de empate prefiere enlaces entre equipos de infraestructura (se evita
    unir dos PC entre sí, poco realista). Es una heurística, no un diseño de red.
    """
    if g.number_of_nodes() < 3 or not nx.is_connected(g):
        return []
    base = _riesgo(g)
    if base == 0:
        return []
    candidatos = []
    for u, v in combinations(sorted(g.nodes), 2):
        if g.has_edge(u, v):
            continue
        if g.nodes[u].get("tipo") == "PC" and g.nodes[v].get("tipo") == "PC":
            continue  # dos equipos finales no suelen enlazarse entre sí
        h = g.copy()
        h.add_edge(u, v, weight=latencia)
        r = _riesgo(h)
        if r < base:
            extremos_pc = sum(g.nodes[x].get("tipo") == "PC" for x in (u, v))
            candidatos.append({
                "origen": u, "destino": v, "reduccion": base - r,
                "spof_despues": _n_spof(h),
                "puentes_despues": _n_puentes(h),
                "indice_despues": indice_resiliencia(h), "latencia": latencia,
                "_pc": extremos_pc,
            })
    candidatos.sort(key=lambda c: (-c["reduccion"], c["spof_despues"], c["_pc"], c["origen"], c["destino"]))
    for c in candidatos:
        c.pop("_pc")
    return candidatos[:k]


# ---------------------------------------------------------------------------
# Métricas de topología y comparación de plantillas
# ---------------------------------------------------------------------------
def metricas_topologia(g: nx.Graph) -> dict:
    n, m = g.number_of_nodes(), g.number_of_edges()
    conectada = n > 0 and nx.is_connected(g)
    indice = indice_resiliencia(g)
    return {
        "Dispositivos": n, "Enlaces": m,
        "Puntos únicos de fallo": _n_spof(g) if n else 0,
        "Enlaces puente": _n_puentes(g) if n else 0,
        "Índice de resiliencia (%)": round(indice, 1) if indice is not None else None,
        "Latencia media entre equipos (ms)": (round(nx.average_shortest_path_length(g, weight="weight"), 2)
                                              if conectada and n > 1 else None),
    }


def comparar_plantillas() -> pd.DataFrame:
    filas = [{"Topología": nombre, **metricas_topologia(f())} for nombre, f in PLANTILLAS.items()]
    return pd.DataFrame(filas)
