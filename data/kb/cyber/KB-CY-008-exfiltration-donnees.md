---
id: KB-CY-008
title: "Exfiltration de données"
kind: fiche_cyber
category: fuite_donnees
priority_hint: P1
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [exfiltration, fuite de données, dns, ftp, rgpd]
mitre: ["T1048"]
graph:
  problemes:
    - id: P-exfiltration-reseau
      label: "Exfiltration de données par un protocole inhabituel"
      symptomes:
        - "alerte : 12 Go envoyés depuis SRV-FILE-01 vers une IP externe inconnue"
        - "volume anormal de requêtes DNS très longues depuis un poste"
        - "transfert FTP sortant en pleine nuit vers un hébergeur inconnu"
      causes:
        - "attaquant exfiltrant des données après une compromission"
        - "outil de transfert ou de synchronisation non autorisé"
      solutions:
        - id: S-exfil-analyse-flux
          label: "Analyser les flux sortants de la machine source (volume, destination, protocole)"
          automatable: true
          action: logs_search
          action_target: hostname
        - id: S-exfil-blocage-destination
          label: "Bloquer temporairement l'IP externe de destination (1 à 24 h)"
          automatable: true
          action: block_ip
          action_target: ip
        - id: S-exfil-isolement-source
          label: "Isoler la machine source (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
      actifs: ["SRV-FILE-01"]
    - id: P-exfiltration-compte
      label: "Compte utilisé pour extraire des données en masse"
      symptomes:
        - "un utilisateur a téléchargé des milliers de fichiers en une heure"
        - "accès massif aux dossiers RH par un compte qui n'y va jamais"
      causes:
        - "compte compromis utilisé par un attaquant"
        - "action malveillante d'un salarié, par exemple avant son départ"
      solutions:
        - id: S-exfil-verif-compte
          label: "Vérifier le compte, ses groupes et ses connexions récentes"
          automatable: true
          action: account_info
          action_target: username
        - id: S-exfil-desactivation-compte
          label: "Désactiver le compte (validation humaine)"
          automatable: false
          action: disable_account
          action_target: username
      actifs: ["SRV-FILE-01"]
---

# Exfiltration de données (T1048)

## Contexte
L'exfiltration par un protocole alternatif (MITRE ATT&CK T1048) consiste à sortir des données par un canal autre que le canal de commande habituel : FTP, SFTP, DNS, HTTPS vers un hébergeur inconnu. Elle précède souvent un rançongiciel (double extorsion). `SRV-FILE-01` concentre les données métier ; seul le compte de service `svc-backup` y réalise des transferts volumineux légitimes, vers la destination de sauvegarde connue du SOC.

## Indicateurs
- Volume sortant inhabituel (plusieurs Go) depuis un poste ou depuis `SRV-FILE-01`, souvent la nuit ou le week-end.
- Destination inconnue : IP d'hébergeur, service de partage de fichiers non autorisé, port 21, 22 ou 53 vers Internet.
- Requêtes DNS très longues ou très nombreuses vers un même domaine (tunnel DNS).
- Création d'archives volumineuses (`.zip`, `.7z`, `.rar`) juste avant le transfert ; accès massif à des dossiers sensibles.

## Analyse (questions à se poser)
1. Quelle machine, quel compte, quel processus est à l'origine du flux ?
2. La destination est-elle connue et légitime (sauvegarde `svc-backup`, prestataire, cloud Microsoft 365) ?
3. Quel volume est sorti, depuis quand, et le transfert est-il toujours en cours ?
4. Quelles données sont concernées (personnelles, RH, financières, clients) ?
5. Y a-t-il d'autres signes de compromission (phishing, PowerShell, connexion anormale) ?

## Réponse
1. Analyser les flux de la machine source (`logs_search`) : destination, protocole, volume, processus.
2. Vérifier le compte à l'origine des accès (`account_info`) ; ne jamais agir automatiquement sur `svc-backup`.
3. Destination externe non légitime : bloquer l'IP 1 à 24 heures (`block_ip`) pour arrêter le transfert.
4. Demander l'isolement de la machine source (`isolate_host`, validation humaine) ; pour `SRV-FILE-01`, la décision revient au RSSI (impact métier).
5. Compte compromis ou malveillant : demander la désactivation du compte (`disable_account`, validation humaine).
6. Conserver les journaux et informer le DPO pour évaluer la notification CNIL (72 heures) et l'information des personnes.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Machine source | 0 | Automatique (lecture seule) |
| `account_info` | Compte | 0 | Automatique (lecture seule) |
| `block_ip` | IP externe de destination | 1 | Automatique si confiance ≥ 0,80, 1 à 24 h ; jamais pour une IP RFC 1918 |
| `isolate_host` | Poste ou serveur source | 2 | Toujours validée par un humain |
| `disable_account` | Compte | 2 | Toujours validée par un humain ; jamais sur `svc-backup` ou `admin` |
| Supprimer des données ou modifier la politique du pare-feu | — | 3 | Interdit à l'agent |

## Quand escalader
- Toute exfiltration confirmée ou probable : SOC et RSSI, priorité P1.
- Données personnelles concernées : DPO immédiatement (délai CNIL de 72 heures).
- Salarié soupçonné : RSSI, RH et juridique ; aucune action visible vers le salarié avant leur décision.
