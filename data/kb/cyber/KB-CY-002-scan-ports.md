---
id: KB-CY-002
title: "Scan de ports réseau"
kind: fiche_cyber
category: scan_reseau
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [scan de ports, reconnaissance, nmap, ids, pare-feu]
mitre: ["T1046"]
graph:
  problemes:
    - id: P-scan-ports-externe
      label: "Scan de ports depuis une IP externe"
      symptomes:
        - "alerte IDS : ET SCAN Nmap Scripting Engine depuis 198.51.100.23"
        - "le pare-feu signale une IP qui contacte plus de 100 ports en une minute"
        - "scan de ports détecté sur SRV-WEB-01"
      causes:
        - "reconnaissance automatisée avant une tentative d'attaque"
        - "moteurs de recherche de services exposés sur Internet"
      solutions:
        - id: S-scan-blocage-temporaire
          label: "Bloquer temporairement l'IP source externe (1 à 24 h)"
          automatable: true
          action: block_ip
          action_target: ip
        - id: S-scan-analyse-journaux
          label: "Analyser les journaux pare-feu et IDS pour l'IP source"
          automatable: true
          action: logs_search
          action_target: ip
      actifs: ["SRV-WEB-01"]
    - id: P-scan-ports-interne
      label: "Scan de ports depuis un poste interne"
      symptomes:
        - "un poste interne balaie les ports SMB et RDP de tout le réseau"
        - "alerte : scan réseau depuis l'adresse interne 10.20.4.57"
      causes:
        - "poste compromis cherchant à se propager"
        - "outil de diagnostic lancé sans autorisation par un utilisateur ou un prestataire"
      solutions:
        - id: S-scan-interne-identification
          label: "Identifier le poste et le compte à l'origine du scan"
          automatable: true
          action: logs_search
          action_target: hostname
        - id: S-scan-interne-isolement
          label: "Isoler le poste source si le scan n'est pas autorisé (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
      actifs: []
---

# Scan de ports réseau (T1046)

## Contexte
Un scan de ports (MITRE ATT&CK T1046, Network Service Discovery) sert à découvrir les services ouverts avant une attaque. Depuis Internet, c'est un bruit de fond quotidien sur `SRV-WEB-01` : il est traité en P3 et bloqué temporairement. Depuis le réseau interne, c'est un signal fort de compromission ou d'usage non autorisé : P2.

## Indicateurs
- Une même IP source contacte de nombreux ports (plus de 100 en une minute) ou de nombreuses machines sur le même port (445, 3389, 22).
- Journaux du pare-feu : rafales de connexions refusées, paquets SYN sans établissement de session.
- Alertes IDS de type `ET SCAN` (Nmap, Masscan, ZMap) ou signatures d'outils de reconnaissance.
- Scan suivi de tentatives d'authentification ou d'exploitation sur un port découvert.

## Analyse (questions à se poser)
1. L'IP source est-elle externe ou interne (RFC 1918) ?
2. S'agit-il du scanner de vulnérabilités du SOC ou d'un test d'intrusion planifié (calendrier des tests autorisés) ?
3. Quels ports ont répondu ? Un service inattendu est-il exposé ?
4. Le scan a-t-il été suivi d'une tentative de connexion (voir KB-CY-001) ou d'exploitation ?
5. Source interne : quel poste, quel compte connecté, quel processus a lancé le scan ?

## Réponse
1. Analyser les journaux pare-feu et IDS pour l'IP source (`logs_search`, cible : IP) : durée, ports, cibles.
2. IP externe : bloquer l'IP 24 heures (`block_ip`) et documenter les ports visés.
3. IP interne : ne jamais bloquer automatiquement. Identifier le poste (`logs_search`, cible : nom d'hôte) et le compte connecté.
4. Scan interne non autorisé : demander l'isolement du poste (`isolate_host`, validation humaine) puis une analyse EDR.
5. Signaler à l'équipe réseau tout service exposé inattendu (fermeture par un humain, jamais par l'agent).

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | IP ou poste source | 0 | Automatique (lecture seule) |
| `block_ip` | IP externe | 1 | Automatique si confiance ≥ 0,80, durée 1 à 24 h ; jamais pour une IP RFC 1918 |
| `isolate_host` | Poste interne source | 2 | Toujours validée par un humain ; jamais sur `DC-01` |
| Modifier les règles ou la politique du pare-feu | — | 3 | Interdit à l'agent |

## Quand escalader
- Toute source interne non identifiée comme scanner autorisé : SOC, priorité P2.
- Scan suivi d'une tentative d'exploitation ou d'authentification réussie : SOC, priorité P1.
- Scan provenant de `DC-01` ou d'un serveur : SOC immédiatement, aucune action automatique.
