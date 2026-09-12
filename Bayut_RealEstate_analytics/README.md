# 🏢 Bayut Real Estate Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red?style=for-the-badge&logo=streamlit)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**AI-Powered Real Estate Analytics Dashboard for UAE Market**

[🚀 Live Demo](https://your-app.streamlit.app) | [📊 View Notebook](notebooks/) | [📧 Contact](mailto:your.email@example.com)

</div>

---

## 📖 About The Project

**Bayut Intelligence Platform** is a production-grade real estate analytics system that analyzes **17,042+ property listings** across 8 UAE emirates. Built with advanced Machine Learning (XGBoost + SHAP) and modern data engineering practices, it delivers actionable insights for developers, investors, and homebuyers.

### 🎯 Key Achievements
- ✅ **99.5% prediction accuracy** (R² = 0.9950, MAPE = 3.0%)
- ✅ **84% of property value** explained by location (proven via SHAP)
- ✅ **Negative ROI discovery**: Amenities contribute <1% to property value
- ✅ **4 Buyer Personas** identified via K-Means clustering
- ✅ **Zero Pickle dependencies** - fully cloud-compatible

---

## 🎨 Features

### 📊 Executive Overview

- Real-time market KPIs (Total Value, Avg Price, PPSF)
- Key insights from 8-phase analysis
- Interactive market distribution charts

### 🤖 AI Price Predictor

- XGBoost-powered price prediction
- 99.5% accuracy (R² = 0.9950)
- Interactive feature inputs
- Instant predictions with confidence scores

### 🗺️ Market Intelligence

- City-level market share analysis
- Property type distribution
- Price vs Area scatter plots
- Historical trends

### 🏠 Property Explorer

- Interactive property gallery
- High-quality property images
- Click-through to original listings
- Advanced filters (City, Type, Price Range)

### Buyer Personas

- 4 distinct market segments
- Budget-Conscious (60.7%)
- Premium Family (36.7%)
- Ultra-Luxury (2.5%)
- Billionaire Elite (0.1%)

### Investment Advisor

- Strategic recommendations for developers
- Investor insights
- End-user buyer guidance
- Key market metrics

----------

## 🧠 Machine Learning Pipeline

### Model Architecture

```
Raw Data → Cleaning → Feature Engineering → XGBoost → SHAP → Predictions
```

### Feature Engineering

- **Target Encoding**: Neighborhood median price (replaces 800+ dummy variables)
- **Interaction Features**: `area_x_dubai`, `beds_x_dubai` (captures location multipliers)
- **Binary Flags**: City, property type, amenities

### Model Performance

|Metric|Value|
|---|---|
|R² Score|0.9950|
|MAPE|3.0%|
|MAE|AED 194,103|
|Features|41|
|Training Samples|13,634|

### Key Insights (SHAP Analysis)

1. **Location Dominance**: 84% of value driven by location
2. **Area Importance**: 37% SHAP importance
3. **Dubai Multiplier**: 2x premium per sqft vs other emirates
4. **Amenities Crisis**: Negative ROI (-98% to -100%)

------------------

## 📊 Data Source

- **Source**: [Bayut.com](https://www.bayut.com/)
- **Coverage**: 8 UAE Emirates
- **Properties**: 17,042+ active listings
- **Last Updated**: September 2026
- **Fields**: Price, Area, Location, Amenities, Images, URLs

------------

## 🛠️ Tech Stack

### Backend

- **Python 3.12+** - Core language
- **XGBoost 2.0+** - ML model (JSON format)
- **scikit-learn** - Preprocessing & clustering
- **SHAP** - Model explainability
- **SQLAlchemy** - Database ORM
- **psycopg2** - PostgreSQL driver

### Frontend

- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **Pillow** - Image processing

### Infrastructure

- **Supabase** - PostgreSQL database
- **Streamlit Cloud** - Deployment
- **GitHub** - Version control

----------------

## 📈 Project Phases

| Phase | Title                 | Key Deliverable                    |
| ----- | --------------------- | ---------------------------------- |
| 1     | Data Quality          | Isolation Forest outlier detection |
| 2     | Market Overview       | KPIs & macro analysis              |
| 3     | Hedonic Pricing       | Linear regression baseline         |
| 4     | Location Intelligence | Target encoding & interactions     |
| 5     | Amenity Analysis      | SHAP-based ROI calculation         |
| 6     | Advanced ML           | XGBoost + hyperparameter tuning    |
| 7     | Market Segmentation   | K-Means buyer personas             |
| 8     | Executive Insights    | Strategic recommendations          |

----------------------

## 👨‍💻 Author

**Abdullah ahmed saeed**
📧 [My Email](abdullah.ahmed.saeed.alnoubi@gmail.com)  
🔗 [LinkedIn](www.linkedin.com/in/abdullah-ahmed-saeed-alnoubi)  
🐙 [GitHub](https://github.com/abdullahA7med/abdullahA7med)


