"""
Test Decision Tree probability outputs
"""
from loan_intelligence import LoanIntelligence
import numpy as np

system = LoanIntelligence()

# Test Case 1: Excellent application
test1 = {
    'no_of_dependents': 2,
    'education': ' Graduate',
    'self_employed': ' No',
    'income_annum': 5000000,
    'loan_amount': 10000000,
    'loan_term': 10,
    'cibil_score': 810,
    'residential_assets_value': 5000000,
    'commercial_assets_value': 3000000,
    'luxury_assets_value': 2000000,
    'bank_asset_value': 1000000
}

# Test Case 2: Moderate application
test2 = {
    'no_of_dependents': 2,
    'education': ' Not Graduate',
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

# Test Case 3: Poor application
test3 = {
    'no_of_dependents': 3,
    'education': ' Not Graduate',
    'self_employed': ' Yes',
    'income_annum': 1000000,
    'loan_amount': 100000,
    'loan_term': 2,
    'cibil_score': 493,
    'residential_assets_value': 500000,
    'commercial_assets_value': 0,
    'luxury_assets_value': 200000,
    'bank_asset_value': 1000000
}

print("="*60)
print("TESTING DECISION TREE PROBABILITIES")
print("="*60)

for i, test in enumerate([test1, test2, test3], 1):
    print(f"\nTest Case {i}:")
    print(f"CIBIL: {test['cibil_score']}, Income: ₹{test['income_annum']:,}, Loan: ₹{test['loan_amount']:,}")
    
    X = system.preprocess_input(test)
    probabilities = system.model.predict_proba(X)[0]
    prediction = system.predict(test)
    risk_score = system.get_risk_score(test)
    confidence = system.get_confidence(test)
    
    print(f"Probabilities: [Approved: {probabilities[0]:.4f}, Rejected: {probabilities[1]:.4f}]")
    print(f"Prediction: {'Approved' if prediction == 0 else 'Rejected'}")
    print(f"Risk Score: {risk_score}/100")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Problem: {'YES - Always 0 or 100!' if risk_score in [0, 100] else 'No'}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("Decision Trees return probabilities based on leaf node purity.")
print("If a leaf is 100% pure (all same class), probability is [1.0, 0.0] or [0.0, 1.0]")
print("This causes risk scores to be only 0 or 100, with no gradation.")
