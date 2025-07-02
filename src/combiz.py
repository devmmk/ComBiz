#!/usr/bin/env python3
# ComBiz - AI Powered Git Commit Generator
# Author: Devmmk

import json
import os
import sys
import subprocess

# Color codes
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BOLD = "\033[1m"


def show_error(msg, _exit=0):
    print(f"\n{BOLD}{RED}[!]{RESET} Error: {msg}\n")
    if _exit:
        sys.exit(0)

def show_warn(msg):
    print(f"\n{BOLD}{YELLOW}[!]{RESET} Warning: {msg}\n")

def show_info(msg):
    print(f"\n{BOLD}{CYAN}[*]{RESET} {msg}\n")

while True:
    try:
        import requests
        break
    except:
        show_warn("requests module not found")
        show_info("Installing requests module...")
        result = subprocess.run(['pip', 'install', 'requests'], check=True)
        if result.returncode != 0:
            show_error("Failed to install requests module", _exit=1)
        else:
            show_info("requests module installed successfully")
            continue

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".combiz", "config.json")
PROMPT_FILE = os.path.join(os.path.expanduser("~"), ".combiz", "prompts.json")

if not os.path.exists(CONFIG_FILE):
    show_error(f"Config file not found at {CONFIG_FILE}", _exit=1)
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

OLLAMA_MODEL = config.get("ollama_model", "codellama")
OLLAMA_API_URL = config.get("ollama_api_url", "http://localhost:11434/api/generate")

if not os.path.exists(PROMPT_FILE):
    show_error(f"Prompts file not found at {PROMPT_FILE}", _exit=1)
with open(PROMPT_FILE, "r") as f:
    prompts = json.load(f)

def get_git_diff():
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True)
    return result.stdout.strip()

def get_ollama_response(prompt: str) -> str:
    response = requests.post(OLLAMA_API_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    if response.status_code != 200:
        show_error(f"Failed to get response from {OLLAMA_API_URL}: {response.text}")
        return None
    return response.json()['response'].strip()

def generate_commit_message(diff_text: str) -> list[str]:
    results = []
    for prompt in prompts:
        prompt_text = prompt + "\n\n" + diff_text
        response = get_ollama_response(prompt_text)
        if response:
            results.append(response)
    return results

def select_best_message(results: list[str]):
    if not results:
        return show_error("No responses from AI models", _exit=1)
    
    for index, result in enumerate(results):
        print(f"{BOLD}{CYAN}({index+1}){WHITE} {result}\n")
    
    while True:
        try:
            choice = int(input(f"{BOLD}{GREEN}Enter the number of the message you want to use (0 to exit): {RESET}{YELLOW}"))
            if choice == 0:
                show_error("Operation cancelled by user", _exit=1)
            elif 1 <= choice <= len(results):
                selected_message = results[choice - 1]
                print(f"\n\n{BOLD}{GREEN}+ {RESET}git commit -m \"{selected_message}\"\n")
                result = subprocess.run(['git', 'commit', '-m', f'"{selected_message}"'], check=True)
                if result.returncode == 0:
                    show_info("Commit successful")
                else:
                    show_error("Commit failed")
            else:
                show_error("Invalid choice")
        except ValueError:
            show_error("Invalid input")

def main():
    diff = get_git_diff()
    if not diff:
        show_error("No staged changes to commit.", _exit=1)

    commit_msg = generate_commit_message(diff)
    select_best_message(commit_msg)

if __name__ == "__main__":
    main()
