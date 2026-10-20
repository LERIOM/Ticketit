# Communication Florent ↔ Antoine

Canal partagé créé le 2026-10-20 à la demande de Florent pour poser des questions
et y répondre via GitHub. Suivis personnels : [Florent.md](Florent.md) et
[Antoine.md](Antoine.md).

## Fonctionnement

- Les deux participants et leurs agents peuvent ajouter ici leurs questions et réponses.
  Cette autorisation concerne ce fichier commun ; chacun conserve son fichier personnel.
- Lire les nouveaux échanges au début de chaque séance et récupérer les changements distants
  avant publication pour préserver les contributions de l'autre.
- Conserver les identifiants : `F-Qn` pour Florent, `A-Qn` pour Antoine.
- Signer chaque réponse avec la date et l'auteur (humain ou agent). Ne pas réécrire la
  contribution de l'autre ; ajouter une correction ou un complément daté.
- États : ouverte, réponse proposée, accord confirmé. Une proposition n'est pas un accord.
- Une modification d'une règle figée exige l'accord des deux et le passage en v2 prévu
  par les prompts. La validation OpenAPI ne remplace pas cet accord.
- Mettre à jour le suivi personnel, puis committer et pousser les échanges terminés.
  Ce fichier ne déclenche pas de notification ni de réponse automatique de l'autre agent.

## Contexte à relire ensemble

**2026-10-20 — Agent de Florent :** les sections de contrat des deux prompts dans
[docs/](docs/) sont identiques. Le [contrat OpenAPI](contracts/executor_v1.openapi.yaml)
passe PyYAML et openapi-spec-validator. Le commit `421323d` documente les ambiguïtés,
mais retire également des contraintes de validation initiales (`required`, bornes de
`confidence`). Il faut revoir ces différences ensemble avant de considérer ce document
comme une référence d'intégration approuvée. Aucun accord d'Antoine n'est présumé.

## Demandes existantes d'Antoine

### A-Q1 — Répartition des tâches

**Source :** [Antoine.md](Antoine.md). Les prompts priment-ils sur la répartition du PDF ?

**2026-10-20 — Agent de Florent :** le périmètre demandé par Florent suit les prompts :
executor côté Florent ; masquage PII, API engine et Streamlit côté Antoine.
**État :** réponse fournie sur le périmètre demandé.

### A-Q2 — Rejet, annulation et outil inconnu

**Source :** Antoine propose reject → refused, undo → nouvelle entrée d'audit,
outil inconnu → niveau 3.

**2026-10-20 — Agent de Florent :** outil inconnu → niveau 3, HTTP 200 et refused
est explicite dans les prompts. Les deux autres comportements sont des propositions
d'Antoine, à confirmer ensemble ; voir F-Q5 et F-Q6.
**État :** réponse partielle ; accord restant à confirmer.

### A-Q3 — Résultats des six outils

**2026-10-20 — Agent de Florent :** seul l'exemple block_ip
`{"blocked_until":"2026-11-03T14:00:00Z"}` figure dans le contrat.
Merci de proposer les structures déjà utilisées par le mock pour comparaison.
Les autres formes ne sont pas encore convenues ; voir F-Q3.
**État :** ouverte.

### A-Q4 — Créneau d'annotation commun

**2026-10-20 — Agent de Florent :** Florent doit fournir ses disponibilités pour
l'annotation des quelque 300 tickets, dont 30 piégés. Aucun créneau n'est fixé.
**Réponse de Florent / Antoine :** à compléter.
**État :** ouverte.

## Questions de Florent à Antoine

Les questions suivantes ont été préparées par l'agent de Florent le 2026-10-20.

### F-Q1 — Champs et validation HTTP

- Les six champs de execute sont-ils tous obligatoires ?
- decision et approver sont-ils tous deux obligatoires pour approvals ?
- request_id doit-il être strictement UUID v4, avec 422 sinon ?
- confidence est-elle bornée à [0, 1] ?
- Champs supplémentaires : acceptés, ignorés ou rejetés ? Chaînes vides autorisées ?
- Confirmer la liste des champs obligatoires des réponses execute et du catalogue.
- Revoir explicitement les contraintes retirées par le commit 421323d.

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q2 — Paramètres des outils

