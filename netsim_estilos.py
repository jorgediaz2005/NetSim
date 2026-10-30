"""Estilos de NetSim: temas día/noche y hojas de estilo CSS de la interfaz.

Aquí viven SOLO textos de estilo (sin lógica de la app). `css_completo()` los
ensambla según el modo activo; app.py únicamente tiene que inyectar el resultado.
"""
from __future__ import annotations

import html

# ---------------------------------------------------------------------------
# Temas (variables CSS que usan todas las hojas de estilo)
# ---------------------------------------------------------------------------
TEMAS = {
    "noche": dict(bg="#0B0F1A", text="#E6EDF3", soft="#94A3B8", line="rgba(255,255,255,.09)",
                  card="rgba(255,255,255,.04)", card2="rgba(255,255,255,.06)", card3="rgba(255,255,255,.02)",
                  side1="#121A2B", side2="#0B0F1A", input="#1A2236", route="#FFD166",
                  hero="linear-gradient(120deg,#101a33,#14213f 40%,#1a1740 70%,#101a33)",
                  shadow="rgba(0,0,0,.35)", chip="rgba(255,255,255,.07)", chipline="rgba(255,255,255,.12)",
                  lg="#CBD5E1", okt="#2ECC71", warnt="#F5A623", badt="#FF8A8C", lineb="rgba(255,255,255,.14)", pri1="#4DA3FF", pri2="#7C5CFF",
                  glow1=".14", glow2=".12", glowh1=".28", glowh2=".25",
                  mut=".7", accentt="#4DA3FF", accent2t="#9B8CFF", codec="#FFB4B6",
                  elev="none", arte="rgba(148,163,184,.55)", ring="transparent", edge="rgba(77,163,255,.40)",
                  tab1="rgba(77,163,255,.38)", tab2="rgba(124,92,255,.38)", tabb="rgba(77,163,255,.70)",
                  hop1="rgba(255,209,102,.20)", hop2="rgba(255,209,102,.06)", hopb="rgba(255,209,102,.55)",
                  hover="rgba(77,163,255,.14)", optsel="rgba(255,255,255,.08)"),
    "dia": dict(bg="#F3F6FB", text="#0F172A", soft="#475569", line="rgba(15,23,42,.13)",
                card="rgba(255,255,255,.80)", card2="#FFFFFF", card3="#F6F9FF",
                side1="#FFFFFF", side2="#E9F0FA", input="#FFFFFF", route="#8A5A00",
                hero="linear-gradient(120deg,#E4EEFF,#ECE7FF 55%,#E1ECFF)",
                shadow="rgba(15,23,42,.14)", chip="rgba(15,23,42,.05)", chipline="rgba(15,23,42,.15)",
                lg="#334155", okt="#166534", warnt="#92400E", badt="#B91C1C", lineb="rgba(15,23,42,.30)", pri1="#2563EB", pri2="#6D4AE0",
                glow1=".10", glow2=".08", glowh1=".20", glowh2=".16",
                mut=".92", accentt="#1D5FD1", accent2t="#5B3FD6", codec="#B91C1C",
                elev="0 1px 2px rgba(15,23,42,.06), 0 4px 14px rgba(15,23,42,.07)",
                arte="rgba(71,85,105,.65)", ring="#FFFFFF", edge="rgba(29,95,209,.35)",
                tab1="rgba(29,95,209,.15)", tab2="rgba(91,63,214,.15)", tabb="#1D5FD1",
                hop1="#FFF1CC", hop2="#FFF8E6", hopb="#D99A1E",
                hover="rgba(29,95,209,.10)", optsel="rgba(29,95,209,.10)"),
}

