from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
import keyboards
import database
from states import ClientForm, AdminStates

from keyboards import (
    get_contact_request_keyboard,
    get_step_nav_keyboard,
    get_preview_keyboard,
    get_admin_panel_keyboard,
)

router = Router()


# ===== СТАРТ =====

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Старт бота"""
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в Fulfillment Helper!\n\n"
        "Я помогу вам быстро рассчитать стоимость услуг и передать заявку нашему специалисту.\n\n"
        "Нажмите '📦 Рассчитать стоимость' или воспользуйтесь меню ниже:",
        reply_markup=keyboards.get_main_menu(
            is_admin=(message.from_user.id == config.ADMIN_ID)
        ),
    )


# ===== НАЧАЛО АНКЕТЫ =====

@router.message(F.text == "📦 Рассчитать стоимость")
async def start_calculation(message: Message, state: FSMContext):
    """Начало сбора информации — шаг 1: товар"""
    await state.clear()
    await state.set_state(ClientForm.waiting_for_category)
    await message.answer(
        "📦 **Шаг 1/7: Какой у вас товар?**\n\n"
        "Напишите категорию (примеры: обувь, одежда, игрушки, техника, косметика, электроника, посуда, книги и т.д.)",
        parse_mode="Markdown",
        reply_markup=None,
    )


# ===== ОБРАБОТКА ТЕКСТА ПО ШАГАМ =====

@router.message(ClientForm.waiting_for_category)
async def process_category(message: Message, state: FSMContext):
    """Шаг 1: категория товара"""
    await state.update_data(category=message.text)

    await state.set_state(ClientForm.waiting_for_quantity)
    await message.answer(
        f"✅ Товар: **{message.text}**\n\n"
        "📊 **Шаг 2/7: Сколько товара?**\n\n"
        "Напишите количество (пример: 100 шт, 50 пар, 200 упаковок и т.д.):",
        parse_mode="Markdown",
        reply_markup=get_step_nav_keyboard(can_go_back=True),
    )


@router.message(ClientForm.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    """Шаг 2: количество"""
    await state.update_data(quantity=message.text)

    await state.set_state(ClientForm.waiting_for_task)
    await message.answer(
        f"✅ Количество: **{message.text}**\n\n"
        "📋 **Шаг 3/7: Техническое задание**\n\n"
        "Опишите, что именно нужно сделать с товаром.\n"
        "Примеры: 'упаковка в брендированную коробку + маркировка Ozon + доставка на склад WB',\n"
        "'просто хранение 30 дней + упаковка по 5 шт',\n"
        "'маркировка штрихкодов + групповые коробки'\n\n"
        "Можете отправить файл с ТЗ:",
        parse_mode="Markdown",
        reply_markup=get_step_nav_keyboard(),
    )


@router.message(ClientForm.waiting_for_task)
async def process_task(message: Message, state: FSMContext):
    """Шаг 3: ТЗ"""
    await state.update_data(task=message.text)

    await state.set_state(ClientForm.waiting_for_marketplace)
    await message.answer(
        f"✅ ТЗ: **{message.text[:100]}...**\n\n"
        "🛒 **Шаг 4/7: Какой маркетплейс?**\n\n"
        "Напишите платформу (Ozon, Wildberries, Яндекс.Маркет, Avito, Lamoda и т.д.):",
        parse_mode="Markdown",
        reply_markup=get_step_nav_keyboard(),
    )


@router.message(ClientForm.waiting_for_marketplace)
async def process_marketplace(message: Message, state: FSMContext):
    """Шаг 4: маркетплейс"""
    await state.update_data(marketplace=message.text)

    await state.set_state(ClientForm.full_name)
    await message.answer(
        f"✅ Маркетплейс: **{message.text}**\n\n"
        "👤 **Шаг 5/7: Ваше ФИО**\n\n"
        "Пожалуйста, введите ваше ФИО полностью.",
        parse_mode="Markdown",
        reply_markup=get_step_nav_keyboard(),
    )


@router.message(ClientForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Шаг 5: ФИО"""
    await state.update_data(full_name=message.text)

    await state.set_state(ClientForm.waiting_for_phone)
    await message.answer(
        f"✅ ФИО: **{message.text}**\n\n"
        "📱 **Шаг 6/7: Номер телефона**\n\n"
        "Отправьте номер для связи с нашим специалистом.\n"
        "Можно нажать кнопку ниже, чтобы автоматически отправить контакт.",
        reply_markup=get_contact_request_keyboard(),
        parse_mode="Markdown",
    )


