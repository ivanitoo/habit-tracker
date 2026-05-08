# Habit Tracker

A modern habit tracking web app built with Django. Track your daily habits, maintain streaks, and visualize your progress with an interactive dashboard featuring a GitHub-style heatmap and charts.

## Features

- User registration and authentication
- Create, edit, and delete habits (daily/weekly)
- One-click habit check-in with AJAX
- GitHub-style yearly heatmap for each habit
- 30-day progress bar chart
- Streak tracking
- Completion rate statistics
- Modern dark UI with Tailwind CSS

## Quick Start

```bash
# Clone & enter directory
cd habit_tracker

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (admin)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to use the app. Admin panel at `/admin/`.

## Deploy to Render (Free)

This project is ready to deploy on [Render](https://render.com) free tier.

1. Push this repo to GitHub
2. In Render dashboard, create a **New Web Service**
3. Connect your GitHub repo
4. Use these settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn habit_tracker.wsgi`
5. Add environment variable:
   - `DJANGO_SECRET_KEY`: generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `.onrender.com`
6. Deploy!

### PostgreSQL (optional but recommended)

After deploying, create a PostgreSQL database in Render and add the `DATABASE_URL` env var. Then update `settings.py` to use it:

```python
import dj_database_url
DATABASES["default"] = dj_database_url.config(conn_max_age=600)
```

Add `dj-database-url` to `requirements.txt`.

## Tech Stack

- Django 5.x
- Tailwind CSS (CDN)
- Chart.js
- SQLite (dev) / PostgreSQL (prod)
- Whitenoise (static files)
- Gunicorn (production server)
