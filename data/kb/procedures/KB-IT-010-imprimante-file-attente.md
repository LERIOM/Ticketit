---
id: KB-IT-010
title: "Impression bloquée ou document introuvable sur le copieur (PaperCut)"
kind: procedure
category: impression
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [imprimante, papercut, file d'attente, spouleur, badge]
mitre: []
graph:
  problemes:
    - id: P-impression-bloquee
      label: "Impression bloquée dans la file d'attente"
      symptomes:
        - "mon document reste bloqué dans la file d'attente"
        - "l'imprimante affiche Erreur - impression"
        - "rien ne sort de l'imprimante alors que j'ai lancé l'impression"
      causes:
        - "travail d'impression corrompu qui bloque la file"
        - "spouleur d'impression Windows planté"
        - "copieur en erreur (bourrage, papier ou toner)"
      solutions:
        - id: S-impression-vider-file
          label: "Annuler les travaux bloqués et relancer l'impression"
          automatable: true
          action: null
          action_target: null
        - id: S-impression-redemarrage-spouleur
          label: "Redémarrer le spouleur d'impression à distance (technicien service desk)"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-papercut-liberation
      label: "Document absent au moment de la libération par badge"
      symptomes:
        - "quand je badge sur le copieur mon document n'apparaît pas"
        - "PaperCut : aucun travail en attente"
        - "le copieur ne reconnaît pas mon badge"
      causes:
        - "impression envoyée sur une autre file que la file sécurisée"
        - "travail expiré après 24 heures"
        - "badge non associé au compte utilisateur"
      solutions:
        - id: S-papercut-file-securisee
          label: "Imprimer sur la file sécurisée Exemplia-Securise et associer le badge"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Impression bloquée ou document introuvable sur le copieur (PaperCut)

## Contexte
Les multifonctions d'Exemplia sont gérés par PaperCut. Les postes impriment sur une file unique, **Exemplia-Securise** : le document est retenu jusqu'à ce que l'utilisateur passe son badge sur n'importe quel copieur du site (impression « Follow-me »). Les travaux non libérés sont supprimés au bout de 24 heures.

## Étapes
### Impression bloquée
1. Vérifier l'écran du copieur : bourrage, bac vide, toner épuisé. Signaler une panne matérielle via l'écran PaperCut ou le portail ITSM.
2. **Paramètres** > **Bluetooth et appareils** > **Imprimantes et scanners** > **Exemplia-Securise** > **Ouvrir la file d'attente**.
3. Menu **Imprimante** > **Annuler tous les documents** (ou clic droit > **Annuler** sur le document en erreur).
4. Relancer l'impression ; pour un PDF volumineux, essayer **Imprimer comme une image** dans les options avancées du lecteur PDF.
5. Si la file reste bloquée, un technicien redémarre le spouleur à distance :
   ```powershell
   Restart-Service -Name Spooler -Force
   ```
6. Redémarrer le poste si le technicien n'est pas disponible : cela relance aussi le spouleur.

### Document introuvable au copieur
1. Vérifier que l'imprimante choisie est bien **Exemplia-Securise** et non une ancienne imprimante directe.
2. Consulter ses travaux en attente sur l'interface utilisateur PaperCut (lien **Mes impressions** du portail intranet) > **Travaux en attente de libération**.
3. Badge non reconnu : sur le copieur, se connecter avec l'identifiant et le mot de passe Windows ; PaperCut propose alors d'**associer la carte** au compte.
4. Réimprimer le document s'il a expiré (plus de 24 heures).

## Vérification
- La file d'attente du poste est vide après l'envoi et le document apparaît dans PaperCut.
- Le document sort après passage du badge.

## Quand escalader
- Copieur en panne (code d'erreur matériel, bruit anormal) : ticket de maintenance prestataire via le N2 Poste de travail.
- Tous les utilisateurs d'un site ne peuvent plus imprimer : incident serveur PaperCut, N2 en priorité P2.
- Message de rançon ou fichiers étranges imprimés en masse : prévenir le SOC.
