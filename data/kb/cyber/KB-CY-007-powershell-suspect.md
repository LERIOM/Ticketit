---
id: KB-CY-007
title: "Exécution PowerShell suspecte"
kind: fiche_cyber
category: malware
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [powershell, script, edr, commande encodée, post-exploitation]
mitre: ["T1059.001"]
graph:
  problemes:
    - id: P-powershell-suspect
      label: "Exécution PowerShell suspecte sur un poste"
      symptomes:
        - "alerte EDR : powershell.exe lancé avec le paramètre -EncodedCommand"
        - "PowerShell lancé par Word ou Outlook"
        - "une fenêtre bleue PowerShell s'est ouverte et refermée toute seule"
        - "téléchargement via IEX et Net.WebClient détecté sur un poste"
      causes:
        - "macro ou pièce jointe malveillante"
        - "script de post-exploitation lancé par un attaquant"
      solutions:
        - id: S-ps-analyse-journaux
          label: "Analyser les journaux PowerShell et EDR du poste"
          automatable: true
          action: logs_search
          action_target: hostname
        - id: S-ps-verif-compte
          label: "Vérifier le compte qui a lancé le script et ses privilèges"
          automatable: true
          action: account_info
          action_target: username
        - id: S-ps-isolement-poste
          label: "Isoler le poste si le script est malveillant (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
      actifs: []
    - id: P-powershell-faux-positif
      label: "Script PowerShell d'administration signalé à tort"
      symptomes:
        - "alerte PowerShell sur un script de déploiement du service IT"
        - "commande encodée détectée pendant une intervention planifiée du N2"
      causes:
        - "script légitime non signé ou lancé hors des outils habituels"
      solutions:
        - id: S-ps-qualification-faux-positif
          label: "Vérifier l'origine et la signature du script avec le SOC avant clôture"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Exécution PowerShell suspecte (T1059.001)

## Contexte
PowerShell est un outil d'administration légitime, très utilisé par les attaquants (MITRE ATT&CK T1059.001) pour télécharger et exécuter du code en mémoire sans fichier sur le disque. Sur les postes Exemplia, la journalisation des blocs de script est activée et l'EDR remonte les lignes de commande. Un utilisateur standard n'a quasiment jamais de raison de lancer PowerShell.

## Indicateurs
- Paramètres typiques : `-nop`, `-w hidden`, `-ExecutionPolicy Bypass`, `-enc` ou `-EncodedCommand` suivi d'une longue chaîne Base64.
- Fonctions de téléchargement et d'exécution : `IEX`, `Invoke-Expression`, `DownloadString`, `Invoke-WebRequest` vers une IP ou un domaine inconnu.
- Processus parent inhabituel : `winword.exe`, `excel.exe`, `outlook.exe`, `mshta.exe`, `wscript.exe`.
- Événements 4104 (bloc de script) et 4688 (création de processus) ; connexion réseau sortante juste après le lancement.

## Analyse (questions à se poser)
1. Quel est le processus parent ? Un document ou un mail vient-il d'être ouvert ?
2. Que contient la commande décodée ? (décoder la chaîne Base64 dans un environnement d'analyse, sans jamais l'exécuter)
3. Le script a-t-il contacté une adresse externe, téléchargé un fichier, créé une tâche planifiée ou une clé de démarrage ?
4. Quel compte l'a lancé ? A-t-il des privilèges élevés ? Un compte protégé est-il impliqué ?
5. Le script correspond-il à un déploiement connu du service IT (outil, signature, heure) ?

## Réponse
1. Récupérer les journaux du poste (`logs_search`, cible : nom d'hôte) : ligne de commande complète, parent, connexions réseau.
2. Vérifier le compte qui a lancé le script (`account_info`).
3. Comportement malveillant confirmé ou probable : demander l'isolement du poste (`isolate_host`, validation humaine).
4. Bloquer l'IP de téléchargement si elle est externe (`block_ip`, 1 à 24 h) et rechercher d'autres postes l'ayant contactée.
5. Demander à l'utilisateur de ne pas éteindre le poste et de ne plus ouvrir le document en cause.
6. Script légitime du service IT : documenter, puis clôturer en faux positif après accord du SOC.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Poste | 0 | Automatique (lecture seule) |
| `account_info` | Compte | 0 | Automatique (lecture seule) |
| `block_ip` | IP externe de téléchargement | 1 | Automatique si confiance ≥ 0,80, 1 à 24 h ; jamais pour une IP RFC 1918 |
| `isolate_host` | Poste | 2 | Toujours validée par un humain |
| Supprimer des fichiers ou modifier la politique d'exécution | — | 3 | Interdit à l'agent |

## Quand escalader
- Toute commande encodée lancée par une application bureautique : SOC, priorité P2 (P1 si connexion externe établie).
- Exécution sur un serveur ou sous un compte protégé (`admin`, `svc-backup`) : SOC immédiatement.
- Signes de propagation (même commande sur plusieurs postes) : SOC, priorité P1.
