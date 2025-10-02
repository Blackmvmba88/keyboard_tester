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
