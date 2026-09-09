#!/usr/bin/env python
"""Raccourci de développement pour les commandes Django du monorepo.

Le vrai projet Django vit dans ``globeinfosport-backend``. Ce fichier permet
néanmoins d'exécuter naturellement ``python manage.py runserver`` depuis la
racine et délègue toujours au virtualenv Python 3.12 configuré pour le projet.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "globeinfosport-backend"
BACKEND_MANAGE = BACKEND_DIR / "manage.py"
BACKEND_PYTHON = BACKEND_DIR / ".venv312" / "Scripts" / "python.exe"


def main() -> None:
    if not BACKEND_MANAGE.is_file():
        raise SystemExit("Projet Django introuvable : globeinfosport-backend/manage.py")
    if not BACKEND_PYTHON.is_file():
        raise SystemExit(
            "Environnement Django introuvable : "
            "globeinfosport-backend/.venv312/Scripts/python.exe"
        )

    # Les conteneurs et les intégrations CI peuvent fournir leur propre base.
    # Ces valeurs ne sont donc appliquées qu'au démarrage local direct.
    database = (BACKEND_DIR / "dev.sqlite3").as_posix()
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{database}")
    os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "True")
    os.environ.setdefault("DEBUG", "True")

    result = subprocess.run(
        [str(BACKEND_PYTHON), str(BACKEND_MANAGE), *sys.argv[1:]],
        cwd=BACKEND_DIR,
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
