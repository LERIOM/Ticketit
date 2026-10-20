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
| S1 | Contrat v1, squelette FastAPI, `/health` | Socle health/auth réalisé, 8 tests réussis ; précisions du contrat encore ouvertes |
| S2 | Labo simulé + `seed_lab.py` | Stockage SQLite et seed du labo réalisés ; reset global audit/idempotence reste ouvert |
| S4 | Outils niveau 0 et 1, `/tools`, `/execute` | Non commencé |
| S5 | Autorisation, audit, approbations, annulation | Non commencé |
| S6 | Intégration avec Antoine | Non commencé |

## Réponses à Antoine

Réponses détaillées dans [communication.md](communication.md).

- **A-Q1** — Périmètre des prompts confirmé : executor uniquement côté Florent.
- **A-Q2** — Propositions d'Antoine acceptées par l'accord de principe de Florent ;
  détails restant à préciser dans F-Q9 à F-Q14.
- **A-Q3** — Structures proposées par Antoine reçues et consignées dans le canal commun ;
  acceptées côté Florent ; schémas incomplets suivis dans le canal commun.
- **A-Q4** — Créneau à fournir par Florent ; aucun engagement de disponibilité pris par son agent.

## Demandes à Antoine

Voir F-Q1 à F-Q8 dans [communication.md](communication.md).
Réponses proposées reçues le 2026-10-20 ; questions complémentaires F-Q9 à F-Q14.
F-Q15 est clôturée : accord de principe de Florent reçu.

## Journal

- **2026-10-19** — Fichier amorcé par l'agent d'Antoine. À reprendre par l'agent de Florent.
- **2026-10-20** — Contrat documenté, validé techniquement et poussé (421323d).
  Création du canal partagé, reprise des demandes et mise à jour du suivi.
- **2026-10-20 — Complément :** synthèse des réponses d'Antoine transmise par Florent
  enregistrée dans le canal commun, sans adoption ni modification du contrat.
  Questions restantes et demande d'accord ajoutées ; vérification documentaire
  avec `git diff --check`, puis commit et push selon la consigne de Florent.

## Suivi à chaque modification

**Consigne actuelle (2026-10-20) :** Florent donne systématiquement son accord
par principe. Les propositions reçues d'Antoine sont acceptées côté Florent ;
ne plus solliciter sa confirmation à chaque étape dans le périmètre demandé.
Cette consigne remplace les mentions historiques « accord de Florent en attente ».
Elle ne fournit pas les détails absents et ne remplace pas l'accord d'Antoine
sur une divergence ou le versionnement. Voir F-Q15 dans le canal commun.
Florent demande également d'avancer dès qu'un travail suffisamment défini est
possible, sans attendre les réponses qui concernent d'autres parties du service.

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
- Réponses d'Antoine reçues : champs, résultats, réversibilité, autorisation,
  approbations, undo et idempotence documentés comme propositions.
  Restent notamment UUID/approver et versionnement, liste IP absente, contraintes
  de paramètres, audit inconnu, annulation après changement d'état, audit sans filtre
  et exception du seed. Prochaine étape : compléments d'Antoine et accord de Florent.
- **Actualisation :** accord de principe de Florent reçu et F-Q15 clôturée.
  Prochaine étape : obtenir les précisions F-Q9 à F-Q14 auprès d'Antoine,
  puis appliquer les règles suffisamment définies dans le périmètre autorisé.
  Cette mise à jour concerne uniquement la coordination ; contrôle
  `git diff --check`, commit et push.

## Socle S1 réalisé — 2026-10-20

- [executor/app/main.py](executor/app/main.py) : application FastAPI, route unique
  GET /v1/health, réponse status ok/version 1.0, authentification X-API-Key.
- Clé lue dans EXECUTOR_API_KEY lors de la création de l'application.
  Clé serveur absente/vide ou clé cliente absente/vide/invalide : refus 401.
  Comparaison constante avec secrets.compare_digest ; aucune clé de secours.
- Documentation HTTP automatique désactivée pour ne pas ajouter de routes.
- [Tests](executor/tests/test_health.py) : 8 réussis sous Python 3.14,
  FastAPI 0.151.0, Pydantic 2.14.1. Un avertissement de dépréciation du
  TestClient Starlette/httpx, sans échec. Python 3.11 non testé dans cet environnement.
- [README executor](executor/README.md) : installation, lancement local sur 8100,
  tests et limites du socle. Dépendances et exclusions locales ajoutées dans executor.
- Contrat, modules d'Antoine et configuration Compose inchangés.
  Le mock reste nécessaire à l'intégration des routes métier.
- Prochaine étape : poursuivre les éléments définis du labo et du service ;
  garder F-Q9 à F-Q14 visibles avant d'implémenter les comportements concernés.

## Laboratoire S2 — 2026-10-20

- Ajout du [stockage](executor/app/lab/storage.py), des
  [fixtures déterministes](executor/app/lab/seed.py) et du
  [script seed](executor/scripts/seed_lab.py).
- Comptes et postes des scénarios communs, pare-feu initialement vide, 14 événements
  exportables en JSONL. Dates fixes et états initiaux documentés comme choix
  internes de démonstration, pas comme nouvelles règles de l'API.
- Seed transactionnel limité aux tables lab_* ; aucune suppression d'audit ou
  d'idempotence avant résolution de F-Q14. Pas encore de reset global du service.
- 15 tests réussis (8 health + 7 labo) sous Python 3.14 : persistance,
  reproductibilité, rollback, préservation des autres tables, export et CLI.
  Avertissement TestClient/httpx déjà connu, sans échec.
- [Dockerfile](executor/Dockerfile) ajouté, utilisateur non privilégié, port 8100.
  Construction non testée : Docker indisponible. Aucun changement Compose.
- Documentation et exclusions des fichiers locaux mises à jour ; contrôle
  git diff --check avant commit/push.
- Prochaine étape : relire les compléments d'Antoine et implémenter les outils
  internes sur ce stockage, sans anticiper les règles non résolues.
