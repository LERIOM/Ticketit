# Florent.md — coordination (agent de Florent, module `executor`)

> Fichier tenu **uniquement** par l'agent de Florent. L'agent d'Antoine le lit, il ne l'écrit pas.
> (Version initiale amorcée par l'agent d'Antoine le 2026-10-19 ; à partir de maintenant, c'est
> l'agent de Florent qui le met à jour.)
> Le protocole de coordination commun est décrit en tête de [`Antoine.md`](Antoine.md) : chacun n'écrit
> que dans son fichier, on lit les deux au début de chaque séance, le contrat v1 est figé.
> À la demande de Florent (2026-10-20), les nouveaux échanges sont centralisés dans
> [communication.md](communication.md), éditable par les deux participants.
> Les fichiers personnels restent propres à leur auteur.

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
| S1 | Contrat v1, squelette FastAPI, `/health` | Contrat validé techniquement ; accord fonctionnel en attente. Squelette non commencé |
| S2 | Labo simulé + `seed_lab.py` | Non commencé |
| S4 | Outils niveau 0 et 1, `/tools`, `/execute` | Non commencé |
| S5 | Autorisation, audit, approbations, annulation | Non commencé |
| S6 | Intégration avec Antoine | Non commencé |

## Réponses à Antoine

Réponses détaillées dans [communication.md](communication.md).

- **A-Q1** — Périmètre des prompts confirmé : executor uniquement côté Florent.
- **A-Q2** — Outil inconnu : niveau 3, refused confirmé. Rejet et audit undo à valider ensemble.
- **A-Q3** — Seul blocked_until est illustré ; autres structures à convenir.
- **A-Q4** — Créneau à fournir par Florent ; aucun engagement de disponibilité pris par son agent.

## Demandes à Antoine

Voir F-Q1 à F-Q8 dans [communication.md](communication.md).

## Journal

- **2026-10-19** — Fichier amorcé par l'agent d'Antoine. À reprendre par l'agent de Florent.
- **2026-10-20** — Contrat documenté, validé techniquement et poussé (421323d).
  Création du canal partagé, reprise des demandes et mise à jour du suivi.

## Suivi à chaque modification

À la demande de Florent, mettre à jour ce fichier après chaque ensemble de modifications
terminé : avancement, vérifications, points ouverts et prochaine étape. Puis effectuer
un commit et un push sans redemander confirmation, dans le cadre des permissions disponibles.
Lire également [Antoine.md](Antoine.md) et [communication.md](communication.md) au début du travail.
Ne jamais présenter une proposition de l'agent comme un accord humain des deux participants.

## Bilan du 2026-10-20

- Seul le contrat a été modifié avant cette mise à jour de coordination ; aucun service executor,
  laboratoire ou test ajouté.
- Sources trouvées dans `docs/`, pas `upload/` ; sections du contrat strictement identiques.
- YAML validé avec PyYAML 6.0.3 ; OpenAPI 3.0.3 validé avec openapi-spec-validator 0.9.0
  dans un environnement temporaire, sans ajout de dépendances au dépôt.
- Contrat poussé dans le commit `421323d` ; il reste une proposition à valider fonctionnellement.
  Attention : les listes required et les bornes de confidence de la version initiale ont été
  retirées en attendant clarification. Ces changements de validation doivent être revus avec
  Antoine et ne constituent pas un accord commun ni une version d'intégration approuvée.
- Prochaine étape : réponses dans le canal commun ; le squelette health/auth peut ensuite
  être développé sur les éléments déjà définis, sans trancher les points ouverts.
- Coordination : création du canal commun et reprise des demandes A-Q1 à A-Q4 et F-Q1 à F-Q8.
