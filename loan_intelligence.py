"""
LOAN DECISION INTELLIGENCE SYSTEM - CORE LOGIC
Phases 5-8: Risk Scoring, Suggestions, What-If Analysis, Anomaly Detection
"""
import pandas as pd
import numpy as np
import pickle
import shap

class LoanIntelligence:
    def __init__(self):
        """Initialize the Loan Intelligence System"""
        # Load model
        with open('model/model.pkl', 'rb') as f:
            self.model = pickle.load(f)
        
        # Load scaler
        with open('model/scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load feature order
        with open('model/feature_order.pkl', 'rb') as f:
            self.feature_order = pickle.load(f)
        
        # Load label encoders
        with open('model/label_encoders.pkl', 'rb') as f:
            self.encoders = pickle.load(f)
        
        # Load feature importances (always load as fallback)
        try:
            with open('model/feature_importances.pkl', 'rb') as f:
                self.feature_importances = pickle.load(f)
        except:
            # If file doesn't exist, use model's feature_importances
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importances = dict(zip(self.feature_order, self.model.feature_importances_))
            else:
                self.feature_importances = {f: 0.0 for f in self.feature_order}
        
        # Load SHAP explainer (if available)
        try:
            with open('model/shap_explainer.pkl', 'rb') as f:
                self.shap_explainer = pickle.load(f)
            self.use_shap = True
        except:
            self.use_shap = False
    
    def preprocess_input(self, input_data):
        """
        Preprocess user input to match training format
        
        Args:
            input_data: dict with keys matching original features
        
        Returns:
            numpy array ready for prediction
        """
        # Create DataFrame
        df = pd.DataFrame([input_data])
        
        # Feature engineering: total_assets
        df['total_assets'] = (
            df['residential_assets_value'] + 
            df['commercial_assets_value'] + 
            df['luxury_assets_value'] + 
            df['bank_asset_value']
        )
        
        # Drop original asset columns
        df = df.drop([
            'residential_assets_value',
            'commercial_assets_value',
            'luxury_assets_value',
            'bank_asset_value'
        ], axis=1)
        
        # Encode categorical variables
        df['education'] = self.encoders['education'].transform([input_data['education']])[0]
        df['self_employed'] = self.encoders['self_employed'].transform([input_data['self_employed']])[0]
        
        # Ensure correct feature order
        df = df[self.feature_order]
        
        # Scale features
        X_scaled = self.scaler.transform(df)
        
        return X_scaled
    
    def predict(self, input_data):
        """
        Make prediction
        
        Returns:
            prediction (0=Approved, 1=Rejected)
        """
        risk_score = self.get_risk_score(input_data)
        decision_band = self.get_decision_band(risk_score)

        # Binary output compatibility:
        # 0 = Approved, 1 = Rejected (Conditional is treated as reject path)
        if decision_band == "Approved":
            return 0
        return 1

    def get_confidence(self, input_data):
        """
        Get prediction confidence score

        Returns:
            confidence (float): Confidence percentage (0-100)
        """
        _, has_conflict = self._get_weighted_risk_components(input_data)
        risk_score = self.get_risk_score(input_data)

        # Lower certainty near decision boundaries (50 and 70).
        distance_from_mid = abs(risk_score - 60)
        confidence = 55.0 + min(distance_from_mid * 0.8, 35.0)

        # Conflicting indicators (e.g. weak credit + strong assets) lower confidence.
        if has_conflict:
            confidence -= 10.0

        confidence = float(np.clip(confidence, 55.0, 92.0))
        return round(confidence, 2)

    
    def get_risk_score(self, input_data):
        """
        PHASE 5: RISK SCORING SYSTEM
        
        Returns:
            risk_score: 0-100 (higher = riskier)
        """
        components, _ = self._get_weighted_risk_components(input_data)
        risk_score = int(round(
            0.4 * components["cibil_risk"] +
            0.3 * components["income_ratio_risk"] +
            0.2 * components["asset_risk"] +
            0.1 * components["income_risk"]
        ))
        return int(np.clip(risk_score, 0, 100))

    def get_decision_band(self, risk_score):
        """
        Decision bands derived from weighted risk score.
        """
        if risk_score > 70:
            return "Rejected"
        if risk_score > 50:
            return "Conditional"
        return "Approved"

    def _get_weighted_risk_components(self, input_data):
        """
        Compute policy risk components and conflict flag using weighted formula.
        """
        income = float(input_data.get("income_annum", 0))
        loan = float(input_data.get("loan_amount", 0))
        cibil = int(input_data.get("cibil_score", 750))
        total_assets = float(
            input_data.get("residential_assets_value", 0)
            + input_data.get("commercial_assets_value", 0)
            + input_data.get("luxury_assets_value", 0)
            + input_data.get("bank_asset_value", 0)
        )

        loan_to_income = loan / max(income, 1.0)
        loan_to_assets = loan / max(total_assets, 1.0)

        # 1) CIBIL risk
        if cibil < 600:
            cibil_risk = 90
        elif cibil < 700:
            cibil_risk = 60
        else:
            cibil_risk = 20

        # 2) Loan-to-income risk
        if loan_to_income > 0.6:
            income_ratio_risk = 90
        elif loan_to_income > 0.3:
            income_ratio_risk = 60
        else:
            income_ratio_risk = 20

        # 3) Loan-to-assets risk
        if loan_to_assets > 0.7:
            asset_risk = 80
        elif loan_to_assets > 0.3:
            asset_risk = 50
        else:
            asset_risk = 20

        # 4) Absolute income risk
        if income < 300000:
            income_risk = 80
        elif income < 800000:
            income_risk = 50
        else:
            income_risk = 20

        has_conflict = (
            cibil < 600 and loan_to_income > 0.6 and loan_to_assets <= 0.3
        ) or (
            income < 800000 and loan_to_assets <= 0.3
        )

        return {
            "cibil_risk": cibil_risk,
            "income_ratio_risk": income_ratio_risk,
            "asset_risk": asset_risk,
            "income_risk": income_risk,
        }, has_conflict
    
    def interpret_risk(self, risk_score):
        """Interpret risk score"""
        if risk_score > 70:
            return "High Risk - Likely Rejection"
        elif risk_score > 50:
            return "Medium Risk - Conditional Approval Zone"
        else:
            return "Low Risk - Likely Approval"
    
    def get_shap_explanation(self, input_data):
        """
        PHASE 4: Get SHAP explanations
        
        Returns:
            dict of feature contributions
        """
        X = self.preprocess_input(input_data)
        
        if self.use_shap:
            try:
                shap_values = self.shap_explainer.shap_values(X)
                
                # Handle different SHAP output formats
                if isinstance(shap_values, list):
                    # Binary classification - use class 1 (Rejected)
                    if len(shap_values) > 1:
                        values = shap_values[1][0]
                    else:
                        values = shap_values[0][0]
                elif len(shap_values.shape) == 3:
                    # 3D array: (samples, features, classes)
                    # Use class 1 (Rejected) for the first sample
                    values = shap_values[0, :, 1]
                elif len(shap_values.shape) == 2:
                    # 2D array: (samples, features)
                    values = shap_values[0]
                else:
                    # 1D array: (features,)
                    values = shap_values
                
                explanations = {}
                for feature, value in zip(self.feature_order, values):
                    try:
                        explanations[feature] = float(value)
                    except (TypeError, ValueError):
                        explanations[feature] = 0.0
                
                return explanations
            except Exception as e:
                print(f"SHAP failed: {e}, using feature importance")
                return self._get_feature_importance_explanation(X)
        else:
            return self._get_feature_importance_explanation(X)
    
    def _get_feature_importance_explanation(self, X):
        """Fallback: Use feature importance * feature value"""
        explanations = {}
        for i, feature in enumerate(self.feature_order):
            importance = self.feature_importances.get(feature, 0)
            value = X[0][i]
            explanations[feature] = float(importance * value)
        return explanations
    
    def get_suggestions(self, input_data, prediction):
        """
        PHASE 6: SUGGESTION ENGINE
        
        Returns:
            list of suggestions
        """
        suggestions = []
        
        # Only suggest if rejected
        if prediction == 1:  # Rejected
            # Check CIBIL score
            if input_data['cibil_score'] < 650:
                suggestions.append(
                    f"⚠️ Improve credit score (current: {input_data['cibil_score']}, target: 650+)"
                )
            
            # Check loan amount vs income
            if input_data['loan_amount'] > 0.5 * input_data['income_annum']:
                suggested_amount = int(0.4 * input_data['income_annum'])
                suggestions.append(
                    f"💰 Reduce loan amount (current: ₹{input_data['loan_amount']:,}, "
                    f"suggested: ₹{suggested_amount:,})"
                )
            
            # Check income
            if input_data['income_annum'] < 300000:
                suggestions.append(
                    f"📈 Increase annual income (current: ₹{input_data['income_annum']:,}, "
                    f"target: ₹300,000+)"
                )
            
            # Check assets
            total_assets = (
                input_data['residential_assets_value'] +
                input_data['commercial_assets_value'] +
                input_data['luxury_assets_value'] +
                input_data['bank_asset_value']
            )
            if total_assets < input_data['loan_amount']:
                suggestions.append(
                    f"🏠 Increase asset value (current: ₹{total_assets:,}, "
                    f"target: ₹{input_data['loan_amount']:,}+)"
                )
        else:
            suggestions.append("✅ Application looks good! No major concerns.")
        
        return suggestions
    
    def what_if_analysis(self, input_data, scenarios):
        """
        PHASE 7: WHAT-IF ANALYSIS
        
        Args:
            input_data: original input
            scenarios: dict of changes to test
                e.g., {'cibil_score': [650, 700, 750], 'income_annum': [400000, 500000]}
        
        Returns:
            dict of scenario results
        """
        results = {}
        
        for param, values in scenarios.items():
            results[param] = []
            for value in values:
                # Create modified input
                modified_input = input_data.copy()
                modified_input[param] = value
                
                # Get prediction
                prediction = self.predict(modified_input)
                risk_score = self.get_risk_score(modified_input)
                
                results[param].append({
                    'value': value,
                    'prediction': 'Approved' if prediction == 0 else 'Rejected',
                    'risk_score': risk_score
                })
        
        return results
    
    def detect_anomalies(self, input_data):
        """
        PHASE 8: ANOMALY DETECTION
        
        Returns:
            list of anomaly warnings
        """
        warnings = []
        
        # Check unrealistic income
        if input_data['income_annum'] > 1e8:
            warnings.append(f"⚠️ Unrealistic income: ₹{input_data['income_annum']:,}")
        
        # Check unrealistic loan amount
        if input_data['loan_amount'] > 1e8:
            warnings.append(f"⚠️ Unrealistic loan amount: ₹{input_data['loan_amount']:,}")
        
        # Check CIBIL score range
        if input_data['cibil_score'] < 300 or input_data['cibil_score'] > 900:
            warnings.append(f"⚠️ Invalid CIBIL score: {input_data['cibil_score']} (valid: 300-900)")
        
        # Check negative values
        for key, value in input_data.items():
            if isinstance(value, (int, float)) and value < 0:
                warnings.append(f"⚠️ Negative value detected: {key} = {value}")
        
        # Check loan term
        if input_data['loan_term'] not in [2, 5, 10, 15, 20]:
            warnings.append(f"⚠️ Unusual loan term: {input_data['loan_term']} years")
        
        return warnings

# Test the system
if __name__ == "__main__":
    print("="*60)
    print("TESTING LOAN INTELLIGENCE SYSTEM")
    print("="*60)
    
    # Initialize system
    system = LoanIntelligence()
    print("\n✓ System initialized")
    
    # Test case 1: High income + high CIBIL → Approved
    test_input_1 = {
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
    
    print("\n" + "="*60)
    print("TEST CASE 1: High income + high CIBIL")
    print("="*60)
    prediction = system.predict(test_input_1)
    risk_score = system.get_risk_score(test_input_1)
    print(f"Prediction: {'Approved' if prediction == 0 else 'Rejected'}")
    print(f"Risk Score: {risk_score}/100 - {system.interpret_risk(risk_score)}")
    
    # Test case 2: Low income + low CIBIL → Rejected
    test_input_2 = {
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
    
    print("\n" + "="*60)
    print("TEST CASE 2: Low income + low CIBIL")
    print("="*60)
    prediction = system.predict(test_input_2)
    risk_score = system.get_risk_score(test_input_2)
    suggestions = system.get_suggestions(test_input_2, prediction)
    print(f"Prediction: {'Approved' if prediction == 0 else 'Rejected'}")
    print(f"Risk Score: {risk_score}/100 - {system.interpret_risk(risk_score)}")
    print(f"\nSuggestions:")
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
