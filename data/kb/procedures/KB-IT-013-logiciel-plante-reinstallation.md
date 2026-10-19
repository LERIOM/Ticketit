---
id: KB-IT-013
title: "Logiciel qui plante : réparation ou réinstallation"
kind: procedure
category: logiciel
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [plantage, microsoft 365, réparation, réinstallation, compléments]
mitre: []
graph:
  problemes:
    - id: P-logiciel-plante
      label: "Application qui plante ou ne démarre plus"
      symptomes:
        - "Excel se ferme tout seul quand j'ouvre un fichier"
        - "l'application ne répond pas puis se ferme"
        - "message : l'application a cessé de fonctionner"
        - "Outlook plante au démarrage"
      causes:
        - "complément (add-in) défectueux"
        - "installation endommagée ou mise à jour incomplète"
      solutions:
        - id: S-app-mode-sans-echec
          label: "Démarrer en mode sans échec et désactiver les compléments"
          automatable: true
          action: null
          action_target: null
        - id: S-office-reparation
          label: "Réparer Microsoft 365 (réparation rapide puis en ligne)"
          automatable: true
          action: null
          action_target: null
        - id: S-app-reinstallation-portail
          label: "Désinstaller puis réinstaller l'application depuis le Portail d'entreprise"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-plantages-multiples
      label: "Plusieurs applications plantent sur le même poste"
      symptomes:
        - "tout plante sur mon PC depuis ce matin"
        - "écran bleu puis redémarrage du poste"
      causes:
        - "fichiers système Windows corrompus"
        - "défaillance matérielle (mémoire, disque)"
      solutions:
        - id: S-poste-controle-systeme
          label: "Contrôle d'intégrité Windows et diagnostic matériel par le N2"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Logiciel qui plante : réparation ou réinstallation

## Contexte
La plupart des plantages d'une seule application viennent d'un complément, d'un fichier précis ou d'une installation abîmée. On procède du plus simple au plus lourd : redémarrage, mode sans échec, réparation, réinstallation. Si plusieurs applications plantent sur le même poste, le problème est système ou matériel.

## Étapes
1. Enregistrer le travail en cours, redémarrer le poste et retester.
2. Noter si le plantage survient avec **un fichier précis** (tester un autre fichier) ou avec tous les fichiers.
3. Applications Office : démarrer en mode sans échec avec `Windows + R` puis `excel /safe` (ou `winword /safe`, `outlook /safe`, `powerpnt /safe`).
4. Si l'application fonctionne en mode sans échec : **Fichier** > **Options** > **Compléments** > **Gérer : Compléments COM** > **Atteindre**, décocher tous les compléments, puis les réactiver un par un pour trouver le coupable.
5. Réparer Microsoft 365 : **Paramètres** > **Applications** > **Applications installées** > **Microsoft 365** > `...` > **Modifier** > **Réparation rapide** ; si insuffisant, **Réparation en ligne** (30 minutes, connexion Internet requise).
6. Autres logiciels : **Portail d'entreprise** > fiche du logiciel > **Désinstaller**, redémarrer, puis **Installer** (voir KB-IT-012).
7. Pour le diagnostic, relever l'erreur dans l'**Observateur d'événements** > **Journaux Windows** > **Application** (événement 1000, nom du module en faute).

### Plantages sur plusieurs applications
1. Relever les codes d'arrêt des écrans bleus et l'heure des incidents.
2. Le N2 lance à distance les contrôles d'intégrité (droits administrateur requis) :
   ```cmd
   sfc /scannow
   DISM /Online /Cleanup-Image /RestoreHealth
   ```
3. Si les contrôles sont sains, le N2 planifie un diagnostic matériel (mémoire, disque).

## Vérification
- L'application démarre normalement et ouvre le fichier qui posait problème.
- Aucun nouvel événement 1000 pour l'application dans l'heure qui suit.

## Quand escalader
- Plantage persistant après réparation en ligne ou réinstallation : N2 Poste de travail avec le nom du module en faute.
- Écrans bleus répétés ou plantages de plusieurs applications : N2 Poste de travail, remplacement du poste possible (KB-IT-017).
- Plantages accompagnés de fenêtres PowerShell ou de processus inconnus : SOC (KB-CY-007).
