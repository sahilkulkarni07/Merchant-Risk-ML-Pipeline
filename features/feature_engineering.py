import json
import os

def build_features(json_path="data/raw/claritypay.json"):
    with open(json_path, "r") as f:
        data = json.load(f)

    value_props = data.get("value_propositions", [])
    stats = data.get("public_stats", [])
    partners = data.get("partners", [])

    features = {
        "num_value_props": len(value_props),
        "num_public_stats": len(stats),
        "num_partners": len(partners),
        "avg_value_prop_length": (
            sum(len(v) for v in value_props) / len(value_props)
            if value_props else 0
        ),
        "has_stats": 1 if len(stats) > 0 else 0,
        "has_partners": 1 if len(partners) > 0 else 0
    }

    return features