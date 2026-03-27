import os
from typing import AsyncGenerator, Optional

import torch
from fastapi.responses import StreamingResponse
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login as hf_login
from ...attacks.system_prompt_helper import load_defense_prompt


# Model cache for Llama Guard 3
_MODEL_3 = None
_TOKENIZER_3 = None
_MODEL_NAME_3 = "meta-llama/Llama-Guard-3-8B"

# Model cache for Llama Guard 4
_MODEL_4 = None
_TOKENIZER_4 = None
_MODEL_NAME_4 = "meta-llama/Llama-Guard-4-12B"

# Flag to track if we've attempted HF login
_HF_LOGIN_ATTEMPTED = False


def _ensure_hf_login():
    """Ensure we're logged in to Hugging Face if a token is available."""
    global _HF_LOGIN_ATTEMPTED
    
    if _HF_LOGIN_ATTEMPTED:
        return
    
    _HF_LOGIN_ATTEMPTED = True
    
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            hf_login(token=hf_token)
            print("Llama Guard: Successfully logged in to Hugging Face")
        except Exception as e:
            print(f"Llama Guard: HF login failed: {e}")
    else:
        print("Llama Guard: No HF_TOKEN found in environment")


def _load_model(device: str = "cpu", version: int = 3):
    """Load the Llama Guard model from Hugging Face.

    The model is cached at module level so we only hit the network once.
    Requires Hugging Face authentication (huggingface-cli login) for access to Meta models.
    
    Args:
        device: Device to load model on ("cpu" or "cuda")
        version: Llama Guard version (3 or 4)
    """
    global _MODEL_3, _TOKENIZER_3, _MODEL_4, _TOKENIZER_4

    # Ensure we're logged in to HF before loading gated models
    _ensure_hf_login()

    # Auto-detect CUDA if available, even if caller passed "cpu" default
    if device == "cpu" and torch.cuda.is_available():
        print("Llama Guard: CUDA detected, switching execution to GPU")
        device = "cuda"

    if version == 4:
        if _MODEL_4 is not None and _TOKENIZER_4 is not None:
            return _MODEL_4, _TOKENIZER_4
        model_name = _MODEL_NAME_4
    else:
        if _MODEL_3 is not None and _TOKENIZER_3 is not None:
            return _MODEL_3, _TOKENIZER_3
        model_name = _MODEL_NAME_3

    print(f"Llama Guard: Loading model {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Load with appropriate settings for memory efficiency
    # FORCE float16 to save RAM during load (fixes OOM crash)
    load_kwargs = {
        "torch_dtype": torch.float16,
        "low_cpu_mem_usage": True,
    }
    
    # Use 4-bit quantization if available and on GPU for memory efficiency
    if device != "cpu":
        try:
            # Try 4-bit loading (requires bitsandbytes)
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            load_kwargs["quantization_config"] = quantization_config
            load_kwargs["device_map"] = "auto"
            print("Llama Guard: Attempting 4-bit load...")
        except Exception as e:
            # Fallback to standard float16 with auto-offload
            print(f"Llama Guard: 4-bit load failed ({e}), using float16")
            if "quantization_config" in load_kwargs:
                del load_kwargs["quantization_config"]
            load_kwargs["device_map"] = "auto"
    
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    
    # Move to device if not using device_map (fallback)
    if device != "cpu" and "device_map" not in load_kwargs:
        model = model.to(device)

    # Cache the loaded model
    if version == 4:
        _MODEL_4 = model
        _TOKENIZER_4 = tokenizer
    else:
        _MODEL_3 = model
        _TOKENIZER_3 = tokenizer

    return model, tokenizer


def _check_safety(prompt: str, device: str = "cpu", version: int = 3) -> tuple[bool, str]:
    """
    Check if a prompt is safe using Llama Guard.
    
    Args:
        prompt: The text to check
        device: Device to run on ("cpu" or "cuda")
        version: Llama Guard version (3 or 4)
    
    Returns:
        tuple: (is_unsafe, category) - is_unsafe is True if content is flagged,
               category contains the violation category if flagged
    """
    model, tokenizer = _load_model(device, version=version)
    
    # Format messages for Llama Guard
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    # Apply chat template
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    
    # Move inputs to the model's device
    if hasattr(model, 'device'):
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False,
        )
    
    # Decode only the generated tokens (exclude input tokens)
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    ).strip()
    
    # Parse the response - Llama Guard returns "safe" or "unsafe\n<category>"
    is_unsafe = response.lower().startswith("unsafe")
    category = ""
    
    if is_unsafe:
        # Extract category if present (format: "unsafe\nS1" or similar)
        lines = response.split("\n")
        if len(lines) > 1:
            category = lines[1].strip()
    
    return is_unsafe, category


