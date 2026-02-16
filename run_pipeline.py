from ingestion.csv_loader import load_merchants_csv
from ingestion.simulated_api_client import fetch_internal_risk
import pandas as pd
from ingestion.rest_countries_client import fetch_country_metadata
import asyncio
from ingestion.pdf_processor import extract_pdf_text_async
from ingestion.scraper import scrape_claritypay

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def enrich_with_internal_api(df: pd.DataFrame) -> pd.DataFrame:
    enriched_rows = []

    for _, row in df.iterrows():
        merchant_id = row["merchant_id"]

        api_data = fetch_internal_risk(merchant_id)

        enriched_row = row.to_dict()

        enriched_row["internal_risk_flag"] = api_data["internal_risk_flag"]
        enriched_row["last_30d_volume"] = api_data["transaction_summary"]["last_30d_volume"]
        enriched_row["last_30d_txn_count"] = api_data["transaction_summary"]["last_30d_txn_count"]
        enriched_row["avg_ticket_size"] = api_data["transaction_summary"]["avg_ticket_size"]
        enriched_row["last_review_date"] = api_data.get("last_review_date")

        enriched_rows.append(enriched_row)

    return pd.DataFrame(enriched_rows)


def enrich_with_country_data(df: pd.DataFrame) -> pd.DataFrame:
    enriched_rows = []

    for _, row in df.iterrows():
        country_data = fetch_country_metadata(row["country"])

        enriched_row = row.to_dict()
        enriched_row.update(country_data)

        enriched_rows.append(enriched_row)

    return pd.DataFrame(enriched_rows)


from model.train import train_risk_model
from model.predict import predict_risk

def extract_pdf_risk_signal(pdf_text):

    if not pdf_text:
        return 0.0

    keywords = ["fraud", "lawsuit", "bankruptcy"]
    return sum(word in pdf_text.lower() for word in keywords) / len(keywords)


def build_external_features(df, pdf_text, scrape_data):

    # ---- PDF Risk Signals ----
    df["pdf_mentions_refunds"] = int("refund" in pdf_text.lower())
    df["pdf_mentions_chargeback"] = int("chargeback" in pdf_text.lower())
    df["pdf_mentions_complaint"] = int("complaint" in pdf_text.lower())

    # ---- Web Scrape Signals ----
    df["num_value_props"] = len(scrape_data.get("value_propositions", []))
    df["num_public_stats"] = len(scrape_data.get("public_stats", []))
    df["num_partners"] = len(scrape_data.get("partners", []))

    # ---- Internal API Signals ----
    # df["internal_flag_numeric"] = df["internal_risk_flag"].astype(int)
    RISK_FLAG_MAP = {
    "low": 0,
    "medium": 1,
    "high": 2
    }

    # Validate unknown categories
    unknown_flags = set(df["internal_risk_flag"].dropna().unique()) - set(RISK_FLAG_MAP.keys())

    if unknown_flags:
        print(f"WARNING: Unknown internal risk flags found: {unknown_flags}")

    df["internal_flag_numeric"] = (
        df["internal_risk_flag"]
            .map(RISK_FLAG_MAP)
    )

    # Optional: Fill missing safely
    df["internal_flag_numeric"] = df["internal_flag_numeric"].fillna(1)

    # ---- Country Risk Proxy ----
    df["is_high_risk_region"] = df["region"].isin(
        ["Africa", "South America"]
    ).astype(int)



    pdf_risk_signal = extract_pdf_risk_signal(pdf_text)
    df["pdf_risk_signal"] = pdf_risk_signal

    return df

def compute_country_risk(df: pd.DataFrame) -> pd.DataFrame:

    if {"chargeback_rate", "fraud_rate"}.issubset(df.columns):

        country_risk = (
            df.groupby("country")[["chargeback_rate", "fraud_rate"]]
            .mean()
            .mean(axis=1)
        )

        df["country_risk_score"] = df["country"].map(country_risk)

    else:
        df["country_risk_score"] = 0.0

    return df

# ---- Portfolio-level aggregation ----
def compute_portfolio_metrics(df):
    portfolio_metrics = {}

    # Count of merchants by tier
    portfolio_metrics['num_high_risk'] = (df['risk_tier'] == 'High').sum()
    portfolio_metrics['num_medium_risk'] = (df['risk_tier'] == 'Medium').sum()
    portfolio_metrics['num_low_risk'] = (df['risk_tier'] == 'Low').sum()

    # Expected number of high-risk merchants (sum of probabilities)
    portfolio_metrics['expected_high_risk_merchants'] = df['risk_probability'].sum()

    # Average probability across portfolio
    portfolio_metrics['average_risk_probability'] = df['risk_probability'].mean()

    return portfolio_metrics

