def generate_underwriting_report(row, feature_importance):

    report = f"""
==============================
MERCHANT RISK ASSESSMENT
==============================

Merchant ID: {row['merchant_id']}
Country: {row['country']}

--- Behavioral Model ---
Risk Probability: {row['risk_probability']:.3f}
Risk Tier: {row['risk_tier']}

--- Top Risk Drivers ---
"""

    for _, feature in feature_importance.head(3).iterrows():
        report += f"- {feature['feature']} (coef: {feature['coefficient']:.4f})\n"

    report += f"""
--- Transaction Metrics ---
Monthly Volume: {row['monthly_volume']}
Transaction Count: {row['transaction_count']}
Dispute Count: {row['dispute_count']}

--- Final Recommendation ---
"""

    if row["risk_tier"] == "High":
        report += "Enhanced due diligence required.\n"
    elif row["risk_tier"] == "Medium":
        report += "Manual review recommended.\n"
    else:
        report += "Standard onboarding.\n"

    report += "\n==============================\n"

    return report