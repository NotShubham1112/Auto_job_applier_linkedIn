from __future__ import annotations

import json
import logging
from typing import Any, Optional

from groq import Groq

from config.settings import AIConfig, GroqModel

logger = logging.getLogger(__name__)


class GroqService:
    """Reusable Groq API service supporting multiple models."""

    def __init__(self, config: AIConfig) -> None:
        self.config = config
        self._client: Optional[Groq] = None

    def _get_client(self) -> Groq:
        if self._client is None:
            if not self.config.groq_api_key:
                raise ValueError("GROQ_API_KEY not set in configuration")
            self._client = Groq(api_key=self.config.groq_api_key)
        return self._client

    def completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        client = self._get_client()
        model = model or self.config.groq_model.value
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            logger.error("Groq API error: %s", e)
            raise

    def completion_json(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
    ) -> dict:
        raw = self.completion(messages, model=model, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown fences
            if "```json" in raw:
                start = raw.index("```json") + 7
                end = raw.index("```", start)
                return json.loads(raw[start:end])
            if "```" in raw:
                start = raw.index("```") + 3
                end = raw.index("```", start)
                return json.loads(raw[start:end])
            raise

    def streaming_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Stream tokens from Groq. Yields strings."""
        client = self._get_client()
        model = model or self.config.groq_model.value
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error("Groq streaming error: %s", e)
            raise

    def close(self) -> None:
        self._client = None

    # ------------------------------------------------------------------
    # High-level AI tasks
    # ------------------------------------------------------------------

    def extract_skills(self, job_description: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert skill extractor. Extract skills from job descriptions. "
                    "Return JSON with keys: tech_stack, technical_skills, other_skills, "
                    "required_skills, nice_to_have. Each key maps to a list of strings."
                ),
            },
            {
                "role": "user",
                "content": f"Extract skills from this job description:\n\n{job_description}",
            },
        ]
        return self.completion_json(messages)

    def answer_application_question(
        self,
        question: str,
        user_info: str,
        job_description: str = "",
        job_title: str = "",
        company: str = "",
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a job application assistant. Answer the question concisely "
                    "and professionally using only the provided user information. "
                    "Never fabricate experience, skills, or credentials. "
                    "Keep answers brief (1-3 sentences). "
                    "If you cannot answer from the provided info, say 'I cannot answer this question from the provided information.'"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Profile:\n{user_info}\n\n"
                    f"Job: {job_title} at {company}\n"
                    f"Job Description:\n{job_description}\n\n"
                    f"Question: {question}\n\n"
                    f"Answer:"
                ),
            },
        ]
        return self.completion(messages, max_tokens=256)

    def rank_job(self, job_data: dict, candidate_profile: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert job ranking agent. Score how well a job matches "
                    "the candidate profile. Return JSON with: score (0-100), "
                    "skill_match (0-100), resume_match (0-100), remote_match (0-100), "
                    "experience_match (0-100), startup_match (0-100), salary_match (0-100), "
                    "reasoning (string explaining the score)."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Profile:\n{candidate_profile}\n\n"
                    f"Job Details:\n{json.dumps(job_data, indent=2)}\n\n"
                    f"Score this job match:"
                ),
            },
        ]
        return self.completion_json(messages)

    def generate_resume_summary(
        self, job_description: str, candidate_profile: str, job_title: str, company: str
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a resume tailoring expert. Generate a concise resume summary "
                    "(3-4 sentences) optimized for the specific job. "
                    "Use ONLY factual information from the candidate profile. "
                    "Never invent skills, experience, or achievements. "
                    "Highlight the most relevant experience and skills for this role."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Profile:\n{candidate_profile}\n\n"
                    f"Job: {job_title} at {company}\n"
                    f"Job Description:\n{job_description}\n\n"
                    f"Generate tailored resume summary:"
                ),
            },
        ]
        return self.completion(messages, max_tokens=512)

    def generate_cover_letter(
        self, job_description: str, candidate_profile: str, job_title: str, company: str
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a cover letter writer. Generate a compelling, concise cover letter "
                    "(250-350 words) for the specific job. "
                    "Use ONLY factual information from the candidate profile. "
                    "Structure: Opening (show enthusiasm + role), Body (2-3 paragraphs connecting "
                    "experience to requirements), Closing (call to action). "
                    "Tone: Professional but genuine. Avoid generic statements and buzzwords."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Profile:\n{candidate_profile}\n\n"
                    f"Job: {job_title} at {company}\n"
                    f"Job Description:\n{job_description}\n\n"
                    f"Generate cover letter:"
                ),
            },
        ]
        return self.completion(messages, max_tokens=1024)

    def decide_application(self, job_data: dict, ranking: dict, candidate_profile: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent application decision agent. Analyze the job, "
                    "ranking, and candidate fit to decide whether to apply. "
                    "Return JSON with: decision (APPLY/SKIP/REVIEW), confidence (0.0-1.0), "
                    "reasoning (detailed explanation). "
                    "APPLY: high confidence match, worth applying. "
                    "SKIP: poor match, waste of time. "
                    "REVIEW: borderline, needs human review."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate Profile:\n{candidate_profile}\n\n"
                    f"Job: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}\n"
                    f"Description:\n{job_data.get('description', '')}\n\n"
                    f"Ranking Score: {ranking.get('score', 0)}/100\n"
                    f"Breakdown: {json.dumps(ranking, indent=2)}\n\n"
                    f"Should we apply? Analyze and decide:"
                ),
            },
        ]
        return self.completion_json(messages)
