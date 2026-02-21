import pandas as pd
import json
import numpy as np

df = pd.read_excel(
    'datasets/IHFC_2024_GHFDB.xlsx',
    header=5,          # row index 5 (row 6 in Excel) is the field name row
    usecols=['lat_NS', 'long_EW', 'qc', 'q']
)

# Use corrected heat flow (qc) where available, fall back to q
df['heat_flow'] = df['qc'].combine_first(df['q'])

# Drop rows with missing coords or non-positive heat flow
df = df.dropna(subset=['lat_NS', 'long_EW', 'heat_flow'])
df = df[df['heat_flow'] > 0]

# Normalize to [0, 1] using 99.5th percentile cap to handle outliers
cap = df['heat_flow'].quantile(0.995)
df['score'] = (df['heat_flow'].clip(upper=cap) / cap).round(4)

# Build output
records = [
    {"coordinates": [round(row['long_EW'], 4), round(row['lat_NS'], 4)], "score": row['score']}
    for _, row in df.iterrows()
]

with open('public/geothermal_data.json', 'w') as f:
    json.dump(records, f, separators=(',', ':'))

print(f"Exported {len(records)} records")
