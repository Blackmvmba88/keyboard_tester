Probador de Teclado

Utilidad pequeña para verificar si las teclas de tu teclado se detectan correctamente.

Modos
- guiado: solicita cada tecla y espera la entrada
- auto: registra pulsaciones de teclas durante N segundos e informa qué teclas esperadas no se detectaron
- simular: usa pynput para simular escritura (útil para probar la simulación de escritura)

Permisos (macOS)
- Debes otorgar permisos de Terminal/Monitoreo de Entrada y Accesibilidad para que el script capture las teclas.

Ejecutar

```bash
python3 -m pip install -r requirements.txt
python3 main.py guiado
```

Hoja de Ruta
------------

- Mejorar GUI: agregar una interfaz de usuario basada en Tkinter o Electron para guiar las pruebas y mostrar un mapa de calor del teclado.
- Mejoras de detección automática: soporte para múltiples diseños (es/US/ISO) y mapeo de posiciones físicas de las teclas.
- CI/pruebas: pruebas unitarias para funciones de análisis/mapeo y una prueba de integración de muestra usando el modo `simular`.
- Exportar/Análisis: permitir exportación CSV (monitor.py) y un pequeño visor para analizar teclas perdidas a lo largo del tiempo.

Script de Monitoreo
-------------------

`monitor.py` registra eventos de presión/liberación de teclas en un archivo CSV e imprime un resumen breve. Ejemplo:

```bash
python3 monitor.py --out keyboard_log.csv --duration 60
```

Notas: otorga permisos de Accesibilidad/Monitoreo de Entrada si lo requiere tu sistema operativo.

BLACKMAMBA TYPE
---------------

El shell de escritura vive en `blackmamba_type/` y puede iniciarse con:

```bash
python3 run_blackmamba_type.py
```

### Iteration 02 — Personalization

Se añadieron funciones para convertir el prototipo en una máquina de escribir personal:

- Temas persistentes: **Mamba**, **Neon**, **Ocean** y **Paper**.
- Dock editable **MY EMOTICONS** con emojis y emoticons de texto.
- Alta y baja de emoticons; la paleta se guarda en `~/.blackmamba_type/settings.json`.
- Doble clic o botón **Insert** para colocar el emoticon en la posición actual del cursor.
- **Focus mode** para ocultar el panel lateral y dejar sólo el área de escritura.
- **Copy all** y **Clear** como acciones rápidas.
- Atajos:
  - `Ctrl+Shift+F`: activar/desactivar Focus mode.
  - `Ctrl+Shift+E`: insertar el emoticon seleccionado.
  - `Ctrl+Shift+T`: cambiar al siguiente tema.
- Se conservan las funciones de Iteration 01: predicción por prefijo, WPM, caracteres por segundo, ahorro de teclas y sparkline de velocidad.

La configuración es local y no requiere cuenta ni servicio externo.
