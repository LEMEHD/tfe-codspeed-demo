"""Introduit la régression de démonstration sur Interval.subtract.

Régression plausible et déterministe : un logging de debug en f-string dans le
hot path. La f-string est évaluée à CHAQUE appel (2× Interval.__str__, soit du
formatage datetime), que le niveau debug soit actif ou non — erreur classique,
détectable par Instruction Counting (saut de palier net, cf. TFE 4.2.2).

Usage :
    git checkout -b demo/perf-regression
    python demo/apply_regression.py
    git commit -am "Add debug logging to Interval.subtract"
    git push -u origin demo/perf-regression
    # → ouvrir la PR : CodSpeed commente avec la régression + flame graph

Annulation : python demo/apply_regression.py --revert
"""

import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "src" / "tfe_bench" / "interval.py"

CLEAN_IMPORTS = "import datetime\nfrom dataclasses import dataclass\n"
REGRESSED_IMPORTS = (
    "import datetime\nimport logging\nfrom dataclasses import dataclass\n\nlogger = logging.getLogger(__name__)\n"
)

CLEAN_SUBTRACT = '    def subtract(self, other: "Interval") -> "Interval | None":\n        if self == other:'
REGRESSED_SUBTRACT = (
    '    def subtract(self, other: "Interval") -> "Interval | None":\n'
    '        logger.debug(f"subtracting {other} from {self}")\n'
    "        if self == other:"
)


def main() -> None:
    src = TARGET.read_text(encoding="utf-8")
    revert = "--revert" in sys.argv

    if revert:
        if REGRESSED_SUBTRACT not in src:
            sys.exit("Régression non présente, rien à annuler.")
        src = src.replace(REGRESSED_IMPORTS, CLEAN_IMPORTS).replace(REGRESSED_SUBTRACT, CLEAN_SUBTRACT)
        print("Régression annulée.")
    else:
        if REGRESSED_SUBTRACT in src:
            sys.exit("Régression déjà appliquée.")
        if CLEAN_IMPORTS not in src or CLEAN_SUBTRACT not in src:
            sys.exit("Motif introuvable — interval.py a divergé.")
        src = src.replace(CLEAN_IMPORTS, REGRESSED_IMPORTS).replace(CLEAN_SUBTRACT, REGRESSED_SUBTRACT)
        print("Régression appliquée : logging f-string dans Interval.subtract.")

    TARGET.write_text(src, encoding="utf-8")


if __name__ == "__main__":
    main()
