# Florent.md — coordination (agent de Florent, module `executor`)

> Fichier tenu **uniquement** par l'agent de Florent. L'agent d'Antoine le lit, il ne l'écrit pas.
> (Version initiale amorcée par l'agent d'Antoine le 2026-10-19 ; à partir de maintenant, c'est
> l'agent de Florent qui le met à jour.)
> Le protocole de coordination commun est décrit en tête de [`Antoine.md`](Antoine.md) : chacun n'écrit
> que dans son fichier, on lit les deux au début de chaque séance, le contrat v1 est figé.

## Périmètre de Florent (rappel, cf. `docs/prompt_florent_executeur.md`)

Module d'exécution sécurisée `executor/` : labo simulé (pare-feu, annuaire, EDR, logs, SQLite),
outils d'action, moteur d'autorisation par niveaux (`config/policy.yaml`), journal d'audit en ajout
seul, API REST conforme à `contracts/executor_v1.openapi.yaml`, tests (dont sécurité), `Dockerfile`.

Florent ne touche pas à : `engine/`, `ui/`, `mock_executor/`, `eval/`, `data/`. Pour un changement de
`docker-compose.yml` ou `.env.example`, faire une demande ci-dessous.

## Ce que l'engine d'Antoine attend de l'executor (pour l'intégration S6)

- Service `executor`, port `8100`, préfixe `/v1`, clé `X-API-Key` = variable `EXECUTOR_API_KEY`
  (`401` sinon, y compris sur `/v1/health`).
- `POST /v1/execute` répond **toujours 200** (sauf 401/422), idempotent par `request_id`.
- `seed_lab.py` remet le labo dans l'état du jeu d'intégration commun : `203.0.113.5` (ssh_bruteforce),
  `198.51.100.23` (port_scan), `SRV-WEB-01`, `j.martin`, `PC-COMPTA-07`, comptes protégés `admin`,
  `svc-backup`, poste protégé `DC-01`, IP interne `10.0.0.12`.
- Un `executor/Dockerfile` qui démarre uvicorn sur `0.0.0.0:8100`. Branchement côté compose :
  `docker-compose.override.yml` → `services: { executor: { build: ./executor } }`.

## État

| Semaine | Objectif | État |
| --- | --- | --- |
| S1 | Contrat v1, squelette FastAPI, `/health` | _à renseigner par Florent_ |
| S2 | Labo simulé + `seed_lab.py` | _à renseigner_ |
| S4 | Outils niveau 0 et 1, `/tools`, `/execute` | _à renseigner_ |
| S5 | Autorisation, audit, approbations, annulation | _à renseigner_ |
| S6 | Intégration avec Antoine | _à renseigner_ |

## Réponses à Antoine

_(répondre ici aux demandes `A-Qn` de `Antoine.md`)_

- **A-Q1** — _à compléter_
- **A-Q2** — _à compléter_
- **A-Q3** — _à compléter_
- **A-Q4** — _à compléter_

## Demandes à Antoine

_(poser ici les questions `F-Qn`)_

## Journal

- **2026-10-19** — Fichier amorcé par l'agent d'Antoine. À reprendre par l'agent de Florent.
