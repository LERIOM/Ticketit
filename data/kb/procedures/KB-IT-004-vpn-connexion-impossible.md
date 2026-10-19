---
id: KB-IT-004
title: "Le VPN Exemplia ne se connecte pas"
kind: procedure
category: reseau
priority_hint: P3
language: fr
version: "1.0"
updated: "2026-10-01"
author: "Service desk Exemplia"
tags: [vpn, forticlient, télétravail, connexion]
mitre: []
graph:
  problemes:
    - id: P-vpn-connexion-impossible
      label: "Le VPN Exemplia ne se connecte pas"
      symptomes:
        - "le VPN Exemplia reste bloqué à 98 % puis échoue"
        - "erreur -14 : impossible d'établir la connexion VPN"
        - "pas de VPN donc pas d'accès aux lecteurs réseau en télétravail"
        - "FortiClient tourne en boucle sans se connecter"
      causes:
        - "pas d'accès Internet ou réseau filtrant (hôtel, Wi-Fi public)"
        - "client FortiClient endommagé ou obsolète"
        - "adaptateur réseau virtuel du VPN désactivé"
      solutions:
        - id: S-vpn-diagnostic-base
          label: "Diagnostic de base : Internet, redémarrage du client, autre réseau"
          automatable: true
          action: null
          action_target: null
        - id: S-vpn-reinstallation-client
          label: "Réinstaller FortiClient depuis le Portail d'entreprise"
          automatable: true
          action: null
          action_target: null
      actifs: []
    - id: P-vpn-identifiants-refuses
      label: "Identifiants refusés par le VPN"
      symptomes:
        - "erreur -7200 : Credential or SSLVPN configuration is wrong"
        - "le VPN refuse mon mot de passe alors qu'il fonctionne sur mon PC"
      causes:
        - "mot de passe expiré ou modifié récemment"
        - "compte verrouillé"
        - "notification MFA non validée à temps"
      solutions:
        - id: S-vpn-verif-compte
          label: "Vérifier l'état du compte (expiration, verrouillage)"
          automatable: true
          action: account_info
          action_target: username
      actifs: []
---

# Le VPN Exemplia ne se connecte pas

## Contexte
Le client **VPN Exemplia** (FortiClient) donne accès au réseau interne depuis l'extérieur : lecteurs réseau, ERP, imprimantes. L'authentification utilise le compte `exemplia.local` et une validation Microsoft Authenticator. Microsoft 365 (Outlook, Teams, OneDrive) fonctionne sans VPN.

## Étapes
1. Vérifier l'accès Internet : ouvrir `https://www.microsoft.com`. Si un portail captif (hôtel, gare) s'affiche, l'accepter d'abord.
2. Fermer complètement FortiClient (clic droit sur l'icône de la zone de notification > **Arrêter FortiClient**), le relancer et retenter la connexion.
3. Vérifier que le profil sélectionné est bien **VPN Exemplia** et que l'identifiant est au format `prenom.nom`.
4. Valider la notification Authenticator dans les 60 secondes.
5. Tester la joignabilité de la passerelle (adresse affichée dans le profil) :
   ```powershell
   Test-NetConnection <passerelle-vpn> -Port 443
   ```
   `TcpTestSucceeded : False` indique un réseau qui bloque le VPN : tester en partage de connexion 4G/5G.
6. Bloqué à 98 % : **Paramètres** > **Réseau et Internet** > **Paramètres réseau avancés**, vérifier que l'adaptateur **Fortinet SSL VPN Virtual Ethernet Adapter** est activé, puis redémarrer le poste.
7. Si l'échec persiste : **Démarrer** > **Portail d'entreprise** > **FortiClient VPN** > **Réinstaller**, puis redémarrer.

### Erreur -7200 (identifiants refusés)
1. Vérifier que le mot de passe n'a pas expiré et que le compte n'est pas verrouillé (KB-IT-001, KB-IT-002).
2. Après un changement de mot de passe, ressaisir le mot de passe dans FortiClient (ne pas utiliser l'enregistrement automatique).

## Vérification
- FortiClient affiche **Connecté** et une adresse IP du réseau Exemplia.
- Le lecteur réseau `S:` est accessible dans l'Explorateur de fichiers.

## Quand escalader
- Plusieurs utilisateurs signalent le même problème au même moment : incident sur la passerelle, escalade N2 Réseau en P2.
- Réinstallation faite, réseau 4G testé, échec persistant : N2 Réseau avec captures d'écran et heure des tentatives.
- Connexions VPN depuis un pays inhabituel ou non reconnues par l'utilisateur : SOC (KB-CY-009).
