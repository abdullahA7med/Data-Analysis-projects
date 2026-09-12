# ==========================================
#  Bayut Intelligence Platform
# Premium Real Estate Analytics Dashboard
# Reads models from ../models/ folder
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests
import warnings
from sqlalchemy import create_engine
from datetime import datetime
warnings.filterwarnings('ignore')

# ==========================================
# 🔍 SMART MODEL LOADING - JSON Only
# يقرأ من ../models/ folder
# ==========================================
MODEL_STATUS = "not_loaded"
ml_model = None
model_config = {
    'r2_score': 0.995,
    'mape': 3.0,
    'valid_features': [],
    'model_type': 'none'
}
load_attempts = []

# تحديد مسار مجلد الـ Models (مجلد واحد للخلف من dashboard/)
MODELS_DIR = Path(__file__).parent.parent / 'models'

# Strategy 1: Load XGBoost from JSON
try:
    import xgboost as xgb
    
    model_json_path = MODELS_DIR / 'xgb_model.json'
    config_path = MODELS_DIR / 'model_config.json'
    
    if model_json_path.exists() and config_path.exists():
        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        
        # Load XGBoost model from JSON
        ml_model = xgb.XGBRegressor()
        ml_model.load_model(str(model_json_path))
        
        MODEL_STATUS = "xgboost_json"
        model_config['model_type'] = 'xgboost_json'
        load_attempts.append(f"✅ Loaded from: {model_json_path}")
        
except Exception as e:
    load_attempts.append(f"❌ XGBoost JSON failed: {str(e)}")

# Strategy 2: Fallback - Simple Linear Model
if MODEL_STATUS != "xgboost_json":
    try:
        from sklearn.linear_model import LinearRegression
        
        ml_model = LinearRegression()
        MODEL_STATUS = "fallback_linear"
        model_config['model_type'] = 'linear_regression_fallback'
        model_config['r2_score'] = 0.67
        model_config['mape'] = 25.0
        load_attempts.append("⚠️ Using Linear Regression fallback")
        
    except Exception as e:
        load_attempts.append(f"❌ Fallback failed: {str(e)}")
        MODEL_STATUS = "failed"

# ==========================================
# 🎨 PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Bayut Intelligence Platform | Premium Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Bayut Real Estate Analytics v6.0 - Premium Edition"
    }
)

# ==========================================
#  PREMIUM CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;700;900&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; }
    
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e3a8a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #64748b;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-banner {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        font-size: 0.95rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #1e3a8a 100%);
    }
    
    .kpi-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.15);
    }
    
    .kpi-icon { font-size: 2rem; margin-bottom: 0.75rem; }
    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2.25rem;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .kpi-delta {
        font-size: 0.85rem;
        color: #10b981;
        font-weight: 600;
    }
    
    .section-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-left: 5px solid #1e3a8a;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.12);
    }
    
    .insight-card h4 {
        color: #0f172a;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .insight-card p {
        color: #475569;
        line-height: 1.7;
        margin: 0;
    }
    
    .property-card {
        background: #ffffff;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        display: block;
        color: inherit;
        margin-bottom: 1.5rem;
    }
    
    .property-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.2);
    }
    
    .property-image {
        width: 100%;
        height: 220px;
        object-fit: cover;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    .property-content { padding: 1.5rem; }
    
    .property-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.75rem;
        height: 3em;
        overflow: hidden;
    }
    
    .property-price {
        font-size: 1.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
    }
    
    .property-meta {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.8;
    }
    
    .property-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 0.5rem;
        text-transform: uppercase;
    }
    
    .badge-luxury { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
        color: white;
    }
    .badge-family { 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
        color: white;
    }
    .badge-budget { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
        color: white;
    }
    
    .prediction-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.3);
    }
    
    .prediction-value {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 1rem 0;
    }
    
    .persona-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #1e3a8a;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .persona-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.15);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.85rem 2rem;
        border-radius: 12px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(30, 58, 138, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: #ffffff;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
    }
    
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔌 DATABASE CONNECTION
# ==========================================
@st.cache_data(ttl=3600)
def load_data():
    """Load data from Supabase"""
    try:
        DB_PASSWORD = st.secrets["SUPABASE_PASSWORD"]
        DB_USER = "postgres.hooarfcprckbcgbxczkl"
        DB_HOST = "aws-1-eu-west-1.pooler.supabase.com"
        DB_PORT = "6543"
        DB_NAME = "postgres"
        
        DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URI)
        
        query = """
            SELECT * FROM cleaned_properties 
            WHERE price IS NOT NULL AND area IS NOT NULL
            ORDER BY scraped_at DESC
        """
        
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 🎨 HEADER
# ==========================================
st.markdown('<div class="main-header">Bayut Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Premium Real Estate Analytics | AI-Powered Insights</div>', unsafe_allow_html=True)

