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

## 3. Contenido de esta versión

- **Siete pestañas:** Mapa, Rutas, Criticidad, Resiliencia, Formación, Aprendizaje automático y Topología y exportación.
- **Modo día y modo noche** conmutables desde *Configuración → Apariencia*. El tema se aplica por CSS y, en las tablas (que Glide pinta en un lienzo), alineando el tema nativo de Streamlit en cada ejecución.
- **Mapa:** forma del nodo según el tipo de dispositivo, color según criticidad, ruta resaltada y 4 disposiciones (resorte, circular, Kamada-Kawai y capas).
- **Fallos al instante:** sin botón *Aplicar*; incluye *Limpiar*, *Aleatorio* y *Peor caso*.
- **Plantillas de topología:** oficina pequeña, estrella, anillo, campus con redundancia y malla de routers.
- **Rutas:** ruta óptima más hasta 3 alternativas con su sobrecoste, y matriz de latencias mínimas (mapa de calor).
- **Resiliencia:** puntos únicos de fallo, enlaces críticos (puentes), índice de resiliencia e impacto de la caída individual de cada dispositivo y enlace.
- **Formación:** 6 lecciones, 5 retos con solución y pistas, 8 preguntas de autoevaluación y glosario de 17 términos.
- **Exportación:** topología e escenario en JSON, criticidad y enlaces en CSV e informe HTML imprimible a PDF.
- **Código por módulos:** `netsim_core` (lógica), `netsim_ml` (árbol de decisión), `netsim_edu` (contenido formativo), `netsim_estilos` (CSS y temas), `netsim_js` (animaciones e interacción) y `netsim_informe` (informe).

## 4. Cómo usarlo

1. **Mapa:** revisa la topología y el estado del escenario.
2. **Panel lateral → Escenario de fallos:** elige dispositivos y enlaces caídos; el resultado se ve al instante.
3. **Panel lateral → Construir red:** carga una plantilla, añade/edita/elimina dispositivos y conexiones.
4. **Rutas:** elige origen y destino; la ruta se resalta también en el mapa.
5. **Criticidad:** puntuación, nivel e interpretación de cada dispositivo.
6. **Resiliencia:** localiza puntos débiles de la topología base.
7. **Formación:** lecciones, retos con su solución y autoevaluación.
8. **Aprendizaje automático:** demostración con árbol de decisión sobre datos sintéticos.
9. **Topología y exportación:** inventario, descargas e importación de topologías.
10. **Configuración → Apariencia:** modo noche, latencias, resaltado de ruta y animaciones.

## 5. Metodología

Grafo no dirigido de NetworkX; cada enlace tiene `weight` = latencia en ms. La ruta óptima minimiza la suma de pesos (Dijkstra); las alternativas usan caminos simples ordenados por latencia.

Criticidad:

`0.35 × centralidad de grado + 0.35 × centralidad de intermediación + 0.30 × importancia del tipo`

Umbrales: **Baja** < 0.30 · **Media** 0.30–0.60 · **Alta** ≥ 0.60. Los pesos por tipo están en `PESOS_TIPO` (`netsim_core.py`).

Resiliencia: un *punto único de fallo* es un punto de articulación del grafo; un *enlace crítico* es un puente. El **índice de resiliencia** es el porcentaje de dispositivos que no son punto único de fallo.

## 6. Limitaciones (conviene explicarlas en la memoria)

- No se conecta a equipos reales; las latencias son valores de ejemplo.
- La criticidad es una regla heurística, no una medición validada de riesgo.
- El módulo de aprendizaje automático usa datos sintéticos etiquetados con esa misma regla: sus métricas indican cuánto reproduce el árbol la regla, no que prediga fallos reales.
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

- `app.py`: interfaz Streamlit (pestañas, panel lateral y mapa).
- `netsim_core.py`: lógica (topologías, criticidad, resiliencia, rutas, import/export).
- `netsim_ml.py`: generación de datos sintéticos y entrenamiento del árbol de decisión.
- `netsim_edu.py`: contenido de Formación (lecciones, retos, cuestionario, glosario y ayuda).
- `netsim_estilos.py`: temas día/noche y hojas CSS.
- `netsim_js.py`: animaciones e interacción inyectadas en el navegador.
- `netsim_informe.py`: informe HTML imprimible del escenario.
- `.streamlit/config.toml`: tema por defecto (modo día), estadísticas desactivadas y `toolbarMode = "minimal"` (sin Stop, Deploy ni menú ⋮ arriba a la derecha). Streamlit Cloud añade además sus botones «Fork» y «source», que `minimal` no toca porque los inyecta la plataforma; esos dos los oculta la regla `[data-testid="stToolbar"]` de `netsim_estilos.py`.
- `requirements.txt`: dependencias.
- `iniciar_netsim.bat`: inicio rápido en Windows (abre el navegador).
- `escritorio/`: lanzador, spec de PyInstaller, icono, script de construcción y guion del instalador (`NetSim.iss`).

