# 🐾 Wildlife Roadkill Hotspot Predictor

**Blueprints 2026 — DSC SVCE**

## 🚀 Live Demo
👉 https://wildlifehotspot-kk6e8pccqn3mh9szwwnfdm.streamlit.app

## 👥 Team Members
- S Neha
- Swathi E
- Priyadarshan M
- Pradyumna Kouiyalam Sriram
- Surya 
- Zeba H

## 🌍 Overview
Highways cutting through forest reserves cause thousands of animal-vehicle collisions every year. This system uses XGBoost and SHAP to forecast where future wildlife-vehicle collisions will occur before they happen.

## ⚙️ Installation
pip install -r requirements.txt
python3 preprocess.py
python3 train_model.py
streamlit run app.py

## 🤖 Model
- Algorithm: XGBoost Classifier
- Explainability: SHAP
- Dataset: NCF India 2473 roadkill incidents 2011-2013
- Features: 9 environmental and infrastructural features

## 🚨 Emerging Hotspots
- Nallamudi: 71.8% risk
- Neerar Dam: 43.9% risk
- Chinnakallar: 40.9% risk

## 📚 Data Source
Jeganathan et al. 2018 — Nature Conservation Foundation India
