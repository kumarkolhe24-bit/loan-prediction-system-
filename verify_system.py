"""
SYSTEM VERIFICATION SCRIPT
Simple verification without emojis for Windows compatibility
"""
import os
import pickle
import pandas as pd
from loan_intelligence import LoanIntelligence

print("="*60)
print("SYSTEM VERIFICATION")
print("="*60)

errors = []
warnings = []

# Check 1: Dataset exists
print("\n[1/10] Checking dataset...")
if os.path.exists('loan_approval_dataset.csv'):
    df = pd.read_csv('loan_approval_dataset.csv')
    if df.shape == (4269, 13):
        print("  OK: Dataset found (4269 rows, 13 columns)")
    else:
        errors.append(f"Dataset shape mismatch: {df.shape}")
else:
    errors.append("Dataset not found")

# Check 2: Model files exist
print("\n[2/10] Checking model files...")
required_files = [
    'model/model.pkl',
    'model/scaler.pkl',
    'model/feature_order.pkl',
    'model/label_encoders.pkl'
]
for file in required_files:
    if os.path.exists(file):
        print(f"  OK: {file}")
    else:
        errors.append(f"Missing: {file}")

# Check 3: Feature order
print("\n[3/10] Checking feature order...")
with open('model/feature_order.pkl', 'rb') as f:
    features = pickle.load(f)
expected = ['no_of_dependents', 'education', 'self_employed', 'income_annum', 
            'loan_amount', 'loan_term', 'cibil_score', 'total_assets']
if features == expected:
    print(f"  OK: Feature order correct ({len(features)} features)")
else:
    errors.append(f"Feature order mismatch: {features}")

# Check 4: loan_status not in features
print("\n[4/10] Checking data leakage...")
if 'loan_status' not in features:
    print("  OK: No data leakage (loan_status not in features)")
else:
    errors.append("DATA LEAKAGE: loan_status found in features!")

# Check 5: Load system
print("\n[5/10] Loading intelligence system...")
try:
    system = LoanIntelligence()
    print("  OK: System loaded successfully")
except Exception as e:
    errors.append(f"Failed to load system: {e}")

# Check 6: Test prediction
print("\n[6/10] Testing prediction...")
try:
    test_input = {
        'no_of_dependents': 2,
        'education': ' Graduate',
        'self_employed': ' No',
        'income_annum': 5000000,
        'loan_amount': 10000000,
        'loan_term': 10,
        'cibil_score': 750,
        'residential_assets_value': 5000000,
        'commercial_assets_value': 3000000,
        'luxury_assets_value': 2000000,
        'bank_asset_value': 1000000
    }
    prediction = system.predict(test_input)
    if prediction in [0, 1]:
        print(f"  OK: Prediction works (result: {prediction})")
    else:
        errors.append(f"Invalid prediction: {prediction}")
except Exception as e:
    errors.append(f"Prediction failed: {e}")

# Check 7: Test risk scoring
print("\n[7/10] Testing risk scoring...")
try:
    risk_score = system.get_risk_score(test_input)
    if 0 <= risk_score <= 100:
        print(f"  OK: Risk scoring works (score: {risk_score})")
    else:
        errors.append(f"Invalid risk score: {risk_score}")
except Exception as e:
    errors.append(f"Risk scoring failed: {e}")

# Check 8: Test suggestions
print("\n[8/10] Testing suggestions...")
try:
    suggestions = system.get_suggestions(test_input, prediction)
    if isinstance(suggestions, list) and len(suggestions) > 0:
        print(f"  OK: Suggestions work ({len(suggestions)} suggestions)")
    else:
        warnings.append("No suggestions generated")
except Exception as e:
    errors.append(f"Suggestions failed: {e}")

# Check 9: Test anomaly detection
print("\n[9/10] Testing anomaly detection...")
try:
    anomalies = system.detect_anomalies(test_input)
    print(f"  OK: Anomaly detection works ({len(anomalies)} anomalies)")
except Exception as e:
    errors.append(f"Anomaly detection failed: {e}")

# Check 10: Test what-if analysis
print("\n[10/10] Testing what-if analysis...")
try:
    scenarios = {'cibil_score': [700, 750]}
    results = system.what_if_analysis(test_input, scenarios)
    if 'cibil_score' in results:
        print(f"  OK: What-if analysis works")
    else:
        errors.append("What-if analysis returned unexpected results")
except Exception as e:
    errors.append(f"What-if analysis failed: {e}")

# Summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)

if len(errors) == 0:
    print("\nSTATUS: ALL CHECKS PASSED")
    print(f"  - 10/10 checks successful")
    if len(warnings) > 0:
        print(f"  - {len(warnings)} warnings")
        for w in warnings:
            print(f"    * {w}")
else:
    print(f"\nSTATUS: {len(errors)} ERRORS FOUND")
    for e in errors:
        print(f"  X {e}")

if len(warnings) > 0 and len(errors) == 0:
    print("\nWarnings can be ignored - system is functional")

print("\n" + "="*60)

# Exit code
exit(0 if len(errors) == 0 else 1)
