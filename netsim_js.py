"""Scripts de navegador de NetSim (JavaScript inyectado en la página).

- JS_ANIM: animaciones de expanders y listas desplegables, y conmutación de la flecha de los
  selectores (en Streamlit actual la flecha solo abre la lista; aquí también la cierra).
  El script localiza el documento que contiene los widgets porque al desplegar la app va dentro
  de un iframe y window.parent apunta a la carcasa de Streamlit Cloud.

El tema día/noche se resuelve con CSS (ver netsim_estilos), salvo las tablas: Glide las pinta en un
lienzo al que no llegan las variables CSS y cuyo tema decide el navegador, así que aquí se mide un
píxel real del lienzo y se marca <html> para que el CSS lo invierte cuando no concuerda.
"""
from __future__ import annotations

JS_ANIM = """<script>
(function () {
  var P, D;
  // El documento útil NO es siempre window.parent: al desplegar, Streamlit envuelve la app en un
  // iframe y window.parent es la carcasa, donde no hay ningún widget. Se toma el primer documento
  // accesible que sí los tenga, empezando por el propio (el caso de st.html).
  function tieneWidgets(d) {
    try {
      return !!(d && d.querySelector &&
        (d.querySelector('[data-testid="stApp"]') || d.querySelector('.react-aria-ComboBox')));
    } catch (e) { return false; }
  }
  var v = window;
  for (var nivel = 0; nivel < 4 && v; nivel++) {
    if (tieneWidgets(v.document)) { D = v.document; P = v; break; }
    if (v.parent === v) break;
    try { v = v.parent; } catch (e) { break; }
  }
  if (!D) return;
  try { if (P.__nsanim) P.__nsanim.off(); } catch (e) {}
  D.documentElement.setAttribute('data-ns-js', '1');
  try { console.info('[NetSim] animaciones activas (v9)'); } catch (e) {}
  var EASE = 'cubic-bezier(.22,.61,.36,1)';
  var reducir = !!(P.matchMedia && P.matchMedia('(prefers-reduced-motion: reduce)').matches);

  function contenido(det) {
    for (var i = 0; i < det.children.length; i++) if (det.children[i].tagName !== 'SUMMARY') return det.children[i];
    return null;
  }
  function esExpander(det) { return det && det.tagName === 'DETAILS' && det.closest('[data-testid="stExpander"]'); }

  // Al CERRAR: el contenido desaparece al instante, así que se deja una copia que se pliega en su lugar
  function alPulsar(ev) {
    var sum = ev.target.closest && ev.target.closest('[data-testid="stExpander"] summary');
    if (!sum) return;
    var det = sum.parentElement;
    if (!esExpander(det) || !det.open) return;
    var c = contenido(det); if (!c) return;
    var r = c.getBoundingClientRect(); if (r.height < 2) return;
    var ghost = D.createElement('div');
    ghost.setAttribute('aria-hidden', 'true');
    ghost.setAttribute('data-nsg', String(Date.now()));
    ghost.setAttribute('data-nsk', 'exp');
    ghost.style.cssText = 'overflow:hidden;pointer-events:none;height:' + r.height + 'px;';
    var copia = c.cloneNode(true);
    copia.style.cssText += ';width:' + r.width + 'px;margin:0;animation:none;';
    copia.setAttribute('inert', '');
    copia.querySelectorAll('[id]').forEach(function (n) { n.removeAttribute('id'); });
    ghost.appendChild(copia);
    det.parentNode.insertBefore(ghost, det.nextSibling);
    var a = ghost.animate([{ height: r.height + 'px', opacity: 1 }, { height: '0px', opacity: 0 }],
                          { duration: reducir ? 160 : 280, easing: EASE, fill: 'forwards' });
    function quitar() { if (ghost.parentNode) ghost.parentNode.removeChild(ghost); }
    a.onfinish = quitar; a.oncancel = quitar;
    P.setTimeout(quitar, 900);   // red de seguridad sin necesidad de barrer la página cada segundo
    setTimeout(function () { if (det.open) a.cancel(); }, 90);   // si el cierre no llegó a ocurrir, se descarta la copia
  }
  D.addEventListener('click', alPulsar, true);

  // Al ABRIR: la altura crece desde 0 (el fundido y el descenso los pone el CSS)
  var obs = new P.MutationObserver(function (ms) {
    ms.forEach(function (m) {
      var det = m.target;
      if (!esExpander(det) || !det.hasAttribute('open') || reducir) return;
      P.requestAnimationFrame(function () {
        var c = contenido(det); if (!c) return;
        var h = c.getBoundingClientRect().height; if (h < 2) return;
        c.style.overflow = 'hidden';
        var a = c.animate([{ height: '0px' }, { height: h + 'px' }], { duration: 300, easing: EASE });
        function fin() { c.style.overflow = ''; }
        a.onfinish = fin; a.oncancel = fin;
      });
    });
  });
  obs.observe(D.body, { subtree: true, attributes: true, attributeFilter: ['open'] });
  // ---- Listas desplegables (selectores): animación al abrir y al cerrar ----
  var LB = '[role="listbox"]';
  var FILTRO = '.js-plotly-plot, [data-testid="stDataFrame"]';
  function lista(n) {                       // la lista contenida en n (o el propio n)
    if (!n || n.nodeType !== 1) return null;
    if (n.matches && n.matches(LB)) return n;
    return n.querySelector ? n.querySelector(LB) : null;
  }
  // Se anima el ancestro más externo de la lista que NO esté posicionado por el navegador
  // (el posicionado usa transform inline y animarlo movería la lista de sitio).
  function objetivo(lb, raiz) {
    var t = lb;
    if (lb === raiz) return t;
    for (var n = lb.parentElement; n && n !== D.body && raiz.contains(n); n = n.parentElement) {
      if (/transform|position|inset|top:|left:/.test(n.getAttribute('style') || '')) break;
      t = n;
    }
    return t;
  }
  // Solo es "capa de lista" si no contiene los propios widgets: si Streamlit redibuja un selector entero,
  // lo que se retira incluye el control y no debe tratarse como una lista que se cierra.
  var WIDGETS = '.react-aria-ComboBox, [data-testid="stSelectbox"], [data-testid="stMultiSelect"], [data-testid="stSidebar"], [data-testid="stMain"], [data-testid="stApp"], [data-testid="stExpander"]';
  function esCapa(n) { return !(n.matches && n.matches(WIDGETS)) && !n.querySelector(WIDGETS); }
  function seguro(f) { return function () { try { return f.apply(this, arguments); } catch (e) { try { console.warn('[NetSim] animación omitida', e); } catch (e2) {} } }; }
  function vivas() {                        // listas visibles que no son una copia en salida
    return Array.prototype.filter.call(D.querySelectorAll(LB), function (x) { return !x.closest('[data-nsg]'); });
  }
  function entrada(lb, raiz) {
    var t = objetivo(lb, raiz);
    t.style.transformOrigin = 'top center';
    t.animate(reducir ? [{ opacity: 0 }, { opacity: 1 }] : [
      { opacity: 0, transform: 'translateY(-8px) scale(.98)', clipPath: 'inset(0 0 100% 0)' },
      { opacity: 1, transform: 'none', clipPath: 'inset(-30px)' }
    ], { duration: reducir ? 120 : 200, easing: EASE });
  }
  // Streamlit elimina la lista al instante. El nodo original NO se vuelve a insertar (eso es de Streamlit):
  // se añade una copia inerte que el CSS desvanece y que se retira sola.
  function salida(lb, n, padre, siguiente) {
    if (!padre || !padre.isConnected) return;
    if (n.__nsAbierto && Date.now() - n.__nsAbierto < 300) return;
    var copia = n.cloneNode(true);
    copia.__nsFantasma = true;
    copia.setAttribute('data-nsg', String(Date.now()));
    copia.setAttribute('aria-hidden', 'true');
    copia.setAttribute('inert', '');
    copia.querySelectorAll('[id]').forEach(function (x) { x.removeAttribute('id'); });
    padre.insertBefore(copia, siguiente && siguiente.parentNode === padre ? siguiente : null);
    P.setTimeout(function () { if (copia.parentNode) copia.parentNode.removeChild(copia); }, 350);
  }
  var obs2 = new P.MutationObserver(seguro(function (ms) {
    var nuevas = [], quitadas = [];
    ms.forEach(function (m) {
      if (m.target.closest && m.target.closest(FILTRO)) return;
      m.addedNodes.forEach(function (n) {
        if (n.nodeType !== 1 || n.__nsFantasma) return;
        var lb = lista(n); if (lb && esCapa(n)) nuevas.push([lb, n]);
      });
      m.removedNodes.forEach(function (n) {
        if (n.nodeType !== 1 || n.__nsFantasma) return;
        var lb = lista(n); if (lb && esCapa(n)) quitadas.push([lb, n, m.target, m.nextSibling]);
      });
    });
    // Si en el mismo lote se quita y se añade una lista, es un redibujado (p. ej. al escribir para filtrar): no se anima
    if (nuevas.length && !quitadas.length) {
      P.requestAnimationFrame(function () { nuevas.forEach(function (x) { x[1].__nsAbierto = Date.now(); entrada(x[0], x[1]); }); });
    } else if (quitadas.length && !nuevas.length && !vivas().length) {
      quitadas.forEach(function (x) { salida(x[0], x[1], x[2], x[3]); });
    }
  }));
  obs2.observe(D.body, { childList: true, subtree: true });

  // ---- Selectores (react-aria): la flecha también CIERRA la lista abierta ----
  // Streamlit (react-aria) conmuta raro: el pointerdown en la flecha cierra la lista, pero
  // el click la vuelve a abrir, así que nunca parece cerrarse. Si la lista está abierta se
  // anula ese pointerdown y, al producirse el click, se envía un Escape al combobox, que es
  // el mismo mecanismo que cierra la lista al pulsar fuera.
  var flechaPulsada = false;
  function alBajarEnFlecha(ev) {
    flechaPulsada = false;
    var b = ev.target.closest && ev.target.closest('button[aria-haspopup="listbox"]');
    if (!b || b.getAttribute('aria-expanded') !== 'true') return;
    flechaPulsada = true;
    ev.preventDefault();
    ev.stopImmediatePropagation();
  }
  function alPulsarFlecha(ev) {
    if (!flechaPulsada) return;
    flechaPulsada = false;
    var b = ev.target.closest && ev.target.closest('button[aria-haspopup="listbox"]');
    var cb = b && b.closest('.react-aria-ComboBox');
    var input = cb && cb.querySelector('input[role="combobox"]');
    if (!input) return;
    ev.preventDefault();
    ev.stopImmediatePropagation();
    // Un Escape cierra tanto el multiselect como el selectbox (blur() solo funcionaba con el multiselect)
    ['keydown', 'keypress', 'keyup'].forEach(function (t) {
      input.dispatchEvent(new P.KeyboardEvent(t, { key: 'Escape', code: 'Escape', bubbles: true, cancelable: true }));
    });
  }
  D.addEventListener('pointerdown', alBajarEnFlecha, true);
  D.addEventListener('click', alPulsarFlecha, true);

  P.__nsanim = { off: function () { obs.disconnect(); obs2.disconnect(); D.removeEventListener('click', alPulsar, true); D.removeEventListener('pointerdown', alBajarEnFlecha, true); D.removeEventListener('click', alPulsarFlecha, true); } };
})();
</script>"""


def script_animaciones() -> str:
    """JavaScript de la página: el tema se resuelve ya con CSS, solo queda la animación."""
    return JS_ANIM

