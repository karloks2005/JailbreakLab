import os
from typing import AsyncGenerator, Optional

import torch
from fastapi.responses import StreamingResponse
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from ...attacks.system_prompt_helper import load_defense_prompt


_CLASSIFIER = None
_MODEL_NAME = "leolee99/PIGuard"


def _load_classifier(device: str = "cpu"):
    """Load the PIGuard classifier from Hugging Face.

    The model is cached at module level so we only hit the network once.
    """
    global _CLASSIFIER

    if _CLASSIFIER is not None:
        return _CLASSIFIER

    tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        _MODEL_NAME, trust_remote_code=True
    )

    # Move model to the appropriate device
    if device != "cpu":
        model = model.to(device)

    _CLASSIFIER = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        device=0 if device != "cpu" and torch.cuda.is_available() else -1,
    )

    return _CLASSIFIER


async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    PIGuard defense: Uses a fine-tuned transformer model to detect prompt injection attacks.
    Returns a StreamingResponse if injection is detected, otherwise None.
    """
    # Load defense prompt and combine with prompt
    defense_prompt = load_defense_prompt("piguard")
    prompt_to_check = prompt
    if defense_prompt.strip():
        prompt_to_check = f"{defense_prompt}\n\n{prompt}"

    try:
        classifier = _load_classifier(device="cpu")
        result = classifier([prompt_to_check])[0]

        label = result.get("label", "").lower()
        score = result.get("score", 0.0)

        # Check if it's an injection
        is_injection = any(keyword in label for keyword in ["injection", "unsafe", "label_1"])

        if is_injection:
            async def blocked_stream() -> AsyncGenerator[bytes, None]:
                msg = f"BLOCKED_PROMPT:\n{prompt}\n"
                yield msg.encode("utf-8")
                confidence = score * 100
                yield f"PIGuard detected prompt injection (confidence: {confidence:.1f}%)\n".encode("utf-8")
                yield b"Blocked input\n"

            return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")

    except Exception:
        pass

    return None
