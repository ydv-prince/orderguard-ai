# OrderGuard AI

OrderGuard AI is a production-oriented, full-stack AI application designed for e-commerce COD (Cash on Delivery) order verification and risk management. It estimates operational risk to prioritize manual verification, helping merchants reduce failed deliveries (RTO - Return to Origin).

> **Disclaimer:** OrderGuard AI predictions do not establish customer intent or guarantee delivery outcomes. The tool is strictly designed to prioritize manual review workflows.

## Features
- **Authentication & Tenant Isolation:** Secure JWT-based auth with strict merchant data isolation.
- **Order Ingestion API:** FastREST API to ingest new orders.
- **Machine Learning Risk Scoring:** Uses a trained Random Forest model to instantly assess the risk of delivery failure on ingestion.
- **Explainability:** Predictions include risk tiers and reason codes.
- **Human-in-the-Loop Workflow:** A React dashboard for reviewing and taking action on risky orders.
- **Automated CI/CD:** GitHub actions configured for testing and building.

## Documentation
- [End-to-End Workflow & Architecture](WORKFLOW.md)
- [API Documentation](docs/api.md)
- [Machine Learning Pipeline](docs/ml_pipeline.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## Tech Stack
- **Frontend:** React, Vite, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, SQLite (local fallback) / Supabase PostgreSQL (cloud)
- **ML:** pandas, scikit-learn (Random Forest)
- **Infrastructure:** Docker, GitHub Actions

## Installation (Production / Docker)

The easiest and recommended way to run the entire stack (PostgreSQL, Backend API, Frontend React App) is using Docker Compose:

```bash
docker-compose up --build -d
```
The application will be available at:
- **Frontend Dashboard:** `http://localhost`
- **Backend API Docs:** `http://localhost:8000/docs`

## Installation (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate

# Install dependencies (ensure you have the same packages as listed in our workflow)
pip install -r requirements.txt

# Environment Setup
# Edit .env file and configure Supabase Database URL (e.g., using connection pooler)
# DATABASE_URL=postgresql://postgres:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Run migrations
alembic upgrade head

# Start API
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Machine Learning (Optional Retraining)
```bash
cd ml
# Generate 5000 rows of synthetic e-commerce data
python generate_synthetic_data.py
# Train and serialize the model
python train_models.py
```

## Usage
1. Open the frontend URL (usually `http://localhost:5173` locally, or `http://localhost` in Docker).
2. Click **"Register as Demo User"** on the login page.
3. You will be logged in to the Verification Queue dashboard.
4. You can use the Swagger UI at `/docs` to POST new orders to `/api/v1/orders/` using your Bearer token.
5. New orders will automatically be evaluated by the ML model in the background and appear in your Verification Queue with a risk score.

## Limitations & Future Work
- The current ML model is trained on synthetic data. Real-world performance may vary significantly.
- Advanced LLM agent integration for reasoning generation is a potential future feature.
