# CodeX 3.0 Intelligent Event Command Center

This is the backend and frontend for the live festival crowd-management dashboard.

## Setup Instructions

1. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server:**
   The backend uses FastAPI and requires an Admin Key to start. Run the following command in PowerShell to inject the environment variables and start the server on port 8000:
   
   ```powershell
   $env:ADMIN_KEY="TEST-KEY"; $env:MONGO_URI="mongodb+srv://satyamguptaishere_db_user:THISISSATYAM@cluster0.shnt6yi.mongodb.net/?appName=Cluster0"; python -m uvicorn backend.main:app --port 8000
   ```

3. **Access the Application:**
   Open your browser and navigate to `http://localhost:8000`

