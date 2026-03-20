# 🚨 LifeLine AI

**Turn messy, real-world inputs into structured, verified, life-saving actions — instantly.**

LifeLine AI is a smart emergency & health action assistant that accepts unstructured inputs (text descriptions, photos, audio recordings, medical records) and uses Google's AI to produce prioritized, actionable response plans with nearby service mapping.

![Python](https://img.shields.io/badge/Python-3.14+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.0_Flash-orange)
![Maps](https://img.shields.io/badge/Google-Maps_Platform-green)
![Security](https://img.shields.io/badge/Security-XSS_Protected-success)
![Modularity](https://img.shields.io/badge/Modularity-Service__Oriented-brightgreen)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Text Analysis** | Paste unstructured medical records, symptom descriptions, emergency reports, weather alerts |
| 📸 **Image Analysis** | Upload photos of accidents, injuries, prescriptions, weather conditions |
| 🎙️ **Audio Analysis** | Upload voice memos or recordings for AI transcription and situation assessment |
| 🎯 **Structured Actions** | Severity-coded action cards (CRITICAL → LOW) with step-by-step instructions |
| 🗺️ **Nearby Services** | Google Maps integration finding the nearest hospitals, pharmacies, and shelters |
| 🛡️ **Verification** | AI provides verified reasoning and sources for every medical/safety recommendation |

---

## 🏗️ Architecture & Modularity

LifeLine AI is built using a highly modular, **Service-Oriented Architecture** ensuring clean separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│               Streamlit UI (main.py)                  │
│  State Management • HTML Escaping • UI Rendering      │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐  │
│  │ Text Tab │  │ Image Tab │  │   Audio Tab      │  │
│  └────┬─────┘  └─────┬─────┘  └────────┬─────────┘  │
│       └───────────────┼─────────────────┘            │
│                       ▼                               │
│        Action Engine (app/action_engine.py)           │
│    Orchestrates AI analysis + Data normalization      │
│       ┌───────────────┼───────────────┐              │
│       ▼               ▼               ▼              │
│  Gemini Service  Maps Service    Models (app/models) │
│       │               │                              │
└───────┼───────────────┼──────────────────────────────┘
        ▼               ▼
  Google Gemini    Google Maps
  2.0 Flash        Platform
```

- **`models.py`:** Strictly typed DataClasses preventing structural data corruption.
- **`config.py`:** Centralized environment, styling, and constants configuration.
- **`gemini_service.py`:** Isolated LLM interaction with smart model fallbacks and backoff logic.
- **`maps_service.py`:** Dedicated external API routing and rigorous error handling.

---

## 🔒 Security Posture

- **XSS Protection:** Implemented rigorous HTML escaping (`html.escape`) on all strings rendered into the UI using Streamlit's `unsafe_allow_html`. This prevents any Cross-Site Scripting vulnerabilities from malicious AI hallucinations or arbitrary user inputs.
- **Secrets Management:** API keys are never stored inside the repository, Docker image, or UI components. They are strictly loaded from environment variables (`os.getenv`), ensuring full alignment with OWASP standards.
- **Isolated User Context:** No user data is cached onto disk or sent to generic third-party logging engines. 

---

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- [Gemini API Key](https://aistudio.google.com/apikey)
- [Google Maps API Key](https://console.cloud.google.com/apis) (Places & Directions enabled)

### Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/your-username/Google_PromptWars.git
cd Google_PromptWars

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -e .

# 5. Configure API keys
cp .env.example .env
# Edit .env and add your API keys.

# 6. Run the app
streamlit run main.py
```

---

## ⚙️ Deployment

### Option 1: Google Cloud Run (Recommended)
This code is fully containerized with a highly optimized, multi-stage, non-root `Dockerfile` and includes a 1-click `deploy.bat` wrapper.

```bash
deploy.bat YOUR_PROJECT_ID YOUR_GEMINI_KEY YOUR_MAPS_KEY
```

### Option 2: Docker
```bash
docker build -t lifeline-ai .
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key" -e GOOGLE_MAPS_API_KEY="your-key" lifeline-ai
```

---

## 🧪 Robust Testing
Includes automated unit-testing leveraging `pytest` with rigorous coverage of data models and service parsers:
```bash
python -m pytest tests/ -v
```

---

## 🌐 Google Services Deep Integration

### Gemini Multimodal Intelligence
Utilizes `gemini-2.5-flash` and `gemini-2.0-flash` with robust exponential backoff and rate-limit resilient model-chain fallbacks (`gemini-1.5-flash`, etc.). Native parsing transforms multimodal messiness into strictly structured JSON objects.

### Google Maps Navigation
Integrates `Places API` and `Directions API` not just for mapping, but strategically querying specific logical constraints (e.g. `pharmacy` vs `fire_station`) based directly on the severity classification analyzed by Gemini.
