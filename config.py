import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Числовой Telegram ID админа
ADMIN_ID = 690609335

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # пример: HelpCaptainFF

WAREHOUSE_ADDRESS = "Южнопортовая ул., 5, стр. 6"
WAREHOUSE_MAP = "https://yandex.ru/maps/213/moscow/?ll=37.688854%2C55.707964&mode=routes&rtext=55.708237%2C37.688749&rtt=mt&ruri=&z=18.52"

ADMIN_PHONE = os.getenv("ADMIN_PHONE")  # пример: +7 995 916 38 77
