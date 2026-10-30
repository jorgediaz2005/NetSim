"""Informe HTML del escenario de NetSim."""
from __future__ import annotations

from datetime import datetime

import networkx as nx
import pandas as pd

import netsim_core as core
from netsim_estilos import esc

_PALETAS = {
    True: dict(bg="#FFFFFF", fg="#0F172A", h2="#1D5FD1", ln="#CBD5E1", th="#E8EEF8", td="#E2E8F0", kb="#F6F9FF",
               ok="#15803D", bad="#B91C1C", warn="#B45309"),
    False: dict(bg="#0B0F1A", fg="#E6EDF3", h2="#7DB8FF", ln="#26324a", th="#17213a", td="#1f2a44", kb="#121a2e",
                ok="#2ECC71", bad="#FF6B6D", warn="#F5A623"),
}

_PLANTILLA_CSS = (
    "body{font-family:Segoe UI,Arial,sans-serif;background:%(bg)s;color:%(fg)s;max-width:1000px;margin:0 auto;"
    "padding:2rem 1.2rem}h1{margin:.2rem 0}h2{margin-top:2rem;border-bottom:1px solid %(ln)s;padding-bottom:.3rem;"
    "color:%(h2)s}.sub{opacity:.75}.t{border-collapse:collapse;width:100%%;font-size:.88rem;margin:.6rem 0}"
    ".t th{background:%(th)s;text-align:left;padding:.45rem .6rem}.t td{padding:.4rem .6rem;"
    "border-top:1px solid %(td)s}.kpis{display:flex;flex-wrap:wrap;gap:.7rem}.k{flex:1;min-width:170px;"
    "background:%(kb)s;border:1px solid %(ln)s;border-radius:12px;padding:.8rem 1rem}.k b{display:block;"
    "font-size:1.5rem}.k span{font-size:.75rem;opacity:.75;text-transform:uppercase}.ok{color:%(ok)s}"
    ".bad{color:%(bad)s}.warn{color:%(warn)s}.nota{opacity:.75;font-size:.85rem}@media print{body{background:#fff;"
    "color:#000}.k,.t th{background:#eee}h2{color:#036}}"
)


def _css_informe(modo_dia: bool) -> str:
    return _PLANTILLA_CSS % _PALETAS[modo_dia]


def generar_informe(g, g_sim, fallos, enlaces_fallidos, pares_perdidos, df_crit, sugerencias, modo_dia):
    """Informe HTML autocontenido del escenario (imprimible a PDF con Ctrl + P).

    `sugerencias` es la lista de `core.sugerir_enlaces` ya calculada (la interfaz la cachea).
    """
    n_activos = g_sim.number_of_nodes()
    n_enlaces = g_sim.number_of_edges()
    comp_act = nx.number_connected_components(g_sim) if n_activos else 0
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    base = core.metricas_topologia(g)

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
    res_nodos = core.impacto_dispositivos(g) if g.number_of_nodes() > 1 else pd.DataFrame()
    res_enl = core.impacto_enlaces(g) if g.number_of_edges() else pd.DataFrame()
    if sugerencias:
        lista_sug = "<ul>" + "".join(
            f"<li><b>{esc(x['origen'])} ↔ {esc(x['destino'])}</b>: reduce el riesgo en {x['reduccion']} elemento(s); "
            f"resiliencia resultante {x['indice_despues']:.0f} %.</li>" for x in sugerencias) + "</ul>"
    else:
        lista_sug = '<p class="nota">No hay mejoras estructurales que sugerir.</p>'
    crit_vista = df_crit.drop(columns=["Interpretación"], errors="ignore")
    ind = base["Índice de resiliencia (%)"]
    return (
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Informe NetSim</title>'
        f'<style>{_css_informe(modo_dia)}</style></head><body>'
        f'<h1>Informe de simulación · NetSim</h1><p class="sub">Generado el {ahora}</p>'
        f'<h2>1. Topología base</h2><div class="kpis">'
        + caja(base["Dispositivos"], "Dispositivos") + caja(base["Enlaces"], "Enlaces")
        + caja(base["Puntos únicos de fallo"], "Puntos únicos de fallo", "bad" if base["Puntos únicos de fallo"] else "ok")
        + caja(base["Enlaces puente"], "Enlaces puente", "bad" if base["Enlaces puente"] else "ok")
        + caja(f"{ind:.0f} %" if ind is not None else "—", "Índice de resiliencia")
        + f'</div><h2>2. Escenario simulado</h2>{escenario}<div class="kpis">'
        + caja(f"{n_activos}/{g.number_of_nodes()}", "Dispositivos activos")
        + caja(f"{n_enlaces}/{g.number_of_edges()}", "Enlaces activos")
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
