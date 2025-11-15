import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, Square, Loader, Check, AlertCircle } from 'lucide-react';
import api from '../../api/axios';

const VoiceRecorder = ({ onTranscription }) => {
  const { t } = useTranslation();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [lastTranscription, setLastTranscription] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());

        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Send to backend for transcription
        await transcribeAudio(audioBlob);
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setError('');
      setSuccess('');

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError(t('sandbox.voice.microphoneError'));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      // Stop timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setIsProcessing(true);
    setError('');

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');

      // Send to backend
      const response = await api.post('/agent/voice-to-text/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { text, language } = response.data;

      setLastTranscription({
        text,
        language,
        timestamp: new Date()
      });

      setSuccess(t('sandbox.voice.transcriptionSuccess'));

      // Call callback with transcribed text
      if (onTranscription) {
        onTranscription(text, language);
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);

    } catch (err) {
      console.error('Transcription error:', err);
      setError(
        err.response?.data?.error ||
        t('sandbox.voice.transcriptionError')
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getLanguageFlag = (lang) => {
    const flags = {
      'uk': '🇺🇦',
      'en': '🇬🇧',
      'pl': '🇵🇱',
      'de': '🇩🇪',
      'ru': '🇷🇺'
    };
    return flags[lang] || '🗣️';
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Mic className="text-primary-500" size={20} />
        {t('sandbox.voice.title')}
      </h3>

      <div className="space-y-4">
        {/* Recording Controls */}
        <div className="flex items-center justify-center">
          {!isRecording && !isProcessing && (
            <button
              onClick={startRecording}
              className="btn-primary flex items-center gap-2 px-6 py-3 text-lg"
            >
              <Mic size={24} />
              {t('sandbox.voice.startRecording')}
            </button>
          )}

          {isRecording && (
            <div className="text-center">
              <button
                onClick={stopRecording}
                className="btn-danger flex items-center gap-2 px-6 py-3 text-lg mb-3"
              >
                <Square size={24} />
                {t('sandbox.voice.stopRecording')}
              </button>

              {/* Recording indicator with pulsing animation */}
              <div className="flex items-center justify-center gap-2 text-red-500">
                <div className="relative">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
                </div>
                <span className="font-mono text-lg">{formatTime(recordingTime)}</span>
              </div>
            </div>
          )}

          {isProcessing && (
            <div className="flex items-center gap-2 text-primary-500">
              <Loader className="animate-spin" size={24} />
              <span>{t('sandbox.voice.processing')}</span>
            </div>
          )}
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-green-800">
              <Check size={18} />
              <span className="text-sm">{success}</span>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle size={18} />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Last Transcription */}
        {lastTranscription && (
          <div className="border-t pt-4">
            <div className="text-sm text-gray-600 mb-2 flex items-center gap-2">
              <span>{t('sandbox.voice.lastTranscription')}:</span>
              <span className="text-lg">{getLanguageFlag(lastTranscription.language)}</span>
              <span className="font-medium">{lastTranscription.language.toUpperCase()}</span>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <p className="text-sm">{lastTranscription.text}</p>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-500 border-t pt-4">
          <p>{t('sandbox.voice.instructions')}</p>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;
