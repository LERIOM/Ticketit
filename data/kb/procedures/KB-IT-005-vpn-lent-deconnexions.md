---
id: KB-IT-005
title: "VPN lent ou déconnexions répétées"
kind: procedure
category: reseau
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [vpn, forticlient, télétravail, lenteur, déconnexion]
mitre: []
graph:
  problemes:
    - id: P-vpn-lent
      label: "VPN lent"
      symptomes:
        - "tout est très lent quand je suis connecté au VPN"
        - "les fichiers du lecteur réseau mettent des minutes à s'ouvrir en télétravail"
        - "l'ERP rame uniquement depuis la maison"
      causes:
        - "connexion Internet domestique faible ou saturée"
        - "Wi-Fi domestique de mauvaise qualité"
        - "ouverture de gros fichiers directement sur les lecteurs réseau à travers le VPN"
      solutions:
        - id: S-vpn-optimisation-connexion
          label: "Mesurer le débit et privilégier une connexion filaire ou proche de la box"
          automatable: true
          action: null
          action_target: null
        - id: S-vpn-usage-onedrive
          label: "Travailler les gros fichiers depuis OneDrive ou SharePoint plutôt que via le VPN"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-vpn-deconnexions
      label: "Déconnexions VPN répétées"
      symptomes:
        - "le VPN se coupe toutes les 10 minutes"
        - "message : la connexion VPN a été interrompue"
        - "je perds le VPN dès que mon PC se met en veille"
      causes:
        - "mise en veille de la carte réseau par la gestion d'alimentation Windows"
        - "box ou partage de connexion 4G instable"
        - "version obsolète de FortiClient"
      solutions:
        - id: S-vpn-gestion-alimentation
          label: "Désactiver l'économie d'énergie de la carte réseau et mettre à jour FortiClient"
          automatable: true
          action: null
          action_target: null
        - id: S-vpn-journaux-passerelle
          label: "Rechercher les déconnexions du compte dans les journaux de la passerelle VPN"
          automatable: true
          action: logs_search
          action_target: username
      actifs: []
---

# VPN lent ou déconnexions répétées

## Contexte
Le VPN Exemplia fait transiter le trafic vers le réseau interne. Sa vitesse dépend d'abord de la connexion Internet de l'utilisateur. Microsoft 365 (Teams, Outlook, OneDrive) sort directement sur Internet et ne passe pas par le tunnel ; seuls les lecteurs réseau, l'ERP et les applications internes l'utilisent.

## Étapes
### Lenteurs
1. Déconnecter le VPN et mesurer le débit sur `https://www.speedtest.net` : en dessous de 5 Mbit/s en envoi ou au-dessus de 80 ms de latence, la cause est la connexion domestique.
2. Se rapprocher de la box, passer en câble Ethernet ou en Wi-Fi 5 GHz ; suspendre les usages lourds du foyer (streaming, téléchargements).
3. Éviter d'ouvrir directement des fichiers volumineux sur `S:` à travers le VPN : les copier en local ou utiliser l'espace OneDrive / SharePoint du service.
4. Fermer les synchronisations inutiles et redémarrer le poste s'il n'a pas été redémarré depuis plusieurs jours.

### Déconnexions
1. **Gestionnaire de périphériques** (clic droit sur **Démarrer**) > **Cartes réseau** > carte Wi-Fi > **Propriétés** > onglet **Gestion de l'alimentation** : décocher **Autoriser l'ordinateur à éteindre ce périphérique pour économiser l'énergie**.
2. **Paramètres** > **Système** > **Alimentation** : régler la mise en veille sur secteur à 30 minutes minimum.
3. Vérifier la version de FortiClient (**À propos**) et la mettre à jour depuis le **Portail d'entreprise** si une version plus récente est proposée.
4. Noter l'heure exacte des coupures et tester une journée en partage de connexion 4G/5G pour isoler la box.
5. Côté service desk, consulter les journaux de la passerelle pour le compte (motif de fin de session : délai d'inactivité, perte de paquets, réauthentification).

## Vérification
- Le VPN reste connecté au moins une heure sans coupure.
- L'ouverture d'un fichier de 10 Mo sur `S:` prend moins de 15 secondes.

## Quand escalader
- Coupures qui touchent plusieurs utilisateurs à la même heure : N2 Réseau (incident passerelle), priorité P2.
- Débit domestique correct mais VPN lent de façon persistante : N2 Réseau avec les mesures de débit et les heures.
- Déconnexions liées à une réauthentification inattendue ou à des connexions inconnues : SOC (KB-CY-009).
