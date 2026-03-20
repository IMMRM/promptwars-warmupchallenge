# 🚨 LifeLine AI

**Turn messy, real-world inputs into structured, verified, life-saving actions — instantly.**

LifeLine AI is a smart emergency & health action assistant that accepts unstructured inputs (text descriptions, photos, audio recordings, medical records) and uses Google's AI to produce prioritized, actionable response plans with nearby service mapping.

![Python](https://img.shields.io/badge/Python-3.14+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.0_Flash-orange)
![Maps](https://img.shields.io/badge/Google-Maps_Platform-green)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Text Analysis** | Paste unstructured medical records, symptom descriptions, emergency reports, weather alerts |
| 📸 **Image Analysis** | Upload photos of accidents, injuries, prescriptions, weather conditions |
| 🎙️ **Audio Analysis** | Upload voice memos or recordings for AI transcription and analysis |
| 🎯 **Structured Actions** | Severity-coded action cards (CRITICAL → LOW) with step-by-step instructions |
| 🗺️ **Nearby Services** | Google Maps integration showing nearest hospitals, pharmacies, fire stations, police |
| 🛡️ **Verification** | AI provides reasoning and verification notes for every recommendation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                   │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐  │
│  │ Text Tab │  │ Image Tab │  │   Audio Tab      │  │
│  └────┬─────┘  └─────┬─────┘  └────────┬─────────┘  │
│       └───────────────┼─────────────────┘            │
│                       ▼                               │
│              Action Engine                            │
│       ┌───────────────┼───────────────┐              │
│       ▼               ▼               ▼              │
│  Gemini Service  Maps Service    Folium Map          │
│       │               │                              │
└───────┼───────────────┼──────────────────────────────┘
        ▼               ▼
  Google Gemini    Google Maps
  2.0 Flash        Platform
```

### How It Works
1. User submits unstructured input (typed text, photo, audio recording)
2. Backend sends it to **Gemini 2.0 Flash** (multimodal) for intelligent parsing
3. Gemini extracts structured data: entities, severity, category, key facts
4. **Action Engine** normalizes and sorts actions by urgency
5. **Google Maps** finds nearby relevant services (hospitals, shelters, pharmacies)
6. Frontend renders beautiful, severity-coded action cards + interactive map

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- [Gemini API Key](https://aistudio.google.com/apikey)
- [Google Maps API Key](https://console.cloud.google.com/apis) (with Places & Directions APIs enabled)

### Setup

```bash
# 1. Clone and enter the project
cd Google_PromptWars

# 2. Create virtual environment (if not already done)
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
# Edit .env and add your API keys

# 6. Run the app
streamlit run main.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for AI analysis |
| `GOOGLE_MAPS_API_KEY` | ✅ Yes | Google Maps API key for nearby services |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --tb=short
```

---

## 📁 Project Structure

```
Google_PromptWars/
├── main.py                    # Streamlit app (entry point)
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment & app configuration
│   ├── models.py              # Data models (ActionCard, AnalysisResult, NearbyPlace)
│   ├── gemini_service.py      # Google Gemini multimodal AI service
│   ├── maps_service.py        # Google Maps Places & Directions service
│   └── action_engine.py       # Orchestrates analysis → actions pipeline
├── tests/
│   ├── __init__.py
│   ├── test_action_engine.py  # Unit tests for action engine
│   └── test_gemini_service.py # Tests for Gemini response parsing
├── .env.example               # API key template
├── pyproject.toml             # Project metadata & dependencies
└── README.md                  # This file
```

---

## 🔒 Security

- API keys are stored in `.env` (git-ignored) and never hardcoded
- All external API calls use HTTPS with timeouts
- User inputs are sent only to Google's APIs — no third-party data sharing
- No user data is stored or logged beyond the current session

---

## ♿ Accessibility

- Semantic HTML structure with proper heading hierarchy
- High-contrast dark mode with readable color choices
- Severity indicators use both color AND icons/text (not color alone)
- All interactive elements are keyboard-navigable (Streamlit default)
- Screen reader compatible labels and descriptions

---

## 🛠️ Google Services Integration

### Gemini 2.0 Flash (Multimodal AI)
- **Text analysis**: Parses unstructured descriptions, medical records, alerts
- **Image analysis**: Analyzes photos for emergencies, injuries, prescriptions
- **Audio analysis**: Processes voice recordings for transcription and situation assessment
- **Structured output**: Returns JSON with severity, actions, verification notes

### Google Maps Platform
- **Places API**: Finds nearest hospitals, pharmacies, fire stations, police stations
- **Directions API**: Provides routing information to nearby services
- **Folium visualization**: Interactive dark-mode map with categorized markers
