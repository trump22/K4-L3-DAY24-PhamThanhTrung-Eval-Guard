"""OpenAI-compatible provider adapter for the imported Day18 enrichment module."""
from config import OPENAI_API_KEY


def has_api_key():
    return bool(OPENAI_API_KEY)


def create_client():
    from openai import OpenAI
    return OpenAI(timeout=60, max_retries=3)