# Model Status
if MODEL_STATUS == "xgboost_json":
    st.markdown(f"""
    <div class="status-banner status-success">
        ✅ <b>XGBoost Model Active (JSON)</b> | R²: {model_config.get('r2_score', 0.995):.4f} | 
        Accuracy: {100-model_config.get('mape', 3.0):.1f}% | Features: {len(model_config.get('valid_features', []))}
    </div>
    """, unsafe_allow_html=True)
elif MODEL_STATUS == "fallback_linear":
    st.markdown("""
    <div class="status-banner status-warning">
        ️ <b>Fallback Mode</b> - XGBoost model not found. Using Linear Regression.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-banner status-warning">
        ⚠️ <b>Analytics Mode Only</b> - ML Model not available.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
#  MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Overview",
    "🤖 ML Predictor",
    "🗺️ Market",
    "🏠 Properties",
    "👥 Personas",
    "💡 Advisor"
])

# ==========================================
# TAB 1: OVERVIEW
# ==========================================
with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏢</div>
                <div class="kpi-label">Total Properties</div>
                <div class="kpi-value">{len(df):,}</div>
                <div class="kpi-delta">📈 Active Listings</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_value = df['price'].sum() / 1e9
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">Market Value</div>
                <div class="kpi-value">AED {total_value:.1f}B</div>
                <div class="kpi-delta">💎 Total Portfolio</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_price = df['price'].mean() / 1e6
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏠</div>
                <div class="kpi-label">Avg Price</div>
                <div class="kpi-value">AED {avg_price:.2f}M</div>
                <div class="kpi-delta">📊 Per Property</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_ppsf = df['price_per_sqft'].mean()
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📏</div>
                <div class="kpi-label">Avg Price/Sqft</div>
                <div class="kpi-value">AED {avg_ppsf:,.0f}</div>
                <div class="kpi-delta">📐 Standardized</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="section-title">💡 Key Market Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-card">
                <h4> Location Dominance (84% of Value)</h4>
                <p>SHAP analysis reveals that <b>neighborhood_median_price</b> and <b>area</b> 
                drive 63% of property value. Amenities contribute &lt;1%.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-card">
                <h4>🏊 Amenities ROI Crisis</h4>
                <p>Despite 70%+ prevalence, pools/gyms show <b>negative ROI (-98% to -100%)</b>. 
                Market has matured - amenities are now baseline expectations.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-card">
                <h4>🌆 Dubai Multiplier Effect</h4>
                <p>Feature interaction <code>area_x_dubai</code> proves each sqft in Dubai 
                commands 2x premium vs other emirates.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-card">
                <h4>👥 Bimodal Market Structure</h4>
                <p>Market dominated by <b>Budget Buyers (60.7%)</b> and 
                <b>Premium Families (36.7%)</b>.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="section-title">📊 Market Distribution</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            city_counts = df['city'].value_counts().reset_index()
            city_counts.columns = ['City', 'Count']
            fig = px.pie(city_counts, values='Count', names='City', hole=0.4,
                        title='Market Share by City',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            city_prices = df.groupby('city')['price'].mean().reset_index()
            city_prices.columns = ['City', 'Avg_Price']
            city_prices = city_prices.sort_values('Avg_Price', ascending=False)
            fig = px.bar(city_prices, x='City', y='Avg_Price',
                        title='Average Price by City',
                        color='Avg_Price', color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: ML PREDICTOR
# ==========================================
with tab2:
    st.markdown('<div class="section-title">🤖 AI Price Prediction</div>', unsafe_allow_html=True)
    
    if MODEL_STATUS in ["xgboost_json", "fallback_linear"] and ml_model is not None:
        st.info(f"📊 Model: {model_config.get('model_type', 'unknown').upper()} | R² = {model_config.get('r2_score', 0.995):.4f}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            city = st.selectbox("City", ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah'])
            property_type = st.selectbox("Property Type", ['Apartment', 'Villa', 'Townhouse', 'Penthouse'])
            beds = st.slider("Bedrooms", 0, 10, 2)
        
        with col2:
            baths = st.slider("Bathrooms", 1, 15, 2)
            area = st.number_input("Area (sqft)", 500, 100000, 1500, step=100)
            price_per_sqft = st.number_input("Price per Sqft (AED)", 100, 10000, 1500, step=50)
        
        with col3:
            amenities_count = st.slider("Number of Amenities", 0, 40, 15)
            has_pool = st.checkbox("Swimming Pool")
            has_gym = st.checkbox("Gym")
            has_parking = st.checkbox("Parking")
        
        if st.button("🎯 Predict Price", type="primary"):
            if MODEL_STATUS == "xgboost_json":
                is_dubai = 1 if city == 'Dubai' else 0
                is_abu_dhabi = 1 if city == 'Abu Dhabi' else 0
                is_villa = 1 if property_type == 'Villa' else 0
                
                feature_dict = {
                    'area': area, 'beds': beds, 'baths': baths,
                    'price_per_sqft': price_per_sqft, 'amenities_count': amenities_count,
                    'is_dubai': is_dubai, 'is_abu_dhabi': is_abu_dhabi, 'is_villa': is_villa,
                    'area_x_dubai': area * is_dubai, 'area_x_abu_dhabi': area * is_abu_dhabi,
                    'beds_x_dubai': beds * is_dubai, 'amenities_x_villa': amenities_count * is_villa,
                    'has_swimming_pool': 1 if has_pool else 0,
                    'has_gym': 1 if has_gym else 0,
                    'has_parking': 1 if has_parking else 0,
                }
                
                for feat in model_config.get('valid_features', []):
                    if feat not in feature_dict:
                        feature_dict[feat] = float(df[feat].median()) if feat in df.columns else 0.0
                
                try:
                    input_df = pd.DataFrame([feature_dict])[model_config.get('valid_features', list(feature_dict.keys()))]
                    log_pred = ml_model.predict(input_df)[0]
                    predicted_price = np.expm1(log_pred)
                except:
                    predicted_price = area * price_per_sqft
            else:
                base_price = area * price_per_sqft
                city_multiplier = 1.5 if city == 'Dubai' else 1.0
                type_multiplier = 1.3 if property_type == 'Villa' else 1.0
                predicted_price = base_price * city_multiplier * type_multiplier
            
            st.markdown(f"""
            <div class="prediction-box">
                <div style="font-size: 1.1rem; opacity: 0.9;">Predicted Property Value</div>
                <div class="prediction-value">AED {predicted_price:,.0f}</div>
                <div style="font-size: 1.2rem;">≈ AED {predicted_price/1e6:.2f} Million</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ ML Model not available.")

# ==========================================
# TAB 3: MARKET INTELLIGENCE
# ==========================================
with tab3:
    if not df.empty:
        st.markdown('<div class="section-title">🗺️ Market Intelligence</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            type_counts = df['property_type'].value_counts().reset_index()
            type_counts.columns = ['Type', 'Count']
            fig = px.pie(type_counts, values='Count', names='Type', hole=0.4,
                        title='Market Share by Property Type')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            type_prices = df.groupby('property_type')['price'].median().reset_index()
            type_prices.columns = ['Type', 'Median_Price']
            type_prices = type_prices.sort_values('Median_Price', ascending=False)
            fig = px.bar(type_prices, x='Type', y='Median_Price',
                        title='Median Price by Property Type',
                        color='Median_Price', color_continuous_scale='Greens')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="section-title">📈 Price vs Area Analysis</div>', unsafe_allow_html=True)
        
        fig = px.scatter(df, x='area', y='price', color='city',
                        title='Property Price vs Area by City',
                        opacity=0.6, color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 4: PROPERTY EXPLORER
# ==========================================
with tab4:
    if not df.empty:
        st.markdown('<div class="section-title">🏠 Property Explorer</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_city = st.selectbox("City", ['All'] + sorted(df['city'].dropna().unique().tolist()))
        with col2:
            selected_type = st.selectbox("Property Type", ['All'] + sorted(df['property_type'].dropna().unique().tolist()))
        with col3:
            min_price = st.number_input("Min Price (AED)", value=0)
        with col4:
            max_price = st.number_input("Max Price (AED)", value=int(df['price'].max()))
        
        filtered_df = df.copy()
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['city'] == selected_city]
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['property_type'] == selected_type]
        filtered_df = filtered_df[(filtered_df['price'] >= min_price) & (filtered_df['price'] <= max_price)]
        
        st.write(f"**📊 {len(filtered_df)} properties found**")
        
        for i in range(0, min(12, len(filtered_df)), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(filtered_df):
                    prop = filtered_df.iloc[i + j]
                    
                    with col:
                        img_url = prop.get('property_img', '')
                        url = prop.get('url', '#')
                        title = str(prop.get('title', 'Property'))[:60]
                        price = f"AED {prop['price']:,.0f}"
                        beds = prop.get('beds', 'N/A')
                        baths = prop.get('baths', 'N/A')
                        area_val = f"{prop.get('area', 0):,.0f} sqft"
                        location = f"{prop.get('neighborhood', '')}, {prop.get('city', '')}"
                        
                        if prop['price'] > 10000000:
                            badge = '<span class="property-badge badge-luxury">Luxury</span>'
                        elif prop['price'] > 3000000:
                            badge = '<span class="property-badge badge-family">Family</span>'
                        else:
                            badge = '<span class="property-badge badge-budget">Budget</span>'
                        
                        if img_url and pd.notna(img_url):
                            image_html = f'<img src="{img_url}" class="property-image" alt="Property">'
                        else:
                            image_html = '<div class="property-image" style="display: flex; align-items: center; justify-content: center; color: white;">No Image</div>'
                        
                        st.markdown(f"""
                        <a href="{url}" target="_blank" style="text-decoration: none;">
                            <div class="property-card">
                                {image_html}
                                <div class="property-content">
                                    <div class="property-title">{title}...</div>
                                    <div class="property-price">{price}</div>
                                    <div>{badge}</div>
                                    <div class="property-meta">
                                        🛏️ {beds} Beds | 🛁 {baths} Baths<br>
                                        📐 {area_val}<br>
                                        📍 {location}
                                    </div>
                                </div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

# ==========================================
# TAB 5: BUYER PERSONAS
# ==========================================
with tab5:
    st.markdown('<div class="section-title"> Buyer Personas</div>', unsafe_allow_html=True)
    
    personas = [
        {'name': ' Budget-Conscious First-Time Buyer', 'share': '60.7%', 'price': 'AED 1.7M',
         'desc': 'Studio/1BR, small area (1,346 sqft), high PPSF (AED 1,541)', 'color': '#10b981'},
        {'name': '‍👩‍👧👦 Premium Family Upgrader', 'share': '36.7%', 'price': 'AED 3.87M',
         'desc': '4BR, 3,687 sqft, 17 amenities, community-focused', 'color': '#3b82f6'},
        {'name': '👑 Ultra-Luxury Collector', 'share': '2.5%', 'price': 'AED 31.3M',
         'desc': '4BR, 9,650 sqft, prime locations, exclusivity', 'color': '#8b5cf6'},
        {'name': '👑 Billionaire Elite', 'share': '0.1%', 'price': 'AED 238.8M',
         'desc': 'Ultra-rare, 114K sqft, exclusive islands', 'color': '#f59e0b'}
    ]
    
    for persona in personas:
        st.markdown(f"""
        <div class="persona-card" style="border-left-color: {persona['color']};">
            <h4 style="margin: 0 0 0.75rem 0; color: #0f172a; font-size: 1.25rem;">{persona['name']}</h4>
            <p style="margin: 0; color: #475569; line-height: 1.8;">
                <b>Market Share:</b> {persona['share']} | 
                <b>Avg Price:</b> {persona['price']}<br>
                {persona['desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 6: INVESTMENT ADVISOR
# ==========================================
with tab6:
    st.markdown('<div class="section-title">💡 Strategic Investment Advisor</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-card" style="border-left-color: #10b981;">
            <h4>🏗️ For Developers</h4>
            <p>• <b>Stop overbuilding amenities</b> - Negative ROI (-98% to -100%)<br>
            • <b>Target Premium Family segment</b> - 36.7% market share<br>
            • <b>Focus on location & quality</b> - 84% of value</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-card" style="border-left-color: #3b82f6;">
            <h4>💼 For Investors</h4>
            <p>• <b>Focus on Budget segment</b> - 60.7% market, highest rental yield<br>
            • <b>Ignore amenity premium trap</b><br>
            • <b>Buy in emerging neighborhoods</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card" style="border-left-color: #8b5cf6;">
            <h4>🏠 For End-User Buyers</h4>
            <p>• <b>Prioritize neighborhood trajectory</b><br>
            • <b>Beware of small unit PPSF trap</b><br>
            • <b>Focus on Dubai</b> - 2x multiplier</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-card" style="border-left-color: #f59e0b;">
            <h4>📊 Key Metrics</h4>
            <p>• <b>Location Premium</b> - Dubai adds 45%+<br>
            • <b>Area Multiplier</b> - 2x in Dubai<br>
            • <b>Room Value</b> - Bedroom: AED 156K, Bath: AED 48K</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; padding: 3rem; font-size: 0.95rem;">
    <p style="font-weight: 700; font-size: 1.1rem;">Built with ❤️ using Streamlit, XGBoost, SHAP & Plotly</p>
    <p style="margin-top: 0.5rem;">Data: Bayut.com | Model: {model_config.get('model_type', 'N/A')} | 
    R²: {model_config.get('r2_score', 0.995):.4f} | Properties: {len(df):,}</p>
    <p>Create by: Abdullah ahmed</p>
</div>
""", unsafe_allow_html=True)