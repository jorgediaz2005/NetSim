"""Contenido educativo y de ayuda de NetSim.

Aquí viven SOLO los textos y datos (lecciones, glosario, retos, test, ayuda).
La interfaz (app.py) los dibuja; así se pueden ampliar o corregir sin tocar código.

Público objetivo: estudiantes de iniciación a redes e informática (ciclos formativos
SMR/ASIR y primeros cursos de grado). Se asume que conocen qué es un router o un
switch, pero no la teoría de grafos ni el análisis de resiliencia.
"""
from __future__ import annotations

PUBLICO = "estudiantes de redes e informática"

# ---------------------------------------------------------------------------
# Explicaciones contextuales (desplegables dentro de cada pestaña)
# ---------------------------------------------------------------------------
EXPLICACIONES = {
    "mapa": ("Cómo leer el mapa", """
- Cada **figura** es un dispositivo y cada **línea** un enlace. El **color** del dispositivo indica su
  *criticidad* (verde, naranja o rojo) y el **grosor/color** del enlace indica su latencia.
- Una **✖ roja** es un dispositivo apagado; una línea roja discontinua, un enlace interrumpido.
- Lo importante no es solo *qué* cae, sino **qué pasa con el resto**: ¿siguen pudiendo hablar entre sí
  los equipos que continúan encendidos?
- Prueba: desactiva un switch en el panel lateral y mira cuántos grupos aparecen debajo del mapa.
"""),
    "rutas": ("¿Cómo elige Dijkstra la ruta?", """
Un router no elige «el camino con menos saltos», sino el de **menor coste total**. En NetSim el coste es
la **latencia en ms**, así que Dijkstra suma las latencias de cada tramo y se queda con la menor suma.

**Ejemplo:** ir de A a C directamente cuesta 10 ms; pasando por B cuesta 3 + 4 = 7 ms. Aunque tenga
más saltos (2 frente a 1), la ruta por B es mejor.

Las **rutas alternativas** muestran la *redundancia*: si falla la mejor, el tráfico puede usar otra,
normalmente con más latencia. Si solo hay una ruta, ese camino es frágil.
"""),
    "criticidad": ("¿Qué significan estas puntuaciones?", """
La puntuación mezcla tres ideas (cada una entre 0 y 1):

1. **Centralidad de grado:** cuántos vecinos directos tiene respecto al máximo posible. Un switch con
   muchos cables tiene un grado alto.
2. **Centralidad de intermediación:** qué fracción de los caminos más cortos *entre otros* dispositivos pasa
   por él. Un dispositivo con pocas conexiones puede ser clave si está «en medio» de todo.
3. **Importancia del tipo:** un router o un firewall pesan más que un PC (decisión de diseño del simulador).

Es una **regla didáctica**, no una medida oficial de riesgo. Sirve para razonar: *¿por qué este equipo
sale rojo y este otro verde?*
"""),
    "resiliencia": ("Punto único de fallo, puente e índice", """
- **Punto único de fallo (SPOF):** dispositivo cuya caída deja a otros equipos sin salida. En teoría de
  grafos se llama *punto de articulación*.
- **Enlace puente:** cable cuya rotura parte la red en dos. Si un PC cuelga de un único cable, ese cable
  es un puente.
- **Índice de resiliencia:** porcentaje de dispositivos que **no** son puntos únicos de fallo.

El índice tiene límites: una red en estrella puede salir con un índice alto porque solo tiene *un* SPOF…
¡pero ese SPOF lo es todo! Mira siempre también los **enlaces puente** y el **impacto por dispositivo**.
"""),
    "ml": ("¿Qué hace aquí el Machine Learning?", """
Un **árbol de decisión** aprende reglas del tipo «si la intermediación es alta *y* el tipo es importante →
criticidad alta» a partir de ejemplos etiquetados.

Aquí los ejemplos son **sintéticos**: se generan al azar y se etiquetan con la misma regla de la pestaña
Criticidad. Por eso el modelo acierta tanto: solo está *imitando una fórmula*. Es una demostración del flujo
(datos → entrenamiento → evaluación → predicción), no una herramienta para predecir averías reales.

- **Exactitud:** aciertos sobre el total.
- **Precisión:** de lo que dijo «Alta», cuánto era realmente «Alta».
- **Recall:** de todo lo que era «Alta», cuánto detectó.
- **F1:** equilibrio entre precisión y recall.
"""),
    "topologia": ("Guardar y compartir tu red", """
Puedes exportar la topología como **JSON** y volver a importarla más tarde (o pasársela a un compañero). El
**informe HTML** resume el escenario y se puede imprimir como PDF (Ctrl + P) para adjuntarlo a una práctica.
Consulta el desplegable **Formato del archivo JSON** para ver la estructura exacta.
"""),
}

