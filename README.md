# ETL em Python (substitui o workflow n8n)

Mesma lógica do backend Next.js, só que a extração roda aqui em vez de no n8n.
Grava nas mesmas tabelas (`ad_performance`, `crm_funnel_snapshot`) — o backend
Next.js e o frontend não mudam nada.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crie um `.env` com as mesmas variáveis do backend Next.js:
```
DATABASE_URL=
WINDSOR_API_KEY=
KOMMO_DOMAIN=
KOMMO_ACCESS_TOKEN=
RD_CRM_TOKEN=
# GOOGLE_ADS_* — só se for usar services/google_ads.py
```

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
   cadastre cada uma das variáveis do `.env` (`DATABASE_URL`, `WINDSOR_API_KEY`,
   `KOMMO_DOMAIN`, `KOMMO_ACCESS_TOKEN`, `RD_CRM_TOKEN`).
3. Pronto — o workflow já roda sozinho às 8h. Pra testar sem esperar o horário,
   vá na aba **Actions → Sync diário do dashboard → Run workflow**.

O banco (Postgres) precisa estar acessível pela internet, já que o job roda
nos servidores do GitHub — um Postgres gerenciado (Supabase, Neon, Railway)
resolve isso sem configuração extra de rede.

## Alternativa sem GitHub Actions
Cron job de um provedor (Railway, Render, Fly.io) — todos têm "scheduled jobs"
nativos, se preferir rodar fora do GitHub.
