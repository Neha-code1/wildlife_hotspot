from pathlib import Path
import pickle
import pandas as pd
import streamlit as st

TRANSECT_ORDER = [
    "Attakatti - 1 hpb",
    "Azhiyar",
    "Old Valparai",
    "Puthuthotam",
    "Neerar Dam",
    "Waterfalls",
    "Chinnakallar",
    "Waverly",
    "Balaji Temple",
    "Sholayar",
    "Nallamudi",
]

TRANSECT_COORDS = {
    "Attakatti - 1 hpb": (10.312, 76.952),
    "Azhiyar": (10.348, 76.942),
    "Old Valparai": (10.325, 76.955),
    "Puthuthotam": (10.318, 76.938),
    "Neerar Dam": (10.342, 76.918),
    "Waterfalls": (10.365, 76.928),
    "Chinnakallar": (10.358, 76.935),
    "Waverly": (10.355, 76.945),
    "Balaji Temple": (10.332, 76.962),
    "Sholayar": (10.298, 76.908),
    "Nallamudi": (10.372, 76.972),
}

@st.cache_resource
def load_model():
    with open(Path("data") / "model.pkl", "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_dashboard_data():
    predictions = pd.read_csv("data/predictions.csv")
    shap_values = pd.read_csv("data/shap_values.csv")
    shap_importance = pd.read_csv("data/shap_importance.csv")
    roadkill = pd.read_csv("data/03_roadkill_data_final.csv")
    return predictions, shap_values, shap_importance, roadkill

def route_segments(start: str, end: str):
    i = TRANSECT_ORDER.index(start)
    j = TRANSECT_ORDER.index(end)
    if i <= j:
        return TRANSECT_ORDER[i:j+1]
    return list(reversed(TRANSECT_ORDER[j:i+1]))

def get_risk_band(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.40:
        return "Moderate"
    return "Low"

def get_alert_icon(score: float) -> str:
    if score >= 0.75:
        return "🔴"
    if score >= 0.40:
        return "🟠"
    return "🟢"