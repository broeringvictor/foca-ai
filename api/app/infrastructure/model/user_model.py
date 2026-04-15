from datetime import datetime
from uuid import UUID
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedColumn
from app.infrastructure.model import table_registry



@table_registry.mapped_as_dataclass()
class UserModel:
    """Modelo ORM — mapeamento para a tabela 'users'."""

    __tablename__ = 'users'

    id: Mapped[UUID] = MappedColumn(PG_UUID(as_uuid=True), primary_key=True)
    email: MappedColumn[str] = MappedColumn(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Recoverty_code
    code: MappedColumn[str] = mapped_column(String(45), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)