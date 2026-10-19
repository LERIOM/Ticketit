---
id: KB-CY-005
title: "Fatigue MFA : bombardement de notifications Authenticator"
kind: fiche_cyber
category: bruteforce
priority_hint: P1
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [mfa, fatigue mfa, authenticator, notifications, compte compromis]
mitre: ["T1621"]
graph:
  problemes:
    - id: P-mfa-fatigue
      label: "Bombardement de notifications MFA (fatigue MFA)"
      symptomes:
        - "je reçois des dizaines de demandes Authenticator que je n'ai pas faites"
        - "mon téléphone n'arrête pas de me demander d'approuver une connexion"
        - "alerte : plus de 10 refus MFA en 15 minutes pour le même utilisateur"
      causes:
        - "mot de passe de l'utilisateur connu de l'attaquant"
        - "attaquant espérant une validation par lassitude"
      solutions:
        - id: S-mfa-fatigue-reset-mdp
          label: "Forcer la réinitialisation du mot de passe (connu de l'attaquant)"
          automatable: true
          action: force_password_reset
          action_target: username
        - id: S-mfa-fatigue-revue-connexions
          label: "Rechercher l'origine des tentatives de connexion du compte"
          automatable: true
          action: logs_search
          action_target: username
      actifs: []
    - id: P-mfa-fatigue-approuvee
      label: "Notification MFA frauduleuse approuvée par erreur"
      symptomes:
        - "j'ai validé une demande Authenticator par erreur"
        - "connexion réussie depuis l'étranger juste après une série de refus MFA"
      causes:
        - "validation par lassitude ou après un faux appel du support"
      solutions:
        - id: S-mfa-fatigue-reset-apres-approbation
          label: "Réinitialiser le mot de passe et révoquer les sessions immédiatement"
          automatable: true
          action: force_password_reset
          action_target: username
        - id: S-mfa-fatigue-desactivation
          label: "Désactiver le compte si l'attaquant a agi (validation humaine)"
          automatable: false
          action: disable_account
          action_target: username
      actifs: []
---

# Fatigue MFA : bombardement de notifications Authenticator (T1621)

## Contexte
L'attaquant connaît déjà le mot de passe (phishing, fuite, password spraying) et déclenche des demandes MFA à répétition (MITRE ATT&CK T1621, Multi-Factor Authentication Request Generation) jusqu'à ce que l'utilisateur, lassé ou trompé par un faux appel du « support », approuve. Chez Exemplia, Authenticator demande de saisir un nombre affiché à l'écran de connexion : une demande avec un nombre que l'utilisateur ne voit nulle part est forcément frauduleuse.

## Indicateurs
- L'utilisateur reçoit des notifications Authenticator alors qu'il ne se connecte pas.
- Journaux Entra ID : nombreuses connexions avec mot de passe correct puis MFA refusée ou expirée (erreur 500121), depuis une IP inconnue.
- Appel ou message d'une personne se présentant comme le support et demandant de valider une notification.
- Connexion réussie juste après une série de refus.

## Analyse (questions à se poser)
1. L'utilisateur a-t-il approuvé une des demandes ? À quelle heure ?
2. D'où viennent les tentatives (IP, pays, application cible) ?
3. Comment le mot de passe a-t-il fuité (phishing récent, réutilisation sur un site personnel) ?
4. Après une éventuelle approbation : quelles actions ont été réalisées (mails, fichiers, ajout de méthode MFA) ?

## Réponse
1. Consigne immédiate à l'utilisateur : **refuser** toutes les demandes et choisir **Je n'ai pas fait cette demande** dans Authenticator. Le support Exemplia ne demande jamais de valider une notification.
2. Forcer la réinitialisation du mot de passe (`force_password_reset`) : sans mot de passe valide, les demandes cessent.
3. Rechercher l'origine et le résultat des tentatives (`logs_search`, cible : identifiant).
4. Demande approuvée : réinitialiser immédiatement le mot de passe et révoquer les sessions ; vérifier règles de messagerie et méthodes MFA ajoutées.
5. Actions malveillantes constatées : demander la désactivation du compte (`disable_account`, validation humaine) le temps de l'analyse.
6. Rappeler à l'utilisateur les règles : ne jamais approuver une demande non initiée, signaler tout appel suspect.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Identifiant | 0 | Automatique (lecture seule) |
| `account_info` | Identifiant | 0 | Automatique (lecture seule) |
| `force_password_reset` | Identifiant | 1 | Automatique si confiance ≥ 0,80 et compte non protégé ; sinon validation humaine |
| `disable_account` | Identifiant | 2 | Toujours validée par un humain |
| Modifier la stratégie MFA ou d'accès conditionnel | — | 3 | Interdit à l'agent |

## Quand escalader
- Demande approuvée par l'utilisateur : SOC immédiatement, priorité P1.
- Compte protégé ou à privilèges visé : aucune action automatique, SOC immédiatement.
- Plusieurs utilisateurs bombardés en même temps : campagne en cours, SOC (voir aussi KB-CY-004).
