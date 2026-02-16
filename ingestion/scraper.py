import requests
import time
from bs4 import BeautifulSoup


BASE_URL = "https://claritypay.com"


HEADERS = {
    "User-Agent": "MerchantRiskAssessmentBot/1.0 (Educational Project)"
}


def scrape_claritypay():
    """
    Scrapes claritypay.com homepage.
    Extracts:
    - Value propositions
    - Partner mentions
    - Public stats
    """

    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to scrape claritypay.com: {e}")

    time.sleep(1)  # Respectful rate limiting

    soup = BeautifulSoup(response.text, "html.parser")

    page_text = soup.get_text(separator="\n")

    # -------------------------
    # Extract Value Propositions
    # -------------------------
    value_props = []
    keywords = ["Pay", "Clear", "Flexible", "Transparent"]

    for line in page_text.split("\n"):
        line = line.strip()
        if any(keyword in line for keyword in keywords):
            if 10 < len(line) < 120:
                value_props.append(line)

    value_props = list(set(value_props))[:10]

    # -------------------------
    # Extract Public Stats
    # -------------------------
    stats = []
    for line in page_text.split("\n"):
        line = line.strip()
        if "+" in line or "$" in line:
            if any(char.isdigit() for char in line):
                stats.append(line)

    stats = list(set(stats))[:10]

    # -------------------------
    # Partner Extraction (heuristic)
    # -------------------------
    partners = []
    for img in soup.find_all("img"):
        alt_text = img.get("alt")
        if alt_text and "partner" in alt_text.lower():
            partners.append(alt_text)

    partners = list(set(partners))

    return {
        "value_propositions": value_props,
        "public_stats": stats,
        "partners": partners,
    }