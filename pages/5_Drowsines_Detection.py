import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Drowsiness Detection — Vanya Raksha AI", page_icon="😴", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
[data-testid="stAppViewContainer"] {
    background: #050a06;
    background-image: radial-gradient(ellipse at 15% 10%, rgba(22,101,52,0.1) 0%, transparent 55%);
}
[data-testid="stSidebar"] { background: #060d07; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3,h4,h5,h6,p,span,div,li,td,th,label,a { font-family: 'DM Sans', sans-serif !important; }
.stMarkdown p { color: #94a3b0 !important; }
.vr-page-header { font-family:'Instrument Serif',serif!important; font-size:36px; color:#f0fdf4; margin:0 0 4px; }
.vr-page-sub { font-size:14px; color:#6b7b8a; margin-bottom:24px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="vr-page-header">😴 Drowsiness Detection — Night Driving Safety</div>', unsafe_allow_html=True)
st.markdown('<div class="vr-page-sub">Uses your webcam to track eye closure. If eyes stay closed for more than 1 second, a loud alarm is triggered to wake the driver.</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(168,85,247,0.06); border:1px solid rgba(168,85,247,0.2);
            border-radius:12px; padding:16px 20px; margin-bottom:20px;">
    <div style="font-size:14px; color:#c4b5fd; line-height:1.6;">
        <b>How it works:</b> MediaPipe Face Mesh detects 468 facial landmarks in real time.
        The Eye Aspect Ratio (EAR) is calculated from eye landmarks — when EAR drops below the threshold
        for more than 1 second, the system triggers an audible alarm.<br><br>
        <b>Privacy:</b> All processing happens locally in your browser. No video is sent to any server.
    </div>
</div>
""", unsafe_allow_html=True)

# Sensitivity control
ear_threshold = st.slider("Eye Aspect Ratio (EAR) Threshold", 0.15, 0.30, 0.22, 0.01,
                          help="Lower = more sensitive. Default 0.22 works for most people.")
closed_seconds = st.slider("Alert after eyes closed for (seconds)", 0.5, 3.0, 1.0, 0.25,
                           help="How long eyes must be closed before alarm triggers.")

st.markdown("---")
st.markdown("### 📹 Live Webcam Feed")
st.markdown("Click **Start Detection** below. Allow camera access when prompted.")

# ── The full drowsiness detection runs in-browser via MediaPipe JS ────────────
DROWSINESS_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#050a06; font-family:'DM Sans',sans-serif; color:#e2e8f0; }}
  .container {{ max-width:800px; margin:0 auto; text-align:center; padding:20px; }}
  #videoContainer {{
    position:relative; display:inline-block; border-radius:16px; overflow:hidden;
    border:2px solid rgba(34,197,94,0.2); margin:16px 0;
  }}
  video {{ width:640px; height:480px; transform:scaleX(-1); display:block; }}
  canvas {{ position:absolute; top:0; left:0; width:640px; height:480px; transform:scaleX(-1); }}
  .status-bar {{
    display:flex; justify-content:center; gap:24px; margin:16px 0; flex-wrap:wrap;
  }}
  .stat {{
    background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.1);
    border-radius:12px; padding:12px 20px; min-width:120px;
  }}
  .stat-val {{ font-size:24px; font-weight:700; }}
  .stat-lbl {{ font-size:10px; color:#6b7b8a; margin-top:2px; text-transform:uppercase; letter-spacing:0.5px; }}
  #startBtn {{
    background:rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.4); color:#4ade80;
    padding:12px 32px; border-radius:10px; font-size:14px; font-weight:600; cursor:pointer;
    transition:all 0.2s;
  }}
  #startBtn:hover {{ background:rgba(34,197,94,0.25); }}
  #alertOverlay {{
    display:none; position:fixed; top:0; left:0; right:0; bottom:0;
    background:rgba(239,68,68,0.15); z-index:100;
    animation: pulse 0.5s infinite alternate;
  }}
  @keyframes pulse {{
    from {{ background:rgba(239,68,68,0.1); }}
    to {{ background:rgba(239,68,68,0.3); }}
  }}
  #alertBanner {{
    display:none; background:rgba(239,68,68,0.12); border:2px solid #ef4444;
    border-radius:12px; padding:16px; margin:12px 0; font-size:18px; font-weight:700; color:#fca5a5;
  }}
</style>
</head>
<body>
<div class="container">
  <button id="startBtn" onclick="startDetection()">▶ Start Detection</button>

  <div id="videoContainer" style="display:none;">
    <video id="video" playsinline></video>
    <canvas id="canvas"></canvas>
  </div>

  <div id="alertOverlay"></div>
  <div id="alertBanner">⚠️ WAKE UP! Eyes closed too long — pull over if drowsy!</div>

  <div class="status-bar">
    <div class="stat">
      <div class="stat-val" id="earVal" style="color:#4ade80;">—</div>
      <div class="stat-lbl">EAR Score</div>
    </div>
    <div class="stat">
      <div class="stat-val" id="eyeStatus" style="color:#4ade80;">—</div>
      <div class="stat-lbl">Eye Status</div>
    </div>
    <div class="stat">
      <div class="stat-val" id="closedTime" style="color:#60a5fa;">0.0s</div>
      <div class="stat-lbl">Closed Duration</div>
    </div>
    <div class="stat">
      <div class="stat-val" id="alertCount" style="color:#fbbf24;">0</div>
      <div class="stat-lbl">Alerts Triggered</div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js" crossorigin="anonymous"></script>

<script>
const EAR_THRESHOLD = {ear_threshold};
const CLOSED_LIMIT = {closed_seconds};

let closedStart = null;
let alertActive = false;
let totalAlerts = 0;
let audioCtx = null;

function beep() {{
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.frequency.value = 880;
  osc.type = 'square';
  gain.gain.value = 0.5;
  osc.start();
  osc.stop(audioCtx.currentTime + 0.3);
}}

function calcEAR(landmarks, indices) {{
  const p = indices.map(i => landmarks[i]);
  const vertical1 = Math.sqrt(Math.pow(p[1].x-p[5].x,2)+Math.pow(p[1].y-p[5].y,2));
  const vertical2 = Math.sqrt(Math.pow(p[2].x-p[4].x,2)+Math.pow(p[2].y-p[4].y,2));
  const horizontal = Math.sqrt(Math.pow(p[0].x-p[3].x,2)+Math.pow(p[0].y-p[3].y,2));
  return (vertical1 + vertical2) / (2.0 * horizontal);
}}

// MediaPipe Face Mesh eye landmark indices
const LEFT_EYE  = [33, 160, 158, 133, 153, 144];
const RIGHT_EYE = [362, 385, 387, 263, 373, 380];

function onResults(results) {{
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = 640; canvas.height = 480;
  ctx.clearRect(0, 0, 640, 480);

  if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {{
    const landmarks = results.multiFaceLandmarks[0];
    const leftEAR = calcEAR(landmarks, LEFT_EYE);
    const rightEAR = calcEAR(landmarks, RIGHT_EYE);
    const ear = (leftEAR + rightEAR) / 2.0;

    document.getElementById('earVal').textContent = ear.toFixed(3);

    // Draw eye points
    const allEye = [...LEFT_EYE, ...RIGHT_EYE];
    allEye.forEach(idx => {{
      const lm = landmarks[idx];
      ctx.beginPath();
      ctx.arc(lm.x*640, lm.y*480, 2, 0, 2*Math.PI);
      ctx.fillStyle = ear < EAR_THRESHOLD ? '#ef4444' : '#4ade80';
      ctx.fill();
    }});

    if (ear < EAR_THRESHOLD) {{
      document.getElementById('eyeStatus').textContent = 'CLOSED';
      document.getElementById('eyeStatus').style.color = '#f87171';
      document.getElementById('earVal').style.color = '#f87171';

      if (!closedStart) closedStart = Date.now();
      const elapsed = (Date.now() - closedStart) / 1000;
      document.getElementById('closedTime').textContent = elapsed.toFixed(1) + 's';

      if (elapsed >= CLOSED_LIMIT && !alertActive) {{
        alertActive = true;
        totalAlerts++;
        document.getElementById('alertCount').textContent = totalAlerts;
        document.getElementById('alertOverlay').style.display = 'block';
        document.getElementById('alertBanner').style.display = 'block';
        beep();
        // Keep beeping
        window._beepInterval = setInterval(beep, 500);
      }}
    }} else {{
      document.getElementById('eyeStatus').textContent = 'OPEN';
      document.getElementById('eyeStatus').style.color = '#4ade80';
      document.getElementById('earVal').style.color = '#4ade80';
      closedStart = null;
      document.getElementById('closedTime').textContent = '0.0s';

      if (alertActive) {{
        alertActive = false;
        document.getElementById('alertOverlay').style.display = 'none';
        document.getElementById('alertBanner').style.display = 'none';
        if (window._beepInterval) clearInterval(window._beepInterval);
      }}
    }}
  }}
}}

function startDetection() {{
  document.getElementById('startBtn').style.display = 'none';
  document.getElementById('videoContainer').style.display = 'inline-block';

  const video = document.getElementById('video');
  const faceMesh = new FaceMesh({{
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${{file}}`
  }});

  faceMesh.setOptions({{
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  }});

  faceMesh.onResults(onResults);

  const camera = new Camera(video, {{
    onFrame: async () => {{ await faceMesh.send({{image: video}}); }},
    width: 640,
    height: 480
  }});
  camera.start();
}}
</script>
</body>
</html>
"""

components.html(DROWSINESS_HTML, height=700, scrolling=False)

st.markdown("---")
st.markdown("""
<div style="background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.1);
            border-radius:16px; padding:20px 24px;">
    <div style="font-size:14px; font-weight:600; color:#e2e8f0; margin-bottom:10px;">
        💡 How the Eye Aspect Ratio (EAR) Works
    </div>
    <div style="font-size:13px; color:#6b7b8a; line-height:1.8;">
        The EAR is computed from 6 eye landmarks per eye — 2 horizontal points and 4 vertical points.
        When the eye is open, EAR is typically between 0.25–0.35. When the eye closes, EAR drops below 0.20.
        If EAR stays below the threshold for more than the configured duration, the system triggers an alarm.<br><br>
        <b>Formula:</b> EAR = (|p2-p6| + |p3-p5|) / (2 × |p1-p4|)<br>
        <b>Reference:</b> Soukupová & Čech, "Real-Time Eye Blink Detection using Facial Landmarks" (2016)
    </div>
</div>
""", unsafe_allow_html=True)
