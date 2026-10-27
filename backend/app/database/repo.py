import json

from sqlalchemy import select

from app.database.models import AlertRecord, ChatMessage, SavedAnalysis, SavedLocation
from app.database.session import session_scope


def list_locations(cid):
    with session_scope() as s:
        return list(s.scalars(select(SavedLocation).where(SavedLocation.client_id == cid).order_by(SavedLocation.id.desc())))


def add_location(cid, data: dict):
    with session_scope() as s:
        existing = s.scalar(select(SavedLocation).where(
            SavedLocation.client_id == cid, SavedLocation.name == data["name"],
            SavedLocation.admin1 == data.get("admin1")))
        if existing:
            return existing
        row = SavedLocation(client_id=cid, **data)
        s.add(row)
        s.flush()
        return row


def delete_location(cid, lid) -> bool:
    with session_scope() as s:
        row = s.get(SavedLocation, lid)
        if not row or row.client_id != cid:
            return False
        s.delete(row)
        return True


def list_analyses(cid):
    with session_scope() as s:
        return list(s.scalars(select(SavedAnalysis).where(SavedAnalysis.client_id == cid).order_by(SavedAnalysis.id.desc())))


def add_analysis(cid, data: dict):
    with session_scope() as s:
        row = SavedAnalysis(client_id=cid, title=data["title"], location=data["location"], parameter=data["parameter"],
                            years=data["years"], summary_json=json.dumps(data["summary"], ensure_ascii=False))
        s.add(row)
        s.flush()
        return row


def delete_analysis(cid, aid) -> bool:
    with session_scope() as s:
        row = s.get(SavedAnalysis, aid)
        if not row or row.client_id != cid:
            return False
        s.delete(row)
        return True


def save_messages(cid, session_id, msgs: list[tuple[str, str, str | None]]):
    with session_scope() as s:
        for role, content, intent in msgs:
            s.add(ChatMessage(client_id=cid, session_id=session_id, role=role, content=content[:4000], intent=intent))


def list_messages(cid, limit=100):
    with session_scope() as s:
        rows = list(s.scalars(select(ChatMessage).where(ChatMessage.client_id == cid).order_by(ChatMessage.id.desc()).limit(limit)))
        return list(reversed(rows))


def record_alerts(cid, alerts) -> None:
    with session_scope() as s:
        for a in alerts:
            exists = s.scalar(select(AlertRecord.id).where(
                AlertRecord.client_id == cid, AlertRecord.location == a.location_name,
                AlertRecord.alert_type == a.type, AlertRecord.date == a.date, AlertRecord.level == a.level))
            if not exists:
                s.add(AlertRecord(client_id=cid, location=a.location_name, alert_type=a.type, level=a.level,
                                  title=a.title, date=a.date))


def list_alert_history(cid, limit=100):
    with session_scope() as s:
        return list(s.scalars(select(AlertRecord).where(AlertRecord.client_id == cid).order_by(AlertRecord.id.desc()).limit(limit)))
