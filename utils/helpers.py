from models import db, AuditLog
from flask_login import current_user
import json

def log_audit(action, table_name, record_id, details=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        table_name=table_name,
        record_id=record_id,
        details=json.dumps(details) if details else None
    )
    db.session.add(log)
    db.session.commit()
