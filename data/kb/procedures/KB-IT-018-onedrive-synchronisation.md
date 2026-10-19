---
id: KB-IT-018
title: "OneDrive ne synchronise plus"
kind: procedure
category: logiciel
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [onedrive, synchronisation, microsoft 365, conflit, fichiers]
mitre: []
graph:
  problemes:
    - id: P-onedrive-sync-bloquee
      label: "OneDrive ne synchronise plus"
      symptomes:
        - "l'icône OneDrive affiche une croix rouge"
        - "mes fichiers ne se synchronisent plus depuis hier"
        - "OneDrive reste bloqué sur Traitement des modifications"
      causes:
        - "synchronisation suspendue ou compte OneDrive déconnecté"
        - "client OneDrive bloqué"
        - "espace OneDrive de 1 To saturé"
      solutions:
        - id: S-onedrive-reprise
          label: "Reprendre la synchronisation et reconnecter le compte"
          automatable: true
          action: null
          action_target: null
        - id: S-onedrive-reinitialisation
          label: "Réinitialiser le client OneDrive"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-onedrive-fichier-bloque
      label: "Fichier impossible à synchroniser ou en conflit"
      symptomes:
        - "un fichier a une icône rouge et ne se synchronise pas"
        - "des doublons de mes fichiers apparaissent avec le nom de mon poste"
      causes:
        - "nom de fichier avec caractères interdits ou chemin trop long"
        - "fichier modifié en même temps sur deux appareils"
        - "fichier ouvert et verrouillé par une application"
      solutions:
        - id: S-onedrive-renommage-fusion
          label: "Renommer le fichier ou raccourcir le chemin, puis fusionner les versions"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# OneDrive ne synchronise plus

## Contexte
Chaque salarié dispose de 1 To sur OneDrive Entreprise ; les dossiers **Bureau**, **Documents** et **Images** y sont redirigés automatiquement. L'icône en forme de nuage dans la zone de notification indique l'état : nuage bleu = à jour, flèches = synchronisation en cours, croix rouge = erreur, pause = synchronisation suspendue.

## Étapes
### Synchronisation bloquée
1. Cliquer sur l'icône OneDrive : lire le message d'erreur affiché en haut du panneau.
2. Si la synchronisation est en pause : roue dentée > **Reprendre la synchronisation**.
3. Si OneDrive demande une connexion : cliquer sur **Se connecter** et valider avec Microsoft Authenticator.
4. Vérifier l'espace : roue dentée > **Paramètres** > **Compte** (utilisation du stockage).
5. Fermer OneDrive (roue dentée > **Quitter OneDrive**) puis le relancer depuis le menu **Démarrer**.
6. Si le blocage persiste, réinitialiser le client avec `Windows + R` :
   ```cmd
   %localappdata%\Microsoft\OneDrive\onedrive.exe /reset
   ```
   Relancer OneDrive depuis le menu **Démarrer** si l'icône ne réapparaît pas après 2 minutes ; la resynchronisation complète peut durer plusieurs heures, sans perte de données.

### Fichier bloqué ou en conflit
1. Caractères interdits dans les noms : `" * : < > ? / \ |` ; supprimer aussi les espaces en fin de nom. Renommer le fichier.
2. Chemin trop long (plus de 400 caractères) : raccourcir les noms de dossiers ou remonter le fichier d'un niveau.
3. Fermer le fichier dans l'application qui l'utilise, puis attendre la synchronisation.
4. Conflit (copie suffixée du nom du poste) : ouvrir les deux versions, fusionner le contenu dans l'original, puis supprimer la copie.
5. Pour revenir en arrière : clic droit sur le fichier > **Historique des versions**. Un fichier supprimé reste 93 jours dans la corbeille OneDrive en ligne.

## Vérification
- L'icône OneDrive affiche **Vos fichiers sont synchronisés**.
- Un fichier modifié sur le poste apparaît à jour sur `https://www.office.com` > **OneDrive**.

## Quand escalader
- Erreur persistante après réinitialisation, ou quota de 1 To atteint : N2 Messagerie et collaboration.
- Fichiers renommés en masse avec une extension inconnue ou disparition massive de fichiers : SOC immédiatement (KB-CY-006).
- Synchronisation d'un grand volume vers un compte OneDrive personnel : signaler au SOC (KB-CY-008).
