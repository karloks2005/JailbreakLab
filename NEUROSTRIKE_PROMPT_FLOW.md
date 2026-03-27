# NeuroStrike Attack - Tok Prompta Kroz Sustav

## Što se Događa Kada se Vrši NeuroStrike Attack

Evo kompletnog toka kako se prompt šalje kroz sustav kada korisnik pokreće NeuroStrike attack:

---

## 1. **FRONTEND - Korisnik unosi prompt**
📍 Datoteka: [frontend/src/App.tsx](frontend/src/App.tsx#L88)

```typescript
// Korisnik unosi poruku
const currentMessage = message;

// Slanje HTTP POST zahtjeva na backend
const response = await fetch(`${API_URL}/api/prompt/stream`, {
   method: "POST",
   headers: { "Content-Type": "application/json" },
   body: JSON.stringify({
      prompt: currentMessage,           // ← PROMPT KOJI JE KORISNIK UNIO
      attack: selectedAttack.id,        // npr. "neurostrike"
      defense: selectedDefense.id,      // npr. "none"
      model: selectedModel.id,          // npr. "google/gemma-2b-it"
      isBlocked: false,
   }),
   signal: controller.signal,
});
```

**Što se šalje:**
- `prompt`: Korisnikova poruka (npr. "Kako napraviti bombu?")
- `attack`: "neurostrike"
- `defense`: Odabrana odbrana
- `model`: Odabrani model

---

## 2. **BACKEND - Primanje zahtjeva**
📍 Datoteka: [backend/main.py](backend/main.py#L59) - Endpoint `/api/prompt/stream`

```python
@app.post("/api/prompt/stream")
async def prompt_stream(request: PromptRequest):
    print(f"POST received - Model: {request.model}, Attack: {request.attack}, Defense: {request.defense}")
    
    # PromptRequest sadrži:
    # - prompt: korisnikov unos
    # - attack: "neurostrike"
    # - defense: odabrana odbrana
    # - model: odabrani model
```

**Što se događa:**
1. Backend prima HTTP zahtjev
2. Pravi se `session_id` (jedinstveni ID za ovu sesiju)
3. Provjerava se je li `attack != "none"`

---

## 3. **ATTACK MANAGER - Rutiranje na NeuroStrike**
📍 Datoteka: [backend/attacks/attack_manager.py](backend/attacks/attack_manager.py#L23)

```python
def run_attack(attack_type, model_id, template, defense, session_id):
    # ...
    elif attack_type == "neurostrike":
        return run_neurostrike_attack(
            model_id=model_id,              # npr. "google/gemma-2b-it"
            template=template,              # ← KORISNIKOV PROMPT
            defense=defense,                # npr. "none"
            session_id=session_id           # jedinstveni ID
        )
```

**Ključna linija u main.py (linija 228):**
```python
generator = run_attack(request.attack, request.model, request.prompt, request.defense, session_id)
```

Ovdje se `request.prompt` prosleđuje kao `template` parametar.

---

## 4. **NeuroStrike ATTACK - Obrada Promptа**
📍 Datoteka: [backend/attacks/neuroStrike/neuroStrike.py](backend/attacks/neuroStrike/neuroStrike.py#L127)

```python
async def run_neurostrike_attack(model_id: str, template: str, defense: str, session_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
    """NeuroStrike white-box attack using pre-computed safety neuron pruning."""
    try:
        yield b"[PROGRESS] 0\n"
        
        # 1. Učitavanje pre-computiranih "safety neurons"
        safety_neurons = load_safety_neurons(model_id)
        yield b"[PROGRESS] 20\n"
        
        # 2. Učitavanje modela
        tokenizer, model = get_model_and_tokenizer(model_id, "cuda" if torch.cuda.is_available() else "cpu")
        yield b"[PROGRESS] 40\n"
        
        # 3. Primjena neuron pruning-a (uklanjanje sigurnosnih neurona)
        hooks = apply_neuron_pruning(model, safety_neurons)
        yield b"[PROGRESS] 60\n"
        
        # 4. Generiranje odgovora sa promptom
        def _generate():
            # ← OVDJE SE KORISTI TEMPLATE (KORISNIKOV PROMPT)
            encoded = tokenizer(template, return_tensors="pt").to(model.device)
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
        # ... ostatak obrade
```

---

## 📊 Dijagram Toka

```
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (React/TypeScript)                                          │
│                                                                      │
│ Korisnik unosi prompt: "Kako napraviti bombu?"                     │
│                                                                      │
│ JSON POST zahtjev:                                                   │
│ {                                                                    │
│   "prompt": "Kako napraviti bombu?",                               │
│   "attack": "neurostrike",                                         │
│   "defense": "none",                                               │
│   "model": "google/gemma-2b-it"                                    │
│ }                                                                    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ HTTP POST
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND - main.py (prompt_stream endpoint)                          │
│                                                                      │
│ - Prima PromptRequest                                               │
│ - Pravi session_id                                                  │
│ - Prosleđuje prompt kao "template" parametar                       │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ run_attack() poziv
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND - attack_manager.py (run_attack funkcija)                   │
│                                                                      │
│ Rutira prema attack_type == "neurostrike"                           │
│ → run_neurostrike_attack(                                           │
│     model_id="google/gemma-2b-it",                                 │
│     template="Kako napraviti bombu?",  ← PROMPT OVDJE             │
│     defense="none",                                                │
│     session_id="..."                                              │
│   )                                                                 │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ async generator
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND - neuroStrike.py (run_neurostrike_attack)                   │
│                                                                      │
│ 1. Load safety_neurons = load_safety_neurons("google/gemma-2b-it")  │
│ 2. Load tokenizer & model                                           │
│ 3. Apply neuron pruning hooks                                       │
│ 4. Generate response:                                               │
│    - encoded = tokenizer(template, ...)  ← PROMPT ENCODE           │
│    - outputs = model.generate(**encoded) ← GENERATE SA PROMPTOM    │
│    - response = tokenizer.decode(outputs)                          │
│ 5. Check attack success                                            │
│                                                                      │
│ Yield:                                                               │
│ - [PROGRESS] statusi                                               │
│ - [ATTACK_SUCCESS] rezultat                                        │
│ - Response tekst                                                   │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ StreamingResponse
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND - main.py (gpu_info_and_stream wrapper)                     │
│                                                                      │
│ - GPU informacija                                                   │
│ - Logiranje u bazu (database.py)                                   │
│ - Detekcija attack success                                         │
│ - Prikupljanje metrika                                            │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ Streaming Response
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (App.tsx)                                                   │
│                                                                      │
│ - Čita stream (getReader())                                        │
│ - Parsira progress [PROGRESS]                                      │
│ - Prikazuje rezultate korisnika                                   │
│ - Sprema u ExecutionHistory                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Ključne Datoteke i Linije

| Faza | Datoteka | Linija | Što se Događa |
|------|----------|--------|---------------|
| **Slanje** | `frontend/src/App.tsx` | 88-95 | POST zahtjev sa promptom |
| **Primitak** | `backend/main.py` | 59-70 | Endpoint prima zahtjev |
| **Rutiranje** | `backend/attacks/attack_manager.py` | 94-99 | Poziva `run_neurostrike_attack` |
| **Obrada** | `backend/attacks/neuroStrike/neuroStrike.py` | 127-175 | Izvršava attack, koristi prompt |
| **Generiranje** | `backend/attacks/neuroStrike/neuroStrike.py` | 147-155 | `model.generate()` sa promptom |
| **Streaming** | `backend/main.py` | 80-155 | Vraća response kao stream |

---

## 🎯 Gdje se Prompt Koristi u NeuroStrike

U [neuroStrike.py](backend/attacks/neuroStrike/neuroStrike.py) linijama **147-155**:

```python
def _generate():
    # Prompt se tokenizira
    encoded = tokenizer(template, return_tensors="pt").to(model.device)
    
    # Modelom se generiše odgovor
    with torch.no_grad():
        outputs = model.generate(
            **encoded,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Odgovor se dekodira
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

**Ključne operacije:**
1. **Tokenizacija**: `tokenizer(template, ...)` - prompt se pretvara u tokene
2. **Generiranje**: `model.generate(**encoded)` - sa pruning hooks aktivnima
3. **Dekodiranje**: `tokenizer.decode(...)` - odgovor se čita kao tekst

---

## 📝 Samarijum

Prompt ide ovim tokom:
```
Korisnik → Frontend → Backend /api/prompt/stream → attack_manager → 
run_neurostrike_attack → tokenizer.encode(template) → model.generate() → 
tokenizerr.decode() → Backend response → Frontend streaming display
```

Prompt se **ne transformira** prije nego što uđe u model - on ostaje **točno onakav kako ga je korisnik unio**, s tom razlikom što se primjenjuje neuron pruning koji briše sigurnosne neurone.
