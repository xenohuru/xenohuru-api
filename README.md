# 🌍 Xenohuru API

> REST API for Tanzania tourism — GPS-accurate attractions, real-time weather, and open data for developers.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Open Source Community](https://img.shields.io/badge/Made%20in-Tanzania-green.svg)](#)

**Live API:** https://xenohuru-o7ix53tg.b4a.run/ | **Frontend UI:** https://x.xenohuru.workers.dev/ | **Sponsor Us:** [Ko-fi](https://ko-fi.com/xenohuru)

---

## About

Open-source Tanzania tourism API by [Xenohuru](https://xenohuru.org) — From Greek "xenos" (explorer) + Swahili "huru" (free).

This backend provides GPS-accurate attraction data, real-time weather, and REST API for developers building tourism experiences.

---

## Architecture

```
xenohuru-api/
├── src/
│   ├── app/
│   │   ├── accounts/     # User authentication & JWT
│   │   ├── attractions/  # Attractions API
│   │   ├── regions/      # Regions API
│   │   └── weather/      # Weather integration
│   ├── config/           # Django settings
│   └── manage.py
├── requirements.txt
└── docs/
```

**Features:**
- REST API with Django REST Framework
- JWT authentication
- Real-time weather (Open-Meteo)
- GPS-accurate locations
- OpenAPI documentation

---

## Quick Start

### Prerequisites
- Python 3.10+, pip, virtualenv
- MySQL (or SQLite for dev)

### Installation

```bash
git clone https://github.com/Xenohuru/xenohuru-api.git
cd xenohuru-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your config
python src/manage.py migrate
python src/manage.py runserver
```

**API runs at:** `http://localhost:8000/api/` | **Admin:** `http://localhost:8000/admin/`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/attractions/` | GET | List attractions |
| `/attractions/:slug/` | GET | Attraction details |
| `/regions/` | GET | List regions |
| `/weather/` | GET | Current weather (by coordinates or attraction) |
| `/auth/login/` | POST | User authentication |
| `/auth/register/` | POST | User registration |

**Full docs:** https://xenohuru-o7ix53tg.b4a.run/ (Swagger)

---

## Testing

```bash
python src/manage.py test src/  # Run all tests
python src/manage.py test src/app/attractions  # Run specific app
```

---

## Tech Stack

- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** MySQL
- **Auth:** JWT (djangorestframework-simplejwt)
- **Weather:** Open-Meteo API
- **Docs:** drf-spectacular (OpenAPI/Swagger)

---

## Key Features

### **For API Consumers:**
- RESTful design with predictable endpoints
- Comprehensive OpenAPI documentation
- JWT authentication support
- Fast response times with database optimization
- Pagination & filtering support
- Free & open-source

### **For Developers:**
- Well-tested codebase (pytest)
- Clear code structure & documentation
- Easy to extend with Django apps
- Docker support (coming soon)
- CI/CD with GitHub Actions

---

## Contributing

We welcome contributors! Fork the repo, create a branch, and submit a PR.

**Steps:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes & test
4. Commit: `git commit -m "Add feature"`
5. Push & open PR

**Read:** [CONTRIBUTING.md](CONTRIBUTING.md) | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## License

MIT License — see [LICENSE](LICENSE)

---

**🌍 Built with Django | 🇹🇿 From Tanzania | ❤️ Support us on [Ko-fi](https://ko-fi.com/xenohuru)**
 
