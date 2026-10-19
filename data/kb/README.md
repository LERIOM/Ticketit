# Base de connaissance TicketIt (Exemplia SA)

Base de connaissance de l'agent TicketIt : 20 procédures IT (`procedures/`) et 10 fiches de réponse cyber inspirées de MITRE ATT&CK (`cyber/`). L'entreprise, les serveurs et les comptes sont fictifs (Exemplia SA, domaine `exemplia.local`).

Actifs de référence : `SRV-WEB-01` (serveur web exposé), `DC-01` (contrôleur de domaine, protégé), `PC-COMPTA-07` (poste de la comptabilité), `SRV-FILE-01` (serveur de fichiers). Comptes protégés : `admin`, `svc-backup`.

## Format des fichiers

Nom : `KB-IT-NNN-<slug>.md` (procédure) ou `KB-CY-NNN-<slug>.md` (fiche cyber). Chaque fichier commence par un front matter YAML (lisible par `yaml.safe_load`), suivi d'un corps Markdown de 25 à 60 lignes.

| Champ | Contenu |
|---|---|
| `id` | `KB-IT-001` à `KB-IT-020`, `KB-CY-001` à `KB-CY-010` |
| `title` | Titre de la fiche |
| `kind` | `procedure` ou `fiche_cyber` |
| `category` | Une valeur parmi `acces_compte`, `mot_de_passe`, `messagerie`, `reseau`, `logiciel`, `materiel`, `impression`, `phishing`, `malware`, `bruteforce`, `scan_reseau`, `fuite_donnees`, `autre` |
| `priority_hint` | `P1` (critique) à `P4` (faible) |
| `language`, `version`, `updated`, `author`, `tags` | Métadonnées (`version` et `updated` sont des chaînes) |
| `mitre` | Techniques ATT&CK (ex. `["T1110.001"]`) ; `[]` pour les procédures |
| `graph.problemes[]` | 1 à 3 problèmes : `id` (préfixe `P-`, unique dans toute la KB), `label`, `symptomes` (2 à 5), `causes` (1 à 3), `solutions` (1 à 3), `actifs` |
| `solutions[]` | `id` (préfixe `S-`, unique), `label`, `automatable` (booléen), `action`, `action_target` |

