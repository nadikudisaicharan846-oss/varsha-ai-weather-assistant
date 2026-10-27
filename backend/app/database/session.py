"""Optional persistence. Weather features never depend on this module working."""
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database.models import Base
from app.exceptions import StorageUnavailable

log = logging.getLogger("varsha.db")
_engine = None
_Session = None
available = False


def init_db() -> bool:
    global _engine, _Session, available
    try:
        url = get_settings().db_url
        args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, connect_args=args, pool_pre_ping=True)
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(_engine, expire_on_commit=False)
        available = True
    except Exception:  # noqa: BLE001 - DB is optional
        log.warning("Database unavailable; saving features are disabled")
        available = False
    return available


@contextmanager
def session_scope():
    if not available or _Session is None:
        raise StorageUnavailable()
    s: Session = _Session()
    try:
        yield s
        s.commit()
    except StorageUnavailable:
        raise
    except Exception:
        s.rollback()
        raise StorageUnavailable() from None
    finally:
        s.close()
