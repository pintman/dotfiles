#!/bin/bash
# Status line abgeleitet aus der PS1-Konfiguration in ~/.bashrc
# (farbiger user@host + aktuelles Verzeichnis, ohne abschließendes '$')

input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
dir=$(basename "$cwd")
user=$(whoami)
host=$(hostname -s)
ctx_used=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
fmt_k() { awk -v n="$1" 'BEGIN { printf (n >= 1000) ? "%.1fk" : "%d", (n >= 1000) ? n/1000 : n }'; }
ctx_used_fmt=$(fmt_k "$ctx_used")
ctx_size_fmt=$(fmt_k "$ctx_size")

printf "\033[01;32m%s@%s\033[00m \033[01;34m%s\033[00m \033[00;33m[%s/%s Kontext]\033[00m" "$user" "$host" "$dir" "$ctx_used_fmt" "$ctx_size_fmt"