if __name__ == "__main__":

    # 1️⃣ Load CSV
    df = load_merchants_csv("data/merchants.csv")
    print("CSV Loaded")

    df = enrich_with_internal_api(df)
    print("Internal API enrichment complete")

    df = enrich_with_country_data(df)
    print("Country enrichment complete")

    # Process PDF asynchronously
    print("Processing merchant summary PDF...")
    pdf_text = asyncio.run(
        extract_pdf_text_async("data/sample_merchant_summary.pdf")
    )
    scrape_data = scrape_claritypay()

    df = build_external_features(df, pdf_text, scrape_data)
    print("External features built")

    # Behavioral rates
    df["transaction_count"] = df["transaction_count"].replace(0, 1)
    df["chargeback_rate"] = df["dispute_count"] / df["transaction_count"]
    df["fraud_rate"] = df["chargeback_rate"] * 0.6
    print("Behavioral rates created")

    # ✅ ADD THIS LINE
    df = compute_country_risk(df)
    print("Country risk computed")

    # Now composite risk score
    df["risk_score"] = (
        0.4 * df["chargeback_rate"] +
        0.3 * df["fraud_rate"] +
        0.2 * df["internal_flag_numeric"] +
        0.1 * df["country_risk_score"]
    )

    # 2️⃣ Train Behavioral Model
    model, feature_importance = train_risk_model(df)

    print("\nTraining Complete\n")

    # 3️⃣ Generate Predictions
    df = predict_risk(df)

    # 4️⃣ Map Probability → Tier
    def map_risk_tier(p):
        if p > 0.7:
            return "High"
        elif p > 0.3:
            return "Medium"
        return "Low"

    df["risk_tier"] = df["risk_probability"].apply(map_risk_tier)

    print("\nSample Predictions:")
    print(df[["merchant_id", "risk_probability", "risk_tier"]].head())

    from reporting.llm_report_generator import generate_llm_underwriting_report
    import os

    # Compute portfolio-level metrics once
    portfolio_metrics = {
        "expected_high_risk_merchants": df['predicted_high_risk'].sum(),
        "average_risk_probability": df['risk_probability'].mean()
    }

    print("\nPipeline complete. You can now generate an LLM underwriting report for any merchant.\n")

    while True:
        merchant_id_to_report = input("Enter Merchant ID (or 'exit' to quit): ").strip()
        
        if merchant_id_to_report.lower() == "exit":
            print("Exiting LLM report generator.")
            break
        
        if merchant_id_to_report not in df['merchant_id'].values:
            print(f"Merchant ID {merchant_id_to_report} not found. Try again.\n")
            continue
        
        merchant_row = df[df["merchant_id"] == merchant_id_to_report].iloc[0]
        
        # Generate the report
        report_text = generate_llm_underwriting_report(
            merchant_row, feature_importance, portfolio_metrics
        )
        
        print("\n--- LLM Underwriting Report ---\n")
        print(report_text[:1000], "...")  # Show first 1000 chars for preview
        
        save_choice = input("\nDo you want to save this report? (y/n): ").strip().lower()
        if save_choice == "y":
            os.makedirs("data/reports", exist_ok=True)
            report_file = f"data/reports/{merchant_id_to_report}_llm_report.txt"
            with open(report_file, "w") as f:
                f.write(report_text)
            print(f"Report saved at {report_file}\n")
        else:
            print("Report not saved.\n")


    # Usage
    portfolio_metrics = compute_portfolio_metrics(df)
    print("\n--- Portfolio-level Risk Metrics ---")
    for k, v in portfolio_metrics.items():
        print(f"{k}: {v}")


    # from model.predict import predict_risk
    from reporting.report_generator import generate_underwriting_report

    # model, feature_importance = train_risk_model(df)

    # df = predict_risk(df)

    # Get highest risk merchant
    highest_risk = df.sort_values(
        by="risk_probability", ascending=False
    ).iloc[0]

    report = generate_underwriting_report(highest_risk, feature_importance)

    print(report)
    # print(df.head(5))
    print(df.columns)