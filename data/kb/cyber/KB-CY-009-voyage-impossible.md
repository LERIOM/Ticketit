---
id: KB-CY-009
title: "Connexion impossible (voyage impossible) sur un compte"
kind: fiche_cyber
category: acces_compte
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [voyage impossible, connexion anormale, entra id, compte compromis, géolocalisation]
mitre: ["T1078"]
graph:
  problemes:
    - id: P-voyage-impossible
      label: "Connexion impossible (voyage impossible) sur un compte utilisateur"
      symptomes:
        - "alerte Entra ID : voyage impossible pour un utilisateur"
        - "connexion depuis Nantes puis 30 minutes plus tard depuis un autre continent"
        - "connexion réussie depuis un pays où Exemplia n'a aucune activité"
      causes:
        - "identifiants volés et réutilisés par un attaquant"
        - "VPN personnel ou proxy qui fausse la localisation"
      solutions:
        - id: S-voyage-analyse-connexions
          label: "Analyser les connexions du compte (IP, pays, appareil, application)"
          automatable: true
          action: logs_search
          action_target: username
        - id: S-voyage-reset-mdp
          label: "Forcer la réinitialisation du mot de passe et révoquer les sessions"
          automatable: true
          action: force_password_reset
          action_target: username
        - id: S-voyage-desactivation-compte
          label: "Désactiver le compte si une activité malveillante est constatée (validation humaine)"
          automatable: false
          action: disable_account
          action_target: username
      actifs: []
    - id: P-voyage-compte-protege
      label: "Connexion anormale sur un compte protégé"
      symptomes:
        - "connexion du compte svc-backup depuis une IP externe"
        - "le compte admin s'est connecté depuis un pays inhabituel"
      causes:
        - "vol d'identifiants d'un compte à privilèges"
      solutions:
        - id: S-protege-infos-compte
          label: "Collecter les informations du compte protégé (lecture seule)"
          automatable: true
          action: account_info
          action_target: username
        - id: S-protege-escalade-soc
          label: "Escalade immédiate au SOC et au RSSI, aucune action automatique"
          automatable: false
          action: null
          action_target: null
      actifs: ["DC-01"]
---

# Connexion impossible (voyage impossible) sur un compte (T1078)

## Contexte
Un « voyage impossible » est détecté quand un même compte se connecte depuis deux lieux trop éloignés pour le temps écoulé entre les connexions. C'est un indicateur classique d'utilisation d'identifiants valides par un attaquant (MITRE ATT&CK T1078, Valid Accounts). Les faux positifs existent (VPN personnel, relais mobile, sortie Internet d'un partenaire) : l'analyse prime sur la réaction.

## Indicateurs
- Alerte Entra ID Protection « voyage atypique » ou « voyage impossible ».
- Deux connexions réussies depuis des pays différents à moins de quelques heures d'intervalle.
- Connexion depuis un hébergeur, un nœud Tor ou un fournisseur de VPN anonyme.
- Appareil ou navigateur jamais vu pour ce compte ; application inhabituelle (accès IMAP, PowerShell, API).

## Analyse (questions à se poser)
1. L'utilisateur est-il en déplacement ou utilise-t-il un VPN personnel ? (le contacter par téléphone, pas par mail)
2. La MFA a-t-elle été validée pour la connexion suspecte ? Par quelle méthode ?
3. Qu'a fait la session suspecte : lecture de mails, règles de transfert, téléchargement de fichiers ?
4. Le compte est-il protégé (`admin`, `svc-backup`) ou à privilèges ?
5. D'autres comptes se connectent-ils depuis la même IP ?

## Réponse
1. Analyser les connexions du compte (`logs_search`, cible : identifiant) sur les 7 derniers jours.
2. Contacter l'utilisateur sur un canal sûr (téléphone de l'annuaire) pour confirmer ou infirmer la connexion.
3. Connexion non reconnue : forcer la réinitialisation du mot de passe (`force_password_reset`), ce qui révoque les sessions.
4. Activité malveillante constatée : demander la désactivation du compte (`disable_account`, validation humaine) et suivre KB-CY-003 pour le nettoyage de la messagerie.
5. Compte protégé : collecter les informations (`account_info`) et escalader immédiatement ; aucune action automatique.
6. Connexion légitime (déplacement confirmé) : documenter et clôturer en faux positif.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Identifiant | 0 | Automatique (lecture seule) |
| `account_info` | Identifiant | 0 | Automatique (lecture seule) |
| `force_password_reset` | Identifiant | 1 | Automatique si confiance ≥ 0,80 et compte non protégé ; sinon validation humaine |
| `block_ip` | IP externe suspecte | 1 | Automatique si confiance ≥ 0,80, 1 à 24 h ; jamais pour une IP RFC 1918 |
| `disable_account` | Identifiant | 2 | Toujours validée par un humain |
| Modifier les stratégies d'accès conditionnel | — | 3 | Interdit à l'agent |

## Quand escalader
- Compte protégé ou à privilèges concerné : SOC et RSSI immédiatement, priorité P1.
- Activité malveillante confirmée (mails envoyés, données téléchargées) : SOC, priorité P1.
- Utilisateur injoignable et connexion toujours active depuis l'étranger : SOC pour décision de désactivation.
