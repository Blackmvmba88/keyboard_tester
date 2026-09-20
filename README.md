# BLACKMAMBA TYPE / keyboard_tester

Máquina de escribir experimental + probador de teclado.

El repo tiene dos partes:

- **BLACKMAMBA TYPE**: editor local con métricas, autocompletado, temas, emoticons y Focus mode.
- **Keyboard tester**: utilidades para comprobar teclas, registrar eventos y simular escritura.

---

## 🚀 Instalar desde cero

### Requisitos

- Python **3.10 o superior**
- Git
- macOS, Linux o Windows
- En macOS, algunas funciones de captura global con `pynput` pueden pedir permisos de **Accesibilidad** y **Monitoreo de Entrada**.

Comprueba Python:

```bash
python3 --version
```

### 1. Clonar el repo

SSH:

```bash
git clone git@github.com:Blackmvmba88/keyboard_tester.git
cd keyboard_tester
```

o HTTPS:

```bash
git clone https://github.com/Blackmvmba88/keyboard_tester.git
cd keyboard_tester
```

> El repo es privado: GitHub te pedirá una sesión/credencial con acceso.

### 2. Usar la Iteration 02

Mientras el PR #4 no esté fusionado:

```bash
git checkout feat/type-iter-02-personalization
```

Después de fusionarlo, bastará con usar la rama principal correspondiente.

### 3. Crear un entorno virtual

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

macOS / Linux:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Windows:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## ⌨️ Ejecutar BLACKMAMBA TYPE

Desde la raíz del repo:

macOS / Linux:

```bash
python3 run_blackmamba_type.py
```

Windows:

```powershell
python run_blackmamba_type.py
```

Debe abrirse la interfaz gráfica de **BLACKMAMBA TYPE**.

### Qué incluye Iteration 02

- Temas persistentes: **Mamba**, **Neon**, **Ocean** y **Paper**.
- Dock editable **MY EMOTICONS**.
- Emojis y emoticons iniciales como `😂`, `🔥`, `😎`, `xD`, `:D`, `;)` y más.
- Alta, baja e inserción de emoticons propios.
- Configuración local en `~/.blackmamba_type/settings.json`.
- **Focus mode**.
- **Copy all** y **Clear**.
- Predicción por prefijo.
- WPM, palabras, caracteres por segundo y teclas ahorradas.
- Sparkline de velocidad en vivo.

### Atajos

| Atajo | Acción |
|---|---|
| `Ctrl+Shift+F` | Activar/desactivar Focus mode |
| `Ctrl+Shift+E` | Insertar emoticon seleccionado |
| `Ctrl+Shift+T` | Cambiar al siguiente tema |
| `↑ / ↓` | Navegar sugerencias |
| `Tab / Enter` | Aceptar sugerencia |
| `Esc` | Ocultar sugerencias |

---

## 🧪 Ejecutar el probador de teclado

### Modo guiado

```bash
python3 main.py guiado
```

### Modo automático

Consulta las opciones disponibles:

```bash
python3 main.py --help
```

### Monitor de pulsaciones

`monitor.py` registra eventos de presión/liberación y puede exportarlos a CSV:

```bash
python3 monitor.py --out keyboard_log.csv --duration 60
```

### Simulación

El proyecto usa `pynput` para pruebas de simulación de escritura. Consulta:

```bash
python3 main.py --help
```

---

## 🍎 Permisos en macOS

Si el tester o monitor no detecta las teclas globales, permite a tu terminal/Python acceder a:

- **Configuración del Sistema → Privacidad y seguridad → Accesibilidad**
- **Configuración del Sistema → Privacidad y seguridad → Monitoreo de Entrada**

BLACKMAMBA TYPE puede abrir y escribir localmente sin necesitar una cuenta o servicio externo; los permisos anteriores son especialmente relevantes para las utilidades que capturan teclas fuera de la ventana.

---

## 🔄 Volver a ejecutar después

Si ya lo instalaste una vez:

macOS / Linux:

```bash
cd keyboard_tester
source .venv/bin/activate
python3 run_blackmamba_type.py
```

Windows PowerShell:

```powershell
cd keyboard_tester
.\.venv\Scripts\Activate.ps1
python run_blackmamba_type.py
```

Para salir del entorno virtual:

```bash
deactivate
```

---

## 🛠️ Problemas rápidos

### `ModuleNotFoundError: No module named 'PySide6'`

Activa el entorno e instala dependencias otra vez:

```bash
python3 -m pip install -r requirements.txt
```

### La interfaz no abre

Comprueba primero:

```bash
python3 --version
python3 -c "import PySide6; print(PySide6.__version__)"
```

### El monitor no detecta teclas en macOS

Revisa permisos de Accesibilidad y Monitoreo de Entrada, cierra Terminal y vuelve a abrirla después de concederlos.

---

## 📂 Estructura principal

```text
keyboard_tester/
├── blackmamba_type/
│   ├── app.py
│   ├── metrics.py
│   ├── predictor.py
│   └── preferences.py
├── run_blackmamba_type.py
├── main.py
├── monitor.py
├── gui.py
└── requirements.txt
```

---

## Hoja de ruta

- Frases rápidas y snippets personales.
- Combinaciones de emoji/emoticons.
- Diccionario personal aprendido por uso.
- Métricas históricas por sesión/día/mes.
- Modo turbo para estudiar velocidad, ráfagas, correcciones y ahorro de pulsaciones.
- Mejoras de detección automática para múltiples diseños de teclado.
- CI/pruebas automatizadas.
- Exportación y análisis de sesiones.
