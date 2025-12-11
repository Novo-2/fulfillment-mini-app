from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import config


def get_main_menu(is_admin: bool = False):
    """Главное меню"""
    rows = [
        [KeyboardButton(text="📦 Рассчитать стоимость")],
        [KeyboardButton(text="📍 Адрес склада"), KeyboardButton(text="📞 Контакты")],
    ]

    if is_admin:
        rows.append([KeyboardButton(text="🛠 Управление заявками")])

    rows.append([KeyboardButton(text="❓ Помощь")])

    kb = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return kb


def get_restart_keyboard():
    """Кнопка начать заново"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Начать заново")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return kb


def get_location_keyboard():
    """Кнопки локации (Яндекс.Карты)"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗺️ Южнопортовая ул., 5, стр. 6",
                    url=config.WAREHOUSE_MAP,
                )
            ]
        ]
    )
    return kb


def get_contacts_keyboard():
    """Контакты админа"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать админу",
                    url=f"https://t.me/{config.ADMIN_USERNAME}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📞 Позвонить",
                    url="tel:"
                    + config.ADMIN_PHONE.replace(" ", "")
                    .replace("-", "")
                    .replace("(", "")
                    .replace(")", "")
                    if config.ADMIN_PHONE
                    else "tel:"
                )
            ],
        ]
    )
    return kb


def get_contact_request_keyboard():
    """Кнопка для отправки номера телефона"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return kb


# ===== НОВЫЕ КЛАВИАТУРЫ ДЛЯ ШАГОВ =====


def get_step_nav_keyboard(can_go_back: bool = True):
    """
    Инлайн-кнопки для навигации по шагам анкеты.
    callback_data:
      - 'step_back'  — перейти на предыдущий шаг
      - 'step_next'  — перейти на следующий шаг / к следующему вопросу
    """
    buttons = []
    if can_go_back:
        buttons.append(
            InlineKeyboardButton(text="⬅ Назад", callback_data="step_back")
        )
    buttons.append(InlineKeyboardButton(text="➡ Далее", callback_data="step_next"))

    kb = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return kb


def get_preview_keyboard():
    """
    Кнопки на финальном экране:
      - 'edit_form'   — вернуться к редактированию (сначала к первому шагу)
      - 'submit_form' — отправить админу
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать", callback_data="edit_form"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Отправить админу", callback_data="submit_form"
                )
            ],
        ]
    )
    return kb


def get_folder_keyboard():
    """
    Клавиатура для выбора папки (категории заявки)
    """
    categories = [
        "Одежда и обувь",
        "Электроника и техника",
        "Косметика и бытовая химия",
        "Детские товары",
        "Дом и сад",
        "Книги и канцелярия",
        "Спорт и отдых",
        "Другое",
    ]
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"folder:{cat}")]
        for cat in categories
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


def get_admin_panel_keyboard():
    """Клавиатура для админ-панели"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Новые заявки", callback_data="admin_new_requests"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📜 История заявок", callback_data="admin_history"
                ),
            ],
        ]
    )
    return kb

def get_folder_list_keyboard():
    """Клавиатура для выбора папки"""
    categories = [
        "Одежда и обувь",
        "Электроника и техника",
        "Косметика и бытовая химия",
        "Детские товары",
        "Дом и сад",
        "Книги и канцелярия",
        "Спорт и отдых",
        "Другое",
    ]
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"folder_show:{cat}")]
        for cat in categories
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
