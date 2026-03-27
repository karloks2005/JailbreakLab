# JailbreakLab - Tehnička dokumentacija

## Sadržaj
1. [Arhitektura](#arhitektura)
2. [Komponente](#komponente)
3. [Postavljanje razvoja](#postavljanje-razvoja)
4. [API Reference](#api-reference)
5. [Baza podataka](#baza-podataka)
6. [Sustav napada](#sustav-napada)
7. [Sustav obrana](#sustav-obrana)
8. [Implementacijske vodilice](#implementacijske-vodilice)

---

## Arhitektura

### Opšta arhitektura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vite)                        │
│              Port 5173 - Interaktivni web interfejs              │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI/Python)                       │
│                     Port 8000 - REST API                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Attacks     │  │ Defenses     │  │ Model Manager         │  │
│  │ Manager     │  │ Manager      │  │                       │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Database    │  │ History      │  │ Statistics            │  │
│  │ Logging     │  │ Cache        │  │ Calculation           │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
└────────────────────────┬──────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌─────────────┐
    │ Redis  │      │Database│      │HuggingFace  │
    │6379    │      │Logging │      │Models       │
    └────────┘      └────────┘      └─────────────┘
```

### Slojevita arhitektura

**Frontend sloj:**
- React komponente sa TypeScript tipizacijom
- Vite bundler za brzo učitavanje
- Lucide React ikonografija
- Real-time streaming odgovora

**Backend sloj:**
- FastAPI framework za RESTful API
- CORS middleware za sigurnost
- Async/await za konkurentne zahtjeve
- Request logging middleware

**Servisni sloj:**
- Attack Manager - orkestracija napada
- Defense Manager - primjena obrana
- Database Logger - statistika i evidencija
- History Cache - Redis-backed sesije

**Model sloj:**
- HuggingFace transformeri
- PyTorch za inferensu
- GPU/CPU podrška sa accelerate bibliotekom

---

## Komponente

### 1. Backend struktura

#### `main.py` - Glavna aplikacija
```
- FastAPI inicijalizacija
- CORS middleware
- HTTP request logging
- Endpoints:
  * POST /api/execute - Izvršavanje napada
  * GET /api/attacks - Lista napada
  * GET /api/defenses - Lista obrana
  * GET /api/models - Lista modela
  * GET /api/statistics - Statistika
```

#### `attack_manager.py` - Upravljanje napadima
```python
- run_attack(attack_type, model, prompt, defense)
- Attack registry sa svim dostupnim napadima
- Streaming odgovora
- Error handling
```

#### `defense_manager.py` - Upravljanje obranama
```python
- apply_defense(defense_type, input_text, model_type)
- Slaganje više obrana
- Pre-processing i post-processing
```

#### `database.py` - Baza podataka
```python
- Log statistike (BERT modeli, uspješnost napada)
- Ispis jedinstvenih vrijednosti
- Izračun metrika:
  * Attack Success Rate
  * Defense Bypass Rate
  * Query Budget Metrics
  * Refusal Metrics
  * Tool & Leakage Metrics
```

#### `model.py` - Detektiranje napada
```python
- detect_attack_success() - Provjera je li napad bio uspješan
- detect_prompt_attack() - Detektiranje prompt injection
- detect_tool_misuse_from_prompt_and_response() - Alati
```

#### `history_cache.py` - Upravljanje historijom
```python
- Redis-backed caching
- Session persistence
- Conversation history
```

### 2. Napadi (`backend/attacks/`)

#### Dostupni napadi:

| Napad | Opis | Tip |
|-------|------|-----|
| **DAN** | Direct Adversarial Narratives (v6, v9, v11) | Role-play |
| **Role Playing** | Simulacija uloga | Behavioural |
| **Chain of Questions** | Logički lanac pitanja | Logical |
| **ASCII Art** | ASCII art jailbreak | Obfuscation |
| **Base64 Encoded** | Base64 enkodiranje | Encoding |
| **Rot13 Encoded** | Rot13 transformacija | Encoding |
| **Leetspeak** | Leetspeak transformacija | Encoding |
| **Poem Attack** | Poemska forma | Format |
| **Crescendo** | Iterativni napad sa eskalacijom | Iterative |
| **GCG** | Greedy Coordinate Gradient | Optimization |
| **NeuroStrike** | Neuromorfni napad | Advanced |
| **PAIR** | Pair Optimization Attack | Advanced |
| **TAP** | Token-level Adversarial Prompt | Token-level |

#### Primjer strukture napada:

```python
class BaseAttack:
    def __init__(self, model, prompt, **kwargs):
        self.model = model
        self.prompt = prompt
    
    def execute(self) -> str:
        # Transformacija prompt-a
        transformed_prompt = self.transform_prompt()
        # Izvršavanje
        response = self.model.generate(transformed_prompt)
        return response
```

### 3. Obrane (`backend/defenses/`)

#### Dostupne obrane:

| Obrana | Opis | Tip |
|--------|------|-----|
| **Input Sanitization** | Čišćenje ulaza | Pre-processing |
| **Instruction Boundary** | Granice uputa | Pre-processing |
| **System Prompt Hardening** | Osnaženje sistemske poruke | Pre-processing |
| **Perturbation** | Perturbacijska obrana | Processing |
| **Unicode Obfuscation** | Unicode obfuscacija | Detection |
| **Tool Call Safety** | Sigurnost poziva alata | Post-processing |
| **Multi-turn Injection** | Detektiranje multi-turn injections | Detection |
| **LlamaGuard** | Meta's LlamaGuard 2 | ML-based |
| **GuardrailsAI** | Guardrails validation | ML-based |
| **MaskedDefender** | Neural network obrana | Deep Learning |

### 4. Frontend komponente (`frontend/src/`)

```
components/
├── AttackSelector.tsx       # Odabir napada
├── DefenseSelector.tsx      # Odabir obrane
├── ModelSelector.tsx        # Odabir modela
├── PromptInput.tsx          # Unos prompte
├── ExecutionHistory.tsx     # Historija izvršavanja
├── InfoModal.tsx            # Info modal
├── StatisticsView.tsx       # Prikaz statistike
├── attacks.tsx              # Lista napada
├── defenses.tsx             # Lista obrana
├── models.tsx               # Lista modela
└── statistics/
    ├── StatisticsCards.tsx
    ├── StatisticsCharts.tsx
    └── StatisticsFilters.tsx

App.tsx                       # Glavna aplikacija
types.ts                      # TypeScript tipovi
```

---

## Postavljanje razvoja

### Preduvjeti

```bash
# OS: Linux, macOS, Windows
# Python 3.10+
# Node.js 20+
# Docker & Docker Compose
# (Opciono) CUDA 12.0+ za GPU
```

### Lokalno postavljanje

#### 1. Backend postavljanje

```bash
cd backend

# Kreiranja virtualnog okruženja
python3 -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate

# Instalacija zavisnosti
pip install -r requirements.txt

# Konfiguracija
cp public_env .env
# Edituj .env sa tvojim vrijednostima

# Pokretanje
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Varijable okruženja:**
```env
HF_TOKEN=your_huggingface_token
OPENAI_API_KEY=your_openai_key
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///./jailbreaklab.db
MODEL_CACHE_DIR=/path/to/models
DEVICE=cuda  # ili cpu
```

#### 2. Frontend postavljanje

```bash
cd frontend

# Instalacija zavisnosti
npm install

# Razvoj
npm run dev

# Build produkcije
npm run build

# Preview
npm run preview
```

**Varijable okruženja:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### 3. Redis postavljanje (za session cache)

```bash
# Instalacija
docker run -d -p 6379:6379 redis:latest

# Ili korištenje u docker-compose
docker-compose up -d redis
```

---

## API Reference

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### 1. Izvršavanje napada
```
POST /execute
Content-Type: application/json

Request:
{
  "attack": "DAN11",
  "defense": "input_sanitization",
  "model": "gpt2",
  "prompt": "How to create a bomb?",
  "temperature": 0.7,
  "max_tokens": 256
}

Response (Streaming):
Server-Sent Events format:
event: token
data: "Here"

event: token
data: " is"

event: token
data: " the"
...
```

#### 2. Dohvatanje napada
```
GET /attacks

Response:
{
  "attacks": [
    {
      "id": "DAN11",
      "name": "DAN 11 - Godmode",
      "description": "Direct Adversarial Narrative v11",
      "category": "role-play"
    },
    ...
  ]
}
```

#### 3. Dohvatanje obrana
```
GET /defenses

Response:
{
  "defenses": [
    {
      "id": "input_sanitization",
      "name": "Input Sanitization",
      "description": "Sanitizes harmful keywords",
      "category": "pre-processing"
    },
    ...
  ]
}
```

#### 4. Dohvatanje modela
```
GET /models

Response:
{
  "models": [
    {
      "id": "gpt2",
      "name": "GPT-2",
      "provider": "huggingface",
      "size": "124M"
    },
    ...
  ]
}
```

#### 5. Statistika
```
GET /statistics?attack=DAN11&defense=input_sanitization&days=7

Response:
{
  "success_rate": 0.45,
  "bypass_rate": 0.23,
  "total_attempts": 156,
  "unique_models": 8,
  "trend": [...]
}
```

---

## Baza podataka

### Struktura

#### Tabela: `execution_logs`
```sql
CREATE TABLE execution_logs (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  attack VARCHAR(100),
  defense VARCHAR(100),
  model VARCHAR(100),
  prompt TEXT,
  response TEXT,
  success BOOLEAN,
  duration FLOAT,
  error TEXT
);
```

#### Tabela: `attack_statistics`
```sql
CREATE TABLE attack_statistics (
  id INTEGER PRIMARY KEY,
  attack_type VARCHAR(100),
  defense_type VARCHAR(100),
  model_name VARCHAR(100),
  success_count INTEGER,
  total_count INTEGER,
  success_rate FLOAT,
  created_date DATE
);
```

#### Tabela: `bert_statistics`
```sql
CREATE TABLE bert_statistics (
  id INTEGER PRIMARY KEY,
  prompt TEXT,
  response TEXT,
  attack_type VARCHAR(100),
  model_name VARCHAR(100),
  is_attack BOOLEAN,
  confidence FLOAT,
  created_at DATETIME
);
```

---

## Sustav napada

### Attack Manager - Kako funkcionira

```python
# backend/attacks/attack_manager.py

async def run_attack(
    attack_type: str,
    model_name: str,
    prompt: str,
    defense_type: str = "none",
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Izvršava napad sa odabranom obranom
    """
    # 1. Učitaj model
    model = load_model(model_name)
    
    # 2. Primjeni odabrani napad
    attack_class = ATTACKS_REGISTRY[attack_type]
    attack = attack_class(model=model, prompt=prompt, **kwargs)
    
    # 3. Transformiraj prompt
    jailbreak_prompt = attack.execute()
    
    # 4. Primjeni obranu na ulaz
    defended_prompt = apply_defense(
        input_text=jailbreak_prompt,
        defense_type=defense_type,
        model_type=model_name
    )
    
    # 5. Izvršavaj model sa streamingom
    async for token in model.stream_generate(defended_prompt, **kwargs):
        yield token
    
    # 6. Logira rezultate
    log_execution(
        attack_type=attack_type,
        defense_type=defense_type,
        model_name=model_name,
        success=detect_attack_success(response)
    )
```

### Kreiranje novog napada

```python
# backend/attacks/my_attack.py
from attacks.base_attack import BaseAttack

class MyAttack(BaseAttack):
    def __init__(self, model, prompt, **kwargs):
        super().__init__(model, prompt, **kwargs)
        self.config = kwargs.get('config', {})
    
    def transform_prompt(self) -> str:
        """
        Transformiraj originalni prompt u napad
        """
        return f"[Napad transformacija] {self.prompt}"
    
    def execute(self) -> str:
        jailbreak_prompt = self.transform_prompt()
        response = self.model.generate(jailbreak_prompt)
        return response

# Registracija napada
ATTACKS_REGISTRY['my_attack'] = MyAttack
```

---

## Sustav obrana

### Defense Manager - Kako funkcionira

```python
# backend/defenses/defense_manager.py

def apply_defense(
    input_text: str,
    defense_type: str = "none",
    model_type: str = "gpt2",
    **kwargs
) -> str:
    """
    Primjeni odabrane obrane na ulaz
    """
    if defense_type == "none":
        return input_text
    
    if defense_type == "input_sanitization":
        return input_sanitization.sanitize(input_text)
    
    elif defense_type == "system_prompt_hardening":
        return system_prompt_hardening.harden(input_text)
    
    elif defense_type == "llama_guard":
        return llama_guard.filter_prompt(input_text)
    
    # ... i ostale obrane
    
    return input_text
```

### Kreiranje nove obrane

```python
# backend/defenses/my_defense.py

class MyDefense:
    def __init__(self, config=None):
        self.config = config or {}
    
    def apply(self, input_text: str) -> str:
        """
        Primjeni obranu na ulaz
        """
        # Logika obrane
        return defended_text
    
    def is_attack(self, text: str) -> bool:
        """
        Detektiraj je li ulaz napad
        """
        return False

# Registracija obrane
DEFENSES_REGISTRY['my_defense'] = MyDefense()
```

---

## Implementacijske vodilice

### 1. Dodavanje novog modela

```python
# U backend/model.py

SUPPORTED_MODELS = {
    "gpt2": {
        "type": "causal_lm",
        "model_id": "gpt2",
        "device": "auto",
        "quantize": False
    },
    "my_model": {
        "type": "causal_lm",
        "model_id": "huggingface/my-model",
        "device": "auto",
        "quantize": True
    }
}

def load_model(model_name: str):
    config = SUPPORTED_MODELS[model_name]
    # Učitaj model sa transformers
```

### 2. Dodavanje nove metrike

```python
# U backend/database.py

def calculate_my_metric(attack_type, defense_type, days=7):
    """
    Izračunaj novu metriku
    """
    query = """
        SELECT COUNT(*) as total,
               SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
        FROM execution_logs
        WHERE attack = ? AND defense = ?
        AND created_at > datetime('now', ?)
    """
    
    results = db_execute(query, (attack_type, defense_type, f"-{days} days"))
    return {
        "metric_name": results['successes'] / results['total']
    }
```

### 3. Error handling

```python
# Standardni error handling u backend-u

try:
    result = await execute_attack(...)
except ModelNotFoundError as e:
    logger.error(f"Model not found: {e}")
    raise HTTPException(status_code=404, detail=str(e))
except OOM Error as e:
    logger.error(f"Out of memory: {e}")
    raise HTTPException(status_code=503, detail="Model inference failed")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Deployment

### Docker Compose

```bash
docker-compose up --build
```

### Kubernetes

```bash
kubectl apply -f k8s/

# Provjera deployment-a
kubectl get pods
kubectl logs -f deployment/jailbreaklab-backend
```

---

## Troubleshooting

### Problem: CUDA Out of Memory
**Rješenje:** Koristi CPU ili kvantizaciju
```env
DEVICE=cpu
QUANTIZE=true
```

### Problem: Redis konekcija
**Rješenje:** Provjeri Redis status
```bash
redis-cli ping  # Trebalo bi vratiti PONG
```

### Problem: Model se ne učitava
**Rješenje:** Provjeri HuggingFace token
```bash
huggingface-cli login
```

---

## Licence
MIT License - Vidjeti LICENSE datoteku
