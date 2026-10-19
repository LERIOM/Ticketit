---
id: KB-CY-001
title: "Force brute SSH sur un serveur exposé"
kind: fiche_cyber
category: bruteforce
priority_hint: P2
language: fr
version: "1.0"
updated: "2026-10-01"
author: "SOC Exemplia"
tags: [ssh, force brute, serveur exposé, linux, fail2ban]
mitre: ["T1110.001"]
graph:
  problemes:
    - id: P-ssh-bruteforce
      label: "Force brute SSH sur un serveur exposé"
      symptomes:
        - "alerte : plus de 50 échecs d'authentification SSH en 5 minutes sur SRV-WEB-01"
        - "Failed password for root from 203.0.113.45 port 52344 ssh2"
        - "nombreuses tentatives de connexion SSH avec des comptes inexistants"
        - "fail2ban bannit la même IP en boucle sur le serveur web"
      causes:
        - "port SSH exposé sur Internet"
        - "robot automatisé testant des listes de mots de passe courants"
      solutions:
        - id: S-ssh-blocage-ip
          label: "Bloquer temporairement l'IP source externe (24 h)"
          automatable: true
          action: block_ip
          action_target: ip
        - id: S-ssh-recherche-succes
          label: "Rechercher dans les journaux une connexion réussie depuis la même IP"
          automatable: true
          action: logs_search
          action_target: ip
      actifs: ["SRV-WEB-01"]
    - id: P-ssh-bruteforce-reussi
      label: "Connexion SSH réussie après une série d'échecs"
      symptomes:
        - "Accepted password depuis l'IP qui générait des échecs SSH"
        - "nouvelle session SSH inattendue sur SRV-WEB-01"
      causes:
        - "mot de passe faible ou par défaut sur un compte du serveur"
      solutions:
        - id: S-ssh-isolement-serveur
          label: "Isoler le serveur compromis du réseau (validation humaine)"
          automatable: false
          action: isolate_host
          action_target: hostname
        - id: S-ssh-analyse-session
          label: "Analyser les actions réalisées pendant la session suspecte"
          automatable: true
          action: logs_search
          action_target: hostname
      actifs: ["SRV-WEB-01"]
---

# Force brute SSH sur un serveur exposé (T1110.001)

## Contexte
`SRV-WEB-01` héberge le site public d'Exemplia et expose SSH pour l'équipe d'exploitation. Des robots y testent en continu des couples identifiant / mot de passe (MITRE ATT&CK T1110.001, Password Guessing). Sans connexion réussie, l'incident est P2 ; une connexion réussie le fait passer en P1.

## Indicateurs
- Plus de 20 lignes `Failed password` ou `Invalid user` depuis une même IP en moins de 5 minutes dans `/var/log/auth.log`.
- Identifiants génériques testés : `root`, `admin`, `test`, `ubuntu`, `oracle`.
- Alerte SIEM « SSH brute force » ou bannissements fail2ban répétés pour la même IP.
- Classement des IP sources : `grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head`

## Analyse (questions à se poser)
1. L'IP source est-elle externe (publique) ou interne (RFC 1918 : 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) ?
2. Existe-t-il une ligne `Accepted password` ou `Accepted publickey` pour cette IP (`grep "Accepted" /var/log/auth.log | grep <ip>`) ?
3. Les comptes visés existent-ils ? Un compte protégé (`admin`, `svc-backup`) est-il ciblé ?
4. D'autres serveurs reçoivent-ils les mêmes tentatives (campagne plus large) ?
5. L'IP appartient-elle à un prestataire ou à un test d'intrusion autorisé par le SOC ?

## Réponse
1. Rechercher toutes les connexions de l'IP source dans les journaux (`logs_search`, cible : IP).
2. IP externe sans connexion réussie : bloquer l'IP 24 heures (`block_ip`) et documenter le ticket.
3. IP interne : ne pas bloquer ; identifier le poste source et escalader au SOC (compromission interne possible, voir KB-CY-002).
4. Connexion réussie : demander l'isolement de `SRV-WEB-01` (`isolate_host`, validation humaine), puis analyser la session : `last -i`, historique shell, `crontab -l`, nouveaux fichiers dans `/tmp` et `/var/www`.
5. Recommander à l'équipe d'exploitation (action humaine, hors agent) : authentification par clé uniquement (`PasswordAuthentication no`), SSH accessible seulement via le VPN, fail2ban actif.

## Actions automatisables et niveau d'autorisation
| Action | Cible | Niveau | Conditions |
|---|---|---|---|
| `logs_search` | IP source, `SRV-WEB-01` | 0 | Automatique (lecture seule) |
| `block_ip` | IP externe | 1 | Automatique si confiance ≥ 0,80, durée 1 à 24 h ; jamais pour une IP interne |
| `isolate_host` | `SRV-WEB-01` | 2 | Toujours validée par un humain |
| Modifier la configuration SSH ou la politique du pare-feu | — | 3 | Interdit à l'agent |

## Quand escalader
- Connexion réussie depuis l'IP attaquante : escalade immédiate au SOC, priorité P1.
- IP source interne, ou tentatives visant un compte protégé (`admin`, `svc-backup`).
- Plus de 5 IP différentes en parallèle (attaque distribuée) : le blocage IP par IP ne suffit plus, le SOC adapte la protection.
