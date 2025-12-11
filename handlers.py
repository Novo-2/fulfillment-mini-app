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
        "📊 **Шаг 2/7: Сколько единиц товара?**\n\n"
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
        "Примеры: 'упаковка в брендированную коробку + маркировка Ozon + доставка на склад',\n"
        "'просто хранение 30 дней + упаковка ',\n"
        "'маркировка штрихкодов + отправка на склад '\n\n"
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
    except Exception:
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
    text = (
        "👨‍💼 **Администратор:** Каушутов Арслан Перманович\n"
        "📞 Телефон: +7 995 916 38 77\n"
        "⏰ Рабочие часы: с 8:00 до 20:00\n\n"
        "💬 Напишите нам или позвоните, если остались вопросы."
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.get_contacts_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(F.text == "📄 Наш прайс")
async def send_price(message: Message):
    price = FSInputFile("Aktualnyi-Prais_FF_captain_fullfill-2.pdf")
    await message.answer_document(
        price,
        caption="Актуальный прайс-лист Fulfillment Helper",
    )


# ===== АДМИН-ПАНЕЛЬ МЕНЮ =====
# (всё, что ниже, оставляй как у тебя было — можно просто вернуть свой блок admin-панели без изменений)
