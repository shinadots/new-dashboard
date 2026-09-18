from google.ads.googleads.client import GoogleAdsClient
from config import (
    GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
    GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID,
)

# Desde set/2026 o Google aposentou o developer token — o acesso é ligado ao
# projeto do Google Cloud dono do Client ID/Secret, não precisa mandar mais
# nada relacionado a ele aqui.


def _build_client() -> GoogleAdsClient:
    config = {
        "client_id": GOOGLE_ADS_CLIENT_ID,
        "client_secret": GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": GOOGLE_ADS_REFRESH_TOKEN,
        "login_customer_id": GOOGLE_ADS_LOGIN_CUSTOMER_ID,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)


def fetch_google_ads_data(customer_ids: list[str], date_from: str, date_to: str) -> list[dict]:
    """
    Busca performance de campanha pra cada conta de cliente (customer_ids vêm
    do clientes_config.conta_google_id — a MCC não devolve tudo de uma vez,
    precisa pedir conta por conta).
    """
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
          customer.id,
          customer.descriptive_name,
          campaign.name,
          segments.date,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'
    """

    rows = []
    for customer_id in customer_ids:
        clean_id = customer_id.replace('-', '').strip()
        if not clean_id:
            continue
        try:
            stream = ga_service.search_stream(customer_id=clean_id, query=query)
            for batch in stream:
                for r in batch.results:
                    rows.append({
                        "date": r.segments.date,
                        "account_id": str(r.customer.id),
                        "account_name": r.customer.descriptive_name,
                        "campaign": r.campaign.name,
                        "clicks": r.metrics.clicks,
                        "spend": r.metrics.cost_micros / 1_000_000,
                        "conversions": r.metrics.conversions,
                    })
        except Exception as e:
            # Uma conta com erro (ex: sem permissão, conta pausada) não pode
            # derrubar a sincronização das outras.
            print(f"[google_ads] falhou pra conta {clean_id}: {e}")

    return rows
