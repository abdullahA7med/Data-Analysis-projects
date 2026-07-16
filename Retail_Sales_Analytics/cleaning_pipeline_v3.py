"""
📦 نور للتجارة — Data Cleaning Pipeline النهائي (V3)
🎯 المستوى: Junior — مشروع #1
🛠️ الأدوات: pandas, numpy, re, logging
📅 تم التحديث: 2026-07-07
✅ يتعامل مع: Nulls, Duplicates, Outliers, Future Dates, Invalid DateKey
"""

import pandas as pd
import numpy as np
import re
import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# ============================================
# إعداد الـ Logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cleaning_pipeline_v3.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============================================
# Data Class للتقرير
# ============================================
@dataclass
class CleaningReport:
    """تقرير بنتائج التنظيف"""

    table_name: str
    rows_before: int
    rows_after: int
    nulls_filled: Dict[str, int] = field(default_factory=dict)
    duplicates_removed: int = 0
    modifications: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================
# الـ Pipeline الرئيسي
# ============================================
class DataCleaningPipeline:
    def __init__(self, unit_cost_ratio: float = 0.6):
        self.reports: Dict[str, CleaningReport] = {}
        self.cleaned_data: Dict[str, pd.DataFrame] = {}
        self.unit_cost_ratio = unit_cost_ratio
        self.today = pd.Timestamp(datetime(2025, 6, 30))  # تاريخ نهاية البيانات

    # ============================================================
    # 1. dim_branch — جدول الفروع
    # ============================================================
    def clean_dim_branch(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔄 بدء تنظيف dim_branch...")
        df_clean = df.copy()
        rows_before = len(df_clean)
        modifications = []

        # تحويل التاريخ
        df_clean["OpeningDate"] = pd.to_datetime(
            df_clean["OpeningDate"], errors="coerce"
        )

        # إزالة المسافات الزائدة
        str_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in str_cols:
            df_clean[col] = df_clean[col].str.strip()

        # حذف التكرارات
        dups_before = df_clean["BranchName"].duplicated().sum()
        if dups_before > 0:
            df_clean = df_clean.drop_duplicates(subset=["BranchName"], keep="first")
            modifications.append(f"حذف {dups_before} تكرار في BranchName")

        # حذف الصفوف الفارغة
        null_rows = df_clean.isnull().any(axis=1).sum()
        if null_rows > 0:
            df_clean = df_clean.dropna()
            modifications.append(f"حذف {null_rows} صف فيه null")

        report = CleaningReport(
            table_name="dim_branch",
            rows_before=rows_before,
            rows_after=len(df_clean),
            duplicates_removed=dups_before,
            modifications=modifications if modifications else ["إزالة مسافات زائدة"],
            warnings=[],
        )
        self.reports["dim_branch"] = report
        self.cleaned_data["dim_branch"] = df_clean

        logger.info(f"✅ dim_branch: {rows_before} → {len(df_clean)} صف")
        return df_clean

    # ============================================================
    # 2. dim_date — جدول التواريخ (🔧 مُعدّل)
    # ============================================================
    def clean_dim_date(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔄 بدء تنظيف dim_date...")
        df_clean = df.copy()
        modifications = []
        warnings = []

        # ✅ [FIXED] بناء عمود Date من DateKey لو مفيش Date
        if "Date" not in df_clean.columns and "DateKey" in df_clean.columns:
            logger.info("   ↪️ بناء عمود Date من DateKey")
            start_date = datetime(2024, 1, 1)
            df_clean["Date"] = df_clean["DateKey"].apply(
                lambda x: (
                    start_date + timedelta(days=int(x) - 1) if pd.notna(x) else pd.NaT
                )
            )
            modifications.append("بناء عمود Date من DateKey")

        # التحقق من التواريخ المستقبلية
        if "Date" in df_clean.columns:
            df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")
            future_dates = (df_clean["Date"] > self.today).sum()
            if future_dates > 0:
                warnings.append(f"موجود {future_dates} تاريخ مستقبلي")
                df_clean.loc[df_clean["Date"] > self.today, "Date"] = pd.NaT
                modifications.append(f"حذف {future_dates} تاريخ مستقبلي")

        report = CleaningReport(
            table_name="dim_date",
            rows_before=len(df_clean),
            rows_after=len(df_clean),
            modifications=modifications if modifications else ["الجدول نظيف"],
            warnings=warnings,
        )
        self.reports["dim_date"] = report
        self.cleaned_data["dim_date"] = df_clean

        logger.info(f"✅ dim_date: نظيف ({len(df_clean)} صف)")
        return df_clean

    # ============================================================
    # 3. dim_employee — جدول الموظفين
    # ============================================================
    def clean_dim_employee(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔄 بدء تنظيف dim_employee...")
        df_clean = df.copy()
        rows_before = len(df_clean)
        nulls_filled = {}
        modifications = []
        warnings = []

        # حذف الصفوف بدون BranchKey
        null_branch = df_clean["BranchKey"].isnull().sum()
        if null_branch > 0:
            df_clean = df_clean.dropna(subset=["BranchKey"])
            nulls_filled["BranchKey"] = null_branch
            warnings.append(f"حذف {null_branch} موظف بدون BranchKey")
            modifications.append(f"حذف {null_branch} موظف بدون BranchKey")

        # تحويل BranchKey لـ int
        df_clean["BranchKey"] = df_clean["BranchKey"].astype(int)
        modifications.append("تحويل BranchKey لـ int")

        # تنظيف الأسماء
        df_clean["FullNameAr"] = df_clean["FullNameAr"].apply(self._clean_name)
        modifications.append("إزالة ألقاب من الأسماء")

        # تنظيف أرقام التليفون
        df_clean["PhoneNumber"] = df_clean["PhoneNumber"].apply(self._clean_phone_sa)
        modifications.append("توحيد أرقام التليفون بالصيغة السعودية")

        report = CleaningReport(
            table_name="dim_employee",
            rows_before=rows_before,
            rows_after=len(df_clean),
            nulls_filled=nulls_filled,
            modifications=modifications,
            warnings=warnings,
        )
        self.reports["dim_employee"] = report
        self.cleaned_data["dim_employee"] = df_clean

        logger.info(f"✅ dim_employee: {rows_before} → {len(df_clean)} صف")
        return df_clean

    def _clean_name(self, name):
        if pd.isna(name):
            return name
        name = str(name).strip()
        titles = [
            "المهندسة",
            "المهندس",
            "الأستاذة",
            "الأستاذ",
            "السيدة",
            "السيد",
            "الدكتورة",
            "الدكتور",
            "الآنسة",
        ]
        for title in titles:
            if name.startswith(title):
                return name[len(title) :].strip()
        return name

    def _clean_phone_sa(self, phone):
        if pd.isna(phone):
            return "غير متوفر"
        phone = str(phone).strip()
        digits_only = re.sub(r"[^0-9]", "", phone)
        if digits_only.startswith("00"):
            digits_only = digits_only[2:]
        if digits_only.startswith("05") and len(digits_only) == 10:
            digits_only = "966" + digits_only[1:]
        if len(digits_only) == 12 and digits_only.startswith("9665"):
            return f"+{digits_only[:3]}-{digits_only[3:4]}{digits_only[4:7]}-{digits_only[7:]}"
        return "غير متوفر"

    # ============================================================
    # 4. dim_product — جدول المنتجات
    # ============================================================
    def clean_dim_product(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔄 بدء تنظيف dim_product...")
        df_clean = df.copy()
        rows_before = len(df_clean)
        nulls_filled = {}
        modifications = []
        warnings = []

        # تصحيح الأسعار السالبة
        negative_prices = (df_clean["UnitPrice"] < 0).sum()
        if negative_prices > 0:
            df_clean.loc[df_clean["UnitPrice"] < 0, "UnitPrice"] = df_clean.loc[
                df_clean["UnitPrice"] < 0, "UnitPrice"
            ].abs()
            modifications.append(f"تصحيح {negative_prices} سعر سالب")

        # ملء missing UnitPrice
        null_prices = df_clean["UnitPrice"].isnull().sum()
        if null_prices > 0:
            df_clean["UnitPrice"] = df_clean.groupby("SubCategory")[
                "UnitPrice"
            ].transform(lambda x: x.fillna(x.mean()))
            remaining = df_clean["UnitPrice"].isnull().sum()
            if remaining > 0:
                df_clean["UnitPrice"] = df_clean["UnitPrice"].fillna(
                    df_clean["UnitPrice"].mean()
                )
            nulls_filled["UnitPrice"] = null_prices
            modifications.append(f"ملء {null_prices} missing UnitPrice")

        # تحذير التكرارات
        dup_count = df_clean["ProductName"].duplicated().sum()
        if dup_count > 0:
            warnings.append(
                f"موجود {dup_count} تكرار في ProductName (مختلفين في Supplier)"
            )

        report = CleaningReport(
            table_name="dim_product",
            rows_before=rows_before,
            rows_after=len(df_clean),
            nulls_filled=nulls_filled,
            modifications=modifications if modifications else ["لا يوجد تعديلات"],
            warnings=warnings,
        )
        self.reports["dim_product"] = report
        self.cleaned_data["dim_product"] = df_clean

        logger.info(f"✅ dim_product: {rows_before} → {len(df_clean)} صف")
        return df_clean

    # ============================================================
    # 5. fact_sales — جدول المبيعات (🔧 مُعدّل بشكل كبير)
    # ============================================================
    def clean_fact_sales(
        self,
        df: pd.DataFrame,
        dim_product: Optional[pd.DataFrame] = None,
        dim_date: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        logger.info("🔄 بدء تنظيف fact_sales...")
        df_clean = df.copy()
        rows_before = len(df_clean)
        nulls_filled = {}
        modifications = []
        warnings = []

        # ✅ [NEW] حذف Duplicates
        dups_before = df_clean.duplicated().sum()
        if dups_before > 0:
            df_clean = df_clean.drop_duplicates()
            modifications.append(f"حذف {dups_before} صف مكرر")

        # ✅ [NEW] حذف DateKey غير صالح (> max في dim_date)
        if dim_date is not None and "DateKey" in dim_date.columns:
            max_valid_datekey = dim_date["DateKey"].max()
            invalid_datekey = df_clean["DateKey"] > max_valid_datekey
            invalid_count = invalid_datekey.sum()
            if invalid_count > 0:
                df_clean = df_clean[~invalid_datekey].reset_index(drop=True)
                modifications.append(
                    f"حذف {invalid_count} صف بـ DateKey > {max_valid_datekey}"
                )

        # ✅ [NEW] حذف Nulls في DateKey (بدل forward fill)
        null_dates = df_clean["DateKey"].isnull().sum()
        if null_dates > 0:
            df_clean = df_clean.dropna(subset=["DateKey"])
            nulls_filled["DateKey"] = null_dates
            modifications.append(f"حذف {null_dates} صف بدون DateKey")

        # تحويل DateKey لـ int
        df_clean["DateKey"] = df_clean["DateKey"].astype(int)

        # ✅ [NEW] بناء عمود Date من DateKey (للربط مع Calendar)
        if dim_date is not None and "Date" in dim_date.columns:
            date_map = dim_date.set_index("DateKey")["Date"].to_dict()
            df_clean["Date"] = df_clean["DateKey"].map(date_map)
            modifications.append("بناء عمود Date من DateKey عبر dim_date")

        # التحقق من التواريخ المستقبلية
        if "Date" in df_clean.columns:
            df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")
            future_mask = df_clean["Date"] > self.today
            future_count = future_mask.sum()
            if future_count > 0:
                df_clean = df_clean[~future_mask].reset_index(drop=True)
                modifications.append(f"حذف {future_count} صف بتواريخ مستقبلية")

        # إزالة المسافات في OrderStatus
        df_clean["OrderStatus"] = df_clean["OrderStatus"].str.strip()
        modifications.append("إزالة مسافات زائدة من OrderStatus")

        # إصلاح إشارة Quantity
        df_clean = self._fix_quantity_signs(df_clean)
        modifications.append("إصلاح إشارات Quantity حسب OrderStatus")

        # إعادة حساب القيم المالية
        df_clean = self._recalculate_amounts(df_clean, dim_product)
        modifications.append("إعادة حساب TotalAmount, CostAmount, ProfitAmount")

        report = CleaningReport(
            table_name="fact_sales",
            rows_before=rows_before,
            rows_after=len(df_clean),
            nulls_filled=nulls_filled,
            duplicates_removed=dups_before,
            modifications=modifications,
            warnings=warnings,
        )
        self.reports["fact_sales"] = report
        self.cleaned_data["fact_sales"] = df_clean

        logger.info(f"✅ fact_sales: {rows_before} → {len(df_clean)} صف")
        return df_clean

    def _fix_quantity_signs(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        mask_completed = (df["OrderStatus"] == "مكتمل") & (df["Quantity"] < 0)
        if mask_completed.sum() > 0:
            df.loc[mask_completed, "Quantity"] = df.loc[
                mask_completed, "Quantity"
            ].abs()
        mask_cancelled = df["OrderStatus"].isin(["ملغي", "مسترجع"]) & (
            df["Quantity"] > 0
        )
        if mask_cancelled.sum() > 0:
            df.loc[mask_cancelled, "Quantity"] = -df.loc[
                mask_cancelled, "Quantity"
            ].abs()
        return df

    def _recalculate_amounts(
        self, df: pd.DataFrame, dim_product: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        df = df.copy()
        if dim_product is not None and "UnitCost" in dim_product.columns:
            df = df.merge(
                dim_product[["ProductKey", "UnitCost"]],
                on="ProductKey",
                how="left",
                suffixes=("", "_from_dim"),
            )
            if "UnitCost_from_dim" in df.columns:
                df["UnitCost"] = df["UnitCost_from_dim"].fillna(
                    df["UnitPrice"] * self.unit_cost_ratio
                )
                df = df.drop(columns=["UnitCost_from_dim"])
        else:
            if "UnitCost" not in df.columns:
                df["UnitCost"] = df["UnitPrice"] * self.unit_cost_ratio

        df["TotalAmount"] = (
            df["Quantity"].abs() * df["UnitPrice"] * (1 - df["DiscountRate"])
        )
        mask_negative = df["OrderStatus"].isin(["ملغي", "مسترجع"])
        df.loc[mask_negative, "TotalAmount"] = -df.loc[
            mask_negative, "TotalAmount"
        ].abs()
        df["CostAmount"] = df["Quantity"].abs() * df["UnitCost"]
        df.loc[mask_negative, "CostAmount"] = -df.loc[mask_negative, "CostAmount"].abs()
        df["ProfitAmount"] = df["TotalAmount"] - df["CostAmount"]
        return df

    # ============================================================
    # تشغيل الـ Pipeline
    # ============================================================
    def run_pipeline(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        logger.info("=" * 60)
        logger.info("🚀 بدء تشغيل Data Cleaning Pipeline V3")
        logger.info("=" * 60)

        # تنظيف dim_date و dim_product أولاً
        if "dim_date" in data_dict:
            self.clean_dim_date(data_dict["dim_date"])
        if "dim_product" in data_dict:
            self.clean_dim_product(data_dict["dim_product"])

        # تنظيف dim_branch و dim_employee
        cleaners = {
            "dim_branch": self.clean_dim_branch,
            "dim_employee": self.clean_dim_employee,
        }
        for table_name, df in data_dict.items():
            if table_name in cleaners:
                cleaners[table_name](df)

        # تنظيف fact_sales (آخر شيء)
        if "fact_sales" in data_dict:
            dim_prod = self.cleaned_data.get("dim_product")
            dim_dt = self.cleaned_data.get("dim_date")
            self.clean_fact_sales(
                data_dict["fact_sales"], dim_product=dim_prod, dim_date=dim_dt
            )

        logger.info("=" * 60)
        logger.info("✅ انتهى الـ Pipeline بنجاح!")
        logger.info("=" * 60)
        return self.cleaned_data

    def get_report(self) -> str:
        lines = ["\n" + "=" * 70, "📊 DATA CLEANING REPORT V3", "=" * 70]
        for name, rep in self.reports.items():
            lines.extend(
                [
                    f"\n📁 {rep.table_name}",
                    f"   📊 الصفوف: {rep.rows_before:,} → {rep.rows_after:,}",
                    f"   🗑️ التكرارات المحذوفة: {rep.duplicates_removed:,}",
                    f"   📝 Nulls تم ملؤها: {rep.nulls_filled}",
                    f"   🔧 التعديلات:",
                ]
            )
            for mod in rep.modifications:
                lines.append(f"      • {mod}")
            if rep.warnings:
                lines.append(f"   ⚠️ التحذيرات:")
                for warn in rep.warnings:
                    lines.append(f"      • {warn}")
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)

    def export_cleaned(self, output_dir: str = "cleaned_data_v3"):
        os.makedirs(output_dir, exist_ok=True)
        saved = []
        for name, df in self.cleaned_data.items():
            path = os.path.join(output_dir, f"cleaned_{name}.csv")
            df.to_csv(path, index=False, encoding="utf-8-sig")
            saved.append(path)
            logger.info(f"💾 تم حفظ {path}")
        return saved


# ============================================================
# الاستخدام
# ============================================================
if __name__ == "__main__":
    data = {
        "dim_branch": pd.read_csv("dataset/dim_branch.csv"),
        "dim_date": pd.read_csv("dataset/dim_date.csv"),
        "dim_employee": pd.read_csv("dataset/dim_employee.csv"),
        "dim_product": pd.read_csv("dataset/dim_product.csv"),
        "fact_sales": pd.read_csv("dataset/fact_sales.csv"),
    }

    pipeline = DataCleaningPipeline(unit_cost_ratio=0.6)
    cleaned = pipeline.run_pipeline(data)
    print(pipeline.get_report())
    saved = pipeline.export_cleaned("cleaned_data_v3")
    print(f"\n📁 تم حفظ {len(saved)} ملف")
