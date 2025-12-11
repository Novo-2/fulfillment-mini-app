from aiogram.fsm.state import State, StatesGroup

class ClientForm(StatesGroup):
    waiting_for_category = State()
    waiting_for_quantity = State()
    waiting_for_task = State()
    waiting_for_marketplace = State()
    full_name = State()
    waiting_for_phone = State()
    preview = State()

# Добавь состояние для отклонения заявки
class AdminStates(StatesGroup):
    waiting_reject_reason = State()
