"""Banc de test local : lancer les suites pytest du projet depuis une page web et lire les résultats.

Lancement (depuis la racine du dépôt) :
    .venv/bin/python -m uvicorn app:app --app-dir tools/banc_de_test --host 127.0.0.1 --port 8765
puis ouvrir http://localhost:8765

Sécurité : écoute sur 127.0.0.1 uniquement, et ne lance QUE les suites déclarées ci-dessous
(aucune commande ni chemin venant de la page).
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "runtime" / "banc_de_test"
HISTORY = 20          # passages gardés par suite
TIMEOUT_S = 900

SUITES = {
    "moteur": {"nom": "Moteur (engine)", "qui": "Antoine", "dossier": "engine", "cibles": [],
               "description": "Modèles, client executor, ingestion, masquage, injection."},
    "faux_executor": {"nom": "Faux executor", "qui": "Antoine", "dossier": "mock_executor", "cibles": [],
                      "description": "Niveaux, idempotence, audit, conformité au contrat."},
    "securite": {"nom": "Sécurité (régressions)", "qui": "Antoine", "dossier": "mock_executor",
                 "cibles": ["tests/test_security_regressions.py"],
                 "description": "Les bugs trouvés en recette ne doivent jamais revenir."},
    "executor_florent": {"nom": "Executor de Florent", "qui": "Florent", "dossier": "executor", "cibles": [],
                         "description": "Health, authentification, labo simulé.",
                         "env": {"EXECUTOR_API_KEY": "cle-du-banc-de-test"}},
}

app = FastAPI(title="Banc de test TicketIt", docs_url=None, redoc_url=None, openapi_url=None)
_locks = {sid: threading.Lock() for sid in SUITES}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _history_file(sid: str) -> Path:
    return RESULTS / f"{sid}.json"


def _load(sid: str) -> list[dict]:
    try:
        return json.loads(_history_file(sid).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def _parse_junit(path: Path) -> list[dict]:
    tests = []
    for case in ET.parse(path).getroot().iter("testcase"):
        status, message, detail = "ok", "", ""
        for tag, label in (("failure", "échec"), ("error", "erreur"), ("skipped", "ignoré")):
            node = case.find(tag)
            if node is not None:
                status, message = label, node.get("message", "")
                detail = (node.text or "")[-4000:]
                break
        fichier = (case.get("classname") or "").replace(".", "/")
        tests.append({"fichier": fichier, "nom": case.get("name", ""), "statut": status,
                      "duree_s": round(float(case.get("time") or 0), 3),
                      "message": message[:500], "detail": detail})
    return tests


def _run(sid: str) -> dict:
    suite = SUITES[sid]
    cwd = ROOT / suite["dossier"]
    if not cwd.is_dir():
        return {"suite": sid, "date": _now(), "statut": "absente", "tests": [],
                "resume": {"total": 0, "ok": 0, "echecs": 0, "ignores": 0},
                "sortie": f"Dossier introuvable : {suite['dossier']}", "duree_s": 0}
    with tempfile.TemporaryDirectory() as tmp:
        junit = Path(tmp) / "junit.xml"
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:warnings", "-p", "no:cacheprovider",
               f"--junitxml={junit}", *suite["cibles"]]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **suite.get("env", {})}
        start = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=TIMEOUT_S)
            sortie, code = (proc.stdout + proc.stderr)[-6000:], proc.returncode
        except subprocess.TimeoutExpired:
            sortie, code = f"Arrêté après {TIMEOUT_S} s", -1
        duree = round(time.monotonic() - start, 1)
        tests = _parse_junit(junit) if junit.exists() else []
    resume = {"total": len(tests),
              "ok": sum(t["statut"] == "ok" for t in tests),
              "echecs": sum(t["statut"] in ("échec", "erreur") for t in tests),
              "ignores": sum(t["statut"] == "ignoré" for t in tests)}
    statut = "vert" if code == 0 and resume["echecs"] == 0 else "rouge"
    return {"suite": sid, "date": _now(), "statut": statut, "resume": resume,
            "duree_s": duree, "tests": tests, "sortie": sortie}


def _run_and_save(sid: str) -> dict:
    lock = _locks[sid]
    if not lock.acquire(blocking=False):
        raise HTTPException(409, "Cette suite est déjà en cours.")
    try:
        result = _run(sid)
        RESULTS.mkdir(parents=True, exist_ok=True)
        history = [result, *_load(sid)][:HISTORY]
        _history_file(sid).write_text(json.dumps(history, ensure_ascii=False), encoding="utf-8")
        return result
    finally:
        lock.release()


@app.get("/")
def page() -> FileResponse:
    return FileResponse(Path(__file__).with_name("index.html"))


@app.get("/api/suites")
def suites() -> list[dict]:
    out = []
    for sid, s in SUITES.items():
        history = _load(sid)
        last = history[0] if history else None
        out.append({"id": sid, "nom": s["nom"], "qui": s["qui"], "description": s["description"],
                    "en_cours": _locks[sid].locked(),
                    "dernier": last and {k: last[k] for k in ("date", "statut", "resume", "duree_s")},
                    "historique": [{k: h[k] for k in ("date", "statut", "resume")} for h in history]})
    return out


@app.post("/api/run/{sid}")
def run(sid: str) -> dict:
    if sid not in SUITES:
        raise HTTPException(404, "Suite inconnue.")
    return _run_and_save(sid)


@app.get("/api/resultat/{sid}")
def resultat(sid: str) -> dict:
    if sid not in SUITES:
        raise HTTPException(404, "Suite inconnue.")
    history = _load(sid)
    if not history:
        raise HTTPException(404, "Pas encore lancée.")
    return history[0]
