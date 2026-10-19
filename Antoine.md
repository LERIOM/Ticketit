# Antoine.md — coordination (agent d'Antoine, module `engine`)

> Fichier tenu **uniquement** par l'agent d'Antoine. L'agent de Florent le lit, il ne l'écrit pas.
> Son pendant est [`Florent.md`](Florent.md), tenu uniquement par l'agent de Florent.

## Protocole de coordination (valable pour les deux agents)

1. **Au début de chaque séance**, lire `Antoine.md` **et** `Florent.md`.
2. **Chacun n'écrit que dans son fichier.** Pour demander quelque chose à l'autre : section
   « Demandes à … » de son propre fichier. L'autre répond dans la section « Réponses à … » du sien.
   Chaque demande a un identifiant (`A-Q1`, `F-Q1`…) pour pouvoir y répondre sans ambiguïté.
3. **Le contrat `contracts/executor_v1.openapi.yaml` est figé.** Personne ne le modifie seul.
   Un changement = une demande ici, accord écrit des deux côtés, puis passage en v2.
4. **Propriété des dossiers** (on ne touche jamais au dossier de l'autre) :

   | Dossier / fichier | Propriétaire |
   | --- | --- |
   | `engine/`, `ui/`, `mock_executor/`, `eval/`, `data/` | Antoine |
   | `docker-compose.yml`, `.env.example`, `README.md`, `.gitignore` | Antoine (Florent demande ici s'il a besoin d'un changement) |
   | `executor/` | Florent |
   | `contracts/` | commun, lecture seule (v1 figée) |
   | `docs/` | commun (prompts de référence + dossier PDF) |
   | `Antoine.md` / `Florent.md` | chacun le sien |

5. **En fin de séance**, mettre à jour « État » et « Journal » de son fichier (date + ce qui a changé).

## Périmètre d'Antoine (rappel, cf. `docs/prompt_antoine_moteur.md`)

Ingestion tickets + alertes SIEM/IDS, masquage Presidio, détection d'injection, classification,
Graph RAG Neo4j + bge-m3, LLM hybride (Ollama / API), agent LangGraph, client executor,
interface Streamlit, boucle d'auto-amélioration, évaluation, `mock_executor`, docker-compose.

**Règle d'or** : l'agent propose, l'executor de Florent décide. L'engine n'agit **jamais** sur le labo
autrement que par `POST /v1/execute` via `engine/app/executor_client.py`.

## Mode de travail (choix d'Antoine)

- **Une étape à la fois** : l'agent propose l'étape (quoi, fichiers, comment vérifier), Antoine
  valide, l'agent l'implémente et la teste, puis s'arrête et propose la suivante.
- **Qualité avant vitesse, coûts bas** : tout en local par défaut (Ollama, bge-m3, Neo4j) ;
  l'API payante reste optionnelle (`LLM_PROVIDER=api`), réservée aux comparaisons de l'évaluation.

## État (2026-10-19)

| Étape | Contenu | État |
| --- | --- | --- |
| 1 | Socle : structure, compose, modèles `Ticket` / `Decision`, contrat v1 | ✅ fait |
| 2 | `mock_executor` complet + `executor_client` testés | ✅ fait, commité (tests verts) |
| 3a | Ingestion `/tickets` + `/alerts`, masquage, injection, stockage | 🟡 écrit et testé **en local chez Antoine, pas commité** |
| 3b | Base de connaissance (30 fiches) | ✅ rédigée et commitée, **à relire par Antoine** |
| 3c | LLM (Ollama / API), RAG vectoriel, réponse sourcée | ⏸️ ébauche LLM locale non commitée, RAG pas commencé |
| 4 | Classification, Graph RAG, agent LangGraph, Streamlit, apprentissage, évaluation | ⏳ à faire |

Tests : `mock_executor` 40 verts ; `engine` 83 verts en local avec la 3a (28 sans).
Seuls les éléments marqués « commité » sont sur GitHub ; le reste n'existe que dans le dossier d'Antoine.

### Ce qui existe déjà (pour reprendre sans tout relire)

- `mock_executor/app/` : `catalog.py` (6 outils, niveaux, validation des paramètres, IP jamais
  bloquées), `state.py` (labo en mémoire seedé avec le jeu d'intégration, audit en ajout seul,
  idempotence), `main.py` (routes v1). Tests : `mock_executor/tests/` dont
  `test_contract_conformity.py` qui valide chaque réponse contre le schéma JSON du contrat.
  `MOCK_EXECUTE_DELAY_S=6` simule un executor lent (démo de l'escalade sur délai).
- `engine/app/executor_client.py` : délai 5 s, 1 nouvelle tentative même `request_id` sur
  délai/réseau/5xx (execute + lectures seulement), `ExecutorError` → l'appelant escalade.
- _(local, non commité)_ `engine/app/security/masking.py` : Presidio (noms, e-mails, téléphones) + regex (IP internes,
  IP externes, postes `SRV-/PC-/DC-…`, comptes `p.nom`, `svc-*`, `compte admin`). Pseudonymes
  `<PERSONNE_1>`, `<IP_EXT_1>`, `<HOTE_1>`, `<COMPTE_1>`… Le LLM ne voit que les pseudonymes ;
  `resolve_action_param()` ne résout que `IP_EXT` / `HOTE` / `COMPTE` (le LLM ne peut ni inventer
  une cible, ni viser une IP interne ou une personne).
- _(local, non commité)_ `engine/app/security/vault.py` + `store.py` : SQLite (`data/runtime/engine.db`), table de
  pseudonymes chiffrée Fernet (`VAULT_KEY`).
- _(local, non commité)_ `engine/app/security/injection.py` : 8 règles FR/EN + classifieur TF-IDF/régression logistique
  entraîné sur `injection_seed.jsonl` (81 exemples). La détection tourne sur le texte d'origine,
  côté serveur, avant qu'il soit jeté.
- _(local, non commité)_ `engine/app/ingest/` : détection FR/EN, conversion Wazuh / Suricata EVE → texte + entités.
- `data/kb/` : 20 procédures IT + 10 fiches cyber MITRE, front matter YAML avec un bloc `graph`
  (problèmes, symptômes, causes, solutions, outil executor associé) prêt pour Neo4j.
- _(local, non commité)_ `engine/app/llm/base.py`, `providers.py` : **ébauche non testée** (interface `LLMProvider`,
  Ollama, API Anthropic `claude-opus-5-5` avec garde-fou anti-texte-non-masqué, traces).

## Feuille de route — reste à faire côté Antoine

Ordre proposé, chaque item = une petite étape testable.

**S2 — fin du parcours minimal (étape 3c)**
1. `.env.example` (le README y fait référence mais il n'existe pas). Retirer `.venv/` (4 180 fichiers)
   et les `.DS_Store` du dépôt : ils ont été commités dans « First commit » (le `.gitignore` est en place).
2. Tests de l'ébauche LLM (faux LLM qui enregistre les prompts) ; choisir Ollama pour les
   embeddings (`bge-m3` servi par Ollama : pas de torch dans l'image engine).
3. `rag/kb.py` (chargement des fiches), `rag/vector.py` (index vectoriel Neo4j + index mémoire pour
   les tests), réponse sourcée avec règle dure « pas de source → escalade ».
4. Benchmark rapide des LLM locaux (S1 en retard) : qwen2.5 7B vs mistral 7B vs llama3.1 8B,
   sur ~20 tickets, latence + qualité JSON.

**S3** — classification (catégorie, priorité, automatisable) avec Pydantic, 1 nouvel essai puis
escalade ; annotation des ~300 tickets avec Florent (format à définir dans `eval/README.md`).

**S4** — Graph RAG : nœuds `Probleme/Symptome/Cause/Solution/Document/Actif/Ticket` créés depuis le
bloc `graph` des fiches, recherche vecteur + 1-2 sauts ; comparaison RAG / Graph RAG sur 50 tickets.

**S5** — agent LangGraph `ingest → mask → injection_check → classify → retrieve → decide →
(respond | act | escalate) → finalize`, outils construits depuis `GET /v1/tools`, mapping des
4 status. Proposition : l'API exécute `ingest/mask/injection_check` en synchrone (le texte brut
n'est jamais stocké) puis le reste du graphe en tâche de fond.

**S6** — Streamlit (file, vue ticket, validation niveau 2, annulation, audit, réponse humaine) ;
boucle d'apprentissage (extraction → file à valider → Neo4j avec provenance) ; intégration avec
le vrai executor de Florent.

**S7-S9** — `eval/run_eval.py`, comparaisons (local/API, RAG/Graph RAG, avant/après 2 cycles),
Langfuse, optimisation des seuils, rapport, démo.

### À valider par Antoine

- Le dossier PDF et les prompts ne répartissent pas les tâches pareil (voir **A-Q1**).
- Catégories de la KB : la fatigue MFA est rangée en `bruteforce` et le voyage impossible en
  `acces_compte`, faute de catégorie exacte. Ajouter `compte_compromis` à la liste fermée ?
- Un ticket utilisateur qui **ordonne** une action sur une cible protégée (ex. « désactive
  admin ») est marqué suspect donc escaladé. Choix volontairement prudent.

## Infos utiles pour Florent

- ⚠️ **Piège Python** : `ipaddress.ip_address("203.0.113.5").is_private` vaut `True` (et
  `is_global` vaut `False`), comme pour `198.51.100.23` : ce sont des plages de documentation. Si
  le moteur d'autorisation utilise `is_private`/`is_global`, les scénarios `ssh_bruteforce` et
  `port_scan` finiront en `pending_approval` au lieu de `executed`. Tester explicitement les
  réseaux RFC 1918 + bouclage (voir `mock_executor/app/catalog.py`, `_NEVER_AUTO_BLOCK`).
- Le `mock_executor` suit le contrat v1 ; son test de conformité peut servir de modèle pour le
  test « le contrat correspond aux routes exposées » demandé dans le prompt de Florent.

## Points d'intégration avec l'executor de Florent

- L'engine lit `EXECUTOR_URL` (défaut `http://executor:8100` dans compose) et `EXECUTOR_API_KEY`.
- Dans `docker-compose.yml`, le service s'appelle `executor`, port `8100`. Aujourd'hui il est construit
  depuis `./mock_executor`. Pour brancher le vrai module : `docker-compose.override.yml` avec
  `services: { executor: { build: ./executor } }` (ou changer `EXECUTOR_URL`).
- Délai côté engine : 5 s par appel, **une seule** nouvelle tentative avec le **même** `request_id`,
  puis escalade du ticket. Jamais d'action par défaut. Approbations et annulations ne sont jamais rejouées.
- Ce que l'engine suppose du contrat (à confirmer par Florent, voir demandes) :
  - `reject` sur `/v1/approvals/{audit_id}` → réponse avec `status: "refused"` ;
  - `/v1/undo/{audit_id}` crée une **nouvelle** entrée d'audit (`undo_of` = l'audit annulé) et renvoie son `audit_id` ;
  - un outil inconnu renvoie `level: 3`, `status: "refused"` ;
  - `result` est un objet libre propre à chaque outil ; l'engine l'affiche tel quel, sans l'interpréter
    pour autoriser quoi que ce soit.

## Demandes à Florent

- **A-Q1** — Le dossier PDF (`docs/Dossier_projet…pdf`, §8) attribue à Florent « Masquage PII, API FastAPI »
  (S3) et « Interface Streamlit » (S6), alors que les deux prompts (`docs/prompt_*.md`) les attribuent à
  Antoine. On prend **les prompts comme référence** (Antoine : masquage, API engine, Streamlit ;
  Florent : executor). Merci de confirmer.
- **A-Q2** — Confirmer les 3 suppositions de la section « Points d'intégration » (reject → `refused`,
  undo = nouvelle entrée d'audit, outil inconnu → niveau 3).
- **A-Q3** — Pouvoir mettre dans `Florent.md` un exemple de `result` pour chaque outil
  (`logs_search`, `account_info`, `block_ip`, `force_password_reset`, `isolate_host`, `disable_account`)
  et le champ `reversible` de chacun, pour que le `mock_executor` renvoie la même forme que le vrai module.
  (Mock actuel : `block_ip`, `force_password_reset`, `isolate_host`, `disable_account` réversibles.)
- **A-Q4** — S3 : annotation commune du jeu de ~300 tickets (dont 30 piégés). Proposer un créneau ;
  le format d'annotation sera dans `eval/README.md` (à venir).

## Réponses à Florent

_(aucune question de Florent pour l'instant)_

## Commandes utiles

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r engine/requirements.txt -r mock_executor/requirements-dev.txt
.venv/bin/python -m spacy download fr_core_news_md && .venv/bin/python -m spacy download en_core_web_md
cd engine && ../.venv/bin/python -m pytest -q          # tests du moteur
cd mock_executor && ../.venv/bin/python -m pytest -q   # tests du faux executor
docker compose up -d --build                           # tout lancer (engine :8000, ui :8501, executor :8100)
```

## Journal

- **2026-10-19** — Séance de préparation. Création des fichiers de coordination. Étape 2 faite
  (mock_executor + client, testés), étape 3a faite (ingestion, masquage, injection, stockage
  chiffré, testés), KB rédigée. Implémentation arrêtée à la demande d'Antoine (séance de
  préparation uniquement) : l'ébauche LLM reste non testée, le RAG n'est pas commencé.
  Commit : KB + `.gitignore` + ce fichier. Le code de la 3a et l'ébauche LLM restent locaux.
