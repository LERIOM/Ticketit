---
id: KB-CY-006
title: "Rançongiciel : chiffrement de fichiers"
kind: fiche_cyber
category: malware
priority_hint: P1
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [rançongiciel, ransomware, chiffrement, serveur de fichiers, gestion de crise]
mitre: ["T1486"]
graph:
  problemes:
    - id: P-rancongiciel-poste
      label: "Chiffrement de fichiers par un rançongiciel sur un poste"
      symptomes:
        - "tous mes fichiers ont une extension bizarre et ne s'ouvrent plus"
        - "un fichier LISEZ-MOI me demande une rançon en bitcoins"
        - "alerte EDR : chiffrement massif de fichiers sur PC-COMPTA-07"
        - "mon fond d'écran a été remplacé par un message de rançon"
      causes:
        - "exécution d'une pièce jointe ou d'un programme malveillant"
        - "compte compromis utilisé pour déployer le rançongiciel"
      solutions:
        - id: S-ransom-consignes-utilisateur
          label: "Consignes immédiates : débrancher le câble réseau, couper le Wi-Fi, ne pas éteindre"
          automatable: true
          action: null
          action_target: null
        - id: S-ransom-isolement-poste
          label: "Isoler le poste infecté via l'EDR (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
        - id: S-ransom-desactivation-compte
          label: "Désactiver le compte utilisé par le rançongiciel (validation humaine)"
          automatable: false
          action: disable_account
          action_target: username
      actifs: ["PC-COMPTA-07"]
    - id: P-rancongiciel-partages
      label: "Modifications massives de fichiers sur le serveur de fichiers"
      symptomes:
        - "des milliers de fichiers modifiés en quelques minutes sur SRV-FILE-01"
        - "les fichiers du lecteur partagé sont renommés en masse"
      causes:
        - "poste infecté chiffrant les partages réseau auxquels il a accès"
      solutions:
        - id: S-ransom-source-partages
          label: "Identifier le poste et le compte à l'origine des modifications"
          automatable: true
          action: logs_search
          action_target: hostname
      actifs: ["SRV-FILE-01"]
---

# Rançongiciel : chiffrement de fichiers (T1486)

## Contexte
Un rançongiciel chiffre les fichiers (MITRE ATT&CK T1486, Data Encrypted for Impact) du poste infecté puis des partages accessibles, en particulier `SRV-FILE-01`, et réclame une rançon. C'est l'incident le plus grave : priorité P1, cellule de crise. Les postes de la comptabilité, comme `PC-COMPTA-07`, sont des cibles fréquentes (pièces jointes de « factures »).

## Indicateurs
- Fichiers renommés avec une extension inconnue, impossibles à ouvrir ; note de rançon (`LISEZ-MOI.txt`, `HOW_TO_DECRYPT.html`) dans chaque dossier.
- Alerte EDR : chiffrement ou renommage massif, suppression des clichés instantanés (`vssadmin delete shadows`).
- `SRV-FILE-01` : pic d'écritures et de renommages depuis un seul compte ou un seul poste.
- Antivirus désactivé, fond d'écran modifié, processus inconnu très consommateur de disque.

## Analyse (questions à se poser)
1. Quel est le premier poste touché et quel compte y était connecté ?
2. Le chiffrement est-il encore actif ? Quels partages ont été atteints ?
3. Les sauvegardes sont-elles intactes (compte `svc-backup` non compromis, sauvegardes hors ligne disponibles) ?
4. Y a-t-il eu exfiltration avant le chiffrement (double extorsion, voir KB-CY-008) ?
5. Des données personnelles sont-elles concernées (obligation de notification à la CNIL sous 72 heures) ?

## Réponse
1. Consigne immédiate à l'utilisateur : débrancher le câble réseau et couper le Wi-Fi, **ne pas éteindre** le poste (preuves en mémoire), ne rien supprimer.
2. Demander l'isolement du poste via l'EDR (`isolate_host`, validation humaine).
3. Identifier la source des modifications sur `SRV-FILE-01` (`logs_search`) et demander la désactivation du compte utilisé (`disable_account`, validation humaine).
4. Le SOC déclenche la cellule de crise (RSSI, direction, DPO) et vérifie l'intégrité des sauvegardes ; il ne faut jamais toucher au compte `svc-backup` ni à `DC-01` sans le SOC.
5. Ne jamais payer la rançon ni contacter les attaquants ; conserver la note de rançon pour l'enquête.
6. La restauration est décidée et réalisée par les équipes humaines, après éradication.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Poste, `SRV-FILE-01` | 0 | Automatique (lecture seule) |
| `account_info` | Compte suspect | 0 | Automatique (lecture seule) |
| `isolate_host` | Poste infecté | 2 | Toujours validée par un humain ; jamais sur `DC-01` |
| `disable_account` | Compte utilisé | 2 | Toujours validée par un humain ; jamais sur `svc-backup` ou `admin` |
| Supprimer ou restaurer des fichiers, modifier le pare-feu | — | 3 | Interdit à l'agent |

## Quand escalader
- Toujours, immédiatement : SOC et RSSI, priorité P1, dès le premier signalement.
- Plusieurs postes ou serveurs touchés : cellule de crise, notification ANSSI / CERT-FR envisagée par le RSSI.
- Données personnelles concernées : DPO, notification CNIL sous 72 heures.
