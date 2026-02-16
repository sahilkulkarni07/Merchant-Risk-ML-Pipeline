def compute_risk_score(features: dict):
    """
    Simple heuristic risk scoring model.
    Lower score = lower risk.
    """

    score = 50  # baseline risk

    # Positive signals reduce risk
    score -= features["num_public_stats"] * 3
    score -= features["num_value_props"] * 1

    if features["has_partners"]:
        score -= 5

    # Guardrails
    score = max(0, min(score, 100))

    return score


class RiskModel:
    def __init__(self):
        # Baseline risk
        self.base_score = 50

    def compute_score(self, features: dict) -> float:
        score = self.base_score

        # Positive signals reduce risk
        score -= features["num_public_stats"] * 3
        score -= features["num_value_props"] * 1

        if features["has_partners"]:
            score -= 5

        # Clamp between 0–100
        score = max(0, min(score, 100))

        return float(round(score, 2))

    def risk_tier(self, score: float) -> str:
        if score < 30:
            return "Low"
        elif score < 60:
            return "Medium"
        else:
            return "High"