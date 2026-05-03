# 🏦 Loan Decision Intelligence System

A complete end-to-end AI-powered loan approval system with explainability, risk scoring, and intelligent suggestions.

## 🌟 Features

-  **Loan Approval Prediction** - 98.48% accuracy using Decision Tree
-  **Risk Scoring** - 0-100 risk assessment
-  **Explainability** - SHAP-based decision explanations
-  **Smart Suggestions** - Actionable improvement recommendations
-  **What-If Analysis** - Simulate different scenarios
-  **Anomaly Detection** - Data quality validation
-  **REST API** - FastAPI backend
-  **Interactive UI** - Streamlit frontend
-  **History Tracking** - All predictions logged

## Project Structure

```
loan-project/
│
├── data/
│   ├── cleaned_data.csv          # Preprocessed data
│   └── scaled_data.csv            # Scaled features
│
├── model/
│   ├── model.pkl                  # Trained model (Decision Tree)
│   ├── scaler.pkl                 # StandardScaler
│   ├── label_encoders.pkl         # Categorical encoders
│   ├── feature_order.pkl          # Feature order (critical!)
│   ├── shap_explainer.pkl         # SHAP explainer
│   ├── feature_importances.pkl    # Feature importances
│   ├── all_models.pkl             # All trained models
│   └── model_metadata.pkl         # Model performance metrics
│
├── backend/
│   └── api.py                     # FastAPI REST API
│
├── frontend/
│   └── app.py                     # Streamlit UI
│
├── loan_intelligence.py           # Core intelligence system
├── history.csv                    # Prediction logs
│
├── phase1_data_validation.py      # Data validation script
├── phase2_preprocessing.py        # Preprocessing pipeline
├── phase3_model_training.py       # Model training & comparison
├── phase4_explainability.py       # SHAP setup
│
└── README.md                      # This file
```

## Quick Start

### 1. Installation

```bash
# Install required packages
pip install pandas numpy scikit-learn shap fastapi uvicorn streamlit plotly
```

### 2. Run All Phases

```bash
# Phase 1: Data Validation
python phase1_data_validation.py

# Phase 2: Preprocessing
python phase2_preprocessing.py

# Phase 3: Model Training
python phase3_model_training.py

# Phase 4: Explainability Setup
python phase4_explainability.py
```

### 3. Test Core System

```bash
python loan_intelligence.py
```

### 4. Start Backend API

```bash
# Terminal 1: Start API
cd backend
python api.py

# API will be available at:
# - http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### 5. Start Frontend

```bash
# Terminal 2: Start Streamlit
cd frontend
streamlit run app.py

# UI will open at: http://localhost:8501
```

## 📊Model Performance

| Model | Training Accuracy | Test Accuracy |
|-------|------------------|---------------|
| Logistic Regression | 91.45% | 92.51% |
| Decision Tree | 100.00% | **98.48%** ✅ |
| Random Forest | 100.00% | 98.01% |

**Best Model**: Decision Tree (98.48% accuracy)

##  Key Features Explained

### 1. Risk Scoring System

```python
risk_score = probability_of_rejection * 100

