# Task Manager API — FastAPI + Supabase

A minimal, internship-ready REST API that demonstrates:
- Auth via **Supabase Auth** (JWT — bearer token)
- Data in **Supabase Postgres** with user-scoped access (use RLS policies)
- CRUD for tasks
- Auto docs at **/docs** (Swagger UI) and **/redoc**
- Tests with `pytest` + `httpx`

## Tech
- Python 3.13 (works on 3.11/3.12 as well)
- FastAPI, Uvicorn
- Supabase Python client (`supabase>=2`)
- Pydantic v2, httpx, pytest/pytest-asyncio
- `pydantic-settings` for `.env`

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# Ensure you created the Supabase table & RLS policies (see below)
uvicorn app.main:app --reload
# Swagger: http://127.0.0.1:8000/docs
```

### Environment (`.env`)
Copy `.env.example` → `.env` and fill your Supabase project values.
```env
SUPABASE_URL=https://<project_id>.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...   # server-only (never commit)
SUPABASE_JWKS_URL=https://<project_id>.supabase.co/auth/v1/keys
APP_ENV=dev
```

### Supabase SQL — table
```sql
create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  title text not null,
  description text,
  done boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

> We update `updated_at` in the API on writes to avoid depending on custom DB triggers.

### Supabase SQL — RLS policies
```sql
alter table public.tasks enable row level security;

create policy "select own tasks"
on public.tasks for select
using (auth.uid() = owner_id);

create policy "insert own tasks"
on public.tasks for insert
with check (auth.uid() = owner_id);

create policy "update own tasks"
on public.tasks for update
using (auth.uid() = owner_id);

create policy "delete own tasks"
on public.tasks for delete
using (auth.uid() = owner_id);
```

## API overview
- `POST /auth/signup?email=&password=` (demo-only, uses service role)
- `POST /auth/login?email=&password=` → `{access_token, ...}`
- `GET /tasks` — list your tasks
- `POST /tasks` — create `{title, description?}`
- `GET /tasks/{id}` — get one
- `PATCH /tasks/{id}` — partial update `{title?, description?, done?}`
- `DELETE /tasks/{id}`

Include the Supabase access token in:
```http
Authorization: Bearer <access_token>
```

## Tests
```bash
pytest -q
```

## Why this project?
This repo showcases API design, authentication, secure data access (RLS), automated docs, and basic testing — the exact building blocks recruiters look for in Python internships.

## Stretch goals
- Filtering & pagination (`/tasks?done=true&limit=20&offset=0`)
- CI with GitHub Actions: run `pytest` + `ruff` + `mypy`
- Deploy to Fly.io/Render; set env vars as secrets; restrict CORS origins
```