# ---------------------------------------------------------------------------
# Lecciones
# ---------------------------------------------------------------------------
LECCIONES = [
    {"titulo": "1. Una red es un grafo", "nivel": "Básico", "texto": """
Un **grafo** es un conjunto de **nodos** unidos por **aristas**. Si pones los dispositivos como nodos y los
cables como aristas, tienes un modelo matemático de tu red.

Con él se pueden responder preguntas sin tocar equipos reales: *¿hay camino entre A y B? ¿cuál es el más
rápido? ¿qué pasa si quito este nodo?*

**Pruébalo:** en el panel lateral abre *Añadir dispositivo* y *Añadir / editar conexión* y construye una red de
4 equipos. Observa cómo cambia el mapa.
"""},
    {"titulo": "2. Latencia y camino más corto", "nivel": "Básico", "texto": """
Cada enlace tiene una **latencia** (ms). La latencia de un camino es la **suma** de sus tramos. El algoritmo de
**Dijkstra** busca el camino de menor suma.

- Más saltos no siempre significa peor camino.
- Si falla un enlace, la mejor ruta puede cambiar y la latencia subir.

**Pruébalo:** en *Rutas* elige dos dispositivos, apunta la latencia, desactiva un enlace del camino y
compara.
"""},
    {"titulo": "3. Redundancia y puntos únicos de fallo", "nivel": "Básico", "texto": """
**Redundancia** es tener más de un camino entre dos puntos. Una red sin redundancia funciona… hasta que algo
falla.

Un **punto único de fallo** es un elemento sin el cual parte de la red queda aislada. Detectarlos es el primer
paso para decidir **dónde poner un enlace extra**.

Regla práctica de diseño: *«N+1»* — piensa que cualquier elemento puede fallar y comprueba que la red sigue
funcionando.

**Pruébalo:** en *Resiliencia* mira la tabla de impacto, y aplica una de las mejoras sugeridas.
"""},
    {"titulo": "4. ¿Qué dispositivo es más crítico?", "nivel": "Intermedio", "texto": """
La importancia de un equipo depende de **lo conectado que está** (grado), de **lo «en medio» que está**
(intermediación) y de **qué función cumple** (tipo).

Un servidor con una sola conexión puede ser muy importante para el negocio aunque estructuralmente sea una
hoja del grafo. Por eso NetSim combina estructura *y* función.

**Pruébalo:** añade un PC y un Router conectados al mismo switch, con la misma latencia, y compara sus
puntuaciones en *Criticidad*.
"""},
    {"titulo": "5. Topologías: estrella, anillo, malla…", "nivel": "Intermedio", "texto": """
La **topología** es la forma en que se conectan los dispositivos. Cada una tiene ventajas y costes:
sencillez, cantidad de cable, resistencia a fallos y latencia.

No hay una «mejor» absoluta: una oficina pequeña no necesita la complejidad de una malla; un campus con
servicios críticos sí necesita redundancia.

**Pruébalo:** en la subpestaña *Topologías* de esta pestaña, compara las métricas de las cinco plantillas.
"""},
    {"titulo": "6. Datos, modelos y sus límites", "nivel": "Avanzado", "texto": """
Un modelo de Machine Learning solo es tan bueno como sus **datos**. Si los datos son sintéticos y se etiquetan
con una fórmula, el modelo aprende esa fórmula, y una exactitud altísima **no** demuestra que sirva en una red
real.

Pregúntate siempre: *¿de dónde salen los datos? ¿se parecen a los casos reales? ¿con qué lo comparo?*

**Pruébalo:** en *Machine Learning* busca los dispositivos donde la predicción del árbol **no coincide**
con la regla (⚠️) e intenta explicar por qué.
"""},
]