`action` vaut `null` ou un outil parmi `logs_search`, `account_info`, `block_ip`, `force_password_reset`, `isolate_host`, `disable_account` ; `action_target` vaut alors `ip`, `username` ou `hostname` (et `null` si `action` est `null`). `automatable: false` signale une étape qui exige un humain (validation d'un manager, achat, création de compte, isolement).

Corps des procédures : `## Contexte`, `## Étapes`, `## Vérification`, `## Quand escalader`.
Corps des fiches cyber : `## Contexte`, `## Indicateurs`, `## Analyse (questions à se poser)`, `## Réponse`, `## Actions automatisables et niveau d'autorisation`, `## Quand escalader`.

## Niveaux d'autorisation des actions

Ces niveaux sont appliqués par le module d'exécution, pas par l'agent : l'agent propose, l'exécuteur décide.

| Niveau | Actions | Règle |
|---|---|---|
| 0 | `logs_search`, `account_info` | Lecture seule, automatique |
| 1 | `block_ip` (IP externe, 1 à 24 h), `force_password_reset` | Automatique si confiance ≥ 0,80 et cible non protégée, sinon validation humaine |
| 2 | `isolate_host`, `disable_account` | Toujours validation humaine |
| 3 | Suppression de données, modification de la politique du pare-feu, tout le reste | Interdit |

Une IP interne (RFC 1918) n'est jamais bloquée automatiquement. `admin`, `svc-backup` et `DC-01` sont protégés.

## Liste des fiches

| ID | Titre | Catégorie | Priorité | MITRE |
|---|---|---|---|---|
| `KB-IT-001` | [Mot de passe expiré ou oublié](procedures/KB-IT-001-mot-de-passe-expire-oublie.md) | `mot_de_passe` | P3 | — |
| `KB-IT-002` | [Compte Active Directory verrouillé](procedures/KB-IT-002-compte-verrouille.md) | `acces_compte` | P3 | — |
| `KB-IT-003` | [MFA : nouveau téléphone, téléphone perdu ou réinscription](procedures/KB-IT-003-mfa-nouveau-telephone.md) | `acces_compte` | P3 | — |
| `KB-IT-004` | [Le VPN Exemplia ne se connecte pas](procedures/KB-IT-004-vpn-connexion-impossible.md) | `reseau` | P3 | — |
| `KB-IT-005` | [VPN lent ou déconnexions répétées](procedures/KB-IT-005-vpn-lent-deconnexions.md) | `reseau` | P4 | — |
| `KB-IT-006` | [Wi-Fi d'entreprise : connexion impossible ou accès invité](procedures/KB-IT-006-wifi-entreprise.md) | `reseau` | P3 | — |
| `KB-IT-007` | [Outlook ne synchronise pas ou boîte aux lettres pleine](procedures/KB-IT-007-outlook-synchronisation-boite-pleine.md) | `messagerie` | P3 | — |
| `KB-IT-008` | [Partage de calendrier et accès à une boîte aux lettres partagée](procedures/KB-IT-008-calendrier-boite-partagee.md) | `messagerie` | P4 | — |
| `KB-IT-009` | [Teams : micro ou caméra qui ne fonctionne pas](procedures/KB-IT-009-teams-micro-camera.md) | `logiciel` | P3 | — |
| `KB-IT-010` | [Impression bloquée ou document introuvable sur le copieur (PaperCut)](procedures/KB-IT-010-imprimante-file-attente.md) | `impression` | P3 | — |
| `KB-IT-011` | [Numérisation vers e-mail : document non reçu ou trop volumineux](procedures/KB-IT-011-scanner-vers-email.md) | `impression` | P4 | — |
| `KB-IT-012` | [Installer un logiciel via le Portail d'entreprise](procedures/KB-IT-012-installation-logiciel-portail.md) | `logiciel` | P4 | — |
| `KB-IT-013` | [Logiciel qui plante : réparation ou réinstallation](procedures/KB-IT-013-logiciel-plante-reinstallation.md) | `logiciel` | P3 | — |
| `KB-IT-014` | [Accès à un dossier partagé : accès refusé ou lecteur réseau absent](procedures/KB-IT-014-acces-dossier-partage.md) | `acces_compte` | P3 | — |
| `KB-IT-015` | [Poste de travail lent](procedures/KB-IT-015-poste-lent.md) | `materiel` | P4 | — |
| `KB-IT-016` | [Écran externe ou station d'accueil qui ne fonctionne pas](procedures/KB-IT-016-ecran-externe-station.md) | `materiel` | P4 | — |
| `KB-IT-017` | [Ordinateur portable perdu, volé ou à renouveler](procedures/KB-IT-017-portable-renouvellement-perte.md) | `materiel` | P2 | — |
| `KB-IT-018` | [OneDrive ne synchronise plus](procedures/KB-IT-018-onedrive-synchronisation.md) | `logiciel` | P3 | — |
| `KB-IT-019` | [Accès refusé ou connexion impossible à l'ERP](procedures/KB-IT-019-acces-erp-refuse.md) | `acces_compte` | P3 | — |
| `KB-IT-020` | [Nouvel arrivant : création de compte et première connexion](procedures/KB-IT-020-nouvel-arrivant.md) | `acces_compte` | P3 | — |
| `KB-CY-001` | [Force brute SSH sur un serveur exposé](cyber/KB-CY-001-force-brute-ssh.md) | `bruteforce` | P2 | T1110.001 |
| `KB-CY-002` | [Scan de ports réseau](cyber/KB-CY-002-scan-ports.md) | `scan_reseau` | P3 | T1046 |
| `KB-CY-003` | [Phishing avec saisie d'identifiants](cyber/KB-CY-003-phishing-saisie-identifiants.md) | `phishing` | P1 | T1566.002, T1078 |
| `KB-CY-004` | [Password spraying sur les comptes de l'entreprise](cyber/KB-CY-004-password-spraying.md) | `bruteforce` | P2 | T1110.003 |
| `KB-CY-005` | [Fatigue MFA : bombardement de notifications Authenticator](cyber/KB-CY-005-fatigue-mfa.md) | `bruteforce` | P1 | T1621 |
| `KB-CY-006` | [Rançongiciel : chiffrement de fichiers](cyber/KB-CY-006-rancongiciel.md) | `malware` | P1 | T1486 |
| `KB-CY-007` | [Exécution PowerShell suspecte](cyber/KB-CY-007-powershell-suspect.md) | `malware` | P2 | T1059.001 |
| `KB-CY-008` | [Exfiltration de données](cyber/KB-CY-008-exfiltration-donnees.md) | `fuite_donnees` | P1 | T1048 |
| `KB-CY-009` | [Connexion impossible (voyage impossible) sur un compte](cyber/KB-CY-009-voyage-impossible.md) | `acces_compte` | P2 | T1078 |
| `KB-CY-010` | [Clé USB malveillante](cyber/KB-CY-010-cle-usb-malveillante.md) | `malware` | P2 | T1091 |

Scénarios de démonstration : `KB-CY-001` (force brute SSH, `block_ip`), `KB-CY-002` (scan de ports, `block_ip` + `logs_search`), `KB-CY-003` (phishing, `force_password_reset`, et `isolate_host` si un fichier a été exécuté).
