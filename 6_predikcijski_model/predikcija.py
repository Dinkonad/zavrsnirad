import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, f1_score
)

sns.set_theme(style="whitegrid")

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/zavrsni_rad_starshema"
RANDOM_STATE = 42
TEST_SIZE = 0.20
VAL_SIZE = 0.20

print("Dohvaćanje podataka iz zvjezdaste sheme")
engine = create_engine(DATABASE_URL)

query = """
SELECT
    f.is_high_engagement,
    f.duration_sec,
    c.creator_avg_views,
    ct.category,
    ct.genre,
    ct.hashtag,
    t.year_month,
    t.week_of_year,
    t.publish_dayofweek,
    t.upload_hour,
    p.platform,
    l.country,
    l.region,
    l.language,
    d.device_type,
    d.device_brand,
    d.traffic_source
FROM fact_engagement f
JOIN dim_creator c   ON f.creator_tk = c.creator_tk
JOIN dim_content ct  ON f.content_tk = ct.content_tk
JOIN dim_time t      ON f.time_tk = t.time_tk
JOIN dim_platform p  ON f.platform_tk = p.platform_tk
JOIN dim_location l  ON f.location_tk = l.location_tk
JOIN dim_device d    ON f.device_tk = d.device_tk
"""

df = pd.read_sql(query, engine)
print(f"Dohvaćeno {len(df)} redaka, {df.shape[1]} stupaca")

print("\n Raspodjela ciljne varijable is_high_engagement:")
print(df["is_high_engagement"].value_counts(normalize=True).round(4) * 100)

cat_cols = [
    "category", "genre", "hashtag", "year_month", "publish_dayofweek",
    "platform", "country", "region", "language",
    "device_type", "device_brand", "traffic_source"
]
num_cols = ["duration_sec", "creator_avg_views", "week_of_year", "upload_hour"]

le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

features = cat_cols + num_cols
X = df[features]
y = df["is_high_engagement"]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=VAL_SIZE / (1 - TEST_SIZE),
    random_state=RANDOM_STATE, stratify=y_train_full
)
print(f"\n📦 Trening skup: {len(X_train)} redaka | Validacijski skup: {len(X_val)} redaka | Test skup: {len(X_test)} redaka")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=-1,
    random_state=RANDOM_STATE
)
model.fit(X_train, y_train)

y_proba_val = model.predict_proba(X_val)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_val, y_proba_val)
f1_scores = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
best_idx = int(np.nanargmax(f1_scores))
best_threshold = float(thresholds[best_idx])
print(f"\n>>> Optimalan prag prema F1 mjeri (pronađen na VALIDACIJSKOM skupu): {best_threshold:.3f}")

y_proba_test = model.predict_proba(X_test)[:, 1]
y_pred_05 = (y_proba_test >= 0.5).astype(int)
y_pred_best = (y_proba_test >= best_threshold).astype(int)

print("\nRezultati na TEST skupu @ prag 0.5")
print(classification_report(y_test, y_pred_05, target_names=["nizak_angazman", "visok_angazman"]))
print("ROC AUC (test skup):", round(roc_auc_score(y_test, y_proba_test), 4))

cm = confusion_matrix(y_test, y_pred_05)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="viridis",
            xticklabels=["nizak_angazman", "visok_angazman"],
            yticklabels=["nizak_angazman", "visok_angazman"])
plt.xlabel("Predviđena klasa")
plt.ylabel("Stvarna klasa")
plt.title("Matrica zabune — Random Forest @0.5 (test skup)")
plt.tight_layout()
plt.savefig("slika_matrica_zabune_05.png", dpi=150)
plt.close()

print("\nRezultati na TEST skupu @ optimalni prag (odabran na validaciji)")
print(classification_report(y_test, y_pred_best, target_names=["nizak_angazman", "visok_angazman"]))

cm_best = confusion_matrix(y_test, y_pred_best)
plt.figure(figsize=(6, 5))
sns.heatmap(cm_best, annot=True, fmt="d", cmap="viridis",
            xticklabels=["nizak_angazman", "visok_angazman"],
            yticklabels=["nizak_angazman", "visok_angazman"])
plt.xlabel("Predviđena klasa")
plt.ylabel("Stvarna klasa")
plt.title(f"Matrica zabune — Random Forest @ optimalni prag ({best_threshold:.2f}, test skup)")
plt.tight_layout()
plt.savefig("slika_matrica_zabune_optimalna.png", dpi=150)
plt.close()

fpr, tpr, _ = roc_curve(y_test, y_proba_test)
plt.figure(figsize=(7, 6))
plt.plot(fpr, tpr, lw=2, label=f"ROC AUC = {roc_auc_score(y_test, y_proba_test):.3f}")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("Lažno pozitivna stopa (FPR)")
plt.ylabel("Stvarno pozitivna stopa (TPR)")
plt.title("ROC krivulja — Random Forest (test skup)")
plt.legend()
plt.tight_layout()
plt.savefig("slika_roc_krivulja.png", dpi=150)
plt.close()


importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
plt.figure(figsize=(9, 7))
sns.barplot(x=importances.values, y=importances.index, hue=importances.index,
            palette="viridis", dodge=False, legend=False)
plt.xlabel("Važnost")
plt.ylabel("Značajka")
plt.title("Važnost značajki (Random Forest)")
plt.tight_layout()
plt.savefig("slika_vaznost_znacajki.png", dpi=150)
plt.close()

print("\n Top 10 najvažnijih značajki:")
print(importances.head(10))

print("\n✅ Gotovo.")
