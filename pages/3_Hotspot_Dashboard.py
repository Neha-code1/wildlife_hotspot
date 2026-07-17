import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
import folium

st.set_page_config(page_title="Hotspot Dashboard — Vanya Raksha AI", page_icon="📊", layout="wide")

# ── Shared CSS (dark forest theme) ────────────────────────────────────────────
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
h1,h2,h3,h4,h5,h6 { font-family: 'DM Sans', sans-serif !important; }
p,span,div,li,td,th,label,a { font-family: 'DM Sans', sans-serif !important; }
.stMarkdown p { color: #94a3b0 !important; }
label[data-testid="stWidgetLabel"] p { color: #94a3b0 !important; }
[data-testid="stTabs"] button[role="tab"] { color: #6b7b8a !important; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #4ade80 !important; }

.vr-page-header { font-family:'Instrument Serif',serif!important; font-size:36px; color:#f0fdf4; margin:0 0 4px; }
.vr-page-sub { font-size:14px; color:#6b7b8a; margin-bottom:24px; }
.mc { background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.1); border-radius:16px;
      padding:20px 16px; text-align:center; }
.mc-val { font-size:28px; font-weight:700; color:#f0fdf4; }
.mc-lbl { font-size:11px; color:#6b7b8a; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px; }
.sh { font-size:18px; font-weight:600; color:#e2e8f0; margin:1.5rem 0 0.5rem;
      border-left:3px solid #4ade80; padding-left:12px; }
.risk-note { background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.1);
             border-radius:12px; padding:14px 18px; font-size:13px; color:#6b7b8a; margin-bottom:16px; line-height:1.7; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('data/model.pkl','rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    return (
        pd.read_csv('data/predictions.csv'),
        pd.read_csv('data/shap_values.csv'),
        pd.read_csv('data/shap_importance.csv'),
        pd.read_csv('data/03_roadkill_data_final.csv'),
    )

model = load_model()
df, shap_vals, shap_imp, roadkill = load_data()

features = ['canopy_score','vertical_score','forest_pct','plantation_pct',
            'tlength_km','is_monsoon','traffic_volume','fencing_present','survey_count']
feature_labels = {
    'canopy_score':'Vegetation Density','vertical_score':'Canopy Height',
    'forest_pct':'Forest Cover %','plantation_pct':'Plantation Cover %',
    'tlength_km':'Road Length (km)','is_monsoon':'Monsoon Season',
    'traffic_volume':'Traffic Volume','fencing_present':'Fencing Installed',
    'survey_count':'Survey Effort'
}
feature_explanations = {
    'Vegetation Density':'dense vegetation reduces driver visibility and provides animals cover',
    'Monsoon Season':'monsoon increases animal movement — migration, foraging, breeding',
    'Forest Cover %':'high forest cover means more wildlife near the road',
    'Canopy Height':'tall canopy indicates mature forest with high biodiversity',
    'Road Length (km)':'longer segments expose more distance to crossing zones',
    'Traffic Volume':'higher traffic increases encounter probability',
    'Plantation Cover %':'plantation edges are known wildlife movement corridors',
    'Fencing Installed':'absence of fencing means no physical barrier',
    'Survey Effort':'higher survey effort reflects more recorded incidents historically'
}

transect_coords = {
    'Attakatti - 1 hpb':(10.312,76.952),'Azhiyar':(10.348,76.942),
    'Chinnakallar':(10.358,76.935),'Waterfalls':(10.365,76.928),
    'Neerar Dam':(10.342,76.918),'Waverly':(10.355,76.945),
    'Old Valparai':(10.325,76.955),'Balaji Temple':(10.332,76.962),
    'Puthuthotam':(10.318,76.938),'Sholayar':(10.298,76.908),
    'Nallamudi':(10.372,76.972),
}
emerging_segments = ['Nallamudi','Neerar Dam','Chinnakallar']

def get_risk_level(s): return "🔴 High" if s>0.75 else ("🟡 Moderate" if s>=0.40 else "🟢 Low")
def get_map_color(s): return ('#ff4444','HIGH') if s>0.75 else (('#ffd700','MODERATE') if s>=0.40 else ('#4ade80','LOW'))

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="vr-page-header">📊 Hotspot Prediction Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="vr-page-sub">XGBoost + SHAP explainability — predict and explain wildlife collision risk across every road segment.</div>', unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(f'<div class="mc"><div class="mc-val">{len(df)}</div><div class="mc-lbl">Total Segments</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="mc"><div class="mc-val" style="color:#f87171">{int((df["risk_probability"]>0.75).sum())}</div><div class="mc-lbl">High Risk</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="mc"><div class="mc-val">{int(df["incident_count"].sum())}</div><div class="mc-lbl">Total Incidents</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="mc"><div class="mc-val" style="color:#4ade80">{len(features)}</div><div class="mc-lbl">Features</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Interactive Map ───────────────────────────────────────────────────────────
st.markdown('<div class="sh">Interactive Hotspot Map</div>', unsafe_allow_html=True)
m = folium.Map(location=[10.335,76.938], zoom_start=12, tiles='CartoDB dark_matter')
df_map = df.groupby('transect')['risk_probability'].max().reset_index()
for _,row in df_map.iterrows():
    name = row['transect']; risk = row['risk_probability']
    coords = transect_coords.get(name,(10.335,76.940))
    color,risk_text = get_map_color(risk)
    incidents = int(df[df['transect']==name]['incident_count'].sum())
    folium.CircleMarker(
        location=coords, radius=12+risk*20,
        color=color, fill=True, fill_color=color, fill_opacity=0.7,
        popup=f"<b>{name}</b><br>{risk_text} — {risk:.0%}<br>{incidents} incidents",
        tooltip=f"{name} — {risk:.0%}"
    ).add_to(m)
components.html(m.get_root().render(), height=480, scrolling=False)

st.markdown("---")

# ── Inspect a Segment ─────────────────────────────────────────────────────────
df_sorted = df.sort_values('risk_probability',ascending=False).copy()
df_sorted['risk_pct'] = (df_sorted['risk_probability']*100).round(1)

st.markdown('<div class="sh">Inspect a Segment</div>', unsafe_allow_html=True)
sc1,sc2 = st.columns(2)
with sc1: selected = st.selectbox("Road segment:", df_sorted['transect'].unique())
with sc2: selected_season = st.selectbox("Season:", ['monsoon','summer'])

row = df[(df['transect']==selected) & (df['season']==selected_season)]
if len(row)>0:
    idx = row.index[0]; score = row['risk_probability'].values[0]; incidents = row['incident_count'].values[0]
    local_shap = shap_vals.iloc[idx]
    shap_df = pd.DataFrame({'feature':[feature_labels[f] for f in features],'shap_value':local_shap.values})
    shap_df_filtered = shap_df[shap_df['shap_value'].abs()>0.001].sort_values('shap_value')
    top_risk = shap_df[shap_df['shap_value']>0].sort_values('shap_value',ascending=False)

    if score>0.75: st.error(f"Risk: {score:.0%} — HIGH")
    elif score>=0.40: st.warning(f"Risk: {score:.0%} — MODERATE")
    else: st.success(f"Risk: {score:.0%} — LOW")

    wc,bc = st.columns(2)
    with wc:
        st.markdown("**SHAP Waterfall**")
        base=0.5; wf=shap_df[shap_df['shap_value'].abs()>0.001].sort_values('shap_value')
        cum=base; wf_f,wf_s,wf_v,wf_c=[],[],[],[]
        for _,wr in wf.iterrows():
            wf_f.append(wr['feature']); wf_s.append(cum); wf_v.append(wr['shap_value'])
            wf_c.append('#f87171' if wr['shap_value']>0 else '#60a5fa'); cum+=wr['shap_value']
        fig_wf=go.Figure(go.Bar(x=wf_v,y=wf_f,base=wf_s,orientation='h',marker_color=wf_c,
                                text=[f"{v:+.3f}" for v in wf_v],textposition='outside'))
        fig_wf.add_vline(x=0.5,line_dash="dash",line_color="#4a5568")
        fig_wf.add_vline(x=score,line_dash="dot",line_color="#fbbf24",
                         annotation_text=f"Final {score:.0%}",annotation_font_size=10)
        fig_wf.update_layout(height=max(280,len(wf_f)*50),xaxis=dict(range=[0,1.1],gridcolor='#1a2e1e'),
                             paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='#e2e8f0'),margin=dict(l=10,r=70,t=20,b=30))
        st.plotly_chart(fig_wf, use_container_width=True)

    with bc:
        st.markdown("**SHAP Contributions**")
        colors=['#f87171' if v>0 else '#60a5fa' for v in shap_df_filtered['shap_value']]
        fig3=go.Figure(go.Bar(x=shap_df_filtered['shap_value'],y=shap_df_filtered['feature'],
                              orientation='h',marker_color=colors,
                              text=shap_df_filtered['shap_value'].apply(lambda v:f'{v:+.3f}'),textposition='outside'))
        fig3.update_layout(height=max(260,len(shap_df_filtered)*45),xaxis=dict(range=[-1,1],gridcolor='#1a2e1e'),
                           paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='#e2e8f0'),margin=dict(l=10,r=50,t=10,b=30))
        st.plotly_chart(fig3, use_container_width=True)

    # Risk explanation
    st.markdown("---")
    st.markdown(f'<div class="sh">Segment Risk Analysis — {selected}</div>', unsafe_allow_html=True)
    top_feats = top_risk['feature'].tolist()[:3]
    for i,feat in enumerate(top_feats,1):
        if feat in feature_explanations:
            st.markdown(f"**{i}. {feat}** — {feature_explanations[feat]}")

    if selected in emerging_segments:
        st.warning(f"🚨 **Emerging Hotspot:** {selected} has few historical incidents but high predicted future risk. Early intervention recommended.")
else:
    st.warning("No data for this combination.")

st.markdown("---")

# ── Risk bar chart ────────────────────────────────────────────────────────────
st.markdown('<div class="sh">Risk Probability by Segment</div>', unsafe_allow_html=True)
fig=px.bar(df_sorted,x='risk_pct',y='transect',color='risk_pct',orientation='h',
           color_continuous_scale=['#4ade80','#fbbf24','#fb923c','#f87171'])
fig.update_layout(height=500,coloraxis_showscale=False,paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#e2e8f0'),
                  xaxis=dict(gridcolor='#1a2e1e',range=[0,100]),yaxis=dict(gridcolor='#1a2e1e'))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Global SHAP ──────────────────────────────────────────────────────────────
st.markdown('<div class="sh">Global Feature Importance (SHAP)</div>', unsafe_allow_html=True)
si=shap_imp.copy(); si['feature']=si['feature'].map(feature_labels); si=si.sort_values('importance',ascending=True)
fig2=px.bar(si,x='importance',y='feature',orientation='h',color='importance',
            color_continuous_scale=['#1e40af','#60a5fa'])
fig2.update_layout(height=360,coloraxis_showscale=False,paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#e2e8f0'),
                   xaxis=dict(gridcolor='#1a2e1e'),yaxis=dict(gridcolor='#1a2e1e'))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Monsoon vs Summer ─────────────────────────────────────────────────────────
st.markdown('<div class="sh">Monsoon vs Summer Comparison</div>', unsafe_allow_html=True)
sdf=df.groupby(['transect','season'])['risk_probability'].max().reset_index()
sdf['risk_pct']=(sdf['risk_probability']*100).round(1)
fig4=px.bar(sdf,x='transect',y='risk_pct',color='season',barmode='group',
            color_discrete_map={'monsoon':'#60a5fa','summer':'#fb923c'})
fig4.update_layout(height=400,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                   font=dict(color='#e2e8f0'),xaxis=dict(gridcolor='#1a2e1e',tickangle=-45),
                   yaxis=dict(gridcolor='#1a2e1e',range=[0,100]),legend=dict(bgcolor='rgba(0,0,0,0)'))
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Species at Risk ───────────────────────────────────────────────────────────
st.markdown('<div class="sh">Species at Risk</div>', unsafe_allow_html=True)
present=roadkill[roadkill['occurrenceStatus']=='present']
if 'taxonRemarks' in present.columns:
    sc=present.groupby('taxonRemarks')['individualCount'].sum().reset_index()
    sc.columns=['Animal Group','Total']
    sc=sc.sort_values('Total',ascending=False).head(10)
    fig5=px.bar(sc,x='Total',y='Animal Group',orientation='h',color='Total',
                color_continuous_scale=['#1e40af','#f87171'])
    fig5.update_layout(height=340,coloraxis_showscale=False,paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#e2e8f0'),
                       xaxis=dict(gridcolor='#1a2e1e'),yaxis=dict(gridcolor='#1a2e1e'))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── Emerging Hotspots ─────────────────────────────────────────────────────────
st.markdown('<div class="sh">🚨 Emerging Hotspots</div>', unsafe_allow_html=True)
st.markdown('<div class="risk-note">These segments have <b>few past incidents</b> but the model predicts <b>high future risk</b>. Act before the numbers rise.</div>', unsafe_allow_html=True)

emerging=df[(df['risk_probability']>=0.4)&(df['incident_count']<=df['incident_count'].quantile(0.6))].sort_values('risk_probability',ascending=False)
if len(emerging)>0:
    for _,erow in emerging.iterrows():
        risk_pct = erow['risk_probability']*100
        if risk_pct>=75: st.error(f"🚨 **{erow['transect']}** ({erow['season']}) — {risk_pct:.1f}% risk | {int(erow['incident_count'])} past incidents")
        else: st.warning(f"⚠️ **{erow['transect']}** ({erow['season']}) — {risk_pct:.1f}% risk | {int(erow['incident_count'])} past incidents")
else:
    st.info("No emerging hotspots detected.")
    #final
    
