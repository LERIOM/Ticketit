---
id: KB-IT-006
title: "Wi-Fi d'entreprise : connexion impossible ou accès invité"
kind: procedure
category: reseau
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [wi-fi, 802.1X, certificat, réseau invité]
mitre: []
graph:
  problemes:
    - id: P-wifi-corp-connexion
      label: "Connexion impossible au Wi-Fi d'entreprise EXEMPLIA"
      symptomes:
        - "mon portable ne se connecte plus au Wi-Fi EXEMPLIA"
        - "Wi-Fi : impossible de se connecter à ce réseau"
        - "je suis connecté au Wi-Fi mais je n'ai pas Internet"
      causes:
        - "certificat machine expiré ou absent"
        - "profil Wi-Fi corrompu"
        - "appareil personnel ou poste non géré par Exemplia"
      solutions:
        - id: S-wifi-oublier-reseau
          label: "Oublier le réseau, se reconnecter et renouveler l'adresse IP"
          automatable: true
          action: null
          action_target: null
        - id: S-wifi-renouveler-certificat
          label: "Renouveler le certificat machine en câble ou via le VPN (gpupdate)"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-wifi-invite
      label: "Accès Wi-Fi pour un visiteur ou un appareil personnel"
      symptomes:
        - "comment connecter un visiteur au Wi-Fi"
        - "mon téléphone personnel n'arrive pas à se connecter au Wi-Fi d'entreprise"
      causes:
        - "le réseau EXEMPLIA est réservé aux postes gérés par Exemplia"
      solutions:
        - id: S-wifi-portail-invites
          label: "Utiliser le réseau EXEMPLIA-INVITES avec un code délivré à l'accueil"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Wi-Fi d'entreprise : connexion impossible ou accès invité

## Contexte
Deux réseaux Wi-Fi sont diffusés dans les locaux :
- `EXEMPLIA` : réservé aux postes Windows 11 gérés par Exemplia, authentification 802.1X par certificat machine (EAP-TLS), accès complet au réseau interne.
- `EXEMPLIA-INVITES` : visiteurs et appareils personnels, accès Internet uniquement, code valable 24 h délivré par l'accueil.

## Étapes
### Poste Exemplia sur le réseau EXEMPLIA
1. Vérifier que le Wi-Fi est activé (`Windows + A`) et que le mode Avion est désactivé.
2. **Paramètres** > **Réseau et Internet** > **Wi-Fi** > **Gérer les réseaux connus** > `EXEMPLIA` > **Oublier**, puis se reconnecter.
3. Dans un terminal, afficher l'état et renouveler l'adresse :
   ```cmd
   netsh wlan show interfaces
   ipconfig /release
   ipconfig /renew
   ipconfig /flushdns
   ```
4. Une adresse en `169.254.x.x` indique un échec d'obtention d'adresse : rapprocher le poste d'une borne et retenter.
5. Vérifier le certificat machine : `certlm.msc` > **Personnel** > **Certificats** ; un certificat émis par l'autorité interne Exemplia doit être valide.
6. Certificat absent ou expiré : brancher le poste en câble (ou se connecter au VPN Exemplia), exécuter `gpupdate /force`, redémarrer, puis retenter le Wi-Fi.

### Visiteur ou appareil personnel
1. Se connecter au réseau `EXEMPLIA-INVITES`.
2. Le portail d'accueil s'ouvre : saisir le code remis par l'accueil et accepter la charte.
3. Les appareils personnels ne doivent jamais être connectés au réseau `EXEMPLIA` ni au réseau filaire.

## Vérification
- `netsh wlan show interfaces` affiche **État : connecté** sur le SSID attendu.
- Le poste accède à `https://support.exemplia.local` (réseau EXEMPLIA) ou à Internet (réseau invités).

## Quand escalader
- Aucun appareil ne capte le Wi-Fi dans une zone ou un étage entier : borne en panne, N2 Réseau en P2.
- Certificat machine toujours absent après `gpupdate /force` : N2 Poste de travail (réinscription du poste).
- Réseau Wi-Fi inconnu au nom proche d'EXEMPLIA détecté dans les locaux : possible borne pirate, prévenir le SOC.
