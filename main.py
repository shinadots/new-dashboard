import logging
from datetime import date as date_cls

from db import upsert_google_ads, upsert_crm_leads, get_google_ads_customer_ids, log_sync
from services.kommo import fetch_kommo_leads
from services.rdstation import fetch_rdstation_leads
from services.google_ads import fetch_google_ads_data
# Windsor NÃO entra aqui: ele já grava direto na tabela meta_ads do Supabase
# do Dashboard-main. Esse script cuida do que falta — funil de CRM (Kommo e
# RD Station, lead a lead, com created_at/updated_at pra filtro de período no
# front) e Google Ads (via API oficial, sem passar pelo Windsor).

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("etl")


def _sync_google_ads(today: str) -> int:
    customer_ids = get_google_ads_customer_ids()
    if not customer_ids:
        log.warning("Nenhum conta_google_id encontrado em clientes_config — nada a sincronizar")
        return 0
    rows = fetch_google_ads_data(customer_ids, today, today)
    return upsert_google_ads(rows)


def run_sync():
    today = date_cls.today().isoformat()
    log.info("Iniciando sync do dia %s", today)

    jobs = {
        "kommo": lambda: upsert_crm_leads(fetch_kommo_leads()),
        "rdstation": lambda: upsert_crm_leads(fetch_rdstation_leads()),
        "google_ads": lambda: _sync_google_ads(today),
    }

    for name, job in jobs.items():
        try:
            rows = job()
            log.info("%s: %s linhas gravadas", name, rows)
            log_sync(name, "success", f"{rows} linhas")
        except Exception as e:
            log.exception("%s falhou", name)
            log_sync(name, "error", str(e))


if __name__ == "__main__":
    run_sync()
