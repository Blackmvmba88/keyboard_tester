Keyboard Tester

Small utility to check whether keys on your keyboard are detected correctly.

Modes
- guided: prompts for each key and waits for input
- auto: record keypresses for N seconds and report which expected keys were not seen
- simulate: uses pynput to simulate typing (useful to test the typing simulation)

Permissions (macOS)
- You must grant the Terminal/Input Monitoring and Accessibility permissions for the script to capture keys.

Run

```bash
python3 -m pip install -r requirements.txt
python3 main.py guided
```

Roadmap
-------

- Improve GUI: add a Tkinter or Electron-based UI to guide tests and show a keyboard heatmap.
- Auto-detection improvements: support multiple layouts (es/US/ISO) and map physical key positions.
- CI/tests: unit tests for parsing/mapping functions and a sample integration test using the `simulate` mode.
- Export/Analysis: allow CSV export (monitor.py) and a small viewer to analyze missed keys over time.

Monitor script
--------------

`monitor.py` logs key press/release events to a CSV file and prints a short summary. Example:

```bash
python3 monitor.py --out keyboard_log.csv --duration 60
```

Notes: grant Accessibility/Input Monitoring permissions if required by your OS.

