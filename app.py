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
.section-header { font-size:20px; font-weight:600; color:#e6edf3; margin:1rem 0 0.5rem; border-left:4px solid #238636; padding-left:12px; }
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
    st.markdown("**Team**")
    st.markdown("Predictive Wildlife Hotspot Modeling")

@st.cache_resource
def load_model():
    with open('data/model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    predictions = pd.read_csv('data/predictions.csv')
    shap_vals = pd.read_csv('data/shap_values.csv')
    shap_imp = pd.read_csv('data/shap_importance.csv')
    return predictions, shap_vals, shap_imp

model = load_model()
df, shap_vals, shap_imp = load_data()

features = ['canopy_score', 'vertical_score', 'forest_pct',
            'plantation_pct', 'tlength_km', 'is_monsoon',
            'traffic_volume', 'fencing_present', 'survey_count']

st.title("🐾 Wildlife Roadkill Hotspot Predictor")
st.markdown("**Anamalai Hills, Western Ghats** — Predictive AI model using NCF India field data (2011–2013)")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Segments</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff6b6b">{int((df["risk_probability"] >= 0.6).sum())}</div><div class="metric-label">High Risk Segments</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["incident_count"].sum())}</div><div class="metric-label">Total Incidents</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#69db7c">{len(features)}</div><div class="metric-label">Features Used</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

transect_coords = {
    'Attakatti - 1 hpb': (10.312, 76.952),
    'Azhiyar': (10.348, 76.942),
    'Chinnakallar': (10.358, 76.935),
    'Waterfalls': (10.365, 76.928),
    'Neerar Dam': (10.342, 76.918),
    'Waverly': (10.355, 76.945),
    'Old Valparai': (10.325, 76.955),
    'Balaji Temple': (10.332, 76.962),
    'Puthuthotam': (10.318, 76.938),
    'Sholayar': (10.298, 76.908),
    'Nallamudi': (10.372, 76.972),
}

st.markdown('<div class="section-header">Interactive Hotspot Map</div>', unsafe_allow_html=True)
st.markdown("Click any marker to see risk details for that road segment.")

m = folium.Map(
    location=[10.335, 76.940],
    zoom_start=13,
    tiles='CartoDB dark_matter'
)

df_map = df.groupby('transect')['risk_probability'].max().reset_index()

for _, row in df_map.iterrows():
    name = row['transect']
    risk = row['risk_probability']
    coords = transect_coords.get(name, (10.335, 76.940))

    if risk >= 0.7:
        color = '#ff4444'
        risk_text = 'HIGH RISK'
    elif risk >= 0.5:
        color = '#ff8800'
        risk_text = 'MEDIUM RISK'
    else:
        color = '#44ff88'
        risk_text = 'LOW RISK'

    incidents = int(df[df['transect'] == name]['incident_count'].sum())

    folium.CircleMarker(
        location=coords,
        radius=12 + risk * 20,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(
            f"""<div style='font-family:Arial;min-width:160px'>
            <b style='font-size:14px'>{name}</b><br>
            <span style='color:{"red" if risk>=0.7 else "orange" if risk>=0.5 else "green"};font-weight:bold'>{risk_text}</span><br>
            Risk Score: <b>{risk:.0%}</b><br>
            Total Incidents: <b>{incidents}</b>
            </div>""",
            max_width=200
        ),
        tooltip=f"{name} — {risk:.0%} risk"
    ).add_to(m)

st_folium(m, width=None, height=450)

st.markdown("---")

left, right = st.columns([1.2, 1])

with left:
    st.markdown('<div class="section-header">Risk Probability by Segment</div>', unsafe_allow_html=True)
    df_sorted = df.sort_values('risk_probability', ascending=False)
    df_sorted['risk_pct'] = (df_sorted['risk_probability'] * 100).round(1)
    df_sorted['status'] = df_sorted['risk_probability'].apply(
        lambda s: "🔴 High" if s >= 0.7 else ("🟠 Medium" if s >= 0.5 else "🟢 Low")
    )

    fig = px.bar(
        df_sorted,
        x='risk_pct',
        y='transect',
        color='risk_pct',
        orientation='h',
        color_continuous_scale=['#44ff88', '#ff8800', '#ff4444'],
        labels={'risk_pct': 'Risk (%)', 'transect': 'Segment'},
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#30363d'),
        yaxis=dict(gridcolor='#30363d')
    )
    st.plotly_chart(fig, width='stretch')

    st.dataframe(
        df_sorted[['transect', 'season', 'incident_count', 'risk_pct', 'status']].rename(
            columns={'transect': 'Segment', 'season': 'Season',
                     'incident_count': 'Incidents', 'risk_pct': 'Risk (%)',
                     'status': 'Level'}
        ),
        width='stretch',
        hide_index=True
    )

with right:
    st.markdown('<div class="section-header">Global Feature Importance (SHAP)</div>', unsafe_allow_html=True)
    st.markdown("Which features drive risk across ALL segments?")

    fig2 = px.bar(
        shap_imp.sort_values('importance'),
        x='importance',
        y='feature',
        orientation='h',
        color='importance',
        color_continuous_scale=['#1f6feb', '#58a6ff'],
        labels={'importance': 'Mean SHAP Value', 'feature': 'Feature'},
    )
    fig2.update_layout(
        height=320,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#30363d'),
        yaxis=dict(gridcolor='#30363d')
    )
    st.plotly_chart(fig2, width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-header">Inspect a Segment</div>', unsafe_allow_html=True)

    selected = st.selectbox("Choose a road segment:", df_sorted['transect'].unique())
    selected_season = st.selectbox("Choose season:", ['monsoon', 'summer'])
    row = df[(df['transect'] == selected) & (df['season'] == selected_season)]

    if len(row) > 0:
        idx = row.index[0]
        score = row['risk_probability'].values[0]
        incidents = row['incident_count'].values[0]

        if score >= 0.7:
            st.error(f"Risk Score: {score:.0%} — HIGH RISK")
        elif score >= 0.5:
            st.warning(f"Risk Score: {score:.0%} — MEDIUM RISK")
        else:
            st.success(f"Risk Score: {score:.0%} — LOW RISK")

        st.write(f"Historical incidents: **{int(incidents)}**")
        st.markdown("**Why this score? (SHAP explanation)**")

        local_shap = shap_vals.iloc[idx]
        shap_df = pd.DataFrame({
            'feature': features,
            'shap_value': local_shap.values
        }).sort_values('shap_value')

        colors = []
        for v in shap_df['shap_value']:
            if v > 0.001:
                colors.append('#ff4444')
            elif v < -0.001:
                colors.append('#58a6ff')
            else:
                colors.append('#8b949e')

        display_vals = shap_df['shap_value'].apply(
            lambda v: v if abs(v) > 0.001 else 0.005
        )

        fig3 = go.Figure(go.Bar(
            x=display_vals,
            y=shap_df['feature'],
            orientation='h',
            marker_color=colors,
            text=shap_df['shap_value'].apply(lambda v: f'{v:.3f}'),
            textposition='outside'
        ))
        fig3.update_layout(
            title='Red = increases risk | Blue = decreases risk | Gray = no effect',
            height=340,
            xaxis_title='SHAP Value',
            xaxis=dict(range=[-1, 1], gridcolor='#30363d'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3')
        )
        st.plotly_chart(fig3, width='stretch')

        top_risk = shap_df[shap_df['shap_value'] > 0].sort_values(
            'shap_value', ascending=False)
        if len(top_risk) > 0:
            top_feature = top_risk.iloc[0]['feature']
            st.info(
                f"Biggest risk driver for **{selected}** ({selected_season}) "
                f"is **{top_feature}**. {int(incidents)} historical incidents. "
                f"Predicted risk: {score:.0%}.")
    else:
        st.warning("No data for this combination.")

st.markdown("---")
st.markdown('<div class="section-header">🚨 Emerging Hotspots — Low History, High Predicted Risk</div>',
            unsafe_allow_html=True)
st.markdown("These segments had few past incidents but the model predicts high future risk:")

emerging = df[
    (df['risk_probability'] >= 0.4) &
    (df['incident_count'] <= df['incident_count'].quantile(0.6))
].sort_values('risk_probability', ascending=False)[
    ['transect', 'season', 'incident_count', 'risk_probability']
].copy()

emerging['risk_probability'] = (emerging['risk_probability'] * 100).round(1)
emerging.columns = ['Segment', 'Season', 'Past Incidents', 'Risk Score (%)']

if len(emerging) > 0:
    st.dataframe(emerging, width='stretch', hide_index=True)
    st.success(f"Found {len(emerging)} emerging hotspots that need immediate attention!")
else:
    st.info("No emerging hotspots detected.")

st.markdown("---")
st.caption("Data: Jeganathan et al. (2018) — NCF India | Model: XGBoost + SHAP | Built for wildlife conservation")

