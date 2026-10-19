---
id: KB-IT-012
title: "Installer un logiciel via le Portail d'entreprise"
kind: procedure
category: logiciel
priority_hint: P4
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [installation, portail d'entreprise, intune, catalogue, licence]
mitre: []
graph:
  problemes:
    - id: P-installation-logiciel
      label: "Installer un logiciel autorisé sans droits administrateur"
      symptomes:
        - "je dois installer un logiciel mais je n'ai pas les droits administrateur"
        - "Windows me demande un mot de passe administrateur pour installer"
        - "comment installer Power BI Desktop sur mon PC"
      causes:
        - "les utilisateurs ne sont pas administrateurs de leur poste"
      solutions:
        - id: S-portail-installation
          label: "Installer le logiciel depuis le Portail d'entreprise"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-installation-echec-portail
      label: "Installation en échec dans le Portail d'entreprise"
      symptomes:
        - "l'installation reste en attente dans le Portail d'entreprise"
        - "le Portail d'entreprise indique Échec de l'installation"
      causes:
        - "poste non synchronisé avec Intune"
        - "espace disque insuffisant ou redémarrage en attente"
      solutions:
        - id: S-portail-synchronisation
          label: "Synchroniser le poste avec Intune, redémarrer puis relancer l'installation"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-logiciel-hors-catalogue
      label: "Logiciel absent du catalogue"
      symptomes:
        - "le logiciel dont j'ai besoin n'est pas dans le Portail d'entreprise"
        - "j'ai besoin d'une licence pour un logiciel payant"
      causes:
        - "logiciel non référencé ou soumis à licence"
      solutions:
        - id: S-logiciel-demande-referencement
          label: "Demande de référencement validée par le manager et la sécurité"
          automatable: false
          action: null
          action_target: null
      actifs: []
---

# Installer un logiciel via le Portail d'entreprise

## Contexte
Les postes Exemplia sont gérés par Microsoft Intune. Les utilisateurs ne sont pas administrateurs : toute installation passe par l'application **Portail d'entreprise**, qui contient les logiciels validés par la DSI et la sécurité. Installer un logiciel téléchargé sur Internet est interdit par la charte informatique.

## Étapes
1. Ouvrir **Démarrer**, rechercher **Portail d'entreprise** et l'ouvrir (connexion automatique avec le compte Exemplia).
2. Onglet **Applications** : rechercher le logiciel par son nom.
3. Cliquer sur la fiche du logiciel puis sur **Installer** ; laisser le poste allumé et connecté (réseau interne ou VPN) pendant l'installation.
4. Le statut passe à **Installé** ; le logiciel apparaît dans le menu **Démarrer**.

### Installation en échec ou bloquée en attente
1. **Paramètres** > **Comptes** > **Accès Professionnel ou Scolaire** > compte Exemplia > **Informations** > **Synchroniser**.
2. Vérifier l'espace disque (au moins 10 Go libres, voir KB-IT-015) et les redémarrages en attente dans **Windows Update**.
3. Redémarrer le poste, rouvrir le Portail d'entreprise et cliquer sur **Réessayer**.

### Logiciel absent du catalogue
1. Ouvrir un ticket sur `https://support.exemplia.local` > **Logiciels** > **Demande de nouveau logiciel** en précisant le nom, l'éditeur, la version et le besoin métier.
2. Le manager valide le besoin et, pour un logiciel payant, le budget de licence.
3. La sécurité vérifie le logiciel (éditeur, données traitées, hébergement) ; le N2 Poste de travail l'ajoute ensuite au catalogue.
4. Délai indicatif : 5 à 10 jours ouvrés.

## Vérification
- Le Portail d'entreprise affiche **Installé** et le logiciel se lance sans message d'erreur.

## Quand escalader
- Échec persistant après synchronisation et redémarrage : N2 Poste de travail avec une capture du message d'erreur.
- Logiciel hors catalogue : workflow de validation manager et sécurité (aucune installation manuelle par le service desk).
- Demande d'accorder des droits administrateur locaux : refus par défaut, dérogation à demander au RSSI.
