<#!
.SYNOPSIS
    Démarre l'API, la vitrine et le back-office en développement Windows.

.DESCRIPTION
    Cette commande utilise SQLite et les tâches Celery synchrones pour pouvoir
    lancer la plateforme sans Docker, PostgreSQL ni Redis installés localement.
    Les fichiers de production restent configurés pour PostgreSQL et Redis.
#>

$projectRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $projectRoot "globeinfosport-backend"
$redaction = Join-Path $projectRoot "globeinfosport-redaction"
$vitrine = Join-Path $projectRoot "globeinfosport-vitrine"
$python = Join-Path $backend ".venv312\Scripts\python.exe"
$databasePath = (Join-Path $backend "dev.sqlite3").Replace("\", "/")

if (-not (Test-Path $python)) {
    throw "Environnement Python absent : $python. Installez les dépendances du backend avant de lancer ce script."
}

$env:DATABASE_URL = "sqlite:///$databasePath"
$env:CELERY_TASK_ALWAYS_EAGER = "True"
$env:DEBUG = "True"

Push-Location $backend
try {
    & $python manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw "Les migrations Django ont échoué." }
} finally {
    Pop-Location
}

# Les enfants héritent des variables d'environnement du processus courant.
Start-Process -FilePath $python -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" -WorkingDirectory $backend -WindowStyle Hidden
Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173" -WorkingDirectory $redaction -WindowStyle Hidden
Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5174" -WorkingDirectory $vitrine -WindowStyle Hidden

Write-Host "API       : http://127.0.0.1:8000/api/v1/docs/"
Write-Host "Rédaction : http://127.0.0.1:5173/"
Write-Host "Vitrine  : http://127.0.0.1:5174/"
