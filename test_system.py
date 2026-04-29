"""
COMPREHENSIVE SYSTEM TESTING
Tests all phases and components
"""
import sys
import os
from loan_intelligence import LoanIntelligence

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_case_1():
    """Test Case 1: High income + high CIBIL → Approved"""
    print("\n" + "="*60)
    print("TEST CASE 1: High Income + High CIBIL → Expected: APPROVED")
    print("="*60)
    
    system = LoanIntelligence()
    
    input_data = {
        'no_of_dependents': 2,
        'education': ' Graduate',
        'self_employed': ' No',
        'income_annum': 9600000,
        'loan_amount': 29900000,
        'loan_term': 20,
        'cibil_score': 778,
        'residential_assets_value': 2400000,
        'commercial_assets_value': 17600000,
        'luxury_assets_value': 22700000,
        'bank_asset_value': 8000000
    }
    
    # Predict
    prediction = system.predict(input_data)
    risk_score = system.get_risk_score(input_data)
    suggestions = system.get_suggestions(input_data, prediction)
    anomalies = system.detect_anomalies(input_data)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"  Prediction: {'✅ APPROVED' if prediction == 0 else '❌ REJECTED'}")
    print(f"  Risk Score: {risk_score}/100")
    print(f"  Risk Level: {system.interpret_risk(risk_score)}")
    
    if anomalies:
        print(f"\n⚠️  Anomalies:")
        for anomaly in anomalies:
            print(f"    {anomaly}")
    
    print(f"\n💡 Suggestions:")
    for suggestion in suggestions:
        print(f"    {suggestion}")
    
    # Verify
    assert prediction == 0, "Expected APPROVED"
    assert risk_score < 50, f"Expected low risk, got {risk_score}"
    print("\n✅ TEST PASSED")
    
    return True

def test_case_2():
    """Test Case 2: Low income + low CIBIL → Rejected"""
    print("\n" + "="*60)
    print("TEST CASE 2: Low Income + Low CIBIL → Expected: REJECTED")
    print("="*60)
    
    system = LoanIntelligence()
    
    input_data = {
        'no_of_dependents': 3,
        'education': ' Not Graduate',
        'self_employed': ' Yes',
        'income_annum': 200000,
        'loan_amount': 500000,
        'loan_term': 5,
        'cibil_score': 550,
        'residential_assets_value': 100000,
        'commercial_assets_value': 0,
        'luxury_assets_value': 0,
        'bank_asset_value': 50000
    }
    
    # Predict
    prediction = system.predict(input_data)
    risk_score = system.get_risk_score(input_data)
    suggestions = system.get_suggestions(input_data, prediction)
    anomalies = system.detect_anomalies(input_data)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"  Prediction: {'✅ APPROVED' if prediction == 0 else '❌ REJECTED'}")
    print(f"  Risk Score: {risk_score}/100")
    print(f"  Risk Level: {system.interpret_risk(risk_score)}")
    
    if anomalies:
        print(f"\n⚠️  Anomalies:")
        for anomaly in anomalies:
            print(f"    {anomaly}")
    
    print(f"\n💡 Suggestions:")
    for suggestion in suggestions:
        print(f"    {suggestion}")
    
    # Verify
    assert prediction == 1, "Expected REJECTED"
    assert risk_score > 50, f"Expected high risk, got {risk_score}"
    assert len(suggestions) > 1, "Expected multiple suggestions"
    print("\n✅ TEST PASSED")
    
    return True

