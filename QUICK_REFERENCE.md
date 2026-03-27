# JailbreakLab - Brza Referenca

## 🚀 Brzi početak

### 30 sekundi - Pokretanje s Dockerom
```bash
git clone https://github.com/karloks2005/JailbreakLab.git && cd JailbreakLab
docker-compose up --build
# Otvorite: http://localhost:5173
```

---

## 📋 Česta Pitanja

### P: Trebam li GPU?
**O:** Preporučeno ali nije obavezno. CPU radi, ali sporije.

### P: Koliko vremena trebalo učitavanje modela?
**O:** GPT-2: ~2-5s | OPT-1.3B: ~5-10s | Mistral-7B: ~30-60s (prvi put)

### P: Što se nakon što se model učita?
**O:** Sprema se u RAM za brže pristupe nakon.

### P: Mogu li testirati strane sustave?
**O:** NE! Samo vaše sustave sa dozvolom vlasnika.

### P: Gdje se čuvaju rezultati?
**O:** SQLite baza podataka + Redis cache

### P: Kako dodati novi napad?
**O:** Vidjeti [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md#kreiranje-novog-napada)

---

## 🛠️ Česte naredbe

### Docker
```bash
# Pokretanje
docker-compose up --build

# Background
docker-compose up -d

# Zaustavljanje
docker-compose down

# Pregled logova
docker-compose logs -f

# Restart specifičnog servisa
docker-compose restart backend
```

### Backend (ako razvijate lokalno)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (ako razvijate lokalno)
```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Struktura direktorija

```
JailbreakLab/
├── backend/                     # Python FastAPI
│   ├── attacks/                 # Implementacije napada
│   ├── defenses/                # Implementacije obrana
│   ├── main.py                  # API server
│   └── requirements.txt
├── frontend/                    # React + TypeScript
│   ├── src/components/          # React komponente
│   ├── src/App.tsx              # Root komponenta
│   └── package.json
├── k8s/                         # Kubernetes manifests
├── docker-compose.yml           # Docker Compose config
└── README.md
```

---

## 🔌 API Primjeri

### Izvršavanje napada
```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "attack": "DAN11",
    "defense": "llama_guard",
    "model": "gpt2",
    "prompt": "How to hack?"
  }'
```

### Dohvatanje napada
```bash
curl http://localhost:8000/api/attacks
```

### Dohvatanje obrana
```bash
curl http://localhost:8000/api/defenses
```

### Dohvatanje modela
```bash
curl http://localhost:8000/api/models
```

### Statistika
```bash
curl "http://localhost:8000/api/statistics?days=7&attack=DAN11"
```

---

## 🐛 Rješavanje problema

### Problem: Port zauzet
```bash
# Pronađi proces
lsof -i :5173

# Ubij proces
kill -9 <PID>
```

### Problem: GPU nije dostupan
```env
# .env datoteka
DEVICE=cpu
```

### Problem: Model se ne učitava
```bash
# Provjera HuggingFace konekcije
huggingface-cli login
```

### Problem: Redis konekcija
```bash
# Test Redis-a
docker exec jailbreaklab-redis redis-cli ping
# Trebalo bi vratiti: PONG
```

---

## 📊 Tipični radni tok

```
1. Odaberite MODEL → 2. Odaberite NAPAD → 3. Odaberite OBRANU
     ↓                    ↓                    ↓
  (GPT-2, itd)       (DAN11, itd)        (LlamaGuard, itd)
     
4. Unesite PROMPT → 5. Kliknite TESTIRAJ → 6. Prikupljanje rezultata
     ↓                    ↓                    ↓
  (Pitanja)          (Streaming)           (Analiza)

7. Pregled STATISTIKE → 8. Analiza → 9. Zaključci
     ↓                    ↓             ↓
  (Grafikon)        (Success rate)   (Izvještaj)
```

---

## 🧠 Razumijevanje napada

| Tip | Primjer | Efektivnost | Obrana |
|-----|---------|-------------|--------|
| **Role-play** | DAN11 | Srednja (45-65%) | System hardening |
| **Logika** | Chain of Questions | Visoka (60-80%) | Multi-turn detection |
| **Obfuskacija** | Base64 | Niska (10-30%) | Tokenization |
| **Napredna** | GCG | Vrlo visoka (80%+) | ML-based |

---

## 🛡️ Razumijevanje obrana

| Obrana | Brzina | Sigurnost | Best For |
|--------|--------|-----------|----------|
| Sanitization | Brza | Srednja | Prerada keywords |
| Hardening | Brza | Srednja | Osnaženje uputa |
| LlamaGuard | Srednja | Visoka | ML klasifikacija |
| MaskedDefender | Spora | Vrlo visoka | Dubinska analiza |

---

## 📈 Čitanje statistike

### Success Rate
```
0-30%:   Obrana je vrlo efektivna
30-60%:  Obrana je dijelomično efektivna
60%+:    Model je ranjiv
```

### Bypass Rate
```
0-20%:   Obrana je odličnih
20-50%:  Obrana je dobar
50%+:    Obrana treba poboljšanja
```

---

## 🔐 Sigurnosni savjeti

✅ **Činite:**
- Testirajte samo vaše sustave
- Čuvajte rezultate privatno
- Dijelite samo generičke nalaze
- Koristite za poboljšanja

❌ **Ne činite:**
- Testiranje tuđih sustava
- Javno objavljivanje eksploita
- Zloupotreba znanja
- Ignoriranje rezultata

---

## 🎓 Učni resursi

- [Dokumentacija](README.md)
- [Korisnička Dokumentacija](USER_DOCUMENTATION.md)
- [Tehnička Dokumentacija](TECHNICAL_DOCUMENTATION.md)
- [Instalacijski Vodič](INSTALLATION_GUIDE.md)
- [Arhitektura](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)

---

## 🔗 Korisni linkovi

- **Backend**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: http://localhost:5173
- **GitHub**: https://github.com/karloks2005/JailbreakLab
- **HuggingFace**: https://huggingface.co
- **OpenAI API**: https://platform.openai.com

---

## 📞 Podrška

**Greške?** → GitHub Issues  
**Pitanja?** → GitHub Discussions  
**Povratne informacije?** → Pull Requests  

---

## 🚀 Sljedeći koraci

1. ✅ Instalirajte projekt
2. 📖 Čitajte dokumentaciju
3. 🧪 Pokrenite prve testove
4. 📊 Analizirajte rezultate
5. 🔄 Eksperimentirajte dalje
6. 📚 Savjetuj znanje

---

**Verzija:** 1.0  
**Datum:** 2026-01-22  
**Status:** Gotovo ✅
