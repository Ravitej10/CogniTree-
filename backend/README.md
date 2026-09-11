# CogniTree backend

FastAPI backend implementing the five modules from the project deck.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

copy env.example .env   # optionally fill in GOOGLE_API_KEY

# SQLite database and tables are created automatically on first run.
uvicorn main:app --reload --port 8000
```

The frontend's `src/pages/LoginPage.jsx` posts to `/api/auth/login`. The Vite config
proxies `/api` to `http://127.0.0.1:8000` during local development.

## Routes -> pipeline phase

| Phase | Endpoint | File |
|---|---|---|
| Auth | `POST /api/auth/signup`, `/login`, `GET /me` | `api/auth.py` |
| 1. Ingestion | `POST /api/documents/upload` | `api/ingestion.py`, `services/ingestion_service.py` |
| 2. Question Factory | `POST /api/questions/generate` | `api/questions.py`, `services/question_factory.py` |
| 3. Quiz Portal | `POST /api/quiz/start`, `/{id}/answer`, `/{id}/complete` | `api/quiz.py` |
| 3. Diagnostic Matrix | `GET /api/diagnostics/matrix` | `api/diagnostics.py`, `services/diagnostic_service.py` |
| 5. Adaptive Loop | `POST /api/diagnostics/adaptive-quiz` | `api/diagnostics.py`, `services/adaptive_service.py` |

## Notes / things to firm up before this is production-ready

- `question_factory.py` assumes `instructor.from_gemini` is available in
  the pinned `instructor` version — check that against whatever version
  you actually install, the Gemini integration surface has moved around
  across `instructor` releases.
- Document upload runs ingestion as a FastAPI `BackgroundTask`, which is
  fine for a class project but won't survive a server restart mid-job —
  move to a real task queue (Celery/RQ) if that matters for your demo.
- No migration tool is wired up yet (`Base.metadata.create_all` only
  creates missing tables, it won't alter existing ones) — add Alembic
  once the schema stabilizes.
- CORS in `main.py` is wide open for `localhost` dev ports only — tighten
  before deploying anywhere public.
