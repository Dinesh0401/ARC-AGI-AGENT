# Backend - Mutual Fund Portfolio Analytics API

FastAPI backend engine for processing Mutual Fund portfolio Excel files, calculating portfolio KPIs, XIRR, asset allocations, and analyzing overlapping stock holdings.

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Sample Data
```bash
python app/sample_generator.py
```

### 4. Run API Server
```bash
uvicorn app.main:app --reload --port 8000
```

The API documentation will be accessible at `http://localhost:8000/docs`.
