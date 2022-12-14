from aiogram import types
from aiogram.dispatcher import FSMContext

from db import get_user


async def return_inline_answer_to_user(
    message_str: str,
    keyboard: types.InlineKeyboardMarkup,
    call: types.CallbackQuery,
) -> None:

    await call.message.answer(
        message_str,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await call.answer()


async def return_cmd_answer_to_user(
    message_str: str,
    keyboard: types.InlineKeyboardMarkup,
    message: types.Message
) -> None:

    await message.answer(
        message_str,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def get_user_data_from_state_storage(state: FSMContext) -> dict:

    data_storage = await state.get_data()
    return data_storage['user_data']


async def update_user_data_in_state_storage(call: types.CallbackQuery, state: FSMContext) -> None:

    user = await get_user(call.from_user['id'])
    user_data = user.user_data

    await state.update_data(user_data=user_data)


def numerate_keywords_list(keywords_list: list) -> str:
    keywords_str = ""
    for i, keyword in enumerate(keywords_list):
        keywords_str += f"{i + 1}. {keyword}; "
    return keywords_str
