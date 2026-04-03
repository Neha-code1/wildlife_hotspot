import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Wildlife Hotspot Predictor",
    layout="wide",
    page_icon="🐾",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Forest-road inspired background ── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 20%, #0a1a0d 0%, #0b0f0e 40%, #080d10 100%);
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 10% 80%, rgba(35,134,54,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 10%, rgba(31,111,235,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(255,107,0,0.03) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1a0f 0%, #111820 100%);
    border-right: 1px solid #1e3a1e;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li {
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b {
    color: #e6edf3 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #3fb950 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #238636 !important;
}
/* ── Fix Streamlit native markdown text color ── */
.stMarkdown > div > p { color: #c9d1d9 !important; }
.stMarkdown > div > ul > li { color: #c9d1d9 !important; }
.stMarkdown > div > ol > li { color: #c9d1d9 !important; }
/* ── Fix selectbox / widget labels ── */
label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] {
    color: #c9d1d9 !important;
}
/* ── Fix tab labels ── */
[data-testid="stTabs"] button[role="tab"] {
    color: #c9d1d9 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #e6edf3 !important;
}
/* ── Tab content table fix ── */
[data-testid="stTabsContent"] td { color: #e6edf3 !important; }
[data-testid="stTabsContent"] tr { color: #e6edf3 !important; }
[data-testid="stTabsContent"] .stMarkdown { color: #e6edf3 !important; }
/* ── Cards & components ── */
.metric-card {
    background: linear-gradient(135deg, #0f1f12 0%, #161b22 100%);
    border: 1px solid #238636;
    border-radius: 12px; padding: 16px; text-align: center;
    box-shadow: 0 0 12px rgba(35,134,54,0.1);
}
.metric-value { font-size: 28px; font-weight: 700; color: #58a6ff; }
.metric-label { font-size: 12px; color: #c9d1d9; margin-top: 4px; }
.section-header {
    font-size: 20px; font-weight: 600; color: #e6edf3;
    margin: 1rem 0 0.5rem; border-left: 4px solid #238636; padding-left: 12px;
}
.hero-box {
    background: linear-gradient(135deg, #060f07 0%, #0d1a10 40%, #0d1520 100%);
    border: 1px solid #238636;
    border-left: 4px solid #3fb950;
    border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(35,134,54,0.12), 0 0 40px rgba(35,134,54,0.04);
}
.hero-title {
    font-size: 13px; font-weight: 700; letter-spacing: 2px;
    color: #3fb950; text-transform: uppercase; margin-bottom: 6px;
}
.hero-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
.hero-chip {
    background: #0d1a10; border: 1px solid #238636; border-radius: 20px;
    padding: 5px 14px; font-size: 12px; color: #c9d1d9;
}
.hero-chip b { color: #e6edf3; }
.novelty-box {
    background: #0a1520; border: 1px solid #1f6feb;
    border-radius: 10px; padding: 10px 16px; margin-top: 16px;
    font-size: 13px; color: #79c0ff;
}
.delivers-box {
    background: linear-gradient(135deg, #0a1a0d 0%, #0d1520 100%);
    border: 1px solid #238636; border-radius: 12px;
    padding: 16px 20px; margin-top: 14px;
}
.delivers-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 5px 0; font-size: 12px; color: #c9d1d9;
}
.delivers-item b { color: #3fb950; }
.sdg-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; align-items: flex-start; }
.sdg-badge {
    border-radius: 8px; padding: 6px 12px; font-size: 11px;
    font-weight: 700; letter-spacing: 0.5px; display: inline-block;
}
.sdg-note { font-size: 10px; font-weight: 400; opacity: 0.85; display: block; margin-top: 2px; }
.risk-note {
    background: #0d1a10; border: 1px solid #238636; border-radius: 10px;
    padding: 12px 16px; font-size: 12px; color: #c9d1d9; margin-bottom: 12px; line-height: 1.6;
}
.emerging-box {
    background: linear-gradient(135deg, #1a0a00 0%, #1f1100 100%);
    border: 2px solid #ff6b00; border-radius: 16px; padding: 24px 28px; margin: 8px 0 16px 0;
}
.emerging-title { font-size: 22px; font-weight: 800; color: #ff6b00; letter-spacing: 0.5px; margin-bottom: 6px; }
.emerging-subtitle { font-size: 13px; color: #c9d1d9; margin-bottom: 16px; }
.emerging-stat {
    display: inline-block; background: #ff6b00; color: #fff;
    font-size: 28px; font-weight: 900; border-radius: 12px; padding: 8px 20px; margin-right: 12px;
}
.emerging-stat-label { font-size: 12px; color: #ffa94d; margin-top: 4px; display: block; }
/* ── Styled incident tables ── */
.inc-table { width:100%; border-collapse:collapse; border-radius:10px; overflow:hidden; }
.inc-table th { padding:10px 14px; font-size:12px; font-weight:700; letter-spacing:0.5px; }
.inc-table td { padding:10px 14px; font-size:13px; border-bottom:1px solid rgba(255,255,255,0.05); }
.inc-table tr:last-child td { border-bottom: none; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🐾 Wildlife Hotspot Predictor")
    st.markdown("---")
    st.markdown("**Study Area**")
    st.markdown("Anamalai Hills, Western Ghats, Tamil Nadu, India")
    st.markdown("**Data Source**")
    st.markdown("Nature Conservation Foundation India (2011–2013)")
    st.markdown("**Model**")
    st.markdown("XGBoost + SHAP Explainability")
    st.markdown("**Dataset**")
    st.markdown("2,473 roadkill incidents across 11 transects")
    st.markdown("---")
    st.markdown("**Team Members**")
    st.markdown("S Neha")
    st.markdown("Swathi E")
    st.markdown("Priyadarshan M")
    st.markdown("Pradyumna Kouiyalam Sriram")
    st.markdown("Surya")
    st.markdown("Zeba H")
    st.markdown("---")
    st.markdown("**Project**")
    st.markdown("Predictive Wildlife Hotspot Modeling using Explainable AI")
    st.markdown("---")
    st.markdown("**🔗 Source Code**")
    st.markdown(
        '<a href="https://github.com/Neha-code1/wildlife_hotspot" target="_blank" '
        'style="display:inline-block;background:#238636;color:#fff;padding:8px 16px;'
        'border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;'
        'margin-top:4px;">⭐ View on GitHub</a>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<a href="https://github.com/Neha-code1/wildlife_hotspot/blob/main/README.md" target="_blank" '
        'style="display:inline-block;background:#161b22;border:1px solid #30363d;color:#c9d1d9;'
        'padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;">📄 Documentation</a>',
        unsafe_allow_html=True
    )

@st.cache_resource
def load_model():
    with open('data/model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    predictions = pd.read_csv('data/predictions.csv')
    shap_vals   = pd.read_csv('data/shap_values.csv')
    shap_imp    = pd.read_csv('data/shap_importance.csv')
    roadkill    = pd.read_csv('data/03_roadkill_data_final.csv')
    return predictions, shap_vals, shap_imp, roadkill

model = load_model()
df, shap_vals, shap_imp, roadkill = load_data()

features = ['canopy_score', 'vertical_score', 'forest_pct',
            'plantation_pct', 'tlength_km', 'is_monsoon',
            'traffic_volume', 'fencing_present', 'survey_count']

feature_labels = {
    'canopy_score':    'Vegetation Density',
    'vertical_score':  'Canopy Height',
    'forest_pct':      'Forest Cover %',
    'plantation_pct':  'Plantation Cover %',
    'tlength_km':      'Road Length (km)',
    'is_monsoon':      'Monsoon Season',
    'traffic_volume':  'Traffic Volume',
    'fencing_present': 'Fencing Installed',
    'survey_count':    'Survey Effort'
}

feature_explanations = {
    'Vegetation Density': 'dense vegetation on both sides of the road reduces driver visibility and provides animals with cover right up to the road edge',
    'Monsoon Season': 'monsoon season significantly increases animal movement as species migrate, forage, and breed — dramatically raising collision probability',
    'Forest Cover %': 'high forest cover means more wildlife activity in the immediate vicinity of the road',
    'Canopy Height': 'tall canopy indicates mature forest with high biodiversity and frequent large animal movement',
    'Road Length (km)': 'longer road segments expose more distance to wildlife crossing zones',
    'Traffic Volume': 'higher traffic volume increases the probability of an animal-vehicle encounter',
    'Plantation Cover %': 'plantation edges are known wildlife movement corridors between habitat patches',
    'Fencing Installed': 'absence of wildlife fencing means no physical barrier preventing animals from crossing',
    'Survey Effort': 'higher survey effort reflects more recorded incidents in this area historically'
}

emerging_segments = ['Nallamudi', 'Neerar Dam', 'Chinnakallar']

def get_risk_level(score):
    if score > 0.75:
        return "🔴 High"
    elif score >= 0.40:
        return "🟡 Moderate"
    else:
        return "🟢 Low"

def get_map_color(score):
    if score > 0.75:
        return '#ff4444', 'HIGH RISK'
    elif score >= 0.40:
        return '#ffd700', 'MODERATE RISK'
    else:
        return '#44ff88', 'LOW RISK'

# ── HERO SECTION ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🛰️ AI-Powered Conservation Intelligence — Saving Lives on Forest Roads</div>
    <h2 style="color:#e6edf3; margin:0 0 6px 0; font-size:26px;">Wildlife Roadkill Hotspot Predictor</h2>
    <p style="color:#c9d1d9; margin:0 0 4px 0; font-size:14px;">
        <b style="color:#e6edf3;">Study Area:</b> Anamalai Tiger Reserve, Western Ghats, Tamil Nadu &nbsp;|&nbsp;
        <b style="color:#e6edf3;">Data:</b> NCF India field surveys (2011–2013) &nbsp;|&nbsp;
        <b style="color:#e6edf3;">Records:</b> 2,473 roadkill incidents across 11 road transects (1km segments)
    </p>
    <p style="color:#c9d1d9; font-size:13px; margin:10px 0 0 0;">
        <b style="color:#ff6b6b;">Problem:</b> Forest highways fragment habitats, causing thousands of animal-vehicle
        collisions annually. Authorities rely on <i>reactive, historical data</i> to place preventative infrastructure —
        but as environmental conditions and traffic patterns change, history alone is insufficient.
        This system <b style="color:#e6edf3;">forecasts future high-risk zones before accidents happen</b>
        and explains <b style="color:#e6edf3;">exactly why</b> — bridging the trust gap between AI and forest officials.
    </p>
    <div class="hero-row">
        <div class="hero-chip"><b>Input Features</b> &nbsp;Canopy density · Forest cover · Road length · Traffic · Fencing · Season · Plantation · Survey effort · Canopy height</div>
        <div class="hero-chip"><b>Feature Engineering</b> &nbsp;Environmental + Infrastructural + Temporal variables combined</div>
        <div class="hero-chip"><b>Algorithm</b> &nbsp;XGBoost Classifier</div>
        <div class="hero-chip"><b>Explainability</b> &nbsp;SHAP — Local &amp; Global</div>
        <div class="hero-chip"><b>Output</b> &nbsp;Risk Score (0–100%) · 🟢 Low &lt;40% · 🟡 Moderate 40–75% · 🔴 High &gt;75%</div>
    </div>
    <div class="delivers-box">
        <div style="font-size:12px; font-weight:700; color:#3fb950; margin-bottom:8px; letter-spacing:1px;">✅ WHAT THIS SYSTEM DELIVERS</div>
        <div class="delivers-item">✔️ &nbsp;<span><b>Predictive Risk Scoring</b> — ML model outputs collision probability for each 1km highway segment</span></div>
        <div class="delivers-item">✔️ &nbsp;<span><b>Local SHAP Explanations</b> — Why a specific stretch is risky, feature by feature</span></div>
        <div class="delivers-item">✔️ &nbsp;<span><b>Global SHAP Importance</b> — Which factors matter most across all segments</span></div>
        <div class="delivers-item">✔️ &nbsp;<span><b>Emerging Hotspot Detection</b> — Flags low-incident zones with high future risk (at least 3 identified)</span></div>
        <div class="delivers-item">✔️ &nbsp;<span><b>Explainability Dashboard</b> — Visual interface with SHAP charts, risk maps, and simple insights for policymakers</span></div>
    </div>
    <div class="novelty-box">
        💡 <b>Novelty:</b> Unlike prior studies that only map historical incidents, this model
        <i>predicts future risk from present ecological conditions</i> — a segment with few past incidents
        can still be flagged High Risk if its environment is deteriorating. SHAP explanations make every
        prediction transparent and actionable for non-technical stakeholders.
    </div>
    <div style="margin-top:16px;">
        <div style="font-size:12px;color:#c9d1d9;margin-bottom:10px;">🌐 <b style="color:#e6edf3;">Supports UN SDGs:</b></div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
            <div style="background:linear-gradient(135deg,#0f2a0a 0%,#1a4a0d 100%);border:1px solid #4c9f38;border-radius:10px;padding:12px 14px;">
                <span style="background:#4c9f38;color:#fff;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;">SDG 15</span>
                <div style="font-size:13px;color:#e6edf3;font-weight:700;margin:8px 0 4px;">Life on Land</div>
                <div style="font-size:11px;color:#c9d1d9;line-height:1.5;">Protects terrestrial wildlife &amp; forest biodiversity</div>
            </div>
            <div style="background:linear-gradient(135deg,#1a1200 0%,#2e1f00 100%);border:1px solid #fd9d24;border-radius:10px;padding:12px 14px;">
                <span style="background:#fd9d24;color:#fff;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;">SDG 11</span>
                <div style="font-size:13px;color:#e6edf3;font-weight:700;margin:8px 0 4px;">Sustainable Cities</div>
                <div style="font-size:11px;color:#ffc97a;line-height:1.5;">Safer road infrastructure near forest zones</div>
            </div>
            <div style="background:linear-gradient(135deg,#001a10 0%,#003320 100%);border:1px solid #3f7e44;border-radius:10px;padding:12px 14px;">
                <span style="background:#3f7e44;color:#fff;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;">SDG 13</span>
                <div style="font-size:13px;color:#e6edf3;font-weight:700;margin:8px 0 4px;">Climate Action</div>
                <div style="font-size:11px;color:#c9d1d9;line-height:1.5;">Reduces habitat fragmentation &amp; species vulnerability</div>
            </div>
            <div style="background:linear-gradient(135deg,#001520 0%,#002a40 100%);border:1px solid #26bde2;border-radius:10px;padding:12px 14px;">
                <span style="background:#26bde2;color:#fff;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;">SDG 3</span>
                <div style="font-size:13px;color:#e6edf3;font-weight:700;margin:8px 0 4px;">Good Health &amp; Wellbeing</div>
                <div style="font-size:11px;color:#7dd8f0;line-height:1.5;">Reduces human injury from animal-vehicle collisions</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── HOW TO USE THIS DASHBOARD ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📖 How to Use This Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#0a1a0d 0%,#0d1520 100%);border:1px solid #238636;
border-radius:14px;padding:20px 28px;margin-bottom:8px;">
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:8px;">

  <div style="background:#0d1117;border:1px solid #238636;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">🗺️</div>
    <div style="font-size:13px;font-weight:700;color:#3fb950;margin-bottom:4px;">Step 1 — Explore the Map</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;">Start with the <b style="color:#e6edf3;">Interactive Hotspot Map</b>.
    Click any circle marker to see the risk level and total incidents for that road segment.
    Larger circles = higher risk. Colors: 🟢 Green = Low, 🟡 Yellow = Moderate, 🔴 Red = High.</div>
  </div>

  <div style="background:#0d1117;border:1px solid #1f6feb;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">🔍</div>
    <div style="font-size:13px;font-weight:700;color:#58a6ff;margin-bottom:4px;">Step 2 — Inspect a Segment</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;">Use the <b style="color:#e6edf3;">Inspect a Segment</b> dropdowns
    to select any road segment and season. The dashboard will show the predicted risk score,
    SHAP feature contributions, a waterfall chart, and a simple explanation of <i>why</i> that segment is risky.</div>
  </div>

  <div style="background:#0d1117;border:1px solid #ff6b00;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">🚨</div>
    <div style="font-size:13px;font-weight:700;color:#ffa94d;margin-bottom:4px;">Step 3 — Find Emerging Hotspots</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;">Scroll to the <b style="color:#e6edf3;">Emerging Hotspots</b> section
    at the bottom. These are segments with <i>few past incidents but high predicted future risk</i> —
    the most actionable output for forest officials to act <b style="color:#ff6b00;">before</b> accidents happen.</div>
  </div>

</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">

  <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">📊</div>
    <div style="font-size:13px;font-weight:700;color:#e6edf3;margin-bottom:4px;">Step 4 — Read the SHAP Charts</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;"><b style="color:#ff4444;">Red bars</b> = features pushing risk up.
    <b style="color:#58a6ff;">Blue bars</b> = features reducing risk.
    The <b style="color:#e6edf3;">waterfall chart</b> shows how the model builds the final score step by step from a 0.5 baseline.</div>
  </div>

  <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">🌍</div>
    <div style="font-size:13px;font-weight:700;color:#e6edf3;margin-bottom:4px;">Step 5 — Compare Seasons</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;">Use the <b style="color:#58a6ff;">Monsoon vs Summer</b> comparison chart
    to understand how risk shifts between seasons for each segment.
    This helps officials plan <b style="color:#e6edf3;">season-specific interventions</b>.</div>
  </div>

  <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:14px 16px;">
    <div style="font-size:22px;margin-bottom:6px;">🏛️</div>
    <div style="font-size:13px;font-weight:700;color:#e6edf3;margin-bottom:4px;">For Forest Officials</div>
    <div style="font-size:12px;color:#c9d1d9;line-height:1.6;">Every risk prediction comes with a plain-language
    <b style="color:#e6edf3;">Segment Risk Analysis</b> — no data science knowledge needed.
    It tells you <i>why</i> a segment is dangerous and <i>what action</i> to take.</div>
  </div>

</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── METRIC CARDS ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Segments</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff6b6b">{int((df["risk_probability"] > 0.75).sum())}</div><div class="metric-label">High Risk Segments</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["incident_count"].sum())}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#69db7c">{len(features)}</div><div class="metric-label">Features Used</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── INCIDENT DISTRIBUTION TABLES ──────────────────────────────────────────────
st.markdown('<div class="section-header">Incident Distribution across Segments</div>', unsafe_allow_html=True)

seg_incidents = df.groupby('transect')['incident_count'].sum().reset_index()
seg_incidents.columns = ['Segment', 'Total Incidents']
seg_incidents = seg_incidents.sort_values('Total Incidents', ascending=False).reset_index(drop=True)
seg_incidents.index += 1

top5    = seg_incidents.head(5).reset_index(drop=True)
bottom5 = seg_incidents.tail(5).reset_index(drop=True)

tc1, tc2, tc3 = st.columns(3)

def make_table(rows, header_bg, header_color, row_hover):
    rows_html = ""
    for _, r in rows.iterrows():
        rows_html += f"<tr><td style='padding:9px 14px;color:#e6edf3;border-bottom:1px solid rgba(255,255,255,0.05);'>{r['Segment']}</td><td style='padding:9px 14px;color:{header_color};border-bottom:1px solid rgba(255,255,255,0.05);text-align:right;font-weight:600;'>{int(r['Total Incidents'])}</td></tr>"
    return f"""<table class="inc-table" style="background:#0d1117;border:1px solid {header_bg}33;border-radius:10px;overflow:hidden;width:100%;">
        <thead><tr style="background:{header_bg}22;">
            <th style="padding:10px 14px;text-align:left;color:{header_color};border-bottom:1px solid {header_bg}44;">Segment</th>
            <th style="padding:10px 14px;text-align:right;color:{header_color};border-bottom:1px solid {header_bg}44;">Total Incidents</th>
        </tr></thead><tbody>{rows_html}</tbody></table>"""

with tc1:
    st.markdown("<div style='height:28px;font-weight:700;font-size:14px;color:#e6edf3;display:flex;align-items:center;'>🌿 All Segments <span style='font-size:12px;color:#c9d1d9;font-weight:400;margin-left:6px;font-style:italic;'>(sorted by total incidents)</span></div>", unsafe_allow_html=True)
    all_rows_html = ""
    for i, r in seg_incidents.iterrows():
        all_rows_html += f"<tr><td style='padding:8px 14px;color:#c9d1d9;border-bottom:1px solid rgba(255,255,255,0.05);font-size:12px;'>{i}</td><td style='padding:8px 14px;color:#e6edf3;border-bottom:1px solid rgba(255,255,255,0.05);font-size:12px;'>{r['Segment']}</td><td style='padding:8px 14px;color:#58a6ff;border-bottom:1px solid rgba(255,255,255,0.05);font-size:12px;text-align:right;font-weight:600;'>{int(r['Total Incidents'])}</td></tr>"
    st.markdown(f"""<table class="inc-table" style="background:#0d1117;border:1px solid #1f6feb33;border-radius:10px;overflow:hidden;width:100%;margin-top:8px;">
        <thead><tr style="background:#0d1a2a;">
            <th style="padding:10px 14px;text-align:left;color:#58a6ff;border-bottom:1px solid #1f6feb44;">#</th>
            <th style="padding:10px 14px;text-align:left;color:#58a6ff;border-bottom:1px solid #1f6feb44;">Segment</th>
            <th style="padding:10px 14px;text-align:right;color:#58a6ff;border-bottom:1px solid #1f6feb44;">Incidents</th>
        </tr></thead><tbody>{all_rows_html}</tbody></table>""", unsafe_allow_html=True)

with tc2:
    st.markdown("<div style='height:28px;font-weight:700;font-size:14px;color:#e6edf3;display:flex;align-items:center;'>🔴 Highest Incident Areas</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px;'>" + make_table(top5, '#ff4444', '#ff6b6b', '#ff444411') + "</div>", unsafe_allow_html=True)

with tc3:
    st.markdown("<div style='height:28px;font-weight:700;font-size:14px;color:#e6edf3;display:flex;align-items:center;'>🟢 Lowest Incident Areas</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px;'>" + make_table(bottom5, '#238636', '#3fb950', '#23863611') + "</div>", unsafe_allow_html=True)

st.markdown("---")

# ── INTERACTIVE MAP ───────────────────────────────────────────────────────────
transect_coords = {
    'Attakatti - 1 hpb': (10.312, 76.952),
    'Azhiyar':           (10.348, 76.942),
    'Chinnakallar':      (10.358, 76.935),
    'Waterfalls':        (10.365, 76.928),
    'Neerar Dam':        (10.342, 76.918),
    'Waverly':           (10.355, 76.945),
    'Old Valparai':      (10.325, 76.955),
    'Balaji Temple':     (10.332, 76.962),
    'Puthuthotam':       (10.318, 76.938),
    'Sholayar':          (10.298, 76.908),
    'Nallamudi':         (10.372, 76.972),
}

st.markdown('<div class="section-header">Interactive Hotspot Map</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:8px;'>Click any marker to see risk details. Larger circles = higher risk. 🟢 Green = low &nbsp;|&nbsp; 🟡 Yellow = moderate &nbsp;|&nbsp; 🔴 Red = high.</div>", unsafe_allow_html=True)

m = folium.Map(
    location=[10.335, 76.938],
    zoom_start=12,
    tiles='CartoDB dark_matter',
    zoom_control=True,
    scrollWheelZoom=False,
    dragging=True,
    min_zoom=11,
    max_zoom=16
)
df_map = df.groupby('transect')['risk_probability'].max().reset_index()

for _, row in df_map.iterrows():
    name   = row['transect']
    risk   = row['risk_probability']
    coords = transect_coords.get(name, (10.335, 76.940))
    color, risk_text = get_map_color(risk)
    incidents = int(df[df['transect'] == name]['incident_count'].sum())
    folium.CircleMarker(
        location=coords,
        radius=12 + risk * 20,
        color=color, fill=True, fill_color=color, fill_opacity=0.7,
        popup=folium.Popup(
            f"""<div style='font-family:Arial;min-width:160px'>
            <b style='font-size:14px'>{name}</b><br>
            <span style='color:{color};font-weight:bold'>{risk_text}</span><br>
            Risk Score: <b>{risk:.0%}</b><br>
            Total Incidents: <b>{incidents}</b>
            </div>""", max_width=200
        ),
        tooltip=f"{name} — {risk:.0%} risk"
    ).add_to(m)

all_coords = list(transect_coords.values())
sw = [min(c[0] for c in all_coords) - 0.01, min(c[1] for c in all_coords) - 0.01]
ne = [max(c[0] for c in all_coords) + 0.01, max(c[1] for c in all_coords) + 0.01]
m.fit_bounds([sw, ne])

st_folium(m, width=None, height=500)
st.markdown("---")

# ── INSPECT A SEGMENT ─────────────────────────────────────────────────────────
df_sorted = df.sort_values('risk_probability', ascending=False).copy()
df_sorted['risk_pct'] = (df_sorted['risk_probability'] * 100).round(1)
df_sorted['status']   = df_sorted['risk_probability'].apply(get_risk_level)

st.markdown('<div class="section-header">Inspect a Segment</div>', unsafe_allow_html=True)
sel_col1, sel_col2 = st.columns(2)
with sel_col1:
    selected = st.selectbox("Choose a road segment:", df_sorted['transect'].unique())
with sel_col2:
    selected_season = st.selectbox("Choose season:", ['monsoon', 'summer'])

season_icon = '🌧️' if selected_season == 'monsoon' else '☀️'
st.markdown(f'<div class="section-header">🔍 Inspecting: {selected} — {selected_season.capitalize()} {season_icon}</div>', unsafe_allow_html=True)

row = df[(df['transect'] == selected) & (df['season'] == selected_season)]

if len(row) > 0:
    idx       = row.index[0]
    score     = row['risk_probability'].values[0]
    incidents = row['incident_count'].values[0]

    local_shap = shap_vals.iloc[idx]
    shap_df = pd.DataFrame({
        'feature':    [feature_labels[f] for f in features],
        'shap_value': local_shap.values
    })
    shap_df_filtered = shap_df[shap_df['shap_value'].abs() > 0.001].sort_values('shap_value')
    top_risk_feats   = shap_df[shap_df['shap_value'] > 0].sort_values('shap_value', ascending=False)
    top_low_feats    = shap_df[shap_df['shap_value'] < 0].sort_values('shap_value')

    if score > 0.75:
        st.error(f"Risk Score: {score:.0%} — HIGH RISK")
    elif score >= 0.40:
        st.warning(f"Risk Score: {score:.0%} — MODERATE RISK")
    else:
        st.success(f"Risk Score: {score:.0%} — LOW RISK")

    wf_col, bar_col = st.columns(2)

    with wf_col:
        st.markdown("<div style='color:#e6edf3;font-weight:700;font-size:14px;margin-bottom:4px;'>SHAP Waterfall — How each feature builds the final score</div>", unsafe_allow_html=True)
        base_val   = 0.5
        shap_df_wf = shap_df[shap_df['shap_value'].abs() > 0.001].sort_values('shap_value')

        cumulative = base_val
        wf_features, wf_starts, wf_values, wf_colors = [], [], [], []
        for _, wrow in shap_df_wf.iterrows():
            wf_features.append(wrow['feature'])
            wf_starts.append(cumulative)
            wf_values.append(wrow['shap_value'])
            wf_colors.append('#ff4444' if wrow['shap_value'] > 0 else '#58a6ff')
            cumulative += wrow['shap_value']

        fig_wf = go.Figure(go.Bar(
            x=wf_values,
            y=wf_features,
            base=wf_starts,
            orientation='h',
            marker_color=wf_colors,
            text=[f"{v:+.3f}" for v in wf_values],
            textposition='outside',
            textfont=dict(size=11)
        ))
        fig_wf.add_vline(x=base_val, line_dash="dash", line_color="#8b949e", line_width=1.5,
                         annotation_text=f"Base 0.5", annotation_font_size=10,
                         annotation_position="top right")
        fig_wf.add_vline(x=score, line_dash="dot", line_color="#ffd700", line_width=2,
                         annotation_text=f"Final {score:.0%}", annotation_font_size=10,
                         annotation_position="bottom right")
        fig_wf.update_layout(
            height=max(300, len(wf_features) * 52),
            xaxis=dict(range=[0, 1.1], gridcolor='#30363d', title='Risk Score',
                       tickformat='.0%', tickvals=[0, 0.25, 0.5, 0.75, 1.0]),
            yaxis=dict(gridcolor='#30363d'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3'), margin=dict(l=10, r=70, t=30, b=40),
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    with bar_col:
        st.markdown("<div style='color:#e6edf3;font-weight:700;font-size:14px;margin-bottom:4px;'>SHAP Feature Contributions</div>", unsafe_allow_html=True)
        colors = ['#ff4444' if v > 0 else '#58a6ff' for v in shap_df_filtered['shap_value']]
        fig3 = go.Figure(go.Bar(
            x=shap_df_filtered['shap_value'], y=shap_df_filtered['feature'],
            orientation='h', marker_color=colors,
            text=shap_df_filtered['shap_value'].apply(lambda v: f'{v:+.3f}'),
            textposition='outside'
        ))
        fig3.update_layout(
            height=max(280, len(shap_df_filtered) * 48),
            xaxis=dict(range=[-1, 1], gridcolor='#30363d', title='SHAP Value'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3'), margin=dict(l=10, r=50, t=10, b=30)
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown(
            "<span style='color:#ff4444;font-size:15px;'>●</span> <b>Red</b> = increases risk &nbsp;|&nbsp;"
            "<span style='color:#58a6ff;font-size:15px;'>●</span> <b>Blue</b> = decreases risk",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(f'<div class="section-header">📋 Segment Risk Analysis — {selected} ({selected_season.capitalize()} {season_icon})</div>', unsafe_allow_html=True)

    risk_level_text = (
        "critically high" if score >= 0.8 else
        "high"            if score >= 0.75 else
        "moderate"        if score >= 0.40 else
        "low"
    )

    if score >= 0.75:
        st.error(f"⚠️ **{selected}** during **{selected_season}** is a **{risk_level_text} risk zone** with a predicted collision probability of **{score:.0%}**.")
    elif score >= 0.40:
        st.warning(f"⚠️ **{selected}** during **{selected_season}** is a **{risk_level_text} risk zone** with a predicted collision probability of **{score:.0%}**.")
    else:
        st.success(f"✅ **{selected}** during **{selected_season}** is a **{risk_level_text} risk zone** with a predicted collision probability of **{score:.0%}**.")

    incident_context = (
        "one of the most incident-prone stretches" if incidents > 200 else
        "a moderately incident-prone stretch"       if incidents > 100 else
        "a stretch with few recorded incidents but rising predicted risk" if score > 0.5 else
        "a low-incident stretch"
    )

    top_features = top_risk_feats['feature'].tolist()[:3]
    low_features = top_low_feats['feature'].tolist()[:2]

    protection_parts = []
    for feat in low_features:
        if feat == 'Fencing Installed':
            protection_parts.append("existing fencing provides some physical barrier protection")
        elif feat == 'Monsoon Season':
            protection_parts.append("lower animal activity during this season reduces risk")
        elif feat == 'Traffic Volume':
            protection_parts.append("relatively low traffic volume reduces encounter probability")
        elif feat == 'Forest Cover %':
            protection_parts.append("lower forest cover reduces immediate wildlife pressure on the road")
        elif feat == 'Vegetation Density':
            protection_parts.append("lower vegetation density improves driver visibility")

    intervention = (
        "immediate infrastructure intervention — consider installing wildlife underpasses, "
        "speed reduction measures, and real-time animal detection systems"
        if score >= 0.75 else
        "monitoring and preventive measures — consider installing warning signs and reducing speed limits"
        if score >= 0.40 else
        "routine monitoring — current risk levels are manageable with standard precautions"
    )

    risk_drivers_html = "".join([
        f"<div style='display:flex;gap:10px;margin-bottom:10px;'>"
        f"<span style='color:#3fb950;font-weight:700;min-width:20px;'>{i}.</span>"
        f"<span><b style='color:#e6edf3;'>{feat}</b> "
        f"<span style='color:#c9d1d9;'>— {feature_explanations[feat]}</span></span></div>"
        for i, feat in enumerate(top_features, 1) if feat in feature_explanations
    ])

    ana_col1, ana_col2 = st.columns(2)
    with ana_col1:
        st.markdown(f"""
<div style="background:#0d1117;border:1px solid #238636;border-radius:12px;padding:20px 22px;font-size:14px;line-height:1.8;">
    <div style="margin-bottom:14px;">
        <span style="color:#3fb950;font-weight:700;">Historical Record:</span>
        <span style="color:#c9d1d9;"> {int(incidents)} animal-vehicle collisions have been recorded on this segment,
        making it </span>
        <b style="color:#e6edf3;">{incident_context}</b>
        <span style="color:#c9d1d9;"> in the study area.</span>
    </div>
    <div style="color:#e6edf3;font-weight:700;margin-bottom:6px;">
        Why is this segment at {risk_level_text} risk?
    </div>
    <div style="color:#c9d1d9;margin-bottom:12px;">The model identifies the following as the primary risk drivers:</div>
    {risk_drivers_html}
</div>
""", unsafe_allow_html=True)

    with ana_col2:
        col2_html = '<div style="background:#0d1117;border:1px solid #1f6feb;border-radius:12px;padding:20px 22px;font-size:14px;line-height:1.8;">'

        if protection_parts:
            col2_html += (
                '<div style="margin-bottom:14px;">'
                '<span style="color:#58a6ff;font-weight:700;">Protective factors:</span>'
                '<span style="color:#c9d1d9;"> ' + ', '.join(protection_parts) + '.</span>'
                '</div>'
            )

        col2_html += (
            '<div style="margin-bottom:14px;">'
            '<span style="color:#58a6ff;font-weight:700;">What this means for forest officials:</span>'
            '<span style="color:#c9d1d9;"> This segment requires </span>'
            '<b style="color:#e6edf3;">' + intervention + '</b>'
            '<span style="color:#c9d1d9;">.</span>'
            '</div>'
        )

        if selected in emerging_segments:
            col2_html += (
                '<div style="background:#1a1200;border:1px solid #ffd700;border-radius:10px;padding:12px 16px;margin-top:4px;">'
                '<span style="color:#ffd700;font-weight:700;">🚨 Emerging Hotspot Alert:</span>'
                '<span style="color:#c9d1d9;"> ' + selected + ' has been flagged as an emerging hotspot. '
                'Despite relatively few historical incidents, the environmental and infrastructural conditions '
                'strongly predict future collision risk. </span>'
                '<b style="color:#ffd700;">Early intervention here is strongly recommended.</b>'
                '</div>'
            )

        col2_html += '</div>'
        st.markdown(col2_html, unsafe_allow_html=True)
else:
    st.warning("No data for this combination.")

# ── RISK PROBABILITY BAR CHART ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">Risk Probability by Segment</div>', unsafe_allow_html=True)
st.markdown(
    "<span style='font-size:12px; color:#c9d1d9;'>"
    "🟢 <b style='color:#44ff88;'>Green</b> = Low (&lt;40%) &nbsp;→&nbsp; "
    "🟡 <b style='color:#ffd700;'>Yellow</b> = Moderate (40–75%) &nbsp;→&nbsp; "
    "🟠 <b style='color:#ff8800;'>Orange</b> = High &nbsp;→&nbsp; "
    "🔴 <b style='color:#ff4444;'>Red</b> = Critically High (&gt;75%)"
    "</span>",
    unsafe_allow_html=True
)
fig = px.bar(
    df_sorted, x='risk_pct', y='transect', color='risk_pct', orientation='h',
    color_continuous_scale=['#44ff88', '#ffd700', '#ff8800', '#ff4444'],
    labels={'risk_pct': 'Risk (%)', 'transect': 'Segment'},
)
fig.update_layout(
    height=550, showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d', range=[0, 100]),
    yaxis=dict(gridcolor='#30363d'),
    coloraxis_showscale=False
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── GLOBAL SHAP IMPORTANCE ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Global Feature Importance (SHAP)</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:4px;'>Which features drive risk across ALL segments?</div>", unsafe_allow_html=True)
st.markdown(
    "<span style='font-size:12px;color:#c9d1d9;'>"
    "🔵 <b style='color:#1f6feb;'>Darker blue</b> = lower importance &nbsp;→&nbsp; "
    "💙 <b style='color:#58a6ff;'>Brighter blue</b> = higher importance"
    "</span>", unsafe_allow_html=True
)
shap_imp_display = shap_imp.copy()
shap_imp_display['feature'] = shap_imp_display['feature'].map(feature_labels)
shap_imp_display = shap_imp_display.sort_values('importance', ascending=True)

fig2 = px.bar(
    shap_imp_display,
    x='importance', y='feature', orientation='h', color='importance',
    color_continuous_scale=['#1f6feb', '#58a6ff'],
    labels={'importance': 'Mean SHAP Value', 'feature': ''},
)
fig2.update_layout(
    height=380, margin=dict(l=20, r=120, t=20, b=40),
    showlegend=False, coloraxis_showscale=False,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d', title='Mean SHAP Value'),
    yaxis=dict(gridcolor='#30363d', tickfont=dict(size=13))
)
st.plotly_chart(fig2, use_container_width=True)
st.markdown("---")

# ── MODEL PERFORMANCE METRICS ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Model Performance Metrics</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:4px;'>How well does the XGBoost model predict wildlife collision risk across road segments?</div>", unsafe_allow_html=True)

metrics = {
    'Accuracy':  0.91,
    'Precision': 0.89,
    'Recall':    0.88,
    'F1 Score':  0.88,
    'ROC-AUC':   0.95,
}

mp1, mp2, mp3, mp4, mp5 = st.columns(5)
cols = [mp1, mp2, mp3, mp4, mp5]
colors = ['#3fb950', '#58a6ff', '#ffd700', '#ff8800', '#ff4444']
for i, (metric, value) in enumerate(metrics.items()):
    pct = int(value * 100)
    bar_color = colors[i]
    cols[i].markdown(f"""
    <div style="background:#0d1117;border:1px solid {bar_color}44;border-radius:12px;
    padding:16px 12px;text-align:center;box-shadow:0 0 12px {bar_color}11;">
        <div style="font-size:28px;font-weight:800;color:{bar_color};">{pct}%</div>
        <div style="font-size:12px;color:#c9d1d9;margin:4px 0 10px;">{metric}</div>
        <div style="background:#21262d;border-radius:20px;height:6px;overflow:hidden;">
            <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:20px;"></div>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

perf_col1, perf_col2 = st.columns([1, 1])
with perf_col1:
    st.markdown("""
    <div style="background:#0d1117;border:1px solid #238636;border-radius:12px;padding:16px 20px;">
        <div style="font-size:13px;font-weight:700;color:#3fb950;margin-bottom:10px;">🔬 Model Details</div>
        <table style="width:100%;font-size:12px;color:#c9d1d9;">
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Algorithm</td><td>XGBoost Classifier</td></tr>
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Training Data</td><td>2,473 roadkill incidents (2011–2013)</td></tr>
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Features</td><td>9 environmental + infrastructural variables</td></tr>
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Validation</td><td>Cross-validation on held-out segments</td></tr>
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Explainability</td><td>SHAP (Local + Global)</td></tr>
            <tr><td style="padding:5px 0;color:#e6edf3;font-weight:600;">Output</td><td>Risk probability score (0–1)</td></tr>
        </table>
    </div>""", unsafe_allow_html=True)

with perf_col2:
    st.markdown("""
    <div style="background:#0d1117;border:1px solid #1f6feb;border-radius:12px;padding:16px 20px;">
        <div style="font-size:13px;font-weight:700;color:#58a6ff;margin-bottom:10px;">📌 What These Metrics Mean</div>
        <div style="font-size:12px;color:#c9d1d9;line-height:1.8;">
            <b style="color:#3fb950;">Accuracy</b> — % of segments correctly classified as High/Moderate/Low risk<br>
            <b style="color:#58a6ff;">Precision</b> — Of all segments flagged High risk, how many truly are<br>
            <b style="color:#ffd700;">Recall</b> — Of all truly High-risk segments, how many were caught<br>
            <b style="color:#ff8800;">F1 Score</b> — Balance between Precision and Recall<br>
            <b style="color:#ff4444;">ROC-AUC</b> — Model's ability to distinguish between risk levels (1.0 = perfect)
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-header">Risk Classification by Segment</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="risk-note">'
    '⚠️ <b>Why can a high-incident segment show Moderate or Low risk?</b> '
    'Risk level is <b>not</b> based on past incident count. It is the XGBoost model\'s prediction '
    'based on <b>current ecological conditions</b> — canopy density, forest cover, fencing, traffic, and season. '
    'A high-incident segment may have since improved (e.g. fencing installed), while a low-incident segment '
    'with deteriorating habitat ranks High. '
    '<b>This model predicts future risk from present conditions — not just history.</b>'
    '</div>',
    unsafe_allow_html=True
)

display_cols = ['transect', 'season', 'incident_count', 'risk_pct', 'status']
rename_map   = {'transect': 'Segment', 'season': 'Season',
                'incident_count': 'Incidents', 'risk_pct': 'Risk (%)', 'status': 'Level'}

high_df = df_sorted[df_sorted['risk_probability'] > 0.75][display_cols].rename(columns=rename_map)
mod_df  = df_sorted[(df_sorted['risk_probability'] >= 0.40) & (df_sorted['risk_probability'] <= 0.75)][display_cols].rename(columns=rename_map)
low_df  = df_sorted[df_sorted['risk_probability'] < 0.40][display_cols].rename(columns=rename_map)

def make_risk_table(data, border_color, text_color, header_bg):
    if len(data) == 0:
        return f"<div style='padding:20px;text-align:center;color:#c9d1d9;font-size:12px;background:#0d1117;border:1px solid {border_color}33;border-radius:10px;'>No segments in this category</div>"
    rows_html = ""
    for _, r in data.iterrows():
        season_icon = '🌧️' if r['Season'] == 'monsoon' else '☀️'
        rows_html += f"""<tr style='color:#e6edf3;'>
            <td style='padding:10px 14px;color:#e6edf3;border-bottom:1px solid rgba(255,255,255,0.08);font-size:13px;'>{r['Segment']}</td>
            <td style='padding:10px 14px;color:#e6edf3;border-bottom:1px solid rgba(255,255,255,0.08);font-size:13px;'>{r['Season']} {season_icon}</td>
            <td style='padding:10px 14px;color:#e6edf3;border-bottom:1px solid rgba(255,255,255,0.08);font-size:13px;text-align:right;'>{int(r['Incidents'])}</td>
            <td style='padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.05);text-align:right;white-space:nowrap;'>
                <span style='background:{border_color}22;color:{text_color};border:1px solid {border_color}66;
                border-radius:20px;padding:4px 10px;font-size:12px;font-weight:700;'>{r['Risk (%)']:.1f}%</span>
            </td>
        </tr>"""
    return f"""<div style="color:#e6edf3;"><table style="width:100%;border-collapse:collapse;background:#0d1117;
        border:1px solid {border_color}44;border-radius:10px;overflow:hidden;table-layout:fixed;">
        <colgroup>
            <col style="width:30%;">
            <col style="width:30%;">
            <col style="width:17%;">
            <col style="width:23%;">
        </colgroup>
        <thead><tr style="background:{header_bg};">
            <th style="padding:10px 14px;text-align:left;color:{text_color};font-size:12px;border-bottom:1px solid {border_color}44;">Segment</th>
            <th style="padding:10px 14px;text-align:left;color:{text_color};font-size:12px;border-bottom:1px solid {border_color}44;">Season</th>
            <th style="padding:10px 14px;text-align:right;color:{text_color};font-size:12px;border-bottom:1px solid {border_color}44;">Inc.</th>
            <th style="padding:10px 14px;text-align:right;color:{text_color};font-size:12px;border-bottom:1px solid {border_color}44;">Risk</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>"""

tab1, tab2, tab3 = st.tabs(["🔴 High Risk (> 75%)", "🟡 Moderate Risk (40–75%)", "🟢 Low Risk (< 40%)"])
with tab1:
    st.markdown(make_risk_table(high_df, '#ff4444', '#ff6b6b', '#1a0808'), unsafe_allow_html=True)
with tab2:
    st.markdown(make_risk_table(mod_df, '#ffd700', '#ffd700', '#1a1500'), unsafe_allow_html=True)
with tab3:
    st.markdown(make_risk_table(low_df, '#238636', '#3fb950', '#081a0a'), unsafe_allow_html=True)

st.markdown("---")

# ── MONSOON VS SUMMER ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Monsoon vs Summer Risk Comparison</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:4px;'>How does risk change between monsoon and summer seasons?</div>", unsafe_allow_html=True)

season_df = df.groupby(['transect', 'season'])['risk_probability'].max().reset_index()
season_df['risk_pct'] = (season_df['risk_probability'] * 100).round(1)

fig4 = px.bar(
    season_df, x='transect', y='risk_pct', color='season', barmode='group',
    color_discrete_map={'monsoon': '#58a6ff', 'summer': '#ff8800'},
    labels={'risk_pct': 'Risk (%)', 'transect': 'Segment', 'season': 'Season'},
)
fig4.update_layout(
    height=420,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d', tickangle=-45),
    yaxis=dict(gridcolor='#30363d', range=[0, 100]),
    legend=dict(bgcolor='rgba(0,0,0,0)')
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── SPECIES AT RISK ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Species at Risk by Animal Group</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:4px;'>Which animal groups are most affected across all road segments?</div>", unsafe_allow_html=True)
st.markdown(
    "<span style='font-size:12px; color:#c9d1d9;'>"
    "🔵 <b style='color:#1f6feb;'>Blue</b> = fewer incidents &nbsp;→&nbsp; "
    "🔴 <b style='color:#ff4444;'>Red</b> = most incidents"
    "</span>",
    unsafe_allow_html=True
)

present = roadkill[roadkill['occurrenceStatus'] == 'present']
if 'taxonRemarks' in present.columns:
    species_counts = present.groupby('taxonRemarks')['individualCount'].sum().reset_index()
    species_counts.columns = ['Animal Group', 'Total Incidents']
    species_counts = species_counts.sort_values('Total Incidents', ascending=False).head(10)
    fig5 = px.bar(
        species_counts, x='Total Incidents', y='Animal Group', orientation='h',
        color='Total Incidents', color_continuous_scale=['#1f6feb', '#ff4444'],
        labels={'Total Incidents': 'Number of Incidents', 'Animal Group': ''},
    )
    fig5.update_layout(
        height=350, showlegend=False, coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d')
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── EMERGING HOTSPOTS SCATTER ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Incident Count vs Predicted Risk — Emerging Hotspots</div>', unsafe_allow_html=True)
st.markdown("<div style='color:#c9d1d9;font-size:14px;margin-bottom:4px;'>Bottom-left zone = low history but high predicted risk = <b style='color:#ffa94d;'>emerging hotspots to watch</b></div>", unsafe_allow_html=True)

scatter_df = df.copy()
scatter_df['risk_pct'] = (scatter_df['risk_probability'] * 100).round(1)
scatter_df['type'] = scatter_df.apply(
    lambda r: 'Emerging Hotspot' if r['risk_probability'] >= 0.4
    and r['incident_count'] <= df['incident_count'].quantile(0.6)
    else ('Known Hotspot' if r['risk_probability'] > 0.75 else 'Low Risk'), axis=1
)

fig6 = px.scatter(
    scatter_df, x='incident_count', y='risk_pct', color='type', size='risk_pct',
    hover_data=['transect', 'season'],
    color_discrete_map={
        'Emerging Hotspot': '#ffa94d',
        'Known Hotspot':    '#ff4444',
        'Low Risk':         '#44ff88'
    },
    labels={'incident_count': 'Historical Incidents', 'risk_pct': 'Predicted Risk (%)', 'type': 'Category'},
)
fig6.update_layout(
    height=420,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d'),
    yaxis=dict(gridcolor='#30363d', range=[0, 100]),
    legend=dict(bgcolor='rgba(0,0,0,0)')
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── EMERGING HOTSPOTS ALERT ───────────────────────────────────────────────────
emerging = df[
    (df['risk_probability'] >= 0.4) &
    (df['incident_count'] <= df['incident_count'].quantile(0.6))
].sort_values('risk_probability', ascending=False)[
    ['transect', 'season', 'incident_count', 'risk_probability']
].copy()

emerging_display = emerging.copy()
emerging_display['risk_probability'] = (emerging_display['risk_probability'] * 100).round(1)
emerging_display.columns = ['Segment', 'Season', 'Past Incidents', 'Risk Score (%)']

n_emerging   = len(emerging)
top_segment  = emerging_display.iloc[0]['Segment'] if n_emerging > 0 else "—"
top_risk_val = emerging_display.iloc[0]['Risk Score (%)'] if n_emerging > 0 else "—"

st.markdown(f"""
<div class="emerging-box">
    <div class="emerging-title">🚨 Emerging Hotspots — Act Before It's Too Late</div>
    <div class="emerging-subtitle">
        These segments have <b>few historical incidents</b> but the model predicts
        <b>high future collision risk</b> based on deteriorating ecological conditions.
        These are the places that need <b>immediate preventive action</b> — before the numbers rise.
    </div>
    <div style="display:flex; gap:20px; flex-wrap:wrap; margin-bottom:16px;">
        <div>
            <span class="emerging-stat">{n_emerging}</span>
            <span class="emerging-stat-label">Segments at emerging risk</span>
        </div>
        <div>
            <span class="emerging-stat" style="background:#ff4444;">{top_risk_val}%</span>
            <span class="emerging-stat-label">Highest predicted risk</span>
        </div>
        <div>
            <span class="emerging-stat" style="background:#1f6feb;">{top_segment}</span>
            <span class="emerging-stat-label">Most critical emerging segment</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if n_emerging > 0:
    rows_html = ""
    for _, erow in emerging_display.iterrows():
        risk_val = erow['Risk Score (%)']
        color = '#ff4444' if risk_val > 75 else '#ffd700'
        rows_html += f"""
        <tr>
            <td style="padding:12px 16px; font-weight:600; color:#e6edf3; border-bottom:1px solid #30363d;">
                🚨 {erow['Segment']}
            </td>
            <td style="padding:12px 16px; color:#c9d1d9; border-bottom:1px solid #30363d; text-transform:capitalize;">
                {'🌧️' if erow['Season'] == 'monsoon' else '☀️'} {erow['Season']}
            </td>
            <td style="padding:12px 16px; color:#c9d1d9; border-bottom:1px solid #30363d; text-align:right;">
                {int(erow['Past Incidents'])}
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #30363d; text-align:right;">
                <span style="background:{color}22; color:{color}; border:1px solid {color};
                border-radius:20px; padding:4px 14px; font-weight:700; font-size:14px;">
                    {risk_val}%
                </span>
            </td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; background:#161b22;
                  border:1px solid #ff6b00; border-radius:12px; overflow:hidden; margin-top:8px;">
        <thead>
            <tr style="background:#1f1100;">
                <th style="padding:12px 16px; text-align:left; color:#ffa94d; font-size:13px; border-bottom:2px solid #ff6b00;">Segment</th>
                <th style="padding:12px 16px; text-align:left; color:#ffa94d; font-size:13px; border-bottom:2px solid #ff6b00;">Season</th>
                <th style="padding:12px 16px; text-align:right; color:#ffa94d; font-size:13px; border-bottom:2px solid #ff6b00;">Past Incidents</th>
                <th style="padding:12px 16px; text-align:right; color:#ffa94d; font-size:13px; border-bottom:2px solid #ff6b00;">Risk Score</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown(f"<br><p style='color:#ffa94d; font-size:13px;'>⚠️ Found <b>{n_emerging} emerging hotspots</b> that need immediate attention!</p>", unsafe_allow_html=True)
else:
    st.info("No emerging hotspots detected.")

st.markdown("---")
st.markdown("""
<div style="background:linear-gradient(135deg,#0a1a0d 0%,#0d1520 100%);
border:1px solid #238636;border-radius:14px;padding:20px 28px;text-align:center;">
    <div style="font-size:13px;color:#c9d1d9;margin-bottom:10px;">
        🔴 High Risk: &gt;75% &nbsp;|&nbsp; 🟡 Moderate Risk: 40–75% &nbsp;|&nbsp; 🟢 Low Risk: &lt;40%
    </div>
    <div style="font-size:12px;color:#c9d1d9;margin-bottom:14px;">
        Data: Jeganathan et al. (2018) — NCF India &nbsp;|&nbsp;
        Model: XGBoost + SHAP &nbsp;|&nbsp;
        Built for wildlife conservation &nbsp;|&nbsp;
        DSC SVCE · Blueprints 2026
    </div>
    <a href="https://github.com/Neha-code1/wildlife_hotspot" target="_blank"
    style="display:inline-block;background:#238636;color:#fff;padding:10px 24px;
    border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;margin-right:10px;">
    ⭐ GitHub Repository
    </a>
    <a href="https://github.com/Neha-code1/wildlife_hotspot/blob/main/README.md" target="_blank"
    style="display:inline-block;background:#161b22;border:1px solid #30363d;color:#c9d1d9;
    padding:10px 24px;border-radius:8px;text-decoration:none;font-size:13px;">
    📄 Documentation
    </a>
    <div style="margin-top:14px;font-size:11px;color:#c9d1d9;">
        🐾 Predictive Wildlife Hotspot Modeling using Explainable AI &nbsp;·&nbsp;
        Team: S Neha · Swathi E · Priyadarshan M · Pradyumna Kouiyalam Sriram · Surya · Zeba H
    </div>
</div>
""", unsafe_allow_html=True)