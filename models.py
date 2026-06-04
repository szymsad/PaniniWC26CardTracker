from dataclasses import dataclass


@dataclass
class Card:
    number: int
    name: str
    category: str
    country: str | None = None
    position: str | None = None