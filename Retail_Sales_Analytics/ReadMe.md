# 📊 Retail Store Analytics Dashboard | نور للتجارة

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-yellow.svg?style=flat-square&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Cleaning-orange.svg?style=flat-square&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success.svg?style=flat-square)

**A comprehensive business intelligence solution for retail store performance analysis**

[ Live Demo](#) | [📱 Screenshots](#screenshots) | [🔧 Data Cleaning](#data-cleaning-pipeline)

</div>
---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Business Problem](#business-problem)
- [Solution Architecture](#solution-architecture)
- [Key Features](#key-features)
- [Dashboard Pages](#dashboard-pages)
- [Data Cleaning Pipeline](#data-cleaning-pipeline)
- [Technologies Used](#technologies-used)
- [Key Metrics & Insights](#key-metrics--insights)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)

---

## 🎯 Project Overview

**Retail Store Analytics Dashboard** is an end-to-end business intelligence solution developed for **نور للتجارة** (Noor Trading Company), a multi-branch retail organization. This project transforms raw sales data into actionable insights through interactive visualizations, comprehensive KPI tracking, and advanced analytics.

### Project Scope
- **Data Volume**: 74.9M SAR total revenue analysis
- **Time Period**: January 2024 - June 2025 (18 months)
- **Branches**: 5 major branches across Saudi Arabia
- **Employees**: Multi-level performance tracking
- **Products**: Category-wise analysis with return rate monitoring

---

## 💼 Business Problem

### Challenges Faced

1. **Fragmented Data Sources**
   - Sales data scattered across 5 separate files (4 dimension tables + 1 fact table)
   - Inconsistent data formats and naming conventions
   - No unified view of business performance

2. **Data Quality Issues**
   - **3,400 missing date entries** in sales transactions
   - **200 negative quantity values** requiring status-based correction
   - **100 future dates** that needed validation
   - **Duplicate branch entries** (فرع الرياض appeared twice with spacing variations)
   - **54 duplicate products** with different supplier information
   - **16 missing product prices** requiring category-based imputation
   - **3 employees** without branch assignments
   - **Inconsistent phone number formats** across employee records

3. **Lack of Performance Visibility**
   - No real-time KPI monitoring
   - Inability to track month-over-month growth trends
   - Missing branch-wise performance comparison
   - No employee target achievement tracking

4. **Decision-Making Gaps**
   - Difficulty identifying seasonal patterns
   - No visibility into product category profitability
   - Inability to monitor profit margins by branch
   - Lack of trend analysis for strategic planning

---



##  Key Features

### 📊 Interactive Visualizations
- **6 Comprehensive Dashboard Pages** with seamless navigation
- **Dark Theme UI** with Saudi national colors (Green/Gold/Red)
- **Responsive Design** optimized for desktop and mobile
- **Bookmark-based Filters** for dynamic data exploration
- **Multi-language Support** (Arabic/English)

###  Advanced Analytics
- **Time Series Analysis**: 18-month trend tracking with seasonal pattern detection
- **MoM Growth Calculation**: Automated month-over-month performance tracking
- **Target vs Actual**: Combo charts showing achievement percentages
- **Profit Margin Analysis**: Branch-wise and category-wise profitability
- **Return Rate Monitoring**: Category-level quality metrics
- **Employee Performance Ranking**: Revenue-based ranking with AOV metrics

### 🎨 Design System
- **Color Palette**: 
  - Background: `#1E1E1E` (Dark Theme)
  - Cards: `#2D2D2D` with `#3D3D3D` borders
  - Positive Metrics: `#006C35` (Saudi Green)
  - Negative Metrics: `#C41E3A` (Alert Red)
  - Accent: `#C5A572` (Gold)
- **Typography**: Cairo/Tajawal Arabic fonts
- **Components**: Reusable KPI Cards, Chart Containers, Slicers

---

## 📱 Dashboard Pages

### 1️⃣ Home Page
**Purpose**: Central navigation hub
- **Features**:
  - 5 navigation buttons with custom icons
  - Clean, minimal design with company branding
  - Quick access to all dashboard sections

### 2️⃣ Overview Page
**Purpose**: Executive summary of business performance
- **KPI Cards**:
  - **Profit Margin**: 15.5%
  - **Total Revenue**: $74.92M
  - **MoM Growth**: 3.59%
  - **Total Profit**: $11.6M
- **Visualizations**:
  - Area chart showing monthly revenue trends (Jan 2024 - Jun 2025)
  - Clear identification of seasonal peaks and valleys

### 3️⃣ Branch Analysis Page
**Purpose**: Multi-dimensional branch performance comparison
- **Visualizations**:
  - **Multi-line Chart**: Revenue by YearMonth and BranchName
  - **Donut Chart**: Profit Margin % by Branch (5 branches: 19-20% each)
  - **Bar Chart**: Total Revenue by BranchName (الرياض leading)
  - **Bar Chart**: Target Achievement % by Branch
  - **Data Table**: Detailed branch metrics (Total Revenue, Total Profit, Target %)
- **Key Insight**: فرع الرياض (Riyadh Branch) shows highest revenue but moderate profit margin

### 4️⃣ Product Analysis Page
**Purpose**: Product and category performance analytics
- **Visualizations**:
  - **Horizontal Bar Chart**: Total Revenue by ProductName (Top 12 products)
  - **Bar Chart**: Return Rate % by Category (5 categories: 19-21% range)
  - **Horizontal Bar Chart**: Total Profit by Category
  - **Donut Chart**: Total Revenue by Category (5 categories with 19-22% distribution)
- **Categories Tracked**:
  - منزلية (Home)
  - إلكترونيات (Electronics)
  - استهلاكية (Consumer Goods)
  - عناية شخصية (Personal Care)
  - ملابس (Clothing)

### 5️ Employee Performance Page
**Purpose**: Sales team performance and target tracking
- **Visualizations**:
  - **Horizontal Bar Chart**: Total Revenue by FullNameAr (Top employees)
  - **Horizontal Bar Chart**: Target Achievement % by Employee
  - **Data Table**: BranchName, FullNameAr, Employee Rank, Total Revenue
  - **Horizontal Bar Chart**: AOV (Average Order Value) by Employee
- **Key Metrics**:
  - Employee ranking system
  - Individual target achievement percentages
  - Branch-wise employee distribution

### 6️ Time Analysis Page
**Purpose**: Temporal patterns and seasonality analysis
- **Visualizations**:
  - **Area Chart**: Total Revenue by YearMonth (18-month trend)
  - **Bar Chart**: Total Revenue by MonthNameAr (Arabic month names)
  - **Combo Chart**: Total Revenue (Bars) + Target Achievement % (Line) by YearMonth
  - **Area Chart**: MoM Growth % by YearMonth (volatility tracking)
- **Insights**:
  - Clear seasonal patterns (peaks in Apr 2024, Mar 2025)
  - MoM growth volatility ranging from -10% to +15%
  - Target achievement consistency monitoring

---

## 🔧 Data Cleaning Pipeline

### Overview
Developed a **production-grade ETL pipeline** using Python (pandas, numpy) to address critical data quality issues across 5 source tables.

### Pipeline Architecture

```python
DataCleaningPipeline (V3)
├── dim_branch Cleaning
│   ├── Spacing normalization
│   ├── Duplicate removal (1 duplicate: فرع الرياض)
│   ├── Date parsing
│   ── Null row elimination
│
── dim_date Cleaning
│   ├── Date column construction from DateKey
│   ├── Future date detection & removal
│   ── Date format validation
│
├── dim_employee Cleaning
│   ├── BranchKey null handling (3 rows deleted)
│   ├── Job title removal from names (Regex-based)
│   ├── Phone number standardization (Saudi format)
│   └── Data type conversion (BranchKey → int)
│
├── dim_product Cleaning
│   ├── Negative price correction
│   ├── Missing price imputation (SubCategory mean)
│   ├── Duplicate flagging (54 products kept - different suppliers)
│   └── Price validation
│
└── fact_sales Cleaning
    ├── Duplicate removal
    ├── Invalid DateKey filtering
    ├── Null DateKey deletion (3,400 rows)
    ├── Date column mapping from dim_date
    ├── Future date removal (100 rows)
    ├── Quantity sign correction (200 rows fixed)
    │   ├── Completed orders: negative → positive
    │   └── Cancelled/Returned orders: positive → negative
    ├── Financial amount recalculation
    │   ├── TotalAmount = Quantity × UnitPrice × (1 - DiscountRate)
    │   ├── CostAmount = Quantity × UnitCost
    │   └── ProfitAmount = TotalAmount - CostAmount
    └── OrderStatus normalization
```

### Pipeline Features

✅ **Automated Logging**: Track every transformation with timestamps  
✅ **Data Validation**: Type checking, range validation, referential integrity  
✅ **Error Recovery**: Graceful handling of missing data with fallback strategies  
✅ **Performance Optimization**: Vectorized operations, efficient memory usage  
✅ **Reporting**: Detailed cleaning report with before/after statistics  
✅ **Export Functionality**: UTF-8 encoded CSV export for Power BI import

-----
---

## 🛠️ Technologies Used

### Data Processing

- **Python 3.8+**: Core programming language
- **pandas**: Data manipulation and ETL
- **numpy**: Numerical operations
- **re (regex)**: Pattern matching for data cleaning

### Visualization & BI

- **Power BI Desktop**: Interactive dashboard development
- **DAX**: Advanced measure calculations
- **Power Query**: Data transformation (supplementary)

### Design & Prototyping

- **Figma**: UI/UX design and prototyping
- **Design System**: Dark theme with Saudi national colors

### Version Control

- **Git**: Source code management
- **GitHub**: Repository hosting


----
## Key Metrics & Insights

### Business Performance (Jun 2024 - Jun 2025)

|Metric|Value|Trend|
|---|---|---|
|**Total Revenue**|74,915,149.30 SAR|+3.59% MoM|
|**Total Profit**|11,648,598.30 SAR|Stable|
|**Profit Margin**|15.5%|Healthy|
|**Average Order Value**|Variable by employee|-|

### Branch Performance Highlights

**Top Performer**: فرع الرياض (Riyadh Branch)

- Highest revenue generation
- Target achievement: 7.55%
- Profit margin: 20.34%

**Areas for Improvement**:

- فرع المدينة (Madinah Branch): Lower revenue, needs marketing focus
- Profit margins relatively uniform (19-20%) across branches

### Product Category Insights

**Revenue Distribution**:

- Balanced across 5 categories (19-22% each)
- No single category dependency
- Diversified product portfolio

**Quality Metrics**:

- Return rates consistent (19-21%) across categories
- Indicates uniform product quality standards

### Temporal Patterns

**Seasonal Peaks**:

- **April 2024**: Major revenue spike (seasonal demand)
- **March 2025**: Secondary peak
- **July 2024**: Lowest point (summer slowdown)

**Growth Volatility**:

- MoM growth ranges: -10% to +15%
- Indicates need for inventory optimization
- Opportunity for demand forecasting


-------
retail-store-analytics/
├── 📁 dataset/
│   ├── dim_branch.csv          # Branch dimension
│   ├── dim_date.csv            # Date dimension
│   ├── dim_employee.csv        # Employee dimension
│   ├── dim_product.csv         # Product dimension
│   └── fact_sales.csv          # Sales fact table
│
├──  cleaned_data_v3/
│   ├── cleaned_dim_branch.csv
│   ├── cleaned_dim_date.csv
│   ├── cleaned_dim_employee.csv
│   ├── cleaned_dim_product.csv
│   └── cleaned_fact_sales.csv
│
── 📁 assets/
│   ├── home.png                # Home page screenshot
│   ├── OverView.png            # Overview page
│   ├── Branch.png              # Branch analysis
│   ├── Product.png             # Product analysis
│   ├── Employee.png            # Employee performance
│   └── Time.png                # Time analysis
│
├── 🔧 cleaning_pipeline_v3.py  # Main ETL script
├── 📊 Retail_Store_Analytics.pbix  # Power BI report
├──  README.md                # This file
├── 📄 data_cleaning_notes.md   # Data quality documentation
└──  requirements.txt         # Python dependencies



-----
## 📄 License

This project is open-source and available for educational purposes.

## 👨‍💻 Author

**Abdullah Ahmed**  
Data Analyst | Business Intelligence Developer