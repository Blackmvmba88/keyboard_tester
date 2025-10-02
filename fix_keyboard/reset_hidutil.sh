#!/usr/bin/env bash
# Reset any user HID keyboard mappings on macOS (hidutil)
# This will remove any remaps created via hidutil and restore default mapping.
# Run in Terminal on macOS.

set -euo pipefail
if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script is for macOS (Darwin) only." >&2
  exit 2
fi

echo "Resetting HID keyboard mappings..."
# clear any user mappings
hidutil property --set '{"UserKeyMapping": []}'

echo "Done. If keys still misbehave, try unplugging/replugging the keyboard or rebooting."