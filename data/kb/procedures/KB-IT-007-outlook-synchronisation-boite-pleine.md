---
id: KB-IT-007
title: "Outlook ne synchronise pas ou boîte aux lettres pleine"
kind: procedure
category: messagerie
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [outlook, microsoft 365, synchronisation, quota, boîte pleine]
mitre: []
graph:
  problemes:
    - id: P-outlook-sync
      label: "Outlook ne synchronise plus"
      symptomes:
        - "je ne reçois plus de mails dans Outlook mais ils sont visibles sur le webmail"
        - "Outlook affiche Déconnecté en bas de la fenêtre"
        - "mes mails restent bloqués dans la boîte d'envoi"
      causes:
        - "Outlook en mode Travailler hors connexion"
        - "fichier de cache OST corrompu"
        - "profil Outlook endommagé"
      solutions:
        - id: S-outlook-mode-connexion
          label: "Désactiver le mode hors connexion et vérifier l'état de la connexion"
          automatable: true
          action: null
          action_target: null
        - id: S-outlook-reconstruction-profil
          label: "Réparer le compte ou recréer le profil Outlook"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-boite-pleine
      label: "Boîte aux lettres pleine"
      symptomes:
        - "message : votre boîte aux lettres est pleine"
        - "je ne peux plus envoyer de mails, quota atteint"
        - "mes correspondants reçoivent un message de non-remise"
      causes:
        - "quota de 50 Go atteint"
        - "pièces jointes volumineuses et éléments supprimés jamais vidés"
      solutions:
        - id: S-boite-nettoyage
          label: "Nettoyer la boîte et activer l'archivage en ligne"
          automatable: true
          action: null
          action_target: null
        - id: S-boite-extension-quota
          label: "Demande d'extension de quota validée par le manager"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Outlook ne synchronise pas ou boîte aux lettres pleine

## Contexte
La messagerie d'Exemplia est hébergée sur Microsoft 365 (Exchange Online). Outlook classique conserve une copie locale (fichier `.ost`). Le webmail `https://outlook.office.com` montre l'état réel de la boîte : si un message y apparaît mais pas dans Outlook, le problème est local au poste. Le quota standard est de 50 Go.

## Étapes
### Outlook ne synchronise plus
1. Comparer avec `https://outlook.office.com` : si le webmail ne fonctionne pas non plus, vérifier l'état du service (escalade).
2. Onglet **Envoi/réception** : si **Travailler hors connexion** est surligné, cliquer dessus pour le désactiver.
3. Fermer Outlook, vérifier dans le Gestionnaire des tâches (`Ctrl + Maj + Échap`) qu'aucun processus `OUTLOOK.EXE` ne subsiste, puis relancer.
4. **Fichier** > **Paramètres du compte** > **Paramètres du compte** > sélectionner le compte > **Réparer**.
5. Si le problème persiste, recréer le profil : **Panneau de configuration** > **Courrier (Microsoft Outlook)** > **Afficher les profils** > **Ajouter**, configurer le compte, puis cocher **Toujours utiliser ce profil**.
6. La première synchronisation du nouveau profil peut durer jusqu'à une heure.

### Boîte aux lettres pleine
1. Voir l'occupation : **Fichier** > **Informations** > **Outils** > **Nettoyage de la boîte aux lettres** > **Afficher la taille de la boîte aux lettres**.
2. Vider le dossier **Éléments supprimés** (clic droit > **Vider le dossier**) puis **Éléments récupérables** depuis le webmail.
3. Rechercher les gros messages : dans la barre de recherche, saisir `taille:énorme` ou trier par taille, et enregistrer les pièces jointes utiles dans OneDrive avant de supprimer les messages.
4. Déplacer les anciens messages dans **Archive en ligne** (dossier **Archive** visible dans le volet de gauche).

## Vérification
- La barre d'état indique **Connecté à : Microsoft Exchange** et **Tous les dossiers sont à jour**.
- La jauge de taille repasse sous 90 % du quota ; un message de test est envoyé et reçu.

## Quand escalader
- Webmail également en panne ou plusieurs utilisateurs touchés : N2 Messagerie, priorité P2.
- Boîte toujours pleine après nettoyage : demande d'extension de quota ou d'archive validée par le manager, traitée par le N2 Messagerie.
- Messages envoyés à l'insu de l'utilisateur ou règles de transfert inconnues : SOC (KB-CY-003).
