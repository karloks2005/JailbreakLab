import os
from typing import AsyncGenerator, Optional

import torch
from fastapi.responses import StreamingResponse
from torch import nn
from transformers import AutoTokenizer, AutoModel
from ...attacks.system_prompt_helper import load_defense_prompt


CHECKPOINT_NAME = "masked_defender.pth"  # Change this to your actual file name that represents your trained model
                                         # It is by default set to our provided model file

class MaskedDefenderClassifier(nn.Module):
    """Classifier matching the architecture used in Colab training.

    Outputs two logits: index 0 = safe, index 1 = unsafe.
    """

    def __init__(self, encoder_name: str):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(encoder_name)
        enc_hidden = self.encoder.config.hidden_size
        self.classifier = nn.Sequential(
            nn.Linear(enc_hidden, 384),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(384, 2),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = outputs.last_hidden_state
        mask = attention_mask.unsqueeze(-1).float()
        masked = last_hidden * mask
        pooled = masked.sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
        logits = self.classifier(pooled)
        return logits


_MODEL: Optional[MaskedDefenderClassifier] = None
_TOKENIZER: Optional[AutoTokenizer] = None


def _get_model_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, CHECKPOINT_NAME)


def _load_defender(device: str = "cpu") -> tuple[MaskedDefenderClassifier, AutoTokenizer]:
    """Load the pretrained classifier and tokenizer from `masked_defender.pth`.

    The model is cached at module level so we only hit disk and
    instantiate the encoder once.
    """

    global _MODEL, _TOKENIZER
    if _MODEL is not None and _TOKENIZER is not None:
        return _MODEL, _TOKENIZER

    ckpt_path = _get_model_path()
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Masked defender checkpoint not found at {ckpt_path}")

    ckpt = torch.load(ckpt_path, map_location=torch.device(device))
    encoder_name = ckpt["encoder_name"]

    tokenizer = AutoTokenizer.from_pretrained(encoder_name)
    model = MaskedDefenderClassifier(encoder_name)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    _MODEL = model
    _TOKENIZER = tokenizer
    return _MODEL, _TOKENIZER


def _classify_prompt(prompt: str, device: str = "cpu") -> dict:
    """Run the classifier on a single prompt and return defense-style dict."""
    # Load defense prompt and combine with prompt
    defense_prompt = load_defense_prompt("masked_defender")
    prompt_to_check = prompt
    if defense_prompt.strip():
        prompt_to_check = f"{defense_prompt}\n\n{prompt}"

    model, tokenizer = _load_defender(device=device)

    encoded = tokenizer(
        [prompt_to_check],
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )

    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)

    with torch.no_grad():
        logits = model(input_ids, attention_mask)  # [1, 2]
        probs = torch.softmax(logits, dim=-1)[0]   # [2]
        prob_safe = probs[0].item()
        prob_unsafe = probs[1].item()

    is_safe = prob_safe >= prob_unsafe
    confidence = prob_safe if is_safe else prob_unsafe

    return {
        "text": prompt,
        "confidence": confidence,
        "is_safe": is_safe,
        # No masking applied here, so full retention
        "retention_ratio": 1.0,
    }


async def run(prompt: str) -> Optional[StreamingResponse]:
    """Evaluate a prompt using the Colab-trained masked_defender classifier.

    Always uses the pretrained weights from `masked_defender.pth`.
    Returns None when the prompt is safe so downstream processing continues,
    or a small StreamingResponse when blocked.
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"
    result = _classify_prompt(prompt, device=device)

    if result["is_safe"]:
        return None

    confidence = result.get("confidence", 0.0)

    async def blocked_stream() -> AsyncGenerator[bytes, None]:
        msg = f"BLOCKED_PROMPT:\n{prompt}\n"
        yield msg.encode("utf-8")
        yield b"Blocked input\n"

    return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")