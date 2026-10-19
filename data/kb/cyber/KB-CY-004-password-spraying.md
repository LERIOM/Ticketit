---
id: KB-CY-004
title: "Password spraying sur les comptes de l'entreprise"
kind: fiche_cyber
category: bruteforce
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [password spraying, force brute, entra id, active directory, verrouillage]
mitre: ["T1110.003"]
graph:
  problemes:
    - id: P-password-spraying
      label: "Password spraying sur de nombreux comptes"
      symptomes:
        - "alerte : échecs de connexion sur 150 comptes différents depuis la même IP"
        - "plusieurs utilisateurs signalent un compte verrouillé au même moment"
        - "Entra ID : pic d'erreurs 50126 (identifiants invalides) sur de nombreux comptes"
      causes:
        - "attaquant testant un mot de passe courant sur tous les comptes"
        - "liste d'adresses e-mail collectée publiquement"
      solutions:
        - id: S-spray-blocage-ip
          label: "Bloquer temporairement l'IP source externe (24 h)"
          automatable: true
          action: block_ip
          action_target: ip
        - id: S-spray-analyse-comptes
          label: "Lister les comptes visés et les éventuelles connexions réussies depuis l'IP"
          automatable: true
          action: logs_search
          action_target: ip
      actifs: ["DC-01"]
    - id: P-spray-compte-compromis
      label: "Compte connecté avec succès pendant un password spraying"
      symptomes:
        - "connexion réussie sur un compte au milieu d'une vague d'échecs"
        - "un des comptes visés s'est connecté depuis l'IP attaquante"
      causes:
        - "mot de passe faible ou prévisible"
      solutions:
        - id: S-spray-reset-compte
          label: "Forcer la réinitialisation du mot de passe du compte compromis"
          automatable: true
          action: force_password_reset
          action_target: username
        - id: S-spray-desactivation-compte
          label: "Désactiver le compte en cas d'activité malveillante (validation humaine)"
          automatable: false
          action: disable_account
          action_target: username
      actifs: []
---

# Password spraying sur les comptes de l'entreprise (T1110.003)

## Contexte
Le password spraying (MITRE ATT&CK T1110.003) consiste à tester un ou deux mots de passe courants (par exemple une saison suivie de l'année) sur un grand nombre de comptes, pour rester sous le seuil de verrouillage. Les cibles sont Microsoft 365 (Entra ID), le VPN Exemplia et les services exposés. Contrairement à la force brute classique, chaque compte ne subit que peu d'échecs.

## Indicateurs
- Une même IP (ou un petit groupe d'IP) génère des échecs sur des dizaines de comptes différents en peu de temps.
- 1 à 3 échecs par compte, souvent dans l'ordre alphabétique de l'annuaire.
- Événements 4625 (sous-statut `0xC000006A`) ou 4771 sur `DC-01`, erreurs 50126 dans les journaux Entra ID.
- Comptes inexistants testés (anciens salariés, formats d'identifiant erronés).
- Vague simultanée de verrouillages de comptes (KB-IT-002).

## Analyse (questions à se poser)
1. Combien de comptes ont été testés, depuis quelles IP, sur quel service (Microsoft 365, VPN, OWA) ?
2. Au moins une connexion a-t-elle réussi depuis ces IP ? Avec ou sans MFA validée ?
3. Les IP sont-elles externes ? Un service interne mal configuré (ancien mot de passe) peut-il expliquer les échecs ?
4. Des comptes protégés (`admin`, `svc-backup`) figurent-ils parmi les cibles ?

## Réponse
1. Lister les comptes visés et les succès éventuels (`logs_search`, cible : IP).
2. IP externe : bloquer chaque IP source 24 heures (`block_ip`).
3. Pour chaque compte connecté avec succès : forcer la réinitialisation du mot de passe (`force_password_reset`) et vérifier ses connexions (voir KB-CY-009).
4. Activité malveillante constatée après la connexion (mails envoyés, fichiers téléchargés) : demander la désactivation du compte (`disable_account`, validation humaine).
5. Vérifier que tous les comptes visés ont bien une MFA enregistrée ; signaler au SOC ceux qui n'en ont pas.
6. Recommandations (actions humaines) : renforcer la liste de mots de passe interdits, revoir les accès hérités sans MFA.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | IP source, comptes | 0 | Automatique (lecture seule) |
| `block_ip` | IP externe | 1 | Automatique si confiance ≥ 0,80, 1 à 24 h ; jamais pour une IP RFC 1918 |
| `force_password_reset` | Compte compromis | 1 | Automatique si confiance ≥ 0,80 et compte non protégé ; sinon validation humaine |
| `disable_account` | Compte compromis | 2 | Toujours validée par un humain |
| Modifier la stratégie de mots de passe ou du pare-feu | — | 3 | Interdit à l'agent |

## Quand escalader
- Au moins une connexion réussie : SOC, priorité P1.
- Compte protégé ciblé ou attaque provenant d'une IP interne : SOC, aucune action automatique.
- Plus de 10 IP sources ou attaque durable : le SOC met en place une protection globale (accès conditionnel, géoblocage).
