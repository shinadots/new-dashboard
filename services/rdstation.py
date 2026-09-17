import requests
from config import RD_CRM_TOKEN

# Funil/oportunidade fica na RD Station CRM API (crm.rdstation.com),
# diferente da API de Marketing (api.rd.services). Confirme qual token voce tem.
BASE_URL = "https://crm.rdstation.com/api/v1"


def fetch_rdstation_funnel_snapshot(date: str) -> list[dict]:
    funnels_res = requests.get(f"{BASE_URL}/deal_pipelines", params={"token": RD_CRM_TOKEN}, timeout=60)
    funnels_res.raise_for_status()
    pipelines = funnels_res.json().get("deal_pipelines", [])

    rows = []

    for pipeline in pipelines:
        page = 1
        has_more = True
        by_stage: dict[str, dict] = {}

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
                key = deal["deal_stage_id"]
                acc = by_stage.setdefault(key, {"count": 0, "value": 0, "name": deal.get("deal_stage", {}).get("name")})
                acc["count"] += 1
                acc["value"] += deal.get("amount_total") or 0

            has_more = len(deals) == 200
            page += 1

        for stage_id, agg in by_stage.items():
            rows.append({
                "crm": "rdstation",
                "pipeline_id": pipeline["_id"],
                "pipeline_name": pipeline["name"],
                "status_id": stage_id,
                "status_name": agg["name"],
                "lead_count": agg["count"],
                "deal_value": agg["value"],
                "date": date,
                "raw": {"pipeline": pipeline["_id"], "stage_id": stage_id},
            })

    return rows
