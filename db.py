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
    # Não é mais usada, deixei só de referência de padrão de upsert.
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


def get_google_ads_customer_ids() -> list[str]:
    """IDs de conta do Google Ads de cada cliente, vindos do clientes_config
    (mesma tabela que já usamos pra Gestor/Squad/meta de CPL)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT conta_google_id FROM clientes_config "
                "WHERE conta_google_id IS NOT NULL AND conta_google_id <> ''"
            )
            return [row[0] for row in cur.fetchall()]


def upsert_google_ads(rows: list[dict]) -> int:
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO google_ads
                    (date, account_id, account_name, campaign, clicks, spend, conversions)
                VALUES %s
                ON CONFLICT (date, account_id, campaign) DO UPDATE SET
                    account_name = EXCLUDED.account_name,
                    clicks = EXCLUDED.clicks,
                    spend = EXCLUDED.spend,
                    conversions = EXCLUDED.conversions,
                    synced_at = now()
                """,
                [
                    (
                        r["date"], r["account_id"], r.get("account_name"), r["campaign"],
                        r.get("clicks", 0), r.get("spend", 0), r.get("conversions", 0),
                    )
                    for r in rows
                ],
                template="(%s,%s,%s,%s,%s,%s,%s)",
            )
    return len(rows)


def upsert_funnel_snapshot(rows: list[dict]) -> int:
    # Mantida só de referência — o ETL não escreve mais aqui (ver upsert_crm_leads).
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


def upsert_crm_leads(rows: list[dict]) -> int:
    if not rows:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO crm_leads
                    (crm, lead_id, pipeline_id, pipeline_name, status_id, status_name, price, created_at, updated_at)
                VALUES %s
                ON CONFLICT (crm, lead_id) DO UPDATE SET
                    pipeline_id = EXCLUDED.pipeline_id,
                    pipeline_name = EXCLUDED.pipeline_name,
                    status_id = EXCLUDED.status_id,
                    status_name = EXCLUDED.status_name,
                    price = EXCLUDED.price,
                    updated_at = EXCLUDED.updated_at,
                    synced_at = now()
                """,
                [
                    (
                        r["crm"], r["lead_id"], r.get("pipeline_id"), r.get("pipeline_name"),
                        r.get("status_id"), r.get("status_name"), r.get("price", 0),
                        r.get("created_at"), r.get("updated_at"),
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
