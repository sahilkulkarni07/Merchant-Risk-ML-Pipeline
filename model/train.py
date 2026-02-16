import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score


def train_risk_model(df: pd.DataFrame):


    df["dispute_rate"] = df["dispute_count"] / df["transaction_count"]
    df["avg_ticket_size"] = df["monthly_volume"] / df["transaction_count"]
    df["high_risk"] = (df["dispute_rate"] > 0.002).astype(int)

    print("Class Distribution:")
    print(df["high_risk"].value_counts())
    print()

    features = [
    # Core transactional
    "monthly_volume",
    "transaction_count",
    "dispute_rate",
    "avg_ticket_size",

    # Internal API
    "last_30d_volume",
    "last_30d_txn_count",
    "internal_flag_numeric",

    # Country risk
    "is_high_risk_region",

    # PDF signals
    "pdf_mentions_refunds",
    "pdf_mentions_chargeback",
    "pdf_mentions_complaint",

    # Web signals
    "num_value_props",
    "num_public_stats",
    "num_partners"
    ]

    X = df[features]
    y = df["high_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)

    y_preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print("Classification Report:")
    print(classification_report(y_test, y_preds))

    print("ROC-AUC:", roc_auc_score(y_test, probs))

    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(model, "artifacts/risk_model.pkl")

    print("Model saved to artifacts/risk_model.pkl")

    importance_df = pd.DataFrame({
        "feature": features,
        "coefficient": model.coef_[0]
    }).sort_values(by="coefficient", ascending=False)

    print("\nFeature Importance:")
    print(importance_df)

    
    return model, importance_df
