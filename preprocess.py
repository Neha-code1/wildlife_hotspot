import pandas as pd
import numpy as np

def load_and_process():
    # Load all 4 files
    habitat = pd.read_csv('data/01_habitat_length.csv')
    events = pd.read_csv('data/02_sampling_events.csv')
    roadkill = pd.read_csv('data/03_roadkill_data_final.csv')
    canopy = pd.read_csv('data/04_canopy_and_habitat.csv')

    # Count incidents per transect per season
    incidents = roadkill[roadkill['occurrenceStatus'] == 'present'].groupby(
        ['transect', 'season'])['individualCount'].sum().reset_index()
    incidents.columns = ['transect', 'season', 'incident_count']

    # Count survey efforts per transect per season
    effort = events.groupby(['transect', 'season']).size().reset_index()
    effort.columns = ['transect', 'season', 'survey_count']

    # Average canopy score per transect
    canopy_avg = canopy.groupby('transect').agg(
        canopy_score=('canopyoverlap', 'mean'),
        vertical_score=('verticaloverlap', 'mean')
    ).reset_index()

    # Forest percentage per transect
    habitat['forest_pct'] = habitat['forest'] / habitat['tlength_m']
    habitat['plantation_pct'] = (
        habitat[['tea', 'coffee', 'eucalyptus']].sum(axis=1) / habitat['tlength_m']
    )

    # Merge everything together
    df = incidents.merge(effort, on=['transect', 'season'], how='left')
    df = df.merge(canopy_avg, on='transect', how='left')
    df = df.merge(habitat[['transect', 'tlength_km', 'forest_pct', 'plantation_pct']],
                  on='transect', how='left')

    # Incident rate per survey
    df['incident_rate'] = df['incident_count'] / df['survey_count']

    # Season as number (monsoon=1, summer=0)
    df['is_monsoon'] = (df['season'] == 'monsoon').astype(int)

    # Manually add traffic and fencing (approximate values for each transect)
    traffic_map = {
        'Balaji Temple': 800, 'Attappadi': 300, 'Valparai': 600,
        'Sholayar': 400, 'Anamalai': 500, 'Udumalpet': 700,
        'Pollachi': 650, 'Topslip': 350, 'Parambikulam': 250,
        'Manamboli': 300, 'Aliyar': 450
    }
    fencing_map = {
        'Balaji Temple': 0, 'Attappadi': 0, 'Valparai': 1,
        'Sholayar': 0, 'Anamalai': 1, 'Udumalpet': 0,
        'Pollachi': 0, 'Topslip': 0, 'Parambikulam': 1,
        'Manamboli': 0, 'Aliyar': 0
    }
    df['traffic_volume'] = df['transect'].map(traffic_map).fillna(400)
    df['fencing_present'] = df['transect'].map(fencing_map).fillna(0)

    # Risk label: high if incident_rate above median
    median_rate = df['incident_rate'].median()
    df['risk_label'] = (df['incident_rate'] > median_rate).astype(int)

    # Fill any missing values
    df = df.fillna(0)

    print("Dataset shape:", df.shape)
    print("\nFeature columns:", df.columns.tolist())
    print("\nSample data:")
    print(df.head())

    return df

if __name__ == '__main__':
    df = load_and_process()
    df.to_csv('data/processed_features.csv', index=False)
    print("\nSaved to data/processed_features.csv")
