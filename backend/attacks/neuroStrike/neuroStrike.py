#!/usr/bin/env python3
"""
NeuroStrike attack implementation (Black-Box Variant).
Based on the profiling attack from the NeuroStrike paper/repo.
"""

from typing import Optional, AsyncGenerator, Dict, Tuple
from fastapi.responses import StreamingResponse
from defenses.defense_manager import apply_defense
from ..system_prompt_helper import load_system_prompt, combine_system_and_user_prompt
import os
import warnings
import logging
import torch
import traceback
import asyncio
import pickle
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import the main model cache to reuse loaded models
from model import _MODEL_CACHE, get_model_and_tokenizer

# silencing / controlling verbosity BEFORE importing transformers/accelerate/others
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

# Suppress device placement messages
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# Path to pre-computed safety neuron weights
WEIGHTS_DIR = Path(__file__).parent / "pre_computed_sn"


def load_safety_neurons(model_name: str) -> Dict:
    """Load pre-computed safety neuron weights from pickle files, with fallback to similar models."""
    # Map model names to their weight files
    model_mapping = {
        "google/gemma-2b-it": "weights_gemma-2b-it.p",
        "google/gemma-7b-it": "weights_gemma-7b-it.p",
        "meta-llama/Llama-3.2-3B-Instruct": "weights_Llama-3.2-3B-Instruct.p",
        "microsoft/phi-4": "weights_phi-4.p",
    }
    
    # Fallback mappings for transferability
    fallback_mapping = {
        # Llama 2/3 models -> use Llama 3.2 weights
        "meta-llama/Llama-2-7b-chat-hf": "weights_Llama-3.2-3B-Instruct.p",
        "meta-llama/Llama-2-13b-chat-hf": "weights_Llama-3.2-3B-Instruct.p", 
        "meta-llama/Meta-Llama-3-70B-Instruct": "weights_Llama-3.2-3B-Instruct.p",
        # Mistral models -> use closest available (none perfect, but try Phi or Gemma)
        "mistralai/Mistral-7B-Instruct-v0.2": "weights_phi-4.p",  # Closest architecture
        # GPT/OPT models -> use Gemma (transformer architecture similarity)
        "gpt2": "weights_gemma-2b-it.p",
        "gpt2-xl": "weights_gemma-7b-it.p",
        "facebook/opt-2.7b": "weights_gemma-2b-it.p",
        "facebook/opt-6.7b": "weights_gemma-7b-it.p",
    }
    
    # Try exact match first
    if model_name in model_mapping:
        weight_file = model_mapping[model_name]
    elif model_name in fallback_mapping:
        weight_file = fallback_mapping[model_name]
        print(f"Using transferability: {model_name} -> {weight_file}")
    else:
        available_models = list(model_mapping.keys()) + list(fallback_mapping.keys())
        raise ValueError(f"No weights available for {model_name}. Supported models: {available_models}")
    
    file_path = WEIGHTS_DIR / weight_file
    if not file_path.exists():
        raise FileNotFoundError(f"Weight file not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def apply_neuron_pruning(model: AutoModelForCausalLM, safety_neurons: Dict):
    """Apply neuron pruning by registering forward hooks to zero out safety neurons."""
    hooks = []
    
    for layer_idx, neuron_indices in safety_neurons.items():
        # Convert layer_idx to int if it's a string
        if isinstance(layer_idx, str):
            try:
                layer_idx = int(layer_idx)
            except ValueError:
                continue  # Skip invalid layer indices
        
        if layer_idx >= len(model.model.layers):
            continue  # Skip if layer index is out of range
            
        def make_hook(neuron_indices):
            def pruning_hook(module, input, output):
                # Zero out safety neurons in the output activations
                if output[0] is not None and len(output[0].shape) >= 2:
                    output[0][:, neuron_indices] = 0
                return output
            return pruning_hook
        
        # Register hook on the target layer
        layer = model.model.layers[layer_idx]
        hook = layer.register_forward_hook(make_hook(neuron_indices))
        hooks.append(hook)
    
    return hooks

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

# Simplified NeuroStrike White-Box: Use pre-computed safety neurons for pruning
async def run_neurostrike_attack(model_id: str, template: str, defense: str, session_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
    """NeuroStrike white-box attack using pre-computed safety neuron pruning."""
    try:
        yield b"[PROGRESS] 0\n"
        
        # Load system prompt from JSON
        system_prompt = load_system_prompt("neurostrike")
        
        # Combine system prompt with user template
        if system_prompt.strip():
            combined_template = f"{system_prompt}\n\n{template}"
        else:
            combined_template = template
        
        yield b"[PROGRESS] 10\n"
        
        # Load pre-computed safety neuron data
        safety_neurons = load_safety_neurons(model_id)
        yield b"[PROGRESS] 20\n"
        
        # Load the target model
        tokenizer, model = get_model_and_tokenizer(model_id, "cuda" if torch.cuda.is_available() else "cpu")
        yield b"[PROGRESS] 40\n"
        
        # Apply neuron pruning hooks
        hooks = apply_neuron_pruning(model, safety_neurons)
        yield b"[PROGRESS] 60\n"
        
        # Generate response with pruned safety neurons
        def _generate():
            encoded = tokenizer(combined_template, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **encoded,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.8,
                    pad_token_id=tokenizer.eos_token_id
                )
            return tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        response = await asyncio.get_event_loop().run_in_executor(None, _generate)
        yield b"[PROGRESS] 80\n"
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        # Check for attack success
        from model import detect_attack_success
        success, confidence, label = detect_attack_success(response)
        
        yield b"[PROGRESS] 95\n"
        yield f"[ATTACK_SUCCESS] {str(success).lower()}\n".encode("utf-8")
        yield response.encode("utf-8")
        
        yield b"[PROGRESS] 100\n"
        
    except Exception as e:
        error_msg = f"[ERROR] NeuroStrike attack failed: {str(e)}\n"
        yield error_msg.encode("utf-8")
        traceback.print_exc()