# ---------------------------------------------------------------------------
# Hojas de estilo
# ---------------------------------------------------------------------------
CSS_BASE = """
.stApp {
    background:
        radial-gradient(1100px 560px at 8% -8%, rgba(77,163,255,var(--glow1)), transparent 60%),
        radial-gradient(900px 520px at 100% 0%, rgba(124,92,255,var(--glow2)), transparent 55%),
        var(--bg) !important;
    color: var(--text);
}
/* Streamlit deja el <body> con el color del tema base (siempre oscuro): se alinea con el modo activo */
html, body {background: var(--bg) !important; color: var(--text) !important;}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebarContent"] {background: transparent !important;}
.block-container {padding-top: 1.1rem; padding-bottom: 2.5rem; max-width: 1500px;}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
header[data-testid="stHeader"] *, [data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] * {color: var(--text) !important;}
hr {border-color: var(--line) !important;}

/* ---------- Texto y widgets nativos (se adaptan al modo día/noche) ---------- */
[data-testid="stMarkdownContainer"] :is(p, li, h1, h2, h3, h4, h5, strong, em, td, th) {color: var(--text);}
[data-testid="stWidgetLabel"] *, label, summary, summary * {color: var(--text);}
[data-testid="stCaptionContainer"] * {color: var(--soft);}
div[data-testid="stAlert"] * {color: var(--text);}
/* Campos (react-aria): la caja del selector es div[role="group"] dentro de .react-aria-ComboBox */
.react-aria-ComboBox > div[role="group"], [data-testid="stTextInputRootElement"],
[data-testid="stNumberInputContainer"], input, textarea {
    background-color: var(--input) !important; border-color: var(--lineb) !important;}
.react-aria-ComboBox :is(input, button, span, div), input, textarea {color: var(--text) !important;}
input, textarea {-webkit-text-fill-color: var(--text) !important;}
input::placeholder, textarea::placeholder {color: var(--soft) !important; -webkit-text-fill-color: var(--soft) !important;}
.react-aria-ComboBox button[aria-haspopup="listbox"] svg, [data-testid="stNumberInput"] svg,
[data-testid="stTooltipIcon"] svg, [data-testid="stFileUploaderDropzone"] svg, summary svg {
    fill: var(--soft) !important; color: var(--soft) !important;}
summary:hover {background: var(--optsel);}
[data-testid="stForm"] {border: 1px solid var(--lineb) !important; background: var(--card3) !important; border-radius: 14px;}
/* Etiquetas del multiselect (valores ya elegidos) */
[data-testid="stMultiSelectTagsContainer"] span[aria-label="Selected values"] > span {
    background-color: var(--accentt) !important; color: #FFFFFF !important;}
[data-testid="stMultiSelectTagsContainer"] span[aria-label="Selected values"] > span :is(span, button, svg) {
    background-color: transparent !important; color: #FFFFFF !important; fill: #FFFFFF !important;}
/* Capa de la lista desplegable (selectbox y multiselect) */
[data-testid="stMultiSelectDropdown"], [data-testid="stSelectboxVirtualDropdown"] {
    background-color: var(--input) !important; background-image: none !important; color: var(--text) !important;
    border: 1px solid var(--lineb) !important; border-radius: 10px !important;
    box-shadow: 0 10px 30px var(--shadow) !important;}
[data-testid="stMultiSelectDropdown"] button {
    background-color: var(--card3) !important; color: var(--text) !important; border: 1px solid var(--lineb) !important;}
[data-testid="stMultiSelectDropdown"] svg, [data-testid="stSelectboxVirtualDropdown"] svg {
    fill: var(--soft) !important; color: var(--soft) !important;}
[data-testid="stMultiSelectDropdown"] hr, [data-testid="stSelectboxVirtualDropdown"] hr {
    border-color: var(--line) !important; background-color: var(--line) !important;}
[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFile"] * {background: transparent !important; color: var(--text) !important;}
[data-testid="stNumberInput"] button {background: var(--input) !important; color: var(--text) !important; border-color: var(--lineb) !important;}
[data-testid="stFileUploaderDropzone"] {background: var(--input) !important; border: 1px dashed var(--lineb) !important;}
[data-testid="stFileUploaderDropzone"] * {color: var(--text);}
[data-testid="stFileUploaderDropzone"] button {background: var(--card2) !important; border: 1px solid var(--lineb) !important; color: var(--text) !important;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color: var(--line) !important;}

/* ---------- Barra lateral ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--side1) 0%, var(--side2) 100%);
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
.brand-sub {font-size:.75rem; opacity:var(--mut); letter-spacing:.6px; text-transform:uppercase;}
.side-title {
    font-size:.72rem; font-weight:700; letter-spacing:1.2px; text-transform:uppercase;
    color: var(--accentt); margin: .9rem 0 .35rem 0;
}

/* ---------- Cabecera ---------- */
.hero {
    position: relative; overflow: hidden; display:flex; justify-content:space-between; align-items:center;
    gap: 1rem; padding: 1.5rem 1.8rem; border-radius: 22px; margin-bottom: 1.1rem;
    background: var(--hero);
    background-size: 220% 220%; animation: shift 16s ease infinite;
    border: 1px solid var(--chipline);
    box-shadow: 0 10px 40px var(--shadow), inset 0 1px 0 rgba(255,255,255,.06);
}
.hero::before {
    content:""; position:absolute; inset:0; pointer-events:none;
    background:
        radial-gradient(500px 220px at 12% 0%, rgba(77,163,255,var(--glowh1)), transparent 60%),
        radial-gradient(420px 220px at 95% 100%, rgba(124,92,255,var(--glowh2)), transparent 60%);
}
.hero-text {position: relative; z-index: 1;}
.hero-eyebrow {font-size:.72rem; letter-spacing:2px; opacity:var(--mut); font-weight:600;}
.hero h1 {margin:.15rem 0 .1rem 0; font-size: 2.4rem; font-weight: 800; letter-spacing:.3px; padding:0;}
.hero h1 span {
    background: linear-gradient(90deg, var(--accentt), var(--accent2t));
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p {margin:.2rem 0 .8rem 0; opacity:var(--mut);}
.hero-chips {display:flex; flex-wrap:wrap; gap:.5rem; align-items:center;}
.chip {
    padding:.28rem .75rem; border-radius:999px; font-size:.8rem; font-weight:600;
    background: var(--chip); border:1px solid var(--chipline);
}
.status {
    display:inline-flex; align-items:center; gap:.45rem; padding:.28rem .8rem; border-radius:999px;
    font-size:.8rem; font-weight:700; letter-spacing:.5px;
}
.status .dot {width:9px; height:9px; border-radius:50%; display:inline-block; animation: pulse-dot 1.8s ease-in-out infinite;}
.status-ok   {background:rgba(46,204,113,.15); color:var(--okt); border:1px solid rgba(46,204,113,.45);}
.status-ok .dot {background:#2ECC71; box-shadow:0 0 0 0 rgba(46,204,113,.7);}
.status-warn {background:rgba(245,166,35,.15); color:var(--warnt); border:1px solid rgba(245,166,35,.45);}
.status-warn .dot {background:#F5A623; box-shadow:0 0 0 0 rgba(245,166,35,.7);}
.status-bad  {background:rgba(255,77,79,.15); color:var(--badt); border:1px solid rgba(255,77,79,.5);}
.status-bad .dot {background:#FF4D4F; box-shadow:0 0 0 0 rgba(255,77,79,.7);}
.hero-art {position: relative; z-index:1; width: 260px; height: 140px; flex-shrink:0;}
.hero-art g {stroke: var(--arte);}
.hero-art circle {stroke: var(--ring); stroke-width: 2;}
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

/* ---------- Contenido didáctico ---------- */
.gl {
    padding:.75rem 1rem; border-radius:14px; margin-bottom:.6rem;
    background: var(--card2); border:1px solid var(--line); box-shadow: var(--elev);
}
.gl p {margin:.2rem 0 .3rem 0;}
.gl small {opacity:var(--mut);}
.nv {
    display:inline-block; padding:.08rem .6rem; border-radius:999px; font-size:.72rem; font-weight:700;
    margin-left:.4rem; border:1px solid var(--chipline);
}
.nv-ok {color:var(--okt); border-color:rgba(46,204,113,.5);}
.nv-warn {color:var(--warnt); border-color:rgba(245,166,35,.5);}
.nv-bad {color:var(--badt); border-color:rgba(255,77,79,.5);}

/* ---------- Tarjetas KPI ---------- */
.kpi {
    display:flex; align-items:center; padding: 1rem 1.1rem; border-radius: 18px;
    background: linear-gradient(145deg, var(--card2), var(--card3));
    border: 1px solid var(--line); position: relative; overflow:hidden; box-shadow: var(--elev);
    transition: transform .2s ease;
    animation: rise .5s ease both;
}
.kpi::before {content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background: var(--k);}
/* Los fundidos de color van SOLO en :hover: al cambiar de modo ningún elemento está en hover, así que
   el tema se aplica de golpe. Si estuvieran declarados en la regla base, el cambio de modo los cruzaría. */
.kpi:hover {transform: translateY(-3px); border-color: var(--k); box-shadow: 0 10px 28px var(--shadow);
    transition: border-color .2s ease, box-shadow .2s ease;}
.kpi-info {--k:#4DA3FF;} .kpi-ok {--k:#2ECC71;} .kpi-warn {--k:#F5A623;} .kpi-bad {--k:#FF4D4F;}
.kpi-label {font-size:.76rem; opacity:var(--mut); text-transform:uppercase; letter-spacing:.8px; font-weight:600;}
.kpi-value {font-size:1.7rem; font-weight:800; line-height:1.15;}
.kpi-sub {font-size:.78rem; opacity:var(--mut);}

/* ---------- Métricas nativas de Streamlit ---------- */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, var(--card2), var(--card3));
    border: 1px solid var(--line); padding: 14px 16px; border-radius: 16px; box-shadow: var(--elev);
    transition: transform .2s ease;
}
div[data-testid="stMetric"]:hover {transform: translateY(-2px); border-color: rgba(77,163,255,.5);
    transition: border-color .2s ease;}
div[data-testid="stMetricLabel"] p {opacity:var(--mut); font-size:.85rem;}

/* ---------- Pestañas (react-aria: div[role="tab"], ya no son button[data-baseweb="tab"]) ---------- */
div[role="tablist"] {gap: .35rem; flex-wrap: wrap;}
div[data-testid="stTab"] {
    border-radius: 999px; padding: .45rem 1.05rem; background: var(--card); cursor: pointer;
    border: 1px solid var(--line); height: auto; transition: transform .15s ease;
}
div[data-testid="stTab"] p {color: var(--text);}
div[data-testid="stTab"]:hover {border-color: var(--tabb); background: var(--hover);
    transition: background-color .2s ease, border-color .2s ease, box-shadow .2s ease;}
div[data-testid="stTab"]:active {transform: scale(.96);}
div[data-testid="stTab"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--tab1), var(--tab2));
    border-color: var(--tabb); box-shadow: 0 4px 16px rgba(77,163,255,.22);
}
/* El subrayado de 2px que pinta react-aria sobra con la píldora seleccionada */
div[data-testid="stTab"] .react-aria-SelectionIndicator {display: none;}

/* ---------- Botones y expanders ---------- */
/* Botones secundarios: normales, de formulario, de descarga y del cargador de archivos */
button[kind="secondary"], button[kind="secondaryFormSubmit"], button[data-testid^="stBaseButton-secondary"],
.stButton > button:not([kind="primary"]), .stDownloadButton > button, .stFormSubmitButton > button:not([kind="primary"]) {
    border-radius: 12px; border: 1px solid var(--lineb) !important; transition: transform .18s ease;
    background: var(--card2) !important; color: var(--text) !important; box-shadow: var(--elev);
}
button[kind="secondary"] :is(p, span, div), button[kind="secondaryFormSubmit"] :is(p, span, div),
button[data-testid^="stBaseButton-secondary"] :is(p, span, div),
.stButton > button:not([kind="primary"]) :is(p, span, div), .stDownloadButton > button :is(p, span, div),
.stFormSubmitButton > button:not([kind="primary"]) :is(p, span, div) {color: var(--text) !important;}
button[kind="secondary"]:is(:hover, :focus-visible, :active), button[kind="secondaryFormSubmit"]:is(:hover, :focus-visible, :active),
button[data-testid^="stBaseButton-secondary"]:is(:hover, :focus-visible, :active),
.stButton > button:not([kind="primary"]):is(:hover, :focus-visible, :active),
.stDownloadButton > button:is(:hover, :focus-visible, :active),
.stFormSubmitButton > button:not([kind="primary"]):is(:hover, :focus-visible, :active) {
    transform: translateY(-1px); border-color: var(--accent) !important; background: var(--hover) !important;
    color: var(--text) !important; box-shadow: 0 6px 18px rgba(77,163,255,.18);
    transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease;
}
button[kind="secondary"]:disabled, button[kind="secondaryFormSubmit"]:disabled,
button[data-testid^="stBaseButton-secondary"]:disabled {opacity: .55; transform: none;}
/* Botones principales (primary) */
button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid^="stBaseButton-primary"],
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--pri1), var(--pri2)) !important; border: none !important;
    font-weight: 700; color: #FFFFFF !important;
}
button[kind="primary"] :is(p, span, div), button[kind="primaryFormSubmit"] :is(p, span, div),
button[data-testid^="stBaseButton-primary"] :is(p, span, div) {color: #FFFFFF !important;}
button[kind="primary"]:is(:hover, :focus-visible, :active), button[kind="primaryFormSubmit"]:is(:hover, :focus-visible, :active),
button[data-testid^="stBaseButton-primary"]:is(:hover, :focus-visible, :active) {
    filter: brightness(1.08); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(77,163,255,.30);
}
div[data-testid="stExpander"] {
    border-radius: 14px; border: 1px solid var(--line); background: var(--card); overflow:hidden;
    box-shadow: var(--elev);
}
div[data-testid="stDataFrame"] {border-radius: 14px; overflow:hidden; border:1px solid var(--line);}

/* ---------- Leyenda, ruta y títulos ---------- */
.legend {display:flex; flex-wrap:wrap; gap:.45rem .5rem; margin:.4rem 0 1rem 0;}
.lg {
    display:inline-flex; align-items:center; gap:.4rem; font-size:.76rem; padding:.22rem .65rem;
    border-radius: 999px; background: var(--card); border:1px solid var(--line); color:var(--lg);
}
.lg i {width:10px; height:10px; border-radius:50%; display:inline-block;}
.lg b {width:18px; height:4px; border-radius:3px; display:inline-block;}
.route {display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; margin:.4rem 0 1rem 0;}
.hop {
    padding:.45rem .85rem; border-radius:12px; font-weight:700;
    background: linear-gradient(135deg, var(--hop1), var(--hop2));
    border:1px solid var(--hopb);
}
.hop-link {font-size:.8rem; opacity:.95; color:var(--route); font-weight:600;}
.sec {
    font-size:1.05rem; font-weight:700; margin: 1.2rem 0 .5rem 0; display:flex; align-items:center; gap:.5rem;
}
.sec::after {content:""; flex:1; height:1px; background: linear-gradient(90deg, var(--line), transparent);}
.scenario {margin: .2rem 0 1rem 0; font-size:.88rem; opacity:.9;}
.tag {
    display:inline-block; padding:.12rem .6rem; border-radius:999px; font-size:.78rem; margin:.1rem .25rem .1rem 0;
    background: rgba(255,77,79,.14); border:1px solid rgba(255,77,79,.4); color:var(--badt);
}

/* ---------- Ficha del inspector ---------- */
.ficha {
    padding: 1.1rem 1.2rem; border-radius: 20px; margin: .4rem 0 1rem 0;
    background: linear-gradient(145deg, rgba(77,163,255,.10), var(--card3));
    border: 1px solid var(--edge); box-shadow: var(--elev); animation: rise .4s ease both;
}
.ficha-head {display:flex; align-items:center; gap:.9rem; margin-bottom:.9rem;}
.ficha-ico {
    width:56px; height:56px; border-radius:16px; display:flex; align-items:center; justify-content:center;
    font-size:1.8rem; background: linear-gradient(135deg, var(--accent), var(--accent2));
    box-shadow: 0 8px 22px rgba(77,163,255,.3);
}
.ficha-name {font-size:1.35rem; font-weight:800; line-height:1.15;}
.ficha-type {font-size:.85rem; opacity:var(--mut); display:flex; align-items:center; gap:.5rem; flex-wrap:wrap;}
.ficha-grid {display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:.7rem; margin-bottom:.9rem;}
.nbs-title {font-size:.74rem; letter-spacing:1px; text-transform:uppercase; opacity:var(--mut); margin-bottom:.4rem; font-weight:700;}
.nb {
    display:inline-block; padding:.3rem .75rem; margin:.15rem .3rem .15rem 0; border-radius:999px;
    font-size:.82rem; background: var(--chip); border:1px solid var(--chipline);
}
.nb-off {opacity:.5; text-decoration: line-through; border-color: rgba(255,77,79,.5);}

/* ---------- Refuerzo de legibilidad (modo día/noche) ---------- */
/* Varios contenedores de widgets llevan el color de letra del tema base en su propia regla de Streamlit:
   se los fija aquí para que sigan el modo activo (los textos hijos ya venían cubiertos abajo). */
.stApp :is(div[data-testid="stExpander"], div[data-testid="stRadioGroup"], div[data-testid="stRadioGroup"] > div,
           label[data-testid="stRadioOption"], div[data-testid="stCheckbox"], div[data-testid="stSelectbox"],
           div[data-testid="stMultiSelect"], div[data-testid="stTextInput"], div[data-testid="stNumberInput"],
           div[data-testid="stFileUploader"], div[data-testid="stButton"], div[data-testid="stDownloadButton"],
           div[data-testid="stForm"], div[data-testid="stTabs"], div[role="tabpanel"], .react-aria-ComboBox) {
    color: var(--text);}
[data-testid="stMarkdownContainer"] {color: var(--text);}
.stApp :is(p, li, label, h1, h2, h3, h4, h5, h6, td, th, summary, dt, dd) {color: var(--text) !important;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * {color: var(--soft) !important;}
input::placeholder, textarea::placeholder {color: var(--soft) !important; -webkit-text-fill-color: var(--soft) !important; opacity: 1 !important;}
[data-testid="stTooltipContent"], [data-testid="stTooltipContent"] * {background: var(--input) !important; color: var(--text) !important;}
[data-testid="stTooltipContent"] {border: 1px solid var(--line); border-radius: 8px;}
div[data-testid="stToast"], div[data-testid="stToast"] > div {background: var(--input) !important; border: 1px solid var(--line);}
div[data-testid="stToast"] * {color: var(--text) !important;}
[data-testid="stCode"], [data-testid="stCode"] pre {background: var(--card3) !important; border-radius: 12px;}
[data-testid="stCode"] * {color: var(--text) !important;}
[data-testid="stMarkdownContainer"] :not(pre) > code {background: var(--chip) !important; color: var(--codec) !important;}

/* Listas desplegables: la capa ya recibe el color del tema; aquí solo se tiñen las filas y el svg */
[role="listbox"], [role="listbox"] * {background-color: transparent !important; color: var(--text) !important;}
[role="listbox"] :is([role="option"], li):is(:hover, [aria-selected="true"], [data-focused], [data-highlighted="true"]) {
    background-color: var(--optsel) !important;}
[role="listbox"] svg {fill: var(--soft) !important; color: var(--soft) !important;}

/* ---------- Expanders: la cabecera nunca usa el fondo oscuro del tema base ---------- */
div[data-testid="stExpander"] {color: var(--text);}
div[data-testid="stRadioGroup"] :is([data-rac], label) {color: var(--text);}
div[data-testid="stExpander"] details, div[data-testid="stExpander"] details[open],
div[data-testid="stExpander"] summary, div[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpanderDetails"] {background: transparent !important; background-color: transparent !important; box-shadow: none !important;}
div[data-testid="stExpander"] summary:is(:hover, :focus-visible, :active) {background-color: var(--optsel) !important;
    transition: background-color .2s var(--ease);}
div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary * {color: var(--text) !important;}

/* Streamlit declara fundidos propios en dos sitios que el cambio de modo sí toca: los cuatro bordes del
   <details> de cada expander y la pista del interruptor. Se reduce su lista de propiedades a transform y
   opacity, que no dependen del tema: el color cambia de golpe y el deslizamiento del pulsador se conserva.
   (Ninguna regla nuestra transiciona color en el selector base; solo dentro de :hover.) */
div[data-testid="stExpander"] details, div[data-testid="stCheckbox"] label > div,
div[data-testid="stCheckbox"] label > div > div {transition-property: transform, opacity !important;}

@media (max-width: 900px) {.hero-art {display:none;} .hero h1 {font-size:1.9rem;}}
"""

