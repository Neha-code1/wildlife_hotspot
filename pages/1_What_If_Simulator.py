import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import folium


from utils_data import (
    load_dashboard_data,
    TRANSECT_ORDER,
    TRANSECT_COORDS,
    route_segments,
    get_risk_band,
    get_alert_icon,
)

st.set_page_config(page_title="What-If Simulator", page_icon="🧭", layout="wide")

df, _, _, _ = load_dashboard_data()

st.title("🧭 What-If Route Risk Simulator")
st.caption("Plan a safer wildlife corridor route and preview high-risk zones before travel.")

c1, c2, c3 = st.columns(3)
with c1:
    start = st.selectbox("Start segment", TRANSECT_ORDER, index=0)
with c2:
    end = st.selectbox("End segment", TRANSECT_ORDER, index=len(TRANSECT_ORDER)-1)
with c3:
    season = st.selectbox("Season", ["summer", "monsoon"], index=1)

c4, c5, c6, c7 = st.columns(4)
with c4:
    night_drive = st.toggle("Night-time travel", value=True)
with c5:
    traffic_level = st.select_slider(
        "Traffic level",
        options=["Low", "Medium", "High", "Very High"],
        value="High",
    )
with c6:
    fencing_present = st.toggle("Fencing present", value=False)
with c7:
    recent_animal_signal = st.toggle("Recent animal signal", value=True)

segments = route_segments(start, end)
route_df = df[(df["transect"].isin(segments)) & (df["season"] == season)].copy()

if route_df.empty:
    st.warning("No route data found for this selection.")
    st.stop()

route_df["route_order"] = route_df["transect"].apply(lambda x: segments.index(x))
route_df = route_df.sort_values("route_order").reset_index(drop=True)

modifier = {
    "Low": -0.05,
    "Medium": 0.00,
    "High": 0.07,
    "Very High": 0.12,
}[traffic_level]

if night_drive:
    modifier += 0.10
if not fencing_present:
    modifier += 0.08
else:
    modifier -= 0.03
if recent_animal_signal:
    modifier += 0.08

route_df["adjusted_risk"] = (route_df["risk_probability"] + modifier).clip(0, 1)
route_df["adjusted_risk_pct"] = (route_df["adjusted_risk"] * 100).round(1)
route_df["risk_band"] = route_df["adjusted_risk"].apply(get_risk_band)

avg_risk = route_df["adjusted_risk"].mean()
critical_count = int((route_df["adjusted_risk"] >= 0.75).sum())
top_row = route_df.sort_values("adjusted_risk", ascending=False).iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Route segments", len(route_df))
m2.metric("Average route risk", f"{avg_risk:.0%}")
m3.metric("Critical zones", critical_count)
m4.metric("Highest-risk segment", top_row["transect"])

st.subheader("Route map")
route_coords = [TRANSECT_COORDS[s] for s in segments if s in TRANSECT_COORDS]

m = folium.Map(location=route_coords[0], zoom_start=12, tiles="CartoDB dark_matter")
folium.PolyLine(route_coords, color="#58a6ff", weight=4).add_to(m)

for _, row in route_df.iterrows():
    color = "#ff4444" if row["adjusted_risk"] >= 0.75 else "#ffd700" if row["adjusted_risk"] >= 0.40 else "#44ff88"
    folium.CircleMarker(
        location=TRANSECT_COORDS[row["transect"]],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        popup=f"{row['transect']} | {row['adjusted_risk_pct']}% | {row['risk_band']}",
    ).add_to(m)

components.html(m.get_root().render(), height=420, scrolling=False)

st.subheader("Upcoming alerts")
for _, row in route_df.iterrows():
    icon = get_alert_icon(row["adjusted_risk"])
    if row["adjusted_risk"] >= 0.75:
        st.error(f"{icon} {row['transect']}: chances of animal crossing are high. Slow down and stay alert.")
    elif row["adjusted_risk"] >= 0.40:
        st.warning(f"{icon} {row['transect']}: moderate wildlife crossing risk. Be alert.")
    else:
        st.success(f"{icon} {row['transect']}: currently lower risk.")

st.subheader("Adjusted route risk by segment")
fig = px.bar(
    route_df,
    x="adjusted_risk_pct",
    y="transect",
    orientation="h",
    color="adjusted_risk_pct",
    color_continuous_scale=["#44ff88", "#ffd700", "#ff8800", "#ff4444"],
    labels={"adjusted_risk_pct": "Adjusted risk (%)", "transect": "Segment"},
)
fig.update_layout(height=450, coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Recommended interventions")
if critical_count > 0:
    st.markdown(
        """
- Install warning signboards before the critical segments
- Add night-time thermal camera or roadside sensor
- Reduce speed in the identified corridor
- Prioritize fencing / underpass planning for the highest-risk stretch
"""
    )
else:
    st.markdown(
        """
- Continue routine monitoring
- Keep signage and patrol support active
- Use this simulation for seasonal planning
"""
    )