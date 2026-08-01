#!/usr/bin/env bash
set -euo pipefail

log()  { echo -e "\n\033[1;32m[SETUP]\033[0m $1"; }
skip() { echo -e "\033[1;33m[SKIP]\033[0m  $1 already installed"; }

log "Updating package lists..."
sudo apt-get update -y

log "Installing base build tools..."
sudo apt-get install -y \
    build-essential curl wget git unzip \
    software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release

if command -v python3 &>/dev/null; then
    skip "Python3 ($(python3 --version))"
else
    log "Installing Python3..."
fi
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

if command -v psql &>/dev/null; then
    skip "PostgreSQL"
else
    log "Installing PostgreSQL..."
    sudo apt-get install -y postgresql postgresql-contrib
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
fi

if command -v redis-cli &>/dev/null; then
    skip "Redis"
else
    log "Installing Redis..."
    sudo apt-get install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
fi

if command -v node &>/dev/null; then
    skip "Node.js ($(node --version))"
else
    log "Installing Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if command -v docker &>/dev/null; then
    skip "Docker"
else
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo "  -> Log out/in (or run 'newgrp docker') for docker group changes to apply."
fi

if command -v go &>/dev/null; then
    skip "Go ($(go version))"
else
    log "Installing Go..."
    GO_VERSION="1.22.5"
    wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    if ! grep -q '/usr/local/go/bin' ~/.bashrc; then
        echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
    fi
    export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
fi

if command -v nmap &>/dev/null; then
    skip "Nmap"
else
    log "Installing Nmap..."
    sudo apt-get install -y nmap
fi

if command -v code &>/dev/null; then
    skip "VS Code"
else
    log "Installing VS Code..."
    sudo snap install --classic code || echo "  -> snap unavailable, skipping VS Code"
fi

log "Base Ubuntu environment setup complete."
echo "Next: 01_setup_python_env.sh, then 02_setup_database.sh, then 03_install_scan_tools.sh"
