"""
🏢 Bayut Real Estate Analytics - Ultimate Cleaning Pipeline v5.0
================================================================
النسخة النهائية - تتضمن جميع الأعمدة بما فيها property_img
"""

import pandas as pd
import numpy as np
import re
import logging
import os
import warnings
import psycopg2
from psycopg2.extras import execute_values
from sklearn.impute import KNNImputer
from typing import Dict, List

# إخفاء التحذيرات غير المهمة
warnings.filterwarnings('ignore', category=UserWarning)

# ==========================================
# 🎨 إعدادات الـ Logging
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class BayutDataCleaner:
    """محرك التنظيف المتقدم"""
    
    def __init__(self):
        logger.info(" Initializing BayutDataCleaner v5.0...")
        
        # 1. قاموس المدن (مُحسّن للأداء)
        self.city_mapping = {
            'Dubai': r'\b(dubai|jvc|jumeirah village|jbr|jlt|marina|downtown|business bay|dso|dip|dubailand|barsha|tecom|internet city|media city|palm|deira|karama|bur dubai|mirdif|al quoz|discovery gardens|international city|sports city|motor city|arabian ranches|springs|meadows|lakes|greens|views|emirates hills|creek harbour|mbr city|tilal al ghaf|damac hills|town square|bluewaters|city walk|la mer|al furjan|dubai south|expo city|dubai hills|sobha|meydan)\b',
            'Abu Dhabi': r'\b(abu dhabi|yas|saadiyat|reem|masdar|khalifa city|corniche|tourist club|al mushrif|al bateen|al nahyan|al wathba|al shamkha|al raha|al reef|al ghadeer|al falah|al samha|al mariya|al maymoun|al bandar|al muneera|shams|najmat|sky tower|ocean heights|marina square|gate towers|al maha|etihad|nation towers|sowwah|al maryah|galleria|lulu island|nurai)\b',
            'Sharjah': r'\b(sharjah|aljada|muwaileh|al majaz|al khan|al nahda|al qasimia|al rolla|al taawun|al yarmook|al zahra|al jazeera|al nouf|al zahia|tilal city|university city|waterfront city|nasma|massar|mleiha|khorfakkan|kalba|dibba|al hamriyah|al dhaid)\b',
            'Ajman': r'\b(ajman|al rashidiya|al hamidiya|al nuaimiya|al jurf|al rawda|al bustan|al mowaihat|al rumailah|al sawan|ajman corniche|ajman downtown|ajman marina|emirates city|garden city|masfout|al manama)\b',
            'Ras Al Khaimah': r'\b(ras al khaimah|rak|al marjan|al hamra|mina al arab|al nakheel|al rams|al seer|al dhait|al jazeera al hamra|khuzam|maamoura|flamingo|marina bay|seahorse|walnut)\b',
            'Umm Al Quwain': r'\b(umm al quwain|uaq|al sinayah|al dar al baida|al rauda|al salamah|al jazirah al hamra|al aqah|al falaj|al humrah|al maydan|al qawra)\b',
            'Fujairah': r'\b(fujairah|dibba|al bidya|al qurrayah|al aqah|al bithnah|al hail|kalba|khorfakkan|masafi|qidfa|sakamkam|sharm|wadi al helo|wadi wurayah)\b',
            'Al Ain': r'\b(al ain|alain|al jimmi|al muwaiji|al hili|al qattara|al sarooj|al towaiya|al khubairah|al maqam|al mutared|al salamat|al shaab|al shweihan|al zahra|al ain oasis)\b'
        }
        
        # 2. قاموس المرافق الشامل
        self.amenity_mapping = {
            'has_swimming_pool': r'\b(swimming pool|pool|shared pool|private pool|infinity pool|rooftop pool|kids pool|communal pool|aquatic)\b',
            'has_gym': r'\b(gym|fitness|health club|fitness center|workout|weight room|gymnasium)\b',
            'has_parking': r'\b(parking|covered parking|parking space|garage|valet parking|basement parking)\b',
            'has_balcony': r'\b(balcony|terrace|private terrace|balcon|patio)\b',
            'has_security': r'\b(security|cctv|24/7 security|security staff|surveillance)\b',
            'has_concierge': r'\b(concierge|reception|lobby|front desk|24 hours concierge)\b',
            'has_kids_area': r'\b(kids play|play area|children|day care|nursery|kids club)\b',
            'has_pets_allowed': r'\b(pets allowed|pet friendly|allows pets)\b',
            'has_maids_room': r'\b(maids|maid|servants|servant|study room|study)\b',
            'has_private_pool': r'\b(private pool|own pool)\b',
            'has_shared_pool': r'\b(shared pool|communal pool)\b',
            'has_sauna': r'\b(sauna)\b',
            'has_jacuzzi': r'\b(jacuzzi|hot tub)\b',
            'has_steam_room': r'\b(steam room|steam)\b',
            'has_garden': r'\b(garden|lawn|green area|landscape)\b',
            'has_bbq_area': r'\b(barbeque|bbq|grill area)\b',
            'has_laundry': r'\b(laundry|washing)\b',
            'has_broadband': r'\b(broadband|internet|wifi)\b',
            'has_central_ac': r'\b(centrally air-conditioned|central ac|central air|hvac)\b',
            'has_elevator': r'\b(elevator|lift|service elevator)\b',
            'has_prayer_room': r'\b(prayer room|mosque)\b',
            'has_business_center': r'\b(business center|meeting room|conference room)\b',
            'has_furnished': r'\b(furnished|fully furnished|semi-furnished|with furniture)\b',
            'has_study_room': r'\b(study room|study)\b',
            'has_shared_kitchen': r'\b(shared kitchen)\b',
            'has_disabled_facilities': r'\b(disabled|wheelchair|facilities for disabled)\b',
            'has_first_aid': r'\b(first aid|medical center|clinic)\b',
            'has_satellite_tv': r'\b(satellite|cable tv)\b',
            'has_heating': r'\b(central heating|heating)\b',
            'has_intercom': r'\b(intercom)\b',
            'has_waste_disposal': r'\b(waste disposal|garbage disposal)\b',
            'has_maintenance': r'\b(maintenance staff|facility management)\b',
            'has_double_glazed': r'\b(double glazed)\b',
            'has_cleaning': r'\b(cleaning services)\b',
            'has_electricity_backup': r'\b(electricity backup|generator)\b',
            'has_cafeteria': r'\b(cafeteria|canteen)\b',
            'has_storage': r'\b(storage areas|storage room)\b',
            'has_atm': r'\b(atm)\b',
            'has_lobby': r'\b(lobby|reception)\b',
            'has_service_elevator': r'\b(service elevator|service lift)\b',
        }

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔄 Starting Data Transformation...")
        df_clean = df.copy()
        
        df_clean = self._clean_numerical(df_clean)
        df_clean = self._extract_from_text_corpus(df_clean)
        df_clean = self._extract_location(df_clean)
        df_clean = self._extract_amenities(df_clean)
        df_clean = self._apply_business_logic(df_clean)
        df_clean = self._feature_engineering(df_clean)
        df_clean = self._handle_missing_values(df_clean)
        df_clean = self._detect_outliers(df_clean)
        
        logger.info(f"✨ Transformation complete! Final Shape: {df_clean.shape}")
        return df_clean

    def _clean_numerical(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🔢 Cleaning numerical columns with Regex...")
        
        # Price
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        
        # Beds & Baths
        for col in ['beds', 'baths']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().str.replace('studio', '0', regex=False)
                df[col] = pd.to_numeric(df[col].str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).astype(int)
        
        # Areas & Sizes
        for col in ['area', 'built_up_area', 'balcony_size', 'building_area']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        
        # Counts
        for col in ['floors', 'elevators', 'parking_spaces', 'retail_centres', 'swimming_pools']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).astype(int)
                
        return df

    def _extract_from_text_corpus(self, df: pd.DataFrame) -> pd.DataFrame:
        """⭐ ميزة Deep Text Mining: استخراج الأرقام المفقودة من النصوص"""
        logger.info("🔍 Deep Text Mining (Description & Amenities)...")
        
        if 'amenities' in df.columns and 'description' in df.columns:
            df['text_corpus'] = (df['amenities'].fillna('') + " " + df['description'].fillna('')).str.lower()
            
            num_extractions = {
                'parking_spaces': r'(\d+)\s*(?:parking|covered parking|parking spaces)',
                'floors': r'(\d+)\s*(?:floors|stories|storeys)',
                'elevators': r'(\d+)\s*(?:elevators|lifts)'
            }
            
            for col, pattern in num_extractions.items():
                if col in df.columns:
                    extracted = df['text_corpus'].str.extract(pattern, expand=False)
                    extracted_num = pd.to_numeric(extracted, errors='coerce')
                    mask_na = df[col].isna() | (df[col] == 0)
                    df.loc[mask_na, col] = extracted_num.loc[mask_na]
                    df[col] = df[col].fillna(0).astype(int)
                    
            df = df.drop(columns=['text_corpus'], errors='ignore')
            
        return df

    def _extract_location(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🗺️ Extracting City & Neighborhood...")
        if 'location' in df.columns:
            location_text = df['location'].astype(str).str.lower()
            df['city'] = 'Unknown'
            
            for city, pattern in self.city_mapping.items():
                mask = location_text.str.contains(pattern, regex=True, na=False)
                df.loc[mask, 'city'] = city
                
            df['neighborhood'] = df['location'].astype(str).str.split(',').str[0].str.strip().str.title()
            df.loc[df['neighborhood'].isin(['Nan', '']), 'neighborhood'] = 'Unknown'
            
        return df

    def _extract_amenities(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🏊 Extracting Boolean Amenities...")
        text_sources = []
        for col in ['amenities', 'description', 'title']:
            if col in df.columns:
                text_sources.append(df[col].fillna('').astype(str).str.lower())
                
        if text_sources:
            combined_text = pd.concat(text_sources, axis=1).apply(lambda x: ' '.join(x), axis=1)
            
            for amenity, pattern in self.amenity_mapping.items():
                df[amenity] = combined_text.str.contains(pattern, regex=True, na=False).astype(int)
                
            amenity_cols = [col for col in df.columns if col.startswith('has_')]
            df['amenities_count'] = df[amenity_cols].sum(axis=1)
            
        return df

    def _apply_business_logic(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🧠 Applying Business Logic...")
        if 'property_type' in df.columns:
            mask_plots = df['property_type'].str.contains('Plot|Building', case=False, na=False)
            df.loc[mask_plots, ['beds', 'baths', 'balcony_size']] = 0
            
        if 'furnishing' in df.columns:
            mask_empty = df['furnishing'].isna() | (df['furnishing'].astype(str).str.strip() == '') | (df['furnishing'].astype(str).str.lower() == 'nan')
            df.loc[mask_empty, 'furnishing'] = 'Unfurnished'
            df['furnishing'] = df['furnishing'].str.title()
            
        return df

    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("📐 Feature Engineering...")
        if 'price' in df.columns and 'area' in df.columns:
            df['price_per_sqft'] = np.where(df['area'] > 0, df['price'] / df['area'], np.nan)
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🤖 Handling missing values with KNN Imputer...")
        numeric_cols = ['beds', 'baths', 'area', 'price']
        existing_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(existing_cols) >= 2:
            imputer = KNNImputer(n_neighbors=5)
            df[existing_cols] = imputer.fit_transform(df[existing_cols])
            
        return df

    def _detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("🛡️ Detecting & Capping Outliers...")
        if 'price' in df.columns:
            df.loc[df['price'] < 10000, 'price'] = np.nan
            df.loc[df['price'] > 1000000000, 'price'] = np.nan
        if 'area' in df.columns:
            df.loc[df['area'] < 100, 'area'] = np.nan
            df.loc[df['area'] > 1000000, 'area'] = np.nan
        return df


class DatabaseManager:
    """إدارة الاتصال وقراءة/كتابة البيانات بسرعة صاروخية"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to PostgreSQL successfully.")
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
            
    def close(self):
        if self.conn:
            self.conn.close()
            logger.info(" Connection closed.")
            
    def extract_raw_data(self) -> pd.DataFrame:
        logger.info(" Fetching raw data from 'properties' table...")
        query = "SELECT * FROM properties;"
        df = pd.read_sql(query, self.conn)
        logger.info(f"✅ Fetched {len(df)} raw records.")
        return df
        
    def load_cleaned_data(self, df: pd.DataFrame, table_name: str = 'cleaned_properties'):
        logger.info(f"💾 Upserting {len(df)} cleaned records to '{table_name}' (Fast Mode)...")
        
        # ==========================================
        # ⭐ 1. تحويل NaN إلى None (مطلوب لـ PostgreSQL)
        # ==========================================
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        
        # ==========================================
        # ⭐ 2. تحديد الأعمدة المطلوبة (بما فيهم property_img)
        # ==========================================
        cols_to_keep = [
            'url', 'scraped_at', 'property_img', 'price', 'currency', 'title', 'location', 
            'beds', 'baths', 'area', 'property_type', 'purpose', 'reference_no', 'completion', 
            'furnishing', 'trucheck_date', 'added_on', 'handover_date', 'description', 'amenities',
            'building_name', 'floors', 'retail_centres', 'swimming_pools', 'parking_spaces',
            'building_area', 'elevators', 'agent_name', 'agency_name', 'developer', 'ownership',
            'built_up_area', 'balcony_size', 'parking_availability', 'permit_number', 'zone_name',
            'registered_agency', 'rera', 'brn', 'city', 'neighborhood', 'price_per_sqft', 'amenities_count'
        ]
        
        # إضافة أعمدة الـ Boolean
        bool_cols = [col for col in df.columns if col.startswith('has_')]
        cols_to_keep.extend(bool_cols)
        
        # فلترة الأعمدة الموجودة فعلياً
        cols_to_keep = [c for c in cols_to_keep if c in df.columns]
        df_final = df[cols_to_keep].copy()
        
        # ==========================================
        # ⭐ 3. تحويل أعمدة المرافق من int إلى bool
        # ==========================================
        for col in bool_cols:
            if col in df_final.columns:
                df_final[col] = df_final[col].fillna(False).astype(bool)
        
        # ==========================================
        #  4. تجهيز استعلام الـ Upsert
        # ==========================================
        columns_str = ', '.join(cols_to_keep)
        update_cols = [f"{col} = EXCLUDED.{col}" for col in cols_to_keep if col not in ['url', 'scraped_at']]
        update_str = ', '.join(update_cols)
        
        upsert_query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES %s
            ON CONFLICT (url, scraped_at) DO UPDATE SET
            {update_str}, cleaned_at = CURRENT_TIMESTAMP;
        """
        
        # ==========================================
        # ⭐ 5. التحويل إلى Tuples والرفع
        # ==========================================
        data_tuples = [tuple(x) for x in df_final.to_numpy()]
        
        try:
            cursor = self.conn.cursor()
            execute_values(cursor, upsert_query, data_tuples, page_size=1000)
            self.conn.commit()
            cursor.close()
            logger.info(f"🎉 Successfully upserted {len(df_final)} cleaned records!")
            
            # التحقق من property_img
            img_count = df_final['property_img'].notna().sum() if 'property_img' in df_final.columns else 0
            logger.info(f"️ property_img records: {img_count}/{len(df_final)}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Upsert failed: {e}")
            raise


# ==========================================
# 🚀 نقطة التشغيل الرئيسية (Orchestrator)
# ==========================================
def run_pipeline():
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'dbname': os.getenv('DB_NAME', 'bayut_db'),
        'user': os.getenv('DB_USER', 'bayut_user'),
        'password': os.getenv('DB_PASSWORD', '1212')
    }
    
    db_manager = DatabaseManager(DB_CONFIG)
    cleaner = BayutDataCleaner()
    
    try:
        db_manager.connect()
        df_raw = db_manager.extract_raw_data()
        
        if df_raw.empty:
            logger.warning("⚠️ No raw data found.")
            return
            
        df_cleaned = cleaner.fit_transform(df_raw)
        db_manager.load_cleaned_data(df_cleaned)
        
        logger.info("✅ Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    run_pipeline()