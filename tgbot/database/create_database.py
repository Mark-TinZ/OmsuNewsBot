import logging

from tgbot.database.postgresql import Database


async def create_table_users(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id BIGINT UNIQUE,
        role character varying(255) NOT NULL,
        course INTEGER DEFAULT NULL,
        "group" VARCHAR(255) DEFAULT NULL,
        settings "char"[] NOT NULL DEFAULT '{}',
        name character varying(255)
    )"""

    await db.pool.execute(sql)

    # TODO: сделать новую таблицу для пар (уроки)
    #    Schedules:
    # • id (идентификатор)
    # • subject (название предмета)
    # • lesson_number (номер пары)
    # • teacher (имя преподавателя)
    # • group (название группы)
    # • day_of_week (день недели)
    # • academic_weeks (учебные недели, когда проходит предмет)
    # • room (аудитория)


async def create_database(db: Database) -> None:
    await create_table_users(db)

    logging.info("Database has been created!")
