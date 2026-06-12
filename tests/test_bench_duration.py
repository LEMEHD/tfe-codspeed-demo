"""Benchmarks calculate_private_duration — réplique S1 du TFE (scaling O(intervals)).

Paliers identiques au tableau 5.1 : 1, 7, 30, 90 jours.
Valeurs IC de référence du PoC : short ≈ 0,97 ms, multiday ≈ 2,0 ms (CV 0,1 %).
"""

from datetime import datetime, time, timedelta

import pytest

from tfe_bench.duration import TZ, calculate_private_duration

PRO_START = time(9, 0)
PRO_END = time(17, 0)


def test_bench_calculate_private_duration_short(benchmark):
    """Réplique de calculate_private_duration_short du PoC."""
    start = datetime(2026, 2, 1, 8, 0, tzinfo=TZ)
    end = start + timedelta(days=1)

    result = benchmark(calculate_private_duration, start, end, PRO_START, PRO_END)

    assert result > 0


@pytest.mark.parametrize("duration_days", [1, 7, 30, 90])
def test_bench_calculate_private_duration_scaling(benchmark, duration_days):
    """Réplique de S1 — scaling avec la durée (tableau 5.1 du TFE)."""
    start = datetime(2026, 2, 1, 8, 0, tzinfo=TZ)
    end = start + timedelta(days=duration_days)

    result = benchmark(calculate_private_duration, start, end, PRO_START, PRO_END)

    assert isinstance(result, int)
    assert result > 0
