---
id: KB-CY-003
title: "Phishing avec saisie d'identifiants"
kind: fiche_cyber
category: phishing
priority_hint: P1
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [phishing, hameçonnage, identifiants, microsoft 365, compte compromis]
mitre: ["T1566.002", "T1078"]
graph:
  problemes:
    - id: P-phishing-identifiants-saisis
      label: "Identifiants saisis sur une page de phishing"
      symptomes:
        - "j'ai cliqué sur un lien dans un mail et saisi mon mot de passe Microsoft"
        - "mail urgent de facture impayée avec un lien vers une page de connexion Office 365"
        - "après avoir entré mon mot de passe la page m'a renvoyé vers une erreur"
        - "alerte : connexion réussie depuis une IP inconnue juste après un clic sur un lien"
      causes:
        - "e-mail d'hameçonnage contenant un lien vers une fausse page de connexion"
        - "adresse du site non vérifiée avant la saisie du mot de passe"
      solutions:
        - id: S-phishing-reset-mdp
          label: "Forcer la réinitialisation du mot de passe du compte exposé"
          automatable: true
          action: force_password_reset
          action_target: username
        - id: S-phishing-revue-connexions
          label: "Rechercher les connexions et règles de messagerie suspectes du compte"
          automatable: true
          action: logs_search
          action_target: username
      actifs: []
    - id: P-phishing-fichier-execute
      label: "Fichier exécuté depuis un e-mail de phishing"
      symptomes:
        - "j'ai ouvert la pièce jointe et activé les macros"
        - "un fichier téléchargé depuis le lien s'est lancé sur mon poste"
      causes:
        - "pièce jointe piégée ou fichier malveillant téléchargé"
      solutions:
        - id: S-phishing-isolement-poste
          label: "Isoler le poste qui a exécuté le fichier (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
        - id: S-phishing-analyse-poste
          label: "Rechercher les processus et connexions lancés depuis le poste"
          automatable: true
          action: logs_search
          action_target: hostname
      actifs: []
    - id: P-phishing-signalement
      label: "Mail suspect reçu sans clic"
      symptomes:
        - "j'ai reçu un mail bizarre qui me demande mes identifiants"
        - "est-ce que ce mail est un phishing"
      causes:
        - "campagne d'hameçonnage ciblant les salariés"
      solutions:
        - id: S-phishing-bouton-signaler
          label: "Signaler le mail avec le bouton Signaler d'Outlook sans cliquer sur les liens"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Phishing avec saisie d'identifiants (T1566.002 + T1078)

## Contexte
L'attaquant envoie un lien (MITRE ATT&CK T1566.002, Spearphishing Link) vers une fausse page de connexion Microsoft 365, puis réutilise les identifiants volés (T1078, Valid Accounts) pour lire la messagerie, créer des règles de transfert ou rebondir vers d'autres victimes. Chaque minute compte : le traitement est P1 dès que l'utilisateur a saisi son mot de passe.

## Indicateurs
- L'utilisateur signale avoir saisi ses identifiants après un clic (souvent un « document partagé », une « facture » ou une « boîte pleine »).
- Domaine du lien différent de `microsoft.com` ou `office.com`, ou nom ressemblant à Exemplia avec une lettre changée.
- Journaux de connexion Entra ID : connexion réussie depuis une IP ou un pays inhabituel peu après le clic.
- Nouvelle règle de boîte de réception (transfert externe, suppression automatique) ou nouvelle méthode MFA ajoutée.

## Analyse (questions à se poser)
1. L'utilisateur a-t-il saisi son mot de passe ? Validé une demande MFA ? Téléchargé ou ouvert un fichier ?
2. Y a-t-il des connexions réussies depuis une IP inconnue depuis le clic ?
3. Des règles de messagerie, des méthodes MFA ou des consentements d'application ont-ils été ajoutés ?
4. Combien d'autres salariés ont reçu le même mail ? D'autres ont-ils cliqué ?
5. Le compte est-il protégé (`admin`, `svc-backup`) ou à privilèges ?

## Réponse
1. Forcer la réinitialisation du mot de passe (`force_password_reset`, cible : identifiant) ; elle révoque les sessions actives.
2. Rechercher les connexions et activités du compte depuis le clic (`logs_search`, cible : identifiant).
3. Avec l'utilisateur ou le N2 Messagerie : supprimer les règles de boîte de réception créées par l'attaquant et retirer les méthodes MFA inconnues.
4. Fichier exécuté : demander l'isolement du poste (`isolate_host`, validation humaine) et lancer une analyse EDR.
5. Le SOC recherche les autres destinataires et retire le mail des boîtes (action humaine) ; il bloque le domaine malveillant sur le proxy.
6. Mail signalé sans clic : remercier l'utilisateur, lui demander d'utiliser le bouton **Signaler** d'Outlook, puis de supprimer le mail.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | Identifiant, poste | 0 | Automatique (lecture seule) |
| `force_password_reset` | Identifiant | 1 | Automatique si confiance ≥ 0,80 et compte non protégé ; sinon validation humaine |
| `isolate_host` | Poste de l'utilisateur | 2 | Toujours validée par un humain |
| `disable_account` | Identifiant | 2 | Toujours validée par un humain (activité malveillante confirmée) |
| Purger les mails ou supprimer des données | — | 3 | Interdit à l'agent |

## Quand escalader
- Connexion réussie de l'attaquant, règles de transfert créées ou mails envoyés depuis le compte : SOC, priorité P1.
- Compte protégé ou à privilèges concerné : aucune action automatique, SOC immédiatement.
- Plusieurs utilisateurs ont cliqué : SOC pour une réponse globale à la campagne.
