import requests
from db import get_rd_config

# Funil/oportunidade fica na RD Station CRM API (crm.rdstation.com),
# diferente da API de Marketing (api.rd.services).
BASE_URL = "https://crm.rdstation.com/api/v1"


def _fetch_pipelines(token: str) -> list[dict]:
    res = requests.get(f"{BASE_URL}/deal_pipelines", params={"token": token}, timeout=60)
    res.raise_for_status()
    data = res.json()
    # A API devolve uma lista direta ([{...}, {...}]), não um objeto
    # {"deal_pipelines": [...]} como a doc antiga sugeria — aceita os dois
    # formatos pra não quebrar se algum outro endpoint vier diferente.
    if isinstance(data, list):
        return data
    return data.get("deal_pipelines", [])


def _fetch_deals(token: str, pipeline_id: str) -> list[dict]:
    deals = []
    page = 1
    has_more = True
    while has_more:
        res = requests.get(
            f"{BASE_URL}/deals",
            params={"token": token, "deal_pipeline_id": pipeline_id, "page": page, "limit": 200},
            timeout=60,
        )
        if not res.ok:
            break
        data = res.json()
        batch = data if isinstance(data, list) else data.get("deals", [])
        deals.extend(batch)
        has_more = len(batch) == 200
        page += 1
    return deals


def fetch_rdstation_leads() -> list[dict]:
    """Devolve um dicionário por deal (não agregado), com pipeline_name já
    como o nome do CLIENTE (não o nome cru do funil da RD) — cada cliente
    pode ter vários funis reais, mas no dashboard eles aparecem consolidados
    num só "pipeline"."""
    config = get_rd_config()  # [{cliente, token, funil}]
    if not config:
        return []

    # agrupa por token pra não buscar os pipelines do mesmo token 2x
    tokens = {c["token"] for c in config}
    pipelines_by_token: dict[str, list[dict]] = {}
    for token in tokens:
        try:
            pipelines_by_token[token] = _fetch_pipelines(token)
        except Exception as e:
            print(f"[rdstation] falhou ao buscar pipelines do token {token[:8]}...: {e}")
            pipelines_by_token[token] = []

    rows = []
    for cfg in config:
        cliente = cfg["cliente"]
        token = cfg["token"]
        funil = cfg.get("funil")
        pipelines = pipelines_by_token.get(token, [])

        if funil:
            alvo = [p for p in pipelines if p.get("name", "").strip() == funil.strip()]
        else:
            alvo = pipelines  # funil não especificado = todos os funis dessa conta

        for pipeline in alvo:
            try:
                deals = _fetch_deals(token, pipeline["_id"])
            except Exception as e:
                print(f"[rdstation] falhou ao buscar deals de {cliente}/{pipeline.get('name')}: {e}")
                continue

            for deal in deals:
                rows.append({
                    "crm": "rdstation",
                    "lead_id": deal["_id"],
                    "pipeline_id": pipeline["_id"],
                    "pipeline_name": cliente,  # ← nome do cliente, não do funil
                    "status_id": deal["deal_stage_id"],
                    "status_name": deal.get("deal_stage", {}).get("name"),
                    "price": deal.get("amount_total") or 0,
                    "created_at": deal.get("created_at"),
                    "updated_at": deal.get("updated_at"),
                })

    return rows
