# JailbreakLab - Kompletan indeks dokumentacije

## 📚 Sve dokumentacijske datoteke

### Za korisnike 👥

#### 1. **[Korisnička dokumentacija](USER_DOCUMENTATION.md)** - Početna točka za korisnike
- Što je JailbreakLab?
- Kako početi (instalacija s Dockerom)
- Objašnjenja napada (22 vrste)
- Objašnjenja obrana (11 vrsta)
- Razumijevanje statistike
- Česte greške i rješenja

**Preporučeno čitanje za:** Svi novi korisnici

---

#### 2. **[Instalacijski vodič](INSTALLATION_GUIDE.md)** - Detaljne instalacijske upute
- Brza instalacija (30 sekundi)
- Preduvjeti i sistemski zahtjevi
- Instalacija s Dockerom (preporučeno)
- Lokalna instalacija (bez Dockera)
- Konfiguracija varijabli okruženja
- Provjera instalacije
- Troubleshooting

**Preporučeno čitanje za:** Oni koji trebaju instalirati projekt

---

#### 3. **[Brza referenca](QUICK_REFERENCE.md)** - Cheat sheet
- 30-sekundni brzi početak
- Česta pitanja (FAQ)
- Česte naredbe
- API primjeri sa curl-om
- Rješavanje čestih problema
- Tipični radni tok
- Sigurnosni savjeti

**Preporučeno čitanje za:** Oni koji trebaju brz odgovor na pitanje

---

### Za razvijače 👨‍💻

#### 4. **[Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md)** - Backend/API specifikacija
- Arhitektura aplikacije
- Detaljne komponente (Frontend, Backend, Database)
- Postavljanje razvoja (za lokalno testiranje)
- REST API reference
- Struktura baze podataka
- Sustav napada (kako implementirati)
- Sustav obrana (kako implementirati)
- Implementacijske vodilice
- Troubleshooting za razvijače

**Preporučeno čitanje za:** Developers, sysadmins, testers

---

#### 5. **[Arhitektura i dizajn](ARCHITECTURE.md)** - Detaljni prikaz arhitekture
- Pregled arhitekture
- Komponente (Frontend layer, Backend layer, itd.)
- Tok podataka kroz sustav
- Model loader - kako se modeli učitavaju
- Attack pipeline - kako se napadi izvršavaju
- Defense pipeline - kako se obrane primjenjuju
- Baza podataka - shema i struktura
- Sigurnosne mjere
- Skalabilnost i load balancing

**Preporučeno čitanje za:** Architects, senior developers, DevOps

---

#### 6. **[API Reference](API_REFERENCE.md)** - Kompletan API vodič
- Overview svih API endpoints
- Authentication (trenutna i budućnost)
- Detaljne specifikacije svih endpoints:
  - `/api/execute` (streaming)
  - `/api/attacks`
  - `/api/defenses`
  - `/api/models`
  - `/api/statistics`
  - `/api/history`
- JavaScript i Python primjeri
- Kompletan workflow primjer
- Error handling
- Rate limiting

**Preporučeno čitanje za:** API consumers, frontend developers, testers

---

#### 7. **[Vodič za razvoj](DEVELOPMENT_GUIDE.md)** - Kako doprinijeti projektu
- Lokalni setup za razvoj
- Dodavanje novog napada (korak po korak)
- Dodavanje nove obrane (korak po korak)
- Dodavanje novih modela
- Unit testovi (Python i TypeScript)
- API testovi
- Best practices
- Debugging technike
- Contributor checklist
- Build i deployment

**Preporučeno čitanje za:** Contributors, developers koji trebaju dodati nove značajke

---

### Reference 📖

#### 8. **[README.md](README.md)** - Projekt overview
- Što je JailbreakLab?
- Značajke
- Brzi početak
- Attack i defense tipovi
- Tehnologije korištene
- Licencija

**Preporučeno čitanje za:** Svi (početna točka)

---

## 🗺️ Preporučeni put čitanja po ulozi

### 👤 Ja sam obični korisnik
1. [README.md](README.md) - Razumijevanje što je to
2. [Instalacijski vodič](INSTALLATION_GUIDE.md) - Instalacija
3. [Korisnička dokumentacija](USER_DOCUMENTATION.md) - Korištenje
4. [Brza referenca](QUICK_REFERENCE.md) - Savjeti i trikovi

---

### 👨‍💻 Ja sam junior developer
1. [README.md](README.md)
2. [Instalacijski vodič](INSTALLATION_GUIDE.md)
3. [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md)
4. [Vodič za razvoj](DEVELOPMENT_GUIDE.md)
5. [API Reference](API_REFERENCE.md)

---

