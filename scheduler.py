from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from main import run_sync

# Use isso só se preferir um processo Python de longa duração (ex: um worker
# num servidor/container) em vez do cron do sistema operacional.
# Pra a maioria dos casos, o crontab (ver README) é mais simples e mais barato
# de operar do que manter esse processo no ar 24h.

scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

scheduler.add_job(
    run_sync,
    trigger=CronTrigger(hour=5, minute=0),
    id="daily_dashboard_sync",
    misfire_grace_time=3600,  # roda mesmo se o processo estava fora do ar até 1h depois das 8h
)

if __name__ == "__main__":
    print("Scheduler ativo — sync diário às 08:00 (America/Sao_Paulo)")
    scheduler.start()
