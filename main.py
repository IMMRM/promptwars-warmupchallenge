"""
LifeLine AI — Streamlit Application
Turn messy, real-world inputs into structured, verified, life-saving actions.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium

from app import action_engine
from app.config import (
    APP_TITLE,
    APP_ICON,
    APP_DESCRIPTION,
    SEVERITY_COLORS,
    SEVERITY_ICONS,
)

# ── Page Configuration ─────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for premium dark styling ────────────────────────────────
st.markdown(
    """
<style>
/* ── Import Google Font ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ──────────────────────────────────────────────── */
:root {
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1a2e;
    --bg-card: rgba(30, 30, 55, 0.7);
    --text-primary: #e8e8f0;
    --text-secondary: #a0a0b8;
    --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --critical: #FF4B4B;
    --high: #FF8C00;
    --medium: #FFD700;
    --low: #00C851;
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --shadow-glow: 0 0 30px rgba(102, 126, 234, 0.15);
}

/* ── Global Overrides ────────────────────────────────────────────── */
.stApp {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e8e8f0 !important;
}

/* ── Hero Header ─────────────────────────────────────────────────── */
.hero-header {
    background: linear-gradient(135deg, #1a1a3e 0%, #2d1b69 50%, #1a1a3e 100%);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-glow);
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 50%);
    animation: pulse-bg 4s ease-in-out infinite;
}

@keyframes pulse-bg {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

.hero-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #a78bfa, #f093fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    position: relative;
    z-index: 1;
}

.hero-header p {
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
}

/* ── Severity Cards ──────────────────────────────────────────────── */
.action-card {
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--medium);
    border-top: 1px solid var(--glass-border);
    border-right: 1px solid var(--glass-border);
    border-bottom: 1px solid var(--glass-border);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

.action-card.critical { border-left-color: var(--critical); }
.action-card.high { border-left-color: var(--high); }
.action-card.medium { border-left-color: var(--medium); }
.action-card.low { border-left-color: var(--low); }

.action-card .card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.action-card .card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.action-card .card-desc {
    color: var(--text-secondary);
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 0.75rem;
}

.action-card .card-steps {
    list-style: none;
    padding: 0;
    margin: 0;
}

.action-card .card-steps li {
    color: var(--text-primary);
    font-size: 0.9rem;
    padding: 0.35rem 0 0.35rem 1.5rem;
    position: relative;
}

.action-card .card-steps li::before {
    content: '→';
    position: absolute;
    left: 0;
    color: #667eea;
    font-weight: 700;
}

/* ── Severity Badge ──────────────────────────────────────────────── */
.severity-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.severity-badge.critical {
    background: rgba(255,75,75,0.2);
    color: var(--critical);
    border: 1px solid rgba(255,75,75,0.3);
}
.severity-badge.high {
    background: rgba(255,140,0,0.2);
    color: var(--high);
    border: 1px solid rgba(255,140,0,0.3);
}
.severity-badge.medium {
    background: rgba(255,215,0,0.2);
    color: var(--medium);
    border: 1px solid rgba(255,215,0,0.3);
}
.severity-badge.low {
    background: rgba(0,200,81,0.2);
    color: var(--low);
    border: 1px solid rgba(0,200,81,0.3);
}

/* ── Key Facts ───────────────────────────────────────────────────── */
.key-facts {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

.key-facts h4 {
    color: #a78bfa;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.5rem 0;
}

.key-facts ul {
    margin: 0;
    padding-left: 1.25rem;
}

.key-facts li {
    color: var(--text-primary);
    font-size: 0.9rem;
    padding: 0.2rem 0;
}

/* ── Verification Box ────────────────────────────────────────────── */
.verification-box {
    background: rgba(102, 126, 234, 0.08);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
}

.verification-box h4 {
    color: #667eea;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.4rem 0;
}

.verification-box p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.6;
}

/* ── Summary Box ─────────────────────────────────────────────────── */
.summary-box {
    background: linear-gradient(135deg, rgba(102,126,234,0.12) 0%, rgba(167,139,250,0.08) 100%);
    border: 1px solid rgba(102,126,234,0.25);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}

.summary-box h3 {
    color: var(--text-primary);
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
}

.summary-box p {
    color: var(--text-secondary);
    font-size: 1rem;
    margin: 0;
    line-height: 1.6;
}

/* ── Input Mode Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 600 !important;
}

/* ── Animations ──────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: fadeInUp 0.5s ease-out forwards;
}

/* ── Time Sensitive Pulse ────────────────────────────────────────── */
@keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 5px rgba(255,75,75,0.3); }
    50% { box-shadow: 0 0 20px rgba(255,75,75,0.6); }
}

.action-card.critical {
    animation: pulse-border 2s ease-in-out infinite;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }
