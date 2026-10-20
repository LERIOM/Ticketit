# Executor — socle S1

Python 3.11+. Seule la route `GET /v1/health` est implémentée à ce stade.
Elle renvoie `{"status":"ok","version":"1.0"}` avec une clé valide, sinon `401`.
Le [contrat partagé](../contracts/executor_v1.openapi.yaml) décrit aussi les
routes métier à implémenter ; le service n'est pas encore prêt pour l'intégration complète.

## Lancement local (PowerShell)

Depuis ce dossier :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:EXECUTOR_API_KEY = Read-Host "Cle API executor"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

Définir la clé avant le démarrage : elle est chargée à la création de l'application.
Une configuration absente ou vide refuse tous les appels, sans clé de secours.
Le service compare la clé reçue dans `X-API-Key` sans la journaliser.
Les routes automatiques de documentation sont désactivées pour ne pas ajouter
de routes au contrat.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests de réponse health, clés absente/vide/invalide, configuration absente/vide,
authentification uniquement par en-tête et absence de routes supplémentaires.

Les questions métier restantes sont suivies dans
[communication.md](../communication.md).
