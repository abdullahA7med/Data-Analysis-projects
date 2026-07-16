"""
📦 نور للتجارة — توليد بيانات المشروع الأول (Retail Sales Analytics)
🎯 المستوى: Junior — مشروع #1
🛠️ الأدوات: pandas, numpy, faker
📅 البيانات: 2024-01-01 إلى 2025-06-30 (18 شهر)
📊 الحجم: ~50,000 صف (طلبات)
📝 لغة الأعمدة: عربية (مع بعض الإنجليزي للـ Keys)
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# تهيئة Faker بالعربي
fake = Faker(['ar_SA'])
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ============================================
# ⚙️ الإعدادات العامة
# ============================================
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 6, 30)
N_ORDERS = 50000
N_PRODUCTS = 800
N_EMPLOYEES = 120

# ============================================
# 🏪 1. dim_branch — جدول الفروع
# ============================================
print("⏳ جاري توليد dim_branch...")

branches_data = {
    'BranchKey': [1, 2, 3, 4, 5],
    'BranchName': ['فرع الرياض', 'فرع جدة', 'فرع الدمام', 'فرع مكة', 'فرع المدينة'],
    'City': ['الرياض', 'جدة', 'الدمام', 'مكة المكرمة', 'المدينة المنورة'],
    'Region': ['الوسطى', 'الغربية', 'الشرقية', 'الغربية', 'الغربية'],
    'ManagerName': ['خالد العتيبي', 'فهد الزهراني', 'سعد القحطاني', 'ناصر الشهراني', 'بندر الدوسري'],
    'OpeningDate': [datetime(2019, 3, 15), datetime(2020, 7, 1),
                    datetime(2021, 1, 10), datetime(2022, 5, 20), datetime(2023, 9, 1)],
    'MonthlyTarget': [800000, 700000, 600000, 500000, 400000],  # ريال
    'SquareMeters': [450, 380, 320, 280, 250]
}

dim_branch = pd.DataFrame(branches_data)

# 💥 تلويث: إضافة فرع مكرر باسم مختلف (لاختبار التنظيف)
duplicate_branch = pd.DataFrame({
    'BranchKey': [6],
    'BranchName': ['فرع الرياض '],  # مسافة في النهاية!
    'City': ['الرياض'],
    'Region': ['الوسطى'],
    'ManagerName': ['خالد العتيبي'],
    'OpeningDate': [datetime(2019, 3, 15)],
    'MonthlyTarget': [800000],
    'SquareMeters': [450]
})
dim_branch = pd.concat([dim_branch, duplicate_branch], ignore_index=True)

print(f"✅ dim_branch: {len(dim_branch)} صف")

# ============================================
# 👤 2. dim_employee — جدول الموظفين
# ============================================
print("⏳ جاري توليد dim_employee...")

job_titles = ['مندوب مبيعات', 'كاشير', 'مدير فرع', 'مشرف مبيعات', 'أخصائي مخزون']
branches_for_emp = [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5]  # توزيع غير متساوٍ

employees = []
for i in range(1, N_EMPLOYEES + 1):
    branch_key = random.choice(branches_for_emp)
    hire_date = fake.date_between(START_DATE - timedelta(days=730), END_DATE - timedelta(days=30))

    # 10% من الموظفين "مندوب مبيعات" (هم اللي عندهم Targets)
    if random.random() < 0.10:
        job = 'مندوب مبيعات'
        target = random.randint(30000, 80000)
    else:
        job = random.choice(job_titles)
        target = 0

    employees.append({
        'EmployeeKey': i,
        'FullNameAr': fake.name(),
        'JobTitle': job,
        'BranchKey': branch_key,
        'HireDate': hire_date,
        'MonthlyTarget': target,
        'PhoneNumber': fake.phone_number(),
        'Email': fake.email()
    })

dim_employee = pd.DataFrame(employees)

# 💥 تلويث: إضافة موظفين مكررين (5%)
n_duplicates = int(N_EMPLOYEES * 0.05)
dup_employees = dim_employee.sample(n=n_duplicates, random_state=42).copy()
dup_employees['EmployeeKey'] = range(N_EMPLOYEES + 1, N_EMPLOYEES + n_duplicates + 1)
dim_employee = pd.concat([dim_employee, dup_employees], ignore_index=True)

# 💥 تلويث: 3% من الموظفين بدون BranchKey (Null)
null_indices = dim_employee.sample(n=int(len(dim_employee) * 0.03), random_state=42).index
dim_employee.loc[null_indices, 'BranchKey'] = np.nan

print(f"✅ dim_employee: {len(dim_employee)} صف")

# ============================================
# 📦 3. dim_product — جدول المنتجات
# ============================================
print("⏳ جاري توليد dim_product...")

categories = {
    'إلكترونيات': ['هواتف ذكية', 'لابتوبات', 'سماعات', 'شواحن', 'كيابل'],
    'استهلاكية': ['مياه', 'عصائر', 'مكسرات', 'شوكولاتة', 'بسكويت'],
    'منزلية': ['أدوات مطبخ', 'منظفات', 'ورقيات', 'بلاستيكيات', 'منظمات'],
    'عناية شخصية': ['شامبو', 'صابون', 'معجون أسنان', 'كريمات', 'مستحضرات'],
    'ملابس': ['تيشيرتات', 'بناطيل', 'أحذية', 'إكسسوارات', 'جوارب']
}

products = []
product_key = 1
for cat, subcats in categories.items():
    for subcat in subcats:
        n_products_in_subcat = N_PRODUCTS // len([s for subs in categories.values() for s in subs])
        for _ in range(n_products_in_subcat):
            cost = random.randint(5, 500)
            margin = random.uniform(0.15, 0.45)
            price = round(cost * (1 + margin), 2)

            products.append({
                'ProductKey': product_key,
                'ProductName': f"{fake.word().capitalize()} {subcat}",
                'Category': cat,
                'SubCategory': subcat,
                'UnitCost': cost,
                'UnitPrice': price,
                'Supplier': fake.company(),
                'StockQuantity': random.randint(0, 500),
                'ReorderPoint': random.randint(20, 100),
                'IsActive': random.random() > 0.05  # 5% غير نشط
            })
            product_key += 1

dim_product = pd.DataFrame(products)

# 💥 تلويث: 2% من المنتجات بدون سعر
null_price_indices = dim_product.sample(n=int(len(dim_product) * 0.02), random_state=42).index
dim_product.loc[null_price_indices, 'UnitPrice'] = np.nan

# 💥 تلويث: بعض المنتجات بسعر سالب (خطأ!)
negative_indices = dim_product.sample(n=5, random_state=42).index
dim_product.loc[negative_indices, 'UnitPrice'] = dim_product.loc[negative_indices, 'UnitPrice'] * -1

print(f"✅ dim_product: {len(dim_product)} صف")

# ============================================
# 📅 4. dim_date — جدول التواريخ
# ============================================
print("⏳ جاري توليد dim_date...")

date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='D')

# تعريف أسماء الأشهر والأيام
month_names = {1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 5: 'مايو', 6: 'يونيو',
               7: 'يوليو', 8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'}
day_names = {0: 'الإثنين', 1: 'الثلاثاء', 2: 'الأربعاء', 3: 'الخميس',
             4: 'الجمعة', 5: 'السبت', 6: 'الأحد'}

# إنشاء DataFrame بشكل صحيح — كل عمود بنفس طول date_range
dim_date = pd.DataFrame({
    'DateKey': range(1, len(date_range) + 1),
    'Date': date_range,
    'Year': date_range.year,
    'Quarter': date_range.quarter,
    'Month': date_range.month,
    'Day': date_range.day,
    'MonthNameAr': [month_names[m] for m in date_range.month],
    'DayNameAr': [day_names[d] for d in date_range.dayofweek],
    'IsWeekend': [d in [4, 5] for d in date_range.dayofweek],  # الجمعة والسبت
    'IsHoliday': [(m in [4, 9] and d in [1, 2, 3]) for m, d in zip(date_range.month, date_range.day)]  # عيد فطر وعيد أضحى (تقريبي)
})

print(f"✅ dim_date: {len(dim_date)} صف")

# ============================================
# 💰 5. fact_sales — جدول المبيعات (Fact Table)
# ============================================
print("⏳ جاري توليد fact_sales...")

sales = []
active_products = dim_product[dim_product['IsActive'] == True]['ProductKey'].tolist()

# 🔧 FIX: Pre-compute valid sales employees per branch to avoid complex list comprehension
# Get all sales reps with valid (non-null) BranchKey
sales_emp_df = dim_employee[
    (dim_employee['JobTitle'] == 'مندوب مبيعات') & 
    (dim_employee['BranchKey'].notna())
][['EmployeeKey', 'BranchKey']].copy()

# Create a dictionary: branch_key -> list of employee_keys
branch_to_employees = {}
for bk in [1, 2, 3, 4, 5]:
    branch_to_employees[bk] = sales_emp_df[sales_emp_df['BranchKey'] == bk]['EmployeeKey'].tolist()

# Fallback: all sales employees (if a branch has no sales reps)
all_sales_employees = sales_emp_df['EmployeeKey'].tolist()

# Seasonality: ذروة في رمضان (شهر 3) وعيد الفطر (شهر 4) والعروض (شهر 11)
def get_seasonality_factor(date):
    month = date.month
    if month == 3:  # رمضان
        return 1.4
    elif month == 4:  # عيد الفطر
        return 1.3
    elif month == 11:  # البلاك فرايدي / العروض
        return 1.2
    elif month in [6, 7, 8]:  # الصيف (بطء)
        return 0.7
    else:
        return 1.0

for i in range(1, N_ORDERS + 1):
    # تاريخ عشوائي مع Seasonality
    base_date = fake.date_between(START_DATE, END_DATE)
    season_factor = get_seasonality_factor(base_date)

    # Branch (مع تفضيل الرياض)
    branch_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
    branch_key = random.choices([1, 2, 3, 4, 5], weights=branch_weights)[0]

    # Product
    product_key = random.choice(active_products)
    product = dim_product[dim_product['ProductKey'] == product_key].iloc[0]

    # 🔧 FIX: Employee assignment using pre-computed mapping
    branch_employees = branch_to_employees.get(branch_key, [])
    if branch_employees:
        employee_key = random.choice(branch_employees)
    else:
        # Fallback if branch has no sales reps
        employee_key = random.choice(all_sales_employees)

    # Quantity مع Seasonality
    base_qty = random.randint(1, 10)
    quantity = max(1, int(base_qty * season_factor))

    # Price مع Discount
    unit_price = product['UnitPrice'] if pd.notna(product['UnitPrice']) else 50
    discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20])  # 50% بدون خصم
    final_price = round(unit_price * (1 - discount), 2)

    total_amount = round(quantity * final_price, 2)
    cost_amount = round(quantity * product['UnitCost'], 2)
    profit_amount = round(total_amount - cost_amount, 2)

    # Payment Method
    payment_methods = ['نقدي', 'بطاقة', 'مدى', 'أبل باي', 'تمارا']
    payment_weights = [0.20, 0.30, 0.25, 0.15, 0.10]

    sales.append({
        'SaleKey': i,
        'DateKey': dim_date[dim_date['Date'] == pd.Timestamp(base_date)]['DateKey'].values[0],
        'ProductKey': product_key,
        'BranchKey': branch_key,
        'EmployeeKey': employee_key,
        'Quantity': quantity,
        'UnitPrice': unit_price,
        'DiscountRate': discount,
        'TotalAmount': total_amount,
        'CostAmount': cost_amount,
        'ProfitAmount': profit_amount,
        'OrderStatus': random.choices(['مكتمل', 'مكتمل', 'مكتمل', 'مكتمل', 'مكتمل',
                                       'مسترجع', 'مسترجع', 'ملغي'],
                                      weights=[0.85, 0.85, 0.85, 0.85, 0.85, 0.05, 0.05, 0.05])[0],
        'PaymentMethod': random.choices(payment_methods, weights=payment_weights)[0]
    })

fact_sales = pd.DataFrame(sales)

# 💥 تلويث: 5% من الطلبات بدون تاريخ
null_date_indices = fact_sales.sample(n=int(N_ORDERS * 0.05), random_state=42).index
fact_sales.loc[null_date_indices, 'DateKey'] = np.nan

# 💥 تلويث: تواريخ مستقبلية (خطأ!)
future_indices = fact_sales.sample(n=50, random_state=42).index
fact_sales.loc[future_indices, 'DateKey'] = len(dim_date) + random.randint(1, 100)

# 💥 تلويث: Outliers — طلبات بقيم خيالية (1%)
outlier_indices = fact_sales.sample(n=int(N_ORDERS * 0.01), random_state=42).index
fact_sales.loc[outlier_indices, 'TotalAmount'] = fact_sales.loc[outlier_indices, 'TotalAmount'] * random.uniform(10, 50)

# 💥 تلويث: قيم سالبة في الكمية (Returns غير موضحة)
negative_qty_indices = fact_sales.sample(n=100, random_state=42).index
fact_sales.loc[negative_qty_indices, 'Quantity'] = fact_sales.loc[negative_qty_indices, 'Quantity'] * -1

# 💥 تلويث: Duplicates (2%)
dup_sales = fact_sales.sample(n=int(N_ORDERS * 0.02), random_state=42).copy()
dup_sales['SaleKey'] = range(N_ORDERS + 1, N_ORDERS + len(dup_sales) + 1)
fact_sales = pd.concat([fact_sales, dup_sales], ignore_index=True)

print(f"✅ fact_sales: {len(fact_sales)} صف")

# ============================================
# 💾 حفظ الملفات
# ============================================
print("\n💾 جاري حفظ الملفات...")

dim_branch.to_csv('dim_branch.csv', index=False, encoding='utf-8-sig')
dim_employee.to_csv('dim_employee.csv', index=False, encoding='utf-8-sig')
dim_product.to_csv('dim_product.csv', index=False, encoding='utf-8-sig')
dim_date.to_csv('dim_date.csv', index=False, encoding='utf-8-sig')
fact_sales.to_csv('fact_sales.csv', index=False, encoding='utf-8-sig')

# ============================================
# 📊 ملخص البيانات
# ============================================
print("\n" + "="*60)
print("📊 ملخص البيانات النهائي")
print("="*60)

for name, df in [('dim_branch', dim_branch), ('dim_employee', dim_employee),
                 ('dim_product', dim_product), ('dim_date', dim_date), ('fact_sales', fact_sales)]:
    print(f"\n📁 {name}: {len(df)} صف × {len(df.columns)} عمود")
    print(f"   القيم المفقودة: {df.isnull().sum().sum()}")
    print(f"   الصفوف المكررة: {df.duplicated().sum()}")

print("\n" + "="*60)
print("✅ تم توليد البيانات بنجاح!")
print("📁 الملفات المحفوظة:")
print("   • dim_branch.csv")
print("   • dim_employee.csv")
print("   • dim_product.csv")
print("   • dim_date.csv")
print("   • fact_sales.csv")
print("="*60)