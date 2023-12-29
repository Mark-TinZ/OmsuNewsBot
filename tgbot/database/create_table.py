import logging

from tgbot.database.postgresql import db


async def create_table_users():
    sql = """
    CREATE TABLE IF  NOT EXISTS users(
    if SERIAL PRIMARY KEY,
    tg_id INTEGER,
    role VARCHAR(255),
    group VARCHAR(255)
    );
    """
    await db.pool.execute(sql)
    logging.info("Table created successfully")


async def create_table_all():
    await create_table_users()
    print(1+1)
