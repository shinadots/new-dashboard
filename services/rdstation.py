import requests
from config import RD_CRM_TOKEN

# Funil/oportunidade fica na RD Station CRM API (crm.rdstation.com),
# diferente da API de Marketing (api.rd.services). Confirme qual token voce tem.
BASE_URL = "https://crm.rdstation.com/api/v1"


def fetch_rdstation_leads() -> list[dict]:
    """Devolve um dicionário por deal (não agregado) com created_at/updated_at,
    pra o front poder filtrar por qualquer período depois."""
    funnels_res = requests.get(f"{BASE_URL}/deal_pipelines", params={"token": RD_CRM_TOKEN}, timeout=60)
    funnels_res.raise_for_status()
    pipelines = funnels_res.json().get("deal_pipelines", [])

    rows = []

    for pipeline in pipelines:
        page = 1
        has_more = True

        while has_more:
            deals_res = requests.get(
                f"{BASE_URL}/deals",
                params={
                    "token": RD_CRM_TOKEN,
                    "deal_pipeline_id": pipeline["_id"],
                    "page": page,
                    "limit": 200,
                },
                timeout=60,
            )
            if not deals_res.ok:
                break
            deals = deals_res.json().get("deals", [])

            for deal in deals:
                rows.append({
                    "crm": "rdstation",
                    "lead_id": deal["_id"],
                    "pipeline_id": pipeline["_id"],
                    "pipeline_name": pipeline["name"],
                    "status_id": deal["deal_stage_id"],
                    "status_name": deal.get("deal_stage", {}).get("name"),
                    "price": deal.get("amount_total") or 0,
                    # RD devolve created_at/updated_at já em ISO8601
                    "created_at": deal.get("created_at"),
                    "updated_at": deal.get("updated_at"),
                })

            has_more = len(deals) == 200
            page += 1

    return rows