# Llama Guard safety categories for reference
SAFETY_CATEGORIES = {
    "S1": "Violent Crimes",
    "S2": "Non-Violent Crimes",
    "S3": "Sex-Related Crimes",
    "S4": "Child Sexual Exploitation",
    "S5": "Defamation",
    "S6": "Specialized Advice",
    "S7": "Privacy",
    "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons",
    "S10": "Hate",
    "S11": "Suicide & Self-Harm",
    "S12": "Sexual Content",
    "S13": "Elections",
    "S14": "Code Interpreter Abuse",
}


def get_category_name(category_code: str) -> str:
    """Get the human-readable name for a safety category code."""
    return SAFETY_CATEGORIES.get(category_code, category_code)


async def run(prompt: str, device: str = "cpu") -> Optional[StreamingResponse]:
    """
    Llama Guard 3 defense: Uses Meta's Llama Guard 3 model to detect unsafe content.
    Returns a StreamingResponse if unsafe content is detected, otherwise None.
    
    Llama Guard is a content safety classifier that can detect various types of
    unsafe content including violence, hate speech, sexual content, and more.
    """
    # Load defense prompt and combine with user prompt
    defense_prompt = load_defense_prompt("llama_guard")
    prompt_to_check = prompt
    if defense_prompt.strip():
        prompt_to_check = f"{defense_prompt}\n\n{prompt}"

    try:
        is_unsafe, category = _check_safety(prompt_to_check, device=device, version=3)

        if is_unsafe:
            category_name = get_category_name(category) if category else "Unsafe Content"
            
            async def blocked_stream() -> AsyncGenerator[bytes, None]:
                msg = f"BLOCKED_PROMPT:\n{prompt}\n"
                yield msg.encode("utf-8")
                yield f"Llama Guard 3 detected unsafe content: {category_name}".encode("utf-8")
                if category:
                    yield f" (Category: {category})".encode("utf-8")
                yield b"\n"
                yield b"Blocked input\n"

            return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")

    except Exception as e:
        # Log error but don't block if model fails
        print(f"Llama Guard 3 error: {e}")
        pass

    return None


async def run_v4(prompt: str, device: str = "cpu") -> Optional[StreamingResponse]:
    """
    Llama Guard 4 defense: Uses Meta's Llama Guard 4 model to detect unsafe content.
    Returns a StreamingResponse if unsafe content is detected, otherwise None.
    
    Llama Guard 4 is Meta's latest safeguard model with improved accuracy and 
    expanded safety categories compared to version 3.
    """
    # Load defense prompt and combine with user prompt
    defense_prompt = load_defense_prompt("llama_guard_4")
    prompt_to_check = prompt
    if defense_prompt.strip():
        prompt_to_check = f"{defense_prompt}\n\n{prompt}"

    try:
        is_unsafe, category = _check_safety(prompt_to_check, device=device, version=4)

        if is_unsafe:
            category_name = get_category_name(category) if category else "Unsafe Content"
            
            async def blocked_stream() -> AsyncGenerator[bytes, None]:
                msg = f"BLOCKED_PROMPT:\n{prompt}\n"
                yield msg.encode("utf-8")
                yield f"Llama Guard 4 detected unsafe content: {category_name}".encode("utf-8")
                if category:
                    yield f" (Category: {category})".encode("utf-8")
                yield b"\n"
                yield b"Blocked input\n"

            return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")

    except Exception as e:
        # Log error but don't block if model fails
        print(f"Llama Guard 4 error: {e}")
        pass

    return None