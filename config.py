import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ВПИШИ сюда свой реальный числовой ID из @userinfobot
ADMIN_ID = 690609335  # замени на свой, если другое число

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # ADMIN_USERNAME=fogcom

WAREHOUSE_ADDRESS = "Южнопортовая ул., 5, стр. 6"
WAREHOUSE_MAP = "https://yandex.ru/profile/1073318465?lang=ru"

ADMIN_PHONE = os.getenv("ADMIN_PHONE")
