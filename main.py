#!/usr/bin/env python3
"""
Keyboard tester

Usage:
  python3 main.py guided   # guided mode: the script asks you to press each key
  python3 main.py auto     # auto mode: press any keys for N seconds to detect missing keys
  python3 main.py simulate # optional: the program will simulate typing (uses pynput.Controller)

Notes:
- On macOS you must grant Accessibility / Input Monitoring permissions to the terminal running this script.
- Install dependencies: pip install -r requirements.txt
"""

import sys
import time
import threading
from collections import defaultdict

try:
    from pynput import keyboard
except Exception as e:
    print("Missing dependency 'pynput'. Install with: pip install pynput")
    raise

# list of keys we'll check (labels)
LETTER_KEYS = [chr(c) for c in range(ord('A'), ord('Z')+1)]
DIGIT_KEYS = [str(d) for d in range(0, 10)]
SPECIAL_KEYS = [
    'space', 'enter', 'tab', 'backspace', 'escape',
    'left', 'right', 'up', 'down',
]
FUNCTION_KEYS = [f'F{i}' for i in range(1, 13)]

# build expected key map: label -> set of acceptable representations
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

# helper to stringify a pynput key
def key_to_str(key):
    if isinstance(key, keyboard.KeyCode):
        return key.char
    else:
        # Key object
        return f'Key.{key.name}' if hasattr(key, 'name') else str(key)

# Listener state
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
    print('GUIDED MODE: For each prompt, press the requested key. Press CTRL+C to abort.')
    time.sleep(0.2)
    all_labels = LETTER_KEYS + DIGIT_KEYS + SPECIAL_KEYS + FUNCTION_KEYS
    ok = []
    mismatch = []
    with keyboard.Listener(on_press=on_press) as listener:
        try:
            for label in all_labels:
                print('\nPlease press:', label)
                key_event.clear()
                # wait for a key press
                key_event.wait()
                got = last_key
                expected = EXPECTED.get(label, {label})
                print('Got:', repr(got))
                if got in expected:
                    ok.append(label)
                    print('OK')
                else:
                    mismatch.append((label, got))
                    print('Mismatch: expected one of', expected)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print('\nAborted by user')
        finally:
            listener.stop()
    print_summary(ok, mismatch)

def auto_mode(duration=20):
    print(f'AUTO MODE: Press any keys for {duration} seconds. Press ESC to finish early.')
    time.sleep(0.2)
    with keyboard.Listener(on_press=on_press) as listener:
        t0 = time.time()
        try:
            while True:
                if key_event.wait(timeout=0.1):
                    key_event.clear()
                    # if escape pressed, finish early
                    if last_key and (last_key.lower() in ('key.esc', 'key.escape', 'esc', '\x1b')):
                        print('Escape pressed — finishing early')
                        break
                if time.time() - t0 >= duration:
                    break
        except KeyboardInterrupt:
            print('\nAborted by user')
        finally:
            listener.stop()
    # compute which expected keys were pressed
    pressed_set = set(pressed_keys.keys())
    ok = []
    missing = []
    for label, expected in EXPECTED.items():
        if pressed_set & expected:
            ok.append(label)
        else:
            missing.append(label)
    print('\nRESULTS:')
    print('Detected pressed keys (sample):', list(pressed_set)[:30])
    print('OK:', ok)
    print('MISSING:', missing)

def simulate_mode(text='The quick brown fox jumps over the lazy dog\n'):
    print('SIMULATE MODE: The program will type some sample text (you may see it in the active window).')
    from pynput.keyboard import Controller
    kb = Controller()
    time.sleep(1.0)
    kb.type(text)
    print('Done typing sample text.')

def print_summary(ok, mismatch):
    print('\nSUMMARY:')
    print('OK keys:', ok)
    if mismatch:
        print('Mismatches (expected -> got):')
        for exp, got in mismatch:
            print(f'  {exp} -> {got}')

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 main.py [guided|auto|simulate]')
        return
    mode = sys.argv[1]
    if mode == 'guided':
        guided_mode()
    elif mode == 'auto':
        dur = 20
        if len(sys.argv) >= 3:
            try:
                dur = int(sys.argv[2])
            except Exception:
                pass
        auto_mode(duration=dur)
    elif mode == 'simulate':
        simulate_mode()
    else:
        print('Unknown mode:', mode)

if __name__ == '__main__':
    main()
