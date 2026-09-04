import sys
sys.stdout.reconfigure(encoding='utf-8')
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

engine = create_engine("mysql+pymysql://root:root@localhost:3306/zavrsni_rad_starshema")
query = """
SELECT f.is_high_engagement, f.row_id, f.duration_sec, c.creator_avg_views,
       ct.category, ct.genre, ct.hashtag, t.year_month, t.week_of_year,
       t.publish_dayofweek, t.upload_hour, p.platform, l.country, l.region, l.language,
       d.device_type, d.device_brand, d.traffic_source
FROM fact_engagement f
JOIN dim_creator c ON f.creator_tk=c.creator_tk
JOIN dim_content ct ON f.content_tk=ct.content_tk
JOIN dim_time t ON f.time_tk=t.time_tk
JOIN dim_platform p ON f.platform_tk=p.platform_tk
JOIN dim_location l ON f.location_tk=l.location_tk
JOIN dim_device d ON f.device_tk=d.device_tk
"""
df = pd.read_sql(query, engine)

raw = pd.read_csv("../../youtube-tiktok-shorts.csv",
                   usecols=["row_id", "sound_type", "notes", "season", "event_season",
                            "publish_period", "title_length", "has_emoji", "is_weekend"])
raw = raw.drop_duplicates(subset="row_id")
df = df.merge(raw, on="row_id", how="left")

cat_cols = ["category", "genre", "hashtag", "year_month", "publish_dayofweek", "platform",
            "country", "region", "language", "device_type", "device_brand", "traffic_source",
            "sound_type", "notes", "season", "event_season", "publish_period"]
num_cols = ["duration_sec", "creator_avg_views", "week_of_year", "upload_hour",
            "title_length", "has_emoji", "is_weekend"]

for c in cat_cols:
    df[c] = LabelEncoder().fit_transform(df[c].astype(str))

X = df[cat_cols + num_cols]
y = df["is_high_engagement"]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("=" * 70)
print("5-STRUKA UNAKRSNA VALIDACIJA (cross-validation) — prosjek ROC AUC")
print("=" * 70)

models = {
    "Random Forest (class_weight=balanced)": RandomForestClassifier(
        n_estimators=300, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=42),
    "Gradient Boosting (sklearn)": GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42),
    "XGBoost (scale_pos_weight)": XGBClassifier(
        n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=(y.value_counts()[0] / y.value_counts()[1]), eval_metric="logloss",
        random_state=42, verbosity=0),
    "LightGBM (class_weight=balanced)": LGBMClassifier(
        n_estimators=400, max_depth=-1, learning_rate=0.05, class_weight="balanced",
        random_state=42, verbosity=-1),
    "Logistic Regression (balanced, scaled)": Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    ]),
}

results = {}
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    results[name] = scores
    print(f"{name:<42} AUC = {scores.mean():.4f}  (± {scores.std():.4f})")

print()
print("=" * 70)
print("RAZLIČITE TEHNIKE RJEŠAVANJA NERAVNOTEŽE KLASA (Random Forest, 5-fold CV)")
print("=" * 70)

imbalance_variants = {
    "bez ikakve korekcije": RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=42),
    "class_weight=balanced": RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=42),
    "class_weight=balanced_subsample": RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=42),
    "SMOTE + Random Forest": ImbPipeline([
        ("smote", SMOTE(random_state=42)),
        ("clf", RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=42))
    ]),
}

for name, model in imbalance_variants.items():
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    print(f"{name:<35} AUC = {scores.mean():.4f}  (± {scores.std():.4f})")

print()
print("✅ Gotovo.")
