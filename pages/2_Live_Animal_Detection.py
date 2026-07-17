import streamlit as st
import pandas as pd
from utils_data import load_dashboard_data

st.set_page_config(page_title="Live Animal Detection — Vanya Raksha AI", page_icon="🦌", layout="wide")

# ── Matching theme CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
[data-testid="stAppViewContainer"] {
    background: #050a06;
    background-image: radial-gradient(ellipse at 15% 10%, rgba(22,101,52,0.1) 0%, transparent 55%);
}
[data-testid="stSidebar"] { background: #060d07; border-right: 1px solid rgba(22,101,52,0.15); }
[data-testid="stSidebar"] * { color: #94a3b0 !important; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3,h4,h5,h6,p,span,div,li,td,th,label,a { font-family: 'DM Sans', sans-serif !important; }
.stMarkdown p { color: #94a3b0 !important; }
label[data-testid="stWidgetLabel"] p { color: #94a3b0 !important; }

.vr-page-header {
    font-family: 'Instrument Serif', serif !important;
    font-size: 36px; color: #f0fdf4; margin: 0 0 4px;
}
.vr-page-sub { font-size: 14px; color: #6b7b8a; margin-bottom: 24px; }
.detection-card {
    background: rgba(10,20,12,0.5);
    border: 1px solid rgba(34,197,94,0.12);
    border-radius: 16px; padding: 20px; text-align: center;
}
.det-val { font-size: 36px; font-weight: 700; line-height: 1; }
.det-lbl { font-size: 11px; color: #6b7b8a; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.alert-box {
    border-radius: 14px; padding: 18px 22px; margin: 12px 0;
    font-size: 14px; line-height: 1.6;
}
.alert-high {
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25); color: #fca5a5;
}
.alert-mod {
    background: rgba(250,204,21,0.08); border: 1px solid rgba(250,204,21,0.25); color: #fde68a;
}
.alert-low {
    background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15); color: #bbf7d0;
}
.result-section {
    background: rgba(10,20,12,0.3);
    border: 1px solid rgba(34,197,94,0.1);
    border-radius: 16px; padding: 20px; margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Import YOLO utils ─────────────────────────────────────────────────────────
try:
    import yolo_utils
    from yolo_utils import load_yolo_model, run_image_detection, run_video_detection
    yolo_available = True
except ImportError as e:
    yolo_available = False
    yolo_error = str(e)

df, _, _, _ = load_dashboard_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="vr-page-header">🦌 Live Animal Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="vr-page-sub">Upload an image or video from a roadside camera — our YOLO model detects wildlife in real time and triggers crossing alerts.</div>', unsafe_allow_html=True)

if not yolo_available:
    st.error(f"YOLO module not available: {yolo_error}. Please install: `pip install ultralytics`")
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    segment = st.selectbox("Current road segment", sorted(df["transect"].unique()))
with c2:
    season = st.selectbox("Current season", ["summer", "monsoon"], index=1)
with c3:
    conf_threshold = st.slider("Confidence threshold", 0.10, 0.90, 0.35, 0.05)

c4, c5 = st.columns(2)
with c4:
    input_options = ["Image"] if yolo_utils.cv2 is None else ["Image", "Video"]
    input_type = st.radio("Input type", input_options, horizontal=True)
    if yolo_utils.cv2 is None:
        st.caption("⚠️ Video disabled — OpenCV not installed.")
with c5:
    weights_choice = st.radio(
        "Model weights",
        ["Custom wildlife model", "Default YOLO small model"],
        horizontal=True,
    )

weights_path = "models/best.pt" if weights_choice == "Custom wildlife model" else "yolov8n.pt"
model = load_yolo_model(weights_path)

# Get baseline risk for this segment
segment_row = df[(df["transect"] == segment) & (df["season"] == season)]
base_risk = float(segment_row["risk_probability"].iloc[0]) if not segment_row.empty else 0.0

# ── Segment risk context ──────────────────────────────────────────────────────
risk_pct = round(base_risk * 100, 1)
if base_risk >= 0.75:
    zone_color = "#f87171"; zone_text = "HIGH RISK"; zone_border = "rgba(239,68,68,0.3)"
elif base_risk >= 0.40:
    zone_color = "#fbbf24"; zone_text = "MODERATE RISK"; zone_border = "rgba(250,204,21,0.3)"
else:
    zone_color = "#4ade80"; zone_text = "LOW RISK"; zone_border = "rgba(34,197,94,0.3)"

st.markdown(f"""
<div style="background:rgba(10,20,12,0.5); border:1px solid {zone_border};
            border-radius:12px; padding:14px 20px; margin:8px 0 16px;">
    <span style="font-size:13px; color:#94a3b0;">Current segment risk:</span>
    <span style="font-size:18px; font-weight:700; color:{zone_color}; margin-left:8px;">{risk_pct}% — {zone_text}</span>
    <span style="font-size:13px; color:#6b7b8a; margin-left:12px;">{segment} · {season.capitalize()}</span>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload image or video",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
)

if uploaded is None:
    st.markdown("""
    <div style="background:rgba(14,165,233,0.06); border:1px solid rgba(14,165,233,0.15);
                border-radius:14px; padding:40px; text-align:center; margin-top:20px;">
        <div style="font-size:40px; margin-bottom:12px;">📷</div>
        <div style="font-size:16px; color:#e2e8f0; font-weight:500;">Upload a file to start detection</div>
        <div style="font-size:13px; color:#6b7b8a; margin-top:6px;">
            Supports JPG, JPEG, PNG for images · MP4, MOV, AVI for video
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
if input_type == "Image":
    original, annotated, det_df = run_image_detection(uploaded, model, conf_threshold)

    # ── Results header ────────────────────────────────────────────────────────
    n_animals = len(det_df) if not det_df.empty else 0

    # Count by class
    if not det_df.empty and 'class' in det_df.columns:
        class_counts = det_df['class'].value_counts().to_dict()
    elif not det_df.empty and 'name' in det_df.columns:
        class_counts = det_df['name'].value_counts().to_dict()
    else:
        class_counts = {}

    # Metric cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        animal_color = "#f87171" if n_animals > 0 else "#4ade80"
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:{animal_color};">{n_animals}</div><div class="det-lbl">Animals Detected</div></div>', unsafe_allow_html=True)
    with m2:
        n_classes = len(class_counts)
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:#60a5fa;">{n_classes}</div><div class="det-lbl">Species / Classes</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:{zone_color};">{risk_pct}%</div><div class="det-lbl">Zone Risk Level</div></div>', unsafe_allow_html=True)
    with m4:
        threat = "CRITICAL" if n_animals > 0 and base_risk >= 0.75 else ("HIGH" if n_animals > 0 else "CLEAR")
        threat_color = "#f87171" if threat == "CRITICAL" else ("#fbbf24" if threat == "HIGH" else "#4ade80")
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:{threat_color};">{threat}</div><div class="det-lbl">Threat Level</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Images side by side ───────────────────────────────────────────────────
    a, b = st.columns(2)
    with a:
        st.markdown("**📷 Original Image**")
        st.image(original, use_container_width=True)
    with b:
        st.markdown("**🔍 Detection Result**")
        st.image(annotated, use_container_width=True)

    # ── Detection details ─────────────────────────────────────────────────────
    if n_animals == 0:
        st.markdown("""
        <div class="alert-box alert-low">
            ✅ <b>No animals detected</b> in this image at the current confidence threshold.
            The road appears clear.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Species breakdown
        if class_counts:
            species_text = " · ".join([f"**{count}× {name}**" for name, count in class_counts.items()])
            st.markdown(f"**Detected:** {species_text}")

        # Show detection dataframe
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("**📋 Detection Details**")
        st.dataframe(det_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Alert based on zone risk
        if base_risk >= 0.75:
            st.markdown("""
            <div class="alert-box alert-high">
                🚨 <b>CRITICAL ALERT:</b> Animal detected inside a <b>HIGH-RISK</b> wildlife zone.<br>
                🦌 Chances of animal crossing are extremely high.<br>
                🚗 <b>Slow down immediately. Reduce speed to 20 km/h.</b><br>
                📢 Alert has been triggered for this segment.
            </div>
            """, unsafe_allow_html=True)
        elif base_risk >= 0.40:
            st.markdown("""
            <div class="alert-box alert-mod">
                ⚠️ <b>WARNING:</b> Animal detected in a <b>MODERATE-RISK</b> zone.<br>
                🐾 Be alert — further crossings are possible.<br>
                🚗 Reduce speed to 30 km/h. Watch for movement on both sides.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box alert-low">
                ℹ️ Animal detected, but this segment is currently <b>LOWER RISK</b>.<br>
                Continue monitoring. Drive carefully.
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VIDEO DETECTION
# ══════════════════════════════════════════════════════════════════════════════
else:
    frames, summary_df = run_video_detection(
        uploaded, model,
        conf_threshold=conf_threshold,
        sample_every=15,
        max_frames=18,
    )

    n_detections = len(summary_df) if not summary_df.empty else 0

    # Metric cards
    m1, m2, m3 = st.columns(3)
    with m1:
        det_color = "#f87171" if n_detections > 0 else "#4ade80"
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:{det_color};">{n_detections}</div><div class="det-lbl">Detections Found</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:#60a5fa;">{len(frames)}</div><div class="det-lbl">Frames Sampled</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="detection-card"><div class="det-val" style="color:{zone_color};">{risk_pct}%</div><div class="det-lbl">Zone Risk</div></div>', unsafe_allow_html=True)

    if n_detections == 0:
        st.markdown("""
        <div class="alert-box alert-low">
            ✅ <b>No animals detected</b> in sampled video frames. Road appears clear.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("**📋 Video Detection Summary**")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if base_risk >= 0.75:
            st.markdown('<div class="alert-box alert-high">🚨 <b>CRITICAL:</b> Animal detections found in a <b>HIGH-RISK</b> corridor. Immediate caution required.</div>', unsafe_allow_html=True)
        elif base_risk >= 0.40:
            st.markdown('<div class="alert-box alert-mod">⚠️ <b>WARNING:</b> Animal detections in a <b>MODERATE-RISK</b> corridor. Stay alert.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-low">ℹ️ Detections found. Continue monitoring this route.</div>', unsafe_allow_html=True)

    # Show sampled frames
    if frames:
        st.markdown("---")
        st.markdown("**🎬 Sampled Detection Frames**")
        cols = st.columns(3)
        for i, item in enumerate(frames[:6]):
            with cols[i % 3]:
                st.image(item["image"], caption=f"Frame {item['frame_no']}", use_container_width=True)
                #final