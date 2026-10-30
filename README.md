# Parking Lot Management System

Deployment link: https://parkinglotmanagement-69xb.onrender.com/docs#/

## Setup Instructions

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://git.beehyv.com/saroja.bamra/parkinglotmanagement
cd parkinglotmanagement
```

### 2. Set up a Virtual Environment

```bash
python3 -m venv parking-env
source parking-env/bin/activate
```

### 3. Install Dependencies

Once your virtual environment is active, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Database Setup

This project uses SQLite as its database (default `parking-lot.db` file). The database tables will be automatically created on application startup if they don't exist.

### 5. Environment Variables

Create a `.env` file in the root directory of your project (at the same level as `app/` and `requirements.txt`).

```env
SECRET_KEY = "SECRET_KEY"
ALGORITHM = "ALGORITHM"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### 6. Run the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

### OpenAPI Specification

The generated OpenAPI 3.1 specification is available in [`openapi.json`](./openapi.json). To regenerate it after changing API routes or schemas, run:

```bash
python -c "import json; from pathlib import Path; from app.main import app; Path('openapi.json').write_text(json.dumps(app.openapi(), indent=2) + '\n')"
```

FastAPI also serves the interactive documentation at `/docs` and the schema at `/openapi.json` while the application is running.