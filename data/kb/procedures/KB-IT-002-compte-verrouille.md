---
id: KB-IT-002
title: "Compte Active Directory verrouillé"
kind: procedure
category: acces_compte
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [compte verrouillé, active directory, déverrouillage, self-service]
mitre: []
graph:
  problemes:
    - id: P-compte-verrouille
      label: "Compte Active Directory verrouillé"
      symptomes:
        - "le compte référencé est verrouillé et ne peut pas être utilisé"
        - "impossible de me connecter, mon compte est bloqué"
        - "message : votre compte a été verrouillé, contactez votre administrateur"
      causes:
        - "5 tentatives de mot de passe erronées en moins de 15 minutes"
        - "ancien mot de passe enregistré sur un appareil qui retente la connexion"
      solutions:
        - id: S-verrou-deverrouillage-selfservice
          label: "Attendre le déverrouillage automatique ou déverrouiller via le portail self-service"
          automatable: true
          action: null
          action_target: null
        - id: S-verrou-etat-compte
          label: "Vérifier l'état du compte (verrouillage, dernier échec, expiration)"
          automatable: true
          action: account_info
          action_target: username
      actifs: []
    - id: P-verrouillage-repete
      label: "Verrouillages répétés du même compte"
      symptomes:
        - "mon compte se verrouille plusieurs fois par jour"
        - "déverrouillé ce matin et de nouveau bloqué une heure après"
      causes:
        - "session ou lecteur réseau ouvert avec l'ancien mot de passe sur un autre poste"
        - "smartphone ou client VPN configuré avec l'ancien mot de passe"
        - "tentatives de connexion malveillantes sur le compte"
      solutions:
        - id: S-verrou-source-logs
          label: "Identifier la source des échecs (événement 4740 sur DC-01)"
          automatable: true
          action: logs_search
          action_target: username
      actifs: ["DC-01"]
---

# Compte Active Directory verrouillé

## Contexte
La stratégie de domaine `exemplia.local` verrouille un compte après 5 mots de passe erronés en 15 minutes. Le déverrouillage est automatique au bout de 30 minutes. Un verrouillage isolé est presque toujours une erreur de saisie ; des verrouillages répétés signalent un appareil qui utilise un ancien mot de passe, voire une attaque.

## Étapes
1. Demander à l'utilisateur s'il a changé son mot de passe récemment et sur quels appareils il est connecté (PC, smartphone, tablette, second poste).
2. Proposer le déverrouillage en autonomie : `https://motdepasse.exemplia.local` > **Déverrouiller mon compte**, validation par Microsoft Authenticator. Sinon, patienter 30 minutes.
3. Si l'utilisateur ne connaît plus son mot de passe : suivre KB-IT-001.
4. Côté service desk, vérifier l'état du compte :
   ```powershell
   Get-ADUser -Identity <identifiant> -Properties LockedOut,BadLogonCount,LastBadPasswordAttempt,PasswordLastSet
   ```
5. Après vérification d'identité, déverrouiller si nécessaire : `Unlock-ADAccount -Identity <identifiant>`.

### Verrouillages répétés
1. Rechercher l'événement 4740 dans le journal Sécurité de `DC-01` (lecture seule) ; le champ **Nom de l'ordinateur appelant** indique l'appareil à l'origine des échecs.
2. Si c'est un poste ou un appareil de l'utilisateur : mettre à jour ou supprimer le mot de passe mémorisé (KB-IT-001, section « Ancien mot de passe resté en mémoire »).
3. Supprimer les lecteurs réseau mappés avec d'anciennes informations : `net use * /delete` puis fermer et rouvrir la session.
4. Si la source est inconnue, externe (Exchange Online, VPN) ou concerne plusieurs comptes : ne pas déverrouiller en boucle, escalader.

## Vérification
- `LockedOut` vaut `False` et `BadLogonCount` revient à 0 après une connexion réussie.
- Aucun nouvel événement 4740 pour ce compte dans l'heure qui suit.

## Quand escalader
- Plusieurs comptes verrouillés au même moment ou échecs provenant d'IP externes : possible password spraying, escalade au SOC (KB-CY-004).
- Compte protégé (`admin`, `svc-backup`) verrouillé : aucune manipulation par le N1, escalade immédiate au SOC.
- Source introuvable après analyse de l'événement 4740 : équipe IAM (N2).
