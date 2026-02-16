import requests
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def fetch_country_metadata(country_name: str) -> Dict:

    url = f"https://restcountries.com/v3.1/name/{country_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()[0]

        result = {
            "region": data.get("region"),
            "subregion": data.get("subregion"),
        }

        if not result["region"]:
            raise ValueError("Missing region field")

        return result

    except Exception as e:
        logger.warning(
            f"REST Countries API failed for {country_name}: {e}. Using fallback."
        )

        # Fallback default
        return {
            "region": "Unknown",
            "subregion": "Unknown",
        }