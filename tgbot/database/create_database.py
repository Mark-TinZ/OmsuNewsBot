import logging

from tgbot.database.postgresql import Database


async def create_table_users(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id BIGINT UNIQUE NOT NULL,
        role_id VARCHAR(255) NOT NULL,
        course_number INTEGER DEFAULT NULL,
        group_id VARCHAR(255) DEFAULT NULL,
        settings "char"[] NOT NULL DEFAULT '{}',
        name VARCHAR(255) DEFAULT NULL
    )"""

    await db.pool.execute(sql)


async def create_table_schedules(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS schedules(
        id SERIAL PRIMARY KEY,
        subject_id VARCHAR(255) NOT NULL,
        lesson_number INTEGER NOT NULL,
        teacher_id VARCHAR(255) NOT NULL,
        group_id VARCHAR(255) NOT NULL,
        weekday INTEGER NOT NULL,
        academic_weeks INTEGER[] NOT NULL,
        room INTEGER NOT NULL,
        type_lesson VARCHAR(255) NOT NULL
    )"""

    await db.pool.execute(sql)


async def create_database(db: Database) -> None:
    await create_table_users(db)
    await create_table_schedules(db)

    logging.info("Database has been created!")
