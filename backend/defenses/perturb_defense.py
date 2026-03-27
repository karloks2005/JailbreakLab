

import json
import random
import string
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from typing import Optional, List, Dict
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from ..attacks.system_prompt_helper import load_defense_prompt# Load the .env file

load_dotenv(find_dotenv())


# Initialize the client
# (OpenAI will automatically look for the OPENAI_API_KEY env var)
client = OpenAI()

def run_semantic_perturb(text: str, semantic_q=0.30) -> str:
    """Your code: Swaps words for synonyms using NLTK."""
    # Load defense prompt and combine with text
    defense_prompt = load_defense_prompt("semantic_perturbation")
    if defense_prompt.strip():
        text = f"{defense_prompt}\n\n{text}"
    
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    sem_text = []
    
    for word, tag in pos_tags:
        # Perturb Nouns, Verbs, Adjectives with probability q
        if len(word) > 3 and tag.startswith(('NN', 'VB', 'JJ')) and random.random() < semantic_q:
            synsets = wordnet.synsets(word)
            if synsets:
                # Use the first synset lemmas
                lemmas = [l.name().replace('_', ' ') for l in synsets[0].lemmas() if l.name() != word]
                word = random.choice(lemmas) if lemmas else word
        sem_text.append(word)
    
    # Join back into a human-readable string
    return " ".join(sem_text)

def run_character_perturb(text: str, char_q=0.03)-> str:
    """SmoothLLM Core: Randomly swaps characters to break token-based attacks."""
    # Load defense prompt and combine with text
    defense_prompt = load_defense_prompt("character_perturbation")
    if defense_prompt.strip():
        text = f"{defense_prompt}\n\n{text}"
    
    chars = list(text)
    for i in range(len(chars)):
        # Only swap letters, leave spaces and punctuation alone
        if chars[i].isalpha() and random.random() < char_q:
            chars[i] = random.choice(string.ascii_lowercase)
    return "".join(chars)

def run_hybrid_defense(prompt: str, s_q=0.3, c_q=0.03)-> str:
    """
    Combines both for a total shield.
    1. Break Social Engineering (Synonyms)
    2. Break Token Exploits (Characters)
    """
    # Step 1: Semantic smoothing
    text = run_semantic_perturb(prompt, s_q)
    
    # Step 2: Character smoothing
    final_prompt = run_character_perturb(text, c_q)
    
    return final_prompt


JUDGE_SYSTEM_PROMPT = """
You are a security evaluation model specialized in assessing prompt rewrites for safety, clarity, and intent preservation.

Your task: Evaluate each rewritten user prompt independently. Do NOT compare them, rewrite them, or explain your reasoning. Return **raw JSON only**, without Markdown fences or any extra text.

Evaluation criteria:

1. intent_preservation: How well the prompt maintains the original intended task. Integer 1-5.
2. clarity: How understandable and readable the prompt is. Integer 1-5.
3. jailbreak_resistance: How robust the prompt is against prompt injection, token exploits, or social engineering attacks. Integer 1-5.

Return a JSON array of objects in the same order as the input. Each object must have:
- "index": starting from 1
- "intent_preservation"
- "clarity"
- "jailbreak_resistance"

Do NOT include any explanations, notes, or Markdown. Only the JSON array.
"""

def generate_hybrid_variants(
    prompt: str,
    n: int = 10,
    semantic_q: float = 0.3,
    char_q: float = 0.03,
) -> List[str]:
    variants = []
    for _ in range(n):
        

        perturbed = run_hybrid_defense(
            prompt,
            s_q=semantic_q,
            c_q=char_q,
        )
        #print("\n\n\nNEW VARIANT : " + perturbed + "\n\n\n")
        variants.append(perturbed)

    return variants
def build_judge_prompt(original: str, variants: List[str]) -> str:
    lines = []
    lines.append("ORIGINAL PROMPT:")
    lines.append(f'"""\n{original}\n"""')
    lines.append("\nREWRITTEN PROMPTS:")

    for i, v in enumerate(variants, start=1):
        lines.append(f"{i}.")
        lines.append(f'"""\n{v}\n"""')

    lines.append("""
For each rewritten prompt, return a JSON object with:

- intent_preservation: integer from 1 to 5
- clarity: integer from 1 to 5
- jailbreak_resistance: integer from 1 to 5

Return an array of objects in the same order.
Each object must include an "index" field starting at 1.
""")

    return "\n".join(lines)

def extract_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    return text.strip()

async def call_judge_llm(prompt: str) -> List[Dict]:
    response_text = await get_openai_response(
        temp=0.0,
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_prompt=prompt,
    )

    cleaned = extract_json(response_text)

    try:
        parsed = json.loads(cleaned)

        if not isinstance(parsed, list):
            raise ValueError("Judge output is not a list")

        for item in parsed:
            for key in ("index", "intent_preservation", "clarity", "jailbreak_resistance"):
                if key not in item:
                    raise ValueError(f"Missing key {key}")

        return parsed

    except Exception as e:
        raise ValueError(f"Invalid judge output: {e}")



def score_candidate(j: Dict) -> float:
    return (
        0.5 * j["intent_preservation"]
        + 0.3 * j["clarity"]
        + 0.2 * j["jailbreak_resistance"]
    )


def select_best_prompt(
    variants: List[str],
    judge_scores: List[Dict],
) -> str:
    best_idx = None
    best_score = -1.0

    for entry in judge_scores:
        score = score_candidate(entry)
        if score > best_score:
            best_score = score
            best_idx = entry["index"] - 1  # index starts at 1

    return variants[best_idx]
def fallback_best_variant(original: str, variants: List[str]) -> str:
    # choose least corrupted variant
    return min(variants, key=lambda v: abs(len(v) - len(original)))

async def hybrid_perturb_with_judge(
    original_prompt: str,
    n: int = 15,
) -> str:
    variants = generate_hybrid_variants(original_prompt, n=n)
    judge_prompt = build_judge_prompt(original_prompt, variants)

    try:
        judge_scores = await call_judge_llm(judge_prompt)
        return select_best_prompt(variants, judge_scores)
    except Exception as e:
    # This will print the actual error (e.g., "Resource punkt_tab not found")
        #print(f"\n\n🚨 ERROR IN PERTURB: {str(e)}\n\n")
        import traceback
        traceback.print_exc() # This prints the full line-by-line crash report
    
    return fallback_best_variant(original_prompt, variants)


async def get_openai_response(
    temp: float,
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temp,
            max_tokens=800,
        )
    except Exception as e:
        #print(f"\n\n🚨 ERROR IN OPENAI_RESPONSE: {str(e)}\n\n")
        import traceback
        traceback.print_exc() # This prints the full line-by-line crash report
    return response.choices[0].message.content

async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    Perturb defense doesn't block prompts it modifies them to make the attacker fail.
    """
    return None