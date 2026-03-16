import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Wildlife Hotspot Predictor", layout="wide", page_icon="🐾")

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
st.markdown("**Anamalai Hills, Western Ghats** — NCF India field data (2011–2013)")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Segments", len(df))
col2.metric("High Risk Segments", int((df['risk_probability'] >= 0.6).sum()))
col3.metric("Total Incidents", int(df['incident_count'].sum()))
col4.metric("Features Used", len(features))

st.markdown("---")

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Risk Probability by Segment")
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
        color_continuous_scale=['green', 'orange', 'red'],
        labels={'risk_pct': 'Risk (%)', 'transect': 'Segment'},
        title='Risk Score per Transect'
    )
    fig.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig, width='stretch')
    st.dataframe(
        df_sorted[['transect', 'season', 'incident_count', 'risk_pct', 'status']].rename(
            columns={'transect': 'Segment', 'season': 'Season',
                     'incident_count': 'Incidents', 'risk_pct': 'Risk (%)', 'status': 'Level'}
        ),
        width='stretch',
        hide_index=True
    )

with right:
    st.subheader("Global Feature Importance (SHAP)")
    fig2 = px.bar(
        shap_imp.sort_values('importance'),
        x='importance',
        y='feature',
        orientation='h',
        color='importance',
        color_continuous_scale=['lightblue', 'darkblue'],
        labels={'importance': 'Mean SHAP Value', 'feature': 'Feature'},
        title='What drives risk overall?'
    )
    fig2.update_layout(height=320, showlegend=False)
    st.plotly_chart(fig2, width='stretch')

    st.markdown("---")
    st.subheader("Inspect a Segment")
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
                colors.append('#D85A30')
            elif v < -0.001:
                colors.append('#185FA5')
            else:
                colors.append('#888780')

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
            title='Red=increases risk | Blue=decreases risk | Gray=no effect',
            height=340,
            xaxis_title='SHAP Value',
            xaxis=dict(range=[-1, 1])
        )
        st.plotly_chart(fig3, width='stretch')

        top_risk = shap_df[shap_df['shap_value'] > 0].sort_values('shap_value', ascending=False)
        if len(top_risk) > 0:
            top_feature = top_risk.iloc[0]['feature']
            st.info(f"Biggest risk driver for **{selected}** ({selected_season}) is **{top_feature}**. "
                    f"{int(incidents)} historical incidents. Predicted risk: {score:.0%}.")
    else:
        st.warning("No data for this combination.")

st.markdown("---")
st.subheader("🚨 Emerging Hotspots — Low History, High Predicted Risk")
st.markdown("Segments with few past incidents but high predicted future risk:")

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
    st.success(f"Found {len(emerging)} emerging hotspots that need attention!")
else:
    st.info("No emerging hotspots detected.")

st.markdown("---")
st.caption("Data: Jeganathan et al. (2018) — NCF India | Model: XGBoost + SHAP")

