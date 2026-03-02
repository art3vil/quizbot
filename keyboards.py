from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, Router, F

from db import (
    get_quiz_index,
    update_quiz_index,
    increment_correct_answers,
    get_correct_answers,
    save_result,
)
from quiz_logic import quiz_data


router = Router()


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=f"answer:{option}",
            )
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message: types.Message, user_id: int):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]["correct_option"]
    opts = quiz_data[current_question_index]["options"]
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(
        quiz_data[current_question_index]["question"],
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("answer:"))
async def process_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    chosen_option = callback.data.removeprefix("answer:")
    user_id = callback.from_user.id

    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]["correct_option"]
    correct_text = quiz_data[current_question_index]["options"][correct_index]

    await callback.message.answer(f"Ваш ответ: {chosen_option}")

    is_correct = chosen_option == correct_text

    if is_correct:
        await callback.message.answer("Верно!")
        await increment_correct_answers(user_id)
    else:
        await callback.message.answer(
            f"Неправильно. Правильный ответ: {correct_text}"
        )

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        total_questions = len(quiz_data)
        correct_answers = await get_correct_answers(user_id)
        await save_result(user_id, correct_answers, total_questions)
        await callback.message.answer(
            f"Это был последний вопрос. Квиз завершен!\n"
            f"Ваш результат: {correct_answers} из {total_questions}."
        )
