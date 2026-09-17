import requests
from config import WINDSOR_API_KEY

WINDSOR_BASE_URL = "https://connectors.windsor.ai/all"  # ajuste pro dataset que voce usa no Looker

DEFAULT_FIELDS = [
    "source", "campaign", "campaign_id", "date",
    "clicks", "spend", "impressions", "conversions",
]


def fetch_windsor_ad_data(date_from: str, date_to: str, fields: list[str] | None = None) -> list[dict]:
    params = {
        "api_key": WINDSOR_API_KEY,
        "date_from": date_from,
        "date_to": date_to,
        "fields": ",".join(fields or DEFAULT_FIELDS),
    }
    res = requests.get(WINDSOR_BASE_URL, params=params, timeout=60)
    res.raise_for_status()
    payload = res.json()
    rows = payload.get("data", payload)

    return [
        {
            "source": r.get("source"),
            "campaign_id": str(r.get("campaign_id") or r.get("campaign")),
            "campaign_name": r.get("campaign"),
            "date": r.get("date"),
            "spend": float(r.get("spend") or 0),
            "clicks": int(r.get("clicks") or 0),
            "impressions": int(r.get("impressions") or 0),
            "conversions": int(r.get("conversions") or 0),
            "raw": r,
        }
        for r in rows
    ]
