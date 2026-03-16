#!/bin/bash

# Beats PM Antigravity - Link Healing Protocol
# Ensures all orchestration entry points (.agent, .agents, .gemini, etc.) 
# are correctly cross-linked using RELATIVE symlinks for maximum compatibility.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR" || exit

echo "🚀 Activating Link Healing Protocol..."

# Source of Truth
SOURCE=".agent"

if [ ! -d "$SOURCE" ]; then
    echo "❌ Error: Source directory $SOURCE not found!"
    exit 1
fi

# 1. Ensure Root Entry Points
for target in ".agents" "_agent" "_agents"; do
    if [ -L "$target" ]; then
        rm "$target"
    elif [ -d "$target" ]; then
        echo "⚠️ $target is a directory. Backing up and converting to symlink..."
        mv "$target" "${target}_backup_$(date +%s)"
    fi
    ln -s "$SOURCE" "$target"
    echo "✅ Linked $target -> $SOURCE"
done

# 2. Ensure .gemini Internal Links (Relative to .gemini dir)
cd .gemini || exit
echo "📂 Synchronizing .gemini orchestration..."

links=(
    "GEMINI.md:../.agent/rules/GEMINI.md"
    "agents:../.agent/agents"
    "skills:../.agent/skills"
    "templates:../.agent/templates"
    "workflows:../.agent/workflows"
)

for link in "${links[@]}"; do
    name="${link%%:*}"
    path="${link#*:}"
    
    if [ -L "$name" ]; then
        rm "$name"
    elif [ -f "$name" ] || [ -d "$name" ]; then
        rm -rf "$name"
    fi
    ln -s "$path" "$name"
    echo "   🔗 $name -> $path"
done

echo "✨ System orchestration is now healthy and synchronized."
