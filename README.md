# Globe Info Sport

Plateforme média sportive haïtienne : API Django REST, back-office React et
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
.\.venv312\Scripts\python.exe manage.py test apps.competitions

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
