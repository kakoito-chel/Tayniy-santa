
# Обновлённая версия: вынесено хранилище подарков в отдельный файл storage.py

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from storage import gift_links, confirmed, assigned, available_targets, numbers_map, user_ids, ALLOWED_USERS, save_storage

BOT_TOKEN = "8279064805:AA***********************yJCD81Co"

dp = Dispatcher()

# === ФУНКЦИЯ: создание клавиатуры подтверждения подарка ===
def gift_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Дарите что хотите", callback_data="nopresent")
    return kb.as_markup()

# === ФУНКЦИЯ: клавиатура выбора числа 1–5 ===
def number_keyboard():
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(text=str(i), callback_data=f"pick_{i}")
    kb.adjust(5)
    return kb.as_markup()

# === Рассылка уведомления о готовности ===
async def notify_all_ready(bot: Bot):
    for uname in ALLOWED_USERS:
        if uname in user_ids:
            try:
                await bot.send_message(user_ids[uname], "Все подтвердили участие! Можете выбирать число — /start")
            except:
                pass

# === START ===
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    username = message.from_user.username
    if username:
        user_ids[username] = message.from_user.id
        save_storage()

    if username not in ALLOWED_USERS:
        return await message.answer("❌ У вас нет доступа к этому боту.")

    if username in assigned:
        return await message.answer("🎁 Вы уже получили своего Тайного Санту!")

    # Если подарок есть → показать статус
    if username in gift_links:
        lines = ["Статус участников (в реальном времени):\n"]
        for uname in sorted(ALLOWED_USERS):
            if uname in gift_links:
                link = gift_links[uname]
                if link:
                    lines.append(f"✔ @{uname} — выбрал(а)")
                else:
                    lines.append(f"✔ @{uname} — выбрал(а)")
            else:
                lines.append(f"⏳ @{uname} — ещё не выбрал(а) подарок")

        if len(confirmed) == len(ALLOWED_USERS):
            lines.append("\nВсе подтвердили участие — можешь выбрать номер: /start")

        return await message.answer("\n".join(lines))

    # Нужно выбрать подарок
    return await message.answer(
        "Привет! Пришли ссылку на подарок 🎁 или нажми кнопку ниже:",
        reply_markup=gift_keyboard()
    )

# === Ссылка на подарок ===
@dp.message()
async def gift_link_handler(message: Message):
    username = message.from_user.username
    if username not in ALLOWED_USERS:
        return

    # Если игра уже началась → менять нельзя
    if len(confirmed) == len(ALLOWED_USERS):
        return await message.answer("Игра уже началась — менять подарок нельзя.")

    prior = gift_links.get(username)
    gift_links[username] = message.text.strip()
    confirmed.add(username)
    save_storage()

    if prior is None:
        await message.answer("Подарок сохранён! 🎁")
    else:
        await message.answer("Подарок обновлён! 🎁")

    if len(confirmed) == len(ALLOWED_USERS):
        await notify_all_ready(message.bot)

# === Нажали «Дарите что хотите» ===
@dp.callback_query(F.data == "nopresent")
async def no_present(callback: CallbackQuery):
    username = callback.from_user.username
    if username not in ALLOWED_USERS:
        return await callback.answer("Нет доступа.")

    if len(confirmed) == len(ALLOWED_USERS):
        return await callback.message.answer("Игра уже началась — менять выбор нельзя.")

    prior = gift_links.get(username)
    gift_links[username] = None
    confirmed.add(username)
    save_storage()

    if prior is None:
        await callback.message.answer("Отлично! Вы выбрали: «Дарите что хотите» 🎉")
    else:
        await callback.message.answer("Вы сменили свой выбор на: «Дарите что хотите» 🎉")

    if len(confirmed) == len(ALLOWED_USERS):
        await notify_all_ready(callback.message.bot)

    await callback.answer()

# === Подготовка случайных чисел ===
async def prepare_random_numbers(username: str, message: Message):
    import random

    possible = list(available_targets - {username})
    random.shuffle(possible)
    numbers_map[username] = possible[:5]
    save_storage()

    await message.answer("Выберите число от 1 до 5:", reply_markup=number_keyboard())

# === Выбор числа ===
@dp.callback_query(F.data.startswith("pick_"))
async def pick_number(callback: CallbackQuery):
    username = callback.from_user.username

    if username not in numbers_map:
        return await callback.answer("Ошибка: номера не готовы. Напишите /start.")

    number = int(callback.data.split("_")[1])
    mapping = numbers_map[username]

    if number > len(mapping):
        return await callback.answer("Это число недоступно.")

    target = mapping[number - 1]

    if target not in available_targets:
        return await callback.answer("Этого человека уже выбрали.")

    assigned[username] = target
    available_targets.remove(target)
    save_storage()

    gift = gift_links.get(target)
    text = f"🎁 Вы вытянули: @{target}"
    if gift:
        text += f"\nСсылка на подарок: {gift}"

    await callback.message.answer(text)
    await callback.answer()

# === MAIN ===
async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
