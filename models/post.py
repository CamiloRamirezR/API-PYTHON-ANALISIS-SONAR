from db import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column


class Post(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    routeId: Mapped[str]
    userId: Mapped[str]
    expireAt: Mapped[datetime]
    createdAt: Mapped[datetime]