## 9. Despliegue web

En Streamlit Cloud o Render, sube la carpeta tal cual (incluida `.streamlit/`) y señala `app.py` como punto de entrada. `requirements.txt` fija `streamlit==1.66.1` a propósito: las animaciones de `netsim_js.py` se probaron contra el DOM de esa versión y una actualización puede descolgarlas.

Render se reconstruye solo con cada push. Streamlit Cloud no siempre: si el cambio va solo en un módulo (`netsim_estilos.py`, `netsim_edu.py`…) puede seguir sirviendo la imagen anterior, y el «Reboot» tampoco vuelve a leer el repo. En ese caso, desde el panel de la app: **Manage app → Redeploy → Clear cache and redeploy**.

## 10. Versión de escritorio (Windows)

NetSim también se empaqueta como programa con ventana propia, sin pestaña de navegador y sin nube. El código está en `escritorio/`:

- `netsim_escritorio.py`: lanzador. Abre una ventana WebView2 (el motor de Edge, ya presente en Windows) y ejecuta Streamlit en un proceso hijo; al cerrar la ventana termina el servidor. Elige un puerto libre y el servidor solo escucha en `127.0.0.1`. Antes de abrir nada comprueba en el registro si WebView2 está instalado; si falta, lo dice en un cuadro de diálogo con el enlace oficial en vez de mostrar una ventana vacía.
- `NetSim.spec`: configuración de PyInstaller. Genera una carpeta `dist/NetSim/`, no un archivo único: onefile desempaleta en cada arranque y Streamlit tarda decenas de segundos.
- `construir_netsim.bat`: compila el ejecutable y crea el acceso directo del Escritorio. Sirve para probar en su propio equipo, pero `dist/NetSim/` es una carpeta: no se puede repartir solo el `.exe`.
- `NetSim.iss` + `construir_instalador.bat`: el instalador para repartir. Congela la app y la comprime en un único `dist/NetSim-1.0-Instalador.exe` (135 MB; ocupa unos 500 MB instalado).

Arranque y registro del servidor: `%LOCALAPPDATA%\NetSim\` (`servidor.log` y `error.log`). El ejecutable se congela sin consola, así que un fallo de arranque solo se ve ahí.

## 11. Instalador para repartir

```bash
python -m pip install pyinstaller pywebview
winget install JRSoftware.InnoSetup
escritorio\construir_instalador.bat
```

Qué obtiene quien lo reciba: asistente en español, elección de carpeta, acceso directo en el menú Inicio (y opcionalmente en el Escritorio), entrada propia en «Aplicaciones instaladas» con su desinstalador, y opción de instalar «solo para mí» sin ser administrador. Al terminar ofrece abrir NetSim.

Pruebas hechas sobre el instalador final: instalación silenciosa por usuario, arranque del programa instalado (ventana propia, `/_stcore/health` en `ok` e interfaz renderizada) y desinstalación limpia — carpeta, accesos del menú Inicio y clave de registro desaparecen sin dejar rastro.

Cosas a tener en cuenta al repartirlo:

- No está firmado. Windows mostrará «SmartScreen ha protegido a la aplicación… No se puede abrir»; hay que pulsar «Más información» → «Ejecutar de todas formas». Firmar cuesta un certificado; si son muchos equipos, la alternativa es pedir al responsable de TI que lo apruebe.
- Antivirus: un ejecutable congelado de PyInstaller con 10 000 archivos dentro suele dar falsos positivos. Si a alguien le bloquea, se añade la carpeta a excepciones.
- Necesita Windows 10 u 11 de 64 bits y el entorno WebView2 (viene con las actualizaciones de Edge). No hace falta instalar Python ni tener internet.
- La primera pantalla puede tardar unos segundos: el servidor arranca en local.

