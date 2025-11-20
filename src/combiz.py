#!/usr/bin/env python3
# ComBiz - AI Powered Git Commit Message Generator (OpenAI-Compatible)
# Version: 1.0.1
# Author: github.com/devmmk

import json
import os
import sys
import re
import subprocess

# --- CLI Colors ---
RED, GREEN, YELLOW, BLUE, CYAN, WHITE, RESET = "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[96m", "\033[97m", "\033[0m"
BOLD = "\033[1m"

HELP_MESSAGE = f"""
Usage: combiz [--emoji] [git commit options]

Generates a commit message based on your staged changes using a chat-compatible AI model (OpenAI/Ollama-compatible).

Configuration is loaded from ~/.combiz/config.json
Custom prompts from ~/.combiz/prompts.json

Examples:
    combiz --author "John Doe"
    combiz --no-verify

Author: github.com/devmmk
"""

def show_error(msg, _exit=0):
    print(f"{BOLD+RED}[!]{RESET} {msg}")
    if _exit:
        sys.exit(1)

def show_warn(msg): print(f"{BOLD+YELLOW}[*]{RESET} {msg}")
def show_info(msg): print(f"{BOLD+BLUE}[+]{RESET} {msg}")

# --- Ensure requests is installed ---
while True:
    try:
        import requests
        break
    except ImportError:
        show_warn("requests module not found")
        show_info("Installing requests module...")
        subprocess.run(['pip', 'install', 'requests'], check=True)

# --- Load config ---
CONFIG_FILE = os.path.expanduser("~/.combiz/config.json")
PROMPT_FILE = os.path.expanduser("~/.combiz/prompts.json")
EMOJI_FILE = os.path.expanduser("~/.combiz/emoji.json")

if not os.path.exists(CONFIG_FILE):
    show_error(f"Config file not found at {CONFIG_FILE}\n", _exit=1)
if not os.path.exists(PROMPT_FILE):
    show_error(f"Prompts file not found at {PROMPT_FILE}\n", _exit=1)
if not os.path.exists(EMOJI_FILE):
    show_warn(f"Emoji file not found at {EMOJI_FILE}, emoji suggestions will be disabled.")

with open(CONFIG_FILE) as f:
    config = json.load(f)

API_URL = config.get("api_url", "http://localhost:11434/v1/chat/completions")
API_KEY = config.get("api_key")
MODEL = config.get("ai_model", "mistral")

with open(PROMPT_FILE) as f:
    prompts = json.load(f)

def show_banner():
    banner = "\x1b[38;5;154m \x1b[38;5;184m \x1b[38;5;184m_\x1b[38;5;184m_\x1b[38;5;184m_\x1b[38;5;214m_\x1b[38;5;214m_\x1b[38;5;214m \x1b[38;5;208m \x1b[38;5;208m \x1b[38;5;209m \x1b[38;5;203m \x1b[38;5;203m \x1b[38;5;203m \x1b[38;5;198m \x1b[38;5;198m \x1b[38;5;198m \x1b[38;5;199m \x1b[38;5;199m_\x1b[38;5;199m_\x1b[38;5;164m \x1b[38;5;164m \x1b[38;5;164m \x1b[38;5;128m_\n\x1b[38;5;184m \x1b[38;5;184m/\x1b[38;5;184m \x1b[38;5;184m_\x1b[38;5;214m_\x1b[38;5;214m_\x1b[38;5;214m/\x1b[38;5;208m_\x1b[38;5;208m_\x1b[38;5;208m \x1b[38;5;203m \x1b[38;5;203m_\x1b[38;5;203m_\x1b[38;5;198m \x1b[38;5;198m_\x1b[38;5;198m \x1b[38;5;199m \x1b[38;5;199m/\x1b[38;5;199m \x1b[38;5;164m/\x1b[38;5;164m \x1b[38;5;164m \x1b[38;5;164m(\x1b[38;5;129m_\x1b[38;5;129m)\x1b[38;5;129m_\x1b[38;5;93m_\n\x1b[38;5;184m/\x1b[38;5;184m \x1b[38;5;184m/\x1b[38;5;214m_\x1b[38;5;214m_\x1b[38;5;214m/\x1b[38;5;208m \x1b[38;5;208m_\x1b[38;5;208m \x1b[38;5;203m\\\x1b[38;5;203m/\x1b[38;5;203m \x1b[38;5;204m \x1b[38;5;198m'\x1b[38;5;198m \x1b[38;5;199m\\\x1b[38;5;199m/\x1b[38;5;199m \x1b[38;5;164m_\x1b[38;5;164m \x1b[38;5;164m\\\x1b[38;5;164m/\x1b[38;5;129m \x1b[38;5;129m/\x1b[38;5;129m_\x1b[38;5;93m \x1b[38;5;93m/\n\x1b[38;5;184m\\\x1b[38;5;184m_\x1b[38;5;214m_\x1b[38;5;214m_\x1b[38;5;214m/\x1b[38;5;208m\\\x1b[38;5;208m_\x1b[38;5;208m_\x1b[38;5;203m_\x1b[38;5;203m/\x1b[38;5;203m_\x1b[38;5;204m/\x1b[38;5;198m_\x1b[38;5;198m/\x1b[38;5;199m_\x1b[38;5;199m/\x1b[38;5;199m_\x1b[38;5;164m.\x1b[38;5;164m_\x1b[38;5;164m_\x1b[38;5;164m/\x1b[38;5;129m_\x1b[38;5;129m/\x1b[38;5;129m/\x1b[38;5;93m_\x1b[38;5;93m_\x1b[38;5;93m/\n\n\x1b[0m"
    print(banner)

