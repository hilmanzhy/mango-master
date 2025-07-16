# InfraTest Project

## What This Magnificently Over-Engineered App Does

Welcome to the most unnecessarily complex "Hello World" application ever created! 🎉

This app accepts text messages from users, waits exactly 3 seconds (because that's how long it takes to process profound thoughts), then responds with "pong [your message]". But wait, there's more! We've also added:

- Real-time Server-Sent Events (because WebSockets are so 2020)
- A dark/light theme toggle (priorities!)
- Database persistence for message history (because someone might want to audit your "hello world" messages)
- Celery task queues (because synchronous processing is for peasants)
- A heartbeat system that announces "heartbeat successful" every 3 seconds (in case you forget the app is running)

## System Architecture

Here's how your message travels through this architectural marvel:

```
┌─────────┐    HTTP     ┌─────────────┐    Task     ┌─────────────┐
│  User   │────────────▶│   Django    │────────────▶│   Celery    │
│ Browser │             │  Web App    │             │   Worker    │
└─────────┘             └─────────────┘             └─────────────┘
     │                         │                           │
     │ Server-Sent Events      │ Store Task              │ sleep(3)
     │                         │                           │
     ▼                         ▼                           ▼
┌─────────┐             ┌─────────────┐             ┌─────────────┐
│  Live   │◀────────────│    Redis    │◀────────────│ "pong msg"  │
│Results  │             │   Broker    │             │   Result    │
└─────────┘             └─────────────┘             └─────────────┘
     │                         │                           │
     │                         │                           │
     ▼                         ▼                           ▼
┌─────────┐             ┌─────────────┐             ┌─────────────┐
│History  │◀────────────│ PostgreSQL  │◀────────────│ Save to DB  │
│ Page    │             │  Database   │             │             │
└─────────┘             └─────────────┘             └─────────────┘
```

## Core Components

- **Django Web Application**: Serves the UI and handles form submissions
- **Celery Workers**: Process messages asynchronously (with dramatic 3-second delays)
- **Celery Beat**: Sends heartbeat messages every 3 seconds (vital for operations)
- **Redis**: Message broker and caching layer
- **PostgreSQL**: Persistent storage for message history
- **Server-Sent Events**: Real-time updates to the browser (because AJAX is so 2010)

## Database Configuration

**Current State**: The app is running on SQLite (because we're not animals), but for production you'll want PostgreSQL.

The good news: `psycopg` and `dj-database-url` are already in `requirements.txt`. The bad news: we're leaving the database setup to you (part of the test!).

You'll need to:
1. Set up a PostgreSQL instance (up to you where you want it installed)
2. Configure the `DATABASE_URL` environment variable (hint: looik-up `dj-database-url`, it's a lifesaver).
3. Run migrations to create the schema

## Service Dependencies

Before you can run this masterpiece, you'll need:

- **Redis Server**: For Celery broker and result backend
- **PostgreSQL**: For persistent message storage
- **Python 3.11+**: Because we're living in the future

## Commands Reference

### Environment Setup
```bash
# Create virtual environment (recommended)
$ python -m virtualenv .venv
$ source .venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

### Database Operations
```bash
# Create database migrations (for the core app)
# you won't be needing this for the test!
$ python manage.py makemigrations core

# Apply database migrations
$ python manage.py migrate
```

### Development Server
```bash
# Start Django development server
$ python manage.py runserver
# Available at http://127.0.0.1:8000
```

### Production Deployment
```bash
# Collect static files (CSS, JS, images)
$ python manage.py collectstatic

# Start production web server
$ gunicorn app.wsgi -b 127.0.0.1:8000
```

### Background Processing
```bash
# Start Celery worker (processes async tasks)
$ celery -A app worker --loglevel=info

# Start Celery beat scheduler (for heartbeat messages)
$ celery -A app beat --loglevel=info

# Or run both together (development only)
$ celery -A app worker --beat --loglevel=info
```

### External Services
```bash
# Start Redis server (if not running as service)
$ redis-server

# Connect to Redis CLI (for debugging)
$ redis-cli
```

## Application Features

### Homepage (`/`)
- Message input form with dark/light theme toggle
- Real-time results display (ephemeral, limited to 25 messages)
- Server-Sent Events for live updates
- AJAX form submission (because page refreshes are so 2005)

### History Page (`/history/`)
- Paginated table of all processed messages
- Shows message status, timestamps, and processing duration
- Searchable and sortable (just kidding, it's basic)

### API Endpoints
- `/submit/` - AJAX endpoint for message processing
- `/events/` - Server-Sent Events stream for real-time updates
- `/admin/` - Django admin interface (if you're into that sort of thing)

## Environment Variables

You'll probably want to set these:

```bash
# Database connection (for PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost/dbname

TODO: There are other bits here that needs to be made configurable
```

## Production Considerations

This is a test application, so don't expect production-ready features like:
- Proper error handling
- Security hardening
- Performance optimization
- Monitoring and logging
- Load balancing
- Auto-scaling
- Health checks

But hey, it has a dark mode toggle! 🌙

## Troubleshooting

**App not starting?**
- Check if Redis is running
- Verify database connections
- Make sure migrations are applied

**Messages not processing?**
- Check if Celery worker is running
- Look at Redis for queued tasks
- Check the logs (what logs?)

## Architecture Decisions We Made

- **SQLite → PostgreSQL**: Because someone said "production-ready"
- **Redis**: Because we needed a message broker and it's trendy
- **Celery**: Because async processing sounds professional
- **Server-Sent Events**: Because WebSockets felt too mainstream
- **Dark mode**: Because developers demand it

Good luck deploying this beautiful disaster! 🚀