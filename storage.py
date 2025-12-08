
# Хранилище данных для Secret Santa (файловое, без SQL)

import json
import os

STORAGE_FILE = "storage_data.json"

# ---------- ДАННЫЕ ПО УМОЛЧАНИЮ ----------
gift_links = {}            # user_id → link на подарок
confirmed = set()          # кто подтвердил участие
assigned = {}              # user_id → кому он дарит
available_targets = {}     # user_id → список доступных целей
numbers_map = {}           # номер → user_id (кто под цифрой)
user_ids = {}              # user_id → username

# ВАЖНО: список разрешённых игроков
ALLOWED_USERS = {
"den_valavin",
    "iliuTb",
    "waterpolist6",
    "derio00",
    "Ayanokoji_Kietak",
    "Rauliokak"
}


# ---------- ЗАГРУЗКА ДАННЫХ ----------
def load_storage():
    global gift_links, confirmed, assigned, available_targets, numbers_map, user_ids

    if not os.path.exists(STORAGE_FILE):
        return

    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        gift_links = data.get("gift_links", {})
        confirmed = set(data.get("confirmed", []))
        assigned = data.get("assigned", {})
        available_targets = data.get("available_targets", {})
        numbers_map = data.get("numbers_map", {})
        user_ids = data.get("user_ids", {})

    except Exception as e:
        print("Ошибка загрузки storage:", e)


# ---------- СОХРАНЕНИЕ ДАННЫХ ----------
def save_storage():
    data = {
        "gift_links": gift_links,
        "confirmed": list(confirmed),
        "assigned": assigned,
        "available_targets": available_targets,
        "numbers_map": numbers_map,
        "user_ids": user_ids
    }

    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print("Ошибка сохранения storage:", e)


# Автозагрузка при импорте
load_storage()
