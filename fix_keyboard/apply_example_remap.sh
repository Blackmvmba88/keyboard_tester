#!/usr/bin/env bash
# Apply a safe example remap using hidutil on macOS: make CapsLock -> Control
# To revert, run reset_hidutil.sh

set -euo pipefail
if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script is for macOS (Darwin) only." >&2
  exit 2
fi

# Mapping: Caps Lock (0x700000039) -> Left Control (0x7000000e0)
MAP='{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000039,"HIDKeyboardModifierMappingDst":0x7000000e0}]}'
echo "Applying remap: CapsLock -> Left Control"
hidutil property --set "$MAP"
echo "Applied. To revert run reset_hidutil.sh"