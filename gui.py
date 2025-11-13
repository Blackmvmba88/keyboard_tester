#!/usr/bin/env python3
"""
GUI del Probador de Teclado (Tkinter)

Características:
- Mapa visual del teclado (QWERTY simple) dibujado en un Canvas
- Resalta teclas cuando se presionan (usa listener de pynput en segundo plano)
- Prueba guiada: muestra la próxima tecla a presionar y marca OK/FALTA
- Exporta resultados a CSV

Ejecutar:
  python3 gui.py

Permisos:
- En macOS otorga permisos de Monitoreo de Entrada/Accesibilidad al terminal o a la aplicación Python.
"""
import sys
import threading
import time
import csv
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except Exception:
    print('Tkinter no está disponible. En algunos sistemas instala python3-tk o usa el Python del sistema.')
    raise

try:
    from pynput import keyboard
except Exception:
    print("Falta la dependencia 'pynput'. Instalar con: pip install pynput")
    raise

# Distribución QWERTY simple por filas (etiquetas)
LAYOUT = [
    ['ESC','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'],
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','BACK'],
    ['TAB','Q','W','E','R','T','Y','U','I','O','P','[',']','\\'],
    ['CAPS','A','S','D','F','G','H','J','K','L',';',"'",'ENTER'],
    ['SHIFT','Z','X','C','V','B','N','M',',','.','/','SHIFT'],
    ['CTRL','META','ALT','SPACE','ALT','META','MENU','CTRL']
]

# mapeo de etiqueta a id de rectángulo en canvas
key_rects = {}
key_labels = {}
pressed_counts = {}

class KeyboardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GUI del Probador de Teclado')
        self.geometry('1000x400')
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill='both', expand=True)
        self.status = tk.StringVar(value='Inactivo')
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side='bottom', fill='x')
        ttk.Label(self.toolbar, textvariable=self.status).pack(side='left', padx=6)
        ttk.Button(self.toolbar, text='Iniciar Guiado', command=self.start_guided).pack(side='right', padx=6)
        ttk.Button(self.toolbar, text='Exportar CSV', command=self.export_csv).pack(side='right')
        self._draw_keyboard()
        self.listener = None
        self.running = True
        self.guided_thread = None
        self.guided_queue = []
        self.results = []
        # iniciar listener en segundo plano
        self._start_listener()

    def _draw_keyboard(self):
        # dibujo de distribución con tamaños simples
        w = self.canvas.winfo_width() or 1000
        h = self.canvas.winfo_height() or 300
        x = 10
        y = 10
        key_w = 60
        key_h = 40
        spacing = 6
        key_rects.clear()
        key_labels.clear()
        for row in LAYOUT:
            x = 10
            for label in row:
                lw = key_w
                if label in ('TAB','CAPS','SHIFT','ENTER','SPACE','BACK','CTRL','ALT','META','MENU'):
                    if label == 'SPACE':
                        lw = key_w * 6
                    else:
                        lw = int(key_w * 1.5)
                rect = self.canvas.create_rectangle(x, y, x+lw, y+key_h, fill='#222', outline='#666')
                text = self.canvas.create_text(x+lw/2, y+key_h/2, text=label, fill='white')
                key_rects[label.upper()] = rect
                key_labels[label.upper()] = text
                pressed_counts[label.upper()] = 0
                x += lw + spacing
            y += key_h + spacing

    def highlight_key(self, label, color='#0f0'):
        L = label.upper()
        if L in key_rects:
            self.canvas.itemconfig(key_rects[L], fill=color)
            # después de un breve retraso quitar el resaltado
            self.after(150, lambda: self.canvas.itemconfig(key_rects[L], fill='#222'))

    def _on_press_gui(self, key_str):
        # ejecutar en hilo GUI
        self.highlight_key(key_str, color='#0a0')
        pressed_counts[key_str.upper()] = pressed_counts.get(key_str.upper(), 0) + 1
        self.status.set(f'Última: {key_str}')

    def _start_listener(self):
        def on_press(key):
            try:
                k = key.char if hasattr(key, 'char') and key.char is not None else f'Key.{key.name}'
            except Exception:
                k = str(key)
            # enviar al hilo GUI
            self.after(0, lambda ks=k: self._on_press_gui(ks))
            # también agregar a la cola guiada si está activa
            if self.guided_queue is not None:
                self.guided_queue.append(k)

        def run_listener():
            with keyboard.Listener(on_press=on_press) as listener:
                self.listener = listener
                listener.join()

        t = threading.Thread(target=run_listener, daemon=True)
        t.start()

    def start_guided(self):
        if self.guided_thread and self.guided_thread.is_alive():
            messagebox.showinfo('Guiado', 'La prueba guiada ya está en ejecución')
            return
        # construir una secuencia de teclas para probar
        seq = []
        for row in LAYOUT:
            for label in row:
                seq.append(label)
        self.guided_queue = []
        self.results = []
        self.guided_thread = threading.Thread(target=self._run_guided, args=(seq,), daemon=True)
        self.guided_thread.start()

    def _run_guided(self, seq):
        for label in seq:
            # solicitar en GUI
            self.after(0, lambda lab=label: self.status.set(f'Presiona: {lab}'))
            # esperar hasta 5 segundos por esa tecla
            found = False
            t0 = time.time()
            while time.time() - t0 < 5:
                # verificar guided_queue
                for k in list(self.guided_queue):
                    if k is None:
                        continue
                    if self._label_matches(label, k):
                        found = True
                        break
                if found:
                    break
                time.sleep(0.05)
            self.results.append((label, 'OK' if found else 'FALTA'))
            # marca visual
            self.after(0, lambda lab=label, ok=found: self._mark_result(lab, ok))
            # limpiar cola
            self.guided_queue.clear()
            time.sleep(0.2)
        # finalizado
        self.after(0, lambda: self.status.set('Prueba guiada finalizada'))
        # mostrar resumen
        ok = sum(1 for _,r in self.results if r=='OK')
        total = len(self.results)
        self.after(0, lambda: messagebox.showinfo('Finalizado', f'OK {ok}/{total}'))

    def _label_matches(self, label, observed):
        # normalizar
        lab = label.upper()
        obs = str(observed)
        if lab == 'BACK' and obs in ('Key.backspace','\x7f'):
            return True
        if lab == 'SPACE' and obs in (' ', 'Key.space'):
            return True
        if lab == 'ENTER' and obs in ('\n','\r','Key.enter'):
            return True
        # coincidencia directa de carácter
        if len(lab) == 1 and obs.lower() == lab.lower():
            return True
        # coincidencia key.Name
        if obs.startswith('Key.') and lab in obs.upper():
            return True
        return False

    def _mark_result(self, label, ok):
        L = label.upper()
        if L in key_rects:
            color = '#0a0' if ok else '#a00'
            self.canvas.itemconfig(key_rects[L], fill=color)
            self.after(800, lambda: self.canvas.itemconfig(key_rects[L], fill='#222'))

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['tecla','cantidad'])
            for k,c in pressed_counts.items():
                writer.writerow([k,c])
        messagebox.showinfo('Exportar', f'Exportado a {path}')

    def on_close(self):
        if messagebox.askokcancel('Salir', '¿Salir?'):
            try:
                if self.listener:
                    self.listener.stop()
            except Exception:
                pass
            self.running = False
            self.destroy()


if __name__ == '__main__':
    app = KeyboardGUI()
    app.mainloop()
