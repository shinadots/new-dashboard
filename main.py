import logging
from datetime import date as date_cls

from db import upsert_ad_performance, upsert_funnel_snapshot, log_sync
from services.windsor import fetch_windsor_ad_data
from services.kommo import fetch_kommo_funnel_snapshot
from services.rdstation import fetch_rdstation_funnel_snapshot
# from services.google_ads import fetch_google_ads_data  # só descomente se não usar Windsor pro Google

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("etl")


def run_sync():
    today = date_cls.today().isoformat()
    log.info("Iniciando sync do dia %s", today)

    jobs = {
        "windsor": lambda: upsert_ad_performance(fetch_windsor_ad_data(today, today)),
        "kommo": lambda: upsert_funnel_snapshot(fetch_kommo_funnel_snapshot(today)),
        "rdstation": lambda: upsert_funnel_snapshot(fetch_rdstation_funnel_snapshot(today)),
        # "google": lambda: upsert_ad_performance(fetch_google_ads_data(today, today)),
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
