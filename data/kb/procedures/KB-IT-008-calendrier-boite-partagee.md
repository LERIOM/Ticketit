---
id: KB-IT-008
title: "Partage de calendrier et accès à une boîte aux lettres partagée"
kind: procedure
category: messagerie
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [outlook, calendrier, boîte partagée, délégation, microsoft 365]
mitre: []
graph:
  problemes:
    - id: P-partage-calendrier
      label: "Partager son calendrier avec un collègue"
      symptomes:
        - "comment donner accès à mon calendrier à mon assistante"
        - "mon collègue ne voit que mes disponibilités et pas le détail des réunions"
        - "je veux que quelqu'un puisse gérer mes invitations"
      causes:
        - "partage par défaut limité aux disponibilités"
      solutions:
        - id: S-calendrier-partage
          label: "Partager le calendrier depuis Outlook avec le niveau de droits adapté"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-acces-boite-partagee
      label: "Accès à une boîte aux lettres partagée"
      symptomes:
        - "la boîte partagée de mon service n'apparaît pas dans Outlook"
        - "accès refusé quand j'ouvre la boîte partagée de la comptabilité"
        - "je ne peux pas envoyer en tant que la boîte du service"
      causes:
        - "droits non attribués sur la boîte partagée"
        - "droits attribués récemment mais Outlook pas encore actualisé"
      solutions:
        - id: S-boite-partagee-demande-droits
          label: "Demande de droits validée par le propriétaire de la boîte partagée"
          automatable: false
          action: null
          action_target: null
        - id: S-boite-partagee-ajout-outlook
          label: "Ajouter la boîte partagée dans Outlook une fois les droits accordés"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Partage de calendrier et accès à une boîte aux lettres partagée

## Contexte
Chaque salarié peut partager lui-même son calendrier. En revanche, l'accès à une boîte aux lettres partagée (par exemple la boîte d'un service) se demande au service desk et doit être validé par le propriétaire de la boîte (en général le responsable du service). Les droits sont accordés via un groupe Microsoft 365.

## Étapes
### Partager son calendrier (Outlook classique)
1. Ouvrir le **Calendrier**, onglet **Accueil** > **Partager le calendrier** > choisir **Calendrier**.
2. Cliquer sur **Ajouter**, rechercher le collègue dans l'annuaire, puis choisir le niveau :
   - **Peut afficher quand je suis occupé(e)** : disponibilités seulement ;
   - **Peut afficher tous les détails** : lecture complète ;
   - **Peut modifier** : création et modification de rendez-vous ;
   - **Délégué** : gestion des invitations au nom de l'utilisateur.
3. Valider par **OK** ; le collègue reçoit une invitation à accepter.
4. Les rendez-vous marqués **Privé** restent masqués, sauf choix explicite pour un délégué.

### Accéder à une boîte partagée
1. Ouvrir un ticket sur `https://support.exemplia.local` > **Messagerie** > **Accès à une boîte partagée** en indiquant l'adresse de la boîte et le besoin (lecture, envoi en tant que).
2. Le propriétaire de la boîte reçoit la demande de validation ; le service desk n'accorde aucun droit sans cet accord.
3. Une fois les droits accordés, patienter jusqu'à 60 minutes : la boîte apparaît automatiquement dans le volet gauche après redémarrage d'Outlook.
4. Si elle n'apparaît pas : **Fichier** > **Paramètres du compte** > **Paramètres du compte** > **Modifier** > **Paramètres supplémentaires** > **Avancé** > **Ajouter** la boîte.
5. Pour envoyer depuis la boîte : dans un nouveau message, **Options** > **De**, puis choisir l'adresse de la boîte partagée.

## Vérification
- Le collègue voit le calendrier partagé dans **Calendriers partagés**.
- La boîte partagée s'ouvre et un message de test peut être envoyé depuis son adresse.

## Quand escalader
- Propriétaire de la boîte absent ou inconnu : demander la validation au manager du demandeur.
- Droits accordés depuis plus de 2 heures et boîte toujours inaccessible : N2 Messagerie.
- Demande d'accès à la boîte d'une personne absente ou partie (RH, direction) : validation RH obligatoire.