@router.message(ClientForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Шаг 6: телефон, затем переход к предпросмотру"""
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)

    await state.set_state(ClientForm.preview)
    data = await state.get_data()

    text = (
        "📄 **Проверьте заявку перед отправкой:**\n\n"
        f"📦 Товар: **{data.get('category', '-') }**\n"
        f"📊 Количество: **{data.get('quantity', '-') }**\n"
        f"📋 ТЗ: **{data.get('task', '-') }**\n"
        f"🛒 Маркетплейс: **{data.get('marketplace', '-') }**\n"
        f"👤 ФИО: **{data.get('full_name', '-') }**\n"
        f"📱 Телефон: **{data.get('phone', '-') }**\n\n"
        "Если всё верно — отправьте заявку админу.\n"
        "Если нужно что‑то поправить — выберите «Редактировать»."
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=get_preview_keyboard())


# ===== НАВИГАЦИЯ ПО ШАГАМ =====

@router.callback_query(F.data == "step_back")
async def step_back(call: CallbackQuery, state: FSMContext):
    """Кнопка «Назад» — переход к предыдущему шагу"""
    current_state = await state.get_state()

    if current_state == ClientForm.waiting_for_quantity.state:
        await state.set_state(ClientForm.waiting_for_category)
        data = await state.get_data()
        await call.message.edit_text(
            "📦 **Шаг 1/7: Какой у вас товар?**\n\n"
            f"Текущее значение: **{data.get('category', 'не заполнено')}**\n\n"
            "Введите категорию ещё раз, если хотите изменить.",
            parse_mode="Markdown",
        )

    elif current_state == ClientForm.waiting_for_task.state:
        await state.set_state(ClientForm.waiting_for_quantity)
        data = await state.get_data()
        await call.message.edit_text(
            "📊 **Шаг 2/7: Сколько товара?**\n\n"
            f"Текущее значение: **{data.get('quantity', 'не заполнено')}**\n\n"
            "Введите количество ещё раз, если хотите изменить.",
            parse_mode="Markdown",
            reply_markup=get_step_nav_keyboard(can_go_back=True),
        )

    elif current_state == ClientForm.waiting_for_marketplace.state:
        await state.set_state(ClientForm.waiting_for_task)
        data = await state.get_data()
        await call.message.edit_text(
            "📋 **Шаг 3/7: Техническое задание**\n\n"
            f"Текущее значение: **{data.get('task', 'не заполнено')[:100]}...**\n\n"
            "Отправьте новое ТЗ, если нужно изменить.",
            parse_mode="Markdown",
            reply_markup=get_step_nav_keyboard(),
        )

    elif current_state == ClientForm.full_name.state:
        await state.set_state(ClientForm.waiting_for_marketplace)
        data = await state.get_data()
        await call.message.edit_text(
            "🛒 **Шаг 4/7: Какой маркетплейс?**\n\n"
            f"Текущее значение: **{data.get('marketplace', 'не заполнено')}**\n\n"
            "Введите платформу ещё раз, если нужно изменить.",
            parse_mode="Markdown",
            reply_markup=get_step_nav_keyboard(),
        )

    elif current_state == ClientForm.waiting_for_phone.state:
        await state.set_state(ClientForm.full_name)
        data = await state.get_data()
        await call.message.edit_text(
            "👤 **Шаг 5/7: Ваше ФИО**\n\n"
            f"Текущее значение: **{data.get('full_name', 'не заполнено')}**\n\n"
            "Введите ФИО ещё раз, если хотите изменить.",
            parse_mode="Markdown",
            reply_markup=get_step_nav_keyboard(),
        )

    await call.answer()


@router.callback_query(F.data == "step_next")
async def step_next(call: CallbackQuery, state: FSMContext):
    """Кнопка «Далее» — подсказка по текущему шагу"""
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == ClientForm.waiting_for_category.state:
        text = (
            "📦 **Шаг 1/7: Какой у вас товар?**\n\n"
            f"Текущее значение: **{data.get('category', 'не заполнено')}**\n\n"
            "Введите категорию товара."
        )
    elif current_state == ClientForm.waiting_for_quantity.state:
        text = (
            "📊 **Шаг 2/7: Сколько товара?**\n\n"
            f"Текущее значение: **{data.get('quantity', 'не заполнено')}**\n\n"
            "Введите количество."
        )
    elif current_state == ClientForm.waiting_for_task.state:
        text = (
            "📋 **Шаг 3/7: Техническое задание**\n\n"
            f"Текущее значение: **{data.get('task', 'не заполнено')[:100]}...**\n\n"
            "Опишите, что нужно сделать."
        )
    elif current_state == ClientForm.waiting_for_marketplace.state:
        text = (
            "🛒 **Шаг 4/7: Какой маркетплейс?**\n\n"
            f"Текущее значение: **{data.get('marketplace', 'не заполнено')}**\n\n"
            "Введите название платформы."
        )
    elif current_state == ClientForm.full_name.state:
        text = (
            "👤 **Шаг 5/7: Ваше ФИО**\n\n"
            f"Текущее значение: **{data.get('full_name', 'не заполнено')}**\n\n"
            "Введите ФИО."
        )
    elif current_state == ClientForm.waiting_for_phone.state:
        text = (
            "📱 **Шаг 6/7: Номер телефона**\n\n"
            f"Текущее значение: **{data.get('phone', 'не заполнено')}**\n\n"
            "Отправьте номер или нажмите кнопку контакта."
        )
    else:
        text = "Продолжайте заполнять анкету."

    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_step_nav_keyboard(
            can_go_back=current_state != ClientForm.waiting_for_category.state
        ),
    )
    await call.answer()


# ===== ПРЕДПРОСМОТР =====

@router.callback_query(ClientForm.preview, F.data == "edit_form")
async def preview_edit(call: CallbackQuery, state: FSMContext):
    """Вернуться к редактированию с начала (шаг 1)"""
    await state.set_state(ClientForm.waiting_for_category)
    data = await state.get_data()

    await call.message.edit_text(
        "📦 **Шаг 1/7: Какой у вас товар?**\n\n"
        f"Текущее значение: **{data.get('category', 'не заполнено')}**\n\n"
        "Введите категорию ещё раз, если хотите изменить.",
        parse_mode="Markdown",
    )
    await call.answer()


@router.callback_query(ClientForm.preview, F.data == "submit_form")
async def preview_submit(call: CallbackQuery, state: FSMContext):
    """Отправка итоговой заявки админу и клиенту"""
    data = await state.get_data()

    username = call.from_user.username or "не указан"
    first_name = call.from_user.first_name or "не указан"
    full_name = data.get("full_name", first_name)
    phone = data.get("phone", "не указан")

    await database.save_client_data(
        call.from_user.id,
        username,
        full_name,
        data.get("category"),
        data.get("quantity"),
        data.get("task"),
        data.get("marketplace"),
        phone,
    )

    admin_text = (
        f"✅ **НОВАЯ ЗАЯВКА #{call.from_user.id}**\n\n"
        f"👤 ФИО: {full_name}\n"
        f"TG: @{username}\n"
        f"🆔 ID: `{call.from_user.id}`\n\n"
        f"📦 Товар: {data.get('category')}\n"
        f"📊 Количество: {data.get('quantity')}\n"
        f"📋 ТЗ: {data.get('task')}\n"
        f"🛒 Маркетплейс: {data.get('marketplace')}\n"
        f"📱 Телефон: `{phone}`\n\n"
        f"🔗 [Связаться в TG](tg://user?id={call.from_user.id})"
    )

    try:
        await call.bot.send_message(
            config.ADMIN_ID,
            admin_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        pdf = FSInputFile("calculations.pdf")
        await call.bot.send_document(
            config.ADMIN_ID, pdf, caption="📊 Расчеты услуг"
        )
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

    await call.message.edit_text(
        f"✅ **Заявка отправлена!**\n\n"
        f"👤 ФИО: **{full_name}**\n"
        f"📱 Номер: **{phone}**\n"
        f"⏰ Наш специалист свяжется в течение рабочего времени с 8:00 до 19:00 \n\n"
        f"📍 **Адрес склада**:\n{config.WAREHOUSE_ADDRESS}\n\n"
        f"📞 **Контакты специалиста**:",
        parse_mode="Markdown",
    )
    try:
        pdf = FSInputFile("calculations.pdf")
        await call.message.answer_document(
            pdf, caption="📊 Расчеты услуг (PDF)"
        )
    except Exception as e:
        await call.message.answer("💾 Файл расчетов будет отправлен специалистом")

    await state.clear()
    await call.message.answer(
        "🔄 Нажмите 'Начать заново' для новой заявки",
        reply_markup=keyboards.get_restart_keyboard(),
    )
    await call.answer()


# ===== ПРОЧИЕ КОМАНДЫ =====

@router.message(F.text == "🔄 Начать заново")
async def restart(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)


@router.message(F.text == "📍 Адрес склада")
async def show_warehouse(message: Message):
    await message.answer(
        f"📍 **Склад находится по адресу**:\n\n**{config.WAREHOUSE_ADDRESS}**\n\n"
        "🗺️ Нажмите кнопку ниже:",
        reply_markup=keyboards.get_location_keyboard(),
        parse_mode="Markdown",
    )


@router.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    await message.answer(
        "👨‍💼 **Наш специалист** всегда готов помочь!\n\n"
        f"📞 Телефон: `{config.ADMIN_PHONE}`\n\n"
        "💬 Напишите напрямую:",
        reply_markup=keyboards.get_contacts_keyboard(),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


# ===== АДМИН-ПАНЕЛЬ МЕНЮ =====

@router.message(F.text == "🛠 Управление заявками")
async def admin_panel_menu(message: Message):
    """Открываем меню админ-панели"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("Эта функция доступна только администратору.")
        return

    # Получаем последние сообщения в чате
    try:
        chat_messages = await message.bot.get_chat_messages(chat_id=message.chat.id, limit=50)
        for msg in chat_messages:
            if msg.from_user.id == config.ADMIN_ID and msg.text not in ["📦 Рассчитать стоимость", "📍 Адрес склада", "📞 Контакты", "🔄 Начать заново", "❓ Помощь"]:
                try:
                    await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                except Exception as e:
                    print(f"Ошибка удаления сообщения: {e}")
    except Exception as e:
        print(f"Ошибка получения истории чата: {e}")

    await message.answer(
        "Выберите действие:",
        reply_markup=get_admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_new_requests")
async def admin_new_requests(call: CallbackQuery):
    """Список новых заявок с кнопками 'Принять'/'Отклонить'"""
    # Удаляем предыдущее сообщение админа
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)

    requests = await database.get_requests_for_admin(status="new", limit=10)
    if not requests:
        await call.message.answer("Новых заявок пока нет.")
        return

    # Собираем текст для всех заявок
    text = "📋 Новые заявки:\n\n"
    for r in requests:
        name = r.get("full_name") or "Без имени"
        telegram_id = r.get("telegram_id") or "Не указан"
        phone = r.get("phone") or "Не указан"
        username = r.get("username") or "Не указан"
        text += (
            f"#{r['id']} — {name}\n"
            f"🆔 ID: {telegram_id}\n"
            f"📞 Телефон: {phone}\n"
            f"👤 TG: @{username}\n"
            f"📦 {r.get('category')} | 📊 {r.get('quantity')}\n"
            f"🛒 {r.get('marketplace')}\n"
            f"{'— — —'}\n"
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="< Меню", callback_data="admin_panel_menu"
                ),
            ],
        ]
    )
    await call.message.answer(text, reply_markup=kb)

    # Отдельно отправляем кнопки для каждой заявки
    for r in requests:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Принять", callback_data=f"req_accept:{r['id']}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отклонить", callback_data=f"req_reject:{r['id']}"
                    ),
                ],
            ]
        )
        await call.message.answer(f"#{r['id']}", reply_markup=kb)

    await call.answer()


