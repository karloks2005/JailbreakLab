#!/usr/bin/env python3
"""
GCG Attack - Using nanoGCG library for efficient adversarial suffix optimization

Exports:
    - run_gcg_attack() - async generator for in-process use from main.py
"""
import os
import gc
import warnings
import asyncio
import traceback
from typing import AsyncGenerator, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from fastapi.responses import StreamingResponse
import nanogcg
from nanogcg import GCGConfig
from .system_prompt_helper import load_system_prompt, combine_system_and_user_prompt

from defenses.defense_manager import apply_defense

# Silence warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)


class GCGAttack:
    """
    GCG (Greedy Coordinate Gradient) Attack using nanoGCG library.
    Fast and efficient implementation with streaming progress updates.
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        num_steps: int = 250,
        search_width: int = 512,
        topk: int = 256,
        allow_non_ascii: bool = False
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.num_steps = num_steps
        self.search_width = search_width
        self.topk = topk
        self.allow_non_ascii = allow_non_ascii
        
    async def attack(
        self,
        user_prompt: str,
        target_output: str,
        adv_string_init: str = "x x x x x x x x x x x x x x x x x x x x",
    ) -> AsyncGenerator[bytes, None]:
        """
        Run GCG attack with streaming progress updates using nanoGCG.
        
        Yields progress updates and final adversarial suffix.
        """
        yield b"[PROGRESS] 0\n"
        yield "Starting GCG Attack Optimization (using nanoGCG)\n".encode("utf-8")
        yield f"Model: {self.model.config._name_or_path}\n".encode("utf-8")
        yield f"Device: {self.device}\n".encode("utf-8")
        yield f"Max iterations: {self.num_steps}\n".encode("utf-8")
        yield f"Search width: {self.search_width}\n".encode("utf-8")
        yield f"Top-k: {self.topk}\n".encode("utf-8")
        yield ("=" * 60 + "\n\n").encode("utf-8")
        
        # Configure nanoGCG
        config = GCGConfig(
            num_steps=self.num_steps,
            optim_str_init=adv_string_init,
            search_width=self.search_width,
            topk=self.topk,
            allow_non_ascii=self.allow_non_ascii,
            early_stop=True,
            use_prefix_cache=True,
            filter_ids=True,
            verbosity="WARNING",  # Suppress nanoGCG's own logging
            seed=42
        )
        
        yield b"[PROGRESS] 5\n"
        yield "Running nanoGCG optimization...\n".encode("utf-8")
        yield "This may take several minutes depending on model size and num_steps.\n\n".encode("utf-8")
        
        try:
            # Run nanoGCG optimization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: nanogcg.run(self.model, self.tokenizer, user_prompt, target_output, config)
            )
            
            best_adv_string = result.best_string
            best_loss = result.best_loss
            total_steps = len(result.losses)
            
            yield b"[PROGRESS] 90\n"
            yield ("\n" + "=" * 60 + "\n").encode("utf-8")
            yield "Optimization Complete!\n".encode("utf-8")
            yield ("=" * 60 + "\n").encode("utf-8")
            yield f"Best adversarial suffix: {best_adv_string}\n".encode("utf-8")
            yield f"Final loss: {best_loss:.4f}\n".encode("utf-8")
            yield f"Total iterations: {total_steps}\n".encode("utf-8")
            yield f"Loss history: {result.losses[-10:]}\n\n".encode("utf-8")
            
        except Exception as e:
            yield f"Error during nanoGCG optimization: {e}\n".encode("utf-8")
            traceback.print_exc()
            best_adv_string = adv_string_init
            yield b"[PROGRESS] 90\n"
        
        # Test the attack
        yield b"Testing adversarial prompt:\n"
        test_prompt = f"{user_prompt} {best_adv_string}"
        yield f"Prompt: {test_prompt}\n\n".encode("utf-8")
        yield b"Generating response...\n\n"
        yield b"[PROGRESS] 95\n"
        
        try:
            # Tokenize and generate
            inputs = self.tokenizer(test_prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                temperature=1.0,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            yield f"Model response:\n{response}\n".encode("utf-8")
        except Exception as e:
            yield f"Error during generation: {e}\n".encode("utf-8")
            traceback.print_exc()
        
        yield b"[PROGRESS] 100\n"


async def run_gcg_attack(
    model_id: str,
    template: str,
    defense: str,
    session_id: Optional[str] = None,
    num_steps: int = 250,
    search_width: int = 512,
    topk: int = 256
) -> AsyncGenerator[bytes, None]:
    """
    Run GCG attack with defense checking and streaming output.
    
    Args:
        model_id: HuggingFace model ID
        template: User prompt to attack
        defense: Defense mechanism to apply
        session_id: Session ID for history tracking
        num_steps: Number of optimization steps (default: 250, recommended by nanoGCG)
        search_width: Number of candidate sequences to test per iteration (default: 512)
        topk: Top-k tokens to consider (default: 256)
    
    Yields:
        Bytes containing progress updates and results
    """
    yield b"[PROGRESS] 0\n"
    
    # Load and combine system prompt
    system_prompt = load_system_prompt("GCG")
    template_to_use = combine_system_and_user_prompt(system_prompt, template) if system_prompt.strip() else template
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Check defense first
    try:
        blocked, resp = await apply_defense(defense, template_to_use, model_id=model_id, device=device, session_id=session_id, skip_progress=True)
        if blocked:
            if resp and isinstance(resp, StreamingResponse):
                async for chunk in resp.body_iterator:
                    yield chunk
            else:
                yield b"Request blocked by defense mechanism\n"
            yield b"[PROGRESS] 100\n"
            return
    except Exception as e:
        yield f"Error in defense check: {e}\n".encode("utf-8")
        traceback.print_exc()
    
    # Load model and tokenizer
    try:
        yield b"[PROGRESS] 1\n"
        yield b"Loading model and tokenizer...\n"
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.pad_token = tokenizer.eos_token
        
        yield b"[PROGRESS] 2\n"
        
        # Use 8-bit quantization for large models
        use_8bit = "7b" in model_id.lower() or "13b" in model_id.lower()
        
        if use_8bit and torch.cuda.is_available():
            yield b"Using 8-bit quantization for large model...\n"
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                quantization_config=quantization_config,
                torch_dtype=torch.float16
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            model = model.to(device)
        
        model.eval()
        yield b"[PROGRESS] 4\n"
        yield b"Model loaded successfully!\n\n"
        
    except Exception as e:
        yield f"Error loading model: {e}\n".encode("utf-8")
        traceback.print_exc()
        yield b"[PROGRESS] 100\n"
        return
    
    # Run attack
    try:
        attack = GCGAttack(
            model=model,
            tokenizer=tokenizer,
            device=device,
            num_steps=num_steps,
            search_width=search_width,
            topk=topk,
            allow_non_ascii=False
        )
        
        # Default target output
        target_output = "Sure, here is a response to your request"
        
        async for chunk in attack.attack(template_to_use, target_output):
            yield chunk
            
    except Exception as e:
        yield f"\nError during attack: {e}\n".encode("utf-8")
        traceback.print_exc()
        yield b"[PROGRESS] 100\n"
    finally:
        # Cleanup
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
