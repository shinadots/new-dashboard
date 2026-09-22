import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]  # connection string do Supabase do Dashboard-main

# Google não precisa mais de developer token (Google aposentou esse modelo em
# set/2026) — o acesso agora é ligado ao projeto do Google Cloud dono do
# Client ID/Secret. LOGIN_CUSTOMER_ID é o ID da conta MCC/gerenciadora (sem
# hífens), necessário pra acessar as contas de cliente por baixo dela.
GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

KOMMO_DOMAIN = os.environ.get("KOMMO_DOMAIN")  # ex: leadscalefranchising.kommo.com
KOMMO_ACCESS_TOKEN = os.environ.get("KOMMO_ACCESS_TOKEN")

# RD_CRM_TOKEN não existe mais aqui — cada cliente tem seu próprio token,
# guardado na tabela rd_config do Supabase (ver db.get_rd_config()).
