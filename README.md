# NetSim — Simulador de redes informáticas

Aplicación académica en Python + Streamlit que representa una red como grafo, permite construir topologías, simular fallos, calcular rutas de menor latencia y estudiar la criticidad y la resiliencia de los dispositivos.

## 1. Requisitos

- Python 3.10 o superior.
- Internet la primera vez (para instalar dependencias).
- Windows, Linux o macOS.

## 2. Ejecución

**Windows:** doble clic en `iniciar_netsim.bat`.

**Terminal:**

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Si `python` no funciona en Windows, usa `py -m pip ...` y `py -m streamlit run app.py`.

## 3. Novedades de esta versión

- **Interfaz oscura renovada:** tema propio, tarjetas de métricas, insignias de estado y gráficos en Plotly.
- **Mapa mejorado:** forma del nodo según el tipo de dispositivo, color según criticidad, ruta resaltada en amarillo, latencias de enlace y 4 disposiciones (resorte, circular, Kamada-Kawai, capas).
- **Fallos al instante:** ya no hace falta pulsar «Aplicar»; incluye botones *Limpiar*, *Aleatorio* y *Peor caso*.
- **Plantillas de topología:** oficina, estrella, anillo, campus con redundancia y malla de routers.
- **Rutas:** ruta óptima más hasta 3 rutas alternativas con su sobrecoste, y matriz de latencias mínimas (mapa de calor).
- **Pestaña de Resiliencia (nueva):** puntos únicos de fallo, enlaces críticos (puentes), índice de resiliencia e impacto de la caída individual de cada dispositivo y enlace.
- **Guardar y cargar topologías** en JSON, además de exportar CSV de criticidad y de enlaces y JSON del escenario.
- **Código ordenado:** la lógica está en `netsim_core.py` y la interfaz en `app.py`.
- Se corrigieron los reinicios de selección de fallos tras borrar elementos y el modelo de ML se entrena una sola vez (caché).

## 4. Cómo usarlo

1. **Mapa:** revisa la topología y el estado del escenario.
2. **Panel lateral → Escenario de fallos:** elige dispositivos y enlaces caídos; el resultado se ve al instante.
3. **Panel lateral → Construir red:** carga una plantilla, añade/edita/elimina dispositivos y conexiones.
4. **Rutas:** elige origen y destino; la ruta se resalta también en el mapa.
5. **Criticidad:** puntuación, nivel e interpretación de cada dispositivo.
6. **Resiliencia:** localiza puntos débiles de la topología base.
7. **Machine Learning:** demostración con árbol de decisión.
8. **Topología y exportación:** inventario, descargas e importación de topologías.

## 5. Metodología

Grafo no dirigido de NetworkX; cada enlace tiene `weight` = latencia en ms. La ruta óptima minimiza la suma de pesos (Dijkstra); las alternativas usan caminos simples ordenados por latencia.

Criticidad:

`0.35 × centralidad de grado + 0.35 × centralidad de intermediación + 0.30 × importancia del tipo`

Umbrales: **Baja** < 0.30 · **Media** 0.30–0.60 · **Alta** ≥ 0.60. Los pesos por tipo están en `PESOS_TIPO` (`netsim_core.py`).

Resiliencia: un *punto único de fallo* es un punto de articulación del grafo; un *enlace crítico* es un puente. El **índice de resiliencia** es el porcentaje de dispositivos que no son punto único de fallo.

## 6. Limitaciones (conviene explicarlas en la memoria)

- No se conecta a equipos reales; las latencias son valores de ejemplo.
- La criticidad es una regla heurística, no una medición validada de riesgo.
- El módulo de ML usa datos sintéticos etiquetados con esa misma regla: sus métricas indican cuánto reproduce el árbol la regla, no que prediga fallos reales.
- El grafo es no dirigido.

## 7. Pruebas recomendadas

1. Inicio: 7 dispositivos y 8 conexiones.
2. Ruta Router → PC 1: Router → Firewall → Switch 1 → PC 1, 6 ms.
3. Desactivar Switch 1: la red se divide en 2 componentes.
4. Cortar Router–Firewall: la red sigue conectada (hay ruta alternativa).
5. Fallo combinado de dispositivo y enlace.
6. Cambiar una latencia (Añadir/editar conexión) y ver cómo cambia la ruta.
7. Resiliencia: Switch 1 y Switch 2 son puntos únicos de fallo (índice 71 %).
8. Exportar la topología a JSON, restablecer e importarla de nuevo.

## 8. Estructura

- `app.py`: interfaz Streamlit.
- `netsim_core.py`: lógica (topologías, criticidad, resiliencia, rutas, import/export).
- `.streamlit/config.toml`: tema oscuro.
- `requirements.txt`: dependencias.
- `iniciar_netsim.bat`: inicio rápido en Windows.
