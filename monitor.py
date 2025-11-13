#!/usr/bin/env python3
"""
Monitor de teclado

Registra eventos de presión/liberación de teclas en un archivo CSV con marcas de tiempo y proporciona un resumen breve.

Uso:
  python3 monitor.py --out /ruta/a/log.csv --duration 60

Notas:
- En macOS otorga permisos de Terminal/Monitoreo de Entrada y Accesibilidad para capturar teclas.
- Depende de pynput (ya está en requirements.txt)
"""
import argparse
import csv
import sys
import time
from collections import Counter

try:
    from pynput import keyboard
except Exception:
    print("Falta la dependencia 'pynput'. Instalar con: pip install pynput")
    raise


def key_to_str(key):
    try:
        if isinstance(key, keyboard.KeyCode):
            return key.char if getattr(key, 'char', None) is not None else str(key)
        else:
            return f'Key.{key.name}' if hasattr(key, 'name') else str(key)
    except Exception:
        return str(key)


class KeyLogger:
    def __init__(self, out_path, append=True):
        self.out_path = out_path
        self.append = append
        self.counts = Counter()
        self.start = time.time()
        self._file = None
        self._writer = None

    def _open(self):
        mode = 'a' if self.append else 'w'
        self._file = open(self.out_path, mode, newline='')
        self._writer = csv.writer(self._file)
        if not self.append:
            self._writer.writerow(['marca_tiempo', 'evento', 'tecla'])

    def on_press(self, key):
        k = key_to_str(key)
        ts = time.time()
        if self._writer is None:
            self._open()
            # si se está agregando y el archivo está vacío, escribir encabezado
            if self.append:
                try:
                    self._file.seek(0, 2)
                    if self._file.tell() == 0:
                        self._writer.writerow(['marca_tiempo', 'evento', 'tecla'])
                except Exception:
                    pass
        self._writer.writerow([ts, 'presion', k])
        self.counts[k] += 1

    def on_release(self, key):
        k = key_to_str(key)
        ts = time.time()
        if self._writer is None:
            self._open()
        self._writer.writerow([ts, 'liberacion', k])

    def close(self):
        if self._file:
            try:
                self._file.flush()
                self._file.close()
            except Exception:
                pass

    def summary(self, top=20):
        elapsed = time.time() - self.start
        print('\nResumen del monitor de teclado:')
        print(f'  tiempo transcurrido: {elapsed:.1f}s')
        print(f'  teclas únicas presionadas: {len(self.counts)}')
        for k, c in self.counts.most_common(top):
            print(f'    {k}: {c}')


def main():
    parser = argparse.ArgumentParser(description='Registrador de eventos de teclado (CSV)')
    parser.add_argument('--out', '-o', default='keyboard_log.csv', help='Ruta del archivo CSV de salida')
    parser.add_argument('--duration', '-d', type=int, default=0, help='Duración en segundos (0 = indefinido)')
    parser.add_argument('--append', action='store_true', help='Agregar a la salida si existe')
    args = parser.parse_args()

    logger = KeyLogger(args.out, append=args.append)
    listener = keyboard.Listener(on_press=logger.on_press, on_release=logger.on_release)
    listener.start()
    print(f'Monitor de teclado iniciado. Registrando en {args.out}. Presiona ESC para detener antes.')
    t0 = time.time()
    try:
        while True:
            if args.duration > 0 and (time.time() - t0) >= args.duration:
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\nInterrumpido por el usuario')
    finally:
        listener.stop()
        logger.close()
        logger.summary()


if __name__ == '__main__':
    main()
