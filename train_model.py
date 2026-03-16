import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import shap
import pickle

def train():
    df = pd.read_csv('data/processed_features.csv')

    features = ['canopy_score', 'vertical_score', 'forest_pct',
                 'plantation_pct', 'tlength_km', 'is_monsoon',
                 'traffic_volume', 'fencing_present', 'survey_count']

    X = df[features]
    y = df['risk_label']

    print("Training data shape:", X.shape)
    print("Risk label distribution:\n", y.value_counts())

    model = XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X, y)

    df['risk_probability'] = model.predict_proba(X)[:, 1]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    shap_importance = pd.DataFrame({
        'feature': features,
        'importance': np.abs(shap_values).mean(axis=0)
    }).sort_values('importance', ascending=False)

    print("\nGlobal Feature Importance (SHAP):")
    print(shap_importance)

    # Fix: use lower threshold to find emerging hotspots
    low_threshold = df['incident_count'].quantile(0.6)
    emerging = df[
        (df['risk_probability'] >= 0.4) &
        (df['incident_count'] <= low_threshold)
    ][['transect', 'season', 'incident_count', 'risk_probability']].sort_values(
        'risk_probability', ascending=False
    )

    print("\nEmerging Hotspots:")
    print(emerging.head(5))

    # Save
    with open('data/model.pkl', 'wb') as f:
        pickle.dump(model, f)

    df.to_csv('data/predictions.csv', index=False)

    shap_df = pd.DataFrame(shap_values, columns=features)
    shap_df.to_csv('data/shap_values.csv', index=False)
    shap_importance.to_csv('data/shap_importance.csv', index=False)

    print("\nAll files saved successfully.")

if __name__ == '__main__':
    train()



