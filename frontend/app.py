"""
PHASE 10: FRONTEND (Streamlit) - FIXED & IMPROVED VERSION
"""
import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pickle
import csv
from datetime import datetime

# Add parent directory to path and change to parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

from loan_intelligence import LoanIntelligence

# Page config
st.set_page_config(
    page_title="Loan Decision Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .approved {
        color: #28a745;
        font-weight: bold;
    }
    .rejected {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize system with error handling
@st.cache_resource
def load_system():
    try:
        return LoanIntelligence()
    except FileNotFoundError as e:
        st.error(f"❌ Model files not found: {e}")
        st.info("Please run the training phases first (phase1-4)")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading system: {e}")
        st.stop()

system = load_system()

# Load label encoders for correct mapping
@st.cache_resource
def load_label_encoders():
    try:
        with open('model/label_encoders.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

encoders = load_label_encoders()

HISTORY_COLUMNS = [
    'no_of_dependents',
    'education',
    'self_employed',
    'income_annum',
    'loan_amount',
    'loan_term',
    'cibil_score',
    'residential_assets_value',
    'commercial_assets_value',
    'luxury_assets_value',
    'bank_asset_value',
    'prediction',
    'risk_score',
    'confidence',
    'timestamp',
]

# Create prediction label mapping
def get_prediction_label(prediction_code):
    """Convert prediction code to human-readable label"""
    if encoders and 'loan_status' in encoders:
        # Use encoder to get correct mapping
        label = encoders['loan_status'].inverse_transform([prediction_code])[0]
        return label.strip()  # Remove spaces
    else:
        # Fallback mapping
        return "Approved" if prediction_code == 0 else "Rejected"


def load_history_file(path='history.csv'):
    """
    Robust history loader that accepts both legacy rows (without confidence)
    and newer rows (with confidence).
    """
    rows = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        _ = next(reader, None)  # Skip existing header if present

        for raw_row in reader:
            if not raw_row:
                continue
            # Legacy format: 14 fields (no confidence)
            if len(raw_row) == 14:
                parsed = raw_row[:13] + [None, raw_row[13]]
            # New format: 15 fields (with confidence)
            elif len(raw_row) == 15:
                parsed = raw_row
            else:
                # Skip malformed lines instead of failing the History tab.
                continue
            rows.append(parsed)

    df = pd.DataFrame(rows, columns=HISTORY_COLUMNS)

    # Numeric conversions for metrics/charts
    for col in [
        'no_of_dependents',
        'income_annum',
        'loan_amount',
        'loan_term',
        'cibil_score',
        'residential_assets_value',
        'commercial_assets_value',
        'luxury_assets_value',
        'bank_asset_value',
        'prediction',
        'risk_score',
        'confidence',
    ]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Initialize session state
if 'last_input' not in st.session_state:
    st.session_state['last_input'] = None

# Title
st.markdown('<h1 class="main-header">🏦 Loan Decision Intelligence System</h1>', unsafe_allow_html=True)
st.markdown("### AI-Powered Loan Approval with Explainability & Risk Analysis")

# Sidebar - Model Info
with st.sidebar:
    st.header("📊 Model Information")
    
    # Load model metadata
    try:
        with open('model/model_metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        
        st.metric("Best Model", metadata['best_model'])
        st.metric("Accuracy", f"{metadata['best_accuracy']*100:.2f}%")
        
        st.subheader("All Models")
        for model_name, acc in metadata['all_accuracies'].items():
            st.write(f"**{model_name}**: {acc*100:.2f}%")
    except:
        st.info("Model metadata not available")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    This system uses machine learning to:
    - Predict loan approval
    - Calculate risk scores
    - Explain decisions
    - Suggest improvements
    - Simulate scenarios
    """)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Application", "🔮 What-If Analysis", "📈 History", "📚 Guide"])

with tab1:
    st.header("Loan Application Form")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Personal Information")
        no_of_dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, value=2)
        education = st.selectbox("Education", [" Graduate", " Not Graduate"])
        self_employed = st.selectbox("Self Employed", [" No", " Yes"])
    
    with col2:
        st.subheader("Financial Information")
        income_annum = st.number_input("Annual Income (₹)", min_value=1, value=5000000, step=100000,
                                       help="Must be greater than 0")
        loan_amount = st.number_input("Loan Amount (₹)", min_value=1, value=10000000, step=100000,
                                      help="Must be greater than 0")
        loan_term = st.selectbox("Loan Term (years)", [2, 5, 10, 15, 20], index=2)
        cibil_score = st.slider("CIBIL Score", min_value=300, max_value=900, value=750)
    
    with col3:
        st.subheader("Assets Information")
        residential_assets_value = st.number_input("Residential Assets (₹)", min_value=0, value=5000000, step=100000)
        commercial_assets_value = st.number_input("Commercial Assets (₹)", min_value=0, value=3000000, step=100000)
        luxury_assets_value = st.number_input("Luxury Assets (₹)", min_value=0, value=2000000, step=100000)
        bank_asset_value = st.number_input("Bank Assets (₹)", min_value=0, value=1000000, step=100000)
    
    st.markdown("---")
    
    if st.button("🔍 Analyze Application", type="primary", use_container_width=True):
        # INPUT VALIDATION
        validation_errors = []
        if income_annum <= 0:
            validation_errors.append("Annual income must be greater than 0")
        if loan_amount <= 0:
            validation_errors.append("Loan amount must be greater than 0")
        
        if validation_errors:
            st.error("❌ **Validation Errors:**")
            for error in validation_errors:
                st.write(f"- {error}")
        else:
            # Prepare input
            input_data = {
                'no_of_dependents': no_of_dependents,
                'education': education,
                'self_employed': self_employed,
                'income_annum': income_annum,
                'loan_amount': loan_amount,
                'loan_term': loan_term,
                'cibil_score': cibil_score,
                'residential_assets_value': residential_assets_value,
                'commercial_assets_value': commercial_assets_value,
                'luxury_assets_value': luxury_assets_value,
                'bank_asset_value': bank_asset_value
            }
            
            # Store in session state for What-If tab
            st.session_state['last_input'] = input_data.copy()
            
            # Check anomalies
            anomalies = system.detect_anomalies(input_data)
            if anomalies:
                st.warning("⚠️ **Anomalies Detected:**")
                for anomaly in anomalies:
                    st.write(f"- {anomaly}")
                st.markdown("---")
            
            # Make prediction
            with st.spinner("Analyzing application..."):
                try:
                    prediction = system.predict(input_data)
                    risk_score = system.get_risk_score(input_data)
                    risk_interpretation = system.interpret_risk(risk_score)
                    shap_values = system.get_shap_explanation(input_data)
                    suggestions = system.get_suggestions(input_data, prediction)
                    
                    # Get confidence score using predict_proba
                    confidence = system.get_confidence(input_data)
                    
                except Exception as e:
                    st.error(f"❌ Prediction error: {e}")
                    st.stop()
            
            # Display results
            st.markdown("## � Analysis Results")
            
            # Prediction with correct label mapping
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                prediction_label = get_prediction_label(prediction)
                if prediction_label == "Approved":
                    st.markdown('<h2 class="approved">✅ APPROVED</h2>', unsafe_allow_html=True)
                else:
                    st.markdown('<h2 class="rejected">❌ REJECTED</h2>', unsafe_allow_html=True)
            
            with col2:
                st.metric("Risk Score", f"{risk_score}/100")
                st.caption(risk_interpretation)
            
            with col3:
                st.metric("Confidence", f"{confidence:.1f}%")
                st.caption("Model certainty")
            
            with col4:
                # FIX: Safe division to avoid division by zero
                total_assets = (residential_assets_value + commercial_assets_value + 
                              luxury_assets_value + bank_asset_value)
                st.metric("Total Assets", f"₹{total_assets:,}")
                if total_assets > 0:
                    loan_to_asset_ratio = (loan_amount / total_assets) * 100
                    st.caption(f"Loan-to-Asset: {loan_to_asset_ratio:.1f}%")
                else:
                    st.caption("Loan-to-Asset: N/A (No assets)")
            
            st.markdown("---")
            
            # Risk gauge
            st.subheader("🎯 Risk Assessment")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgreen"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance - FIX: Use RdBu color scale for SHAP
            st.subheader("🧠 Decision Explanation")
            
            # Sort by absolute impact and show top features
            shap_df = pd.DataFrame(list(shap_values.items()), columns=['Feature', 'Impact'])
            shap_df = shap_df.sort_values('Impact', key=abs, ascending=False)
            
            # Display top 3 features
            st.markdown("**Top 3 Most Important Factors:**")
            top_3 = shap_df.head(3)
            for idx, row in top_3.iterrows():
                impact_direction = "increases" if row['Impact'] > 0 else "decreases"
                st.write(f"🔹 **{row['Feature']}**: {impact_direction} approval chance (impact: {row['Impact']:.3f})")
            
            st.markdown("---")
            
            # Full SHAP chart with correct color scale
            fig = px.bar(shap_df, x='Impact', y='Feature', orientation='h',
                         title='Feature Impact on Decision (SHAP Values)',
                         color='Impact',
                         color_continuous_scale='RdBu',  # FIX: Correct color scale for SHAP
                         color_continuous_midpoint=0)
            st.plotly_chart(fig, use_container_width=True)
            
            # Suggestions
            st.subheader("💡 Suggestions")
            for suggestion in suggestions:
                st.info(suggestion)
            
            # Log to history
            log_entry = input_data.copy()
            log_entry['prediction'] = prediction
            log_entry['risk_score'] = risk_score
            log_entry['timestamp'] = datetime.now().isoformat()
            
            df_log = pd.DataFrame([log_entry])
            try:
                if os.path.exists('history.csv'):
                    df_log.to_csv('history.csv', mode='a', header=False, index=False)
                else:
                    df_log.to_csv('history.csv', mode='w', header=True, index=False)
            except Exception as e:
                st.warning(f"Could not save to history: {e}")

with tab2:
    st.header("🔮 What-If Analysis")
    st.write("Simulate changes to see how they affect the decision")
    
    # FIX: Use session state instead of undefined variables
    if st.session_state['last_input'] is None:
        st.warning("⚠️ Please make a prediction in the Application tab first!")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Scenario: CIBIL Score")
            cibil_scenarios = st.multiselect(
                "Test CIBIL Scores",
                [600, 650, 700, 750, 800, 850],
                default=[650, 750]
            )
        
        with col2:
            st.subheader("Scenario: Annual Income")
            income_scenarios = st.multiselect(
                "Test Income Levels (₹)",
                [3000000, 4000000, 5000000, 6000000, 7000000],
                default=[4000000, 6000000]
            )
        
        if st.button("Run What-If Analysis"):
            # Use session state input
            base_input = st.session_state['last_input'].copy()
            
            scenarios = {}
            if cibil_scenarios:
                scenarios['cibil_score'] = cibil_scenarios
            if income_scenarios:
                scenarios['income_annum'] = income_scenarios
            
            if scenarios:
                with st.spinner("Running simulations..."):
                    try:
                        results = system.what_if_analysis(base_input, scenarios)
                    except Exception as e:
                        st.error(f"Error running analysis: {e}")
                        st.stop()
                
                # Display results
                for param, param_results in results.items():
                    st.subheader(f"📊 {param.replace('_', ' ').title()}")
                    
                    df_results = pd.DataFrame(param_results)
                    
                    # Create visualization
                    fig = px.line(df_results, x='value', y='risk_score', 
                                 markers=True, title=f'Risk Score vs {param}')
                    fig.add_scatter(x=df_results['value'], y=[50]*len(df_results), 
                                   mode='lines', name='Medium Risk Threshold',
                                   line=dict(dash='dash', color='orange'))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show table
                    st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("Please select at least one scenario to test")

with tab3:
    st.header("📈 Prediction History")
    
    if os.path.exists('history.csv'):
        try:
            df_history = load_history_file('history.csv')
            
            # FIX: Limit to last 100 records to prevent file growth issues
            if len(df_history) > 100:
                df_history = df_history.tail(100)
            
            if len(df_history) > 0:
                st.metric("Total Applications (Last 100)", len(df_history))
                
                col1, col2 = st.columns(2)
                with col1:
                    approved = (df_history['prediction'] == 0).sum()
                    st.metric("Approved", approved, f"{approved/len(df_history)*100:.1f}%")
                with col2:
                    rejected = (df_history['prediction'] == 1).sum()
                    st.metric("Rejected", rejected, f"{rejected/len(df_history)*100:.1f}%")
                
                # Show recent applications
                st.subheader("Recent Applications")
                display_df = df_history.tail(20).copy()
                
                # Add readable prediction labels
                if 'prediction' in display_df.columns:
                    display_df['status'] = display_df['prediction'].apply(get_prediction_label)
                
                st.dataframe(display_df, use_container_width=True)
                
                # Risk score distribution
                st.subheader("Risk Score Distribution")
                fig = px.histogram(df_history, x='risk_score', nbins=20,
                                 title='Distribution of Risk Scores',
                                 labels={'risk_score': 'Risk Score', 'count': 'Frequency'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No history available yet")
        except Exception as e:
            st.error(f"Error loading history: {e}")
    else:
        st.info("No history available yet. Make your first prediction!")

with tab4:
    st.header("📚 User Guide")
    
    st.markdown("""
    ## How to Use This System
    
    ### 1. Fill Application Form
    - Enter all required information in the **Application** tab
    - Ensure all values are realistic and positive
    - Click **Analyze Application** to get results
    
    ### 2. Understand Results
    - **Prediction**: Approved or Rejected
    - **Risk Score**: 0-100 (lower is better)
        - 0-50: Low Risk (Likely Approval)
        - 50-80: Medium Risk
        - 80-100: High Risk (Likely Rejection)
    - **Confidence**: Model's certainty in the prediction
    - **Feature Impact**: Shows which factors influenced the decision
        - Positive values → increase approval chance
        - Negative values → decrease approval chance
    - **Suggestions**: Actionable recommendations for improvement
    
    ### 3. What-If Analysis
    - Test different scenarios
    - See how changes affect approval chances
    - Plan improvements strategically
    - **Note**: Make a prediction first to enable this feature
    
    ### 4. Key Factors
    The most important factors for loan approval:
    1. **CIBIL Score** (Most Important - 81.89%)
    2. **Loan Term** (8.27%)
    3. **Income** (4.33%)
    4. **Loan Amount** (4.01%)
    5. **Total Assets** (1.00%)
    
    ### 5. Tips for Approval
    - Maintain CIBIL score above 650 (ideally 750+)
    - Keep loan amount reasonable relative to income
    - Build substantial assets
    - Choose appropriate loan term
    - Ensure stable employment
    
    ### 6. Anomaly Warnings
    The system will warn you if:
    - Income seems unrealistic (>₹10 crore)
    - CIBIL score is out of valid range (300-900)
    - Any negative values are entered
    - Unusual loan terms are selected
    
    ### 7. Understanding SHAP Values
    - SHAP values explain individual predictions
    - They show how each feature pushes the prediction
    - Red bars (negative) → push toward rejection
    - Blue bars (positive) → push toward approval
    - Larger absolute values = stronger impact
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Loan Decision Intelligence System v2.0 (Fixed & Improved) | Built with ❤️ using Streamlit & ML</p>
</div>
""", unsafe_allow_html=True)
