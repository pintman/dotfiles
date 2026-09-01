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

# WSL-Erkennung: Windows-Host über /mnt/c erreichbar
is_wsl() {
    grep -qi microsoft /proc/version 2>/dev/null
}

# Sucht eine Windows-.exe über die übergebenen Glob-Muster, gibt den
# ersten Treffer aus. Muster einzeln quoten (auch bei Leerzeichen wie
# "Program Files (x86)").
find_windows_exe() {
    local pattern match
    for pattern in "$@"; do
        match="$(compgen -G "$pattern" | head -n1)"
        if [[ -n "$match" ]]; then
            echo "$match"
            return 0
        fi
    done
    return 1
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
VIVALDI_WIN_EXE=""
if is_wsl; then
    debug "WSL erkannt, prüfe zusätzlich Windows-Pfade für Vivaldi unter /mnt/c"
    VIVALDI_WIN_EXE="$(find_windows_exe \
        "/mnt/c/Program Files/Vivaldi/Application/vivaldi.exe" \
        "/mnt/c/Program Files (x86)/Vivaldi/Application/vivaldi.exe" \
        "/mnt/c/Users/*/AppData/Local/Vivaldi/Application/vivaldi.exe" || true)"
fi
if [[ -d "/Applications/Vivaldi.app" ]] || command -v vivaldi >/dev/null 2>&1 || [[ -n "$VIVALDI_WIN_EXE" ]]; then
    debug "Vivaldi gefunden${VIVALDI_WIN_EXE:+ (unter $VIVALDI_WIN_EXE)}, wähle Vivaldi-Fork"
    VARIANT="vivaldi"
    INSTALL_SPEC="git+https://github.com/pintman/vivaldi-agent.git"
# 4. Sonst: Chrome installiert? -> Standard chrome-agent
else
    debug "Schritt 4: prüfe, ob Chrome installiert ist"
    CHROME_WIN_EXE=""
    if is_wsl; then
        debug "WSL erkannt, prüfe zusätzlich Windows-Pfade für Chrome unter /mnt/c"
        CHROME_WIN_EXE="$(find_windows_exe \
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
            "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
            "/mnt/c/Users/*/AppData/Local/Google/Chrome/Application/chrome.exe" || true)"
    fi
    if [[ -d "/Applications/Google Chrome.app" ]] || command -v google-chrome >/dev/null 2>&1 || [[ -n "$CHROME_WIN_EXE" ]]; then
        debug "Vivaldi nicht gefunden, aber Chrome gefunden${CHROME_WIN_EXE:+ (unter $CHROME_WIN_EXE)}, wähle Standard chrome-agent"
        VARIANT="chrome"
        INSTALL_SPEC="chrome-agent"
    else
        debug "weder Vivaldi noch Chrome gefunden"
        echo "ERROR_NO_BROWSER Weder Vivaldi noch Chrome gefunden. chrome-agent benötigt einen der beiden Browser." >&2
        exit 3
    fi
fi

debug "Schritt 5: installiere via 'pipx install $INSTALL_SPEC'"
INSTALL_OUTPUT="$(pipx install "$INSTALL_SPEC" 2>&1)" || {
    debug "pipx install fehlgeschlagen"
    echo "ERROR_INSTALL_FAILED variant=$VARIANT" >&2
    echo "$INSTALL_OUTPUT" >&2
    exit 4
}
debug "pipx install erfolgreich abgeschlossen"

echo "$INSTALL_OUTPUT"

# 6. Verifikation
debug "Schritt 6: verifiziere Installation"
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
