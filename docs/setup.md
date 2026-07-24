# Developer Setup Guide

## Environment Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 recommended.
- **OS**: Windows, macOS, or Linux.
- **Git**: Standard installation.

## Step-by-Step Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/Dinesh0401/ARC-AGI-AGENT.git
   cd ARC-AGI-AGENT
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate Virtual Environment**:
   - On Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - On Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify Installation**:
   - Run baseline script:
     ```bash
     python main.py
     ```
   - Run tests:
     ```bash
     python -m pytest tests/
     ```
