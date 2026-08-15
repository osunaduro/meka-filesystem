#!/usr/bin/env bash
# Empaqueta meka-filesystem como extensión .mcpb para Claude Desktop.
# Uso: ./build_mcpb.sh
set -euo pipefail

REPO="/home/martin/Documentos/Documentos-AI/programacion/meka-filesystem"
BUILD_DIR="$HOME/mcpb-bundles/meka-filesystem"
VENV_PY="$REPO/.venv/bin/python"
ENTRY="$REPO/workspace/servers/filesystem_stdio.py"
OUT="meka-filesystem.mcpb"

mkdir -p "$BUILD_DIR"

cat > "$BUILD_DIR/manifest.json" <<EOF
{
  "\$schema": "https://raw.githubusercontent.com/anthropics/mcpb/main/dist/mcpb-manifest.schema.json",
  "manifest_version": "0.1",
  "name": "meka-filesystem",
  "display_name": "MEKA Filesystem",
  "version": "0.1.0",
  "description": "Servidor MCP de filesystem para MEKA Workspace",
  "author": { "name": "Martín" },
  "server": {
    "type": "python",
    "entry_point": "workspace/servers/filesystem_stdio.py",
    "mcp_config": {
      "command": "$VENV_PY",
      "args": ["$ENTRY"]
    }
  }
}
EOF

cd "$BUILD_DIR"

if ! command -v mcpb &> /dev/null; then
  echo "Instalando mcpb CLI..."
  npm install -g @anthropic-ai/mcpb
fi

mcpb pack . "$OUT"

echo ""
echo "Listo: $BUILD_DIR/$OUT"
echo "Para instalar: Claude Desktop -> Settings -> Extensions -> Advanced settings -> Extension Developer -> Install Extension..."
