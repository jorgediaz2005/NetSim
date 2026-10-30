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
    "mapa": ("Lectura del mapa", """
- Cada **figura** representa un dispositivo y cada **línea**, un enlace. El **color** del dispositivo indica su
  *criticidad* (verde, naranja o rojo); el **grosor y el color** del enlace indican su latencia.
- Una **✖ roja** señala un dispositivo desactivado; una línea roja discontinua, un enlace interrumpido.
- El dato relevante no es solo qué elemento falla, sino **qué ocurre con el resto**: si los equipos que
  permanecen activos siguen pudiendo comunicarse entre sí.
- Para comprobarlo: desactive un switch en el panel lateral y observe cuántos componentes aparecen bajo el mapa.
"""),
    "rutas": ("Criterio de selección de ruta (Dijkstra)", """
Un router no selecciona el camino con menos saltos, sino el de **menor coste total**. En NetSim el coste es la
**latencia en ms**: Dijkstra suma las latencias de cada tramo y conserva la menor suma.

**Ejemplo:** de A a C directamente se invierten 10 ms; pasando por B, 3 + 4 = 7 ms. Pese a tener un salto más,
la ruta por B es la óptima.

Las **rutas alternativas** indican la *redundancia* disponible: si falla la mejor, el tráfico puede usar otra,
normalmente con más latencia. Cuando solo existe una ruta, ese camino es un punto único de fallo.
"""),
    "criticidad": ("Interpretación de las puntuaciones", """
La puntuación combina tres factores (cada uno entre 0 y 1):

1. **Centralidad de grado:** número de vecinos directos respecto al máximo posible. Un switch con muchos
   enlaces alcanza un grado alto.
2. **Centralidad de intermediación:** fracción de los caminos mínimos *entre otros* dispositivos que pasan por
   el nodo analizado. Un dispositivo con pocas conexiones puede ser determinante si concentra el tránsito ajeno.
3. **Importancia del tipo:** un router o un firewall pesan más que un PC; es una decisión de diseño del
   simulador, no una medición obtenida de la red.

Se trata de una **regla didáctica**, no de una medición oficial de riesgo. Su finalidad es permitir razonar por
qué un dispositivo se clasifica en nivel alto y otro en nivel bajo.
"""),
    "resiliencia": ("Punto único de fallo, puente e índice", """
- **Punto único de fallo (SPOF):** dispositivo cuya caída deja a otros equipos sin comunicación. En teoría de
  grafos se denomina *punto de articulación*.
- **Enlace puente:** enlace cuya interrupción divide la red en dos componentes. Si un PC depende de un único
  enlace, ese enlace es un puente.
- **Índice de resiliencia:** porcentaje de dispositivos que **no** son puntos únicos de fallo.

El índice tiene un límite interpretativo: una topología en estrella puede mostrar un índice alto porque solo
concentra *un* punto único de fallo, pero ese punto condiciona a toda la red. Conviene revisar también los
**enlaces puente** y el **impacto por dispositivo**.
"""),
    "ml": ("Función del módulo de aprendizaje automático", """
Un **árbol de decisión** infiere reglas del tipo «si la intermediación es alta *y* el tipo es relevante →
criticidad alta» a partir de ejemplos etiquetados.

En este módulo los ejemplos son **sintéticos**: se generan de forma aleatoria y se etiquetan con la misma regla
de la pestaña Criticidad. Por eso el modelo acierta con tanta frecuencia: reproduce *una fórmula ya definida*.
Es una demostración del flujo (datos → entrenamiento → evaluación → predicción), no una herramienta capaz de
predecir fallos en una red real.

- **Exactitud:** proporción de aciertos sobre el total de casos.
- **Precisión:** de los casos clasificados como «Alta», proporción que realmente lo era.
- **Recall (sensibilidad):** de los casos realmente «Alta», proporción detectada.
- **F1:** media armónica entre precisión y recall.
"""),
    "topologia": ("Guardado e intercambio de la topología", """
La topología puede exportarse como **JSON** y volverse a importar más tarde, o compartirse con otros usuarios. El
**informe HTML** resume el escenario y admite impresión como PDF (Ctrl + P) para adjuntarlo a una práctica.
El desplegable **Formato del archivo JSON** muestra la estructura exacta del archivo.
"""),
}

