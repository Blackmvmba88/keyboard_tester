#!/usr/bin/env bash
# Aplicar un remapeo de ejemplo seguro usando hidutil en macOS: convertir BloqMayús -> Control
# Para revertir, ejecuta reset_hidutil.sh

set -euo pipefail
if [[ "$(uname)" != "Darwin" ]]; then
  echo "Este script es solo para macOS (Darwin)." >&2
  exit 2
fi

# Mapeo: Bloq Mayús (0x700000039) -> Control Izquierdo (0x7000000e0)
MAP='{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000039,"HIDKeyboardModifierMappingDst":0x7000000e0}]}'
echo "Aplicando remapeo: BloqMayús -> Control Izquierdo"
hidutil property --set "$MAP"
echo "Aplicado. Para revertir ejecuta reset_hidutil.sh"