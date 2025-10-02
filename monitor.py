#!/usr/bin/env python3
"""
Keyboard monitor

Logs key press/release events to a CSV file with timestamps and provides a short summary.

Usage:
  python3 monitor.py --out /path/to/log.csv --duration 60

Notes:
- On macOS grant Terminal/Input Monitoring and Accessibility permissions to capture keys.
- Depends on pynput (already in requirements.txt)
"""
import argparse
import csv
import sys
import time
from collections import Counter

try:
    from pynput import keyboard
except Exception:
    print("Missing dependency 'pynput'. Install with: pip install pynput")
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
            self._writer.writerow(['timestamp', 'event', 'key'])

    def on_press(self, key):
        k = key_to_str(key)
        ts = time.time()
        if self._writer is None:
            self._open()
            # if appending and file empty, write header
            if self.append:
                try:
                    self._file.seek(0, 2)
                    if self._file.tell() == 0:
                        self._writer.writerow(['timestamp', 'event', 'key'])
                except Exception:
                    pass
        self._writer.writerow([ts, 'press', k])
        self.counts[k] += 1

    def on_release(self, key):
        k = key_to_str(key)
        ts = time.time()
        if self._writer is None:
            self._open()
        self._writer.writerow([ts, 'release', k])

    def close(self):
        if self._file:
            try:
                self._file.flush()
                self._file.close()
            except Exception:
                pass

    def summary(self, top=20):
        elapsed = time.time() - self.start
        print('\nKeyboard monitor summary:')
        print(f'  elapsed: {elapsed:.1f}s')
        print(f'  unique keys pressed: {len(self.counts)}')
        for k, c in self.counts.most_common(top):
            print(f'    {k}: {c}')


def main():
    parser = argparse.ArgumentParser(description='Keyboard event logger (CSV)')
    parser.add_argument('--out', '-o', default='keyboard_log.csv', help='Output CSV path')
    parser.add_argument('--duration', '-d', type=int, default=0, help='Duration in seconds (0 = indefinite)')
    parser.add_argument('--append', action='store_true', help='Append to output if exists')
    args = parser.parse_args()

    logger = KeyLogger(args.out, append=args.append)
    listener = keyboard.Listener(on_press=logger.on_press, on_release=logger.on_release)
    listener.start()
    print(f'Started keyboard monitor. Logging to {args.out}. Press ESC to stop early.')
    t0 = time.time()
    try:
        while True:
            if args.duration > 0 and (time.time() - t0) >= args.duration:
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\nInterrupted by user')
    finally:
        listener.stop()
        logger.close()
        logger.summary()


if __name__ == '__main__':
    main()
