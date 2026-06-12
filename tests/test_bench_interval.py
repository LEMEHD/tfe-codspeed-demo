"""Benchmarks Interval — réplique le dispositif PoC du TFE (cas d'étude 4.2).

test_bench_interval_subtract instrumente la fonction « sur un jeu d'entrées
représentatif » (TFE 4.2.1) : 2 500 paires couvrant les cinq branches de
subtract (égalité, inclusion, chevauchement gauche/droite, disjonction).
CPU pur, déterministe → mode Instruction Counting en CI.
"""

from datetime import datetime, timedelta

from tfe_bench.interval import Interval

BASE = datetime(2026, 6, 1, 0, 0)


def _build_subtract_pairs() -> list[tuple[Interval, Interval]]:
    """500 × 5 paires déterministes, une par branche de subtract."""
    pairs: list[tuple[Interval, Interval]] = []
    for i in range(500):
        t = BASE + timedelta(hours=3 * i)
        seg = Interval(t, t + timedelta(hours=3))
        pairs.append((seg, Interval(t, t + timedelta(hours=3))))  # égalité → None
        pairs.append((seg, Interval(t - timedelta(hours=1), t + timedelta(hours=4))))  # seg inclus → None
        pairs.append((seg, Interval(t + timedelta(hours=2), t + timedelta(hours=5))))  # chevauchement droite
        pairs.append((seg, Interval(t - timedelta(hours=2), t + timedelta(hours=1))))  # chevauchement gauche
        pairs.append((seg, Interval(t + timedelta(hours=10), t + timedelta(hours=12))))  # disjoint
    return pairs


def test_bench_interval_subtract(benchmark):
    """Réplique de test_bench_interval_subtract du PoC (TFE 4.2)."""
    pairs = _build_subtract_pairs()

    result = benchmark(lambda: [seg.subtract(other) for seg, other in pairs])

    assert len(result) == 2500
    assert sum(1 for r in result if r is None) == 1000  # égalité + inclusion
    assert all(r.start < r.end for r in result if r is not None)


def test_bench_interval_overlaps(benchmark):
    """interval_overlaps — hot path isolé (TFE annexe A)."""
    window = Interval(BASE, BASE + timedelta(days=30))
    bookings = [Interval(BASE + timedelta(hours=3 * i), BASE + timedelta(hours=3 * i + 2)) for i in range(2000)]

    result = benchmark(lambda: sum(1 for b in bookings if window.overlaps(b)))

    assert result == 240  # seules les réservations dans la fenêtre de 720 h


def test_bench_interval_contains(benchmark):
    """interval_contains — appartenance d'un point (TFE annexe A)."""
    bookings = [Interval(BASE + timedelta(hours=3 * i), BASE + timedelta(hours=3 * i + 2)) for i in range(240)]
    probes = [BASE + timedelta(minutes=30 * i) for i in range(1000)]

    result = benchmark(lambda: sum(1 for b in bookings for p in probes if b.contains(p)))

    assert result > 0
