---
id: KB-IT-014
title: "Accès à un dossier partagé : accès refusé ou lecteur réseau absent"
kind: procedure
category: acces_compte
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [dossier partagé, lecteur réseau, droits, groupes ad, serveur de fichiers]
mitre: []
graph:
  problemes:
    - id: P-dossier-partage-refuse
      label: "Accès refusé à un dossier partagé"
      symptomes:
        - "accès refusé au dossier de mon service sur le lecteur S:"
        - "vous n'avez pas l'autorisation d'accéder à ce dossier"
        - "je dois accéder au dossier d'un autre service pour un projet"
      causes:
        - "compte absent du groupe AD qui donne accès au dossier"
        - "nouvel arrivant ou changement de service"
        - "droits ajoutés mais session Windows pas encore renouvelée"
      solutions:
        - id: S-partage-verif-groupes
          label: "Vérifier les groupes AD du compte"
          automatable: true
          action: account_info
          action_target: username
        - id: S-partage-demande-droits
          label: "Demande de droits validée par le propriétaire du dossier"
          automatable: false
          action: null
          action_target: null
        - id: S-partage-renouvellement-session
          label: "Fermer puis rouvrir la session pour appliquer les nouveaux groupes"
          automatable: true
          action: null
          action_target: null
      actifs: ["SRV-FILE-01"]
    - id: P-lecteur-reseau-absent
      label: "Lecteur réseau absent ou déconnecté"
      symptomes:
        - "le lecteur S: a disparu de l'Explorateur de fichiers"
        - "le lecteur réseau affiche une croix rouge"
      causes:
        - "VPN non connecté hors des locaux"
        - "script de connexion non exécuté à l'ouverture de session"
      solutions:
        - id: S-lecteur-reconnexion
          label: "Reconnecter le lecteur réseau (VPN, gpupdate ou net use)"
          automatable: true
          action: null
          action_target: null
      actifs: ["SRV-FILE-01"]
---

# Accès à un dossier partagé : accès refusé ou lecteur réseau absent

## Contexte
Les dossiers partagés sont hébergés sur `SRV-FILE-01` et montés en lecteur `S:` à l'ouverture de session. Les droits sont donnés par des groupes Active Directory nommés `GG_FILE_<Service>_RO` (lecture) et `GG_FILE_<Service>_RW` (modification). Chaque dossier a un propriétaire métier (en général le responsable du service) qui valide les accès. Le service desk n'accorde jamais un droit sans cette validation.

## Étapes
### Accès refusé
1. Faire préciser le chemin exact (par exemple `S:\Finance\Budget`) et le besoin : lecture ou modification.
2. Vérifier les groupes du compte : côté utilisateur `whoami /groups | findstr GG_FILE`, côté service desk via la fiche du compte.
3. Si le groupe attendu est présent : fermer la session Windows et la rouvrir (le jeton de groupes n'est mis à jour qu'à l'ouverture de session), puis retester.
4. Si le groupe est absent : ouvrir une demande sur `https://support.exemplia.local` > **Accès** > **Demande d'accès à un dossier partagé** avec le chemin, le niveau d'accès et la justification.
5. Le propriétaire du dossier valide ; l'équipe IAM ajoute le compte au groupe ; l'utilisateur ferme puis rouvre sa session.

### Lecteur réseau absent
1. Hors des locaux : se connecter au VPN Exemplia (KB-IT-004).
2. Ouvrir un terminal et exécuter `gpupdate /force`, puis fermer et rouvrir la session.
3. À défaut, monter le lecteur manuellement :
   ```cmd
   net use S: \\SRV-FILE-01\Services /persistent:yes
   ```
4. Vérifier l'accès en ouvrant `\\SRV-FILE-01\Services` dans l'Explorateur de fichiers.

## Vérification
- Le dossier s'ouvre avec le niveau attendu (création d'un fichier test en modification, puis suppression de ce fichier).
- Le lecteur `S:` reste présent après un redémarrage.

## Quand escalader
- Propriétaire du dossier introuvable : validation par le manager du demandeur, puis équipe IAM.
- Dossiers sensibles (RH, paie, direction, juridique) : double validation propriétaire et RSSI.
- `SRV-FILE-01` injoignable pour plusieurs utilisateurs : N2 Systèmes, priorité P2.
- Fichiers renommés avec une extension inconnue ou message de rançon : SOC immédiatement (KB-CY-006).
