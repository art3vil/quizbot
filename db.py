import aiosqlite


DB_NAME = "quiz_bot.db"


async def create_table() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER,
                correct_answers INTEGER DEFAULT 0
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_results (
                user_id INTEGER PRIMARY KEY,
                correct_answers INTEGER NOT NULL,
                total_questions INTEGER NOT NULL
            )
            """
        )
        # Мягкая миграция: добавляем колонку correct_answers, если таблица уже существовала без неё
        try:
            await db.execute(
                "ALTER TABLE quiz_state ADD COLUMN correct_answers INTEGER DEFAULT 0"
            )
        except Exception:
            pass
        await db.commit()


async def get_quiz_index(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT question_index FROM quiz_state WHERE user_id = (?)",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row is not None else 0


async def update_quiz_index(user_id: int, index: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            UPDATE quiz_state
            SET question_index = ?
            WHERE user_id = ?
            """,
            (index, user_id),
        )
        if cursor.rowcount == 0:
            await db.execute(
                """
                INSERT INTO quiz_state (user_id, question_index, correct_answers)
                VALUES (?, ?, 0)
                """,
                (user_id, index),
            )
        await db.commit()


async def reset_quiz_state(user_id: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers)
            VALUES (?, 0, 0)
            """,
            (user_id,),
        )
        await db.commit()


async def increment_correct_answers(user_id: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE quiz_state
            SET correct_answers = COALESCE(correct_answers, 0) + 1
            WHERE user_id = ?
            """,
            (user_id,),
        )
        await db.commit()


async def get_correct_answers(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT correct_answers FROM quiz_state WHERE user_id = (?)",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row is not None else 0


async def save_result(user_id: int, correct_answers: int, total_questions: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO quiz_results (user_id, correct_answers, total_questions)
            VALUES (?, ?, ?)
            """,
            (user_id, correct_answers, total_questions),
        )
        await db.commit()


async def get_last_result(user_id: int) -> tuple[int, int] | None:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT correct_answers, total_questions
            FROM quiz_results
            WHERE user_id = (?)
            """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return int(row[0]), int(row[1])