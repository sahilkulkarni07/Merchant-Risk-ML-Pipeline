from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import random

app = FastAPI(title="Simulated Internal Merchant Risk API")


# -----------------------------
# Pydantic Models (Match Schema)
# -----------------------------

class TransactionSummary(BaseModel):
    last_30d_volume: float = Field(..., ge=0)
    last_30d_txn_count: int = Field(..., ge=0)
    avg_ticket_size: float = Field(..., ge=0)


class MerchantRiskResponse(BaseModel):
    merchant_id: str
    internal_risk_flag: str
    transaction_summary: TransactionSummary
    last_review_date: Optional[date]


# -----------------------------
# Mock Logic
# -----------------------------

VALID_RISK_FLAGS = ["low", "medium", "high"]


@app.get("/risk/{merchant_id}", response_model=MerchantRiskResponse)
def get_merchant_risk(merchant_id: str):

    if not merchant_id.startswith("M"):
        raise HTTPException(status_code=400, detail="Invalid merchant_id")

    # Simulated random data
    last_30d_volume = round(random.uniform(10000, 200000), 2)
    last_30d_txn_count = random.randint(100, 5000)
    avg_ticket_size = round(last_30d_volume / last_30d_txn_count, 2)

    return MerchantRiskResponse(
        merchant_id=merchant_id,
        internal_risk_flag=random.choice(VALID_RISK_FLAGS),
        transaction_summary={
            "last_30d_volume": last_30d_volume,
            "last_30d_txn_count": last_30d_txn_count,
            "avg_ticket_size": avg_ticket_size,
        },
        last_review_date=date.today(),
    )