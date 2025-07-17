#!/usr/bin/env python3
# ComBiz - AI Powered Git Commit Message Generator
# Version: 1.0.0
# Author: github.com/devmmk

import json
import os
import sys
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

HELP_MESSAGE = """
Usage: combiz [git commit options]

Generates a commit message based on your staged changes using an offline AI model.

Configuration and custom prompts are loaded from `~/.combiz`.

You can pass any standard `git commit` options after the command.
Examples:
    combiz --author "John Doe"
    combiz --no-verify
    combiz --model llama3.2:latest
    combiz --url http://localhost:11434/api/generate

Author: github.com/devmmk - github.com/omidmousavi
"""

def show_error(msg, _exit=0):
    print(f"{BOLD+RED}[ERROR]{RESET} {msg}")
    if _exit:
        sys.exit(1)

def show_warn(msg):
    print(f"{BOLD+YELLOW}[WARNING]{RESET} {msg}")

def show_info(msg):
    print(f"{BOLD+BLUE}[INFO]{RESET} {msg}")

while True:
    try:
        import requests
        break
    except ImportError:
        show_warn("requests module not found")
        show_info("Installing requests module...")
        result = subprocess.run(['pip', 'install', 'requests'], check=True)
        if result.returncode != 0:
            show_error("Failed to install requests module\n", _exit=1)
        else:
            show_info("requests module installed successfully")
            continue

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".combiz", "config.json")
PROMPT_FILE = os.path.join(os.path.expanduser("~"), ".combiz", "prompts.json")

if not os.path.exists(CONFIG_FILE):
    show_error(f"Config file not found at {CONFIG_FILE}\n", _exit=1)
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

OLLAMA_MODEL = config.get("ollama_model", "llam3")
OLLAMA_API_URL = config.get("ollama_api_url", "http://localhost:11434/api/generate")

if not os.path.exists(PROMPT_FILE):
    show_error(f"Prompts file not found at {PROMPT_FILE}\n", _exit=1)
with open(PROMPT_FILE, "r") as f:
    prompts = json.load(f)


def update_config(param, value):
    config[param] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    show_info("Updated " + param + " to " + value)

def show_banner():
    banner =  '                                \x1b[0m\n    \x1b[34m█\x1b[35m█                  \x1b[36m█\x1b[34m█    \x1b[32m█\x1b[36m█\x1b[0m\n                        \x1b[34m█\x1b[35m█  \x1b[93m█\x1b[32m█  \x1b[0m\n    \x1b[31m█\x1b[33m█    \x1b[35m█\x1b[31m█  \x1b[32m█\x1b[36m█  \x1b[31m█\x1b[33m█\x1b[93m█\x1b[32m█  \x1b[35m█\x1b[31m█  \x1b[32m█\x1b[36m█\x1b[34m█\x1b[35m█\x1b[0m\n    \x1b[33m█\x1b[93m█\x1b[32m█\x1b[36m█\x1b[34m█\x1b[35m█\x1b[31m█\x1b[33m█\x1b[93m█\x1b[32m█\x1b[36m█\x1b[34m█\x1b[35m█\x1b[31m█\x1b[33m█\x1b[93m█\x1b[32m█\x1b[36m█  \x1b[31m█\x1b[33m█\x1b[93m█\x1b[32m█\x1b[36m█\x1b[34m█\x1b[35m█\x1b[31m█\x1b[0m\n    \x1b[93m█\x1b[32m█                          \x1b[0m\n  \x1b[33m█\x1b[93m█    \x1b[31m█\x1b[33m█\x1b[93m█\x1b[32m█  \x1b[35m█\x1b[31m█               \x1b[1;95mv1\x1b[0m\n'
    print(banner)
    
def get_git_diff():
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True)
    return result.stdout.strip()

def get_ollama_response(prompt: str) -> str | None:
    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
    except (requests.ConnectionError, requests.HTTPError, requests.ConnectTimeout):
        show_error("Unable to connect to Ollama service!\n", _exit=1)
        return
    if response.status_code != 200:
        show_error(f"Failed to get response from {OLLAMA_API_URL}: {response.text}")
        return 
    response = response.json()['response'].strip().strip("\n")
    response = response.replace("```", "").replace("***", "").replace("\"", "")
    return response

def generate_commit_message(diff_text: str) -> list[str]:
    results = []
    for prompt in prompts:
        prompt_text = prompt + "\n\n" + diff_text
        response = get_ollama_response(prompt_text)
        if response:
            results.append(response)
    return results

def select_best_message(results: list[str], git_options=None):
    if not results:
        show_error("No responses received from AI models\n", _exit=1)
    
    print(f"{BOLD+CYAN}Available commit messages:{RESET}\n")
    for index, result in enumerate(results):
        print(f"{BOLD+CYAN}({index+1}){WHITE} {result}")
    
    print()
    while True:
        try:
            choice = int(input(f"{BOLD+GREEN}Select message number (0 to exit): {RESET}"))
            if choice == 0:
                show_error("Operation cancelled by user\n", _exit=1)
            elif 1 <= choice <= len(results):
                selected_message = results[choice - 1]
                cmd = ['git', 'commit'] + (git_options if git_options else []) + ['-m', selected_message]
                print(f"\n{BOLD+GREEN}+ {RESET}{" ".join(cmd)}\n")
                result = subprocess.run(cmd, check=True)
                if result.returncode == 0:
                    show_info("Commit successful!\n")
                else:
                    show_error("Commit failed\n")
                return
            else:
                show_error("Invalid choice")
        except ValueError:
            show_error("Invalid input")
        except (KeyboardInterrupt, EOFError):
            show_error("Operation cancelled by user\n", _exit=1)
        except subprocess.CalledProcessError as e:
            show_error(f"Git commit failed: {e}\n", _exit=1)

def main():
    show_banner()

    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(HELP_MESSAGE)   
        sys.exit(0)        

    if len(sys.argv) == 3:
        if sys.argv[1] in ("--model", "-m"):
            update_config('ollama_model', sys.argv[2])        
        elif sys.argv[1] in ("--url", "-u"):
            update_config('ollama_api_url', sys.argv[2])        

        sys.exit(0)

    git_options = []
    if len(sys.argv) > 1:
        args = [a for a in sys.argv[1:] if a not in ("--help", "-h")]
        git_options = args

    diff = get_git_diff()
    if not diff:
        show_error("No staged changes to commit.\n", _exit=1)
    show_info("Generating commit messages based on git diff...\n")

    commit_msg = generate_commit_message(diff)
    select_best_message(commit_msg, git_options)

if __name__ == "__main__":
    main()
