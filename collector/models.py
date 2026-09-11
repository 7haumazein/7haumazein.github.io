"""Small, serialisable data objects shared by providers and statistics."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Quote:
    exchange: str
    code: str
    name: str
    price: Optional[float]
    prev_close: Optional[float]
    amount: Optional[float] = None
    quote_time: Optional[datetime] = None
    industry: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    status: str = "normal"
    st: bool = False
    listed_at: Optional[str] = None

    @property
    def key(self) -> str:
        return f"{self.exchange.upper()}:{self.code.zfill(6)}"

    def as_dict(self):
        value = asdict(self)
        value["quote_time"] = self.quote_time.isoformat() if self.quote_time else None
        value["key"] = self.key
        return value
