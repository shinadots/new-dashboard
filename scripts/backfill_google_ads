"""
Backfill do Google Ads — roda uma vez só pra trazer o histórico (a sync diária
normal só pega o dia atual). Usa as mesmas credenciais do .env / GitHub Actions.

Uso:
    python scripts/backfill_google_ads.py --days 30

Precisa do mesmo .env que o main.py usa (DATABASE_URL, GOOGLE_ADS_CLIENT_ID,
GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID).
Pode rodar local (mais simples) ou adaptar pra um workflow_dispatch manual.
"""

import argparse
import logging
import sys
import os
from datetime import date, timedelta

# permite rodar "python scripts/backfill_google_ads.py" a partir da raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import upsert_google_ads, get_google_ads_customer_ids, log_sync
from services.google_ads import fetch_google_ads_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("backfill")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30, help="Quantos dias pra trás buscar (padrão: 30)")
    args = parser.parse_args()

    date_to = date.today() - timedelta(days=1)  # ontem — hoje já foi coberto pela sync diária
    date_from = date_to - timedelta(days=args.days - 1)

    log.info("Backfill de %s até %s", date_from.isoformat(), date_to.isoformat())

    customer_ids = get_google_ads_customer_ids()
    if not customer_ids:
        log.error("Nenhum conta_google_id encontrado em clientes_config — nada a fazer")
        return

    log.info("Buscando %d contas...", len(customer_ids))
    rows = fetch_google_ads_data(customer_ids, date_from.isoformat(), date_to.isoformat())
    log.info("Recebidas %d linhas da API, gravando no Supabase...", len(rows))

    total = upsert_google_ads(rows)
    log.info("Backfill concluído: %d linhas gravadas/atualizadas", total)
    log_sync("google_ads_backfill", "success", f"{total} linhas ({args.days} dias)")


if __name__ == "__main__":
    main()
