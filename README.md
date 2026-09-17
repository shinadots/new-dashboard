# ETL em Python — funil de CRM pro Dashboard-main

Esse script cuida só do que falta no Supabase do **Dashboard-main**: o funil de
CRM (Kommo + RD Station). Anúncios (`meta_ads`, `google_ads`) já são gravados
direto pelo Windsor — esse ETL não mexe nisso.

Grava numa tabela nova, `crm_funnel_snapshot`, no mesmo Supabase do
Dashboard-main (ver `schema.sql`).

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crie um `.env`:
```
DATABASE_URL=          # connection string do Supabase do Dashboard-main
                        # (Project Settings → Database → Connection string, modo "URI")
KOMMO_DOMAIN=
KOMMO_ACCESS_TOKEN=
RD_CRM_TOKEN=
```

Rode o `schema.sql` no SQL Editor do Supabase (cria `crm_funnel_snapshot`,
`sync_log` e os índices de performance nas tabelas de ads existentes).

Teste rodando uma vez:
```bash
python main.py
```

## Agendar para todo dia às 8h — Opção 1: crontab (recomendado)
Mais simples e não precisa de processo rodando o dia todo. No servidor:

```bash
crontab -e
```

Adicione (ajuste os paths e o timezone do servidor, ou prefixe com `TZ=America/Sao_Paulo`):
```
TZ=America/Sao_Paulo
0 8 * * * cd /caminho/do/projeto && /caminho/do/projeto/venv/bin/python main.py >> /var/log/dashboard-etl.log 2>&1
```

## Agendar para todo dia às 8h — Opção 2: APScheduler
Se preferir manter um processo Python rodando (ex: dentro de um container/worker
que já fica no ar), use:

```bash
python scheduler.py
```

Ele mesmo dispara `run_sync()` todo dia às 08:00 (America/Sao_Paulo) e fica
esperando — precisa de algo tipo `pm2`, `supervisor` ou um serviço systemd pra
garantir que reinicia se cair.

## Opção 3: GitHub Actions (recomendado — já incluído neste projeto)
Já tem o workflow em `.github/workflows/daily-sync.yml`, agendado pra rodar
todo dia às 08:00 (horário de Brasília). Não precisa de servidor nenhum —
o próprio GitHub dispara o job. Passo a passo:

1. Suba este projeto pra um repositório no GitHub (pode ser privado).
2. Em **Settings → Secrets and variables → Actions → New repository secret**,
   cadastre cada uma das variáveis do `.env` (`DATABASE_URL`, `KOMMO_DOMAIN`,
   `KOMMO_ACCESS_TOKEN`, `RD_CRM_TOKEN`).
3. Pronto — o workflow já roda sozinho às 8h. Pra testar sem esperar o horário,
   vá na aba **Actions → Sync diário do dashboard → Run workflow**.

O banco (Postgres) precisa estar acessível pela internet, já que o job roda
nos servidores do GitHub — um Postgres gerenciado (Supabase, Neon, Railway)
resolve isso sem configuração extra de rede.

## Alternativa sem GitHub Actions
Cron job de um provedor (Railway, Render, Fly.io) — todos têm "scheduled jobs"
nativos, se preferir rodar fora do GitHub.
