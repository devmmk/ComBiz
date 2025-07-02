#!/usr/bin/bash
cp src/combiz.py ~/.local/bin/combiz
chmod +x ~/.local/bin/combiz
cp -r config ~/.combiz
pip install requests
printf "\n\n\033[34m ComBiz Installed Successfully\033[0m\n"
printf "Run \033[32mcombiz\033[0m to start using it\n\n"