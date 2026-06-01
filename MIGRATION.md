# Migration Guide: LinkedIn Auto-Apply Bot → AI Job Application Agent

## Overview

This guide walks through migrating from the old `runAiBot.py`-based system to the new multi-agent architecture.

## 1. New Directory Structure

```
D:\Auto_job_applier_linkedIn\
├── main.py                          # NEW: Entry point (replaces runAiBot.py)
├── scheduler.py                     # NEW: Automated daily workflow
├── .env.example                     # NEW: Environment variable template
├── requirements.txt                 # NEW: All dependencies
│
├── config/
│   ├── settings.py                  # NEW: Pydantic config (replaces all config/*.py)
│   ├── personals.py                 # OLD: Kept for backward compat
│   ├── questions.py                 # OLD: Kept for backward compat
│   ├── search.py                    # OLD: Kept for backward compat
│   ├── secrets.py                   # OLD: Kept for backward compat
│   └── settings_old.py              # OLD: Renamed from original settings.py
│
├── agents/
│   ├── __init__.py
│   ├── search_agent.py              # NEW: Multi-platform job search
│   ├── ranking_agent.py             # NEW: AI-powered job scoring
│   ├── resume_agent.py              # NEW: Resume selection & tailoring
│   ├── cover_letter_agent.py        # NEW: Cover letter generation
│   ├── application_agent.py         # NEW: Intelligent decision-making
│   ├── tracking_agent.py            # NEW: Application tracking & reports
│   └── workflow.py                  # NEW: LangGraph orchestrator
│
├── services/
│   ├── __init__.py
│   ├── groq_service.py              # NEW: Central LLM service (Groq API)
│   ├── linkedin_service.py          # NEW: Playwright-based LinkedIn scraper
│   ├── wellfound_service.py         # NEW: Wellfound job scraper
│   ├── yc_jobs_service.py           # NEW: YC Work at a Startup scraper
│   ├── remoteok_service.py          # NEW: RemoteOK API client
│   └── google_sheets_service.py     # NEW: Google Sheets dashboard
│
├── database/
│   ├── __init__.py
│   ├── models.py                    # NEW: SQLAlchemy models
│   └── repository.py               # NEW: Data access layer
│
├── api/
│   ├── __init__.py
│   └── routes.py                    # NEW: FastAPI REST endpoints
│
├── frontend/dashboard/              # REPLACED: Google Sheets (was Next.js)
│
├── modules/                         # OLD: Preserved as-is
│   ├── ai/                          # OLD: Now superseded by groq_service.py
│   ├── resumes/                     # OLD: Now superseded by resume_agent.py
│   └── ...
│
├── runAiBot.py                      # OLD: Original entry point (preserved)
└── app.py                           # OLD: Flask UI (preserved)
```

## 2. Step-by-Step Migration

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Set Up Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 3: Set Up Google Sheets (Optional)

1. Create a Google Cloud project
2. Enable Google Sheets API and Drive API
3. Create a Service Account and download JSON key
4. Place at `credentials/google_sheets_credentials.json`
5. Create a Google Sheet and copy the spreadsheet ID
6. Set `JOB_AGENT_GOOGLE_SHEETS__SPREADSHEET_ID` in `.env`

### Step 4: Create Resumes Directory

```
all resumes/
├── default/
│   └── resume.pdf
├── ai.pdf
├── backend.pdf
├── fullstack.pdf
├── ml.pdf
└── research.pdf
```

### Step 5: Configure Candidate Profile

Edit `shubham.md` with your own profile, or point to a different file via `--profile`.

## 3. Running the New System

### Single workflow run (same as old runAiBot.py):
```bash
python main.py --mode run
```

### Start API server:
```bash
python main.py --mode api --port 8000
```

### Search only:
```bash
python main.py --mode search
```

### Search + Rank only:
```bash
python main.py --mode rank
```

### Start scheduler:
```bash
python main.py --mode scheduler
```

### API Endpoints:
```
GET  /api/health              - Health check
POST /api/workflow/run        - Run full workflow
POST /api/workflow/search     - Search only
GET  /api/applications        - List all applications
GET  /api/applications/{id}   - Get specific application
PUT  /api/applications/{id}/status - Update status
GET  /api/dashboard           - Dashboard stats
GET  /api/dashboard/platforms - Platform breakdown
GET  /api/dashboard/scores    - Score distribution
GET  /api/reports             - Daily reports
POST /api/sheets/sync         - Sync to Google Sheets
```

## 4. Architecture Changes

### Before (Old System):
- Single monolithic `runAiBot.py` (1305 lines)
- Selenium + undetected-chromedriver
- OpenAI/DeepSeek/Gemini AI providers
- CSV-based data storage
- Flask web UI
- Config via Python files with wildcard imports
- No job scoring or intelligent decisions
- LinkedIn-only platform support

### After (New System):
- 6 specialized agents with clear responsibilities
- Playwright for browser automation (modern, async-ready)
- Groq API as primary LLM (supports DeepSeek-R1, Qwen, Llama)
- SQLite database with SQLAlchemy ORM
- FastAPI REST API
- Google Sheets dashboard
- Pydantic config with environment variables
- AI-powered job scoring (0-100) with configurable weights
- Intelligent APPLY/SKIP/REVIEW decisions
- Multi-platform support (LinkedIn, Wellfound, YC Jobs, RemoteOK)
- LangGraph workflow orchestration
- Candidate profile-driven (never fabricates experience)

## 5. Key Differences

| Feature | Old System | New System |
|---------|-----------|------------|
| Entry point | `runAiBot.py` | `main.py` |
| Browser | Selenium | Playwright |
| AI Provider | OpenAI/DeepSeek/Gemini | Groq (primary) |
| Storage | CSV files | SQLite + Google Sheets |
| Config | Python files | Pydantic + .env |
| Platforms | LinkedIn | LinkedIn, Wellfound, YC, RemoteOK |
| Decision Logic | Apply to all | Score + AI decision |
| API | Flask (read-only) | FastAPI (full CRUD) |
| Dashboard | HTML table | Google Sheets |
| Workflow | Linear script | LangGraph state machine |

## 6. Preserved Files

The following old files are preserved for reference:
- `runAiBot.py` - Original entry point (still works)
- `app.py` - Original Flask UI (still works)
- `config/personals.py` - Old personal config
- `config/questions.py` - Old questions config
- `config/search.py` - Old search config
- `config/secrets.py` - Old secrets config
- `modules/` - All original modules

## 7. Rollback

To revert to the old system:
```bash
python runAiBot.py
```

The old system is fully preserved and untouched.
