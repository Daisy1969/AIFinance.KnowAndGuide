# AIFinance.KnowAndGuide

Autonomous Financial Advisory System.

## Architecture
- **Frontend**: Next.js (React), Tailwind CSS
- **Backend**: Python (Flask), PyPortfolioOpt, yfinance
- **Database**: PostgreSQL
- **Integration**: Selenium/Playwright (Browser Agent)

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js & npm (for local frontend dev)
- Python 3.9+ (for local backend dev)

### Running with Docker
```bash
docker-compose up --build
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