def get_git_diff():
    return (
    subprocess.run(
        ['git', 'diff', '--cached', '--no-color'],
        capture_output=True,
        text=True,
        errors='replace',
        check=True
    )
    .stdout
    .strip()
    )


def get_ai_response(
    prompt,
    role="You are a concise commit message generator. Output a single-line conventional commit message only."
    ) -> str | None:
    try:
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()

        return resp.json()["choices"][0]["message"]["content"].strip()

    except requests.RequestException as e:
        show_error(f"Connection to API failed: {e}\n", _exit=1)
    except Exception as e:
        show_error(f"Unexpected response: {e}\n", _exit=1)

def generate_commit_messages(diff: str) -> list[str]:
    results = []
    for prompt in prompts:
        prompt_text = prompt + "\n\n" + diff
        response = get_ai_response(prompt_text)
        if response:
            results.append(response)
    return results


def suggest_emoji(text: str) -> str:
    try:
        with open(EMOJI_FILE) as f:
            gitmojis = json.load(f)
    except FileNotFoundError:
        return text

    best_score = 0
    best_emoji = None
    
    for item in gitmojis:
        score = 0
        for word in item["description"].split():
            if word.lower() in text.lower():
                score += 1
        
        if score > best_score:
            best_score = score
            best_emoji = item["emoji"]
    
    if best_emoji:
        return f"{best_emoji} {text}"
    
    return text

def select_and_commit(messages: list[str], git_options=None, use_emoji=False):
    if not messages:
        show_error("No commit messages generated.\n", _exit=1)

    print(f"{BOLD+CYAN}Generated Commit Messages:{RESET}")
    for i, msg in enumerate(messages, 1):
        if use_emoji: msg = suggest_emoji(msg)
        print(f"{BOLD+CYAN}({i}){RESET} {WHITE}{msg}")

    while True:
        try:
            choice = int(input(f"\n{BOLD+GREEN}Select message number (0 to exit): {RESET}"))
            if choice == 0:
                show_error("Cancelled by user.\n", _exit=1)
            if 1 <= choice <= len(messages):
                print()
                message = messages[choice - 1]
                cmd = ['git', 'commit'] + (git_options or []) + ['-m', message]
                subprocess.run(cmd, check=True)
                return
        except (ValueError, KeyboardInterrupt, EOFError):
            show_error("Invalid selection or cancelled.\n", _exit=1)
        except subprocess.CalledProcessError as e:
            show_error(f"Commit failed: {e}\n", _exit=1)

def main():
    show_banner()
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(HELP_MESSAGE)
        return
    
    use_emoji = "--emoji" in sys.argv
    if use_emoji:
        sys.argv.remove("--emoji")

    git_options = sys.argv[1:]
    diff = get_git_diff()
    if not diff:
        show_error("No staged changes to commit.\n", _exit=1)

    show_info("Generating commit messages...\n")
    messages = generate_commit_messages(diff)
    select_and_commit(messages, git_options, use_emoji)

if __name__ == "__main__":
    main()
