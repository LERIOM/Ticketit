---
id: KB-IT-011
title: "Numérisation vers e-mail : document non reçu ou trop volumineux"
kind: procedure
category: impression
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [scanner, numérisation, copieur, papercut, e-mail]
mitre: []
graph:
  problemes:
    - id: P-scan-email-non-recu
      label: "Numérisation vers e-mail non reçue"
      symptomes:
        - "j'ai scanné un document mais je ne reçois pas le mail"
        - "le copieur affiche une erreur d'envoi SMTP"
        - "le scan vers ma messagerie ne marche plus depuis ce matin"
      causes:
        - "message classé en courrier indésirable ou en quarantaine"
        - "adresse de destination mal saisie"
        - "relais SMTP du copieur indisponible"
      solutions:
        - id: S-scan-verif-reception
          label: "Vérifier l'adresse, le courrier indésirable et la quarantaine"
          automatable: true
          action: null
          action_target: null
        - id: S-scan-escalade-relais
          label: "Vérification du relais SMTP des copieurs par le N2"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-scan-taille-pj
      label: "Fichier numérisé trop volumineux"
      symptomes:
        - "le scan d'un document de 80 pages n'arrive jamais"
        - "message : la taille du fichier dépasse la limite autorisée"
      causes:
        - "pièce jointe supérieure à 20 Mo"
        - "résolution ou mode couleur trop élevés"
      solutions:
        - id: S-scan-reduction-taille
          label: "Réduire la résolution, scanner en noir et blanc ou utiliser Scan vers OneDrive"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Numérisation vers e-mail : document non reçu ou trop volumineux

## Contexte
Sur les multifonctions PaperCut, la fonction **Scan vers moi** envoie le document à l'adresse de l'utilisateur badgé. Les messages partent d'une adresse technique des copieurs via un relais SMTP interne. La taille maximale d'une pièce jointe issue d'un copieur est de 20 Mo ; au-delà, utiliser **Scan vers OneDrive**.

## Étapes
### Document non reçu
1. Vérifier sur le copieur que l'utilisateur était bien badgé et a choisi **Scan vers moi** (et non une adresse saisie à la main).
2. Attendre 5 minutes : les gros fichiers peuvent mettre du temps à arriver.
3. Dans Outlook, vérifier le dossier **Courrier indésirable** ; rechercher l'expéditeur des copieurs dans tous les dossiers.
4. Vérifier la quarantaine Microsoft 365 : `https://security.microsoft.com/quarantine` > **Mes messages en quarantaine** ; demander la libération si le message y figure.
5. Faire un scan de test d'une seule page en noir et blanc.
6. Si le copieur affiche une erreur SMTP ou si le test échoue, noter le numéro du copieur (étiquette sur la façade) et l'heure du test.

### Fichier trop volumineux
1. Sur le copieur, dans **Paramètres de numérisation** : choisir **Noir et blanc** ou **Niveaux de gris**, résolution **200 ppp**, format **PDF compact**.
2. Scinder un document de plus de 50 pages en plusieurs envois.
3. Préférer **Scan vers OneDrive** : le fichier arrive dans le dossier `OneDrive > Numérisations` sans limite de taille.

## Vérification
- Le scan de test d'une page arrive dans la boîte de réception en moins de 2 minutes.
- Le document complet est reçu et lisible.

## Quand escalader
- Erreur SMTP sur un ou plusieurs copieurs, ou aucun utilisateur ne reçoit ses scans : N2 Poste de travail (relais SMTP des copieurs), priorité P3.
- Messages des copieurs bloqués en quarantaine pour tous les utilisateurs : N2 Messagerie.
- Utilisateur recevant des « scans » qu'il n'a pas faits avec des liens ou pièces jointes : possible phishing, voir KB-CY-003.
