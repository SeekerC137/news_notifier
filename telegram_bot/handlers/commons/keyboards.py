from aiogram import types


def get_start_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="📝 Ключевые слова", callback_data="keywords"),
    ]
    keyboard.add(*buttons)
    return keyboard


def get_start_keywords_editing_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="➕ Добавить ключевые слова", callback_data="add_keywords"),
        types.InlineKeyboardButton(text="➖ Удалить ключевые слова", callback_data="delete_keywords"),
        types.InlineKeyboardButton(text="↩️ Вернуться в начало", callback_data="cancel")
    ]
    keyboard.add(*buttons)
    return keyboard


def get_last_menu_keyboard(parent_dialog_key: None | str = None) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if not parent_dialog_key:
        buttons = [
            types.InlineKeyboardButton(text="↩️ Вернуться в начало", callback_data="cancel")
        ]
    else:
        buttons = [
            types.InlineKeyboardButton(text="⬆️ Назад", callback_data=parent_dialog_key),
            types.InlineKeyboardButton(text="↩️ Вернуться в начало", callback_data="cancel")
        ]
    keyboard.add(*buttons)
    return keyboard
