"""
PHASE 9: BACKEND API (FastAPI)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loan_intelligence import LoanIntelligence

# Initialize FastAPI app
app = FastAPI(
    title="Loan Decision Intelligence API",
    description="AI-powered loan approval prediction with explainability",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Loan Intelligence System
system = LoanIntelligence()

# Pydantic models for request/response
class LoanApplication(BaseModel):
    no_of_dependents: int = Field(..., ge=0, le=10, description="Number of dependents")
    education: str = Field(..., description="Education level: ' Graduate' or ' Not Graduate'")
    self_employed: str = Field(..., description="Self-employed: ' Yes' or ' No'")
    income_annum: int = Field(..., gt=0, description="Annual income in rupees")
    loan_amount: int = Field(..., gt=0, description="Loan amount requested")
    loan_term: int = Field(..., description="Loan term in years")
    cibil_score: int = Field(..., ge=300, le=900, description="CIBIL credit score")
    residential_assets_value: int = Field(..., ge=0, description="Residential assets value")
    commercial_assets_value: int = Field(..., ge=0, description="Commercial assets value")
    luxury_assets_value: int = Field(..., ge=0, description="Luxury assets value")
    bank_asset_value: int = Field(..., ge=0, description="Bank assets value")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }

class PredictionResponse(BaseModel):
    prediction: str
    prediction_code: int
    risk_score: int
    risk_interpretation: str
    shap_values: Dict[str, float]
    suggestions: List[str]
    anomalies: List[str]
    timestamp: str

class WhatIfScenario(BaseModel):
    application: LoanApplication
    scenarios: Dict[str, List[int]]

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Loan Decision Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "what_if": "/what-if",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_loan(application: LoanApplication):
    """
    Predict loan approval with full intelligence
    
    Returns:
        - prediction: Approved/Rejected
        - risk_score: 0-100
        - shap_values: Feature contributions
        - suggestions: Improvement recommendations
        - anomalies: Data quality warnings
    """
    try:
        # Convert to dict
        input_data = application.dict()
        
        # Detect anomalies
        anomalies = system.detect_anomalies(input_data)
        
        # Make prediction
        prediction_code = system.predict(input_data)
        prediction = "Approved" if prediction_code == 0 else "Rejected"
        
        # Get risk score
        risk_score = system.get_risk_score(input_data)
        risk_interpretation = system.interpret_risk(risk_score)
        
        # Get SHAP explanations
        shap_values = system.get_shap_explanation(input_data)
        
        # Get suggestions
        suggestions = system.get_suggestions(input_data, prediction_code)
        
        # Log to history
        log_prediction(input_data, prediction_code, risk_score)
        
        return PredictionResponse(
            prediction=prediction,
            prediction_code=prediction_code,
            risk_score=risk_score,
            risk_interpretation=risk_interpretation,
            shap_values=shap_values,
            suggestions=suggestions,
            anomalies=anomalies,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/what-if")
def what_if_analysis(request: WhatIfScenario):
    """
    Perform what-if analysis
    
    Args:
        application: Base loan application
        scenarios: Dict of parameter changes to test
    
    Returns:
        Results for each scenario
    """
    try:
        input_data = request.application.dict()
        scenarios = request.scenarios
        
        results = system.what_if_analysis(input_data, scenarios)
        
        return {
            "base_prediction": "Approved" if system.predict(input_data) == 0 else "Rejected",
            "base_risk_score": system.get_risk_score(input_data),
            "scenarios": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def log_prediction(input_data, prediction, risk_score):
    """
    PHASE 11: DATA LOGGING
    Log prediction to history.csv
    """
    try:
        # Prepare log entry
        log_entry = input_data.copy()
        log_entry['prediction'] = prediction
        log_entry['risk_score'] = risk_score
        log_entry['timestamp'] = datetime.now().isoformat()
        
        # Convert to DataFrame
        df = pd.DataFrame([log_entry])
        
        # Append to history.csv
        if os.path.exists('history.csv'):
            df.to_csv('history.csv', mode='a', header=False, index=False)
        else:
            df.to_csv('history.csv', mode='w', header=True, index=False)
    
    except Exception as e:
        print(f"Logging error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 Starting Loan Decision Intelligence API")
    print("="*60)
    print("\n📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
