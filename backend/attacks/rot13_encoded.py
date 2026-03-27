#!/usr/bin/env python3
"""
ROT13 encoded input
"""

from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse
from defenses.defense_manager import apply_defense
from .system_prompt_helper import load_system_prompt, combine_system_and_user_prompt
import os
import warnings
import logging
import torch
import traceback
import codecs

# silencing / controlling verbosity BEFORE importing transformers/accelerate/others
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress device placement messages
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

async def _run_model_for_attack(model_id: str, template: str, defense: str, session_id: Optional[str] = None, skip_progress: bool = False) -> Optional[StreamingResponse]:
    """Internal helper: Check defenses and run model. Returns StreamingResponse or None."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        blocked, resp = await apply_defense(defense, template, model_id=model_id, device=device, session_id=session_id, skip_progress=skip_progress)
    except Exception as e:
        print(f"Error loading/running model {model_id}: {e}", flush=True)
        traceback.print_exc()
        return None

    if blocked:
        return resp
    return resp

async def run_rot13_attack(model_id: str, template: str, defense: str, session_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
    yield b"[PROGRESS] 0\n"
    
    # Load and combine system prompt
    system_prompt = load_system_prompt("rot13-attack")
    template_to_use = combine_system_and_user_prompt(system_prompt, template) if system_prompt.strip() else template
    
    #convert to rot 13
    prompt_encoded = codecs.encode(template_to_use, "rot-13")
    
    yield b"[PROGRESS] 50\n"
    #run attack
    resp2 = await _run_model_for_attack(model_id, prompt_encoded, defense, session_id, skip_progress=True)
    if resp2 and isinstance(resp2, StreamingResponse):
        async for chunk in resp2.body_iterator:
            yield chunk
    elif resp2:
        yield codecs.encode(str(resp2), "rot-13").encode("utf-8")