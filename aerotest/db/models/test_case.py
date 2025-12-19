"""æµè¯ç¨ä¾æ¨¡å"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from aerotest.db.base import Base


class TestCase(Base):
    """æµè¯ç¨ä¾æ¨¡å"""

    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    steps: Mapped[List] = mapped_column(JSON, nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    timeout: Mapped[int] = mapped_column(Integer, default=300000)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"<TestCase id={self.id} name={self.name}>"

