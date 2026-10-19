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

## État

| Étape | Contenu | État |
| --- | --- | --- |
| 1 | Socle : structure, compose, modèles `Ticket` / `Decision`, contrat v1 | ✅ fait |
| 2 | `mock_executor` complet + `executor_client` testés | 🔄 en cours |
| 3 | Parcours minimal ticket → masquage → RAG vectoriel → réponse sourcée | ⏳ à faire |
| 4 | Injection, classification, Graph RAG, action, Streamlit, apprentissage, évaluation | ⏳ à faire |

## Points d'intégration avec l'executor de Florent

- L'engine lit `EXECUTOR_URL` (défaut `http://executor:8100` dans compose) et `EXECUTOR_API_KEY`.
- Dans `docker-compose.yml`, le service s'appelle `executor`, port `8100`. Aujourd'hui il est construit
  depuis `./mock_executor`. Pour brancher le vrai module : `docker-compose.override.yml` avec
  `services: { executor: { build: ./executor } }` (ou changer `EXECUTOR_URL`).
- Délai côté engine : 5 s par appel, **une seule** nouvelle tentative avec le **même** `request_id`,
  puis escalade du ticket. Jamais d'action par défaut.
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
  pour que le `mock_executor` renvoie la même forme que le vrai module.
- **A-Q4** — S3 : annotation commune du jeu de ~300 tickets (dont 30 piégés). Proposer un créneau ;
  le format d'annotation sera dans `eval/README.md` (à venir).

## Réponses à Florent

_(aucune question de Florent pour l'instant)_

## Commandes utiles

```bash
cd engine && pytest -q                 # tests du moteur
cd mock_executor && pytest -q          # tests du faux executor
docker compose up -d --build           # tout lancer (engine :8000, ui :8501, executor :8100)
```

## Journal

- **2026-10-19** — Création des fichiers de coordination. Étape 1 constatée faite. Démarrage étape 2.
