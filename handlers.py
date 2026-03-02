from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards import get_question
from db import reset_quiz_state, get_last_result
from quiz_logic import quiz_data


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


async def new_quiz(message: types.Message) -> None:
    user_id = message.from_user.id
    await reset_quiz_state(user_id)
    await get_question(message, user_id)


@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    result = await get_last_result(user_id)

    if result is None:
        await message.answer("Вы еще не проходили квиз.")
        return

    correct, total = result
    percent = round(correct / total * 100) if total > 0 else 0
    await message.answer(
        f"Ваш последний результат: {correct} из {total} ({percent}%)."
    )