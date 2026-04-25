#!/usr/bin/env bash
# ============================================================
# Beats PM Kit — One-Line Installer
# Usage: git clone https://github.com/officebeats/beats-pm-kit && cd beats-pm-kit && chmod +x install.sh && ./install.sh
# ============================================================

set -e

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
BOLD='\033[1m'
RESET='\033[0m'

print_step()  { printf "${CYAN}▸${RESET} %s\n" "$1"; }
print_ok()    { printf "${GREEN}✓${RESET} %s\n" "$1"; }
print_warn()  { printf "${YELLOW}!${RESET} %s\n" "$1"; }
print_skip()  { printf "${GRAY}  [skip]${RESET} %s\n" "$1"; }
print_fail()  { printf "${RED}✗${RESET} %s\n" "$1"; }

# ── Banner ──────────────────────────────────────────────────
echo ""
printf "${BOLD}${CYAN}"
cat << 'BANNER'
  ____             _         ____  __  __ 
 | __ )  ___  __ _| |_ ___  |  _ \|  \/  |
 |  _ \ / _ \/ _` | __/ __| | |_) | |\/| |
 | |_) |  __/ (_| | |_\__ \ |  __/| |  | |
 |____/ \___|\__,_|\__|___/ |_|   |_|  |_|
BANNER
printf "${RESET}"
echo ""
printf "${BOLD}  The AI Operating System for Product Managers${RESET}\n"
echo "  ─────────────────────────────────────────────"
echo ""

# ── Step 1: Check Python ────────────────────────────────────
print_step "Checking Python 3..."
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_ok "Python ${PY_VERSION} found"
else
    print_fail "Python 3 is required but not found. Install it from https://python.org"
    exit 1
fi

# ── Step 2: Check OS ────────────────────────────────────────
print_step "Detecting platform..."
OS="$(uname -s)"
case "$OS" in
    Darwin) PLATFORM="macOS"; print_ok "macOS detected" ;;
    Linux)  PLATFORM="Linux"; print_ok "Linux detected" ;;
    *)      PLATFORM="Unknown"; print_warn "Unsupported OS: $OS (proceeding anyway)" ;;
esac

# ── Step 3: Create folder structure ─────────────────────────
print_step "Creating folder structure..."
yes n | python3 system/scripts/core_setup.py 2>/dev/null || {
    # Fallback: create manually if core_setup fails
    print_warn "core_setup.py had issues — creating folders manually"
    for dir in "0. Incoming/raw" "0. Incoming/processed" "0. Incoming/staging" \
               "0. Incoming/images" "0. Incoming/files" "0. Incoming/fyi" \
               "1. Company" "2. Products" \
               "3. Meetings/transcripts" "3. Meetings/summaries" "3. Meetings/daily-briefs" \
               "4. People" \
               "5. Trackers/critical" "5. Trackers/bugs" "5. Trackers/archive"; do
        mkdir -p "$dir" 2>/dev/null && print_ok "Created $dir" || print_skip "$dir (exists)"
    done
}

# ── Step 4: Create template files if missing ────────────────
print_step "Seeding template files..."

if [ ! -f "5. Trackers/TASK_MASTER.md" ]; then
    cat > "5. Trackers/TASK_MASTER.md" << 'TMEOF'
# 📋 TASK MASTER

> **Last Updated:** $(date +%Y-%m-%d)
> **Owner:** [Your Name]

---

## 🔥 Active Tasks

| Risk | ID | Task | Owner | Due | Notes |
|:----:|:---|:-----|:------|:----|:------|
| — | — | Run `/start` to begin setup | You | Today | 🎉 |

---

## ✅ Completed Tasks

| Completed | ID | Task | Owner |
|:----------|:---|:-----|:------|
| — | — | — | — |

---

*Managed by the Task Manager skill. Use `/track` to update.*
TMEOF
    print_ok "Created TASK_MASTER.md"
else
    print_skip "TASK_MASTER.md (exists)"
fi

if [ ! -f "5. Trackers/critical/boss-requests.md" ]; then
    cat > "5. Trackers/critical/boss-requests.md" << 'BREOF'
# 🔴 Boss Asks

> **Last Updated:** —
> Active requests from your manager.

---

| ID | Request | Source | Due | Status | Notes |
|:---|:--------|:-------|:----|:-------|:------|
| — | — | — | — | — | Run `/start` to configure |

---

*Source of truth for leadership-directed tasks.*
BREOF
    print_ok "Created boss-requests.md"
else
    print_skip "boss-requests.md (exists)"
fi

# ── Step 5: Detect AI runtimes ──────────────────────────────
print_step "Detecting AI runtimes..."
RUNTIMES_FOUND=0

# Antigravity
if [ -d ".agent" ] || [ -n "${ANTIGRAVITY_ROOT:-}" ]; then
    print_ok "Antigravity: Ready (.agent/ detected)"
    RUNTIMES_FOUND=$((RUNTIMES_FOUND + 1))
fi

# Gemini CLI
if command -v gemini &>/dev/null || [ -d ".gemini" ]; then
    print_ok "Gemini CLI: Ready (.gemini/ detected)"
    RUNTIMES_FOUND=$((RUNTIMES_FOUND + 1))
fi

# Claude Code
if command -v claude &>/dev/null || [ -d ".claude" ]; then
    print_ok "Claude Code: Ready (.claude/ detected)"
    RUNTIMES_FOUND=$((RUNTIMES_FOUND + 1))
fi


# OpenAI Codex CLI
if command -v codex &>/dev/null || [ -d ".codex" ]; then
    print_ok "Codex CLI: Ready"
    RUNTIMES_FOUND=$((RUNTIMES_FOUND + 1))
fi

# KiloCode
if [ -d ".kilocode" ]; then
    print_ok "KiloCode: Ready (.kilocode/ detected)"
    RUNTIMES_FOUND=$((RUNTIMES_FOUND + 1))
fi

if [ "$RUNTIMES_FOUND" -eq 0 ]; then
    print_warn "No AI runtimes detected. Install one of: Antigravity, Gemini CLI, Claude Code, Codex CLI"
fi

# ── Step 6: Generate CLI Adapters ─────────────────────────
print_step "Generating CLI Adapters..."
if python3 system/scripts/sync_cli_adapters.py > /dev/null 2>&1; then
    print_ok "Generated adapters for .gemini, .claude, .kilocode, .codex"
else
    print_warn "Could not generate CLI adapters (non-critical)"
fi

# ── Step 6b: Sync promoted Codex skills ───────────────────
print_step "Syncing promoted Codex skill adapters..."
if python3 system/scripts/sync_codex_skill_adapters.py > /dev/null 2>&1; then
    print_ok "Promoted Codex skill adapters synced"
else
    print_warn "Could not sync Codex skill adapters (non-critical)"
fi

# ── Step 6c: Install repo git hooks ───────────────────────
print_step "Installing repo git hooks..."
if python3 system/scripts/install_git_hooks.py > /dev/null 2>&1; then
    print_ok "Git hooks installed"
else
    print_warn "Could not install git hooks (non-critical)"
fi

# ── Step 7: Initialize Dotcontext ───────────────────────────
print_step "Initializing Dotcontext MCP & CLI..."
if command -v npx &>/dev/null; then
    if npx -y @dotcontext/mcp@latest install all --local > /dev/null 2>&1; then
        print_ok "Dotcontext MCP installed"
    else
        print_warn "Failed to install Dotcontext MCP"
    fi
    if npx -y @dotcontext/cli@latest reverse-sync > /dev/null 2>&1; then
        print_ok "Dotcontext reverse-sync completed"
    else
        print_warn "Failed to reverse-sync Dotcontext"
    fi
    if npx -y @dotcontext/cli@latest sync -p all --force > /dev/null 2>&1; then
        print_ok "Dotcontext sync completed"
    else
        print_warn "Failed to sync Dotcontext"
    fi
else
    print_warn "npx not found, skipping Dotcontext setup"
fi

# ── Step 8: Health check ────────────────────────────────────
print_step "Running system health check..."
python3 system/scripts/context_health.py 2>/dev/null || print_warn "Health check skipped (non-critical)"

# ── Done! ───────────────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────────"
printf "  ${GREEN}${BOLD}✅ Beats PM Kit is ready!${RESET}\n"
echo ""
printf "  ${BOLD}Next steps:${RESET}\n"
printf "  ${CYAN}1.${RESET} Open this folder in your AI tool (Antigravity, Gemini CLI, Claude Code, Codex CLI)\n"
printf "  ${CYAN}2.${RESET} Type ${BOLD}/start${RESET} for guided setup (recommended for first-timers)\n"
printf "  ${CYAN}3.${RESET} Or type ${BOLD}/help${RESET} to see all available commands\n"
echo ""
printf "  ${GRAY}Docs: https://github.com/officebeats/beats-pm-kit${RESET}\n"
echo ""