@router.callback_query(F.data == "admin_history")
async def admin_history(call: CallbackQuery):
    """История всех заявок одним сообщением"""
    # Удаляем предыдущее сообщение админа
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)

    requests = await database.get_requests_for_admin(status=None, limit=20)
    if not requests:
        await call.message.answer("Заявок пока нет.")
        return

    # Собираем текст для всех заявок
    text = "📜 История заявок:\n\n"
    for r in requests:
        name = r.get("full_name") or "Без имени"
        status = r.get("status", "new")
        text += (
            f"#{r['id']} — {name}\n"
            f"📦 {r.get('category')} | 📊 {r.get('quantity')}\n"
            f"🛒 {r.get('marketplace')} | 📱 {r.get('phone')}\n"
            f"📌 Статус: {status}\n"
            f"{'— — —'}\n"
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="< Меню", callback_data="admin_panel_menu"
                ),
            ],
        ]
    )
    await call.message.answer(text, reply_markup=kb)

    await call.answer()


# ===== ПРИНЯТЬ/ОТКЛОНИТЬ =====

@router.callback_query(F.data.startswith("req_accept:"))
async def admin_accept_request(call: CallbackQuery):
    """Админ нажал 'Принять' — меняем статус и шлём клиенту сообщение"""
    if call.from_user.id != config.ADMIN_ID:
        await call.answer("Не для тебя эта кнопка.", show_alert=True)
        return

    parts = call.data.split(":")
    request_id = int(parts[1])

    # Получаем данные заявки
    requests = await database.get_requests_for_admin(status=None, limit=100)
    req = next((r for r in requests if r["id"] == request_id), None)

    if not req:
        await call.answer("Заявка не найдена.", show_alert=True)
        return

    await database.update_request_status(request_id, "accepted")

    full_name = req.get("full_name") or "клиент"
    user_id = req["telegram_id"]

    text_client = (
        f"Добрый день, {full_name}!\n\n"
        "Ваша заявка принята, наши специалисты скоро с вами свяжутся "
        "для уточнения деталей. Спасибо, что выбрали нашу компанию!"
    )

    try:
        await call.bot.send_message(user_id, text_client)
    except Exception as e:
        print(f"Ошибка отправки клиенту: {e}")

    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("Заявка принята, клиенту отправлено сообщение.")


