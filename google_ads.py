from google.ads.googleads.client import GoogleAdsClient
from config import (
    GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
    GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CUSTOMER_ID, GOOGLE_ADS_REFRESH_TOKEN,
)

# Só ative esse service se o dado do Google não vier todo pelo Windsor —
# muita conta usa Windsor pra tudo e não precisa desse passo separado.


def _build_client() -> GoogleAdsClient:
    config = {
        "client_id": GOOGLE_ADS_CLIENT_ID,
        "client_secret": GOOGLE_ADS_CLIENT_SECRET,
        "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
        "refresh_token": GOOGLE_ADS_REFRESH_TOKEN,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)


def fetch_google_ads_data(date_from: str, date_to: str) -> list[dict]:
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          segments.date,
          metrics.clicks,
          metrics.cost_micros,
          metrics.impressions,
          metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'
    """

    stream = ga_service.search_stream(customer_id=GOOGLE_ADS_CUSTOMER_ID, query=query)

    rows = []
    for batch in stream:
        for r in batch.results:
            rows.append({
                "source": "google_ads",
                "campaign_id": str(r.campaign.id),
                "campaign_name": r.campaign.name,
                "date": r.segments.date,
                "spend": r.metrics.cost_micros / 1_000_000,
                "clicks": r.metrics.clicks,
                "impressions": r.metrics.impressions,
                "conversions": r.metrics.conversions,
                "raw": {"campaign_id": r.campaign.id, "date": r.segments.date},
            })
    return rows
