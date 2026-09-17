import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

WINDSOR_API_KEY = os.environ["WINDSOR_API_KEY"]

GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")

KOMMO_DOMAIN = os.environ["KOMMO_DOMAIN"]  # ex: leadscalefranchising.kommo.com
KOMMO_ACCESS_TOKEN = os.environ["KOMMO_ACCESS_TOKEN"]

RD_CRM_TOKEN = os.environ["RD_CRM_TOKEN"]
