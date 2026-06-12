"""calculate_private_duration — calcul de durée hors heures de bureau.
Implémentation autonome, sans dépendance externe.
"""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Brussels")


def is_week_end(at: datetime) -> bool:
    return at.isoweekday() in [6, 7]


def calculate_private_duration(
    start: datetime, end: datetime, start_pro_time: time, end_pro_time: time
) -> int:
    """Calculate private duration in minutes, taking office hours (PRO hours) and week-ends into account."""

    if end_pro_time < start_pro_time:
        raise ValueError(f"{start_pro_time} must be before {end_pro_time}")

    current = start
    duration = 0.0
    while current < end:
        start_of_private_hours = datetime(
            current.year,
            current.month,
            current.day,
            end_pro_time.hour,
            end_pro_time.minute,
            0,
            0,
            tzinfo=TZ,
        )
        end_of_private_hours = datetime(
            current.year,
            current.month,
            current.day,
            start_pro_time.hour,
            start_pro_time.minute,
            0,
            0,
            tzinfo=TZ,
        )

        if current < end_of_private_hours and current < start_of_private_hours:
            next_tick = min(end, end_of_private_hours)
            increase_private = True
        elif end_of_private_hours <= current < start_of_private_hours:
            next_tick = min(end, start_of_private_hours)
            increase_private = is_week_end(current)
        elif start_of_private_hours <= current and end_of_private_hours < current:
            next_tick = min(end, end_of_private_hours + timedelta(days=1))
            increase_private = True
        else:
            raise AssertionError("unreachable")

        if increase_private:
            duration += (next_tick - current).total_seconds() / 60

        current = next_tick

    return round(duration)
