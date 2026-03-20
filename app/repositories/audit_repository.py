from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def registrar_log(self, log: AuditLog):
        self.db.add(log)
        self.db.commit()