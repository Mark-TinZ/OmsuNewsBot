from tgbot.database.postgresql import db

async def select_schedule(**kwargs):
	sql = "SELECT * FROM schedules WHERE"
	sql, parameters = db.format_args(sql, kwargs)
	
	return await db.pool.fetchrow(sql, *parameters)
