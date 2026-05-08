# Habit Tracker

Aplicación web para registrar hábitos diarios con Django. Panel mensual interactivo, rachas, toggle EN/ES y diseño dark.

## Funcionalidades

- Registro e inicio de sesión con mensajes de error en español
- Crear, editar y eliminar hábitos (diarios/semanales)
- Check instantáneo con AJAX (sin recargar la página)
- Calendario mensual con puntitos de colores por hábito
- Barra de progreso de 31 días por hábito
- Rachas actuales con indicador visual
- Filtro por mes (2026)
- Toggle de idioma español/inglés
- Diseño responsive dark con Tailwind CSS

## Inicio rápido

```bash
cd habit_tracker
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visitar `http://127.0.0.1:8000`

## Deploy en Render (gratis)

1. Subir el repo a GitHub
2. En Render, crear **New Web Service** y conectar el repo
3. **Build Command:** `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
4. **Start Command:** `gunicorn habit_tracker.wsgi`
5. Variables de entorno:
   - `DJANGO_SECRET_KEY`: generar con `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://tu-app.onrender.com`
   - `DATABASE_URL`: (opcional) URL de PostgreSQL en Render

## Tech Stack

- Django 5.x
- Tailwind CSS (CDN)
- SQLite (dev) / PostgreSQL (prod)
- Whitenoise (static files)
- Gunicorn (production server)
