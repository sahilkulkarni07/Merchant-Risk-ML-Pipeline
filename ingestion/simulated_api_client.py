import requests


BASE_URL = "http://127.0.0.1:8000"


def fetch_internal_risk(merchant_id: str) -> dict:
    """
    Calls the simulated internal risk API
    and returns JSON response.
    """

    url = f"{BASE_URL}/risk/{merchant_id}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"API call failed for {merchant_id}: {e}")

    return response.json()