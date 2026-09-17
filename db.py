import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from config import DATABASE_URL


@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _unused_upsert_ad_performance(rows: list[dict]) -> int:
    # Não é mais usada: o Windsor já grava direto em meta_ads/google_ads.
    # Deixei aqui só de referência, caso um dia precise voltar a fazer isso via Python.
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO ad_performance
                    (source, campaign_id, campaign_name, date, spend, clicks, impressions, conversions, raw)
                VALUES %s
                ON CONFLICT (source, campaign_id, date) DO UPDATE SET
                    campaign_name = EXCLUDED.campaign_name,
                    spend = EXCLUDED.spend,
                    clicks = EXCLUDED.clicks,
                    impressions = EXCLUDED.impressions,
                    conversions = EXCLUDED.conversions,
                    raw = EXCLUDED.raw,
                    synced_at = now()
                """,
                [
                    (
                        r["source"], r["campaign_id"], r.get("campaign_name"), r["date"],
                        r.get("spend", 0), r.get("clicks", 0), r.get("impressions", 0),
                        r.get("conversions", 0), psycopg2.extras.Json(r.get("raw", {})),
                    )
                    for r in rows
                ],
                template="(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            )
    return len(rows)


def upsert_funnel_snapshot(rows: list[dict]) -> int:
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO crm_funnel_snapshot
                    (crm, pipeline_id, pipeline_name, status_id, status_name, lead_count, deal_value, date, raw)
                VALUES %s
                ON CONFLICT (crm, pipeline_id, status_id, date) DO UPDATE SET
                    pipeline_name = EXCLUDED.pipeline_name,
                    status_name = EXCLUDED.status_name,
                    lead_count = EXCLUDED.lead_count,
                    deal_value = EXCLUDED.deal_value,
                    raw = EXCLUDED.raw,
                    synced_at = now()
                """,
                [
                    (
                        r["crm"], r["pipeline_id"], r.get("pipeline_name"), r["status_id"],
                        r.get("status_name"), r.get("lead_count", 0), r.get("deal_value", 0),
                        r["date"], psycopg2.extras.Json(r.get("raw", {})),
                    )
                    for r in rows
                ],
                template="(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            )
    return len(rows)


def log_sync(job: str, status: str, message: str = ""):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sync_log (job, status, message) VALUES (%s, %s, %s)",
                (job, status, message),
            )
