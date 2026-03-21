# Expense Tracker — Backend

A Django REST Framework backend for the Expense Tracker project, extended with
an AI-powered expense insights module as part of the SpendWise AI contribution.

---

## Stack

- **Python** 3.11+
- **Django** 6.0.2
- **Django REST Framework** 3.16
- **Authentication** — `djangorestframework-simplejwt`
- **Filtering** — `django-filter`
- **API Documentation** — `drf-spectacular` (Swagger UI at `/`)
- **AI Insights** — Groq LLM API via `httpx`

---

## Getting Started

### 1. Clone and create a virtual environment
```bash
git clone https://github.com/varaprasadchilakanti/Expense-Tracker-Backend.git
cd Expense-Tracker-Backend/expense_tracker
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r ../requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
```

Open `.env` and set the required values. See `.env.example` for reference.
`SECRET_KEY` is required in all environments. `LLM_API_KEY` is required only
if you intend to use the AI insights endpoint.

### 3. Apply migrations and run
```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.
Swagger UI is available at `http://127.0.0.1:8000/`.

---

## Environment Configuration

Settings are split across three files under `expense_tracker/settings/`.

| File | Purpose |
|---|---|
| `base.py` | Shared configuration for all environments |
| `dev.py` | Development — `DEBUG=True`, SQLite, localhost CORS |
| `prod.py` | Production — `DEBUG=False`, env-driven hosts and CORS |

`manage.py` defaults to `settings.dev`. In production, set the environment
variable explicitly:
```bash
export DJANGO_SETTINGS_MODULE=expense_tracker.settings.prod
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/token/` | None | Obtain access and refresh tokens |
| POST | `/api/token/refresh/` | None | Refresh access token |
| POST | `/api/register/` | None | Create a new user account |
| GET | `/api/expenses/` | JWT | List expenses (filterable, orderable) |
| POST | `/api/expenses/` | JWT | Create a new expense |
| GET | `/api/expenses/<pk>/` | JWT | Retrieve a single expense |
| PUT / PATCH | `/api/expenses/<pk>/` | JWT | Update a single expense |
| DELETE | `/api/expenses/<pk>/` | JWT | Delete a single expense |
| GET | `/api/expenses/summary/` | JWT | Monthly spend total and count |
| GET | `/api/expenses/category-breakdown/` | JWT | Monthly spend grouped by category |
| GET | `/api/expenses/insights/` | JWT | AI-generated savings recommendations |
| GET | `/api/schema/` | None | OpenAPI schema |
| GET | `/` | None | Swagger UI |

### Filtering and ordering

The `/api/expenses/` endpoint supports filtering by `category` and `amount`,
and ordering by `amount` or `created_at`:
GET /api/expenses/?category=Food
GET /api/expenses/?ordering=-amount

### AI Insights

`GET /api/expenses/insights/` returns between 3 and 5 actionable spending
recommendations derived from the authenticated user's 30 most recent expenses.
Responses are cached per user for 15 minutes based on the expense data content.

**Requires** `LLM_API_KEY` to be set in the environment. Obtain a free API key
at [console.groq.com](https://console.groq.com). To swap the LLM provider,
replace the engine implementation in `expenses/ai/engines/` — the interface
in `expenses/ai/interface.py` remains unchanged.

**Response shape:**
```json
{
  "insights": [
    "Your food spending accounts for 40% of total expenses this month...",
    "Three transactions at the same vendor suggest a subscription..."
  ],
  "source": "groq",
  "cached": false
}
```

---

## Project Structure
expense_tracker/
manage.py
.env.example
expense_tracker/
settings/
base.py           shared configuration
dev.py            development overrides
prod.py           production overrides
urls.py             root URL configuration
asgi.py             ASGI entry point
wsgi.py             WSGI entry point
expenses/
models.py           Expense model
serializer.py       ExpenseSerializer, RegisterSerializer
views.py            all API views
urls.py             expenses/ routes
admin.py            Expense registered in admin
ai/
interface.py      public contract — get_expense_insights()
exceptions.py     typed exception hierarchy
engines/
groq_engine.py  Groq LLM implementation
prompts/
templates.py    externalised prompt strings

---

## Contributing

One concern per pull request. No PR mixes refactoring with feature work.
Architecture is confirmed before implementation begins. Each PR must be
self-contained and reviewable without context from other open PRs.

---

## Known Technical Debt

| Item | Location |
|---|---|
| `HttpClient` injected inside Angular auth interceptor — circular dependency risk | Frontend only |
| `settings_deprecate.py` retained for reference | `expense_tracker/settings_deprecate.py` |
| SQLite used in production settings — replace with PostgreSQL for production deployment | `settings/prod.py` |
| AI module scoped to `expenses/ai/` — promote to top-level `ai/` if additional apps are added | `expenses/ai/` |