# Interpretation:
# 0-50:   Low Risk (Likely Approval)
# 50-80:  Medium Risk (Uncertain)
# 80-100: High Risk (Likely Rejection)
```

### 2. Feature Importance

Most important factors (in order):
1. **CIBIL Score** (81.89%) - Most critical
2. **Loan Term** (8.27%)
3. **Income** (4.33%)
4. **Loan Amount** (4.01%)
5. **Total Assets** (1.00%)

### 3. Suggestion Engine Rules

- CIBIL < 650 → Suggest improvement
- Loan Amount > 50% of Income → Suggest reduction
- Income < ₹300,000 → Suggest increase
- Assets < Loan Amount → Suggest asset improvement

### 4. Anomaly Detection

Flags:
- Income > ₹10 crore
- Loan Amount > ₹10 crore
- CIBIL Score outside 300-900 range
- Negative values
- Unusual loan terms

## 🌐 API Endpoints

### POST /predict

Predict loan approval with full intelligence.

**Request:**
```json
{
  "no_of_dependents": 2,
  "education": " Graduate",
  "self_employed": " No",
  "income_annum": 5000000,
  "loan_amount": 10000000,
  "loan_term": 10,
  "cibil_score": 750,
  "residential_assets_value": 5000000,
  "commercial_assets_value": 3000000,
  "luxury_assets_value": 2000000,
  "bank_asset_value": 1000000
}
```

**Response:**
```json
{
  "prediction": "Approved",
  "prediction_code": 0,
  "risk_score": 15,
  "risk_interpretation": "Low Risk - Likely Approval",
  "shap_values": {
    "cibil_score": -0.42,
    "income_annum": -0.25,
    ...
  },
  "suggestions": [
    "✅ Application looks good! No major concerns."
  ],
  "anomalies": [],
  "timestamp": "2024-04-14T12:00:00"
}
```

### POST /what-if

Perform what-if analysis.

**Request:**
```json
{
  "application": { ... },
  "scenarios": {
    "cibil_score": [650, 700, 750],
    "income_annum": [4000000, 5000000, 6000000]
  }
}
```

##  Frontend Features

### Application Tab
- Input form for all loan details
- Real-time validation
- Instant prediction with visualization
- Risk gauge chart
- Feature impact bar chart
- Actionable suggestions

### What-If Analysis Tab
- Test multiple scenarios
- Interactive charts
- Compare outcomes
- Strategic planning tool

### History Tab
- View all past predictions
- Approval/rejection statistics
- Risk score distribution
- Recent applications table

### Guide Tab
- Complete user documentation
- Tips for approval
- Factor explanations
- Best practices

## 🧪 Testing

### Test Case 1: High Income + High CIBIL → Approved
```python
{
    'income_annum': 9600000,
    'cibil_score': 778,
    'loan_amount': 29900000,
    ...
}
# Expected: Approved, Risk Score: 0-20
```

### Test Case 2: Low Income + Low CIBIL → Rejected
```python
{
    'income_annum': 200000,
    'cibil_score': 550,
    'loan_amount': 500000,
    ...
}
# Expected: Rejected, Risk Score: 80-100
```

### Test Case 3: Extreme Income → Anomaly
```python
{
    'income_annum': 150000000,  # 15 crore
    ...
}
# Expected: Anomaly warning
```

## 📝 Data Logging

All predictions are automatically logged to `history.csv`:

```csv
no_of_dependents,education,self_employed,income_annum,...,prediction,risk_score,timestamp
2, Graduate, No,5000000,...,0,15,2024-04-14T12:00:00
```

##  Critical Rules (DO NOT VIOLATE)

1. ✅ Same preprocessing in training and prediction
2. ✅ Never include `loan_status` in features
3. ✅ Maintain column order consistency (use `feature_order.pkl`)
4. ✅ Always scale input before prediction
5. ✅ Handle errors explicitly
6. ✅ Validate input data
7. ✅ Log all predictions

## 🛠️ Troubleshooting

### Issue: Inconsistent Predictions
**Solution**: Check that you're using the same scaler and feature order

### Issue: API Connection Error
**Solution**: Ensure backend is running on port 8000

### Issue: SHAP Errors
**Solution**: System automatically falls back to feature importance

### Issue: Import Errors
**Solution**: Install all required packages

##  Future Enhancements

- [ ] Add more ML models (XGBoost, LightGBM)
- [ ] Implement A/B testing
- [ ] Add user authentication
- [ ] Deploy to cloud (AWS/Azure/GCP)
- [ ] Add email notifications
- [ ] Implement batch processing
- [ ] Add model retraining pipeline
- [ ] Create mobile app

##  Development

### Adding New Features

1. Update `loan_intelligence.py` with new logic
2. Add API endpoint in `backend/api.py`
3. Update frontend in `frontend/app.py`
4. Test thoroughly
5. Update documentation

### Retraining Model

```bash
# 1. Update dataset
# 2. Run preprocessing
python phase2_preprocessing.py

# 3. Retrain models
python phase3_model_training.py

# 4. Update explainability
python phase4_explainability.py

# 5. Restart services
```

##  License

MIT License - Feel free to use and modify

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

##  Contact

For questions or support, please open an issue.

---

