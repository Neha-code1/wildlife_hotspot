import streamlit as st
import pandas as pd

from utils_data import load_dashboard_data
from yolo_utils import load_yolo_model, run_image_detection, run_video_detection

st.set_page_config(page_title="Live Animal Detection", page_icon="🦌", layout="wide")

df, _, _, _ = load_dashboard_data()

st.title("🦌 Live Animal Detection")
st.caption("Upload an image or video and trigger real-time wildlife crossing alerts.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    segment = st.selectbox("Current road segment", sorted(df["transect"].unique()))
with c2:
    season = st.selectbox("Current season", ["summer", "monsoon"], index=1)
with c3:
    conf_threshold = st.slider("Confidence threshold", 0.10, 0.90, 0.35, 0.05)
with c4:
    input_type = st.radio("Input type", ["Image", "Video"], horizontal=False)

weights_choice = st.radio(
    "Model weights",
    ["Custom wildlife model", "Default YOLO small model"],
    horizontal=True,
)

weights_path = "models/best.pt" if weights_choice == "Custom wildlife model" else "yolov8n.pt"
model = load_yolo_model(weights_path)

segment_row = df[(df["transect"] == segment) & (df["season"] == season)]
base_risk = float(segment_row["risk_probability"].iloc[0]) if not segment_row.empty else 0.0

uploaded = st.file_uploader(
    "Upload image or video",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
)

if uploaded is None:
    st.info("Upload a file to start detection.")
    st.stop()

if input_type == "Image":
    original, annotated, det_df = run_image_detection(uploaded, model, conf_threshold)

    a, b = st.columns(2)
    with a:
        st.image(original, caption="Original", use_container_width=True)
    with b:
        st.image(annotated, caption="Detected animals", use_container_width=True)

    if det_df.empty:
        st.success("No animals detected in this image.")
    else:
        st.dataframe(det_df, use_container_width=True)

        if base_risk >= 0.75:
            st.error("Critical alert: animal detected inside a historically high-risk zone. Slow down immediately.")
        elif base_risk >= 0.40:
            st.warning("Warning: animal detected in a moderate-risk zone. Be alert.")
        else:
            st.info("Animal detected, but this segment is historically lower risk. Monitor carefully.")

else:
    frames, summary_df = run_video_detection(
        uploaded,
        model,
        conf_threshold=conf_threshold,
        sample_every=15,
        max_frames=18,
    )

    if summary_df.empty:
        st.success("No animals detected in sampled video frames.")
    else:
        st.dataframe(summary_df, use_container_width=True)

        if base_risk >= 0.75:
            st.error("Critical alert: animal detections found in a high-risk hotspot corridor.")
        elif base_risk >= 0.40:
            st.warning("Warning: animal detections found in a moderate-risk corridor.")
        else:
            st.info("Animal detections found. Continue monitoring this route.")

        st.subheader("Sampled detection frames")
        for item in frames[:6]:
            st.image(item["image"], caption=f"Frame {item['frame_no']}", use_container_width=True)
            #final