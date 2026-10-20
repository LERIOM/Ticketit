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
Les mentions « à compléter » ci-dessous sont conservées comme historique.
Voir le complément daté « Réponses reçues d'Antoine » en fin de fichier :
F-Q1 à F-Q8 ont désormais une réponse proposée, parfois partielle, sans accord de Florent.

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

## Réponses reçues d'Antoine — 2026-10-20

**Consigné par l'agent de Florent**, à partir du message d'Antoine transmis par
Florent en pièce jointe (« Pasted text #1 », échange du 20 octobre 2026).
Synthèse du message, pas une transcription littérale. Les coordonnées et le fil
cité ne sont pas recopiés.

**État : réponse proposée pour F-Q1 à F-Q8 et A-Q2/A-Q3.**
Florent a autorisé l'enregistrement et les questions complémentaires, pas
l'adoption des règles proposées. Aucun « OK » fonctionnel n'est enregistré.
Le contrat OpenAPI et le code restent inchangés à cette étape.

### F-Q1 — Proposition de validation

- Six champs execute obligatoires ; champ absent ou mauvais type : 422,
  notamment params non objet.
- decision et approver obligatoires ; decision dans approve/reject.
- approver vide : 422, resserrement explicitement reconnu par Antoine.
  Les autres chaînes vides ne produisent pas de 422 selon sa proposition.
- request_id : UUID canonique 8-4-4-4-12, toute version ; l'engine génère du v4.
- confidence : nombre strict, fini, entre 0 et 1 inclus ; booléens, NaN et
  Infinity refusés en 422.
- Champs supplémentaires à la racine ignorés et non enregistrés.
- Tous les champs des réponses execute et du catalogue obligatoires ;
  result peut être null.

### F-Q2 — Proposition de validation métier

- Outil inconnu : niveau 3, 200/refused, avant les contrôles des paramètres.
- Paramètre manquant, mauvais type, hors bornes ou supplémentaire :
  200/refused avec niveau de l'outil et raison.
- logs_search : query chaîne et since_minutes entier, tous deux obligatoires.
- username et hostname : chaînes obligatoires ASCII.
- block_ip : ip et duration_hours obligatoires.
- Borne minimale de since_minutes, longueurs et formats complets non fournis.

### F-Q3 / A-Q3 — Résultats et réversibilité proposés

Les accolades suivantes décrivent les champs proposés, sans inventer de types
ou de valeurs que le message ne précise pas.

| Outil | Réversible | Résultat executed proposé | Annulation proposée |
| --- | --- | --- | --- |
| logs_search | false | count, hits ; maximum 50 hits, plus récents d'abord, count = total | Sans objet |
| account_info | false | username, active, must_change_password, protected | Sans objet |
| block_ip | true | ip, blocked_until | Échéance précédente ou absence de blocage (blocked_until null) |
| force_password_reset | true | username, must_change_password true | Ancienne valeur du drapeau |
| isolate_host | true | hostname, isolated true | Ancienne valeur du drapeau |
| disable_account | true | username, active false | Ancienne valeur du drapeau |

- L'état antérieur est capturé au moment de l'exécution, sans inversion systématique.
- block_ip conserve le maximum entre l'ancienne échéance et maintenant + durée.
- Dates UTC en ISO 8601 avec Z.
- result toujours présent et null pour refused, pending_approval et failed.
- undo_available true seulement si executed, outil réversible et entrée qui
  n'est pas elle-même une annulation.
- force_password_reset modifie uniquement un drapeau, sans générer de mot de passe.

### F-Q4 — Autorisation proposée

- Niveau 0 prioritaire pour account_info, même compte protégé ; protected true
  dans le résultat.
- Définition des IP publiques par liste explicite d'exclusion et liste protégée,
  sans is_private/is_global. La « liste ci-dessous » annoncée est absente du message.
- Un humain peut approuver une action sur une IP non publique/protégée ou sur
  un compte/poste protégé.
- L'interface prend toutes les actions pending_approval, niveau 1 compris.
- Seuil inclusif : 0.80 passe au seuil par défaut.

### F-Q5 / A-Q2 — Approbation proposée

- approve exécute sans revérifier le seuil ; executed, ou failed si cible inexistante.
- reject : refused, result null, undo_available false.
- audit_id inconnu : 200/refused, niveau 3 ; voir aussi F-Q6 pour l'UUID nul.
- Action non en attente ou décision répétée : 200/refused avec motif explicite.
- approver déclaré par l'interface ; seule la clé API est vérifiée en v1.
- request_id initial, nouvelle entrée d'audit pour la décision, nouvel audit_id.
  L'entrée en attente est conservée ; une annulation vise l'entrée de décision.

### F-Q6 — Annulation proposée

- audit_id inconnu : refused, UUID nul, aucune entrée d'audit.
- Refus si action non executed, outil non réversible, entrée d'annulation ou
  action déjà annulée ; création d'une entrée pour ces refus sur action connue.
- Restaurer seulement ce qui a été modifié. La note finale précise un refus
  lorsque l'état a changé ; la comparaison exacte et le cas d'expiration restent à définir.
- request_id initial, nouvel audit_id, approver null dans l'entrée d'audit.
- undo_of désigne l'audit visé, quel que soit le résultat, pour les cibles connues.

### F-Q7 — Idempotence proposée

- Conservation SQLite aussi longtemps que le labo, y compris après redémarrage.
  Le seed efface réponses, labo et audit ; le mock conserve en mémoire.
- Même identifiant avec contenu différent : réponse stockée et avertissement
  applicatif, sans exécution supplémentaire.
- Appels simultanés : une seule exécution ; le second attend la même réponse.
- Après approbation/annulation : execute rejoué renvoie la réponse initiale.
- Table d'idempotence séparée de l'audit, dont plusieurs entrées partagent request_id.

### F-Q8 — Audit et erreurs proposés

- ticket_id facultatif ; le contenu exact sans filtre reste non précisé.
- Premier execute : entrée avec request_id reçu, approver null et undo_of null.
- Execute rejoué : aucune nouvelle entrée.
- Approbation d'une action en attente : entrée avec request_id initial, approver
  déclaré, undo_of null ; executed/failed pour approve, refused pour reject.
- Approbation impossible sur action connue : entrée refused avec approver déclaré.
- Undo sur action connue : entrée avec request_id initial, approver null, undo_of visé,
  statut executed/refused/failed.
- Audit inconnu : aucune entrée.
- 401/422 : pas de corps imposé ; format FastAPI acceptable pour l'engine.
- Refus métier en 200 ; 5xx réservés aux pannes réelles.
- La rubrique « Lecture côté interface » est vide dans le message transmis.

### Corrections annoncées par Antoine pour son mock

Antoine annonce des corrections de classification IP (IPv4 mappées en IPv6,
adresse indéfinie, plage partagée, multicast), de casse des cibles protégées,
d'acceptation Unicode dans les identifiants, de confidence booléenne, de restauration
et contrôle d'état lors d'undo, de request_id lors d'undo/audit inconnu et de tri des logs.
Ces corrections sont annoncées, pas vérifiées comme réalisées par l'agent de Florent.

Les idées 404, 409, corps approver sur undo et authentification par analyste restent
explicitement hors v1 (« v2 ? »).

## Questions complémentaires après réception

**2026-10-20 — Agent de Florent.** Toutes les questions ci-dessous sont ouvertes.
Antoine peut ajouter une réponse datée sous chaque identifiant ; l'accord de Florent
reste à recueillir séparément.

### F-Q9 — UUID et resserrement approver

Le prompt indique uuid-v4, tandis que tu proposes toute version. Confirmer ensemble
la règle et sa qualification (clarification ou changement). Pour approver vide,
comment traiter ce resserrement avec notre règle de versionnement ?
La chaîne composée uniquement d'espaces est-elle concernée ?

### F-Q10 — Liste IP et normalisation

Peux-tu fournir la liste d'exclusion annoncée mais absente, les formats IPv4/IPv6
admis et le traitement des IPv4 mappées en IPv6 ? Préciser aussi la normalisation
des noms pour comparer les cibles protégées, puisque tu annonces une correction de casse.

### F-Q11 — Contraintes et résultats encore incomplets

Quelle borne minimale pour since_minutes ? Quels formats/longueurs et traitement
des chaînes vides dans les paramètres ? Quel schéma pour chaque élément de hits,
et quelle sémantique de recherche pour query ? Merci de distinguer contraintes
prévues et absence volontaire de contrainte.

### F-Q12 — Réponse complète pour audit inconnu

Peux-tu fournir le JSON complet pour approvals et undo sur audit inconnu,
notamment la valeur audit_id en l'absence de nouvelle entrée et la représentation
exacte de l'UUID nul ? Ne pas confondre UUID composé de zéros et valeur JSON null.

### F-Q13 — État modifié et résultats d'annulation

Quelle comparaison déclenche le refus si l'état a changé ? Comment traiter un
blocage expiré, un blocage prolongé ou une modification intermédiaire revenue à la
même valeur ? Quelle structure result renvoyer pour chaque annulation réussie ?

### F-Q14 — Audit sans filtre et réinitialisation

Que retourne audit sans ticket_id ? Préciser la lecture côté interface laissée vide.
Le seed qui efface l'audit est-il une exception explicitement réservée à la remise
à zéro du laboratoire, à distinguer de la règle d'audit en ajout seul ?

### F-Q15 — Accord fonctionnel de Florent

**À Florent :** après les compléments, confirmer ou contre-proposer les règles
reçues, notamment priorité du niveau 0, autorisation humaine sur cibles protégées,
réversibilité du reset, annulation et validation d'approver. L'autorisation de
consigner ce message n'est pas une acceptation de ces décisions.

### Journal complémentaire

- **2026-10-20 — Agent de Florent :** réponses reçues consignées sur autorisation
  de Florent ; F-Q9 à F-Q15 ajoutées. Aucun changement du contrat ou du service.
