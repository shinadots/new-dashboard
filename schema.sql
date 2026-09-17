-- Roda isso no SQL Editor do Supabase do Dashboard-main.
-- meta_ads e google_ads NÃO entram aqui — já existem e são alimentadas pelo Windsor.
-- Essas duas tabelas abaixo são só pro funil de CRM (Kommo + RD Station).

CREATE TABLE IF NOT EXISTS crm_funnel_snapshot (
  id            BIGSERIAL PRIMARY KEY,
  crm           TEXT NOT NULL,          -- 'kommo' | 'rdstation'
  pipeline_id   TEXT NOT NULL,
  pipeline_name TEXT,
  status_id     TEXT NOT NULL,
  status_name   TEXT,
  lead_count    INTEGER DEFAULT 0,
  deal_value    NUMERIC(14,2) DEFAULT 0,
  date          DATE NOT NULL,
  raw           JSONB,
  synced_at     TIMESTAMPTZ DEFAULT now(),
  UNIQUE (crm, pipeline_id, status_id, date)
);

CREATE TABLE IF NOT EXISTS sync_log (
  id          BIGSERIAL PRIMARY KEY,
  job         TEXT NOT NULL,           -- 'kommo' | 'rdstation'
  status      TEXT NOT NULL,           -- 'success' | 'error'
  message     TEXT,
  started_at  TIMESTAMPTZ,
  finished_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_funnel_date ON crm_funnel_snapshot(date);
CREATE INDEX IF NOT EXISTS idx_funnel_crm ON crm_funnel_snapshot(crm);

-- Índices nas tabelas existentes de ads, pra acelerar o filtro de data
-- que o Dashboard-main agora faz direto no Supabase (ver page.tsx atualizado).
-- Ajuste os nomes de coluna se forem diferentes dos que vi no código.
CREATE INDEX IF NOT EXISTS idx_meta_ads_data_inicio ON meta_ads (data_inicio);
CREATE INDEX IF NOT EXISTS idx_google_ads_data_inicio ON google_ads ("dataInicio");
CREATE INDEX IF NOT EXISTS idx_meta_ads_cliente ON meta_ads ("CLIENTE");
CREATE INDEX IF NOT EXISTS idx_google_ads_cliente ON google_ads (cliente);
