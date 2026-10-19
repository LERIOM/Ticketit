---
id: KB-IT-017
title: "Ordinateur portable perdu, volé ou à renouveler"
kind: procedure
category: materiel
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [ordinateur portable, perte, vol, renouvellement, bitlocker]
mitre: []
graph:
  problemes:
    - id: P-portable-perdu-vole
      label: "Ordinateur portable perdu ou volé"
      symptomes:
        - "on m'a volé mon ordinateur portable dans le train"
        - "j'ai oublié mon PC portable dans un taxi"
        - "mon sac avec le PC du travail a disparu"
      causes:
        - "perte ou vol du matériel en déplacement"
      solutions:
        - id: S-perte-reset-mdp
          label: "Réinitialiser le mot de passe et révoquer les sessions après vérification d'identité"
          automatable: false
          action: force_password_reset
          action_target: username
        - id: S-perte-isolement-poste
          label: "Isoler le poste à distance via l'EDR en attendant la décision du RSSI"
          automatable: false
          action: isolate_host
          action_target: hostname
      actifs: []
    - id: P-portable-renouvellement
      label: "Renouvellement d'un ordinateur portable"
      symptomes:
        - "mon portable a plus de 4 ans et devient trop lent"
        - "la batterie de mon portable ne tient plus une heure"
        - "l'écran de mon ordinateur portable est cassé"
      causes:
        - "fin du cycle de vie de 4 ans"
        - "panne matérielle ou casse"
      solutions:
        - id: S-renouvellement-demande
          label: "Demande de renouvellement validée par le manager"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Ordinateur portable perdu, volé ou à renouveler

## Contexte
Les portables Exemplia sont chiffrés par BitLocker et gérés par Intune et l'EDR : un poste perdu ne donne pas directement accès aux données, mais les sessions ouvertes et les mots de passe mémorisés doivent être neutralisés au plus vite. Les postes sont nommés selon le service et un numéro (exemple : `PC-COMPTA-07`), indiqués sur l'étiquette d'inventaire. Le cycle de renouvellement standard est de 4 ans.

## Étapes
### Perte ou vol (priorité P2)
1. Déclarer immédiatement la perte au service desk (téléphone ou `https://support.exemplia.local` > **Matériel** > **Déclaration de perte ou de vol**) avec le nom du poste, le lieu, la date et l'heure.
2. Le service desk vérifie l'identité du déclarant (rappel sur le numéro professionnel de l'annuaire ou validation du manager).
3. Le service desk réinitialise le mot de passe et révoque les sessions Microsoft 365 du compte.
4. Le SOC isole le poste via l'EDR dès sa prochaine connexion ; le RSSI décide d'un éventuel effacement à distance via Intune (action humaine, jamais automatique).
5. En cas de vol : déposer plainte sous 48 heures et joindre le récépissé au ticket (obligatoire pour l'assurance).
6. Si le téléphone professionnel a aussi disparu : suivre KB-IT-003 (cas 3).
7. Un poste de prêt est remis après validation du manager ; les données OneDrive sont retrouvées à la première connexion.

### Renouvellement
1. Vérifier l'âge du poste sur l'étiquette d'inventaire ou dans le Portail d'entreprise (**Appareils**).
2. Ouvrir une demande sur `https://support.exemplia.local` > **Matériel** > **Renouvellement de poste** en précisant le motif (âge, panne, casse).
3. Le manager valide la demande ; un rendez-vous de remise est proposé sous 10 jours ouvrés.
4. Avant la remise : vérifier que tous les fichiers sont dans OneDrive (aucun fichier uniquement sur le bureau ou dans `C:\`).
5. Restituer l'ancien poste, son chargeur et sa station si elle est remplacée ; le poste est effacé par la DSI.

## Vérification
- Perte : sessions révoquées, poste marqué perdu dans l'inventaire, isolement demandé dans l'EDR.
- Renouvellement : l'utilisateur retrouve ses fichiers OneDrive, ses applications et son imprimante sur le nouveau poste.

## Quand escalader
- Tout vol ou perte : SOC et RSSI informés systématiquement ; les actions d'isolement et d'effacement exigent une validation humaine.
- Poste perdu contenant des données sensibles hors OneDrive (RH, clients) : RSSI et DPO, évaluation d'une notification CNIL sous 72 heures.
- Renouvellement hors cycle (casse répétée, besoin spécifique) : validation du manager et du responsable Poste de travail.
