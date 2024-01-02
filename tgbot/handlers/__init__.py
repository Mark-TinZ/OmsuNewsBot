from tgbot.handlers.admin import admin_router
from tgbot.handlers.registration import registration_router

routers_list = [
    admin_router,
    registration_router
]

__all__ = [
    "routers_list",
]