- logs_search : query chaîne et since_minutes entier ? Tous deux obligatoires ?
  Quelle borne minimale (maximum 1440 déjà fixé) ?
- username et hostname : chaînes obligatoires ? Formats, longueurs et caractères permis ?
- query : quelles contraintes ?
- block_ip : IPv4, IPv6 et quels formats autorisés ?
- Les paramètres supplémentaires d'un outil provoquent-ils 200/refused ?

Les erreurs propres aux paramètres d'un outil restent des refus métier HTTP 200,
distincts du 422 pour une requête non conforme au schéma.

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q3 — Réversibilité et résultats

- Quelle réversibilité pour logs_search, account_info, force_password_reset,
  isolate_host et disable_account ? Seul block_ip est explicitement réversible.
- Quel état restaurer lors d'une annulation ?
- Quelle structure result par outil, et pour refused, pending_approval et failed :
  objet, null ou autre ?
- Dans quels cas undo_available vaut-il true ?

Antoine indique que son moteur affiche result sans l'interpréter pour autoriser une action.
Cela ne fixe pas encore les structures communes avec le mock (A-Q3).

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q4 — Priorité des règles d'autorisation

- account_info sur un compte protégé : niveau 0 toujours exécuté ou cible protégée
  toujours pending_approval ?
- Comment traiter les IP de documentation 203.0.113.5 et 198.51.100.23 des scénarios
  au regard de l'exigence d'IP publique ?
- Une approbation humaine peut-elle autoriser les actions sur les IP privées,
  de bouclage ou protégées, et sur les comptes/postes protégés ?
- L'interface prendra-t-elle toutes les actions pending_approval, y compris niveau 1,
  malgré la mention du seul niveau 2 dans sa description ?

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q5 — Approbation humaine

- Confirmer la proposition d'Antoine reject → refused.
- Quel comportement si audit_id est inconnu, l'action n'est plus en attente,
  ou la décision a déjà été envoyée ?
- approver est-il une identité déclarée par l'interface ou doit-il être vérifié autrement ?
- Quel request_id et quel audit_id dans la réponse : ceux d'origine ou une nouvelle entrée ?

**Réponse d'Antoine :** à compléter (proposition initiale en A-Q2).
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q6 — Annulation

- Quel comportement pour audit_id inconnu, action non exécutée ou déjà annulée ?
- Que faire si l'état a changé entre-temps, par exemple blocage IP expiré ?
- Confirmer la proposition d'Antoine : nouvelle entrée d'audit et nouvel audit_id,
  undo_of pointant vers l'entrée annulée.
- Quel request_id renvoyer ?

**Réponse d'Antoine :** à compléter (proposition initiale en A-Q2).
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q7 — Idempotence

- Durée de conservation et persistance après redémarrage ?
- Même request_id avec un contenu différent : comportement exact ?
- Confirmer l'unicité d'exécution pour deux appels simultanés.
- Après approbation ou annulation, un nouvel execute avec le même request_id
  renvoie-t-il toujours la réponse initiale ?

La garantie déjà fixée reste : même request_id, même réponse, sans deuxième exécution.

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

### F-Q8 — Audit et erreurs

- ticket_id est-il obligatoire pour GET /audit ? Sinon, réponse sans filtre ?
- Quelles entrées append-only ajouter lors d'une approbation, d'un rejet et d'une annulation ?
- Quel corps pour 401 et 422 ? Le format standard FastAPI convient-il ?
- Quels statuts et codes HTTP pour les cas non définis en F-Q5/F-Q6, sans inventer
  un nouveau code unilatéralement ?

**Réponse d'Antoine :** à compléter.
**Accord de Florent :** à compléter.
**État :** ouverte.

## Nouvelles questions d'Antoine

Ajouter ici A-Q5 et les suivantes avec date, auteur, question, réponse et état.

## Journal des échanges

- **2026-10-20 — Agent de Florent :** création du canal à la demande de Florent ;
  reprise des demandes existantes, réponses partielles et questions de clarification.
