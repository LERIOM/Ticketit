---
id: KB-CY-010
title: "Clé USB malveillante"
kind: fiche_cyber
category: malware
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [clé usb, support amovible, ingénierie sociale, edr, badusb]
mitre: ["T1091"]
graph:
  problemes:
    - id: P-usb-branchee
      label: "Clé USB inconnue branchée sur un poste"
      symptomes:
        - "j'ai trouvé une clé USB sur le parking et je l'ai branchée sur mon PC"
        - "après avoir branché une clé USB une fenêtre s'est ouverte et a tapé des commandes toute seule"
        - "alerte EDR : exécution d'un fichier depuis un lecteur amovible"
      causes:
        - "clé piégée déposée volontairement comme appât"
        - "clé infectée par un ver qui se propage par les supports amovibles"
      solutions:
        - id: S-usb-analyse-poste
          label: "Rechercher les fichiers exécutés et connexions du poste depuis le branchement"
          automatable: true
          action: logs_search
          action_target: hostname
        - id: S-usb-isolement-poste
          label: "Isoler le poste sur lequel la clé a été branchée (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
      actifs: []
    - id: P-usb-trouvee
      label: "Clé USB trouvée, non branchée"
      symptomes:
        - "j'ai trouvé une clé USB dans la salle de réunion, que dois-je en faire"
        - "un courrier contenait une clé USB promotionnelle"
      causes:
        - "tentative d'ingénierie sociale par dépôt de clé"
      solutions:
        - id: S-usb-remise-soc
          label: "Ne pas brancher la clé et la remettre au SOC"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Clé USB malveillante (T1091)

## Contexte
Déposer des clés USB piégées sur un parking, à l'accueil ou dans un courrier est une technique d'accès initial éprouvée (MITRE ATT&CK T1091, Replication Through Removable Media). Une clé peut contenir un programme malveillant, ou se faire passer pour un clavier (« BadUSB ») et taper des commandes en quelques secondes. Chez Exemplia, l'exécution automatique est désactivée, mais un clic suffit.

## Indicateurs
- L'utilisateur a branché une clé d'origine inconnue (trouvée, reçue, offerte lors d'un salon).
- Fenêtre de commande ou PowerShell qui s'ouvre et tape seule juste après le branchement.
- Nouveau périphérique de type clavier détecté au moment du branchement d'une « clé ».
- Alerte EDR : exécution depuis un lecteur amovible (`E:\`, `F:\`), fichier `.lnk` ou `.exe` déguisé en dossier.

## Analyse (questions à se poser)
1. La clé a-t-elle été branchée ? Sur quel poste, à quelle heure ?
2. L'utilisateur a-t-il ouvert un fichier ? Une fenêtre s'est-elle ouverte toute seule ?
3. Le poste a-t-il établi des connexions sortantes inhabituelles après le branchement ?
4. La clé a-t-elle été branchée sur d'autres postes ? D'autres clés ont-elles été trouvées sur le site ?

## Réponse
1. Clé non branchée : demander de ne pas la brancher, de la mettre dans une enveloppe et de la remettre au SOC ou à l'accueil sécurité.
2. Clé branchée : la retirer, ne plus l'utiliser, la remettre au SOC ; ne pas éteindre le poste.
3. Rechercher les exécutions et connexions du poste depuis le branchement (`logs_search`, cible : nom d'hôte).
4. Exécution constatée ou comportement de type BadUSB : demander l'isolement du poste (`isolate_host`, validation humaine) et une analyse EDR complète.
5. Si un compte a été utilisé pendant l'incident, vérifier ses connexions et, en cas de doute, réinitialiser son mot de passe (KB-CY-003).
6. Le SOC prévient la sécurité du site et peut lancer une sensibilisation ciblée.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Poste | 0 | Automatique (lecture seule) |
| `account_info` | Compte de l'utilisateur | 0 | Automatique (lecture seule) |
| `force_password_reset` | Compte de l'utilisateur | 1 | Automatique si confiance ≥ 0,80 et compte non protégé ; sinon validation humaine |
| `isolate_host` | Poste | 2 | Toujours validée par un humain |
| Supprimer des fichiers ou modifier les stratégies USB | — | 3 | Interdit à l'agent |

## Quand escalader
- Toute clé branchée sur un poste Exemplia : SOC, priorité P2 (P1 si exécution confirmée).
- Clé branchée sur un serveur ou sur `PC-COMPTA-07` et autres postes sensibles : SOC immédiatement.
- Plusieurs clés trouvées sur le site : SOC et sécurité du site (campagne ciblée probable).
