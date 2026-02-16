import joblib
import pandas as pd


def load_model():
    return joblib.load("artifacts/risk_model.pkl")


def predict_risk(df: pd.DataFrame):

    model = load_model()

    df["dispute_rate"] = df["dispute_count"] / df["transaction_count"]
    df["avg_ticket_size"] = df["monthly_volume"] / df["transaction_count"]

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

    probs = model.predict_proba(df[features])[:, 1]
    df["risk_probability"] = probs

    # Calibrated threshold for imbalance
    threshold = 0.25

    df["predicted_high_risk"] = (df["risk_probability"] > threshold).astype(int)

    # Tiering logic
    def assign_tier(p):
        if p > 0.6:
            return "High"
        elif p > 0.3:
            return "Medium"
        else:
            return "Low"

    df["risk_tier"] = df["risk_probability"].apply(assign_tier)

    return df