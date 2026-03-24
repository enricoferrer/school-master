import uuid

from sqlalchemy import UUID, Column, String, ForeignKey, UniqueConstraint, text
from app.core.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("fk_role", "permission", name="uq_role_permission"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fk_role = Column(UUID(as_uuid=True),ForeignKey("roles.id", ondelete="CASCADE"),nullable=False,index=True,
    )
    permission = Column(String(100), nullable=False)