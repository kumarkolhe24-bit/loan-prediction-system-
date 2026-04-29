"""
PHASE 1: DATA UNDERSTANDING & VALIDATION
"""
import pandas as pd
import numpy as np
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("PHASE 1: DATA UNDERSTANDING & VALIDATION")
print("="*60)

# Load dataset
df = pd.read_csv('loan_approval_dataset.csv')

# Strip column names
df.columns = df.columns.str.strip()

print("\n✓ Dataset loaded successfully")
print(f"Shape: {df.shape}")

# Print column names
print("\n📋 Column Names:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Verify structure
print("\n📊 Data Types:")
print(df.dtypes)

# Check missing values
print("\n🔍 Missing Values:")
missing = df.isnull().sum()
if missing.sum() == 0:
    print("  ✓ No missing values found")
else:
    print(missing[missing > 0])

# Target distribution
print("\n🎯 Target Distribution (loan_status):")
if 'loan_status' in df.columns:
    print(df['loan_status'].value_counts())
    # Count approved (handle both with and without leading space)
    approved_count = df['loan_status'].str.strip().str.lower().eq('approved').sum()
    print(f"\nApproval Rate: {approved_count / len(df) * 100:.2f}%")
else:
    print("  ❌ ERROR: loan_status column not found!")
    exit(1)

# Basic statistics
print("\n📈 Basic Statistics:")
print(df.describe())

# Check for duplicates
print(f"\n🔄 Duplicate rows: {df.duplicated().sum()}")

print("\n" + "="*60)
print("✅ PHASE 1 COMPLETED SUCCESSFULLY")
print("="*60)
