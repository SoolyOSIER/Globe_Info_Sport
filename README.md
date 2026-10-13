# Globe Info Sport

Plateforme média sportive internationale, avec une place particulière pour Haïti : API Django REST, back-office React et
site vitrine React. La stack de production est PostgreSQL, Redis, Celery et
Nginx ; un démarrage Windows sans Docker est également fourni.

## Démarrage local Windows

Les dépendances Python (dans `globeinfosport-backend/.venv312`) et JavaScript
des deux SPA doivent être installées une première fois. Ensuite, depuis la
racine du dépôt :

```powershell
.\scripts\start-local.ps1
```

Pour ne lancer que Django depuis la racine, cette commande est aussi valable :

```powershell
python manage.py runserver
```

Le script applique les migrations sur `dev.sqlite3`, puis démarre :

- API et documentation : `http://127.0.0.1:8000/api/v1/docs/`
- Back-office : `http://127.0.0.1:5173/`
- Vitrine : `http://127.0.0.1:5174/`

Il initialise aussi les sports, pays et types de contenus. En production,
exécutez une fois `python manage.py seed_editorial` après les migrations.

Les articles programmés sont publiés chaque minute par Celery Beat en
production. Pour vérifier une échéance dans l'environnement local, utilisez :

```powershell
cd globeinfosport-backend
.\.venv312\Scripts\python.exe manage.py publish_scheduled
```

## Classements et calendriers automatiques

Les cinq grands championnats de football — Premier League, Liga, Serie A,
Bundesliga et Ligue 1 — sont préparés par `seed_editorial`. Le connecteur
football-data.org actualise leurs équipes, calendrier, résultats et classement.

Créez une clé auprès du fournisseur puis définissez-la sans la committer :

```powershell
$env:FOOTBALL_DATA_API_TOKEN = 'votre-cle-api'
```

Dans Docker ou en production, ajoutez cette variable à `.env`. Les éditeurs en
chef peuvent ensuite utiliser **Compétitions → Synchroniser maintenant**. Celery
Beat effectue aussi cette synchronisation toutes les 30 minutes lorsqu'une clé
est configurée. Pour une exécution ponctuelle :

```powershell
cd globeinfosport-backend
.\.venv312\Scripts\python.exe manage.py synchroniser_football_data
```

Le fournisseur et la date de dernière synchronisation sont exposés avec chaque
compétition afin de distinguer les données importées des contenus rédigés.

Créer les rôles et un administrateur de développement :

```powershell
cd globeinfosport-backend
$env:DATABASE_URL = 'sqlite:///C:/Users/storl/Music/Globe_Info_Sport/globeinfosport-backend/dev.sqlite3'
.\.venv312\Scripts\python.exe manage.py create_roles
.\.venv312\Scripts\python.exe manage.py create_admin --identifiant admin --nom Administrateur --password 'ChangeMe123!'
```

Changez immédiatement ce mot de passe dès que l'environnement est partagé.

## Vérifications

```powershell
cd globeinfosport-backend
.\.venv312\Scripts\python.exe manage.py check
.\.venv312\Scripts\python.exe manage.py test apps.core apps.actualites apps.competitions

cd ..\globeinfosport-redaction
npm run build
cd ..\globeinfosport-vitrine
npm run build
```

## Docker

Après avoir renseigné un fichier `.env` à partir de `.env.example` :

```powershell
docker compose up --build
```

Pour la configuration de production avec Nginx :

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

## Audit du cahier des charges

Consultez [le bilan fonctionnel](files/AUDIT_IMPLEMENTATION.md) pour les
fonctions existantes, les corrections et les limites restant à traiter.

La migration `joueurs/0003_international_athletes` ajoute le sport et le pays
aux athlètes et rend le poste facultatif. Elle conserve les fiches existantes ;
leurs sports et pays doivent être complétés par la rédaction.

Le sitemap dynamique et robots.txt sont disponibles à la racine de la vitrine
via Nginx ou le proxy Vite local. Configurez `PUBLIC_SITE_URL` dans le backend
avec le domaine public de production, et la même origine dans `VITE_SITE_URL`.
Les brouillons, archives et publications futures sont exclus du sitemap.

Tests des formulaires et parcours navigateur (Edge, base de test isolee) :

```powershell
cd globeinfosport-redaction
npm test
npm run test:e2e
```

La redaction utilise `/api/v1` via le proxy Vite en local. Apres modification
du backend, relancez Django si celui-ci fonctionne avec `--noreload`.
