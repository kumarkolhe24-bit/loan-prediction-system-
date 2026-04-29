"""
PHASE 3: MODEL TRAINING & COMPARISON
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

print("="*60)
print("PHASE 3: MODEL TRAINING & COMPARISON")
print("="*60)

# Load scaled data
df = pd.read_csv('data/scaled_data.csv')
print(f"\n✓ Loaded scaled data: {df.shape}")

# Split features and target
X = df.drop('loan_status', axis=1)
y = df['loan_status']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n✂️  Train-Test Split:")
print(f"  Training set: {X_train.shape}")
print(f"  Test set: {X_test.shape}")

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
}

results = {}

print("\n" + "="*60)
print("🤖 TRAINING MODELS")
print("="*60)

for name, model in models.items():
    print(f"\n📊 Training {name}...")
    
    # Train
    model.fit(X_train, y_train)
    
    # Predict
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Evaluate
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    results[name] = {
        'model': model,
        'train_accuracy': train_acc,
        'test_accuracy': test_acc,
        'predictions': y_pred_test
    }
    
    print(f"  ✓ Training Accuracy: {train_acc*100:.2f}%")
    print(f"  ✓ Test Accuracy: {test_acc*100:.2f}%")
    
    # Check overfitting
    if train_acc - test_acc > 0.1:
        print(f"  ⚠️  WARNING: Possible overfitting detected!")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_test)
    print(f"\n  Confusion Matrix:")
    print(f"    {cm}")
    
    # Classification Report
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred_test, target_names=['Approved', 'Rejected']))

# Model Comparison
print("\n" + "="*60)
print("📊 MODEL COMPARISON")
print("="*60)

for name, result in results.items():
    print(f"  {name}: {result['test_accuracy']*100:.2f}%")

# Select best model
best_model_name = max(results, key=lambda x: results[x]['test_accuracy'])
best_model = results[best_model_name]['model']
best_accuracy = results[best_model_name]['test_accuracy']

print(f"\n🏆 Best Model: {best_model_name}")
print(f"   Accuracy: {best_accuracy*100:.2f}%")

# Failure check
if best_accuracy < 0.70:
    print(f"\n❌ WARNING: Best accuracy ({best_accuracy*100:.2f}%) is below 70%!")
else:
    print(f"\n✅ Accuracy check passed ({best_accuracy*100:.2f}% >= 70%)")

# Save best model
with open('model/model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
print(f"\n💾 Saved best model: model/model.pkl")

# Save all models for comparison
with open('model/all_models.pkl', 'wb') as f:
    pickle.dump({name: result['model'] for name, result in results.items()}, f)
print(f"💾 Saved all models: model/all_models.pkl")

# Save model metadata
metadata = {
    'best_model': best_model_name,
    'best_accuracy': best_accuracy,
    'all_accuracies': {name: result['test_accuracy'] for name, result in results.items()}
}
with open('model/model_metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)
print(f"💾 Saved metadata: model/model_metadata.pkl")

print("\n" + "="*60)
print("✅ PHASE 3 COMPLETED SUCCESSFULLY")
print("="*60)
