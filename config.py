import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]  # connection string do Supabase do Dashboard-main

# Windsor não entra mais aqui — grava direto em meta_ads/google_ads no Supabase.
# GOOGLE_ADS_* abaixo só é necessário se algum dia precisar do services/google_ads.py.
GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")

KOMMO_DOMAIN = os.environ["KOMMO_DOMAIN"]  # ex: leadscalefranchising.kommo.com
KOMMO_ACCESS_TOKEN = os.environ["KOMMO_ACCESS_TOKEN"]

RD_CRM_TOKEN = os.environ["RD_CRM_TOKEN"]
