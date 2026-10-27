# TicketIt

Agent IA de traitement des tickets de support IT et cybersécurité (projet ISEN, binôme Antoine / Florent).
L'agent (`engine`) propose des actions ; le module `executor` (Florent) décide et exécute, selon le contrat
[`contracts/executor_v1.openapi.yaml`](contracts/executor_v1.openapi.yaml).

## Démarrer

```bash
cp .env.example .env              # puis changer les mots de passe
docker compose up -d --build      # engine :8000, ui :8501, executor :8100, neo4j :7474
docker compose exec ollama ollama pull qwen2.5:7b-instruct
docker compose --profile observability up -d   # optionnel : Langfuse sur :3000
```

Vérifier : `curl localhost:8000/health` et `curl -H "X-API-Key: change-me" localhost:8100/v1/health`.

## Tests

```bash
cd engine && pip install -r requirements.txt && pytest -q
```

## Structure

```
engine/app/          API FastAPI, modèles, agent (ingest, security, classify, rag, llm, agent, learning)
engine/app/executor_client.py   seul point d'accès à l'executor
ui/                  Streamlit
mock_executor/       faux executor conforme au contrat v1 (EXECUTOR_URL choisit faux ou vrai)
contracts/           contrat v1, identique chez Antoine et Florent
eval/  data/         évaluation, base de connaissance, tickets annotés
```

## Avancement

- [x] Étape 1 : socle (structure, compose, modèles `Ticket` / `Decision`, contrat v1)
- [ ] Étape 2 : `mock_executor` complet et `executor_client` testés
- [ ] Étape 3 : parcours minimal ticket → masquage → RAG vectoriel → réponse sourcée
- [ ] Étape 4 : injection, classification, Graph RAG, action, Streamlit, apprentissage, évaluation