# Ajustes que solo se aplican en modo día
CSS_DIA = """
.stApp a {color: var(--accentt) !important;}
/* Chips del multiselect (valores ya elegidos) */
[data-testid="stMultiSelectTagsContainer"] span[aria-label="Selected values"] > span {background-color: var(--accentt) !important;}
/* Interruptor y casillas: la pista es el primer div del label, el pulsador es su hijo */
div[data-testid="stCheckbox"] label > div:first-of-type {background-color: #CBD5E1 !important;}
div[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type {background-color: var(--accentt) !important;}
div[data-testid="stCheckbox"] label > div:first-of-type > div {background-color: #FFFFFF !important; box-shadow: 0 1px 3px rgba(15,23,42,.35);}
/* Botones de radio: el círculo es el primer div dentro del div del label */
label[data-testid="stRadioOption"] > div > div:first-child {background-color: #FFFFFF !important; border: 1px solid #64748B !important;}
label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {background-color: var(--accentt) !important; border-color: var(--accentt) !important;}
label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div {background-color: #FFFFFF !important;}
div[data-testid="stAlert"] {border: 1px solid var(--lineb); border-radius: 12px;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {background: #E8F1FF !important; border-color: #9CC2F5;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {background: #E6F6EC !important; border-color: #86D3A0;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {background: #FFF4DB !important; border-color: #F0C36A;}
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {background: #FDEAEA !important; border-color: #F2A3A3;}
section[data-testid="stSidebar"] {box-shadow: 2px 0 14px rgba(15,23,42,.06);}
"""

