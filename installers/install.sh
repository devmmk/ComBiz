#!/usr/bin/env bash

set -e

echo -e "\n\033[34mComBiz Installer (Linux)\033[0m\n"

if ! command -v python3 &> /dev/null; then
    echo -e "\033[91mPython3 is not installed. Please install Python3 first.\033[0m"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo -e "\033[91mpip is not installed. Please install pip first.\033[0m"
    exit 1
fi

INSTALL_BIN="$HOME/.local/bin"
INSTALL_CONF="$HOME/.combiz"

mkdir -p "$INSTALL_BIN"
mkdir -p "$INSTALL_CONF"

cp src/combiz.py "$INSTALL_BIN/combiz"
chmod +x "$INSTALL_BIN/combiz"

cp -r config/* "$INSTALL_CONF/"

# Install Python dependencies
pip install --user requests --break-system-packages

# Check if $INSTALL_BIN is in PATH
if ! grep -q "$INSTALL_BIN" <<< "$PATH"; then
    echo -e "\033[93mWarning: $INSTALL_BIN is not in your PATH. Adding it...\033[0m"

    # Detect shell and corresponding config file
    SHELL_NAME=$(basename "$SHELL")
    case "$SHELL_NAME" in
        bash) CONFIG_FILE="$HOME/.bashrc" ;;
        zsh) CONFIG_FILE="$HOME/.zshrc" ;;
        *) CONFIG_FILE="$HOME/.profile" ;;  # fallback
    esac

    NEW_PATH='export PATH="$HOME/.local/bin:$PATH"'

    echo "$NEW_PATH" >> "$CONFIG_FILE"
    echo "Added \$HOME/.local/bin to PATH in $CONFIG_FILE"

    echo -e "\033[33mPlease restart your terminal or run:\033[0m source $CONFIG_FILE"
fi

# Final message
echo -e "\n\033[32mComBiz Installed Successfully!\033[0m"
echo -e "Run \033[36mcombiz\033[0m to start using it."