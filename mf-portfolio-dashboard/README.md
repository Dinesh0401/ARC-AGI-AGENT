# Mutual Fund Portfolio Analytics Dashboard

A modern, locally hosted web application built for **Anand (PASS Science)** to analyze Mutual Fund portfolio Excel files, calculate key financial performance metrics, XIRR returns, asset allocations, and detect **overlapping stock holdings** across mutual funds.

---

## Key Features

- **Excel Upload & Flexible Parser**: Drag-and-drop `.xlsx`, `.xls`, or `.csv` files containing Mutual Fund holdings and underlying stock data. Includes a 1-click sample loader (`jon_doe_MF.xlsx`).
- **Portfolio Overview (KPI Cards)**:
  - Total Invested Amount (₹)
  - Current Market Value (₹)
  - Total Profit / Loss (₹)
  - Overall Return %
  - **Portfolio XIRR %** (calculated via `pyxirr`)
- **Allocation Analysis (Interactive Recharts)**:
  - Equity vs Hybrid Allocation
  - Allocation by Asset Management Company (AMC)
  - Allocation by Fund Category (Large Cap, Flexi Cap, Small Cap, etc.)
- **Portfolio Summary Counters**:
  - Number of Funds
  - Number of Unique Schemes
- **Overlapping Stocks Analysis (Primary Target)**:
  - Stock Name
  - Overlap Count (number of funds holding the stock)
  - Funds Holding Stock (with holding weight % breakdown)
  - Filterable by overlap count (≥ 2 funds, ≥ 3 funds) and searchable by stock or sector.

---

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts, Lucide React, Axios, Vite
- **Backend**: FastAPI, Pandas, NumPy, PyXIRR, OpenPyXL, Uvicorn

---

## Recommended Repository Structure

```
mf-portfolio-dashboard/
│
├── frontend/                # Vite + React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/      # Navbar, OverviewCards, AllocationCharts, OverlapTable, etc.
│   │   ├── services/        # Axios API client
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                 # FastAPI + Pandas + PyXIRR
│   ├── app/
│   │   ├── main.py          # API Endpoints (/api/upload, /api/sample)
│   │   ├── analytics.py     # XIRR & Overlap calculation engine
│   │   ├── parser.py        # Excel / CSV parsing logic
│   │   ├── models.py        # Pydantic Schemas
│   │   └── sample_generator.py # Sample dataset generator
│   ├── requirements.txt
│   └── README.md
│
├── sample_data/             # Pre-generated sample dataset
│   └── jon_doe_MF.xlsx
│
├── docker-compose.yml       # Local containerization setup
├── .gitignore
└── README.md
```

---

## Quick Start & Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Generate sample dataset (creates sample_data/jon_doe_MF.xlsx)
python app/sample_generator.py

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API interactive documentation will be live at `http://localhost:8000/docs`.

### 3. Frontend Setup (Open a new terminal)
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
The dashboard interface will be available locally at `http://localhost:5173`.

---

## GitHub Repository Setup Commands

To publish this project to GitHub:

```bash
# Initialize git in project root
git init

# Add all project files
git add .

# Create initial commit
git commit -m "Initial commit - Mutual Fund Portfolio Analytics Dashboard"

# Set default branch to main
git branch -M main

# Link your remote GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/mf-portfolio-dashboard.git

# Push to GitHub
git push -u origin main
```

---

## Docker Quickstart (Optional)

Run both backend and frontend in isolated Docker containers:

```bash
docker-compose up --build
```
Access the application at `http://localhost:5173`.