# Animaciones: solo se animan opacity y transform (las compone la GPU, sin recalcular el diseño de la
# página). La apertura/cierre de los expanders usa ::details-content cuando el navegador lo soporta
# (con interpolate-size para animar hasta "height:auto") y, si no, un fundido con desplazamiento al abrir.
CSS_ANIM = """
:root {--ease: cubic-bezier(.22, .61, .36, 1); interpolate-size: allow-keywords;}
@keyframes fade-up {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: none;}}
@keyframes slide-down {from {opacity: 0; transform: translateY(-8px);} to {opacity: 1; transform: none;}}
@keyframes pop-in {from {opacity: 0; transform: translateY(-6px) scale(.98);} to {opacity: 1; transform: none;}}

/* Cambio de pestaña: el panel que se muestra entra con un fundido y un leve ascenso */
[role="tabpanel"]:not([hidden]) {animation: fade-up .38s var(--ease) both;}

/* El cambio de modo día/noche NO se anima: se aplica de golpe. Para que así sea, ninguna regla base
   transiciona propiedades de color (background, border, box-shadow); los fundidos de color viven solo
   dentro de :hover, que es el único momento en que interesa que haya. */

/* Paneles desplegables (expanders): fundido y descenso al abrir; la altura y el cierre los anima el script */
div[data-testid="stExpander"] details[open] > :not(summary) {animation: slide-down .3s var(--ease) both;}

/* Copia de salida de una lista desplegable: se desvanece sola y termina invisible e intocable */
@keyframes ns-salida {from {opacity: 1;} to {opacity: 0; visibility: hidden;}}
@keyframes ns-lista-salida {from {opacity: 1; transform: none;} to {opacity: 0; transform: translateY(-6px) scale(.98);}}
[data-nsg]:not([data-nsk]) {pointer-events: none !important; animation: ns-salida .16s var(--ease) forwards !important;}
[data-nsg]:not([data-nsk]) [role="listbox"] {transform-origin: top center; animation: ns-lista-salida .16s var(--ease) forwards !important;}

/* Respaldo sin script: la lista aparece con animación (con el script activo se encarga él, también al cerrar) */
html:not([data-ns-js]) [role="listbox"] {animation: pop-in .18s var(--ease) both; transform-origin: top center;}

/* Los mensajes aparecen con suavidad. Gráficos y tablas NO llevan animación de entrada: Streamlit los
   monta de nuevo en cada refresco, así que fundirlos se vería también al cambiar de modo. */
div[data-testid="stAlert"] {animation: fade-up .3s var(--ease) both;}

/* Pulsar un botón da una respuesta táctil */
button[kind="secondary"]:active, button[kind="secondaryFormSubmit"]:active, button[kind="primary"]:active,
button[kind="primaryFormSubmit"]:active, button[data-testid^="stBaseButton-"]:active {transform: scale(.97);}
"""