def test_case_3():
    """Test Case 3: Extreme income → Anomaly"""
    print("\n" + "="*60)
    print("TEST CASE 3: Extreme Income → Expected: ANOMALY WARNING")
    print("="*60)
    
    system = LoanIntelligence()
    
    input_data = {
        'no_of_dependents': 2,
        'education': ' Graduate',
        'self_employed': ' No',
        'income_annum': 150000000,  # 15 crore - unrealistic
        'loan_amount': 10000000,
        'loan_term': 10,
        'cibil_score': 750,
        'residential_assets_value': 5000000,
        'commercial_assets_value': 3000000,
        'luxury_assets_value': 2000000,
        'bank_asset_value': 1000000
    }
    
    # Detect anomalies
    anomalies = system.detect_anomalies(input_data)
    
    # Display results
    print(f"\n⚠️  Anomalies Detected:")
    for anomaly in anomalies:
        print(f"    {anomaly}")
    
    # Verify
    assert len(anomalies) > 0, "Expected anomaly detection"
    assert any('income' in a.lower() for a in anomalies), "Expected income anomaly"
    print("\n✅ TEST PASSED")
    
    return True

def test_case_4():
    """Test Case 4: What-If Analysis"""
    print("\n" + "="*60)
    print("TEST CASE 4: What-If Analysis")
    print("="*60)
    
    system = LoanIntelligence()
    
    base_input = {
        'no_of_dependents': 2,
        'education': ' Graduate',
        'self_employed': ' No',
        'income_annum': 5000000,
        'loan_amount': 10000000,
        'loan_term': 10,
        'cibil_score': 650,  # Borderline
        'residential_assets_value': 5000000,
        'commercial_assets_value': 3000000,
        'luxury_assets_value': 2000000,
        'bank_asset_value': 1000000
    }
    
    scenarios = {
        'cibil_score': [650, 700, 750],
        'income_annum': [4000000, 5000000, 6000000]
    }
    
    print("\n🔮 Running What-If Analysis...")
    results = system.what_if_analysis(base_input, scenarios)
    
    # Display results
    for param, param_results in results.items():
        print(f"\n📊 Scenario: {param}")
        for result in param_results:
            print(f"    {param}={result['value']:,} → "
                  f"{result['prediction']} (Risk: {result['risk_score']})")
    
    # Verify
    assert 'cibil_score' in results, "Expected CIBIL scenarios"
    assert 'income_annum' in results, "Expected income scenarios"
    assert len(results['cibil_score']) == 3, "Expected 3 CIBIL scenarios"
    print("\n✅ TEST PASSED")
    
    return True

def test_case_5():
    """Test Case 5: Feature Consistency"""
    print("\n" + "="*60)
    print("TEST CASE 5: Feature Order Consistency")
    print("="*60)
    
    system = LoanIntelligence()
    
    # Check feature order
    print(f"\n📋 Feature Order:")
    for i, feature in enumerate(system.feature_order, 1):
        print(f"    {i}. {feature}")
    
    # Verify
    expected_features = [
        'no_of_dependents', 'education', 'self_employed', 
        'income_annum', 'loan_amount', 'loan_term', 
        'cibil_score', 'total_assets'
    ]
    
    assert system.feature_order == expected_features, "Feature order mismatch!"
    assert 'loan_status' not in system.feature_order, "loan_status should not be in features!"
    
    print("\n✅ TEST PASSED")
    return True

def test_case_6():
    """Test Case 6: Preprocessing Consistency"""
    print("\n" + "="*60)
    print("TEST CASE 6: Preprocessing Consistency")
    print("="*60)
    
    system = LoanIntelligence()
    
    input_data = {
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
    
    # Preprocess twice
    X1 = system.preprocess_input(input_data)
    X2 = system.preprocess_input(input_data)
    
    # Verify consistency
    import numpy as np
    assert np.allclose(X1, X2), "Preprocessing not consistent!"
    
    print(f"\n✓ Preprocessing is consistent")
    print(f"  Shape: {X1.shape}")
    print(f"  Sample values: {X1[0][:3]}")
    
    print("\n✅ TEST PASSED")
    return True

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE SYSTEM TESTING")
    print("="*60)
    
    tests = [
        ("High Income + High CIBIL", test_case_1),
        ("Low Income + Low CIBIL", test_case_2),
        ("Extreme Income Anomaly", test_case_3),
        ("What-If Analysis", test_case_4),
        ("Feature Consistency", test_case_5),
        ("Preprocessing Consistency", test_case_6)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"  Total Tests: {len(tests)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
