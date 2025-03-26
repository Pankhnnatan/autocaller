
import os
import json
import time
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import pytz

# Загрузка переменных из .env
load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Загрузка конфигурации
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

FROM = cfg["from_number"]
TO = cfg["to_number"]
DURATION = cfg["call_duration"]
ATTEMPTS = cfg["max_attempts"]
INTERVAL = cfg["interval_seconds"]
NAME = cfg["name"]
riga_tz = pytz.timezone("Europe/Riga")
START_TIME = riga_tz.localize(datetime.strptime(cfg["start_time"], "%Y-%m-%d %H:%M:%S"))
UNTIL_ANSWERED = cfg.get("repeat_until_answered", False)

def is_valid_number(num):
    return num.startswith('+') and num[1:].replace(" ", "").isdigit()

def is_trial_account():
    return 'trial' in client.api.accounts(ACCOUNT_SID).fetch().status.lower()

def check_numbers():
    if not is_valid_number(FROM):
        raise ValueError(f"FROM номер некорректен: {FROM}")
    if not is_valid_number(TO):
        raise ValueError(f"TO номер некорректен: {TO}")
    if FROM == TO:
        raise ValueError("FROM и TO номера не должны совпадать")
    if is_trial_account():
        verified_numbers = [v.phone_number for v in client.outgoing_caller_ids.list()]
        if TO not in verified_numbers:
            raise ValueError(f"На trial-аккаунте можно звонить только на Verified номера. TO: {TO} не подтверждён.")

# Проверка
check_numbers()

print(f"[{datetime.now()}] Ожидание запуска задачи '{NAME}' в {START_TIME}")
while datetime.now(riga_tz) < START_TIME:
    time.sleep(5)

print(f"[{datetime.now()}] Запуск автозвонка: '{NAME}'")
attempt = 1
while True:
    print(f"[{datetime.now()}] Попытка {attempt} звонка на {TO}")

    call = client.calls.create(
        to=TO,
        from_=FROM,
        url="http://demo.twilio.com/docs/voice.xml",
        timeout=DURATION
    )

    print(f"Call SID: {call.sid}, Статус: {call.status}")
    time.sleep(5)

    call_status = client.calls(call.sid).fetch().status
    print(f"[{datetime.now()}] Результат звонка: {call_status}")

    if call_status in ["completed", "in-progress"]:
        print("✅ Ответ получен. Завершаем.")
        break

    attempt += 1
    if not UNTIL_ANSWERED and attempt > ATTEMPTS:
        print("❌ Достигнуто максимальное количество попыток.")
        break

    print(f"Ожидание {INTERVAL} секунд до следующей попытки...")
    time.sleep(INTERVAL)

print("✅ Все попытки завершены.")
