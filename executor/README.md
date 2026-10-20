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

## Laboratoire SQLite

Depuis ce dossier, créer un répertoire local puis initialiser la base :

```powershell
New-Item -ItemType Directory -Force runtime
.\.venv\Scripts\python.exe -m scripts.seed_lab --database runtime/lab.sqlite3 --logs runtime/events.jsonl
```

La commande réinitialise **uniquement les quatre tables lab_*** de la base choisie :
comptes, postes, blocages et logs. Ne pas l'utiliser sur un labo dont on veut
conserver l'état. Le chemin parent doit déjà exister. L'export JSONL est facultatif ;
sa création est séparée de la transaction SQLite (un échec d'export ne défait pas le seed).

Choix internes des fixtures, sans changement du contrat :

- Comptes j.martin, admin et svc-backup initialement actifs, drapeau de changement
  de mot de passe désactivé.
- Postes SRV-WEB-01, PC-COMPTA-07 et DC-01 initialement non isolés.
- Aucun blocage initial. L'adresse piège 10.0.0.12 sert à une future demande
  d'exécution ; elle n'est pas prébloquée.
- Douze échecs SSH, une alerte agrégée de scan (300 ports en 30 secondes) et
  un événement de phishing. Horloge de référence fixe : 2026-11-03T12:00:00Z.
  Une future recherche temporelle devra utiliser une horloge injectable pour
  les tests ; ces événements ne représentent pas les dernières minutes réelles.
- JSONL interne inspiré des logs de sécurité, pas encore le schéma de hits
  de logs_search. Les protections relèveront de la politique d'autorisation,
  pas des tables d'état du labo.

La création des tables est non destructive. Les modifications et le seed sont
transactionnels, les connexions sont fermées après usage. Les tables éventuelles
d'audit/idempotence ne sont ni effacées ni modifiées : leur remise à zéro reste
à clarifier (F-Q14). **Ce seed n'est donc pas encore le reset global du service** :
ne pas l'associer à un executor métier actif avec un historique d'idempotence.

## Conteneur

Depuis la racine du dépôt, après avoir défini EXECUTOR_API_KEY :

```powershell
docker build -t ticketit-executor ./executor
docker run --rm -p 127.0.0.1:8100:8100 -e EXECUTOR_API_KEY ticketit-executor
```

Le conteneur utilise Python 3.11, un utilisateur non privilégié et écoute sur
0.0.0.0:8100. Le répertoire /service/runtime est inscriptible ; monter un volume
à cet emplacement pour conserver ultérieurement le labo entre conteneurs.
Le serveur health n'initialise ni ne réinitialise automatiquement de base.
Le Compose commun continue d'utiliser le mock jusqu'à l'intégration complète.
Construction Docker non vérifiée dans l'environnement de développement actuel
(Docker indisponible).

## Opérations internes du labo

[app/lab/actions.py](app/lab/actions.py) fournit force_password_reset,
disable_account et isolate_host sur une connexion SQLite appartenant à l'appelant.
Chaque opération capture la valeur précédente et applique la nouvelle valeur
dans la même transaction, sans commit autonome. Une cible inexistante lève
TargetNotFound sans créer d'actif. Les identifiants sont liés comme paramètres SQL.

Ces primitives ne sont pas encore les outils exposés par l'API : elles ne
prennent aucune décision d'autorisation, ne valident pas le contrat métier,
ne créent pas d'audit et ne fournissent pas d'undo. Le futur orchestrateur devra
les appeler uniquement après autorisation, puis écrire l'audit et l'idempotence
dans la même transaction. Aucun endpoint supplémentaire n'est exposé.

Le [pare-feu interne](app/lab/firewall.py) stocke les échéances en UTC et prend
une horloge explicite pour les tests. Un nouveau blocage ne raccourcit jamais
une échéance existante ; les écritures concurrentes sont sérialisées par SQLite.
L'expiration est évaluée à la lecture, sans effacer la valeur précédente.
IPv4/IPv6 sont normalisées par le stockage ; cela ne définit pas encore leur
admissibilité dans l'API ni leur caractère public/protégé (F-Q10).
La [lecture d'annuaire](app/lab/directory.py) renvoie uniquement l'état enregistré ;
le champ protected du futur outil account_info devra provenir de la politique.