# ---------------------------------------------------------------------------
# Topologías (fichas)
# ---------------------------------------------------------------------------
TOPOLOGIAS = {
    "Oficina pequeña": {
        "idea": "Router y firewall en la entrada, dos switches interconectados y un servidor conectado a ambos.",
        "pros": ["Dos switches enlazados: el servidor sigue accesible si falla uno de los enlaces hacia él.",
                 "El firewall protege la red interna."],
        "contras": ["Cada PC cuelga de un único switch: si ese switch cae, el PC queda aislado.",
                    "Los switches son puntos únicos de fallo."],
        "uso": "Pequeños negocios y aulas.",
    },
    "Estrella (1 switch)": {
        "idea": "Todos los equipos se conectan a un switch central.",
        "pros": ["Muy sencilla de montar y administrar.", "Si falla un PC, los demás no se enteran."],
        "contras": ["El switch central es un punto único de fallo: si cae, todo queda aislado.",
                    "Todos los enlaces son puentes."],
        "uso": "Aulas y oficinas pequeñas sin requisitos de alta disponibilidad.",
    },
    "Anillo de switches": {
        "idea": "Los switches forman un círculo; cada uno tiene dos vecinos.",
        "pros": ["Si se corta un enlace del anillo, el tráfico va por el otro lado.",
                 "Poco cable para la redundancia que ofrece."],
        "contras": ["Dos cortes dividen el anillo.", "La latencia crece al rodear el anillo.",
                    "En la plantilla, el router cuelga de un solo switch: sigue siendo punto único de fallo."],
        "uso": "Redes industriales o de campus con cableado en bucle (con protocolos que evitan bucles).",
    },
    "Campus con redundancia": {
        "idea": "Dos switches de núcleo interconectados con accesos y servidores enlazados a ambos.",
        "pros": ["Sobrevive a la caída de un núcleo.", "Los servidores tienen dos caminos."],
        "contras": ["Coste y complejidad mayores.",
                    "Si caen **los dos** núcleos, la red se fragmenta; los PC siguen colgando de un único acceso."],
        "uso": "Campus, hospitales o empresas con servicios críticos.",
    },
    "Malla de routers": {
        "idea": "Los routers se interconectan entre sí con varios caminos posibles.",
        "pros": ["Muchos caminos alternativos entre routers.", "Rutas cortas gracias a enlaces directos."],
        "contras": ["Más enlaces y configuración.",
                    "Un núcleo en malla no protege a los equipos finales que dependen de un solo router."],
        "uso": "Redes troncales y de operadores.",
    },
}

# ---------------------------------------------------------------------------
# Retos guiados (se cargan con un botón; el contenido se verificó con netsim_core)
# ---------------------------------------------------------------------------
RETOS = [
    {
        "titulo": "El switch que lo sostiene todo", "nivel": "Básico", "plantilla": "Estrella (1 switch)",
        "fallos": ["Switch central"], "enlaces": [], "ruta": None,
        "objetivo": "Con el switch central apagado, ¿en cuántos grupos queda la red y cuántos pares de "
                    "equipos pierden la comunicación?",
        "pistas": ["Mira la cabecera de la pestaña Mapa y los indicadores de arriba.",
                   "Cada equipo que queda solo es un grupo."],
        "solucion": "Quedan **6 grupos** (cada equipo, aislado) y **15 pares** sin comunicación. El switch central "
                    "es un punto único de fallo y todos los enlaces de la estrella son puentes.",
    },
    {
        "titulo": "Un corte en el anillo", "nivel": "Básico", "plantilla": "Anillo de switches",
        "fallos": [], "enlaces": [("Switch 1", "Switch 2")], "ruta": ("Switch 2", "Router"),
        "objetivo": "Se ha cortado el enlace Switch 1 ↔ Switch 2. ¿Sigue conectada la red? ¿Cuánto cambia la "
                    "latencia de Switch 2 a Router? Pulsa *Limpiar* para comparar con la red sana.",
        "pistas": ["Abre Rutas: el origen y el destino ya están elegidos.",
                   "Compara la latencia con y sin el enlace cortado."],
        "solucion": "La red **sigue conectada** (0 pares perdidos): el tráfico rodea el anillo. La ruta pasa de "
                    "**4 ms** (2 saltos) a **14 ms** (5 saltos). Redundancia sí, pero a costa de latencia.",
    },
    {
        "titulo": "Encuentra el peor caso", "nivel": "Básico", "plantilla": "Oficina pequeña",
        "fallos": [], "enlaces": [], "ruta": None,
        "objetivo": "¿Qué dispositivo, al caer, deja sin comunicación a más equipos? Compruébalo con el botón "
                    "«Peor caso» y con la tabla de Resiliencia.",
        "pistas": ["Fíjate en la columna «Pares que pierden comunicación».",
                   "¿Qué tienen en común los dispositivos con más impacto?"],
        "solucion": "Los dos **switches** empatan con **5 pares** perdidos. Son puntos únicos de fallo porque "
                    "cada uno sostiene a un PC que no tiene otro camino.",
    },
    {
        "titulo": "Cuando la redundancia se acaba", "nivel": "Intermedio", "plantilla": "Campus con redundancia",
        "fallos": ["Núcleo A"], "enlaces": [], "ruta": None,
        "objetivo": "Con Núcleo A apagado, comprueba que no se pierde comunicación. Después **desactiva también "
                    "Núcleo B** en el panel lateral. ¿Qué ocurre?",
        "pistas": ["Añade «Núcleo B» al selector de dispositivos desactivados.",
                   "Compara el número de componentes antes y después."],
        "solucion": "Con un solo núcleo caído hay **0 pares perdidos**. Con los dos caídos la red se rompe en "
                    "**6 grupos** y **49 pares** pierden la comunicación. La redundancia protege frente a *un* "
                    "fallo, no frente a cualquier combinación.",
    },
    {
        "titulo": "Arregla la oficina", "nivel": "Intermedio", "plantilla": "Oficina pequeña",
        "fallos": [], "enlaces": [], "ruta": None,
        "objetivo": "Deja la red sin puntos únicos de fallo ni puentes. Usa *Mejoras sugeridas* en la pestaña "
                    "Resiliencia y pulsa *Aplicar*. Repite hasta que no queden sugerencias.",
        "pistas": ["Tras aplicar una mejora, vuelve a mirar el índice de resiliencia.",
                   "¿Es realista conectar un PC al firewall? Piensa qué haría un técnico en la práctica."],
        "solucion": "Bastan **dos enlaces**: el índice sube de **71 %** a **86 %** con el primero y a **100 %** "
                    "con el segundo. Ojo: la heurística es estructural; en una red real un PC con dos cables "
                    "exige configuración y hardware adecuados.",
    },
]

