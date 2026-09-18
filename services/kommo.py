from datetime import datetime, timedelta, timezone
import requests
from config import KOMMO_DOMAIN, KOMMO_ACCESS_TOKEN

BASE_URL = f"https://{KOMMO_DOMAIN}/api/v4"
HEADERS = {"Authorization": f"Bearer {KOMMO_ACCESS_TOKEN}"}
PAGE_SIZE = 250

# O campo is_archive da API do Kommo não está pegando esses pipelines (por
# algum motivo o valor não vem como esperado), então reforça com exclusão
# por nome — são os que aparecem em "Pipelines arquivados" no Kommo, mais o
# Lead Scale (Geral), que o time decidiu desconsiderar do funil também.
EXCLUDED_PIPELINE_NAMES = {
    "whats pedro (não utilizar)",
    "nacho man",
    "al sultan",
    "bendito ponto",
    "ibá açaí",
    "selava",
    "lidera.ia",
    "sorvetes bruna",
    "coxinha no pote",
    "pastel 365",
    "lead scale (geral)",
    "whats pedro (não utilizar)",
    "af seguros",
    "spirito santo multimarcas",
    "quintal brincante"
}

# Só busca leads tocados nos últimos N dias —  cobre com folga os presets do
# front (1D/7D/14D) e a maioria dos ranges customizados sem trazer o
# histórico inteiro. Um lead criado há muito tempo e nunca mais atualizado
# não entra aqui (mas também não seria relevante pra nenhum período recente).
SYNC_WINDOW_DAYS = 90


def _unix(dt: datetime) -> int:
    return int(dt.timestamp())


def _fetch_all_leads(pipeline_id: int, updated_from_unix: int) -> list[dict]:
    leads = []
    page = 1
    while True:
        res = requests.get(
            f"{BASE_URL}/leads",
            headers=HEADERS,
            params={
                "filter[pipeline_id]": pipeline_id,
                "filter[updated_at][from]": updated_from_unix,
                "limit": PAGE_SIZE,
                "page": page,
            },
            timeout=60,
        )
        if res.status_code == 204:  # Kommo devolve 204 quando a página está vazia
            break
        if not res.ok:
            break
        batch = res.json().get("_embedded", {}).get("leads", [])
        if not batch:
            break
        leads.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        page += 1
    return leads


def fetch_kommo_leads() -> list[dict]:
    """Devolve um dicionário por lead (não agregado) com created_at/updated_at,
    pra o front poder filtrar por qualquer período depois."""
    pipelines_res = requests.get(f"{BASE_URL}/leads/pipelines", headers=HEADERS, timeout=60)
    pipelines_res.raise_for_status()
    pipelines = pipelines_res.json()["_embedded"]["pipelines"]

    updated_from_unix = _unix(datetime.now(timezone.utc) - timedelta(days=SYNC_WINDOW_DAYS))

    rows = []

    for pipeline in pipelines:
        if pipeline.get("is_archive"):
            continue
        if pipeline["name"].strip().lower() in EXCLUDED_PIPELINE_NAMES:
            continue

        statuses_by_id = {s["id"]: s["name"] for s in pipeline["_embedded"]["statuses"]}
        leads = _fetch_all_leads(pipeline["id"], updated_from_unix)

        for lead in leads:
            rows.append({
                "crm": "kommo",
                "lead_id": str(lead["id"]),
                "pipeline_id": str(pipeline["id"]),
                "pipeline_name": pipeline["name"],
                "status_id": str(lead["status_id"]),
                "status_name": statuses_by_id.get(lead["status_id"]),
                "price": lead.get("price") or 0,
                "created_at": datetime.fromtimestamp(lead["created_at"], tz=timezone.utc).isoformat() if lead.get("created_at") else None,
                "updated_at": datetime.fromtimestamp(lead["updated_at"], tz=timezone.utc).isoformat() if lead.get("updated_at") else None,
            })

    return rows
