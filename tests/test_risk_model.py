import pandas as pd
# from model.risk_model import compute_risk_score  # adjust to your actual file
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.risk_model import RiskModel

def test_risk_model_score():
    model = RiskModel()

    features = {
        "num_public_stats": 2,
        "num_value_props": 3,
        "has_partners": True
    }

    score = model.compute_score(features)

    assert isinstance(score, float)
    assert 0 <= score <= 100

def test_risk_tier():
    model = RiskModel()

    assert model.risk_tier(20) == "Low"
    assert model.risk_tier(45) == "Medium"
    assert model.risk_tier(80) == "High"