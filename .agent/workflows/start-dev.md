# Workflow: Start Dev

## Description
Launches local development environments for API, Web frontend, and Streamlit dashboard.

## Execution
```powershell
# In terminal 1 (FastAPI backend):
uvicorn apps.api.main:app --reload --port 8000

# In terminal 2 (React Vite Web App):
cd apps/web && npm run dev

# In terminal 3 (Streamlit PRD Dashboard):
streamlit run apps/streamlit/app.py --server.port 8501
```
