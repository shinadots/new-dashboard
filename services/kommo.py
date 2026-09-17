import requests
from config import KOMMO_DOMAIN, KOMMO_ACCESS_TOKEN

BASE_URL = f"https://{KOMMO_DOMAIN}/api/v4"
HEADERS = {"Authorization": f"Bearer {KOMMO_ACCESS_TOKEN}"}


def fetch_kommo_funnel_snapshot(date: str) -> list[dict]:
    pipelines_res = requests.get(f"{BASE_URL}/leads/pipelines", headers=HEADERS, timeout=60)
    pipelines_res.raise_for_status()
    pipelines = pipelines_res.json()["_embedded"]["pipelines"]

    rows = []

    for pipeline in pipelines:
        leads_res = requests.get(
            f"{BASE_URL}/leads",
            headers=HEADERS,
            params={"filter[pipeline_id]": pipeline["id"], "limit": 250},
            timeout=60,
        )
        if not leads_res.ok:
            continue
        leads = leads_res.json().get("_embedded", {}).get("leads", [])

        # agrupa por status_id, igual a agregação atual do workflow n8n
        by_status: dict[int, dict] = {}
        statuses_by_id = {s["id"]: s["name"] for s in pipeline["_embedded"]["statuses"]}

        for lead in leads:
            key = lead["status_id"]
            acc = by_status.setdefault(key, {"count": 0, "value": 0})
            acc["count"] += 1
            acc["value"] += lead.get("price") or 0

        for status_id, agg in by_status.items():
            rows.append({
                "crm": "kommo",
                "pipeline_id": str(pipeline["id"]),
                "pipeline_name": pipeline["name"],
                "status_id": str(status_id),
                "status_name": statuses_by_id.get(status_id),
                "lead_count": agg["count"],
                "deal_value": agg["value"],
                "date": date,
                "raw": {"pipeline": pipeline["id"], "status_id": status_id},
            })

    return rows
