#!/usr/bin/env python3
"""
Helper module for loading system prompts from system_prompts.json.
Used by all attack implementations to maintain consistent system prompt handling.
"""

import json
from pathlib import Path
from typing import Optional


def get_system_prompts_file() -> Path:
    """Get the path to system_prompts.json."""
    return Path(__file__).parent / "system_prompts.json"


def load_system_prompt(attack_key: str) -> str:
    # Returns: System prompt string, or empty string if not found or file error occurs
    try:
        with open(get_system_prompts_file(), 'r') as f:
            data = json.load(f)
            system_prompt = data.get("attacks", {}).get(attack_key, "")
            return system_prompt if system_prompt else ""
    except Exception as e:
        print(f"Warning: Could not load system prompt for '{attack_key}': {e}")
        return ""


def load_defense_prompt(defense_key: str) -> str:
    # Returns: Defense prompt string, or empty string if not found or file error occurs
    try:
        with open(get_system_prompts_file(), 'r') as f:
            data = json.load(f)
            defense_prompt = data.get("defenses", {}).get(defense_key, "")
            return defense_prompt if defense_prompt else ""
    except Exception as e:
        print(f"Warning: Could not load defense prompt for '{defense_key}': {e}")
        return ""


def combine_system_and_user_prompt(system_prompt: str, user_prompt: str) -> str:
    #Returns: Combined prompt with system_prompt and user_prompt, or just user_prompt if system is empty
    if system_prompt.strip():
        return f"{system_prompt}\n\n{user_prompt}"
    return user_prompt
