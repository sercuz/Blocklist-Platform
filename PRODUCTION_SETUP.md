# Production Setup Guide

This guide will help you set up the Blocklist Platform for production use.

## Prerequisites

- Docker and Docker Compose installed
- A server with at least 2GB RAM
- Domain name (optional, but recommended)
- SSL certificate (recommended for production)

## Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/blocklist-platform.git
cd blocklist-platform
```

2. **Set up environment variables**

Create a .env file in the project root:

```bash
# Django settings
SECRET_KEY=your-secure-random-secret-key-here
DEBUG=0
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Optional: Database settings (if using PostgreSQL)
# DB_NAME=blocklist
# DB_USER=blocklist_user
# DB_PASSWORD=secure_password
# DB_HOST=db
# DB_PORT=5432
```

**Generate a secure SECRET_KEY:**

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

3. **Build and start the containers**

```bash
docker-compose up -d --build
```

4. **Set up the database**

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create a superuser
docker-compose exec backend python manage.py createsuperuser
```

5. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/swagger/

## Production Deployment

For production deployment, see [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for a comprehensive checklist.

### Key Security Steps

1. **Change SECRET_KEY**: Use a strong, random secret key
2. **Set DEBUG=0**: Disable debug mode in production
3. **Configure ALLOWED_HOSTS**: Restrict to your domain(s)
4. **Set up SSL/TLS**: Use HTTPS in production
5. **Configure firewall**: Restrict access to necessary ports only
6. **Set up backups**: Regular backups of the data directory

### Recommended: Reverse Proxy Setup

Use Nginx or Apache as a reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP \;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP \;
    }
}
```

## Backup and Restore

### Backup

```bash
# Backup data directory
tar -czf blocklist-backup-$(date +%Y%m%d-%H%M%S).tar.gz data/

# Backup database
docker-compose exec backend python manage.py dumpdata > backup.json
```

### Restore

```bash
# Restore data directory
tar -xzf blocklist-backup-YYYYMMDD-HHMMSS.tar.gz

# Restore database
docker-compose exec backend python manage.py loaddata backup.json
```

## Monitoring

Monitor your application:

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check container status
docker-compose ps
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database issues

```bash
# Reset database (WARNING: This will delete all data)
docker-compose down
rm backend/db.sqlite3
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Permission issues

```bash
# Fix permissions on data directory
sudo chown -R \-data data/
sudo chmod -R 775 data/
```

## Support

For questions or issues:
- Email: alwaleedabosaq@gmail.com
- Review: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Check: [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)

## License

This project is licensed under the BSD 4-Clause License. See [LICENSE](LICENSE) for details.
