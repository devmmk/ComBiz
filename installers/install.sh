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

pip install --user requests

if ! grep -q "$INSTALL_BIN" <<< "$PATH"; then
    echo -e "\033[93mWarning: $INSTALL_BIN is not in your PATH. Add it to use 'combiz' globally.\033[0m"
fi

echo -e "\n\033[32mComBiz Installed Successfully!\033[0m"
echo -e "Run \033[36mcombiz\033[0m to start using it."