# Si el sistema operativo pide reducir el movimiento, se respeta aunque las animaciones estén activadas
CSS_MOVIMIENTO_REDUCIDO = """
/* Con "reducir movimiento" activo en el sistema se conservan los fundidos suaves, pero se quitan los
   desplazamientos, los escalados y las animaciones que se repiten sin parar. */
@media (prefers-reduced-motion: reduce) {
    @keyframes fade-up {from {opacity: 0;} to {opacity: 1;}}
    @keyframes slide-down {from {opacity: 0;} to {opacity: 1;}}
    @keyframes pop-in {from {opacity: 0;} to {opacity: 1;}}
    @keyframes rise {from {opacity: 0;} to {opacity: 1;}}
    .hero, .status .dot, .hero-art line, .hero-art circle {animation: none !important;}
    button:active {transform: none !important;}
}
"""

# Las tablas se dibujan en un lienzo que no admite CSS: si su tema base no coincide con el modo, se invierten
CSS_TABLAS_INVERTIDAS = '\ndiv[data-testid="stDataFrame"] {filter: invert(1) hue-rotate(180deg);}\n'

# ---------------------------------------------------------------------------
# Ilustración de la cabecera
# ---------------------------------------------------------------------------
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


def css_completo(modo_dia: bool, invertir_tablas: bool) -> str:
    """Devuelve el bloque <style> final: variables del tema + hojas de estilo del modo activo."""
    tema = TEMAS["dia" if modo_dia else "noche"]
    variables = (":root{color-scheme:" + ("light" if modo_dia else "dark") + ";"
                 + "".join(f"--{k}:{v};" for k, v in tema.items())
                 + "--accent:#4DA3FF;--accent2:#7C5CFF;--ok:#2ECC71;--warn:#F5A623;--bad:#FF4D4F;}")
    css = CSS_BASE + (CSS_DIA if modo_dia else "") + CSS_ANIM + CSS_MOVIMIENTO_REDUCIDO
    if invertir_tablas:
        css += CSS_TABLAS_INVERTIDAS
    lineas = (l for l in (variables + css).splitlines() if l.strip())
    return "<style>\n" + "\n".join(lineas) + "\n</style>"


# ---------------------------------------------------------------------------
# Utilidades de HTML y color
# ---------------------------------------------------------------------------
def esc(x) -> str:
    """Escapa cualquier valor para insertarlo en HTML."""
    return html.escape(str(x))


def colapsar_html(texto: str) -> str:
    """Colapsa HTML en una línea (evita que Markdown lo interprete como bloque de código)."""
    return "".join(linea.strip() for linea in texto.splitlines())


def rgba(color_hex: str, alpha) -> str:
    """'#RRGGBB' + opacidad -> 'rgba(r,g,b,alpha)'."""
    h = color_hex.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"
