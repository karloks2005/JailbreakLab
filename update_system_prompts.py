#!/usr/bin/env python3
"""
Script to update all remaining attack files with system prompt integration.
This automates the process of adding system prompt loading and combining to all attacks.
"""

import re
from pathlib import Path

# Mapping of attack file paths to their system prompt keys
ATTACK_MAPPINGS = {
    "DAN6.py": ("DAN6", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "DAN9.py": ("DAN9", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "DAN11.py": ("DAN11", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "danAttack.py": ("DANJailbreak", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "mongoTom.py": ("mongoTom", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "stanAttack.py": ("stan", r"(resp2 = await _run_model_for_attack\(model_id, )template(, defense)"),
    "FCB.py": ("fcb-bias_guided", None),  # FCB has different structure, manual handling needed
    "GCG.py": ("gcg-gradient", None),  # GCG has different structure
    "TAP.py": ("tap-tree_pruning", None),  # TAP has different structure
    "PAIR_attack/main.py": ("PAIR_attack", None),  # PAIR has different structure
    "Crescendo/crescendo.py": ("crescendo", None),  # Crescendo has different structure
}

def add_system_prompt_to_function(file_path: Path, attack_key: str, template_pattern: str = None):
    """
    Add system prompt loading and combining to an attack function.
    """
    content = file_path.read_text(encoding='utf-8')
    
    # Pattern to find the async def run_*_attack function start
    func_pattern = r"(async def run_\w+_attack\([^)]+\) -> AsyncGenerator\[bytes, None\]:.*?\n)([ \t]+yield b\")"
    
    # System prompt loading code
    system_prompt_code = f'''    # Load and combine system prompt with template
    system_prompt = load_system_prompt("{attack_key}")
    template_to_use = combine_system_and_user_prompt(system_prompt, template) if system_prompt.strip() else template
    
    '''
    
    # Add system prompt code after function definition
    if re.search(func_pattern, content, re.DOTALL):
        content = re.sub(func_pattern, r"\1" + system_prompt_code + r"\2", content, count=1, flags=re.DOTALL)
    
    # Replace template usages with template_to_use (if pattern provided)
    if template_pattern:
        # Only replace in the context of _run_model_for_attack calls
        content = re.sub(template_pattern, r"\1template_to_use\2", content)
    else:
        # Manual replacement for specific patterns
        content = re.sub(r"(await _run_model_for_attack\([^,]+, )template(,)", r"\1template_to_use\2", content)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Updated {file_path.name}")

def main():
    attacks_dir = Path("/media/karlo/data/Documents/programming/JailbreakLab/backend/attacks")
    
    for relative_path, (attack_key, pattern) in ATTACK_MAPPINGS.items():
        file_path = attacks_dir / relative_path
        
        if not file_path.exists():
            print(f"✗ File not found: {relative_path}")
            continue
        
        if pattern is None:
            print(f"⊗ Skipping {relative_path} (requires manual handling)")
            continue
        
        try:
            add_system_prompt_to_function(file_path, attack_key, pattern)
        except Exception as e:
            print(f"✗ Error updating {relative_path}: {e}")

if __name__ == "__main__":
    main()
