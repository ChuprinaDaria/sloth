"""
API key validators for different photo recognition providers
"""
import httpx
import asyncio
from typing import Tuple


async def test_openai_key(api_key: str) -> Tuple[bool, str]:
    """
    Test OpenAI API key

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )

            if response.status_code == 200:
                return True, "API key is valid"
            elif response.status_code == 401:
                return False, "Invalid API key"
            else:
                return False, f"Unexpected response: {response.status_code}"

    except httpx.TimeoutException:
        return False, "Request timeout - please try again"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


async def test_anthropic_key(api_key: str) -> Tuple[bool, str]:
    """
    Test Anthropic Claude API key

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        async with httpx.AsyncClient() as client:
            # Test with a minimal request
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "test"}]
                },
                timeout=10.0
            )

            if response.status_code in [200, 400]:  # 400 means key is valid but request invalid
                return True, "API key is valid"
            elif response.status_code == 401:
                return False, "Invalid API key"
            else:
                return False, f"Unexpected response: {response.status_code}"

    except httpx.TimeoutException:
        return False, "Request timeout - please try again"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


async def test_google_key(api_key: str) -> Tuple[bool, str]:
    """
    Test Google Gemini API key

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=10.0
            )

            if response.status_code == 200:
                return True, "API key is valid"
            elif response.status_code == 400:
                return False, "Invalid API key"
            else:
                return False, f"Unexpected response: {response.status_code}"

    except httpx.TimeoutException:
        return False, "Request timeout - please try again"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def test_provider_key_sync(provider_slug: str, api_key: str) -> Tuple[bool, str]:
    """
    Synchronous wrapper for testing provider API keys

    Args:
        provider_slug: Provider identifier
        api_key: API key to test

    Returns:
        Tuple of (is_valid, error_message)
    """
    validators = {
        'gpt4_vision': test_openai_key,
        'claude_opus': test_anthropic_key,
        'claude_sonnet': test_anthropic_key,
        'gemini_pro': test_google_key,
    }

    validator = validators.get(provider_slug)

    if not validator:
        return True, "Validation not implemented for this provider"

    try:
        # Run async validator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(validator(api_key))
        loop.close()
        return result
    except Exception as e:
        return False, f"Validation error: {str(e)}"
