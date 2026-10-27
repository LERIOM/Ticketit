# TicketIt

> An AI agent that triages IT support and cybersecurity tickets, proposes actions, and hands them to a separate executor that decides and acts.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?logo=neo4j&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-black)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20progress-orange)

9-week engineering project at ISEN Nantes (AI track), built in pairs by **Antoine Riom** (agent / `engine`) and **Florent** (`executor`).

[Version française](README.fr.md)

## How it works

```
 ticket ──► engine (agent) ──────────────► executor ──► action
            ingest → mask sensitive data      decides and executes,
            → injection check → classify      following contract v1
            → RAG (vector + graph) → LLM
            → proposed action + sources
```

The agent never acts on its own. It **proposes**; the executor **decides and executes**. The two sides only talk through a frozen API contract, [`contracts/executor_v1.openapi.yaml`](contracts/executor_v1.openapi.yaml), so each half can be built and tested independently (a contract-compliant `mock_executor` stands in for the real one).

## Stack

| Layer | Tools |
|---|---|
| Agent API | FastAPI, Pydantic |
| LLM | Ollama (`qwen2.5:7b-instruct`), running locally |
| Retrieval | Vector RAG + Graph RAG on Neo4j |
| UI | Streamlit |
| Observability | Langfuse (optional profile) |
| Infra | Docker Compose |

## Getting started

```bash
cp .env.example .env              # then change the passwords
docker compose up -d --build      # engine :8000, ui :8501, executor :8100, neo4j :7474
docker compose exec ollama ollama pull qwen2.5:7b-instruct
docker compose --profile observability up -d   # optional: Langfuse on :3000
```

Health checks:

```bash
curl localhost:8000/health
curl -H "X-API-Key: change-me" localhost:8100/v1/health
```

## Tests

```bash
cd engine && pip install -r requirements.txt && pytest -q
```

## Project layout

```
engine/app/                    FastAPI agent: ingest, security, classify, rag, llm, agent, learning
engine/app/executor_client.py  the only entry point to the executor
executor/                      real executor (Florent)
mock_executor/                 fake executor that follows contract v1 (EXECUTOR_URL picks fake or real)
ui/                            Streamlit front end
contracts/                     contract v1, shared by both sides
eval/  data/                   evaluation, knowledge base, annotated tickets
docs/                          project brief and working prompts
```

## Roadmap

- [x] Step 1: foundations (structure, compose, `Ticket` / `Decision` models, contract v1)
- [ ] Step 2: complete `mock_executor` and tested `executor_client`
- [ ] Step 3: minimal path: ticket → masking → vector RAG → sourced answer
- [ ] Step 4: injection detection, classification, Graph RAG, actions, Streamlit, learning loop, evaluation
