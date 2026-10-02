# Deployment Guide

OrderGuard AI is designed for containerized deployment using Docker.

## Prerequisites
- A PostgreSQL database (e.g., Supabase or AWS RDS).
- Docker and Docker Compose installed on your host.
- Proper SSL/TLS termination at your load balancer/proxy (e.g., Nginx, Traefik).

## Environment Configuration
Provide a `.env` file in the root containing:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your_secure_secret
VITE_GOOGLE_CLIENT_ID=your_oauth_client_id
```

## Docker Compose
Run the stack using:
```bash
docker-compose up --build -d
```
This spins up:
- The backend FastAPI application on port 8000.
- The frontend Vite application served via Nginx on port 80.

## Database Migrations
Always ensure Alembic migrations are executed against the production database before spinning up the new application version:
```bash
docker-compose exec backend alembic upgrade head
```
