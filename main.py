import logging
from datetime import date as date_cls, timedelta

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

# Conversões do Google Ads têm atraso de atribuição — um lead pode ser
# atribuído a um clique de vários dias atrás, e o número final de conversões
# só se estabiliza depois de alguns dias. Por isso, todo sync re-busca os
# últimos N dias (não só "hoje") e faz upsert por cima — isso corrige gasto e
# leads de dias recentes que já tinham sido gravados com valor desatualizado.
GOOGLE_ADS_ROLLING_WINDOW_DAYS = 14


def _sync_google_ads(today: date_cls) -> int:
    customer_ids = get_google_ads_customer_ids()
    if not customer_ids:
        log.warning("Nenhum conta_google_id encontrado em clientes_config — nada a sincronizar")
        return 0
    date_from = (today - timedelta(days=GOOGLE_ADS_ROLLING_WINDOW_DAYS - 1)).isoformat()
    date_to = today.isoformat()
    rows = fetch_google_ads_data(customer_ids, date_from, date_to)
    return upsert_google_ads(rows)


def run_sync():
    today = date_cls.today()
    log.info("Iniciando sync do dia %s", today.isoformat())

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