# ---------------------------------------------------------------------------
# Glosario: (término, definición, en NetSim)
# ---------------------------------------------------------------------------
GLOSARIO = [
    ("Grafo", "Conjunto de nodos unidos por aristas. Es el modelo matemático de una red.",
     "Toda la topología es un grafo no dirigido."),
    ("Nodo", "Elemento de un grafo. Representa un dispositivo.",
     "Router, switch, servidor, PC, firewall, punto de acceso u otro."),
    ("Arista (enlace)", "Conexión entre dos nodos.", "Cada enlace tiene una latencia en ms."),
    ("Latencia", "Tiempo que tarda un paquete en recorrer un enlace o un camino.",
     "Es el «peso» de cada arista; la de un camino es la suma de sus tramos."),
    ("Salto (hop)", "Paso de un dispositivo al siguiente en un camino.", "Se muestra en la pestaña Rutas."),
    ("Dijkstra", "Algoritmo que encuentra el camino de menor coste total entre dos nodos.",
     "Calcula la ruta óptima y sus alternativas."),
    ("Grado", "Número de conexiones directas de un nodo.", "Columna «Conexiones»."),
    ("Centralidad de grado", "El grado dividido entre el máximo posible (n − 1).",
     "Pesa un 35 % en la criticidad."),
    ("Centralidad de intermediación",
     "Fracción de caminos mínimos entre otros pares de nodos que pasan por este.",
     "Pesa un 35 % en la criticidad."),
    ("Componente conexo", "Grupo de nodos que pueden comunicarse entre sí.",
     "Si hay más de uno, la red está fragmentada."),
    ("Punto único de fallo (SPOF)", "Nodo cuya caída aísla a otros. En grafos: punto de articulación.",
     "Se marca «Sí» en la tabla de resiliencia."),
    ("Puente", "Enlace cuya rotura divide la red.", "Columna «Enlace crítico (puente)»."),
    ("Redundancia", "Existencia de caminos o equipos alternativos.", "Aparece como rutas alternativas."),
    ("Topología", "Forma en que se conectan los dispositivos de una red.",
     "Estrella, anillo, malla, campus, oficina."),
    ("Índice de resiliencia", "Porcentaje de dispositivos que no son punto único de fallo.",
     "Tiene límites: consulta también los puentes."),
    ("Árbol de decisión", "Modelo de ML que clasifica mediante preguntas sucesivas sobre los datos.",
     "Imita la regla de criticidad con datos sintéticos."),
    ("Exactitud, precisión y recall",
     "Métricas de clasificación: aciertos totales, aciertos al predecir una clase y casos detectados de una clase.",
     "Se muestran en la pestaña Machine Learning."),
]