</style>
""",
    unsafe_allow_html=True,
)


# ── Helper: render an action card ──────────────────────────────────────
def render_action_card(action):
    """Render a single action card with severity styling."""
    sev = action.severity.lower()
    icon = SEVERITY_ICONS.get(action.severity, "⚪")
    time_badge = " ⏰ TIME-SENSITIVE" if action.time_sensitive else ""

    steps_html = ""
    if action.steps:
        items = "".join(f"<li>{step}</li>" for step in action.steps)
        steps_html = f'<ul class="card-steps">{items}</ul>'

    verification_html = ""
    if action.verification:
        verification_html = (
            f'<div style="margin-top:0.5rem; font-size:0.82rem; color:#888;">'
            f"✅ <em>{action.verification}</em></div>"
        )

    html = f"""
    <div class="action-card {sev} animate-in">
        <div class="card-header">
            <span class="severity-badge {sev}">{icon} {action.severity}{time_badge}</span>
            <span style="color:#888;font-size:0.8rem;">📁 {action.category}</span>
        </div>
        <div class="card-title">{action.title}</div>
        <div class="card-desc">{action.description}</div>
        {steps_html}
        {verification_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ── Helper: render results ─────────────────────────────────────────────
def render_results(result):
    """Render the full analysis result."""
    sev = result.severity.lower()
    icon = SEVERITY_ICONS.get(result.severity, "⚪")

    # Summary box
    st.markdown(
        f"""
    <div class="summary-box animate-in">
        <h3>{icon} {result.summary}</h3>
        <p>
            <span class="severity-badge {sev}">{result.severity}</span>
            &nbsp; Category: <strong>{result.category}</strong>
            &nbsp; | &nbsp; Input type: <strong>{result.raw_input_type}</strong>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key facts
    if result.key_facts:
        facts_items = "".join(f"<li>{f}</li>" for f in result.key_facts)
        st.markdown(
            f"""
        <div class="key-facts animate-in">
            <h4>🔍 Key Facts Extracted</h4>
            <ul>{facts_items}</ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Actions
    st.markdown("### 🎯 Recommended Actions")
    for action in result.actions:
        render_action_card(action)

    # Verification notes
    if result.verification_notes:
        st.markdown(
            f"""
        <div class="verification-box animate-in">
            <h4>🛡️ Verification & Sources</h4>
            <p>{result.verification_notes}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ── Helper: render map ─────────────────────────────────────────────────
def render_map(lat, lng, places):
    """Render a Folium map with nearby service markers."""
    m = folium.Map(location=[lat, lng], zoom_start=13, tiles="CartoDB dark_matter")

    # User location marker
    folium.Marker(
        [lat, lng],
        popup="📍 Your Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    # Service markers
    type_colors = {
        "hospital": "red",
        "pharmacy": "green",
        "fire_station": "orange",
        "police": "darkblue",
        "shelter": "purple",
    }
    type_icons = {
        "hospital": "plus-square",
        "pharmacy": "medkit",
        "fire_station": "fire-extinguisher",
        "police": "shield",
        "shelter": "home",
    }

    for place in places:
        color = type_colors.get(place.place_type, "gray")
        fa_icon = type_icons.get(place.place_type, "map-marker")
        popup_text = f"<b>{place.name}</b><br>{place.address}"
        if place.rating:
            popup_text += f"<br>⭐ {place.rating}"

        folium.Marker(
            [place.lat, place.lng],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=color, icon=fa_icon, prefix="fa"),
        ).add_to(m)

    st_folium(m, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════

# ── Hero Header ────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-header">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>{APP_DESCRIPTION}</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Sidebar: Input Configuration ──────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    st.markdown("### 📍 Your Location")
    st.caption("Used to find nearby emergency services on the map.")
    col_lat, col_lng = st.columns(2)
    with col_lat:
        user_lat = st.number_input("Latitude", value=28.6139, format="%.4f", key="lat")
    with col_lng:
        user_lng = st.number_input("Longitude", value=77.2090, format="%.4f", key="lng")

    st.markdown("---")

    st.markdown("### 🏥 Nearby Service Type")
    service_type = st.selectbox(
        "Find nearby",
        options=["hospital", "pharmacy", "fire_station", "police"],
        index=0,
        format_func=lambda x: {
            "hospital": "🏥 Hospitals",
            "pharmacy": "💊 Pharmacies",
            "fire_station": "🚒 Fire Stations",
            "police": "🚔 Police Stations",
        }.get(x, x),
    )

    st.markdown("---")

    st.markdown(
        """
    <div style="text-align:center; color:#666; font-size:0.8rem; margin-top:1rem;">
        Powered by<br>
        <strong style="color:#a78bfa;">Google Gemini</strong> &
        <strong style="color:#667eea;">Google Maps</strong>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── Main: Input Tabs ──────────────────────────────────────────────────
tab_text, tab_image, tab_audio = st.tabs(
    ["📝 Text Input", "📸 Image Upload", "🎙️ Audio Upload"]
)

with tab_text:
    st.markdown(
        "**Paste or type any unstructured input** — medical records, symptoms, "
        "emergency descriptions, weather alerts, news, or anything else."
    )
    text_input = st.text_area(
        "Your input",
        height=180,
        placeholder=(
            "Example: My grandmother is 78 years old. She's been having chest pain "
            "for the last 30 minutes. She takes blood thinners (Warfarin) daily and "
            "has a history of diabetes. Currently sweating and short of breath."
        ),
        label_visibility="collapsed",
    )
    text_context = st.text_input(
        "Additional context (optional)",
        placeholder="e.g., location, time of day, other relevant info",
        key="text_ctx",
    )
    text_submit = st.button(
        "🚀 Analyze Text", type="primary", use_container_width=True, key="btn_text"
    )

with tab_image:
    st.markdown(
        "**Upload a photo** — accident scene, medical document, prescription, "
        "injury, weather condition, or any visual that needs analysis."
    )
    uploaded_image = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image preview", use_container_width=True)
    image_context = st.text_input(
        "Additional context (optional)",
        placeholder="e.g., what happened, when, where",
        key="img_ctx",
    )
    image_submit = st.button(
        "🚀 Analyze Image", type="primary", use_container_width=True, key="btn_img"
    )

with tab_audio:
    st.markdown(
        "**Upload an audio recording** — voice memo describing symptoms, "
        "emergency call recording, or any audio that needs analysis."
    )
    uploaded_audio = st.file_uploader(
        "Upload an audio file",
        type=["wav", "mp3", "ogg", "m4a", "webm"],
        label_visibility="collapsed",
    )
    if uploaded_audio:
        st.audio(uploaded_audio)
    audio_context = st.text_input(
        "Additional context (optional)",
        placeholder="e.g., who is speaking, what situation",
        key="aud_ctx",
    )
    audio_submit = st.button(
        "🚀 Analyze Audio", type="primary", use_container_width=True, key="btn_aud"
    )

# ── Processing Logic ──────────────────────────────────────────────────
result = None

# Status placeholder for showing retry progress
status_area = st.empty()


def _status_callback(msg: str):
    """Update the status area with retry/fallback messages."""
    status_area.info(f"🔄 {msg}")


if text_submit and text_input.strip():
    full_text = text_input.strip()
    if text_context.strip():
        full_text += f"\n\nAdditional context: {text_context.strip()}"
    with st.spinner("🔄 Analyzing with Gemini AI..."):
        try:
            result = action_engine.process_text(full_text, status_callback=_status_callback)
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
    status_area.empty()

elif image_submit and uploaded_image:
    image_bytes = uploaded_image.getvalue()
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    ext = uploaded_image.name.rsplit(".", 1)[-1].lower()
    mime = mime_map.get(ext, "image/jpeg")
    with st.spinner("🔄 Analyzing image with Gemini AI..."):
        try:
            result = action_engine.process_image(
                image_bytes, mime, image_context, status_callback=_status_callback
            )
        except Exception as e:
            st.error(f"❌ Image analysis failed: {e}")
    status_area.empty()

elif audio_submit and uploaded_audio:
    audio_bytes = uploaded_audio.getvalue()
    mime_map = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4",
        "webm": "audio/webm",
    }
    ext = uploaded_audio.name.rsplit(".", 1)[-1].lower()
    mime = mime_map.get(ext, "audio/wav")
    with st.spinner("🔄 Analyzing audio with Gemini AI..."):
        try:
            result = action_engine.process_audio(
                audio_bytes, mime, audio_context, status_callback=_status_callback
            )
        except Exception as e:
            st.error(f"❌ Audio analysis failed: {e}")
    status_area.empty()

# ── Render Results ────────────────────────────────────────────────────
if result:
    st.markdown("---")
    render_results(result)

    # Nearby services + map
    st.markdown("---")
    st.markdown("### 🗺️ Nearby Emergency Services")
    with st.spinner("📍 Finding nearby services..."):
        try:
            places = action_engine.enrich_with_nearby_services(
                result, user_lat, user_lng, service_type
            )
            if places:
                render_map(user_lat, user_lng, places)
                # List of places
                for place in places:
                    rating_str = f"⭐ {place.rating}" if place.rating else ""
                    st.markdown(
                        f"**{place.name}** — {place.address} {rating_str}"
                    )
            else:
                st.info(
                    "No nearby services found. Make sure your Google Maps API key "
                    "is configured in `.env` and the Places API is enabled."
                )
                # Still show map with user location
                render_map(user_lat, user_lng, [])
        except Exception as e:
            st.warning(f"⚠️ Could not load nearby services: {e}")
            render_map(user_lat, user_lng, [])

# ── Empty State ───────────────────────────────────────────────────────
if not result:
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align:center; padding:3rem 1rem; color:#888;">
        <div style="font-size:3rem; margin-bottom:1rem;">🧠</div>
        <h3 style="color:#a0a0b8; font-weight:600;">Ready to Analyze</h3>
        <p style="max-width:500px; margin:0 auto; line-height:1.7;">
            Choose an input mode above — type a description, upload a photo,
            or provide an audio recording. LifeLine AI will instantly convert
            your unstructured input into structured, actionable steps.
        </p>
        <div style="margin-top:2rem; display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">🩺</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">Medical Records</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">🚨</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">Emergencies</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">🌪️</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">Weather Alerts</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">📰</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">News & Safety</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">📷</div>
                <div style="font-size:0.85rem; margin-top:0.3rem;">Photos & Scenes</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
