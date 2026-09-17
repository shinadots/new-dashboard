import logging
from datetime import date as date_cls

from db import upsert_funnel_snapshot, log_sync
from services.kommo import fetch_kommo_funnel_snapshot
from services.rdstation import fetch_rdstation_funnel_snapshot
# Windsor NÃO entra aqui: ele já grava direto nas tabelas meta_ads/google_ads
# do Supabase do Dashboard-main, sem precisar desse ETL. Esse script cuida só
# do que o Windsor não faz — funil de CRM (Kommo e RD Station).

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("etl")


def run_sync():
    today = date_cls.today().isoformat()
    log.info("Iniciando sync do dia %s", today)

    jobs = {
        "kommo": lambda: upsert_funnel_snapshot(fetch_kommo_funnel_snapshot(today)),
        "rdstation": lambda: upsert_funnel_snapshot(fetch_rdstation_funnel_snapshot(today)),
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
