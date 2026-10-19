---
id: KB-IT-016
title: "Écran externe ou station d'accueil qui ne fonctionne pas"
kind: procedure
category: materiel
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [écran, station d'accueil, usb-c, affichage, périphériques]
mitre: []
graph:
  problemes:
    - id: P-ecran-non-detecte
      label: "Écran externe non détecté"
      symptomes:
        - "mon deuxième écran reste noir"
        - "l'écran affiche Aucun signal"
        - "Windows ne détecte qu'un seul écran"
      causes:
        - "mode d'affichage réglé sur Écran du PC uniquement"
        - "câble débranché ou mauvaise entrée sélectionnée sur l'écran"
        - "pilote graphique obsolète"
      solutions:
        - id: S-ecran-projection
          label: "Choisir le mode Étendre (Windows + P) et lancer la détection des écrans"
          automatable: true
          action: null
          action_target: null
        - id: S-ecran-pilote
          label: "Mettre à jour le pilote graphique via Windows Update ou le Portail d'entreprise"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-station-accueil
      label: "Station d'accueil : périphériques, réseau ou charge inopérants"
      symptomes:
        - "le clavier et la souris branchés sur la station ne fonctionnent plus"
        - "pas de réseau filaire via la station d'accueil"
        - "la station d'accueil ne charge plus mon portable"
      causes:
        - "firmware de la station obsolète"
        - "alimentation de la station débranchée ou insuffisante"
        - "station d'accueil défectueuse"
      solutions:
        - id: S-station-reinitialisation
          label: "Réinitialiser la station (coupure 30 secondes) et mettre à jour son firmware"
          automatable: true
          action: null
          action_target: null
        - id: S-station-remplacement
          label: "Remplacement de la station d'accueil (demande de matériel)"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Écran externe ou station d'accueil qui ne fonctionne pas

## Contexte
Les postes portables Exemplia se branchent sur une station d'accueil USB-C qui alimente le portable et relie écrans, clavier, souris et réseau filaire. Un câble USB-C unique relie le portable à la station. La plupart des pannes se règlent par une bonne séquence de rebranchement.

## Étapes
### Écran non détecté
1. Vérifier que l'écran est allumé et que la bonne entrée est choisie (bouton **Source** ou **Input** : HDMI, DisplayPort).
2. Appuyer sur `Windows + P` et choisir **Étendre**.
3. **Paramètres** > **Système** > **Écran** > **Plusieurs écrans** > **Détecter**.
4. Débrancher puis rebrancher le câble vidéo côté écran et côté station ; tester un autre câble si disponible.
5. Mettre à jour le pilote : **Paramètres** > **Windows Update** > **Options avancées** > **Mises à jour facultatives** > pilotes graphiques ; ou via le **Portail d'entreprise** (outil de mise à jour du constructeur).

### Station d'accueil
1. Débrancher le câble USB-C du portable, puis débrancher l'alimentation de la station pendant 30 secondes.
2. Rebrancher l'alimentation de la station, attendre que son voyant soit fixe, puis rebrancher le portable.
3. Vérifier que le bloc d'alimentation est bien celui de la station (puissance suffisante pour charger le portable).
4. Brancher le câble USB-C sur le port du portable marqué d'un éclair ou du logo Thunderbolt.
5. Mettre à jour le firmware de la station via l'outil constructeur disponible dans le **Portail d'entreprise**, puis redémarrer.
6. Tester les périphériques directement sur le portable pour distinguer une panne de station d'une panne de périphérique.

## Vérification
- Les écrans s'affichent en mode étendu, la résolution est correcte (**Paramètres** > **Écran**).
- Clavier, souris et réseau filaire fonctionnent ; l'icône de batterie indique **En charge**.

## Quand escalader
- Station toujours défaillante après réinitialisation et mise à jour : demande de remplacement sur `https://support.exemplia.local` (validation du manager), traitée par le N2 Poste de travail.
- Écran défectueux (pixels morts, ne s'allume plus) : demande de matériel, aucune réparation sur place.
- Besoin d'un écran supplémentaire : demande d'achat validée par le manager.
