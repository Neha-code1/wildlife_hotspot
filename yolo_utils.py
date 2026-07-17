from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st
from PIL import Image

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    YOLO_AVAILABLE = False
    YOLO_ERROR = str(e)

try:
    import cv2
except Exception:
    cv2 = None


@st.cache_resource
def load_yolo_model(weights_path="models/best.pt"):
    if not YOLO_AVAILABLE:
        st.error(f"YOLO unavailable: {YOLO_ERROR}")
        st.stop()

    weights = Path(weights_path)
    if weights.exists():
        return YOLO(str(weights))
    return YOLO("yolov8n.pt")


def _detections_to_df(result) -> pd.DataFrame:
    rows = []
    if result.boxes is None:
        return pd.DataFrame(columns=["animal", "confidence"])

    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        label = result.names.get(cls_id, str(cls_id))
        rows.append(
            {
                "animal": label,
                "confidence": round(conf, 3),
            }
        )

    return pd.DataFrame(rows)


def run_image_detection(uploaded_file, model, conf_threshold: float = 0.35):
    image = Image.open(uploaded_file).convert("RGB")

    results = model.predict(image, conf=conf_threshold, verbose=False)
    result = results[0]

    annotated_bgr = result.plot()
    annotated_rgb = annotated_bgr[:, :, ::-1]

    det_df = _detections_to_df(result)

    return image, annotated_rgb, det_df


def run_video_detection(
    uploaded_file,
    model,
    conf_threshold: float = 0.35,
    sample_every: int = 15,
    max_frames: int = 24,
):
    if cv2 is None:
        raise ImportError(
            "OpenCV is not installed. Video detection is temporarily unavailable."
        )

    suffix = Path(uploaded_file.name).suffix or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        temp_path = tmp.name

    cap = cv2.VideoCapture(temp_path)

    frames = []
    summary = {}
    frame_no = 0

    while cap.isOpened() and len(frames) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break

        frame_no += 1

        if frame_no % sample_every != 0:
            continue

        results = model.predict(frame, conf=conf_threshold, verbose=False)
        result = results[0]

        det_df = _detections_to_df(result)

        for _, row in det_df.iterrows():
            summary[row["animal"]] = summary.get(row["animal"], 0) + 1

        annotated_bgr = result.plot()
        annotated_rgb = annotated_bgr[:, :, ::-1]

        frames.append(
            {
                "frame_no": frame_no,
                "image": annotated_rgb,
                "detections": det_df,
            }
        )

    cap.release()

    summary_df = pd.DataFrame(
        [{"animal": k, "detections": v} for k, v in summary.items()]
    )

    if not summary_df.empty:
        summary_df = summary_df.sort_values(
            "detections",
            ascending=False,
        )

    return frames, summary_df