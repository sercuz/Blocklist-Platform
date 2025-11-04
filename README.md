# Blocklist Platform

[![Development Status](https://img.shields.io/badge/status-under%20development-yellow)](https://github.com/sercuz/blocklist-platform)
[![License](https://img.shields.io/badge/license-BSD%204--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)

A lightweight web portal that allows analysts to quickly add or remove indicators of compromise (IOCs) such as IP addresses, domains, and URLs, while maintaining an auditable record of every action.

## 🚧 Development Status

**This project is currently under active development.** While the core functionality is working and stable, new features are being added and improvements are ongoing. 

- ✅ Core blocking/unblocking functionality
- ✅ JWT authentication and API keys
- ✅ Audit logging
- ✅ Docker deployment
- 🔄 Additional features and enhancements in progress
- 🔄 Extended testing and optimization

Feel free to use it, test it, and provide feedback! Contributions and issue reports are welcome.

**⚠️ IMPORTANT NOTICE**: This platform is intended solely for legitimate cybersecurity and network security purposes. Misuse of this software for illegal activities, unauthorized access, censorship, or any prohibited purposes as outlined in the Terms of Service is strictly forbidden and may result in legal action.

## License

This project is licensed under the **BSD 4-Clause License**. See the [LICENSE](LICENSE) file for details.

## Terms of Service

By using this software, you agree to the [Terms of Service](TERMS_OF_SERVICE.md). Please read them carefully before deploying or using this platform.

## Contact

For questions, issues, or concerns, please contact: **alwaleedabosaq@gmail.com**

## Features

- Single-page application with a clean, modern UI
- Block/unblock IP addresses, domains, and URLs
- Searchable blocklist table with inline unblock functionality
- Audit logs for all actions
- JWT-based authentication
- RESTful API for future automation
- Flat-file storage for tamper-evident audit trail

## Tech Stack

- **Backend**: Python + Django REST Framework
- **Frontend**: React with modern component library
- **Storage**: Flat files (can be swapped for DB later)
- **Authentication**: JWT tokens
- **Deployment**: Docker containers

## 🚀 Quick Start

For detailed setup instructions, see **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** for a comprehensive step-by-step guide.

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)

### Basic Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sercuz/blocklist-platform.git
   cd blocklist-platform
   ```

2. **Start the application**
   ```bash
   docker-compose up -d --build
   ```

3. **Set up the database**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/swagger/

### For Production Deployment

**⚠️ Important**: Before deploying to production, please review:

- **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** - Complete production setup guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Security and deployment checklist
- **[TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)** - Legal terms and acceptable use policy

Key production considerations:
- Change the `SECRET_KEY` environment variable
- Set `DEBUG=0` in production
- Configure `ALLOWED_HOSTS` properly
- Set up SSL/TLS certificates
- Configure regular backups of the `data/` directory

## API Endpoints

- `/api/token/` - Obtain JWT token (POST)
- `/api/token/refresh/` - Refresh JWT token (POST)
- `/api/block/` - Block indicators (POST)
- `/api/unblock/` - Unblock indicators (POST)
- `/api/list/` - Get all blocklist entries (GET)
- `/api/logs/` - Get audit logs (GET)

## Data Storage

All data is stored in flat text files in the `data` directory:

- `ip-address-blocklist.txt` - IP address blocklist
- `domain-blocklist.txt` - Domain blocklist
- `url-blocklist.txt` - URL blocklist
- `blocklist-log.txt` - Audit log

## Docker Configuration

The application consists of two Docker containers:

1. **Backend** - Django REST API running on port 8000
2. **Frontend** - React application running on port 3000

The containers are configured in the `docker-compose.yml` file and can be customized as needed.
