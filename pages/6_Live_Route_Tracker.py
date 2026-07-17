import streamlit as st
import streamlit.components.v1 as components
import time
import json

st.set_page_config(page_title="Live Route Tracker — Vanya Raksha AI", page_icon="📡", layout="wide")

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
label[data-testid="stWidgetLabel"] p { color: #94a3b0 !important; }
.vr-page-header { font-family:'Instrument Serif',serif!important; font-size:36px; color:#f0fdf4; margin:0 0 4px; }
.vr-page-sub { font-size:14px; color:#6b7b8a; margin-bottom:24px; }
</style>
""", unsafe_allow_html=True)

from utils_data import load_dashboard_data, TRANSECT_ORDER, TRANSECT_COORDS, route_segments

df, _, _, _ = load_dashboard_data()

st.markdown('<div class="vr-page-header">📡 Live Route Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="vr-page-sub">Simulates GPS-based journey tracking with real-time zone alerts as you approach high-risk segments.</div>', unsafe_allow_html=True)

# ── Journey setup ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    start = st.selectbox("Entry point", TRANSECT_ORDER, index=0)
with c2:
    end = st.selectbox("Exit point", TRANSECT_ORDER, index=len(TRANSECT_ORDER)-1)
with c3:
    season = st.selectbox("Season", ["monsoon", "summer"], index=0)

c4, c5 = st.columns(2)
with c4:
    night_mode = st.toggle("Night-time driving", value=True)
with c5:
    speed = st.select_slider("Simulation speed", ["Slow", "Normal", "Fast"], value="Normal")

speed_map = {"Slow": 2.5, "Normal": 1.5, "Fast": 0.7}

segments = route_segments(start, end)
route_df = df[(df['transect'].isin(segments)) & (df['season'] == season)].copy()
route_df['route_order'] = route_df['transect'].apply(lambda x: segments.index(x) if x in segments else 99)
route_df = route_df.sort_values('route_order').reset_index(drop=True)

if route_df.empty:
    st.warning("No data for this route.")
    st.stop()

# Night modifier
if night_mode:
    route_df['adjusted_risk'] = (route_df['risk_probability'] + 0.10).clip(0, 1)
else:
    route_df['adjusted_risk'] = route_df['risk_probability']

# ── Build route data for JS map ──────────────────────────────────────────────
route_points = []
for _, row in route_df.iterrows():
    coords = TRANSECT_COORDS.get(row['transect'], (10.335, 76.940))
    risk = row['adjusted_risk']
    zone = 'high' if risk >= 0.75 else ('moderate' if risk >= 0.40 else 'low')
    route_points.append({
        'name': row['transect'],
        'lat': coords[0],
        'lng': coords[1],
        'risk': round(risk * 100, 1),
        'zone': zone,
        'incidents': int(row['incident_count']),
    })

route_json = json.dumps(route_points)

st.markdown("---")

# ── Journey simulation ───────────────────────────────────────────────────────
if st.button("🚀 Start Journey", type="primary", use_container_width=True):

    # Show live map
    map_html = f"""
    <div id="mapContainer" style="width:100%; height:420px; border-radius:16px; overflow:hidden;
         border:1px solid rgba(34,197,94,0.15);"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    const routeData = {route_json};
    const map = L.map('mapContainer').setView([routeData[0].lat, routeData[0].lng], 12);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

    // Draw route line
    const latlngs = routeData.map(p => [p.lat, p.lng]);
    L.polyline(latlngs, {{color:'#60a5fa', weight:3, opacity:0.6}}).addTo(map);

    // Add all segment markers
    routeData.forEach((p, i) => {{
        const color = p.zone === 'high' ? '#ef4444' : (p.zone === 'moderate' ? '#fbbf24' : '#4ade80');
        L.circleMarker([p.lat, p.lng], {{
            radius: 8, color: color, fillColor: color, fillOpacity: 0.3, weight: 1
        }}).bindTooltip(p.name + ' — ' + p.risk + '%').addTo(map);
    }});

    // Driver marker
    const driverIcon = L.divIcon({{
        html: '<div style="width:20px;height:20px;background:#3b82f6;border:3px solid #fff;border-radius:50%;box-shadow:0 0 12px rgba(59,130,246,0.6);"></div>',
        iconSize: [20, 20], iconAnchor: [10, 10]
    }});
    const driverMarker = L.marker([routeData[0].lat, routeData[0].lng], {{icon: driverIcon}}).addTo(map);

    // Fit bounds
    map.fitBounds(latlngs.map(l => L.latLng(l[0], l[1])).reduce((b, l) => b.extend(l), L.latLngBounds(latlngs[0], latlngs[0])));
    </script>
    """
    components.html(map_html, height=440, scrolling=False)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📍 Live Journey Alerts")

    progress = st.progress(0)
    current_segment_display = st.empty()
    alert_area = st.container()

    for i, (_, seg) in enumerate(route_df.iterrows()):
        risk = seg['adjusted_risk']
        risk_pct = round(risk * 100, 1)
        name = seg['transect']

        # Update progress
        progress.progress((i + 1) / len(route_df))
        current_segment_display.markdown(
            f"<div style='background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.1); "
            f"border-radius:12px; padding:14px 20px; font-size:14px; color:#e2e8f0;'>"
            f"📍 <b>Current location:</b> {name} &nbsp;|&nbsp; "
            f"Segment {i+1} of {len(route_df)} &nbsp;|&nbsp; "
            f"Risk: <b>{risk_pct}%</b></div>",
            unsafe_allow_html=True
        )

        with alert_area:
            if risk >= 0.75:
                st.error(
                    f"🔴 **{name}** — DANGER ZONE ({risk_pct}% risk)\n\n"
                    f"🦌 **Chances of animal crossing are HIGH**\n\n"
                    f"🚗 Reduce speed to 20 km/h immediately. Stay extremely alert for the next 1 km."
                )
                if night_mode:
                    st.error("🌙 **Night driving warning:** Visibility is severely reduced. Use high beams cautiously — they can freeze animals in place.")

            elif risk >= 0.40:
                st.warning(
                    f"🟡 **{name}** — CAUTION ({risk_pct}% risk)\n\n"
                    f"🐾 **Be alert — animal crossings are possible in this zone.**\n\n"
                    f"🚗 Reduce speed to 30 km/h. Watch for movement on both sides."
                )
            else:
                st.success(
                    f"🟢 **{name}** — Lower risk ({risk_pct}% risk)\n\n"
                    f"Continue at normal speed. Stay aware."
                )

        time.sleep(speed_map[speed])

    # Journey complete
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:30px 20px;">
        <div style="font-size:40px; margin-bottom:12px;">🏁</div>
        <div style="font-family:'Instrument Serif',serif; font-size:24px; color:#f0fdf4; margin-bottom:8px;">
            Journey Complete
        </div>
        <div style="font-size:14px; color:#6b7b8a;">
            You have safely exited the wildlife corridor. Thank you for driving carefully.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()

else:
    # Show route preview
    st.markdown("### 📋 Route Preview")
    for i, (_, seg) in enumerate(route_df.iterrows()):
        risk = seg['adjusted_risk']
        risk_pct = round(risk * 100, 1)
        if risk >= 0.75:
            st.markdown(f"**{i+1}.** 🔴 {seg['transect']} — {risk_pct}% risk")
        elif risk >= 0.40:
            st.markdown(f"**{i+1}.** 🟡 {seg['transect']} — {risk_pct}% risk")
        else:
            st.markdown(f"**{i+1}.** 🟢 {seg['transect']} — {risk_pct}% risk")
            #final