# ---------------------------------------------------------------------------
# Test: (pregunta, opciones, índice correcto, explicación)
# ---------------------------------------------------------------------------
QUIZ = [
    ("¿Qué es un punto único de fallo?",
     ["Un dispositivo cuya caída deja a otros equipos sin comunicación",
      "El dispositivo con más latencia", "El primer router de la red", "Un enlace de alta velocidad"], 0,
     "Si cae, parte de la red queda aislada. En grafos se llama punto de articulación."),
    ("En NetSim, Dijkstra elige la ruta que minimiza…",
     ["El número de saltos", "La suma de latencias", "El número de dispositivos activos",
      "La criticidad de los nodos"], 1,
     "Minimiza el coste total (ms), no los saltos: un camino con más saltos puede ser más rápido."),
    ("En una topología en estrella, si cae el switch central…",
     ["Solo se pierde ese switch", "Se aíslan todos los equipos entre sí", "La red sigue igual gracias a Dijkstra",
      "Solo caen los servidores"], 1,
     "Todos los equipos dependen de él: es un punto único de fallo."),
    ("Un enlace puente es aquel que…",
     ["Tiene la menor latencia", "Conecta dos switches", "Si se rompe, divide la red en partes",
      "Une un PC con un servidor"], 2,
     "Es una arista cuya eliminación aumenta el número de componentes."),
    ("La centralidad de intermediación mide…",
     ["Cuántos cables tiene un nodo", "Cuántos caminos mínimos entre otros pares pasan por el nodo",
      "La velocidad del nodo", "El precio del dispositivo"], 1,
     "Un nodo con pocas conexiones puede ser clave si está «en medio» de muchos caminos."),
    ("¿Qué aporta la redundancia?",
     ["Menos latencia siempre", "Caminos o equipos alternativos cuando algo falla",
      "Menos dispositivos", "Mayor seguridad frente a ataques"], 1,
     "Aporta tolerancia a fallos; no garantiza menor latencia ni seguridad por sí sola."),
    ("Un componente conexo es…",
     ["Un dispositivo averiado", "Un grupo de dispositivos que pueden comunicarse entre sí",
      "Un enlace de la red troncal", "Un tipo de switch"], 1,
     "Si hay más de uno, la red está fragmentada."),
    ("El modelo de ML de NetSim acierta casi siempre. ¿Qué significa?",
     ["Que predice averías reales con gran precisión",
      "Que reproduce muy bien una regla artificial con la que se etiquetaron datos sintéticos",
      "Que la criticidad es una medición oficial de riesgo", "Que no necesita más datos"], 1,
     "Los datos son sintéticos: el modelo imita una fórmula, no valida nada sobre redes reales."),
]

# ---------------------------------------------------------------------------
# Ayuda (apartado Configuración del panel lateral)
# ---------------------------------------------------------------------------
AYUDA_PASOS = [
    "En el panel lateral, *Escenario de fallos*: apaga un dispositivo o corta un enlace.",
    "Mira el estado y los indicadores: la red se recalcula al instante.",
    "En *Rutas* elige origen y destino para ver el camino de menor latencia.",
    "Para practicar, usa los retos de la pestaña *Aprende*.",
]

# (pregunta, respuesta)
AYUDA_FAQ = [
    ("¿Los fallos cambian mi red?",
     "No: se aplican sobre una copia. Pulsa *Limpiar* para volver a la red base."),
    ("¿Qué son los «pares sin comunicación»?",
     "Parejas de dispositivos encendidos que antes se comunicaban y ahora no."),
    ("¿Por qué la ruta no es la de menos saltos?",
     "Porque se minimiza la latencia total, no el número de saltos."),
    ("¿Qué hace el botón «Peor caso»?",
     "Apaga el dispositivo cuya caída deja incomunicadas a más parejas."),
    ("¿Se guarda lo que modifico?",
     "No. Exporta la topología en JSON desde *Topología y exportación*."),
    ("¿Por qué el árbol de ML acierta tanto?",
     "Aprende una regla que nosotros mismos inventamos, con datos sintéticos: es una demostración, "
     "no una validación real."),
]

JSON_EJEMPLO = """{
  "nodos": [
    {"nombre": "Router", "tipo": "Router"},
    {"nombre": "Switch 1", "tipo": "Switch"},
    {"nombre": "Servidor", "tipo": "Servidor"},
    {"nombre": "PC 1", "tipo": "PC"}
  ],
  "enlaces": [
    {"origen": "Router", "destino": "Switch 1", "latencia": 2},
    {"origen": "Switch 1", "destino": "Servidor", "latencia": 3},
    {"origen": "Switch 1", "destino": "PC 1", "latencia": 4}
  ]
}"""