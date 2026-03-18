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
[data-testid="stAppViewContainer"] { background-color: #0e1117; }
[data-testid="stSidebar"] { background-color: #161b22; }
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.metric-value { font-size: 28px; font-weight: 700; color: #58a6ff; }
.metric-label { font-size: 12px; color: #8b949e; margin-top: 4px; }
.section-header {
    font-size: 20px; font-weight: 600; color: #e6edf3;
    margin: 1rem 0 0.5rem; border-left: 4px solid #238636; padding-left: 12px;
}
.hero-box {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #1a2332 100%);
    border: 1px solid #30363d;
    border-left: 4px solid #238636;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.hero-title {
    font-size: 13px; font-weight: 700; letter-spacing: 2px;
    color: #238636; text-transform: uppercase; margin-bottom: 6px;
}
.hero-row {
    display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px;
}
.hero-chip {
    background: #21262d; border: 1px solid #30363d; border-radius: 20px;
    padding: 5px 14px; font-size: 12px; color: #8b949e;
}
.hero-chip b { color: #e6edf3; }
.novelty-box {
    background: #1a2332; border: 1px solid #1f6feb;
    border-radius: 10px; padding: 10px 16px; margin-top: 16px;
    font-size: 13px; color: #79c0ff;
}
.sdg-row {
    display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; align-items: flex-start;
}
.sdg-badge {
    border-radius: 8px; padding: 6px 12px; font-size: 11px;
    font-weight: 700; letter-spacing: 0.5px; display: inline-block;
}
.sdg-note {
    font-size: 10px; font-weight: 400; opacity: 0.85;
    display: block; margin-top: 2px;
}
.risk-note {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 12px 16px; font-size: 12px; color: #8b949e; margin-bottom: 12px;
    line-height: 1.6;
}
.emerging-box {
    background: linear-gradient(135deg, #1a0a00 0%, #1f1100 100%);
    border: 2px solid #ff6b00;
    border-radius: 16px;
    padding: 24px 28px;
    margin: 8px 0 16px 0;
}
.emerging-title {
    font-size: 22px; font-weight: 800; color: #ff6b00;
    letter-spacing: 0.5px; margin-bottom: 6px;
}
.emerging-subtitle {
    font-size: 13px; color: #8b949e; margin-bottom: 16px;
}
.emerging-stat {
    display: inline-block; background: #ff6b00;
    color: #fff; font-size: 28px; font-weight: 900;
    border-radius: 12px; padding: 8px 20px; margin-right: 12px;
}
.emerging-stat-label {
    font-size: 12px; color: #ffa94d; margin-top: 4px; display: block;
}
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
    st.markdown("Priyadarshan M")
    st.markdown("S Neha")
    st.markdown("Pradyumna Koyiyalam Sriram")
    st.markdown("Surya S")
    st.markdown("Swathi E")
    st.markdown("Zeba H")
    st.markdown("---")
    st.markdown("**Project**")
    st.markdown("Predictive Wildlife Hotspot Modeling using Explainable AI")

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
    <p style="color:#8b949e; margin:0 0 4px 0; font-size:14px;">
        <b style="color:#e6edf3;">Study Area:</b> Anamalai Tiger Reserve, Western Ghats, Tamil Nadu &nbsp;|&nbsp;
        <b style="color:#e6edf3;">Data:</b> NCF India field surveys (2011–2013) &nbsp;|&nbsp;
        <b style="color:#e6edf3;">Records:</b> 2,473 roadkill incidents across 11 road transects
    </p>
    <p style="color:#8b949e; font-size:13px; margin:10px 0 0 0;">
        <b style="color:#ff6b6b;">Problem:</b> Forest highways fragment habitats, causing thousands of animal-vehicle
        collisions annually. Reactive measures arrive only after fatalities. This system
        <b style="color:#e6edf3;">predicts where the next collision will occur</b> — before it happens —
        enabling proactive intervention by forest officials.
    </p>
    <div class="hero-row">
        <div class="hero-chip"><b>Input Features</b> &nbsp;Canopy density · Forest cover · Road length · Traffic · Fencing · Season · Plantation · Survey effort · Canopy height</div>
        <div class="hero-chip"><b>Algorithm</b> &nbsp;XGBoost Classifier</div>
        <div class="hero-chip"><b>Explainability</b> &nbsp;SHAP Values</div>
        <div class="hero-chip"><b>Output</b> &nbsp;Risk Score (0–100%) · 🔴 High &gt;75% · 🟡 Moderate 40–75% · 🟢 Low &lt;40%</div>
    </div>
    <div class="novelty-box">
        💡 <b>Novelty:</b> Unlike prior studies that only map historical incidents, this model
        <i>predicts future risk from present ecological conditions</i> — a segment with few past incidents
        can still be flagged High Risk if its environment is deteriorating. SHAP explanations make every
        prediction transparent and actionable for non-technical stakeholders.
    </div>
    <div class="sdg-row">
        <span style="font-size:12px; color:#8b949e; align-self:center; margin-right:4px;">🌐 Supports UN SDGs:</span>
        <div style="display:inline-block;">
            <span class="sdg-badge" style="background:#3f7e44; color:#fff;">SDG 15 · Life on Land</span>
            <span class="sdg-note" style="color:#6abf69;">Protects terrestrial wildlife &amp; forest biodiversity</span>
        </div>
        <div style="display:inline-block;">
            <span class="sdg-badge" style="background:#fd6925; color:#fff;">SDG 11 · Sustainable Cities</span>
            <span class="sdg-note" style="color:#ffa07a;">Safer road infrastructure near forest zones</span>
        </div>
        <div style="display:inline-block;">
            <span class="sdg-badge" style="background:#3f7e44; color:#fff;">SDG 13 · Climate Action</span>
            <span class="sdg-note" style="color:#6abf69;">Reduces habitat fragmentation &amp; species vulnerability</span>
        </div>
        <div style="display:inline-block;">
            <span class="sdg-badge" style="background:#4c9f38; color:#fff;">SDG 3 · Good Health &amp; Wellbeing</span>
            <span class="sdg-note" style="color:#90ee90;">Reduces human injury from animal-vehicle collisions</span>
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

seg_incidents = df[['transect', 'season', 'incident_count']].copy()
seg_incidents.columns = ['Segment', 'Season', 'Total Incidents']
seg_incidents = seg_incidents.sort_values('Total Incidents', ascending=False).reset_index(drop=True)
seg_incidents.index += 1

transect_totals = df.groupby('transect')['incident_count'].sum().reset_index()
transect_totals.columns = ['Segment', 'Total Incidents']
transect_totals = transect_totals.sort_values('Total Incidents', ascending=False).reset_index(drop=True)

top5    = transect_totals.head(5).reset_index(drop=True)
bottom5 = transect_totals.tail(5).reset_index(drop=True)

tc1, tc2, tc3 = st.columns(3)
with tc1:
    st.markdown("**📊 All Segments** *(sorted by incidents)*")
    st.dataframe(seg_incidents, hide_index=False, height=350, use_container_width=True)
with tc2:
    st.markdown("**🔴 Top 5 — Highest Incident Areas**")
    st.dataframe(top5, hide_index=True, height=230, use_container_width=True)
with tc3:
    st.markdown("**🟢 Bottom 5 — Lowest Incident Areas**")
    st.dataframe(bottom5, hide_index=True, height=230, use_container_width=True)

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
st.markdown("Click any marker to see risk details. Larger circles = higher risk. 🔴 Red = high &nbsp;|&nbsp; 🟡 Yellow = moderate &nbsp;|&nbsp; 🟢 Green = low.")

m = folium.Map(location=[10.335, 76.940], zoom_start=13, tiles='CartoDB dark_matter')
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

st_folium(m, width=None, height=450)
st.markdown("---")

# ── RISK BAR CHART + INSPECT SEGMENT ──────────────────────────────────────────
df_sorted = df.sort_values('risk_probability', ascending=False).copy()
df_sorted['risk_pct'] = (df_sorted['risk_probability'] * 100).round(1)
df_sorted['status']   = df_sorted['risk_probability'].apply(get_risk_level)

left, right = st.columns([1.2, 1])

with left:
    st.markdown('<div class="section-header">Risk Probability by Segment</div>', unsafe_allow_html=True)
    fig = px.bar(
        df_sorted, x='risk_pct', y='transect', color='risk_pct', orientation='h',
        color_continuous_scale=['#44ff88', '#ffd700', '#ff8800', '#ff4444'],
        labels={'risk_pct': 'Risk (%)', 'transect': 'Segment'},
    )
    fig.update_layout(
        height=520, showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#30363d', range=[0, 100]),
        yaxis=dict(gridcolor='#30363d'),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── FULL RISK SUMMARY TABLE ──
    st.markdown('<div class="section-header">All Segments — Risk Summary</div>', unsafe_allow_html=True)
    st.dataframe(
        df_sorted[['transect', 'season', 'incident_count', 'risk_pct', 'status']].rename(
            columns={'transect': 'Segment', 'season': 'Season',
                     'incident_count': 'Incidents', 'risk_pct': 'Risk (%)', 'status': 'Level'}
        ),
        use_container_width=True, hide_index=True, height=420
    )

with right:
    st.markdown('<div class="section-header">Inspect a Segment</div>', unsafe_allow_html=True)
    selected        = st.selectbox("Choose a road segment:", df_sorted['transect'].unique())
    selected_season = st.selectbox("Choose season:", ['monsoon', 'summer'])
    row = df[(df['transect'] == selected) & (df['season'] == selected_season)]

    if len(row) > 0:
        idx       = row.index[0]
        score     = row['risk_probability'].values[0]
        incidents = row['incident_count'].values[0]

        if score > 0.75:
            st.error(f"Risk Score: {score:.0%} — HIGH RISK")
        elif score >= 0.40:
            st.warning(f"Risk Score: {score:.0%} — MODERATE RISK")
        else:
            st.success(f"Risk Score: {score:.0%} — LOW RISK")

        st.write(f"Historical incidents: **{int(incidents)}**")

        # ── LOCAL SHAP BAR CHART (only non-zero features) ──
        st.markdown("**Why this score? — SHAP Feature Contributions**")

        local_shap = shap_vals.iloc[idx]
        shap_df = pd.DataFrame({
            'feature':    [feature_labels[f] for f in features],
            'shap_value': local_shap.values
        })
        # Filter out zero/negligible contributions
        shap_df = shap_df[shap_df['shap_value'].abs() > 0.001].sort_values('shap_value')

        colors = ['#ff4444' if v > 0 else '#58a6ff' for v in shap_df['shap_value']]

        fig3 = go.Figure(go.Bar(
            x=shap_df['shap_value'],
            y=shap_df['feature'],
            orientation='h',
            marker_color=colors,
            text=shap_df['shap_value'].apply(lambda v: f'{v:+.3f}'),
            textposition='outside'
        ))
        fig3.update_layout(
            height=max(250, len(shap_df) * 45),
            xaxis_title='SHAP Value',
            xaxis=dict(range=[-1, 1], gridcolor='#30363d'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3'), margin=dict(l=10, r=50, t=10, b=40)
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown(
            "<span style='color:#ff4444;font-size:16px;'>●</span> <b>Red</b> = increases risk &nbsp;|&nbsp;"
            "<span style='color:#58a6ff;font-size:16px;'>●</span> <b>Blue</b> = decreases risk",
            unsafe_allow_html=True
        )

        # ── LOCAL SHAP WATERFALL CHART ──
        st.markdown("**SHAP Waterfall — How each feature builds the final score**")

        base_val = 0.5
        shap_df_wf = pd.DataFrame({
            'feature':    [feature_labels[f] for f in features],
            'shap_value': local_shap.values
        }).sort_values('shap_value', ascending=False)
        shap_df_wf = shap_df_wf[shap_df_wf['shap_value'].abs() > 0.001]

        cumulative = base_val
        starts, ends, labels, bar_colors = [], [], [], []
        for _, wrow in shap_df_wf.iterrows():
            starts.append(cumulative)
            ends.append(cumulative + wrow['shap_value'])
            labels.append(wrow['feature'])
            bar_colors.append('#ff4444' if wrow['shap_value'] > 0 else '#58a6ff')
            cumulative += wrow['shap_value']

        fig_wf = go.Figure()
        for i in range(len(starts)):
            fig_wf.add_trace(go.Bar(
                x=[ends[i] - starts[i]],
                y=[labels[i]],
                base=[starts[i]],
                orientation='h',
                marker_color=bar_colors[i],
                name=labels[i],
                showlegend=False,
                text=f"{ends[i] - starts[i]:+.3f}",
                textposition='outside'
            ))

        fig_wf.add_vline(x=base_val, line_dash="dash", line_color="#8b949e",
                         annotation_text=f"Base={base_val}", annotation_position="top")
        fig_wf.add_vline(x=score, line_dash="dot", line_color="#ffd700",
                         annotation_text=f"Final={score:.0%}", annotation_position="bottom")
        fig_wf.update_layout(
            height=max(250, len(shap_df_wf) * 45),
            xaxis=dict(range=[0, 1], gridcolor='#30363d', title='Risk Score'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3'), margin=dict(l=10, r=50, t=20, b=40),
            barmode='overlay'
        )
        st.plotly_chart(fig_wf, use_container_width=True)

        top_risk = shap_df[shap_df['shap_value'] > 0].sort_values('shap_value', ascending=False)
        if len(top_risk) > 0:
            top_feature = top_risk.iloc[0]['feature']
            st.info(f"Biggest risk driver for **{selected}** ({selected_season}) is **{top_feature}**. "
                    f"{int(incidents)} historical incidents. Predicted risk: {score:.0%}.")
    else:
        st.warning("No data for this combination.")

st.markdown("---")

# ── GLOBAL SHAP IMPORTANCE ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Global Feature Importance (SHAP)</div>', unsafe_allow_html=True)
st.markdown("Which features drive risk across ALL segments?")
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

# ── RISK CLASSIFICATION TABLES (3 parallel) ───────────────────────────────────
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

rc1, rc2, rc3 = st.columns(3)
with rc1:
    st.markdown("**🔴 High Risk** *(> 75%)*")
    st.dataframe(high_df, hide_index=True, height=300, use_container_width=True)
with rc2:
    st.markdown("**🟡 Moderate Risk** *(40–75%)*")
    st.dataframe(mod_df, hide_index=True, height=300, use_container_width=True)
with rc3:
    st.markdown("**🟢 Low Risk** *(< 40%)*")
    st.dataframe(low_df, hide_index=True, height=300, use_container_width=True)

st.markdown("---")

# ── MONSOON VS SUMMER ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Monsoon vs Summer Risk Comparison</div>', unsafe_allow_html=True)
st.markdown("How does risk change between monsoon and summer seasons?")

season_df = df.groupby(['transect', 'season'])['risk_probability'].max().reset_index()
season_df['risk_pct'] = (season_df['risk_probability'] * 100).round(1)

fig4 = px.bar(
    season_df, x='transect', y='risk_pct', color='season', barmode='group',
    color_discrete_map={'monsoon': '#58a6ff', 'summer': '#ff8800'},
    labels={'risk_pct': 'Risk (%)', 'transect': 'Segment', 'season': 'Season'},
)
fig4.update_layout(
    height=380,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d', tickangle=45),
    yaxis=dict(gridcolor='#30363d', range=[0, 100]),
    legend=dict(bgcolor='rgba(0,0,0,0)')
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── SPECIES AT RISK ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Species at Risk by Animal Group</div>', unsafe_allow_html=True)
st.markdown("Which animal groups are most affected across all road segments?")

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
st.markdown("Bottom-left zone = low history but high predicted risk = **emerging hotspots to watch**")

scatter_df = df.copy()
scatter_df['risk_pct'] = (scatter_df['risk_probability'] * 100).round(1)
scatter_df['type'] = scatter_df.apply(
    lambda r: '🚨 Emerging Hotspot' if r['risk_probability'] >= 0.4
    and r['incident_count'] <= df['incident_count'].quantile(0.6)
    else ('🔴 Known Hotspot' if r['risk_probability'] > 0.75 else '🟢 Low Risk'), axis=1
)

fig6 = px.scatter(
    scatter_df, x='incident_count', y='risk_pct', color='type', size='risk_pct',
    hover_data=['transect', 'season'],
    color_discrete_map={
        '🚨 Emerging Hotspot': '#ffa94d',
        '🔴 Known Hotspot':    '#ff4444',
        '🟢 Low Risk':         '#44ff88'
    },
    labels={'incident_count': 'Historical Incidents', 'risk_pct': 'Predicted Risk (%)', 'type': 'Category'},
)
fig6.update_layout(
    height=400,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3'),
    xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d'),
    legend=dict(bgcolor='rgba(0,0,0,0)')
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── EMERGING HOTSPOTS — HIGHLIGHTED ALERT SECTION ─────────────────────────────
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
    st.dataframe(emerging_display, use_container_width=True, hide_index=True)
else:
    st.info("No emerging hotspots detected.")

st.markdown("---")
st.caption("🔴 High Risk: >75% | 🟡 Moderate Risk: 40–75% | 🟢 Low Risk: <40%")
st.caption("Data: Jeganathan et al. (2018) — NCF India | Model: XGBoost + SHAP | Built for wildlife conservation")