import logging

from tgbot.database.postgresql import Database


async def create_table_users(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id BIGINT UNIQUE,
        role VARCHAR(255),
        course INTEGER DEFAULT NULL,
        "group" VARCHAR(255) DEFAULT NULL,
        settings "char"[] NOT NULL DEFAULT '{}'
    )"""
    await db.pool.execute(sql)


async def create_database(db: Database) -> None:
    await create_table_users(db)

    logging.info("Database has been created!")