### 🔧 Ja sam senior developer / DevOps
1. [Arhitektura i dizajn](ARCHITECTURE.md)
2. [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md)
3. [Vodič za razvoj](DEVELOPMENT_GUIDE.md)
4. [API Reference](API_REFERENCE.md)

---

### 🏗️ Ja trebam deployati projekt
1. [Instalacijski vodič](INSTALLATION_GUIDE.md) - Docker setup
2. [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md) - Environment vars
3. [Arhitektura i dizajn](ARCHITECTURE.md) - Skalabilnost

---

### 🧪 Ja testiram API
1. [API Reference](API_REFERENCE.md) - Endpoints
2. [Brza referenca](QUICK_REFERENCE.md) - curl primjeri
3. [Tehnička dokumentacija](TECHNICAL_DOCUMENTATION.md) - Error codes

---

## 📊 Veličina dokumentacije

| Dokument | Veličina | Čitanje | Fokus |
|----------|----------|---------|-------|
| README.md | ~10 min | 2-3 stranice | Pregled |
| Korisnička doc | ~20 min | 8-10 stranica | Korištenje |
| Instalacijski vodič | ~15 min | 6-8 stranica | Instalacija |
| Tehnička doc | ~30 min | 12-15 stranica | Backend |
| Arhitektura | ~25 min | 10-12 stranica | Design |
| API Reference | ~20 min | 15-18 stranica | API |
| Vodič za razvoj | ~20 min | 12-15 stranica | Development |
| Brza referenca | ~5 min | 2-3 stranice | Lookup |

**Ukupno**: ~145 min čitanja (≈ 2.5 sata)

---

## 🎯 Brzi linkovi po temi

