#!/usr/bin/env bash
# Richtet chrome-agent (bzw. den Vivaldi-Fork) via pipx ein.
# Exit-Codes:
#   0 - Erfolg (bereits installiert oder frisch installiert)
#   2 - pipx fehlt
#   3 - weder Vivaldi noch Chrome gefunden
#   4 - pipx install fehlgeschlagen
#   5 - Verifikation nach Installation fehlgeschlagen
set -euo pipefail

debug() {
    echo "[debug] $*" >&2
}

# 1. Bereits installiert?
debug "Schritt 1: prüfe, ob chrome-agent bereits im PATH liegt"
if command -v chrome-agent >/dev/null 2>&1; then
    debug "chrome-agent gefunden unter $(command -v chrome-agent)"
    echo "ALREADY_INSTALLED path=$(command -v chrome-agent) version=$(chrome-agent --version 2>/dev/null || echo unbekannt)"
    exit 0
fi
debug "chrome-agent nicht gefunden, fahre mit Installation fort"

# 2. pipx verfügbar?
debug "Schritt 2: prüfe, ob pipx verfügbar ist"
if ! command -v pipx >/dev/null 2>&1; then
    debug "pipx nicht gefunden"
    echo "ERROR_NO_PIPX pipx ist nicht installiert (z.B. 'brew install pipx' oder 'apt install pipx')." >&2
    exit 2
fi
debug "pipx gefunden unter $(command -v pipx)"

# 3. Vivaldi installiert? -> Vivaldi-Fork
debug "Schritt 3: prüfe, ob Vivaldi installiert ist"
if [[ -d "/Applications/Vivaldi.app" ]] || command -v vivaldi >/dev/null 2>&1; then
    debug "Vivaldi gefunden, wähle Vivaldi-Fork"
    VARIANT="vivaldi"
    INSTALL_SPEC="git+https://github.com/pintman/vivaldi-agent.git"
# 4. Sonst: Chrome installiert? -> Standard chrome-agent
elif [[ -d "/Applications/Google Chrome.app" ]] || command -v google-chrome >/dev/null 2>&1; then
    debug "Vivaldi nicht gefunden, aber Chrome gefunden, wähle Standard chrome-agent"
    VARIANT="chrome"
    INSTALL_SPEC="chrome-agent"
else
    debug "weder Vivaldi noch Chrome gefunden"
    echo "ERROR_NO_BROWSER Weder Vivaldi noch Chrome gefunden. chrome-agent benötigt einen der beiden Browser." >&2
    exit 3
fi

debug "Schritt 4: installiere via 'pipx install $INSTALL_SPEC'"
INSTALL_OUTPUT="$(pipx install "$INSTALL_SPEC" 2>&1)" || {
    debug "pipx install fehlgeschlagen"
    echo "ERROR_INSTALL_FAILED variant=$VARIANT" >&2
    echo "$INSTALL_OUTPUT" >&2
    exit 4
}
debug "pipx install erfolgreich abgeschlossen"

echo "$INSTALL_OUTPUT"

# 5. Verifikation
debug "Schritt 5: verifiziere Installation"
if command -v chrome-agent >/dev/null 2>&1; then
    debug "chrome-agent nach Installation gefunden unter $(command -v chrome-agent)"
    echo "INSTALLED variant=$VARIANT path=$(command -v chrome-agent) version=$(chrome-agent --version 2>/dev/null || echo unbekannt)"
    exit 0
else
    debug "chrome-agent nach Installation weiterhin nicht im PATH"
    echo "ERROR_VERIFY_FAILED variant=$VARIANT" >&2
    echo "$INSTALL_OUTPUT" >&2
    exit 5
fi
