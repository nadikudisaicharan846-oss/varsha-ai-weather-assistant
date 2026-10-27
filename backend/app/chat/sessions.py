import time
import uuid
from dataclasses import dataclass, field

from app.schemas.weather import Location


@dataclass
class Session:
    id: str
    location: Location | None = None
    hint_key: str | None = None
    intent: str | None = None
    date: tuple[int, int] | None = None
    parameter: str | None = None
    turns: list[dict] = field(default_factory=list)  # last few {"role","content"} for LLM context
    touched: float = field(default_factory=time.monotonic)


class SessionStore:
    """Short-term conversation memory (in-process). Swap for Redis to scale horizontally."""

    def __init__(self, ttl=2 * 3600, max_sessions=2000):
        self.ttl, self.max = ttl, max_sessions
        self._s: dict[str, Session] = {}

    def get(self, sid: str | None) -> Session:
        now = time.monotonic()
        if len(self._s) > self.max:
            for k in [k for k, v in self._s.items() if now - v.touched > self.ttl]:
                self._s.pop(k, None)
        if sid and sid in self._s and now - self._s[sid].touched <= self.ttl:
            s = self._s[sid]
        else:
            s = Session(id=sid or uuid.uuid4().hex[:24])
            self._s[s.id] = s
        s.touched = now
        return s

    def remember(self, s: Session, user: str, assistant: str):
        s.turns += [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}]
        s.turns = s.turns[-8:]
