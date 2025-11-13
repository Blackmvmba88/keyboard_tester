#!/usr/bin/env bash
# Restablecer cualquier mapeo de teclado HID de usuario en macOS (hidutil)
# Esto eliminará cualquier remapeo creado a través de hidutil y restaurará el mapeo predeterminado.
# Ejecutar en Terminal en macOS.

set -euo pipefail
if [[ "$(uname)" != "Darwin" ]]; then
  echo "Este script es solo para macOS (Darwin)." >&2
  exit 2
fi

echo "Restableciendo mapeos de teclado HID..."
# limpiar cualquier mapeo de usuario
hidutil property --set '{"UserKeyMapping": []}'

echo "Hecho. Si las teclas aún no funcionan correctamente, intenta desconectar/reconectar el teclado o reiniciar."