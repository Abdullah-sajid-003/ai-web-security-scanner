#!/usr/bin/env bash
set -euo pipefail
log()  { echo -e "\n\033[1;32m[TOOLS]\033[0m $1"; }
skip() { echo -e "\033[1;33m[SKIP]\033[0m  $1 already installed"; }
export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin

if ! command -v go &>/dev/null; then
    echo "ERROR: Go not installed. Run 00_setup_ubuntu.sh first." >&2
    exit 1
fi

if command -v nmap &>/dev/null; then skip "nmap"; else log "Installing nmap..."; sudo apt-get install -y nmap; fi

install_go_tool() {
    local name="$1" pkg="$2" bin="$3"
    if command -v "$bin" &>/dev/null; then skip "$name"; else log "Installing $name..."; go install "$pkg@latest"; fi
}
install_go_tool "httpx"     "github.com/projectdiscovery/httpx/cmd/httpx"         httpx
install_go_tool "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder" subfinder
install_go_tool "katana"    "github.com/projectdiscovery/katana/cmd/katana"       katana
install_go_tool "nuclei"    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"    nuclei
install_go_tool "ffuf"      "github.com/ffuf/ffuf/v2"                             ffuf

if command -v sqlmap &>/dev/null; then
    skip "sqlmap"
else
    log "Installing sqlmap..."
    sudo apt-get install -y sqlmap || {
        git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git ~/tools/sqlmap
        sudo ln -sf ~/tools/sqlmap/sqlmap.py /usr/local/bin/sqlmap
        sudo chmod +x /usr/local/bin/sqlmap
    }
fi

if command -v nuclei &>/dev/null; then
    log "Updating nuclei templates..."
    nuclei -update-templates || true
fi
log "Scanner engine tools installed."