### Instalacija
- [Docker instalacija](INSTALLATION_GUIDE.md#instalacija-s-dockerom)
- [Lokalna instalacija](INSTALLATION_GUIDE.md#lokalna-instalacija)
- [Troubleshooting instalacije](INSTALLATION_GUIDE.md#problemi-i-rješenja)

### Korištenje
- [Brzi početak](QUICK_REFERENCE.md#-brzi-početak)
- [Kako koristiti napad](USER_DOCUMENTATION.md#brzi-početak)
- [Kako koristiti obranu](USER_DOCUMENTATION.md#objašnjenja-obrana)

### API
- [Execute endpoint](API_REFERENCE.md#1-execute-attack)
- [Svi endpoints](API_REFERENCE.md#endpoints)
- [Python primjer](API_REFERENCE.md#complete-workflow---python)
- [JavaScript primjer](API_REFERENCE.md#complete-workflow---javascript)

### Razvoj
- [Dodaj novi napad](DEVELOPMENT_GUIDE.md#dodavanje-novog-napada)
- [Dodaj novu obranu](DEVELOPMENT_GUIDE.md#dodavanje-nove-obrane)
- [Setup za razvoj](DEVELOPMENT_GUIDE.md#setup)
- [Testiranje](DEVELOPMENT_GUIDE.md#testiranje)

### Arhitektura
- [Backend struktura](ARCHITECTURE.md#komponente)
- [Frontend struktura](TECHNICAL_DOCUMENTATION.md#4-frontend-komponente)
- [Attack pipeline](ARCHITECTURE.md#attack-pipeline)
- [Defense pipeline](ARCHITECTURE.md#defense-pipeline)

---

## 🔍 Pretraživanje po ključnim rečima

### Instalacija
- Docker → [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#instalacija-s-dockerom)
- Python setup → [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#lokalna-instalacija)
- npm install → [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#opcija-2-frontend-react)

### Napadi
- DAN11 → [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md#objašnjenja-napada)
- Role-playing → [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md#1️⃣-role-playing-napadi)
- Dodaj novi → [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md#dodavanje-novog-napada)

### Obrane
- LlamaGuard → [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md#2️⃣-ml-based-obrane)
- Input Sanitization → [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md#1️⃣-pre-processing-obrane)
- Dodaj novu → [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md#dodavanje-nove-obrane)

### API
- Execute → [API_REFERENCE.md](API_REFERENCE.md#1-execute-attack)
- Statistics → [API_REFERENCE.md](API_REFERENCE.md#5-get-statistics)
- Error handling → [API_REFERENCE.md](API_REFERENCE.md#error-handling)

### Problemi
- GPU error → [QUICK_REFERENCE.md](QUICK_REFERENCE.md#problem-gpu-nije-dostupan)
- Port zauzet → [QUICK_REFERENCE.md](QUICK_REFERENCE.md#problem-port-zauzet)
- Model nije dostupan → [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#-problem-models-failed-to-download)

---

## 📋 Checklist za početnike

- [ ] Pročitaj [README.md](README.md)
- [ ] Instaliraj projekt koristeći [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- [ ] Pročitaj [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [ ] Testiraj prvi napad
- [ ] Pročitaj [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md)
- [ ] Analiziraj statistiku
- [ ] Eksperimentiraj sa različitim napadima/obranama

---

## 📋 Checklist za developere

- [ ] Pročitaj [README.md](README.md)
- [ ] Instaliraj projekt
- [ ] Pročitaj [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
- [ ] Pročitaj [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Pročitaj [API_REFERENCE.md](API_REFERENCE.md)
- [ ] Pročitaj [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- [ ] Testiraj API endpoint
- [ ] Dodaj novu značajku (napad/obranu/model)
- [ ] Napiši testove
- [ ] Prosledi Pull Request

---

## 🆘 Gdje tražiti pomoć

### Za instalaciju
→ [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#problemi-i-rješenja)

### Za korištenje
→ [USER_DOCUMENTATION.md](USER_DOCUMENTATION.md#česte-greške)

### Za brz odgovor
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Za API
→ [API_REFERENCE.md](API_REFERENCE.md)

### Za razvoj
→ [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

### Za arhitekturu
→ [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🎓 Učni ciljevi po datoteci

### Nakon čitanja README.md:
✓ Razumijem što je JailbreakLab  
✓ Znam koje su glavne značajke

### Nakon čitanja USER_DOCUMENTATION.md:
✓ Mogu koristiti aplikaciju  
✓ Razumijem različite napade i obrane  
✓ Mogu analizirati statistiku

### Nakon čitanja INSTALLATION_GUIDE.md:
✓ Mogu instalirati projekt  
✓ Mogu konfigurirati okruženje  
✓ Mogu troubleshoot probleme

### Nakon čitanja TECHNICAL_DOCUMENTATION.md:
✓ Razumijem backend arhitekturu  
✓ Znam kako API funkcionira  
✓ Mogu dodati nove napade/obrane

### Nakon čitanja ARCHITECTURE.md:
✓ Razumijem kompletnu arhitekturu  
✓ Znam kako se model podaci komuniciraju  
✓ Mogu izplanirati skalabilnost

### Nakon čitanja API_REFERENCE.md:
✓ Mogu integrirati API u svoje aplikacije  
✓ Razumijem sve endpoint-e  
✓ Mogu pisati klijent aplikacije

### Nakon čitanja DEVELOPMENT_GUIDE.md:
✓ Mogu doprinijeti projektu  
✓ Mogu dodati nove značajke  
✓ Mogu pisati testove

---

## 📝 Verzije dokumentacije

**Trenutna verzija:** 1.0  
**Datum zadnje ažuriranja:** 2026-01-22  
**Status:** ✅ Kompletan

### Što je novo u v1.0:
- ✅ Kompletan user guide
- ✅ Instalacijski vodič
- ✅ Tehnička dokumentacija
- ✅ API reference
- ✅ Architecture documentation
- ✅ Development guide
- ✅ Quick reference

---

## 🔗 Dodatni resursi

### External linkovi
- [HuggingFace Dokumentacija](https://huggingface.co/docs)
- [FastAPI Dokumentacija](https://fastapi.tiangolo.com/)
- [React Dokumentacija](https://react.dev/)
- [Docker Dokumentacija](https://docs.docker.com/)
- [Kubernetes Dokumentacija](https://kubernetes.io/docs/)

### Video tutoriali (planirati)
- [ ] Instalacija i setup
- [ ] Prvi napad
- [ ] Analiza statistike
- [ ] Dodavanje novog napada
- [ ] API integracija

---

## 📞 Kontakt i podrška

**GitHub Issues**: Greške i problemi  
**GitHub Discussions**: Pitanja i povratne informacije  
**GitHub Pull Requests**: Doprinos koda  

---

## ✅ Dokumentacijska checklist

- [x] README.md - Projekt overview
- [x] USER_DOCUMENTATION.md - Korisnički vodič
- [x] INSTALLATION_GUIDE.md - Instalacijski vodič
- [x] TECHNICAL_DOCUMENTATION.md - Tehnička dokumentacija
- [x] ARCHITECTURE.md - Arhitektura
- [x] API_REFERENCE.md - API dokumentacija
- [x] DEVELOPMENT_GUIDE.md - Vodič za razvoj
- [x] QUICK_REFERENCE.md - Brza referenca
- [x] DOCUMENTATION_INDEX.md - Ovaj indeks

---

**Dokumentacija za JailbreakLab je sada gotova! 🎉**

Sva dokumentacija je dostupna na hrvatskom jeziku i detaljno pokriva sve aspekte projekta, od instalacije do naprednog razvoja.

Hvala što čitate! 📖
