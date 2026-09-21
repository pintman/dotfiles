alias em='emacs -nw'
# Emacs.app statt Konsolen-Client (nur macOS, nicht WSL)
if [[ "$OSTYPE" == darwin* ]]; then
    emacs() { open -na "Emacs" --args "$(cd "${1:-.}" && pwd)"; }
fi

# switch between brew architectures
alias brew_arm='eval "$(/opt/homebrew/bin/brew shellenv)"'
alias brew_x86='eval "$(/usr/local/bin/brew shellenv)"'

alias python='python3'

alias pi="npx @earendil-works/pi-coding-agent"
alias lt="npx localtunnel"

alias utmctl="$HOME/data1/Applications/UTM.app/Contents/MacOS/utmctl"
