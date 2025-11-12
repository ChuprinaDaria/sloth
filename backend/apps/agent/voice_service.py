"""
Voice Service - TTS/STT with OpenAI Whisper and TTS
"""
import os
import time
from pathlib import Path
from openai import OpenAI
from django.conf import settings
from .models import VoiceSettings, VoiceMessage, Message


class VoiceService:
    """
    Сервіс для роботи з голосовими повідомленнями
    - STT (Speech-to-Text) через OpenAI Whisper
    - TTS (Text-to-Speech) через OpenAI TTS
    - Voice cloning через ElevenLabs (для преміум)
    """

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')

    def get_or_create_settings(self):
        """Get or create voice settings for user"""
        settings, _ = VoiceSettings.objects.get_or_create(
            user_id=self.user_id,
            defaults={
                'voice_name': 'nova',
                'tts_enabled': True,
                'stt_enabled': True,
                'auto_detect_language': True,
                'preferred_language': 'uk'
            }
        )
        return settings

    def transcribe_audio(self, audio_file_path, language=None):
        """
        Розпізнати голос → текст (STT)

        Args:
            audio_file_path: шлях до аудіо файлу
            language: мова (uk, en, pl, de) або None для auto-detect

        Returns:
            dict: {
                'text': розпізнаний текст,
                'language': виявлена мова,
                'duration': тривалість обробки
            }
        """
        start_time = time.time()

        try:
            settings = self.get_or_create_settings()

            # Відкрити аудіо файл
            with open(audio_file_path, 'rb') as audio_file:
                # Використовуємо OpenAI Whisper API
                if language and not settings.auto_detect_language:
                    # Якщо вказана мова
                    transcription = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json"
                    )
                else:
                    # Auto-detect мови
                    transcription = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json"
                    )

            # Визначити мову
            detected_language = transcription.language if hasattr(transcription, 'language') else 'uk'

            return {
                'text': transcription.text,
                'language': detected_language,
                'duration': time.time() - start_time,
                'success': True
            }

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return {
                'text': '',
                'language': 'uk',
                'duration': time.time() - start_time,
                'success': False,
                'error': str(e)
            }

    def generate_speech(self, text, voice_name=None, speed=1.0):
        """
        Згенерувати голос з тексту (TTS)

        Args:
            text: текст для озвучення
            voice_name: ім'я голосу (alloy, echo, fable, onyx, nova, shimmer)
            speed: швидкість (0.25 - 4.0)

        Returns:
            dict: {
                'audio_path': шлях до згенерованого аудіо,
                'duration': тривалість генерації,
                'voice_used': використаний голос
            }
        """
        start_time = time.time()

        try:
            settings = self.get_or_create_settings()

            # Визначити голос
            if voice_name is None:
                voice_name = settings.get_voice_name()

            # Якщо це клонований голос - використати ElevenLabs
            if settings.is_cloned and self.elevenlabs_api_key:
                return self._generate_speech_elevenlabs(text, settings.cloned_voice_id, speed)

            # Використати OpenAI TTS
            response = self.openai_client.audio.speech.create(
                model="tts-1-hd",  # or tts-1 for faster/cheaper
                voice=voice_name,
                input=text,
                speed=speed
            )

            # Зберегти аудіо файл
            output_dir = Path(settings.MEDIA_ROOT) / 'voice' / self.tenant_schema
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time() * 1000)
            audio_filename = f"tts_{self.user_id}_{timestamp}.mp3"
            audio_path = output_dir / audio_filename

            # Записати аудіо
            response.stream_to_file(str(audio_path))

            return {
                'audio_path': str(audio_path),
                'relative_path': f"voice/{self.tenant_schema}/{audio_filename}",
                'duration': time.time() - start_time,
                'voice_used': voice_name,
                'success': True
            }

        except Exception as e:
            print(f"Error generating speech: {e}")
            return {
                'audio_path': None,
                'duration': time.time() - start_time,
                'voice_used': voice_name,
                'success': False,
                'error': str(e)
            }

    def _generate_speech_elevenlabs(self, text, voice_id, speed=1.0):
        """
        Генерація голосу через ElevenLabs (клоновані голоси)
        """
        try:
            import requests

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }

            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "speed": speed
                }
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                # Зберегти аудіо
                output_dir = Path(settings.MEDIA_ROOT) / 'voice' / self.tenant_schema
                output_dir.mkdir(parents=True, exist_ok=True)

                timestamp = int(time.time() * 1000)
                audio_filename = f"tts_cloned_{self.user_id}_{timestamp}.mp3"
                audio_path = output_dir / audio_filename

                with open(audio_path, 'wb') as f:
                    f.write(response.content)

                return {
                    'audio_path': str(audio_path),
                    'relative_path': f"voice/{self.tenant_schema}/{audio_filename}",
                    'voice_used': f"cloned_{voice_id}",
                    'success': True
                }
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code}")

        except Exception as e:
            print(f"Error with ElevenLabs: {e}")
            # Fallback to OpenAI TTS
            return self.generate_speech(text, voice_name='nova', speed=speed)

    def clone_voice(self, audio_samples):
        """
        Клонувати голос користувача (тільки для преміум підписки)

        Args:
            audio_samples: список шляхів до аудіо зразків (мінімум 1 хвилина)

        Returns:
            dict: {
                'voice_id': ID клонованого голосу,
                'success': True/False
            }
        """
        try:
            # Перевірити підписку
            from apps.subscriptions.models import Subscription
            from apps.accounts.models import User

            user = User.objects.get(id=self.user_id)
            if not user.organization:
                return {'success': False, 'error': 'No organization'}

            subscription = user.organization.subscription
            # Перевірити чи це преміум план (не FREE)
            if subscription.is_free_plan():
                return {
                    'success': False,
                    'error': 'Voice cloning requires premium subscription'
                }

            # Використати ElevenLabs Voice Cloning API
            import requests

            url = "https://api.elevenlabs.io/v1/voices/add"
            headers = {
                "xi-api-key": self.elevenlabs_api_key
            }

            files = []
            for sample_path in audio_samples:
                files.append(('files', open(sample_path, 'rb')))

            data = {
                'name': f'User_{self.user_id}_Voice',
                'description': f'Cloned voice for user {self.user_id}'
            }

            response = requests.post(url, headers=headers, data=data, files=files)

            # Закрити файли
            for _, file_obj in files:
                file_obj.close()

            if response.status_code == 200:
                voice_data = response.json()
                voice_id = voice_data.get('voice_id')

                # Зберегти в налаштуваннях
                settings = self.get_or_create_settings()
                settings.is_cloned = True
                settings.cloned_voice_id = voice_id
                settings.cloned_voice_sample_path = audio_samples[0] if audio_samples else ''
                settings.save()

                return {
                    'success': True,
                    'voice_id': voice_id
                }
            else:
                return {
                    'success': False,
                    'error': f'ElevenLabs error: {response.text}'
                }

        except Exception as e:
            print(f"Error cloning voice: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_voice_message(self, message_id, audio_file_path, is_from_user=True):
        """
        Обробити голосове повідомлення

        Args:
            message_id: ID повідомлення
            audio_file_path: шлях до аудіо
            is_from_user: True якщо від користувача, False якщо згенероване AI

        Returns:
            VoiceMessage object
        """
        try:
            message = Message.objects.get(id=message_id)
            settings = self.get_or_create_settings()

            if is_from_user and settings.stt_enabled:
                # Розпізнати голос
                transcription = self.transcribe_audio(
                    audio_file_path,
                    language=settings.preferred_language if not settings.auto_detect_language else None
                )

                # Створити VoiceMessage
                voice_msg = VoiceMessage.objects.create(
                    message=message,
                    audio_file_path=audio_file_path,
                    audio_duration=0.0,  # TODO: get actual duration
                    transcribed_text=transcription['text'],
                    detected_language=transcription['language'],
                    is_generated=False
                )

                # Оновити content повідомлення
                if not message.content:
                    message.content = transcription['text']
                    message.save()

                return voice_msg

            else:
                # Це згенероване AI голосове повідомлення
                voice_msg = VoiceMessage.objects.create(
                    message=message,
                    audio_file_path=audio_file_path,
                    audio_duration=0.0,
                    is_generated=True,
                    voice_used=settings.get_voice_name()
                )

                return voice_msg

        except Exception as e:
            print(f"Error processing voice message: {e}")
            return None

    def should_respond_with_voice(self, conversation_source):
        """
        Визначити чи потрібно відповідати голосом

        Args:
            conversation_source: telegram, whatsapp, web

        Returns:
            bool
        """
        settings = self.get_or_create_settings()

        if not settings.tts_enabled:
            return False

        # Перевірити налаштування для конкретного месенджера
        if conversation_source == 'telegram':
            return settings.telegram_voice_enabled
        elif conversation_source == 'whatsapp':
            return settings.whatsapp_voice_enabled
        elif conversation_source == 'web':
            return settings.web_voice_enabled

        return False
