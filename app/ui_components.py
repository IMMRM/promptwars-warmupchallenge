"""Streamlit UI components for LifeLine AI.

Provides modular visualization elements to render actions, maps, and results.
"""

import html
import streamlit as st
import folium
from streamlit_folium import st_folium

from app.models import AnalysisResult, NearbyPlace, ActionCard
from app.config import SEVERITY_ICONS

# ── Custom CSS ────────────────────────────────────────────────────────
PREMIUM_CSS = """
<style>
/* ── Base Theme & Fonts ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0f0f1a;
    color: #e8e8f0;
}

/* ── Headings ────────────────────────────────────────────────────── */
h1, h2, h3 {
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #b4c4ff 0%, #ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Cards & Containers ──────────────────────────────────────────── */
.action-card {
    background: rgba(30, 30, 46, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
    background: rgba(40, 40, 56, 0.8);
}

/* ── Severity Styling ────────────────────────────────────────────── */
.action-card.critical { border-left: 6px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); }
.action-card.high     { border-left: 6px solid #ff9f43; background: rgba(255, 159, 67, 0.05); }
.action-card.medium   { border-left: 6px solid #feca57; background: rgba(254, 202, 87, 0.05); }
.action-card.low      { border-left: 6px solid #48dbfb; background: rgba(72, 219, 251, 0.05); }

/* ── Typography inside cards ─────────────────────────────────────── */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.5rem;
}

.card-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.card-desc {
    font-size: 0.95rem;
    color: #b2bec3;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.card-steps {
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem 1rem 1rem 2.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #dfe6e9;
    border: 1px solid rgba(255,255,255,0.02);
}
.card-steps li {
    margin-bottom: 0.4rem;
}
.card-steps li:last-child {
    margin-bottom: 0;
}

/* ── Badges ──────────────────────────────────────────────────────── */
.severity-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.severity-badge.critical { background: rgba(255, 75, 75, 0.2); color: #ff7675; border: 1px solid rgba(255, 75, 75, 0.3); }
.severity-badge.high     { background: rgba(255, 159, 67, 0.2); color: #ffb142; border: 1px solid rgba(255, 159, 67, 0.3); }
.severity-badge.medium   { background: rgba(254, 202, 87, 0.2); color: #feca57; border: 1px solid rgba(254, 202, 87, 0.3); }
.severity-badge.low      { background: rgba(72, 219, 251, 0.2); color: #48dbfb; border: 1px solid rgba(72, 219, 251, 0.3); }

/* ── Summary & Info Boxes ────────────────────────────────────────── */
.summary-box {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.key-facts {
    background: rgba(45, 52, 54, 0.4);
    border-left: 4px solid #0984e3;
    padding: 1rem 1.5rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 2rem;
}

.verification-box {
    background: rgba(0, 184, 148, 0.1);
    border: 1px solid rgba(0, 184, 148, 0.3);
    border-left: 4px solid #00b894;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-top: 2rem;
    font-size: 0.9rem;
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
"""

def apply_custom_css() -> None:
    """Inject the premium CSS styles into the Streamlit app."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def render_action_card(action: ActionCard) -> None:
    """Render a single action card with severity styling and XSS protection."""
    sev = html.escape(action.severity.lower())
    icon = html.escape(SEVERITY_ICONS.get(action.severity, "⚪"))
    time_badge = " ⏰ TIME-SENSITIVE" if action.time_sensitive else ""
    title = html.escape(action.title)
    description = html.escape(action.description)
    category = html.escape(action.category)

    steps_html = ""
    if action.steps:
        items = "".join(f"<li>{html.escape(step)}</li>" for step in action.steps)
        steps_html = f'<ul class="card-steps">{items}</ul>'

    verification_html = ""
    if action.verification:
        verification = html.escape(action.verification)
        verification_html = (
            f'<div style="margin-top:0.5rem; font-size:0.82rem; color:#888;">'
            f"✅ <em>{verification}</em></div>"
        )

    role_attr = 'role="alert" aria-live="assertive"' if action.severity in ["CRITICAL", "HIGH"] else ""

    action_html = f"""
    <article class="action-card {sev} animate-in" {role_attr}>
        <header class="card-header">
            <span class="severity-badge {sev}">{icon} {html.escape(action.severity)}{time_badge}</span>
            <span style="color:#888;font-size:0.8rem;">📁 {category}</span>
        </header>
        <h4 class="card-title" style="margin-top:0;">{title}</h4>
        <div class="card-desc">{description}</div>
        {steps_html}
        {verification_html}
    </article>
    """
    st.markdown(action_html, unsafe_allow_html=True)


def render_results(result: AnalysisResult) -> None:
    """Render the full analysis result securely."""
    sev = html.escape(result.severity.lower())
    icon = html.escape(SEVERITY_ICONS.get(result.severity, "⚪"))
    summary = html.escape(result.summary)
    category = html.escape(result.category)
    severity_label = html.escape(result.severity)
    raw_input_type = html.escape(result.raw_input_type)

    # Summary box
    st.markdown(
        f"""
    <div class="summary-box animate-in">
        <h3>{icon} {summary}</h3>
        <p>
            <span class="severity-badge {sev}">{severity_label}</span>
            &nbsp; Category: <strong>{category}</strong>
            &nbsp; | &nbsp; Input type: <strong>{raw_input_type}</strong>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key facts
    if result.key_facts:
        facts_items = "".join(f"<li>{html.escape(f)}</li>" for f in result.key_facts)
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
        verification_notes = html.escape(result.verification_notes)
        st.markdown(
            f"""
        <div class="verification-box animate-in">
            <h4>🛡️ Verification & Sources</h4>
            <p>{verification_notes}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_map(lat: float, lng: float, places: list[NearbyPlace]) -> None:
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
        
        # Protect against potential XSS in place names or addresses
        safe_name = html.escape(place.name)
        safe_address = html.escape(place.address)
        
        popup_text = f"<b>{safe_name}</b><br>{safe_address}"
        if place.rating:
            popup_text += f"<br>⭐ {html.escape(str(place.rating))}"
        if place.duration_text and place.distance_text:
            popup_text += f"<br>🚗 {html.escape(place.duration_text)} ({html.escape(place.distance_text)})"

        folium.Marker(
            [place.lat, place.lng],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=color, icon=fa_icon, prefix="fa"),
        ).add_to(m)

    # Render map in streamlit
    st_folium(m, width=800, height=500, return_on_hover=False)
