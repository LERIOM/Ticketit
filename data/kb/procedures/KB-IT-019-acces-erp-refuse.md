---
id: KB-IT-019
title: "Accès refusé ou connexion impossible à l'ERP"
kind: procedure
category: acces_compte
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [erp, application métier, habilitation, droits, séparation des tâches]
mitre: []
graph:
  problemes:
    - id: P-erp-acces-refuse
      label: "Accès refusé à une fonction de l'ERP"
      symptomes:
        - "l'ERP m'affiche accès refusé sur le module achats"
        - "je ne vois pas le menu de validation des factures dans l'ERP"
        - "erreur AUTH-403 : autorisation insuffisante"
      causes:
        - "rôle ERP non attribué ou retiré lors d'un changement de poste"
        - "habilitation temporaire arrivée à échéance"
      solutions:
        - id: S-erp-verif-roles
          label: "Vérifier les groupes et rôles ERP du compte"
          automatable: true
          action: account_info
          action_target: username
        - id: S-erp-demande-habilitation
          label: "Demande d'habilitation validée par le manager et le propriétaire applicatif"
          automatable: false
          action: null
          action_target: null
      actifs: []
    - id: P-erp-connexion-impossible
      label: "Connexion impossible à l'ERP"
      symptomes:
        - "l'ERP ne me laisse pas me connecter"
        - "la page de connexion de l'ERP tourne en boucle"
      causes:
        - "mot de passe expiré ou compte verrouillé"
        - "VPN non connecté hors des locaux"
        - "cache du navigateur corrompu"
      solutions:
        - id: S-erp-diagnostic-connexion
          label: "Vérifier le VPN, l'état du compte et vider le cache du navigateur"
          automatable: true
          action: null
          action_target: null
      actifs: []
---

# Accès refusé ou connexion impossible à l'ERP

## Contexte
L'ERP d'Exemplia (finance, achats, ventes, stocks) est accessible depuis le navigateur à l'adresse `https://erp.exemplia.local`, uniquement depuis le réseau interne ou le VPN. La connexion utilise le compte `exemplia.local`. Les droits sont des **rôles métier** attribués par habilitation : chaque rôle est validé par le manager et par le propriétaire applicatif du module (par exemple le contrôle de gestion pour la finance). Le service desk ne peut pas attribuer un rôle lui-même.

## Étapes
### Connexion impossible
1. Hors des locaux : vérifier que le VPN Exemplia est connecté (KB-IT-004).
2. Vérifier que le mot de passe n'a pas expiré et que le compte n'est pas verrouillé (KB-IT-001, KB-IT-002).
3. Ouvrir l'ERP dans une fenêtre de navigation privée (`Ctrl + Maj + N` dans Edge) : si cela fonctionne, vider le cache (**Paramètres** > **Confidentialité, recherche et services** > **Effacer les données de navigation**, cookies et images en cache).
4. Utiliser Microsoft Edge, seul navigateur supporté par l'ERP.

### Accès refusé à une fonction
1. Relever le message exact, le code d'erreur (par exemple `AUTH-403`), le module et la transaction concernés.
2. Vérifier les rôles du compte : un changement de poste récent entraîne le retrait des anciens rôles.
3. Ouvrir une demande sur `https://support.exemplia.local` > **Applications** > **Demande d'habilitation ERP** en indiquant le rôle souhaité et la justification.
4. Circuit de validation : manager, puis propriétaire applicatif du module ; l'équipe IAM applique le rôle (délai indicatif 2 jours ouvrés).
5. Après attribution : se déconnecter de l'ERP et se reconnecter.

### Séparation des tâches
Certains rôles sont incompatibles (par exemple création de fournisseur et validation de paiement). Une demande qui créerait un conflit est refusée automatiquement, sauf dérogation écrite du directeur financier.

## Vérification
- L'utilisateur accède à la fonction demandée et le code `AUTH-403` ne réapparaît plus.

## Quand escalader
- Demande de rôle : toujours via le circuit de validation, jamais d'attribution directe par le N1.
- ERP indisponible pour plusieurs utilisateurs : N2 Applications métier, priorité P2 (P1 en période de clôture comptable).
- Accès ou modifications dans l'ERP que l'utilisateur ne reconnaît pas : SOC (KB-CY-009).
