---
id: KB-IT-020
title: "Nouvel arrivant : création de compte et première connexion"
kind: procedure
category: acces_compte
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [nouvel arrivant, onboarding, création de compte, rh, première connexion]
mitre: []
graph:
  problemes:
    - id: P-nouvel-arrivant-compte
      label: "Création de compte pour un nouvel arrivant"
      symptomes:
        - "un nouveau collaborateur arrive lundi et n'a pas de compte"
        - "pouvez-vous créer un compte pour mon stagiaire"
        - "le nouvel arrivant n'a ni ordinateur ni adresse e-mail"
      causes:
        - "dossier d'embauche non finalisé dans le SIRH"
        - "arrivée non transmise par les RH à la DSI"
      solutions:
        - id: S-arrivant-escalade-rh
          label: "Escalader aux RH : la création de compte est déclenchée uniquement par le SIRH"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-arrivant-premiere-connexion
      label: "Première connexion d'un nouvel arrivant"
      symptomes:
        - "première connexion : on me demande de changer mon mot de passe"
        - "comment configurer Authenticator le premier jour"
      causes:
        - "mot de passe temporaire à changer à la première connexion"
        - "inscription MFA pas encore réalisée"
      solutions:
        - id: S-arrivant-premiere-connexion
          label: "Guider la première connexion : mot de passe, MFA, Outlook et Teams"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Nouvel arrivant : création de compte et première connexion

## Contexte
Chez Exemplia, les comptes sont créés automatiquement à partir du SIRH : quand les RH valident le dossier d'embauche (contrat, date d'arrivée, service, manager), le compte `exemplia.local`, la boîte Microsoft 365 et la commande du poste sont déclenchés. Le service desk ne crée **jamais** un compte sur simple demande d'un manager ou d'un collègue : c'est une mesure de sécurité contre les comptes fantômes.

## Étapes
### Demande de création de compte
1. Remercier le demandeur et expliquer que la création dépend du dossier RH.
2. Vérifier dans le portail ITSM si une demande d'arrivée existe déjà pour cette date (recherche par service et date d'arrivée).
3. Si aucune demande n'existe : escalader le ticket à la file **RH - Gestion administrative** sur `https://support.exemplia.local` en indiquant le service, le manager et la date d'arrivée prévue.
4. Indiquer au manager les délais : 5 jours ouvrés entre la validation RH et la remise du poste.
5. Pour les stagiaires, alternants et prestataires : même circuit, avec date de fin de contrat obligatoire (le compte expire automatiquement).

### Première connexion (le jour d'arrivée)
1. Le manager remet le poste et l'enveloppe contenant l'identifiant et le mot de passe temporaire.
2. Ouvrir la session Windows avec `prenom.nom` et le mot de passe temporaire, puis choisir un nouveau mot de passe (12 caractères minimum, voir KB-IT-001).
3. Installer Microsoft Authenticator sur le téléphone et suivre l'assistant **Informations de sécurité** affiché à la première connexion à Microsoft 365 (voir KB-IT-003).
4. Ouvrir Outlook et Teams : la configuration est automatique avec le compte Exemplia.
5. Ouvrir le **Portail d'entreprise** pour installer les logiciels du service (KB-IT-012).
6. Demander les accès spécifiques (dossiers partagés, ERP) via le portail ITSM avec validation du manager (KB-IT-014, KB-IT-019).

## Vérification
- L'utilisateur ouvre sa session, reçoit un e-mail de test et rejoint une réunion Teams.
- Microsoft Authenticator est enregistré comme méthode par défaut.

## Quand escalader
- Toute demande de création de compte sans dossier RH : escalade RH, aucune création par le service desk.
- Compte créé mais poste non livré le jour d'arrivée : N2 Poste de travail pour un poste de prêt.
- Mot de passe temporaire perdu ou enveloppe ouverte : réinitialisation par le service desk après vérification d'identité auprès du manager.
