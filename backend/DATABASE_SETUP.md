# Database Setup

The SQLite database file (db.sqlite3) is not included in the repository.

## Initial Setup

After cloning the repository, you need to set up the database:

```bash
# Run migrations to create the database
docker-compose exec backend python manage.py migrate

# Create a superuser account
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Database Location

The database file will be created at: Backend/db.sqlite3

This file is excluded from git (see .gitignore) to prevent accidentally committing sensitive user data.
