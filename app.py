import streamlit as st
import os

st.set_page_config(
    page_title="Vanya Raksha AI",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed",
)

# ── Helper: safe page link ────────────────────────────────────────────────────
def safe_page_link(page_path, label, icon):
    try:
        st.page_link(page_path, label=label, icon=icon)
    except Exception:
        st.markdown(f"<div style='color:#4a5568;font-size:13px;padding:8px 0;'>{icon} {label} (page not found)</div>", unsafe_allow_html=True)

# ── Auto-detect page filenames ────────────────────────────────────────────────
pages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
actual_files = os.listdir(pages_dir) if os.path.exists(pages_dir) else []

def find_page(keyword):
    for f in actual_files:
        if keyword.lower() in f.lower() and f.endswith('.py'):
            return f"pages/{f}"
    return None

PAGE_WHATIF = find_page("what_if") or find_page("simulator") or "pages/1_What_If_Simulator.py"
PAGE_ANIMAL = find_page("animal") or find_page("detection") or "pages/2_Live_Animal_Detection.py"
PAGE_HOTSPOT = find_page("hotspot") or find_page("dashboard") or "pages/3_Hotspot_Dashboard.py"
PAGE_WHATSAPP = find_page("whatsapp") or find_page("alert") or "pages/4_WhatsApp_Alerts.py"
PAGE_DROWSY = find_page("drowsi") or find_page("drowsiness") or "pages/5_Drowsiness_Detection.py"
PAGE_TRACKER = find_page("tracker") or find_page("route_tracker") or "pages/6_Live_Route_Tracker.py"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&display=swap');
[data-testid="stAppViewContainer"]{background:#050a06;background-image:radial-gradient(ellipse at 15% 10%,rgba(22,101,52,.12) 0%,transparent 55%),radial-gradient(ellipse at 85% 85%,rgba(22,101,52,.06) 0%,transparent 50%);background-attachment:fixed}
[data-testid="stSidebar"]{background:#060d07;border-right:1px solid rgba(22,101,52,.2)}
[data-testid="stSidebar"] *{color:#94a3b0!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#4ade80!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1rem!important;max-width:1200px}
h1,h2,h3,h4,h5,h6{font-family:'DM Sans',sans-serif!important}
p,span,div,li,td,th,label,a{font-family:'DM Sans',sans-serif!important}
.vr-hero{text-align:center;padding:60px 20px 40px;position:relative}
.vr-hero::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:600px;background:radial-gradient(circle,rgba(34,197,94,.08) 0%,transparent 70%);pointer-events:none}
.vr-badge{display:inline-block;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);color:#4ade80;font-size:11px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;padding:6px 20px;border-radius:100px;margin-bottom:24px}
.vr-title{font-family:'Instrument Serif',serif!important;font-size:72px;font-weight:400;color:#f0fdf4;letter-spacing:-2px;line-height:1.05;margin:0 0 8px}
.vr-title em{font-style:italic;color:#4ade80}
.vr-subtitle{font-size:17px;color:#94a3b0;max-width:620px;margin:0 auto 12px;line-height:1.7;font-weight:300}
.vr-stats-row{display:flex;justify-content:center;gap:48px;margin-top:36px;flex-wrap:wrap}
.vr-stat{text-align:center}
.vr-stat-val{font-size:36px;font-weight:700;color:#f0fdf4;line-height:1}
.vr-stat-label{font-size:12px;color:#6b7b8a;margin-top:6px;text-transform:uppercase;letter-spacing:1px}
.vr-section-tag{display:inline-block;font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#4ade80;margin-bottom:8px}
.vr-section-title{font-family:'Instrument Serif',serif!important;font-size:38px;color:#f0fdf4;font-weight:400;margin:0 0 6px;letter-spacing:-.5px}
.vr-section-desc{font-size:15px;color:#6b7b8a;max-width:540px;line-height:1.6}
.vr-card{background:linear-gradient(160deg,rgba(22,101,52,.06) 0%,rgba(10,20,12,.6) 100%);border:1px solid rgba(34,197,94,.12);border-radius:20px;padding:32px 28px 28px;position:relative;overflow:hidden;height:100%}
.vr-card-icon{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:20px}
.vr-card-title{font-size:18px;font-weight:600;color:#f0fdf4;margin-bottom:8px}
.vr-card-desc{font-size:13px;color:#7a8d9a;line-height:1.65;margin-bottom:16px}
.vr-card-tags{display:flex;gap:6px;flex-wrap:wrap}
.vr-card-tag{font-size:10px;font-weight:500;padding:4px 10px;border-radius:6px;background:rgba(34,197,94,.06);color:#4ade80;border:1px solid rgba(34,197,94,.12)}
.vr-step{display:flex;gap:20px;align-items:flex-start;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.vr-step-num{width:40px;height:40px;min-width:40px;border-radius:12px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);color:#4ade80;font-size:16px;font-weight:700;display:flex;align-items:center;justify-content:center}
.vr-step-title{font-size:15px;font-weight:600;color:#e2e8f0;margin-bottom:4px}
.vr-step-desc{font-size:13px;color:#6b7b8a;line-height:1.6}
.vr-metric-card{background:rgba(10,20,12,.5);border:1px solid rgba(34,197,94,.1);border-radius:16px;padding:24px 20px;text-align:center}
.vr-metric-val{font-size:32px;font-weight:700;color:#f0fdf4}
.vr-metric-label{font-size:12px;color:#6b7b8a;margin-top:4px;letter-spacing:.5px}
.vr-footer{text-align:center;padding:40px 20px;border-top:1px solid rgba(255,255,255,.04);margin-top:40px}
.vr-footer-text{font-size:12px;color:#4a5568;line-height:1.8}
.stMarkdown p,.stMarkdown li{color:#94a3b0!important}
label[data-testid="stWidgetLabel"] p{color:#94a3b0!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="vr-hero">
    <div class="vr-badge">AI-Powered Wildlife Safety Platform</div>
    <div class="vr-title">Vanya Raksha <em>AI</em></div>
    <div class="vr-subtitle">Protecting wildlife, safeguarding travellers. An intelligent early-warning system that predicts animal-vehicle collision risk on forest highways and alerts drivers in real time.</div>
    <div class="vr-stats-row">
        <div class="vr-stat"><div class="vr-stat-val">2,473</div><div class="vr-stat-label">Incidents Analysed</div></div>
        <div class="vr-stat"><div class="vr-stat-val">11</div><div class="vr-stat-label">Road Transects</div></div>
        <div class="vr-stat"><div class="vr-stat-val">95%</div><div class="vr-stat-label">Model AUC</div></div>
        <div class="vr-stat"><div class="vr-stat-val">9</div><div class="vr-stat-label">Ecological Features</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin:20px 0 40px;">
    <div class="vr-section-tag">Platform Modules</div>
    <div class="vr-section-title">Everything You Need for Safer Forest Roads</div>
    <div class="vr-section-desc" style="margin:8px auto 0;">Six integrated modules — from predictive analytics to real-time driver alerts.</div>
</div>
""", unsafe_allow_html=True)

r1c1,r1c2,r1c3 = st.columns(3)
with r1c1:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);">🔴</div><div class="vr-card-title">Hotspot Predictor</div><div class="vr-card-desc">XGBoost predicts collision probability per 1km segment. SHAP explains <em>exactly why</em> a zone is dangerous.</div><div class="vr-card-tags"><span class="vr-card-tag">XGBoost</span><span class="vr-card-tag">SHAP</span><span class="vr-card-tag">Explainable AI</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_HOTSPOT, "Open Hotspot Dashboard →", "📊")
with r1c2:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);">🧭</div><div class="vr-card-title">Route Risk Simulator</div><div class="vr-card-desc">Plan your journey. Toggle night mode, traffic, fencing — see adjusted risk across every segment.</div><div class="vr-card-tags"><span class="vr-card-tag">What-If</span><span class="vr-card-tag">Route Planning</span><span class="vr-card-tag">Risk Scoring</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_WHATIF, "Open Route Simulator →", "🧭")
with r1c3:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);">🦌</div><div class="vr-card-title">Live Animal Detection</div><div class="vr-card-desc">Upload camera images or video — custom YOLO model detects wildlife and triggers crossing alerts.</div><div class="vr-card-tags"><span class="vr-card-tag">YOLOv8</span><span class="vr-card-tag">Computer Vision</span><span class="vr-card-tag">Real-Time</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_ANIMAL, "Open Animal Detection →", "🦌")

r2c1,r2c2,r2c3 = st.columns(3)
with r2c1:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(250,204,21,.08);border:1px solid rgba(250,204,21,.2);">📲</div><div class="vr-card-title">WhatsApp Driver Alerts</div><div class="vr-card-desc">Register number on entry. Receive zone-based WhatsApp alerts. Number auto-deleted on exit.</div><div class="vr-card-tags"><span class="vr-card-tag">Twilio API</span><span class="vr-card-tag">Real-Time Alerts</span><span class="vr-card-tag">Privacy-First</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_WHATSAPP, "Open WhatsApp Alerts →", "📲")
with r2c2:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(168,85,247,.08);border:1px solid rgba(168,85,247,.2);">😴</div><div class="vr-card-title">Drowsiness Detection</div><div class="vr-card-desc">Webcam eye tracking for night driving. Detects closed eyes >1 second, triggers loud alarm.</div><div class="vr-card-tags"><span class="vr-card-tag">MediaPipe</span><span class="vr-card-tag">Eye Tracking</span><span class="vr-card-tag">Night Safety</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_DROWSY, "Open Drowsiness Detector →", "😴")
with r2c3:
    st.markdown('<div class="vr-card"><div class="vr-card-icon" style="background:rgba(14,165,233,.08);border:1px solid rgba(14,165,233,.2);">📡</div><div class="vr-card-title">Live Route Tracker</div><div class="vr-card-desc">GPS journey simulation with real-time zone alerts as you approach high-risk segments.</div><div class="vr-card-tags"><span class="vr-card-tag">GPS Simulation</span><span class="vr-card-tag">Zone Alerts</span><span class="vr-card-tag">Journey Tracking</span></div></div>', unsafe_allow_html=True)
    safe_page_link(PAGE_TRACKER, "Open Route Tracker →", "📡")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="margin:20px 0 10px;"><div class="vr-section-tag">How It Works</div><div class="vr-section-title">From Data to Action in Four Steps</div></div>', unsafe_allow_html=True)
hw1,hw2 = st.columns(2)
with hw1:
    st.markdown('<div class="vr-step"><div class="vr-step-num">1</div><div><div class="vr-step-title">Ecological Data Ingestion</div><div class="vr-step-desc">Nine features collected for each 1km segment — canopy density, forest cover, traffic, fencing, season.</div></div></div><div class="vr-step"><div class="vr-step-num">2</div><div><div class="vr-step-title">Predictive Risk Scoring</div><div class="vr-step-desc">XGBoost classifier outputs collision probability (0–100%) — predicts future risk from present conditions.</div></div></div>', unsafe_allow_html=True)
with hw2:
    st.markdown('<div class="vr-step"><div class="vr-step-num">3</div><div><div class="vr-step-title">Explainable AI (SHAP)</div><div class="vr-step-desc">Feature-by-feature breakdowns tell officials exactly why a segment is dangerous and what to fix.</div></div></div><div class="vr-step"><div class="vr-step-num">4</div><div><div class="vr-step-title">Real-Time Driver Alerts</div><div class="vr-step-desc">WhatsApp alerts warn drivers of high-risk zones, animal crossings, and speed advisories as they travel.</div></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="margin:20px 0 10px;"><div class="vr-section-tag">Study Area</div><div class="vr-section-title">Anamalai Tiger Reserve, Western Ghats</div><div class="vr-section-desc">Tamil Nadu, India — one of the most biodiverse regions on Earth.</div></div>', unsafe_allow_html=True)
i1,i2,i3,i4 = st.columns(4)
with i1: st.markdown('<div class="vr-metric-card"><div class="vr-metric-val" style="color:#4ade80;">91%</div><div class="vr-metric-label">Accuracy</div></div>', unsafe_allow_html=True)
with i2: st.markdown('<div class="vr-metric-card"><div class="vr-metric-val" style="color:#60a5fa;">95%</div><div class="vr-metric-label">ROC-AUC</div></div>', unsafe_allow_html=True)
with i3: st.markdown('<div class="vr-metric-card"><div class="vr-metric-val" style="color:#fbbf24;">88%</div><div class="vr-metric-label">Recall</div></div>', unsafe_allow_html=True)
with i4: st.markdown('<div class="vr-metric-card"><div class="vr-metric-val" style="color:#f87171;">89%</div><div class="vr-metric-label">Precision</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="margin:20px 0 16px;"><div class="vr-section-tag">Impact</div><div class="vr-section-title">Aligned with UN Sustainable Development Goals</div></div>', unsafe_allow_html=True)
s1,s2,s3,s4 = st.columns(4)
with s1: st.markdown('<div class="vr-metric-card" style="border-color:rgba(76,159,56,.3);"><div style="font-size:11px;font-weight:700;color:#4c9f38;">SDG 15</div><div style="font-size:16px;font-weight:600;color:#f0fdf4;margin:8px 0 4px;">Life on Land</div><div style="font-size:12px;color:#6b7b8a;">Protects terrestrial wildlife & forest biodiversity.</div></div>', unsafe_allow_html=True)
with s2: st.markdown('<div class="vr-metric-card" style="border-color:rgba(253,157,36,.3);"><div style="font-size:11px;font-weight:700;color:#fd9d24;">SDG 11</div><div style="font-size:16px;font-weight:600;color:#f0fdf4;margin:8px 0 4px;">Sustainable Cities</div><div style="font-size:12px;color:#6b7b8a;">Safer road infrastructure near forest zones.</div></div>', unsafe_allow_html=True)
with s3: st.markdown('<div class="vr-metric-card" style="border-color:rgba(63,126,68,.3);"><div style="font-size:11px;font-weight:700;color:#3f7e44;">SDG 13</div><div style="font-size:16px;font-weight:600;color:#f0fdf4;margin:8px 0 4px;">Climate Action</div><div style="font-size:12px;color:#6b7b8a;">Reduces habitat fragmentation & species vulnerability.</div></div>', unsafe_allow_html=True)
with s4: st.markdown('<div class="vr-metric-card" style="border-color:rgba(38,189,226,.3);"><div style="font-size:11px;font-weight:700;color:#26bde2;">SDG 3</div><div style="font-size:16px;font-weight:600;color:#f0fdf4;margin:8px 0 4px;">Health & Wellbeing</div><div style="font-size:12px;color:#6b7b8a;">Reduces human injury from animal-vehicle collisions.</div></div>', unsafe_allow_html=True)

st.markdown("""
<div class="vr-footer">
    <div style="font-size:20px;margin-bottom:12px;">🛡️</div>
    <div style="font-size:14px;color:#4ade80;font-weight:600;margin-bottom:4px;">Vanya Raksha AI</div>
    <div class="vr-footer-text">Predictive Wildlife Hotspot Modeling using Explainable AI<br>Data: Jeganathan et al. (2018) — NCF India · Model: XGBoost + SHAP · Vision: YOLOv8<br>DSC SVCE · Blueprints 2026</div>
    <div style="margin-top:16px;display:flex;justify-content:center;gap:12px;">
        <a href="https://github.com/Neha-code1/wildlife_hotspot" target="_blank" style="display:inline-block;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.25);color:#4ade80;padding:8px 20px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">⭐ GitHub</a>
        <a href="https://github.com/Neha-code1/wildlife_hotspot/blob/main/README.md" target="_blank" style="display:inline-block;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);color:#6b7b8a;padding:8px 20px;border-radius:8px;text-decoration:none;font-size:12px;">📄 Docs</a>
    </div>
    <div style="font-size:11px;color:#2d3748;margin-top:16px;">Team: S Neha · Swathi E · Priyadarshan M · Pradyumna K S · Surya · Zeba H</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛡️ Vanya Raksha AI")
    st.markdown("---")
    st.markdown("**Pages found:**")
    for f in sorted(actual_files):
        if f.endswith('.py'): st.markdown(f"✅ `{f}`")