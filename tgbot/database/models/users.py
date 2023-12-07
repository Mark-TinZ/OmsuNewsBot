from sqlalchemy import BIGINT, String, INT
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BIGINT)
    group: Mapped[str] = mapped_column(String(255))
    course: Mapped[int] = mapped_column(INT)
    role: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<User {self.id} {self.tg_id} {self.group} {self.course}>"
