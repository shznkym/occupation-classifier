#!/usr/bin/env python3
"""
Convert e-Stat occupation classification CSV to classifier format
"""
import pandas as pd
import sys

# Read the downloaded e-Stat CSV
print("Reading e-Stat CSV...")
df = pd.read_csv(
    'estat/FEK_download.csv',
    encoding='utf-8-sig',  # Handle BOM
    skiprows=1  # Skip the title row
)

print(f"Loaded {len(df)} rows")
print(f"Columns: {list(df.columns)}")

# Rename columns to match classifier format
df.columns = ['code', 'name', 'description']

# Filter out rows where code is empty, whitespace, or just notes
df = df[df['code'].notna()]
df = df[df['code'].astype(str).str.strip() != '']
df = df[df['code'].astype(str).str.strip() != '　']  # Full-width space

# Clean up the data
df['code'] = df['code'].astype(str).str.strip()
df['name'] = df['name'].astype(str).str.strip()
df['description'] = df['description'].fillna('').astype(str).str.strip()

# Filter out rows that start with '※' (notes)
df = df[~df['name'].str.startswith('※')]

# Combine name and description for better embedding
df['description'] = df.apply(
    lambda row: f"{row['name']}。{row['description']}" if row['description'] else row['name'],
    axis=1
)

print(f"\nAfter cleaning: {len(df)} occupation records")
print(f"\nFirst 5 records:")
print(df.head().to_string(index=False))

# Save to backend/data/occupation.csv
output_path = 'backend/data/occupation.csv'
df.to_csv(output_path, index=False, encoding='utf-8')
print(f"\n✅ Saved to {output_path}")

print(f"\n📊 Statistics:")
print(f"  - Total occupations: {len(df)}")
print(f"  - Code length range: {df['code'].str.len().min()}-{df['code'].str.len().max()} chars")
print(f"  - Average description length: {df['description'].str.len().mean():.0f} chars")
