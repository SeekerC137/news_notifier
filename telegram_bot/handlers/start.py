from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from db import get_user
from db import create_new_user
from db import update_user_data
from db import UserData

from telegram_bot.handlers.commons.commons import return_inline_answer_to_user
from telegram_bot.handlers.commons.commons import return_cmd_answer_to_user
from telegram_bot.handlers.commons.commons import get_user_data_from_state_storage
from telegram_bot.handlers.commons.commons import update_user_data_in_state_storage
from telegram_bot.handlers.commons.commons import numerate_keywords_list

from telegram_bot.handlers.commons.keyboards import get_last_menu_keyboard
from telegram_bot.handlers.commons.keyboards import get_start_menu_keyboard
from telegram_bot.handlers.commons.keyboards import get_start_keywords_editing_menu_keyboard


START_MESSAGE = (
    "Этот бот будет оповещать Вас о выходе новостей по интересующим Вас темам.\n\n"
    "Для этого Вам нужно создать список ключевых слов которые он будет искать в заголовках и текстах новостей. "
    "Если ключевое слово будет найдено, то бот пришлет оповещение.\n\n"
    "В качестве источников новостей используются RSS ленты Google News (на русском и английском языках) и "
    "Интерфакс."
)


class KeywordsEditingStates(StatesGroup):
    start_keywords_editing = State()
    adding_keywords = State()
    deleting_keywords = State()


async def start_message(message: types.Message, state: FSMContext) -> None:

    await state.finish()

    message_str = START_MESSAGE

    keyboard = get_start_menu_keyboard()
    await return_cmd_answer_to_user(message_str, keyboard, message)

    await check_user_registration(message)


async def inline_start_message(call: types.CallbackQuery, state: FSMContext) -> None:

    await state.finish()

    message_str = START_MESSAGE

    keyboard = get_start_menu_keyboard()
    await return_inline_answer_to_user(message_str, keyboard, call)


async def check_user_registration(message: types.Message) -> None:

    try:
        user = await get_user(message.from_user['id'])
        _ = user.user_data
    except Exception:
        user_data = UserData(
            keywords=[],
        )
        await create_new_user(message.from_user['id'], user_data)


async def start_keywords_editing(call: types.CallbackQuery, state: FSMContext) -> None:

    await KeywordsEditingStates.start_keywords_editing.set()

    await update_user_data_in_state_storage(call, state)

    user_data = await get_user_data_from_state_storage(state)
    keywords = user_data["keywords"]

    if len(keywords) > 0:
        message_str_1 = (
            "Ваш текущий список ключевых слов:\n\n"
            f"{keywords}\n\n"
        )
    else:
        message_str_1 = (
            "Ваш текущий список ключевых слов пуст.\n\n"
        )
    message_str_2 = (
        "Чтобы добавить или удалить ключевые слова из списка нажмите соответствующую кнопку ниже."
    )
    message_str = message_str_1 + message_str_2

    keyboard = get_start_keywords_editing_menu_keyboard()
    await return_inline_answer_to_user(message_str, keyboard, call)


async def add_keywords(call: types.CallbackQuery) -> None:

    await KeywordsEditingStates.adding_keywords.set()

    message_str = (
        "Чтобы добавить ключевые слова в Ваш список просто отправьте их в чат отдельными сообщениями.\n\n"
        "⚠️Бот ищет точное соответствие слов в тексте и заголовках новостей, поэтому чтобы ничего не пропустить "
        "рекомендуется добавлять ключевые слова без окончаний (например 'Москв' вместо 'Москва' или 'Москве')."
    )

    keyboard = get_last_menu_keyboard("keywords")
    await return_inline_answer_to_user(message_str, keyboard, call)


async def delete_keywords(call: types.CallbackQuery, state: FSMContext) -> None:

    user_data = await get_user_data_from_state_storage(state)
    keywords = user_data["keywords"]

    if len(keywords) > 0:
        await KeywordsEditingStates.deleting_keywords.set()
        message_str = (
            "Ваш текущий список ключевых слов:\n\n"
            f"{numerate_keywords_list(keywords)}\n\n"
            "Чтобы удалить ключевые слова отправьте в чат отдельными сообщениями их номера из списка выше."
        )
    else:
        message_str = (
            "Ваш текущий список ключевых слов пуст!"
        )

    keyboard = get_last_menu_keyboard("keywords")
    await return_inline_answer_to_user(message_str, keyboard, call)


async def get_keyword_from_user(message: types.Message, state: FSMContext) -> None:

    keyword = message.text
    user_data = await get_user_data_from_state_storage(state)
    user_data["keywords"].append(keyword)
    await update_user_data(message.from_user['id'], user_data)
    await state.update_data(user_data=user_data)

    message_str = (
        f"Ключевое слово '{keyword}' было добавлено.\n\n"
        "Ваш текущий список ключевых слов:\n\n"
        f"{user_data['keywords']}\n\n"
        "Чтобы добавить еще ключевые слова просто отправьте их в чат отдельными сообщениями."
    )

    keyboard = get_last_menu_keyboard("keywords")
    await return_cmd_answer_to_user(message_str, keyboard, message)


async def get_keyword_number_from_user(message: types.Message, state: FSMContext) -> None:

    user_data = await get_user_data_from_state_storage(state)

    try:
        keyword_number = int(message.text)
        deleted_keyword = user_data["keywords"].pop(keyword_number - 1)
    except Exception:
        message_str = (
            f"Вы отправили неверный номер из списка либо вообще не число.\n\n"
            "Ваш текущий список ключевых слов:\n\n"
            f"{numerate_keywords_list(user_data['keywords'])}\n\n"
            "Чтобы удалить ключевые слова отправьте в чат отдельными сообщениями их номера из списка выше."
        )
    else:
        await update_user_data(message.from_user['id'], user_data)
        await state.update_data(user_data=user_data)
        message_str = (
            f"Ключевое слово '{deleted_keyword}' было удалено.\n\n"
            "Ваш текущий список ключевых слов:\n\n"
            f"{numerate_keywords_list(user_data['keywords'])}\n\n"
            "Чтобы удалить еще ключевые слова отправьте в чат отдельными сообщениями их номера из списка выше."
        )

    keyboard = get_last_menu_keyboard("keywords")
    await return_cmd_answer_to_user(message_str, keyboard, message)


def register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_message,
                                commands="start",
                                state="*")
    dp.register_callback_query_handler(inline_start_message,
                                       text="cancel",
                                       state="*")
    dp.register_callback_query_handler(start_keywords_editing,
                                       text="keywords",
                                       state="*")
    dp.register_callback_query_handler(add_keywords,
                                       text="add_keywords",
                                       state=KeywordsEditingStates.start_keywords_editing)
    dp.register_callback_query_handler(delete_keywords,
                                       text="delete_keywords",
                                       state=KeywordsEditingStates.start_keywords_editing)
    dp.register_message_handler(get_keyword_from_user,
                                state=KeywordsEditingStates.adding_keywords)
    dp.register_message_handler(get_keyword_number_from_user,
                                state=KeywordsEditingStates.deleting_keywords)
