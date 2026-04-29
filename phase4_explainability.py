"""
PHASE 4: EXPLAINABILITY (SHAP)
"""
import pandas as pd
import numpy as np
import pickle
import shap

print("="*60)
print("PHASE 4: EXPLAINABILITY (SHAP)")
print("="*60)

# Load model and data
with open('model/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('model/feature_order.pkl', 'rb') as f:
    feature_order = pickle.load(f)

df = pd.read_csv('data/scaled_data.csv')
X = df.drop('loan_status', axis=1)

print(f"\n✓ Model loaded")
print(f"✓ Features: {list(X.columns)}")

# Initialize SHAP explainer
print("\n🧠 Initializing SHAP TreeExplainer...")
try:
    explainer = shap.TreeExplainer(model)
    print("  ✓ SHAP explainer initialized successfully")
    
    # Calculate SHAP values for a sample
    print("\n📊 Calculating SHAP values for sample predictions...")
    sample_size = min(100, len(X))
    X_sample = X.iloc[:sample_size]
    
    shap_values = explainer.shap_values(X_sample)
    
    print(f"  ✓ SHAP values calculated for {sample_size} samples")
    print(f"  ✓ SHAP values shape: {np.array(shap_values).shape}")
    
    # Save explainer
    with open('model/shap_explainer.pkl', 'wb') as f:
        pickle.dump(explainer, f)
    print("\n💾 Saved: model/shap_explainer.pkl")
    
    # Example: Show SHAP values for first prediction
    print("\n📋 Example SHAP values for first sample:")
    if isinstance(shap_values, list):
        # For binary classification, use class 1 (Rejected)
        sample_shap = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
    else:
        sample_shap = shap_values[0]
    
    for feature, value in zip(feature_order, sample_shap):
        print(f"  {feature}: {value:.4f}")
    
    print("\n✅ SHAP explainability configured successfully")
    
except Exception as e:
    print(f"\n❌ SHAP initialization failed: {e}")
    print("⚠️  Fallback: Will use feature importance instead")
    
    # Fallback: Feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        print("\n📊 Feature Importances (Fallback):")
        for feature, importance in zip(feature_order, importances):
            print(f"  {feature}: {importance:.4f}")
        
        # Save feature importances
        with open('model/feature_importances.pkl', 'wb') as f:
            pickle.dump(dict(zip(feature_order, importances)), f)
        print("\n💾 Saved: model/feature_importances.pkl")

print("\n" + "="*60)
print("✅ PHASE 4 COMPLETED")
print("="*60)
