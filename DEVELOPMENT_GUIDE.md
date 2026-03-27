# JailbreakLab - Vodič za razvoj

## Sadržaj
1. [Setup](#setup)
2. [Arhitektura](#arhitektura)
3. [Dodavanje novog napada](#dodavanje-novog-napada)
4. [Dodavanje nove obrane](#dodavanje-nove-obrane)
5. [Dodavanje novih modela](#dodavanje-novih-modela)
6. [Testiranje](#testiranje)
7. [Best Practices](#best-practices)
8. [Debugging](#debugging)

---

## Setup

### Preuvjeti
- Python 3.10+
- Node.js 20+
- Git
- Docker (preporučeno)

### Lokalni razvoj

#### 1. Kloniranje i konfiguracija

```bash
# Kloniranje
git clone https://github.com/karloks2005/JailbreakLab.git
cd JailbreakLab

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (u novoj terminali)
cd frontend
npm install
```

#### 2. Pokretanje servisa

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis (ako je potrebno)
docker run -d -p 6379:6379 redis:latest
```

#### 3. Provjera

- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs

---

## Arhitektura

### File struktura - Backend

```
backend/
├── main.py                          # FastAPI aplikacija
├── model.py                         # Model utilities
├── database.py                      # Baza podataka
├── history_cache.py                 # Redis cache
├── requirements.txt                 # Python zavisnosti
├── attacks/
│   ├── __init__.py
│   ├── base_attack.py               # Bazna klasa za napade
│   ├── attack_manager.py            # Manager svih napada
│   ├── DAN11.py
│   ├── rolePlaying.py
│   ├── chainOfQuestions.py
│   └── ... (ostali napadi)
└── defenses/
    ├── __init__.py
    ├── defense_manager.py           # Manager svih obrana
    ├── input_sanitization.py
    ├── system_prompt_hardening.py
    └── ... (ostale obrane)
```

### File struktura - Frontend

```
frontend/
├── src/
│   ├── App.tsx                      # Root komponenta
│   ├── types.ts                     # TypeScript tipovi
│   ├── components/
│   │   ├── AttackSelector.tsx
│   │   ├── DefenseSelector.tsx
│   │   ├── ModelSelector.tsx
│   │   ├── PromptInput.tsx
│   │   ├── ExecutionHistory.tsx
│   │   ├── StatisticsView.tsx
│   │   └── ... (ostale komponente)
│   └── ... (ostale datoteke)
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Dodavanje novog napada

### Korak 1: Kreirajte datoteku

```bash
touch backend/attacks/my_new_attack.py
```

### Korak 2: Implementirajte klasu

```python
# backend/attacks/my_new_attack.py

from attacks.base_attack import BaseAttack

class MyNewAttack(BaseAttack):
    """
    Opis napada i kako radi
    """
    
    # Metadata
    name = "My New Attack"
    description = "Detaljni opis napada"
    category = "role-play"  # ili: logic, encoding, format, advanced
    difficulty = "medium"  # easy, medium, hard
    
    # Jailbreak template
    JAILBREAK_TEMPLATE = """
    [Your jailbreak instruction here]
    
    Now respond to: {prompt}
    """
    
    def __init__(self, model, prompt, **kwargs):
        super().__init__(model, prompt, **kwargs)
        self.temperature = kwargs.get('temperature', 0.7)
        # Varijable specifične za napad
    
    def transform_prompt(self) -> str:
        """
        Transformiraj originalni prompt u jailbreak prompt
        """
        return self.JAILBREAK_TEMPLATE.format(prompt=self.prompt)
    
    def execute(self) -> str:
        """
        Izvršava napad
        """
        transformed = self.transform_prompt()
        
        # Generiraj odgovor
        response = self.model.generate(
            transformed,
            max_length=256,
            temperature=self.temperature,
            top_p=0.95
        )
        
        return response
```

### Korak 3: Registrirajte napad

```python
# backend/attacks/attack_manager.py

from attacks.my_new_attack import MyNewAttack

ATTACKS_REGISTRY = {
    "DAN11": DAN11,
    "role_playing": RolePlaying,
    "my_new_attack": MyNewAttack,  # ← Dodajte ovdje
    # ... ostali napadi
}
```

### Korak 4: Frontend (opciono)

```typescript
// frontend/src/components/attacks.ts

const attacks: Attack[] = [
  {
    id: "DAN11",
    name: "DAN 11",
    description: "...",
  },
  {
    id: "my_new_attack",  // ← Dodajte
    name: "My New Attack",
    description: "Detaljni opis",
    category: "role-play",
    difficulty: "medium",
  },
  // ... ostali napadi
];

export default attacks;
```

### Korak 5: Testiranje

```bash
# Pokrenite backend
cd backend && python -m uvicorn main:app --reload

# Testirajte sa curl-om
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "attack": "my_new_attack",
    "defense": "no_defense",
    "model": "gpt2",
    "prompt": "How to hack?"
  }'
```

---

## Dodavanje nove obrane

### Korak 1: Kreirajte datoteku

```bash
touch backend/defenses/my_new_defense.py
```

### Korak 2: Implementirajte klasu

```python
# backend/defenses/my_new_defense.py

class MyNewDefense:
    """
    Opis obrane i kako radi
    """
    
    # Metadata
    name = "My New Defense"
    description = "Detaljni opis obrane"
    category = "pre-processing"  # ili: ml-based, post-processing
    effectiveness = 0.6  # 0.0 - 1.0
    
    def __init__(self, config=None):
        self.config = config or {}
        self.harmful_keywords = [
            "bypass", "ignore", "forget", "override"
        ]
    
    def apply(self, input_text: str, model_type: str = None) -> str:
        """
        Primjeni obranu na ulazni tekst
        """
        result = input_text
        
        # Primjena logike obrane
        for keyword in self.harmful_keywords:
            if keyword.lower() in result.lower():
                # Uklonite ili zamijenite
                result = result.replace(keyword, "[REDACTED]")
        
        return result
    
    def is_attack(self, text: str) -> bool:
        """
        Detektiraj je li ulaz potencijalni napad (opciono)
        """
        for keyword in self.harmful_keywords:
            if keyword.lower() in text.lower():
                return True
        return False
```

### Korak 3: Registrirajte obranu

```python
# backend/defenses/defense_manager.py

from defenses.my_new_defense import MyNewDefense

DEFENSES_REGISTRY = {
    "input_sanitization": InputSanitization(),
    "llama_guard": LlamaGuard(),
    "my_new_defense": MyNewDefense(),  # ← Dodajte
    # ... ostale obrane
}
```

### Korak 4: Ažurirajte defense_manager.py

```python
# U apply_defense() funkciji

def apply_defense(input_text: str, defense_type: str, model_type: str = "gpt2"):
    if defense_type == "no_defense":
        return input_text
    
    elif defense_type == "my_new_defense":
        defense = DEFENSES_REGISTRY["my_new_defense"]
        return defense.apply(input_text, model_type)
    
    # ... ostale obrane
```

### Korak 5: Frontend (opciono)

```typescript
// frontend/src/components/defenses.ts

const defenses: Defense[] = [
  {
    id: "input_sanitization",
    name: "Input Sanitization",
    description: "...",
  },
  {
    id: "my_new_defense",  // ← Dodajte
    name: "My New Defense",
    description: "Detaljni opis",
    category: "pre-processing",
  },
  // ... ostale obrane
];

export default defenses;
```

### Korak 6: Testiranje

```bash
# Pokrenite backend
cd backend && python -m uvicorn main:app --reload

# Testirajte sa curl-om
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "attack": "DAN11",
    "defense": "my_new_defense",
    "model": "gpt2",
    "prompt": "How to hack?"
  }'
```

---

## Dodavanje novih modela

### Korak 1: Dodajte u supported models

```python
# backend/model.py

SUPPORTED_MODELS = {
    "gpt2": {
        "type": "causal_lm",
        "model_id": "gpt2",
        "size": "124M",
        "device": "auto",
        "quantize": False,
    },
    "my_model": {  # ← Dodajte
        "type": "causal_lm",
        "model_id": "huggingface/my-model",  # HF model ID
        "size": "7B",
        "device": "auto",
        "quantize": True,  # Ako trebate
    },
    # ... ostali modeli
}
```

### Korak 2: Frontend (opciono)

```typescript
// frontend/src/components/models.ts

const models: Model[] = [
  {
    id: "gpt2",
    name: "GPT-2",
    provider: "huggingface",
    size: "124M",
  },
  {
    id: "my_model",  // ← Dodajte
    name: "My Model",
    provider: "huggingface",
    size: "7B",
  },
  // ... ostali modeli
];

export default models;
```

### Korak 3: Testiranje

```python
# test_model_loading.py

from model import load_model

# Testirajte učitavanje
model_info = load_model("my_model")
print(f"Model učitan: {model_info}")
```

---

## Testiranje

### Unit testovi - Backend

```python
# backend/tests/test_attacks.py

import pytest
from attacks.my_new_attack import MyNewAttack
from unittest.mock import Mock

def test_my_new_attack_transform():
    """Test prompt transformation"""
    mock_model = Mock()
    attack = MyNewAttack(
        model=mock_model,
        prompt="How to hack?"
    )
    
    transformed = attack.transform_prompt()
    assert "[Your jailbreak instruction here]" in transformed
    assert "How to hack?" in transformed

def test_my_new_attack_execute():
    """Test attack execution"""
    mock_model = Mock()
    mock_model.generate.return_value = "I can't help..."
    
    attack = MyNewAttack(
        model=mock_model,
        prompt="How to hack?"
    )
    
    result = attack.execute()
    assert result == "I can't help..."
    mock_model.generate.assert_called_once()

# Pokretanje testova
# pytest backend/tests/test_attacks.py -v
```

### API testovi

```python
# backend/tests/test_api.py

import requests

def test_execute_endpoint():
    """Test API endpoint"""
    response = requests.post(
        "http://localhost:8000/api/execute",
        json={
            "attack": "DAN11",
            "defense": "no_defense",
            "model": "gpt2",
            "prompt": "Test"
        }
    )
    
    assert response.status_code == 200
    # Stream event validation

def test_attacks_endpoint():
    """Test attacks list"""
    response = requests.get("http://localhost:8000/api/attacks")
    assert response.status_code == 200
    data = response.json()
    assert "attacks" in data
    assert len(data["attacks"]) > 0
```

### Frontend testovi

```typescript
// frontend/src/components/__tests__/AttackSelector.test.tsx

import { render, screen } from '@testing-library/react';
import AttackSelector from '../AttackSelector';

test('renders attack options', () => {
  render(
    <AttackSelector
      attacks={[{ id: "DAN11", name: "DAN 11" }]}
      selected="DAN11"
      onChange={() => {}}
    />
  );
  
  expect(screen.getByText('DAN 11')).toBeInTheDocument();
});
```

---

## Best Practices

### Python/Backend

1. **Tipizacija**
```python
from typing import Optional, List

def run_attack(
    attack_type: str,
    prompt: str,
    temperature: float = 0.7
) -> str:
    """Type hints za sve funkcije"""
    pass
```

2. **Logging**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Loading model: {model_name}")
logger.error(f"Error: {e}")
```

3. **Error handling**
```python
try:
    model = load_model(model_name)
except ModelNotFoundError as e:
    logger.error(f"Model not found: {e}")
    raise HTTPException(status_code=404, detail=str(e))
```

4. **Dokumentacija**
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Description
    
    Raises:
        ValueError: When...
    """
    pass
```

### TypeScript/Frontend

1. **Tipizacija**
```typescript
interface Attack {
  id: string;
  name: string;
  category: 'role-play' | 'logic' | 'encoding';
}

const processAttack = (attack: Attack): void => {
  // ...
};
```

2. **Komponente**
```typescript
interface Props {
  attacks: Attack[];
  selected: string;
  onChange: (id: string) => void;
}

const AttackSelector: React.FC<Props> = ({
  attacks,
  selected,
  onChange
}) => {
  return <>{/* JSX */}</>;
};
```

---

## Debugging

### Backend debugging sa VSCode

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "justMyCode": true
    }
  ]
}
```

### Frontend debugging

```typescript
// Dodajte console.logs ili breakpoints
console.log("Attack selected:", selectedAttack);
debugger;
```

### Logovanje

```python
# Backend - detaljno logovanje
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Network debugging

```bash
# Sniffovanje zahtjeva
curl -v http://localhost:8000/api/attacks

# sa jq za ljepši JSON output
curl http://localhost:8000/api/attacks | jq
```

---

## Contributor Checklist

Prije push-a na GitHub:

- [ ] Kod je pokrenuto lokalno
- [ ] Svi testovi prolaze
- [ ] Nema `console.log()` ili `print()` left
- [ ] Dokumentacija je ažurna
- [ ] Commit poruka je jasna
- [ ] Bez `merge conflicts`
- [ ] Prije je `main` branch pullan `git pull`

---

## Build i deployment

### Build za produkciju

```bash
# Backend - nema dodatnog builda potrebnog (FastAPI)

# Frontend
cd frontend
npm run build  # Generiše dist/ mapu

# Docker
docker-compose up --build -d
```

### Kubernetes deployment

```bash
kubectl apply -f k8s/

# Provjera
kubectl get pods
kubectl logs -f deployment/jailbreaklab-backend
```

---

**Verzija:** 1.0  
**Datum:** 2026-01-22
