from transformers import pipeline

# Load model once (downloads first time only)
llm = pipeline(
    "text-generation",
    model="google/flan-t5-small"
)

def generate_llm_underwriting_report(merchant_row, feature_importance, portfolio_metrics):

    if feature_importance is not None:
        top_drivers = "\n".join([
        f"- {row['feature']}: coef={row['coefficient']:.4f}"
        for _, row in feature_importance.head(3).iterrows()
        ])
    else:
        top_drivers = "Feature importance data not available."

    prompt = f"""
    Generate a professional BNPL underwriting report.

    Merchant ID: {merchant_row['merchant_id']}
    Country: {merchant_row['country']}
    Risk Tier: {merchant_row['risk_tier']}
    Risk Probability: {merchant_row['risk_probability']:.2f}

    Top Risk Drivers:
    {top_drivers}

    Monthly Volume: {merchant_row['monthly_volume']}
    Transactions: {merchant_row['transaction_count']}
    Dispute Count: {merchant_row['dispute_count']}

    Portfolio Average Risk: {portfolio_metrics['average_risk_probability']:.2f}

    Provide:
    - Risk summary
    - Key red flags
    - Recommendation
    """

    result = llm(
        prompt,
        max_new_tokens=400,
        do_sample=False
    )

    return result[0]["generated_text"]