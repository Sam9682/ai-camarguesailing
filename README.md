# Camargue Sailing Website

A Flask-based web application for promoting and managing sailing voyage bookings in the Camargue area of South France.

## Features

- Public information pages about sailing voyages and the Camargue area
- User registration with email verification
- Booking system for managing voyage reservations
- Discussion forum for registered users
- PostgreSQL database for data persistence
- Docker support for easy deployment

## Project Structure

```
camargue-sailing-website/
├── src/                    # Application code
│   ├── __init__.py
│   ├── app.py             # Flask application and routes
│   ├── config.py          # Configuration management
│   ├── database.py        # Database models and setup
│   ├── auth.py            # Authentication logic
│   ├── booking.py         # Booking management
│   ├── forum.py           # Forum functionality
│   └── email_service.py   # Email sending
├── templates/             # Jinja2 HTML templates
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   └── images/           # Boat images and photos
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker services configuration
└── .env.example          # Environment variables template

```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (optional)

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your settings
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database (PostgreSQL must be running)
6. Run the application:
   ```bash
   flask run
   ```

### Docker Deployment

1. Copy `.env.example` to `.env` and configure your settings
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at http://localhost:5000

## Testing

Run the test suite:
```bash
pytest
```

Run property-based tests with more iterations:
```bash
pytest --hypothesis-iterations=1000
```

## Requirements

See `requirements.txt` for a complete list of Python dependencies.

## License

Proprietary - All rights reserved