@router.callback_query(F.data.startswith("req_reject:"))
async def admin_reject_request(call: CallbackQuery, state: FSMContext):
    """Админ нажал 'Отклонить' — меняем статус и запрашиваем причину"""
    if call.from_user.id != config.ADMIN_ID:
        await call.answer("Не для тебя эта кнопка.", show_alert=True)
        return

    parts = call.data.split(":")
    request_id = int(parts[1])

    # Получаем данные заявки
    requests = await database.get_requests_for_admin(status=None, limit=100)
    req = next((r for r in requests if r["id"] == request_id), None)

    if not req:
        await call.answer("Заявка не найдена.", show_alert=True)
        return

    # Сохраняем ID заявки и ID клиента в FSM
    await state.set_state(AdminStates.waiting_reject_reason)
    await state.update_data(request_id=request_id, telegram_id=req["telegram_id"])

    await call.message.answer("Введите причину отклонения заявки:")
    await call.answer()


@router.message(AdminStates.waiting_reject_reason)
async def admin_reject_reason(message: Message, state: FSMContext):
    """Админ ввёл причину отклонения"""
    data = await state.get_data()
    request_id = data.get("request_id")
    telegram_id = data.get("telegram_id")
    reason = message.text

    # Обновляем статус заявки
    await database.update_request_status(request_id, "rejected", reason)

    # Отправляем сообщение клиенту
    text_client = (
        f"Добрый день!\n\n"
        f"К сожалению, ваша заявка отклонена по причине:\n"
        f"{reason}\n\n"
        "Если у вас есть вопросы — свяжитесь с нами."
    )

    try:
        await message.bot.send_message(telegram_id, text_client)
        await message.answer(f"Вы отменили заявку №{request_id}, клиент уведомлён об отмене.")
    except Exception as e:
        await message.answer(f"Ошибка отправки клиенту: {e}")

    # Завершаем FSM
    await state.clear()

@router.callback_query(F.data == "admin_panel_menu")
async def back_to_menu(call: CallbackQuery):
    """Вернуться в главное меню админа"""
    # Удаляем предыдущее сообщение админа
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)

    await call.message.answer(
        "Выберите действие:",
        reply_markup=get_admin_panel_keyboard()
    )
    await call.answer()


@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    await message.answer(
        "🆘 **Как пользоваться ботом:**\n\n"
        "1️⃣ Нажмите 'Рассчитать стоимость'\n"
        "2️⃣ Ответьте на вопросы\n"
        "3️⃣ Проверьте анкету и отправьте заявку\n\n"
        "⏰ **Скорость ответа**: 30 минут\n"
        "🔒 **Конфиденциальность**: 100% защита данных",
        parse_mode="Markdown",
        reply_markup=keyboards.get_main_menu(
            is_admin=(message.from_user.id == config.ADMIN_ID)
        ),
    )
