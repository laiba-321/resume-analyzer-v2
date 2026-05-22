import json
import os
import re

import ollama
import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def build_prompt(text: str) -> str:
    return f"""
You are an expert resume reviewer.

Return ONLY valid JSON. No markdown. No explanation outside JSON.

Format:
{{
  "score": 0,
  "summary": "short summary",
  "suggestions": ["point1", "point2"],
  "skills": ["skill1", "skill2"]
}}

Rules:
- score must be between 0 and 100
- suggestions must be practical and short
- skills must be extracted from resume only

Resume:
{text}
"""


def clean_json_response(raw: str) -> dict:
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)


def analyze_with_ollama(text: str) -> dict:
    response = ollama.chat(
        model="gemma3:1b",
        messages=[{"role": "user", "content": build_prompt(text)}]
    )

    raw = response["message"]["content"]
    return clean_json_response(raw)


def analyze_with_openai(text: str) -> dict:
    if not client:
        raise ValueError("OPENAI_API_KEY is missing")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=build_prompt(text)
    )

    raw = response.output_text
    return clean_json_response(raw)


def analyze_with_gemini(text: str) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(build_prompt(text))

    raw = response.text
    return clean_json_response(raw)


def analyze_resume_with_ai(text: str, provider: str | None = None) -> dict:
    selected_provider = provider or DEFAULT_PROVIDER

    if selected_provider == "gemini":
        return analyze_with_gemini(text)

    if selected_provider == "openai":
        return analyze_with_openai(text)

    if selected_provider == "ollama":
        return analyze_with_ollama(text)

    raise ValueError(f"Unsupported provider: {selected_provider}")