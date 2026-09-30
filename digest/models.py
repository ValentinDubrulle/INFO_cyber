from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    id: str
    title: str
    url: str
    source: str
    published: datetime  # toujours en UTC, timezone-aware
    text: str = ""
    kind: str = "article"  # "article" ou "kev"
    extra: dict = field(default_factory=dict)
