---
id: KB-IT-001
title: "Mot de passe expiré ou oublié"
kind: procedure
category: mot_de_passe
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [mot de passe, active directory, self-service, expiration]
mitre: []
graph:
  problemes:
    - id: P-mdp-expire
      label: "Mot de passe expiré ou oublié"
      symptomes:
        - "impossible d'ouvrir ma session Windows, mot de passe refusé"
        - "message : votre mot de passe a expiré et doit être changé"
        - "j'ai oublié mon mot de passe"
        - "Outlook et Teams me redemandent sans arrêt mon mot de passe"
      causes:
        - "expiration automatique du mot de passe après 90 jours"
        - "oubli du mot de passe après une absence prolongée"
      solutions:
        - id: S-mdp-selfservice
          label: "Réinitialiser le mot de passe via le portail self-service"
          automatable: true
          action: null
          action_target: null
        - id: S-mdp-reset-servicedesk
          label: "Réinitialisation par le service desk après vérification d'identité"
          automatable: false
          action: force_password_reset
          action_target: username
      actifs: []
    - id: P-mdp-ancien-memorise
      label: "Ancien mot de passe encore mémorisé sur d'autres appareils"
      symptomes:
        - "depuis que j'ai changé mon mot de passe mon téléphone ne reçoit plus les mails"
        - "le Wi-Fi ou le VPN refuse mon nouveau mot de passe"
      causes:
        - "ancien mot de passe enregistré sur le smartphone, le VPN ou le Wi-Fi"
      solutions:
        - id: S-mdp-maj-appareils
          label: "Mettre à jour le mot de passe sur tous les appareils et applications"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Mot de passe expiré ou oublié

## Contexte
Les mots de passe des comptes `exemplia.local` expirent tous les 90 jours ; un rappel s'affiche 14 jours avant l'échéance. La politique impose 12 caractères minimum, trois types de caractères (majuscules, minuscules, chiffres, symboles) et interdit les 10 derniers mots de passe. Chaque salarié peut réinitialiser son mot de passe lui-même sur le portail self-service, à condition d'avoir enregistré Microsoft Authenticator.

## Étapes
1. Depuis un poste du réseau interne, un smartphone ou le poste d'un collègue, ouvrir `https://motdepasse.exemplia.local`.
   - Depuis l'écran de connexion Windows 11, le lien **Réinitialiser le mot de passe** mène au même service.
2. Saisir l'identifiant au format `prenom.nom@exemplia.local` puis approuver la notification Microsoft Authenticator.
3. Choisir **Mot de passe oublié** (ou **Changer mon mot de passe** si l'ancien est connu) et saisir deux fois le nouveau mot de passe.
4. Poste hors des locaux : se connecter d'abord au VPN Exemplia avec le nouveau mot de passe, puis verrouiller la session (`Windows + L`) et la déverrouiller avec ce même mot de passe pour mettre à jour le cache local.
5. Mettre à jour le mot de passe partout où l'ancien est enregistré (section suivante).

### Ancien mot de passe resté en mémoire
1. Smartphone : application Outlook > **Paramètres** > compte Exemplia > **Réinitialiser le compte**, puis saisir le nouveau mot de passe.
2. Wi-Fi : **Paramètres** > **Réseau et Internet** > **Wi-Fi** > **Gérer les réseaux connus** > `EXEMPLIA` > **Oublier**, puis se reconnecter.
3. Windows : **Panneau de configuration** > **Gestionnaire d'identification** > **Informations d'identification Windows** : supprimer les entrées contenant `exemplia.local`.
4. Éteindre les appareils non mis à jour pour éviter un verrouillage du compte (voir KB-IT-002).

## Vérification
- L'utilisateur ouvre sa session Windows, Outlook et Teams sans nouvelle demande de mot de passe.
- Le portail self-service affiche une date d'expiration repoussée de 90 jours.

## Quand escalader
- Méthode MFA indisponible (téléphone perdu ou changé) : le self-service est impossible, suivre KB-IT-003.
- Le portail affiche « compte non éligible » ou une erreur : escalader à l'équipe IAM (N2) via `https://support.exemplia.local`.
- Réinitialisation par le service desk : uniquement après vérification d'identité (rappel sur le numéro professionnel de l'annuaire ou validation du manager). Ne jamais transmettre un mot de passe par e-mail ou par Teams.
- L'utilisateur a saisi son mot de passe sur un site suspect : traiter comme un incident de sécurité (KB-CY-003).
