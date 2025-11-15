"""
Voice Recognition Service using OpenAI Whisper API

Supports automatic language detection and high-quality transcription
for voice messages from Telegram, Instagram, and Sandbox
"""
import httpx
import asyncio
import logging
from typing import Tuple, Optional
from django.conf import settings
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


class VoiceRecognitionService:
    """Service for converting voice messages to text using OpenAI Whisper"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize service with API key

        Args:
            api_key: OpenAI API key (uses settings.OPENAI_API_KEY if not provided)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY

    async def transcribe_audio_async(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Transcribe audio file to text using OpenAI Whisper

        Args:
            audio_file_path: Path to audio file
            language: Optional language code (ISO-639-1). If None, auto-detects
            prompt: Optional prompt to guide transcription style

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()

            # Determine file extension
            file_extension = Path(audio_file_path).suffix or '.mp3'
            filename = f"audio{file_extension}"

            # Prepare request data
            files = {
                'file': (filename, audio_data, 'audio/mpeg')
            }

            data = {
                'model': 'whisper-1',
            }

            # Add optional parameters
            if language:
                data['language'] = language

            if prompt:
                data['prompt'] = prompt

            # Make request to OpenAI Whisper API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    files=files,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result.get('text', '')
                    detected_language = result.get('language', language or 'unknown')

                    logger.info(
                        f"Successfully transcribed audio. "
                        f"Language: {detected_language}, Length: {len(text)} chars"
                    )

                    return True, text, detected_language
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    logger.error(f"Whisper API error: {error_msg}")
                    return False, f"Transcription failed: {error_msg}", 'unknown'

        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_file_path}")
            return False, "Audio file not found", 'unknown'
        except Exception as e:
            logger.error(f"Voice transcription error: {e}")
            return False, f"Transcription error: {str(e)}", 'unknown'

    def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Synchronous wrapper for audio transcription

        Args:
            audio_file_path: Path to audio file
            language: Optional language code (ISO-639-1)
            prompt: Optional prompt to guide transcription

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.transcribe_audio_async(audio_file_path, language, prompt)
            )
            return result
        finally:
            loop.close()

    async def transcribe_audio_url_async(
        self,
        audio_url: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Download audio from URL and transcribe

        Args:
            audio_url: URL to audio file
            language: Optional language code
            prompt: Optional transcription prompt

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        try:
            # Download audio file
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(audio_url)

                if response.status_code != 200:
                    return False, "Failed to download audio file", 'unknown'

                # Detect file extension from content-type or URL
                content_type = response.headers.get('content-type', '')
                if 'ogg' in content_type or audio_url.endswith('.ogg'):
                    extension = '.ogg'
                elif 'mp4' in content_type or audio_url.endswith('.mp4'):
                    extension = '.mp4'
                elif 'webm' in content_type or audio_url.endswith('.webm'):
                    extension = '.webm'
                else:
                    extension = '.mp3'

                # Save to temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=extension
                ) as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name

            # Transcribe
            success, text, detected_lang = await self.transcribe_audio_async(
                temp_file_path,
                language,
                prompt
            )

            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

            return success, text, detected_lang

        except Exception as e:
            logger.error(f"Error transcribing from URL: {e}")
            return False, f"Download/transcription error: {str(e)}", 'unknown'

    def transcribe_audio_url(
        self,
        audio_url: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Synchronous wrapper for URL transcription

        Args:
            audio_url: URL to audio file
            language: Optional language code
            prompt: Optional transcription prompt

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.transcribe_audio_url_async(audio_url, language, prompt)
            )
            return result
        finally:
            loop.close()

    async def transcribe_audio_bytes_async(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Transcribe audio from bytes

        Args:
            audio_bytes: Audio file content as bytes
            filename: Original filename (for extension detection)
            language: Optional language code
            prompt: Optional transcription prompt

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        try:
            # Detect extension from filename
            extension = Path(filename).suffix or '.mp3'

            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            # Transcribe
            success, text, detected_lang = await self.transcribe_audio_async(
                temp_file_path,
                language,
                prompt
            )

            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

            return success, text, detected_lang

        except Exception as e:
            logger.error(f"Error transcribing from bytes: {e}")
            return False, f"Transcription error: {str(e)}", 'unknown'

    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Synchronous wrapper for bytes transcription

        Args:
            audio_bytes: Audio file content as bytes
            filename: Original filename
            language: Optional language code
            prompt: Optional transcription prompt

        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.transcribe_audio_bytes_async(audio_bytes, filename, language, prompt)
            )
            return result
        finally:
            loop.close()
