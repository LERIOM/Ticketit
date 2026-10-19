---
id: KB-IT-015
title: "Poste de travail lent"
kind: procedure
category: materiel
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [lenteur, performance, windows 11, disque plein, redémarrage]
mitre: []
graph:
  problemes:
    - id: P-poste-lent
      label: "Poste de travail lent"
      symptomes:
        - "mon PC est très lent"
        - "le démarrage prend plus de 10 minutes"
        - "le ventilateur tourne en permanence et tout rame"
      causes:
        - "poste non redémarré depuis plusieurs jours"
        - "mises à jour Windows en attente"
        - "application consommant trop de processeur ou de mémoire"
      solutions:
        - id: S-poste-lent-autodiagnostic
          label: "Redémarrer, installer les mises à jour et identifier le processus gourmand"
          automatable: true
          action: null
          action_target: null
        - id: S-poste-lent-intervention-n2
          label: "Prise en main à distance et diagnostic matériel par le N2"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-disque-plein
      label: "Disque système presque plein"
      symptomes:
        - "espace disque insuffisant sur C:"
        - "Windows indique que le stockage est faible"
      causes:
        - "fichiers temporaires et téléchargements accumulés"
        - "fichiers OneDrive tous conservés en local"
      solutions:
        - id: S-disque-nettoyage
          label: "Nettoyer le disque et libérer l'espace occupé par OneDrive"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Poste de travail lent

## Contexte
La lenteur d'un poste Windows 11 a le plus souvent une cause simple : poste jamais redémarré (la mise en veille ne remplace pas un redémarrage), mises à jour en attente, disque presque plein ou application trop gourmande. Le matériel n'est en cause qu'après ces vérifications.

## Étapes
1. Vérifier la date du dernier démarrage :
   ```cmd
   systeminfo | findstr /C:"Heure de démarrage du système"
   ```
   Plus de 3 jours : **Démarrer** > **Marche/Arrêt** > **Redémarrer** (pas **Arrêter**, qui conserve un démarrage rapide).
2. **Paramètres** > **Windows Update** : installer les mises à jour en attente et redémarrer.
3. Ouvrir le Gestionnaire des tâches (`Ctrl + Maj + Échap`) > **Processus**, trier par **Processeur** puis par **Mémoire** ; fermer l'application qui consomme le plus si elle n'est pas nécessaire.
4. Onglet **Applications de démarrage** : désactiver les applications non indispensables (ne pas toucher à l'antivirus ni à FortiClient).
5. Fermer les onglets de navigateur inutiles ; au-delà de 30 onglets, la mémoire est souvent saturée.

### Disque presque plein
1. **Paramètres** > **Système** > **Stockage** : consulter la répartition et ouvrir **Recommandations de nettoyage**.
2. Supprimer les fichiers temporaires, vider la **Corbeille** et trier le dossier **Téléchargements**.
3. Activer l'**Assistant Stockage** pour un nettoyage automatique.
4. OneDrive : clic droit sur un dossier volumineux > **Libérer de l'espace** (les fichiers restent disponibles en ligne).
5. Objectif : au moins 15 % du disque libre.

## Vérification
- Le Gestionnaire des tâches montre un processeur sous 30 % et une mémoire sous 80 % au repos.
- Le démarrage du poste prend moins de 2 minutes.

## Quand escalader
- Lenteur persistante après redémarrage, mises à jour et nettoyage : N2 Poste de travail (prise en main à distance, diagnostic disque et mémoire).
- Poste de plus de 4 ans ou disque en erreur : renouvellement (KB-IT-017).
- Processus inconnu très gourmand, fenêtres PowerShell qui s'ouvrent seules ou antivirus désactivé : SOC (KB-CY-007).
