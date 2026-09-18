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

KOMMO_DOMAIN = os.environ["KOMMO_DOMAIN"]  # ex: leadscalefranchising.kommo.com
KOMMO_ACCESS_TOKEN = os.environ["KOMMO_ACCESS_TOKEN"]

RD_CRM_TOKEN = os.environ["RD_CRM_TOKEN"]
