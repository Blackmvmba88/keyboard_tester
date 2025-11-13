#!/usr/bin/env python3
"""
Probador de teclado

Uso:
  python3 main.py guiado   # modo guiado: el script te pide presionar cada tecla
  python3 main.py auto     # modo auto: presiona cualquier tecla durante N segundos para detectar teclas faltantes
  python3 main.py simular  # opcional: el programa simulará escritura (usa pynput.Controller)

Notas:
- En macOS debes otorgar permisos de Accesibilidad / Monitoreo de Entrada al terminal ejecutando este script.
- Instalar dependencias: pip install -r requirements.txt
"""

import sys
import time
import threading
from collections import defaultdict

try:
    from pynput import keyboard
except Exception as e:
    print("Falta la dependencia 'pynput'. Instalar con: pip install pynput")
    raise

# lista de teclas que verificaremos (etiquetas)
LETTER_KEYS = [chr(c) for c in range(ord('A'), ord('Z')+1)]
DIGIT_KEYS = [str(d) for d in range(0, 10)]
SPECIAL_KEYS = [
    'space', 'enter', 'tab', 'backspace', 'escape',
    'left', 'right', 'up', 'down',
]
FUNCTION_KEYS = [f'F{i}' for i in range(1, 13)]

# construir mapa de teclas esperadas: etiqueta -> conjunto de representaciones aceptables
def build_expected_map():
    m = {}
    for L in LETTER_KEYS:
        m[L] = {L.lower(), L.upper()}
    for d in DIGIT_KEYS:
        m[d] = {d}
    m['space'] = {'Key.space', ' '}
    m['enter'] = {'Key.enter', '\n', '\r'}
    m['tab'] = {'Key.tab', '\t'}
    m['backspace'] = {'Key.backspace'}
    m['escape'] = {'Key.esc', 'Key.escape', 'esc', '\x1b'}
    m['left'] = {'Key.left'}
    m['right'] = {'Key.right'}
    m['up'] = {'Key.up'}
    m['down'] = {'Key.down'}
    for k in FUNCTION_KEYS:
        m[k] = {f'Key.{k.lower()}', k}
    return m

EXPECTED = build_expected_map()

# función auxiliar para convertir una tecla pynput a cadena
def key_to_str(key):
    try:
        if isinstance(key, keyboard.KeyCode):
            # key.char puede ser None para algunas teclas; usar str(key) como alternativa
            return key.char if getattr(key, 'char', None) is not None else str(key)
        else:
            # Objeto Key (teclas especiales)
            return f'Key.{key.name}' if hasattr(key, 'name') else str(key)
    except Exception:
        return str(key)

# Estado del listener
last_key = None
key_event = threading.Event()
pressed_keys = defaultdict(int)

def on_press(key):
    global last_key
    k = key_to_str(key)
    last_key = k
    pressed_keys[k] += 1
    key_event.set()

def guided_mode():
    print('MODO GUIADO: Para cada solicitud, presiona la tecla indicada. Presiona CTRL+C para cancelar.')
    time.sleep(0.2)
    all_labels = LETTER_KEYS + DIGIT_KEYS + SPECIAL_KEYS + FUNCTION_KEYS
    ok = []
    mismatch = []
    # reiniciar estado del listener
    pressed_keys.clear()
    global last_key
    last_key = None
    key_event.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        try:
            for label in all_labels:
                print('\nPor favor presiona:', label)
                key_event.clear()
                # esperar una pulsación de tecla
                key_event.wait()
                got = last_key
                expected = EXPECTED.get(label, {label})
                print('Recibido:', repr(got))
                if got in expected:
                    ok.append(label)
                    print('OK')
                else:
                    mismatch.append((label, got))
                    print('No coincide: se esperaba uno de', expected)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print('\nCancelado por el usuario')
        finally:
            listener.stop()
    print_summary(ok, mismatch)

def auto_mode(duration=20):
    print(f'MODO AUTO: Presiona cualquier tecla durante {duration} segundos. Presiona ESC para finalizar antes.')
    time.sleep(0.2)
    # reiniciar estado
    pressed_keys.clear()
    global last_key
    last_key = None
    key_event.clear()

    with keyboard.Listener(on_press=on_press) as listener:
        t0 = time.time()
        try:
            while True:
                if key_event.wait(timeout=0.1):
                    key_event.clear()
                    # si se presiona escape, finalizar antes
                    if last_key and (str(last_key).lower() in ('key.esc', 'key.escape', 'esc', '\x1b')):
                        print('Escape presionado — finalizando antes')
                        break
                if time.time() - t0 >= duration:
                    break
        except KeyboardInterrupt:
            print('\nCancelado por el usuario')
        finally:
            listener.stop()
    # calcular qué teclas esperadas fueron presionadas
    # filtrar None y normalizar
    pressed_set = set(k for k in pressed_keys.keys() if k is not None)
    ok = []
    missing = []
    for label, expected in EXPECTED.items():
        if pressed_set & expected:
            ok.append(label)
        else:
            missing.append(label)
    print('\nRESULTADOS:')
    print('Teclas presionadas detectadas (muestra):', list(pressed_set)[:30])
    print('OK:', ok)
    print('FALTANTES:', missing)

def simulate_mode(text='El veloz murciélago hindú comía feliz cardillo y kiwi\n'):
    print('MODO SIMULAR: El programa escribirá texto de muestra (puedes verlo en la ventana activa).')
    from pynput.keyboard import Controller
    kb = Controller()
    time.sleep(1.0)
    kb.type(text)
    print('Escritura de texto de muestra completada.')

def print_summary(ok, mismatch):
    print('\nRESUMEN:')
    print('Teclas OK:', ok)
    if mismatch:
        print('No coinciden (esperado -> recibido):')
        for exp, got in mismatch:
            print(f'  {exp} -> {got}')

def main():
    if len(sys.argv) < 2:
        print('Uso: python3 main.py [guiado|auto|simular]')
        return
    mode = sys.argv[1]
    if mode in ('guiado', 'guided'):
        guided_mode()
    elif mode == 'auto':
        dur = 20
        if len(sys.argv) >= 3:
            try:
                dur = int(sys.argv[2])
            except Exception:
                pass
        auto_mode(duration=dur)
    elif mode in ('simular', 'simulate'):
        simulate_mode()
    else:
        print('Modo desconocido:', mode)

if __name__ == '__main__':
    main()
