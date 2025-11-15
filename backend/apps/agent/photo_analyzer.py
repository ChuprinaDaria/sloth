"""
Photo Analysis Service for processing client photos with AI

Supports multiple AI providers:
- GPT-4 Vision (OpenAI)
- Claude Opus (Anthropic)
- Claude Sonnet (Anthropic)
- Gemini Pro Vision (Google)
"""
import httpx
import asyncio
from typing import Dict, Optional, Tuple
from django.conf import settings
from apps.integrations.models import UserPhotoRecognitionConfig
from apps.core.utils.encryption import decrypt_api_key
import logging

logger = logging.getLogger(__name__)


class PhotoAnalyzer:
    """Service for analyzing client photos using configured AI providers"""

    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_active_provider_config(self) -> Optional[UserPhotoRecognitionConfig]:
        """
        Get the default active photo recognition configuration for user

        Returns:
            UserPhotoRecognitionConfig or None
        """
        return UserPhotoRecognitionConfig.objects.filter(
            user_id=self.user_id,
            is_active=True,
            is_default=True
        ).select_related('provider').first()

    async def analyze_photo_async(
        self,
        image_url: str,
        analysis_prompt: Optional[str] = None
    ) -> Tuple[bool, str, Dict]:
        """
        Analyze a photo using the configured AI provider

        Args:
            image_url: URL of the photo to analyze
            analysis_prompt: Custom prompt for analysis (optional)

        Returns:
            Tuple of (success, result_text, metadata)
        """
        config = self.get_active_provider_config()

        if not config:
            return False, "No photo recognition provider configured", {}

        # Get provider details
        provider = config.provider
        api_key = decrypt_api_key(config.api_key_encrypted) if config.api_key_encrypted else ''

        # Default analysis prompt
        if not analysis_prompt:
            analysis_prompt = (
                "Analyze this client photo. Describe their hair type, condition, "
                "length, color, and any visible styling or treatments. "
                "Provide professional recommendations for salon services."
            )

        # Route to appropriate provider
        try:
            if provider.slug == 'gpt4_vision':
                success, result = await self._analyze_with_openai(
                    api_key, image_url, analysis_prompt
                )
            elif provider.slug in ['claude_opus', 'claude_sonnet']:
                model = 'claude-3-opus-20240229' if provider.slug == 'claude_opus' else 'claude-3-5-sonnet-20241022'
                success, result = await self._analyze_with_anthropic(
                    api_key, image_url, analysis_prompt, model
                )
            elif provider.slug == 'gemini_pro':
                success, result = await self._analyze_with_google(
                    api_key, image_url, analysis_prompt
                )
            else:
                return False, f"Unsupported provider: {provider.slug}", {}

            if success:
                # Update usage statistics
                config.images_processed += 1
                config.total_cost += float(provider.cost_per_image)
                config.save(update_fields=['images_processed', 'total_cost', 'last_used'])

            metadata = {
                'provider': provider.slug,
                'provider_name': provider.name,
                'cost': float(provider.cost_per_image)
            }

            return success, result, metadata

        except Exception as e:
            logger.error(f"Photo analysis error: {e}")
            return False, f"Analysis failed: {str(e)}", {}

    async def _analyze_with_openai(
        self,
        api_key: str,
        image_url: str,
        prompt: str
    ) -> Tuple[bool, str]:
        """Analyze photo using OpenAI GPT-4 Vision"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4-vision-preview",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_url}
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data['choices'][0]['message']['content']
                    return True, result
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    return False, f"OpenAI API error: {error_msg}"

        except Exception as e:
            return False, f"OpenAI request failed: {str(e)}"

    async def _analyze_with_anthropic(
        self,
        api_key: str,
        image_url: str,
        prompt: str,
        model: str
    ) -> Tuple[bool, str]:
        """Analyze photo using Anthropic Claude"""
        try:
            # Download image to base64 (Claude requires base64)
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Download image
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    return False, "Failed to download image"

                import base64
                image_data = base64.b64encode(img_response.content).decode('utf-8')

                # Detect media type
                content_type = img_response.headers.get('content-type', 'image/jpeg')

                # Analyze with Claude
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model,
                        "max_tokens": 500,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": content_type,
                                            "data": image_data
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data['content'][0]['text']
                    return True, result
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    return False, f"Anthropic API error: {error_msg}"

        except Exception as e:
            return False, f"Anthropic request failed: {str(e)}"

    async def _analyze_with_google(
        self,
        api_key: str,
        image_url: str,
        prompt: str
    ) -> Tuple[bool, str]:
        """Analyze photo using Google Gemini Pro Vision"""
        try:
            # Download image to base64
            async with httpx.AsyncClient(timeout=30.0) as client:
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    return False, "Failed to download image"

                import base64
                image_data = base64.b64encode(img_response.content).decode('utf-8')

                # Analyze with Gemini
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"text": prompt},
                                    {
                                        "inline_data": {
                                            "mime_type": "image/jpeg",
                                            "data": image_data
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data['candidates'][0]['content']['parts'][0]['text']
                    return True, result
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    return False, f"Google API error: {error_msg}"

        except Exception as e:
            return False, f"Google request failed: {str(e)}"

    def analyze_photo(
        self,
        image_url: str,
        analysis_prompt: Optional[str] = None
    ) -> Tuple[bool, str, Dict]:
        """
        Synchronous wrapper for photo analysis

        Args:
            image_url: URL of the photo to analyze
            analysis_prompt: Custom prompt for analysis (optional)

        Returns:
            Tuple of (success, result_text, metadata)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.analyze_photo_async(image_url, analysis_prompt)
            )
            return result
        finally:
            loop.close()
