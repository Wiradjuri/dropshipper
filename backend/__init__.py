"""Backend package marker for absolute imports from repo root.

This allows running commands like:
    uvicorn backend.app.main:app --reload --port 8000

Alternatively, you can `cd backend` and run:
    uvicorn app.main:app --reload --port 8000
"""
