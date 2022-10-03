from aiogram import types
from aiogram.dispatcher import FSMContext

from db import get_user


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
