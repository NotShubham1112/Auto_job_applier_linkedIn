from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AIProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"


class GroqModel(str, Enum):
    LLAMA_4_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"
    LLAMA_33_70B = "llama-3.3-70b-versatile"
    LLAMA_31_8B = "llama-3.1-8b-instant"
    QWEN3_32B = "qwen/qwen3-32b"
    DEEPSEEK_R1 = "deepseek-r1-distill-llama-70b"


class JobPlatform(str, Enum):
    LINKEDIN = "linkedin"
    WELLFOUND = "wellfound"
    YC_JOBS = "yc_jobs"
    REMOTEOK = "remoteok"


class ApplicationDecision(str, Enum):
    APPLY = "APPLY"
    SKIP = "SKIP"
    REVIEW = "REVIEW"


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    OFFER = "Offer"
    WITHDRAWN = "Withdrawn"


class SortOption(str, Enum):
    RELEVANCE = "RELEVANCE"
    DATE_POSTED = "DATE_POSTED"
    SALARY_HIGH = "SALARY_HIGH"


# ---------------------------------------------------------------------------
# Sub-configs
# ---------------------------------------------------------------------------

class PersonalInfo(BaseModel):
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    email: str = ""
    current_city: str = ""
    street: str = ""
    state: str = ""
    zipcode: str = ""
    country: str = ""
    ethnicity: str = ""
    gender: str = ""
    disability_status: str = ""
    veteran_status: str = ""
    portfolio: str = ""
    github: str = ""


class SearchConfig(BaseModel):
    search_terms: list[str] = Field(default_factory=lambda: ["AI Engineer", "Full Stack Developer"])
    search_location: str = ""
    platforms: list[JobPlatform] = Field(default_factory=lambda: [JobPlatform.LINKEDIN])
    randomize_search_order: bool = False
    sort_by: SortOption = SortOption.RELEVANCE
    date_posted: str = "past week"
    easy_apply_only: bool = True
    experience_level: list[str] = Field(default_factory=lambda: ["associate", "mid_senior"])
    job_type: list[str] = Field(default_factory=lambda: ["full_time"])
    remote_only: bool = True
    max_experience_required: int = -1
    current_experience: int = 0
    did_masters: bool = False
    require_visa: bool = False
    under_10_applicants: bool = False
    bad_words: list[str] = Field(default_factory=lambda: [
        "staffing", "recruiting", "commission", "unpaid", "internship",
        "mlm", "multi-level", "door to door", "data entry",
    ])
    about_company_bad_words: list[str] = Field(default_factory=lambda: [
        "staffing", "recruiting", "consulting",
    ])
    about_company_good_words: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    industry: list[str] = Field(default_factory=list)
    job_function: list[str] = Field(default_factory=list)
    job_titles: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)


class AIConfig(BaseModel):
    use_ai: bool = True
    provider: AIProvider = AIProvider.GROQ
    groq_api_key: str = ""
    groq_model: GroqModel = GroqModel.LLAMA_33_70B
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 1024
    show_error_alerts: bool = False


class ResumeConfig(BaseModel):
    default_resume_path: str = "all resumes/default/resume.pdf"
    resumes_dir: str = "all resumes"
    generated_resume_path: str = "all resumes/generated"
    years_of_experience: int = 0
    linkedin_headline: str = ""
    linkedin_summary: str = ""
    cover_letter: str = ""
    website: str = ""
    linkedin_url: str = ""
    desired_salary: str = ""
    notice_period: str = ""
    confidence_level: str = ""


class ApplicationConfig(BaseModel):
    pause_before_submit: bool = False
    pause_at_failed_question: bool = False
    overwrite_previous_answers: bool = False
    follow_companies: bool = False
    user_information_all: str = ""


class RankingConfig(BaseModel):
    """Thresholds and weights for job ranking."""
    min_score_threshold: int = 60
    confidence_threshold: float = 0.7

    # Score weights (0-1 each)
    skill_match_weight: float = 0.25
    resume_match_weight: float = 0.20
    remote_preference_weight: float = 0.15
    experience_match_weight: float = 0.15
    startup_quality_weight: float = 0.15
    salary_weight: float = 0.10

    # Boosts
    ai_engineering_boost: int = 25
    agentic_ai_boost: int = 20
    llm_infrastructure_boost: int = 20
    rag_systems_boost: int = 15
    startup_role_boost: int = 15
    founding_engineer_boost: int = 15
    research_engineering_boost: int = 10

    # Penalties
    non_technical_penalty: int = -20
    sales_penalty: int = -20
    customer_support_penalty: int = -25
    wordpress_penalty: int = -25
    data_entry_penalty: int = -30

    # Auto-reject keywords
    auto_reject_keywords: list[str] = Field(default_factory=lambda: [
        "mlm", "multi-level marketing", "commission only",
        "unpaid internship", "suspicious",
    ])


class SchedulerConfig(BaseModel):
    enabled: bool = False
    search_time: str = "08:00"
    rank_time: str = "08:05"
    generate_time: str = "08:10"
    apply_time: str = "08:20"
    report_time: str = "08:30"


class BrowserConfig(BaseModel):
    stealth_mode: bool = True
    run_in_background: bool = False
    close_tabs: bool = True
    disable_extensions: bool = True
    safe_mode: bool = True
    smooth_scroll: bool = True
    keep_screen_awake: bool = True
    click_gap: float = 1.0


class GoogleSheetsConfig(BaseModel):
    enabled: bool = False
    spreadsheet_id: str = ""
    credentials_path: str = "credentials/google_sheets_credentials.json"
    sheet_name: str = "Job Applications"
    auto_sync: bool = True
    sync_interval_minutes: int = 30


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///data/job_applications.db"
    echo: bool = False


class AppConfig(BaseSettings):
    """Root application configuration."""
    model_config = {
        "env_prefix": "JOB_AGENT_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",
    }

    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    search: SearchConfig = Field(default_factory=SearchConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    resume: ResumeConfig = Field(default_factory=ResumeConfig)
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    ranking: RankingConfig = Field(default_factory=RankingConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    google_sheets: GoogleSheetsConfig = Field(default_factory=GoogleSheetsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    logs_folder_path: str = "logs"
    screenshots_folder: str = "logs/screenshots"


def load_config() -> AppConfig:
    """Load configuration from environment / .env file."""
    return AppConfig()


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent
