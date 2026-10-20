# Banc de test

Page web locale pour lancer les suites de tests du projet et lire le résultat de chaque test.

```bash
.venv/bin/python -m uvicorn app:app --app-dir tools/banc_de_test --host 127.0.0.1 --port 8765
```

Puis ouvrir http://localhost:8765. Suites : moteur, faux executor, régressions de sécurité,
executor de Florent. Historique des 20 derniers passages par suite dans `data/runtime/banc_de_test/`
(non versionné). Le serveur n'écoute que sur 127.0.0.1 et ne lance que les suites déclarées dans `app.py`.
