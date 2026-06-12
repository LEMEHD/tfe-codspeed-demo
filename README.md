# tfe-bench — Support de démonstration (défense TFE)

[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://app.codspeed.io/LEMEHD/tfe-codspeed-demo?utm_source=badge)

Dépôt de démonstration accompagnant le TFE *« Intégration du Continuous Benchmarking
par Instruction Counting dans le pipeline CI/CD d'une plateforme SaaS de mobilité
partagée »* (Mehdi Laghmich, ISFCE, 2025-2026).

Le dépôt d'entreprise (Monolit, MyMove) n'étant plus accessible après la fin du stage,
ce dépôt extrait les deux fonctions CPU-bound étudiées dans le TFE — `Interval`
(cas d'étude 4.2) et `calculate_private_duration` (benchmarks S1) — afin de rejouer
en conditions réelles le pipeline décrit au chapitre 3.4 : benchmarks pytest-codspeed,
workflow GitHub Actions, détection automatique de régression sur PR, dashboard et
flame graphs CodSpeed.

## Mise en place (une fois, ~15 min)

1. Sortir ce dossier du dépôt Monolit, puis `git init`, premier commit, pousser sur
   un dépôt GitHub **public** (ex. `tfe-codspeed-demo`).
2. Sur [codspeed.io](https://codspeed.io), installer l'app GitHub sur ce dépôt.
3. Copier le token CodSpeed dans les secrets du dépôt : `Settings → Secrets →
   Actions → CODSPEED_TOKEN`.
4. Pousser sur `main` (ou `workflow_dispatch`) → premier run = baseline sur le dashboard.

## Démo 1 — Déterminisme IC vs bruit Walltime (local)

```bash
# Deux runs walltime : les temps divergent (bruit environnemental)
pytest tests/ --codspeed
pytest tests/ --codspeed

# Deux runs Instruction Counting sous Valgrind : comptes identiques
docker build -f Dockerfile.bench -t tfe-bench .
docker run --rm tfe-bench pytest tests/ --codspeed --codspeed-mode instrumentation
docker run --rm tfe-bench pytest tests/ --codspeed --codspeed-mode instrumentation
```

## Démo 2 — Régression détectée sur PR (rejoue le cas d'étude 4.2)

```bash
git checkout -b demo/perf-regression
python demo/apply_regression.py
git commit -am "Add debug logging to Interval.subtract"
git push -u origin demo/perf-regression
```

Ouvrir la PR : le workflow tourne, CodSpeed poste un commentaire automatique avec
la variation relative par benchmark, et le flame graph montre `Interval.__str__`
apparu dans le profil de `subtract` — confirmation indépendante que la dégradation
porte sur la fonction elle-même (cf. TFE 4.2.4).

La régression est volontairement réaliste : un `logger.debug(f"...")` en hot path,
dont la f-string est évaluée à chaque appel même si le niveau debug est inactif.

Annulation : `python demo/apply_regression.py --revert`.

## Conseil avant la défense

Lancer la PR de régression la veille (le run CI prend quelques minutes) et garder
l'onglet du dashboard + le commentaire de PR ouverts. Préparer des captures d'écran
de secours de chaque étape.
