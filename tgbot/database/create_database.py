import logging
from re import S

from tgbot.database.postgresql import Database


async def create_table_users(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id BIGINT UNIQUE NOT NULL,
        role_id VARCHAR(255) NOT NULL,
        settings JSONB NOT NULL DEFAULT '{}'
    )"""

    await db.pool.execute(sql)

async def create_table_teacher(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS teacher(
        id SERIAL PRIMARY KEY,
        name  VARCHAR(255) NOT NULL,
        user_id INTEGER,
        tg_authkey VARCHAR(255) NOT NULL,
        is_sick BOOLEAN DEFAULT false,
        is_fired BOOLEAN DEFAULT false
    )"""
    
    await db.pool.execute(sql)

async def create_table_student(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS student(
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id),
        group_id INTEGER NOT NULL REFERENCES subjects(group_id),
        course_number INTEGER NOT NULL,
        is_moderator BOOLEAN DEFAULT NULL
    )"""
    
    await db.pool.acquire(sql)

async def create_table_lesson(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS lesson(
        id SERIAL PRIMARY KEY,
        subject_id VARCHAR(255) NOT NULL REFERENCES subjects(id),
        lesson_number INTEGER NOT NULL,
        teacher_id VARCHAR(255) NOT NULL REFERENCES teacher(id),
        group_id VARCHAR(255) NOT NULL REFERENCES group(id),
        weekday INTEGER NOT NULL,
        academic_weeks INTEGER[] NOT NULL,
        room INTEGER NOT NULL,
        type_lesson VARCHAR(255) NOT NULL
    )"""

    await db.pool.execute(sql)

async def create_table_subjects(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS subjects(
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        course_number INTEGER[] NOT NULL,
        group_id INTEGER[] NOT NULL REFERENCES group(id),
        teacher_id INTEGER[] NOT NULL REFERENCES teacher(id)
    )"""
    
    await db.pool.execute(sql)

async def create_table_group(db: Database) -> any:
    sql = """
    CREATE TABLE IF NOT EXISTS group(
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        course_count INTEGER[] NOT NULL
    )"""
    
    await db.pool.execute(sql)


async def create_database(db: Database) -> None:
    await create_table_users(db)
    await create_table_student(db)
    await create_table_teacher(db)
    await create_table_lesson(db)
    await create_table_subjects(db)
    await create_table_group(db)

    logging.info("Database has been created!")
