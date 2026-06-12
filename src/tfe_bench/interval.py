"""Primitive Interval — extraite à l'identique de utils/interval.py du Monolit (MyMove).

Fonction cible du cas d'étude 4.2 du TFE (régression détectée sur Interval.subtract).
"""

import datetime
from dataclasses import dataclass


@dataclass
class Interval:
    start: datetime.datetime
    end: datetime.datetime

    def overlaps(self, other: "Interval") -> bool:
        return self.start < other.end and self.end > other.start

    def is_overlapped_left(self, other: "Interval") -> bool:
        return self.end > other.end > self.start > other.start

    def is_overlapped_right(self, other: "Interval") -> bool:
        return self.start < other.start < self.end < other.end

    def is_inside(self, other: "Interval") -> bool:
        return other.start <= self.start <= self.end <= other.end

    def subtract(self, other: "Interval") -> "Interval | None":
        if self == other:
            return None
        if self.is_inside(other):
            return None
        if other.is_inside(self):
            raise ValueError("other interval is_inside")
        if self.is_overlapped_right(other):
            return Interval(self.start, other.start)
        if self.is_overlapped_left(other):
            return Interval(other.end, self.end)
        return Interval(self.start, self.end)

    def contains(self, dt: datetime.datetime) -> bool:
        return self.start <= dt < self.end

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if not isinstance(other, Interval):
            return False
        return self.start == other.start and self.end == other.end

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"
