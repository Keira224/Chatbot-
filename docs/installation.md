# Installation - AcadReminder

## Prerequis

- Python 3.10 ou plus recent.
- `pip`.

## Installation Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_academic_events
python manage.py createsuperuser
python manage.py runserver
```

## Installation macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_academic_events
python manage.py createsuperuser
python manage.py runserver
```

## Acces

- Application : `http://127.0.0.1:8000/`
- Administration : `http://127.0.0.1:8000/admin/`
