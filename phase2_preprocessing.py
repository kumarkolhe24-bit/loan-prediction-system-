"""
PHASE 2: PREPROCESSING PIPELINE
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os

print("="*60)
print("PHASE 2: PREPROCESSING PIPELINE")
print("="*60)

# Create directories
os.makedirs('data', exist_ok=True)
os.makedirs('model', exist_ok=True)

# Load dataset
df = pd.read_csv('loan_approval_dataset.csv')
df.columns = df.columns.str.strip()

print(f"\n✓ Original shape: {df.shape}")

# Remove loan_id
print("\n🗑️  Removing loan_id...")
df = df.drop('loan_id', axis=1)

# Feature Engineering: Create total_assets
print("\n🔧 Feature Engineering: Creating total_assets...")
df['total_assets'] = (
    df['residential_assets_value'] + 
    df['commercial_assets_value'] + 
    df['luxury_assets_value'] + 
    df['bank_asset_value']
)

# Drop original asset columns
print("🗑️  Dropping original asset columns...")
df = df.drop([
    'residential_assets_value',
    'commercial_assets_value', 
    'luxury_assets_value',
    'bank_asset_value'
], axis=1)

print(f"\n✓ Shape after feature engineering: {df.shape}")
print(f"\n📋 Columns after engineering:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Save cleaned data before encoding
df.to_csv('data/cleaned_data.csv', index=False)
print("\n💾 Saved: data/cleaned_data.csv")

# Encode categorical variables
print("\n🔤 Encoding categorical variables...")

# Education
le_education = LabelEncoder()
df['education'] = le_education.fit_transform(df['education'])
print(f"  ✓ education: {list(le_education.classes_)}")

# Self_employed
le_self_employed = LabelEncoder()
df['self_employed'] = le_self_employed.fit_transform(df['self_employed'])
print(f"  ✓ self_employed: {list(le_self_employed.classes_)}")

# Loan_status (target)
le_loan_status = LabelEncoder()
df['loan_status'] = le_loan_status.fit_transform(df['loan_status'])
print(f"  ✓ loan_status: {list(le_loan_status.classes_)}")

# Save encoders
with open('model/label_encoders.pkl', 'wb') as f:
    pickle.dump({
        'education': le_education,
        'self_employed': le_self_employed,
        'loan_status': le_loan_status
    }, f)
print("\n💾 Saved: model/label_encoders.pkl")

# Split features and target
print("\n✂️  Splitting features and target...")
X = df.drop('loan_status', axis=1)
y = df['loan_status']

print(f"  ✓ X shape: {X.shape}")
print(f"  ✓ y shape: {y.shape}")

# CRITICAL CHECK: Ensure loan_status not in X
if 'loan_status' in X.columns:
    print("  ❌ ERROR: loan_status found in features!")
    exit(1)
else:
    print("  ✓ loan_status NOT in features (correct)")

# Feature order (CRITICAL for consistency)
feature_order = list(X.columns)
print(f"\n📋 Feature Order (CRITICAL):")
for i, col in enumerate(feature_order, 1):
    print(f"  {i}. {col}")

# Save feature order
with open('model/feature_order.pkl', 'wb') as f:
    pickle.dump(feature_order, f)
print("\n💾 Saved: model/feature_order.pkl")

# Scale features
print("\n⚖️  Scaling features using StandardScaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save scaler
with open('model/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("💾 Saved: model/scaler.pkl")

# Save scaled data
scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
scaled_df['loan_status'] = y.values
scaled_df.to_csv('data/scaled_data.csv', index=False)
print("💾 Saved: data/scaled_data.csv")

print("\n" + "="*60)
print("✅ PHASE 2 COMPLETED SUCCESSFULLY")
print("="*60)
print(f"\nFiles created:")
print(f"  - data/cleaned_data.csv")
print(f"  - data/scaled_data.csv")
print(f"  - model/scaler.pkl")
print(f"  - model/label_encoders.pkl")
print(f"  - model/feature_order.pkl")
