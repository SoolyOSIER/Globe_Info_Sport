# Bilan Globe Info Sport — 24 septembre 2026

Référence principale : `files/comment.txt`. Ce document étend l'ancien plan
centré sur le football haïtien. Les changements préexistants dans le dépôt ont
été conservés. Ce bilan ne certifie pas une conformité complète aux 35 rubriques.

## Pages de rédaction réparées

- La migration `joueurs.0003_international_athletes` était absente de la base
  locale. Elle a été appliquée après sauvegarde dans
  `globeinfosport-backend/dev.before-international-athletes.sqlite3`.
- Les référentiels des formulaires parcourent toutes les pages de l'API : les
  clubs, athlètes, catégories et albums ne sont plus limités aux 20 ou 100 premiers.
- Les boutons de création, modification et suppression respectent les rôles
  exigés par le serveur. Un rédacteur peut consulter les catalogues réservés aux
  éditeurs sans se voir proposer une action qui échouerait systématiquement.
- Les comptes utilisent les véritables identifiants de rôles fournis par `/roles/`.
  Le mot de passe est obligatoire à la création et facultatif à la modification.
- Une page « Clubs des expatriés » permet de créer les clubs nécessaires aux
  fiches d'expatriés.
- Les dates de match sont adaptées au champ de saisie local puis envoyées avec
  fuseau horaire. Les résultats existants sont rechargés lors de leur réouverture.
- Les envois d'images conservent les listes vides, booléens et valeurs nulles :
  on peut réellement enlever des relations tout en changeant un logo.
- La suppression d'une référence encore utilisée renvoie un conflit explicite,
  et les erreurs de validation métier renvoient une réponse 400.
- L'éditeur suit la saisie immédiatement, protège la navigation avec un texte
  non enregistré, conserve ce texte lors d'un commentaire et affiche l'image
  choisie dans la prévisualisation.
- Les données en cache sont effacées au changement de compte. Le proxy local
  utilise la même origine que la rédaction. Le build Nginx prévoit `/redaction/`.

## Avancement par domaine

| Domaine du cahier des charges | État constaté |
| --- | --- |
| Architecture Django REST + deux applications React | Conservée et vérifiée par tests et compilations |
| Articles, catégories, sports, pays, clubs, compétitions, sélections | Modèles et API existants réutilisés ; filtres géographiques corrigés |
| Athlètes internationaux | Sport et pays ajoutés ; poste de football facultatif ; anciennes fiches à compléter manuellement |
| Workflow rédactionnel | Brouillon, soumission, publication, programmation, archive, commentaires et historique existants ; retour en brouillon ajouté |
| Éditeur riche | Mise en forme et prévisualisation présentes ; repose encore sur `contentEditable` / `execCommand` ; pas de restauration complète de version ni d'édition collaborative |
| Haïti et International | Pages présentes ; recherches des clubs, compétitions, sélections et athlètes reliées aux filtres ; un article associé à Haïti et un autre pays peut apparaître dans les deux zones |
| Recherche | Articles et répertoires sportifs consultables ; pas encore de moteur global classant ensemble tous les types de contenus |
| Page article | Tags, auteur, galerie, partage, navigation précédent/suivant, vidéos YouTube intégrées |
| Matchs et résultats | Calendrier, scores, buteurs et classement présents ; moteur statistique toujours principalement football |
| Globe Info Sport TV | Sélection manuelle de vidéos et liens vers la chaîne ; pas de récupération automatique validée de toute la chaîne |
| Réseaux sociaux sources | Facebook et YouTube inaccessibles depuis l'outil de consultation ; aucune analyse exhaustive ou import de leurs publications n'est revendiqué |
| Administration | Ressources éditoriales présentes ; régie publicitaire et paramètres globaux complets non réalisés |
| SEO | Balises existantes, sitemap paginé et robots.txt ajoutés ; rendu serveur des métadonnées pour tous les robots sociaux non réalisé |
| Mobile | Navigation et styles responsives présents ; contrôle navigateur ciblé, pas de certification de tous les appareils |
| Newsletter | Inscription, désabonnement et liste de gestion existants ; préférences par sport non réalisées |
| Notifications / monétisation | Mentions de contenu sponsorisé existantes ; notifications personnalisées, abonnements payants et régie publicitaire restent à développer |
| Performance | Pagination API, chargement différé de pages et images présents ; pas d'audit de charge ou de mesure Lighthouse réalisé |

## Vérifications

- 26 tests Django : workflow, confidentialité, filtres, athlètes, sitemap,
  accès aux collections éditoriales, permissions, rôles, multipart et conflits.
- 4 tests JavaScript des transformations de formulaires.
- 6 parcours Edge réussis avec une API réelle et une base isolée : ouverture de 20 pages,
  formulaires, édition et soumission d'article, commentaires, comptes, pagination
  des références, séparation des rôles, réouverture des résultats et navigation mobile.
- Compilations de la rédaction et de la vitrine réussies. Contrôles Django et migrations sans anomalie.
- Lecture de 15 collections API sur la base locale : toutes répondent HTTP 200.
- Les tests navigateur créent une base `e2e-*.sqlite3` distincte de `dev.sqlite3`.
  Aucun contenu utilisateur n'est utilisé pour les créations de test.

## Utilisation

Depuis la racine, `./scripts/start-local.ps1` applique les migrations puis lance
les services. Après des changements de code backend, relancer l'API est nécessaire
car le script utilise `--noreload`.

Les tests de rédaction se lancent dans `globeinfosport-redaction` :

```powershell
npm test
npm run test:e2e
```

Les tests navigateur nécessitent Edge installé et les ports 8011 et 5177 libres.
La configuration Python du test est adaptée à l'environnement Windows du dépôt.

En production, renseigner `PUBLIC_SITE_URL` et `VITE_SITE_URL` avec l'origine
publique, configurer les services PostgreSQL/Redis/Celery et la clé du fournisseur
sportif. La programmation automatique demande un processus Celery Beat actif ;
en local, `manage.py publish_scheduled` exécute les publications arrivées à échéance.

Les clubs initialisés par l'ancien script `seed_editorial` n'ont pas fait l'objet
d'une vérification externe de leur appartenance actuelle aux championnats.
