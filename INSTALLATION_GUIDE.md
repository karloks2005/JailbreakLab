# JailbreakLab - Vodič instalacije

## Sadržaj
1. [Brza instalacija](#brza-instalacija)
2. [Preduvjeti](#preduvjeti)
3. [Instalacija s Dockerom](#instalacija-s-dockerom)
4. [Lokalna instalacija](#lokalna-instalacija)
5. [Konfiguracija](#konfiguracija)
6. [Provjera instalacije](#provjera-instalacije)
7. [Problemi i rješenja](#problemi-i-rješenja)

---

## Brza instalacija

### Za Linux/macOS korisnika (najbrže)

```bash
# 1. Klonirajte projekt
git clone https://github.com/karloks2005/JailbreakLab.git
cd JailbreakLab

# 2. Pokrenite Docker Compose
docker-compose up --build

# 3. Otvorite u pretraživaču
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
```

### Za Windows korisnika

```powershell
# 1. Klonirajte projekt
git clone https://github.com/karloks2005/JailbreakLab.git
cd JailbreakLab

# 2. Pokrenite Docker Compose
docker-compose up --build

# 3. Otvorite u pretraživaču
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
```

---

## Preduvjeti

### Obavezno

- **64-bitni OS**
  - Windows 10/11 Pro, Enterprise, ili Education (za Hyper-V)
  - Ubuntu 18.04+ (ili drugi Linux)
  - macOS 11+ (Intel ili Apple Silicon)

- **Docker Desktop**
  - [Preuzmite Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Verzija 4.0+
  - 4+ GB RAM dostupno Dockeru

- **Internet konekcija** (za preuzimanje modela)

### Opciono (za lokalnu instalaciju bez Dockera)

- **Python 3.10 ili novije**
  - `python --version` za provjeru
  - [python.org](https://www.python.org/)

- **Node.js 20 ili novije**
  - `node --version` za provjeru
  - [nodejs.org](https://nodejs.org/)

- **Git** (za kloniranje projekta)
  - [git-scm.com](https://git-scm.com/)

### Preporučeno za brže performanse

- **NVIDIA GPU**
  - CUDA 12.0+
  - NVIDIA Driver 530+
  - Najmanje 8GB VRAM

- **16GB+ RAM**
  - 8GB minimum, 16GB preporučeno

---

## Instalacija s Dockerom

### Korak 1: Instalacija Dockera

#### Windows

1. Preuzmite [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Izvršite instalator
3. Ponovo pokrenite računalo
4. Otvorite PowerShell ili CMD i provjerite:
```powershell
docker --version
docker run hello-world
```

#### macOS

1. Preuzmite [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Otvorite DMG datoteku
3. Povucite Docker u Applications mapu
4. Pokrenite Docker.app
5. Otvorite terminal i provjerite:
```bash
docker --version
docker run hello-world
```

#### Linux (Ubuntu/Debian)

```bash
# Instalacija
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Pokretanje bez sudo
sudo usermod -aG docker $USER
newgrp docker

# Provjera
docker --version
docker run hello-world
```

---

### Korak 2: Kloniranje projekta

```bash
# Klonirajte projekt
git clone https://github.com/karloks2005/JailbreakLab.git
cd JailbreakLab

# Ili ako koristite SSH
git clone git@github.com:karloks2005/JailbreakLab.git
cd JailbreakLab

# Provjera da li su svi datoteke prisutne
ls -la
# Trebalo bi da vidite: docker-compose.yml, backend/, frontend/, k8s/
```

---

### Korak 3: Pokretanje s Dockerom

```bash
# Build i pokretanje svih servisa
docker-compose up --build

# Ili u background modu
docker-compose up --build -d

# Provjera statusa
docker-compose ps

# Prikaz logova (ako je pokrenuto u background)
docker-compose logs -f

# Zaustavljanje
docker-compose down
```

---

### Korak 4: Provjera da li je sve pokrenuto

1. **Frontend:**
   - Otvorite http://localhost:5173
   - Trebalo bi vidjeti interaktivni interfejs

2. **Backend API:**
   - Otvorite http://localhost:8000/docs
   - Trebalo bi vidjeti Swagger dokumentaciju

3. **Redis (interno):**
   ```bash
   docker exec jailbreaklab-redis redis-cli ping
   # Trebalo bi vratiti: PONG
   ```

---

## Lokalna instalacija

### Opcija 1: Backend (Python)

#### Windows

```powershell
# 1. Navigacija
cd backend

# 2. Stvaranje virtualnog okruženja
python -m venv venv
.\venv\Scripts\activate

# 3. Instalacija zavisnosti
pip install --upgrade pip
pip install -r requirements.txt

# 4. Pokretanje
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 5. Provjera
# http://localhost:8000/docs
```

#### Linux/macOS

```bash
# 1. Navigacija
cd backend

# 2. Stvaranje virtualnog okruženja
python3 -m venv venv
source venv/bin/activate

# 3. Instalacija zavisnosti
pip install --upgrade pip
pip install -r requirements.txt

# 4. Pokretanje
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 5. Provjera
# http://localhost:8000/docs
```

---

### Opcija 2: Frontend (React)

#### Za sve sisteme

```bash
# 1. Navigacija
cd frontend

# 2. Instalacija zavisnosti
npm install

# 3. Razvoj (sa hot reloadom)
npm run dev

# 4. Provjera
# http://localhost:5173

# 5. Build za produkciju (opciono)
npm run build

# 6. Preview build-a (opciono)
npm run preview
```

---

### Opcija 3: Redis (Session cache)

#### S Dockerom (preporučeno)

```bash
docker run -d -p 6379:6379 --name jailbreaklab-redis redis:latest

# Provjera
docker exec jailbreaklab-redis redis-cli ping
```

#### Lokalno (Linux)

```bash
# Instalacija
sudo apt-get install redis-server

# Pokretanje
redis-server

# Provjera u drugoj terminali
redis-cli ping
```

#### Lokalno (macOS s Homebrew)

```bash
# Instalacija
brew install redis

# Pokretanje
redis-server

# Provjera u drugoj terminali
redis-cli ping
```

#### Lokalno (Windows)

1. Preuzmite [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
2. Izvršite instalator
3. Pokrenite Redis Server iz Start menija
4. Provjera (cmd):
```cmd
redis-cli ping
```

---

## Konfiguracija

### Varijable okruženja

#### Backend - Kreirajte `.env` datoteku u `backend/` direktoriju

```env
# Model konfiguracija
DEVICE=cuda  # ili cpu
MODEL_CACHE_DIR=/path/to/models
QUANTIZE=false

# HuggingFace
HF_TOKEN=hf_your_token_here

# OpenAI (opciono)
OPENAI_API_KEY=sk_your_key_here

# Redis
REDIS_URL=redis://localhost:6379

# Baza podataka
DATABASE_URL=sqlite:///./jailbreaklab.db

# Logging
LOG_LEVEL=INFO
```

#### Frontend - Kreirajte `.env.local` datoteku u `frontend/` direktoriju

```env
# API URL
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_MAX_RETRIES=3
```

#### Docker Compose - Kreirajte `.env` datoteku u rootu projekta

```env
# Backend
BACKEND_PORT=8000
BACKEND_WORKERS=4
DEVICE=cuda

# Frontend
FRONTEND_PORT=5173

# Redis
REDIS_PORT=6379

# GPU (ako imate NVIDIA GPU)
ENABLE_GPU=true
CUDA_VISIBLE_DEVICES=0
```

---

### HuggingFace Token (opciono ali preporučeno)

```bash
# 1. Kreirajte account na https://huggingface.co/
# 2. Generirajte token: https://huggingface.co/settings/tokens
# 3. Postavite u .env datoteku
HF_TOKEN=hf_your_token_here

# 4. Ili login preko CLI
huggingface-cli login
```

---

## Provjera instalacije

### Korak 1: Provjera Dockera

```bash
docker --version
docker run hello-world
docker-compose --version
```

### Korak 2: Provjera servisa

```bash
# Vidi sve pokrenute kontejnere
docker-compose ps

# Trebalo bi vidjeti:
# NAME                COMMAND             STATUS
# jailbreaklab-backend   "python main.py"   Up
# jailbreaklab-frontend  "npm run dev"      Up
# jailbreaklab-redis     "redis-server"     Up
```

### Korak 3: Provjera konekcije

```bash
# Backend API
curl http://localhost:8000/docs

# Frontend
curl http://localhost:5173

# Redis
docker exec jailbreaklab-redis redis-cli ping
```

### Korak 4: Provjera logova

```bash
# Svi logovi
docker-compose logs

# Samo backend
docker-compose logs backend

# Samo frontend
docker-compose logs frontend

# Real-time praćenje
docker-compose logs -f
```

---

## Problemi i rješenja

### ❌ Problem: "Docker nije instaliran"

**Rješenje:**
1. Preuzmite [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Trebalo bi imati instaliran Hyper-V (Windows) ili KVM (Linux)
3. Ponovo pokrenite računalo nakon instalacije

---

### ❌ Problem: "docker-compose: command not found"

**Rješenje:**
```bash
# Provjera verzije
docker compose version  # Novija verzija

# Ili instalacija
pip install docker-compose
```

---

### ❌ Problem: "Port 5173 je već zauzet"

**Rješenje:**
```bash
# Ako je port zauzet, koristite drugi port
docker-compose up -d -e FRONTEND_PORT=5174

# Ili ubijte proces
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5173
kill -9 <PID>
```

---

### ❌ Problem: "CUDA out of memory"

**Rješenje:**
```env
# U .env datoteci
DEVICE=cpu          # Koristi CPU umjesto GPU-a
QUANTIZE=true       # Kvantiziraj model
```

---

### ❌ Problem: "Models failed to download"

**Rješenje:**
```bash
# Provjerite internet konekciju
ping huggingface.co

# Ili postavite HuggingFace token
HF_TOKEN=hf_your_token

# Pokušajte ponovo preuzeti model
docker-compose restart backend
```

---

### ❌ Problem: "Redis connection refused"

**Rješenje:**
```bash
# Provjera da li Redis radi
docker-compose ps

# Ako ne radi, pokrenite
docker-compose restart redis

# Provjera konekcije
docker exec jailbreaklab-redis redis-cli ping
```

---

### ❌ Problem: "Frontend se ne učitava"

**Rješenje:**
```bash
# Provjera da li frontend radi
docker-compose logs frontend

# Provjera porta
# http://localhost:5173

# Ako ne radi, pokrenite ponovo
docker-compose restart frontend
```

---

### ❌ Problem: "Backend API nije dostupan"

**Rješenje:**
```bash
# Provjera da li backend radi
docker-compose ps

# Provjera logova
docker-compose logs backend

# Pokrenite ponovo
docker-compose restart backend

# Provjera dokumentacije
curl http://localhost:8000/docs
```

---

## Sljedeći koraci

1. **Učitajte dokumentaciju:**
   - [Korisnička dokumentacija](USER_DOCUMENTATION.md)
   - [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md)

2. **Započnite sa testiranjem:**
   - Odaberite model
   - Odaberite napad
   - Dodajte obranu
   - Izvršite test

3. **Istražite statistiku:**
   - Pogledajte grafikone
   - Analizirajte rezultate
   - Napravite zaključke

---

## Dodatni resursi

- **Docker dokumentacija:** https://docs.docker.com/
- **React dokumentacija:** https://react.dev/
- **FastAPI dokumentacija:** https://fastapi.tiangolo.com/
- **HuggingFace dokumentacija:** https://huggingface.co/docs

---

**Verzija:** 1.0  
**Zadnja ažuriranja:** 2026-01-22  
**Licencija:** MIT