# ---------------------------------------------------------------------------
# Lecciones
# ---------------------------------------------------------------------------
LECCIONES = [
    {"titulo": "1. Una red es un grafo", "nivel": "Principiante", "texto": """
Un **grafo** es un conjunto de **nodos** unidos por **aristas**. Al representar los dispositivos como nodos y
los cables como aristas se obtiene un modelo matemático de la red.

El modelo permite responder preguntas sin intervenir equipos reales: *¿existe un camino entre A y B?, ¿cuál es
el de menor latencia?, ¿qué ocurre si se retira un nodo?*

**Práctica:** en el panel lateral despliegue *Añadir dispositivo* y *Añadir / editar conexión* y construya una
red de 4 equipos. Observe cómo cambia el mapa.
"""},
    {"titulo": "2. Latencia y camino de coste mínimo", "nivel": "Principiante", "texto": """
Cada enlace tiene una **latencia** (ms). La latencia de un camino es la **suma** de sus tramos, y el algoritmo
de **Dijkstra** calcula el de menor suma.

- Más saltos no implican necesariamente un peor camino.
- Si falla un enlace, la ruta óptima puede cambiar y la latencia, aumentar.

**Práctica:** en *Rutas* seleccione dos dispositivos, anote la latencia obtenida, desactive un enlace del camino
y compare ambos resultados.
"""},
    {"titulo": "3. Redundancia y puntos únicos de fallo", "nivel": "Principiante", "texto": """
**Redundancia** es la existencia de más de un camino entre dos puntos. Una red sin redundancia funciona hasta
que un elemento falla.

Un **punto único de fallo** es aquel elemento sin el cual parte de la red queda aislada. Identificarlos es el
primer paso para decidir **dónde añadir un enlace extra**.

Regla práctica de diseño: *«N+1»* — suponga que cualquier elemento puede fallar y compruebe que la red sigue
operativa.

**Práctica:** en *Resiliencia* consulte la tabla de impacto y aplique una de las mejoras sugeridas.
"""},
    {"titulo": "4. Factores que determinan la criticidad", "nivel": "Intermedio", "texto": """
La importancia de un dispositivo depende de **su nivel de conexión** (grado), de **cuánto tránsito ajeno
concentra** (intermediación) y de **la función que cumple** (tipo).

Un servidor con una sola conexión puede ser crítico para el servicio aunque, estructuralmente, sea una hoja del
grafo. Por eso NetSim combina estructura *y* función.

**Práctica:** añada un PC y un Router conectados al mismo switch, con la misma latencia, y compare sus
puntuaciones en *Criticidad*.
"""},
    {"titulo": "5. Topologías: estrella, anillo y malla", "nivel": "Intermedio", "texto": """
La **topología** es la forma en que se conectan los dispositivos. Cada una presenta ventajas y costes
distintos: sencillez, cantidad de cableado, resistencia a fallos y latencia.

No existe una topología óptima absoluta: una oficina pequeña no requiere la complejidad de una malla, mientras
que un campus con servicios críticos sí necesita redundancia.

**Práctica:** en la subpestaña *Topologías* de esta pestaña, compare las métricas de las cinco plantillas.
"""},
    {"titulo": "6. Datos, modelos y sus límites", "nivel": "Avanzado", "texto": """
Un modelo de aprendizaje automático depende por completo de sus **datos**. Si son sintéticos y se etiquetan
mediante una fórmula, el modelo aprende esa fórmula, y una exactitud muy alta **no** demuestra que sea útil en
una red real.

Conviene plantear siempre: *¿de dónde proceden los datos?, ¿se parecen a los casos reales?, ¿con qué criterio
se comparan?*

**Práctica:** en *Aprendizaje automático* localice los dispositivos donde la predicción del árbol **no coincide**
con la regla (⚠️) e intente explicar la diferencia.
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
        "contras": ["Cada PC depende de un único switch: si ese switch falla, el PC queda aislado.",
                    "Los switches son puntos únicos de fallo."],
        "uso": "Pequeños negocios y aulas.",
    },
    "Estrella (1 switch)": {
        "idea": "Todos los equipos se conectan a un switch central.",
        "pros": ["Muy sencilla de instalar y administrar.", "La caída de un PC no afecta a los demás equipos."],
        "contras": ["El switch central es un punto único de fallo: si falla, todos los equipos quedan aislados "
                    "entre sí.", "Todos los enlaces son puentes."],
        "uso": "Aulas y oficinas pequeñas sin requisitos de alta disponibilidad.",
    },
    "Anillo de switches": {
        "idea": "Los switches forman un ciclo; cada uno tiene dos vecinos.",
        "pros": ["Si se interrumpe un enlace del anillo, el tráfico circula por el lado opuesto.",
                 "Menor cableado para la redundancia que ofrece."],
        "contras": ["Dos interrupciones dividen el anillo.", "La latencia aumenta al rodear el anillo.",
                    "En la plantilla, el router depende de un solo switch: este sigue siendo punto único de "
                    "fallo."],
        "uso": "Redes industriales o de campus con cableado en bucle (con protocolos que evitan bucles).",
    },
    "Campus con redundancia": {
        "idea": "Dos switches de núcleo interconectados con accesos y servidores enlazados a ambos.",
        "pros": ["Mantiene el servicio ante la caída de un núcleo.", "Los servidores disponen de dos caminos."],
        "contras": ["Coste y complejidad mayores.",
                    "Si caen **los dos** núcleos, la red se fragmenta; los PC siguen dependiendo de un único "
                    "acceso."],
        "uso": "Campus, hospitales o empresas con servicios críticos.",
    },
    "Malla de routers": {
        "idea": "Los routers se interconectan entre sí con varios caminos posibles.",
        "pros": ["Múltiples caminos alternativos entre routers.", "Rutas cortas gracias a los enlaces directos."],
        "contras": ["Más enlaces y más configuración.",
                    "Un núcleo en malla no protege a los equipos finales que dependen de un solo router."],
        "uso": "Redes troncales y de operadores.",
    },
}

# ---------------------------------------------------------------------------
# Retos guiados (se cargan con un botón; el contenido se verificó con netsim_core)
# ---------------------------------------------------------------------------
RETOS = [
    {
        "titulo": "El switch central concentra todo el riesgo", "nivel": "Principiante",
        "plantilla": "Estrella (1 switch)",
        "fallos": ["Switch central"], "enlaces": [], "ruta": None,
        "objetivo": "Con el switch central desactivado, ¿en cuántos componentes queda la red y cuántos pares de "
                    "equipos pierden la comunicación?",
        "pistas": ["Observe la cabecera de la pestaña Mapa y los indicadores superiores.",
                   "Cada equipo que queda aislado forma un componente."],
        "solucion": "Quedan **6 componentes** (cada equipo, aislado) y **15 pares** sin comunicación. El switch "
                    "central es un punto único de fallo y todos los enlaces de la estrella son puentes.",
    },
    {
        "titulo": "Interrupción de un enlace en el anillo", "nivel": "Principiante",
        "plantilla": "Anillo de switches",
        "fallos": [], "enlaces": [("Switch 1", "Switch 2")], "ruta": ("Switch 2", "Router"),
        "objetivo": "Se ha interrumpido el enlace Switch 1 ↔ Switch 2. ¿Sigue conectada la red? ¿Cuánto varía la "
                    "latencia de Switch 2 a Router? Haga clic en *Limpiar* para comparar con la red sin fallos.",
        "pistas": ["Abra *Rutas*: el origen y el destino ya están seleccionados.",
                   "Compare la latencia con y sin el enlace interrumpido."],
        "solucion": "La red **sigue conectada** (0 pares perdidos): el tráfico rodea el anillo. La ruta pasa de "
                    "**4 ms** (2 saltos) a **14 ms** (5 saltos): existe redundancia, pero a costa de latencia.",
    },
    {
        "titulo": "Identificación del peor caso", "nivel": "Principiante", "plantilla": "Oficina pequeña",
        "fallos": [], "enlaces": [], "ruta": None,
        "objetivo": "¿Qué dispositivo, al fallar, deja sin comunicación a más equipos? Compruebe el resultado con "
                    "el botón «Peor caso» y con la tabla de Resiliencia.",
        "pistas": ["Observe la columna «Pares que pierden comunicación».",
                   "¿Qué característica comparten los dispositivos de mayor impacto?"],
        "solucion": "Los dos **switches** empatan con **5 pares** perdidos. Son puntos únicos de fallo porque cada "
                    "uno sostiene a un PC que no tiene otro camino.",
    },
    {
        "titulo": "Agotamiento de la redundancia", "nivel": "Intermedio", "plantilla": "Campus con redundancia",
        "fallos": ["Núcleo A"], "enlaces": [], "ruta": None,
        "objetivo": "Con Núcleo A desactivado, compruebe que no se pierde comunicación. Después **desactive "
                    "también Núcleo B** en el panel lateral. ¿Qué ocurre?",
        "pistas": ["Añada «Núcleo B» al selector de dispositivos desactivados.",
                   "Compare el número de componentes antes y después."],
        "solucion": "Con un solo núcleo desactivado se pierden **0 pares**. Con los dos fuera de servicio la red se "
                    "fragmenta en **6 componentes** y **49 pares** pierden la comunicación. La redundancia protege "
                    "frente a *un* fallo, no frente a cualquier combinación.",
    },
    {
        "titulo": "Corrección de la topología de oficina", "nivel": "Intermedio", "plantilla": "Oficina pequeña",
        "fallos": [], "enlaces": [], "ruta": None,
        "objetivo": "Deje la red sin puntos únicos de fallo ni puentes. Utilice *Mejoras sugeridas* en la pestaña "
                    "Resiliencia y haga clic en *Aplicar*. Repita la operación hasta que no queden sugerencias.",
        "pistas": ["Tras aplicar una mejora, vuelva a consultar el índice de resiliencia.",
                   "¿Es realista conectar un PC al firewall? Considere qué aplicaría un técnico en la práctica."],
        "solucion": "Bastan **dos enlaces**: el índice sube de **71 %** a **86 %** con el primero y a **100 %** con "
                    "el segundo. La heurística es estructural: en una red real, enlazar un PC a dos equipos exige "
                    "configuración y hardware adecuados.",
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
    ("Componente conexo", "Conjunto de nodos que pueden comunicarse entre sí.",
     "Si hay más de uno, la red está fragmentada."),
    ("Punto único de fallo (SPOF)", "Nodo cuya caída aísla a otros. En grafos: punto de articulación.",
     "Se marca «Sí» en la tabla de resiliencia."),
    ("Puente", "Enlace cuya rotura divide la red.", "Columna «Enlace crítico (puente)»."),
    ("Redundancia", "Existencia de caminos o equipos alternativos.", "Aparece como rutas alternativas."),
    ("Topología", "Forma en que se conectan los dispositivos de una red.",
     "Estrella, anillo, malla, campus, oficina."),
    ("Índice de resiliencia", "Porcentaje de dispositivos que no son punto único de fallo.",
     "Tiene límites: conviene consultar también los enlaces puente."),
    ("Árbol de decisión", "Modelo de aprendizaje automático que clasifica mediante decisiones sucesivas sobre los datos.",
     "Aproxima la regla de criticidad a partir de datos sintéticos."),
    ("Exactitud, precisión y recall",
     "Métricas de clasificación: aciertos totales, aciertos al predecir una clase y casos detectados de una clase.",
     "Se muestran en la pestaña Aprendizaje automático."),
]

# ---------------------------------------------------------------------------
# Test: (pregunta, opciones, índice correcto, explicación)
# ---------------------------------------------------------------------------
QUIZ = [
    ("¿Qué es un punto único de fallo?",
     ["Un dispositivo cuya caída deja a otros equipos sin comunicación",
      "El dispositivo con más latencia", "El primer router de la red", "Un enlace de alta velocidad"], 0,
     "Si cae, parte de la red queda aislada. En grafos se llama punto de articulación."),
    ("En NetSim, el algoritmo de Dijkstra selecciona la ruta que minimiza…",
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
     ["Número de conexiones directas del nodo", "Cuántos caminos mínimos entre otros pares pasan por el nodo",
      "La velocidad del nodo", "El precio del dispositivo"], 1,
     "Un nodo con pocas conexiones puede resultar determinante si concentra buena parte de los caminos."),
    ("¿Qué aporta la redundancia?",
     ["Menos latencia siempre", "Caminos o equipos alternativos cuando algo falla",
      "Menos dispositivos", "Mayor seguridad frente a ataques"], 1,
     "Aporta tolerancia a fallos; no garantiza menor latencia ni seguridad por sí sola."),
    ("Un componente conexo es…",
     ["Un dispositivo averiado", "Un conjunto de dispositivos que pueden comunicarse entre sí",
      "Un enlace de la red troncal", "Un tipo de switch"], 1,
     "Si hay más de uno, la red está fragmentada."),
    ("El modelo de aprendizaje automático de NetSim acierta en casi todos los casos. ¿Qué indica esto?",
     ["Que predice averías reales con gran precisión",
      "Que reproduce con fidelidad la regla definida en el proyecto, aplicada a datos sintéticos",
      "Que la criticidad es una medición oficial de riesgo", "Que no requiere más datos"], 1,
     "Los datos son sintéticos: el modelo imita una fórmula establecida en este proyecto "
     "y no valida el comportamiento de redes reales."),
]

# ---------------------------------------------------------------------------
# Ayuda (apartado Configuración del panel lateral)
# ---------------------------------------------------------------------------
AYUDA_PASOS = [
    "En el panel lateral, apartado *Escenario de fallos*: desactive un dispositivo o interrompa un enlace.",
    "Consulte el estado y los indicadores: la red se recalcula de inmediato.",
    "En *Rutas*, seleccione origen y destino para obtener el camino de menor latencia.",
    "Para practicar, utilice los retos de la pestaña *Formación*.",
]

# (pregunta, respuesta)
AYUDA_FAQ = [
    ("¿Los fallos modifican mi red?",
     "No: se aplican sobre una copia. Haga clic en *Limpiar* para volver a la red base."),
    ("¿Qué son los «pares sin comunicación»?",
     "Parejas de dispositivos activos que podían comunicarse en la red base y ya no pueden hacerlo."),
    ("¿Por qué la ruta no es la de menos saltos?",
     "Porque se minimiza la latencia total, no el número de saltos."),
    ("¿Qué hace el botón «Peor caso»?",
     "Desactiva el dispositivo cuya caída incomunica a un mayor número de parejas."),
    ("¿Se guarda lo que modifico?",
     "No. Exporte la topología en JSON desde *Topología y exportación*."),
    ("¿Por qué el árbol de aprendizaje automático acierta con tanta frecuencia?",
     "Porque aprende la regla definida en este proyecto a partir de datos sintéticos: es una demostración "
     "del procedimiento, no una validación real."),
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