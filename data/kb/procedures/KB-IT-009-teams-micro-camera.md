---
id: KB-IT-009
title: "Teams : micro ou caméra qui ne fonctionne pas"
kind: procedure
category: logiciel
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [teams, micro, caméra, visioconférence, périphériques]
mitre: []
graph:
  problemes:
    - id: P-teams-micro
      label: "Micro non détecté ou inaudible dans Teams"
      symptomes:
        - "mes collègues ne m'entendent pas dans Teams"
        - "Teams : aucun microphone détecté"
        - "mon casque fonctionne pour la musique mais pas dans Teams"
      causes:
        - "mauvais périphérique audio sélectionné dans Teams"
        - "accès au micro bloqué dans les paramètres de confidentialité Windows"
        - "casque Bluetooth connecté en mode écoute seule"
      solutions:
        - id: S-teams-selection-peripherique
          label: "Sélectionner le bon périphérique dans Teams et faire un appel test"
          automatable: true
          action: null
          action_target: null
        - id: S-teams-confidentialite-windows
          label: "Autoriser l'accès au micro et à la caméra dans la confidentialité Windows"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-teams-camera
      label: "Caméra noire ou indisponible dans Teams"
      symptomes:
        - "ma caméra reste noire en réunion Teams"
        - "Teams indique que la caméra est utilisée par une autre application"
      causes:
        - "caméra déjà utilisée par une autre application"
        - "cache physique ou touche de désactivation de la caméra"
        - "cache de Teams corrompu"
      solutions:
        - id: S-teams-liberation-camera
          label: "Libérer la caméra (fermer les autres applications, ouvrir le cache physique)"
          automatable: true
          action: null
          action_target: null
        - id: S-teams-reinitialisation-cache
          label: "Réinitialiser l'application Teams"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Teams : micro ou caméra qui ne fonctionne pas

## Contexte
Microsoft Teams utilise les périphériques choisis dans ses propres paramètres, indépendamment du périphérique par défaut de Windows. Windows 11 peut aussi bloquer l'accès au micro ou à la caméra pour les applications de bureau. Les postes portables Exemplia disposent d'un cache physique sur la caméra et d'une touche de coupure du micro (touche **F4** ou équivalent selon le modèle).

## Étapes
### Micro
1. Vérifier le bouton de sourdine du casque et la touche de coupure du micro du clavier (voyant allumé = micro coupé).
2. Dans Teams : **Paramètres et plus** (`...`) > **Paramètres** > **Appareils** ; dans **Périphériques audio**, choisir le casque utilisé pour le haut-parleur **et** le micro.
3. Cliquer sur **Passer un appel test** et suivre l'enregistrement de 10 secondes.
4. **Paramètres Windows** > **Confidentialité et sécurité** > **Microphone** : activer **Accès au microphone** et **Autoriser les applications de bureau à accéder à votre microphone**.
5. Casque Bluetooth : dans **Paramètres** > **Bluetooth et appareils** > **Son**, sélectionner l'entrée **Mains libres** du casque ; à défaut, retirer puis réappairer le casque.

### Caméra
1. Ouvrir le cache physique de la caméra et vérifier la touche de désactivation de la caméra.
2. Fermer les applications qui peuvent utiliser la caméra (application Caméra, navigateur avec une autre visio, logiciels de visio tiers).
3. Teams > **Paramètres** > **Appareils** > **Caméra** : vérifier l'aperçu ; choisir la caméra intégrée ou la webcam externe.
4. **Confidentialité et sécurité** > **Caméra** : autoriser l'accès pour les applications de bureau.
5. Si l'aperçu reste noir : **Paramètres** > **Applications** > **Applications installées** > **Microsoft Teams** > **Options avancées** > **Réinitialiser**, puis relancer Teams et se reconnecter.
6. Redémarrer le poste (et la station d'accueil si la webcam y est branchée).

## Vérification
- L'appel test restitue la voix correctement ; l'aperçu caméra s'affiche dans les paramètres Teams.
- Une réunion avec un collègue confirme le son et l'image.

## Quand escalader
- Micro ou caméra introuvables dans le **Gestionnaire de périphériques** : panne matérielle probable, N2 Poste de travail.
- Casque fourni par Exemplia défectueux : demande de remplacement via le portail ITSM (validation du manager).
- Problème présent dans toutes les applications après réinitialisation : N2 Poste de travail (pilote ou image système).
