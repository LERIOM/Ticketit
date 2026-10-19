---
id: KB-IT-003
title: "MFA : nouveau téléphone, téléphone perdu ou réinscription"
kind: procedure
category: acces_compte
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [mfa, microsoft authenticator, téléphone, entra id]
mitre: []
graph:
  problemes:
    - id: P-mfa-nouveau-telephone
      label: "Changement de téléphone : Microsoft Authenticator à transférer"
      symptomes:
        - "j'ai changé de téléphone et je ne reçois plus les notifications Authenticator"
        - "mon compte Exemplia n'apparaît plus dans Authenticator"
        - "on me demande d'approuver la connexion mais je n'ai plus l'ancien téléphone"
      causes:
        - "Authenticator non transféré sur le nouveau téléphone"
        - "application réinstallée sans sauvegarde des comptes"
      solutions:
        - id: S-mfa-ajout-autonome
          label: "Ajouter le nouveau téléphone depuis la page Informations de sécurité"
          automatable: true
          action: null
          action_target: null
        - id: S-mfa-reinitialisation-methodes
          label: "Réinitialiser les méthodes MFA après vérification d'identité (équipe IAM)"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-mfa-telephone-perdu
      label: "Téléphone portant l'application MFA perdu ou volé"
      symptomes:
        - "j'ai perdu mon téléphone avec Authenticator"
        - "téléphone volé, je ne peux plus valider mes connexions"
      causes:
        - "perte ou vol du smartphone"
      solutions:
        - id: S-mfa-perte-revocation
          label: "Supprimer l'ancien appareil, révoquer les sessions puis réinscrire la MFA"
          automatable: false
          action: null
          action_target: null
        - id: S-mfa-perte-verif-connexions
          label: "Vérifier l'absence de connexions suspectes sur le compte"
          automatable: true
          action: logs_search
          action_target: username
      actifs: []
---

# MFA : nouveau téléphone, téléphone perdu ou réinscription

## Contexte
L'authentification multifacteur (MFA) d'Exemplia repose sur Microsoft Authenticator (notification avec saisie d'un nombre). Elle protège Microsoft 365, le VPN Exemplia et le portail self-service. Sans MFA fonctionnelle, l'utilisateur ne peut ni se connecter à distance ni réinitialiser son mot de passe seul.

## Étapes
### Cas 1 : nouveau téléphone, ancien téléphone encore disponible
1. Installer **Microsoft Authenticator** sur le nouveau téléphone (App Store ou Google Play).
2. Sur un PC, ouvrir `https://mysignins.microsoft.com/security-info` et se connecter avec le compte Exemplia (validation sur l'ancien téléphone).
3. Cliquer sur **Ajouter une méthode de connexion** > **Application Authenticator** > **Suivant**, puis scanner le QR code avec le nouveau téléphone.
4. Valider la notification de test, puis définir le nouveau téléphone comme **méthode par défaut**.
5. Supprimer l'ancien téléphone de la liste (**Supprimer** à droite de l'appareil).

### Cas 2 : ancien téléphone indisponible (réinitialisé, cassé)
1. Ouvrir un ticket sur `https://support.exemplia.local` (catégorie **Accès > MFA**) depuis le poste d'un collègue ou en appelant le service desk.
2. Le service desk vérifie l'identité (présentation du badge en visioconférence ou au guichet IT, validation du manager).
3. L'équipe IAM supprime les méthodes enregistrées et délivre un **Temporary Access Pass** valable 1 heure.
4. L'utilisateur suit alors les étapes 2 à 4 du cas 1 en se connectant avec ce code temporaire.

### Cas 3 : téléphone perdu ou volé
1. Traiter en priorité P2 : un téléphone volé donne accès aux notifications MFA.
2. Rechercher les connexions récentes du compte (IP, pays, applications) pour détecter un usage anormal.
3. L'équipe IAM supprime l'appareil, révoque les sessions actives, puis suit le cas 2 pour la réinscription.
4. Si le téléphone était professionnel : déclarer la perte au service Moyens généraux pour blocage de la ligne.

## Vérification
- Une connexion à `https://outlook.office.com` déclenche bien la notification sur le nouveau téléphone.
- La page **Informations de sécurité** n'affiche plus l'ancien appareil.

## Quand escalader
- Toute réinitialisation des méthodes MFA : équipe IAM (N2), jamais sans vérification d'identité.
- Connexions suspectes constatées sur le compte : SOC (voir KB-CY-009).
- L'utilisateur reçoit des demandes MFA qu'il n'a pas initiées : traiter comme une fatigue MFA (KB-CY-005).
