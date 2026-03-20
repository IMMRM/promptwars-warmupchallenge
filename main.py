"""
LifeLine AI — Streamlit Application
Turn messy, real-world inputs into structured, verified, life-saving actions.
"""

import streamlit as st

from app import action_engine
from app.config import (
    APP_TITLE,
    APP_ICON,
    APP_DESCRIPTION,
)
from app.ui_components import apply_custom_css, render_results, render_map

# ── Page Configuration ─────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global premium styling
apply_custom_css()

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
    @st.cache_data(ttl=3600)
    def get_auto_location():
        """Auto-detect rough location based on IP address."""
        try:
            import httpx
            # Use ip-api or ipapi.co as a free, no-key IP geolocation service
            resp = httpx.get("https://ipapi.co/json/", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                return float(data.get("latitude", 28.6139)), float(data.get("longitude", 77.2090))
        except Exception:
            pass
        return 28.6139, 77.2090  # Default to New Delhi if offline/rate-limited

    auto_lat, auto_lng = get_auto_location()

    col_lat, col_lng = st.columns(2)
    with col_lat:
        user_lat = st.number_input("Latitude", value=auto_lat, format="%.4f", key="lat")
    with col_lng:
        user_lng = st.number_input("Longitude", value=auto_lng, format="%.4f", key="lng")

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
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
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
            st.session_state.analysis_result = action_engine.process_text(full_text, status_callback=_status_callback)
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
            st.session_state.analysis_result = action_engine.process_image(
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
            st.session_state.analysis_result = action_engine.process_audio(
                audio_bytes, mime, audio_context, status_callback=_status_callback
            )
        except Exception as e:
            st.error(f"❌ Audio analysis failed: {e}")
    status_area.empty()

# ── Render Results ────────────────────────────────────────────────────
if st.session_state.analysis_result:
    st.markdown("---")
    render_results(st.session_state.analysis_result)

    # Nearby services + map
    st.markdown("---")
    st.markdown("### 🗺️ Nearby Emergency Services")
    with st.spinner("📍 Finding nearby services..."):
        try:
            places = action_engine.enrich_with_nearby_services(
                st.session_state.analysis_result, user_lat, user_lng, service_type
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
if not st.session_state.analysis_result:
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
