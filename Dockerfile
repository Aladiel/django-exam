# Dockerfile

FROM python:3.12-slim

# Installe les dépendances système utiles (compilation, pillow, etc)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non root
RUN useradd -m appuser

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/static
RUN chown -R appuser /app

USER appuser

# Expose le port pour Django
EXPOSE 8000

# RUN python manage.py collectstatic --noinput          à décommenter pour la prod
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]     #  inversement, à commenter en prod

# CMD pour PROD (décommente pour prod, adapte le chemin wsgi si besoin)
# CMD ["gunicorn", "mon_projet.wsgi:application", "--bind", "0.0.0.0:8000"]