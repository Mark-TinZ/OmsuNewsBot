import logging

from tgbot.database.postgresql import database


async def create_table_users():
    async with database as db:
        sql = """
        CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id BIGINT UNIQUE,
        role VARCHAR(255),
        course INTEGER DEFAULT NULL,
        "group" VARCHAR(255) DEFAULT NULL
        )"""
        await db.pool.execute(sql)


async def create_database():
    await create_table_users()

    logging.info("Database has been created!")
