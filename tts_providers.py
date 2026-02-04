"""
TTS Provider implementations for benchmarking
"""
import time
import asyncio
import aiohttp
import requests
import ssl
import certifi
from typing import Dict, Any, Optional, Tuple, AsyncGenerator
from dataclasses import dataclass
from abc import ABC, abstractmethod
import io
import json
from config import get_api_key, TTS_PROVIDERS

def get_ssl_context():
    """Create SSL context with proper certificate handling"""
    try:
        # Try to use certifi certificates first
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        return ssl_context
    except Exception:
        # Fallback to no verification if certifi fails
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

def get_connector():
    """Create aiohttp connector with SSL handling"""
    ssl_context = get_ssl_context()
    return aiohttp.TCPConnector(ssl=ssl_context)

@dataclass
class TTSResult:
    """Result from TTS generation"""
    success: bool
    audio_data: Optional[bytes]
    latency_ms: float
    file_size_bytes: int
    error_message: Optional[str]
    metadata: Dict[str, Any]
    latency_1: float = 0.0  # Network latency (pure RTT) without TTS processing

@dataclass
class TTSRequest:
    """TTS generation request"""
    text: str
    voice: str
    provider: str
    model: Optional[str] = None
    speed: float = 1.0
    format: str = "mp3"

class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self.config = TTS_PROVIDERS[provider_id]
        self.api_key = get_api_key(provider_id)
    
    @abstractmethod
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech from text"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        pass
    
    def validate_request(self, request: TTSRequest) -> Tuple[bool, str]:
        """Validate TTS request"""
        if len(request.text) > self.config.max_chars:
            return False, f"Text exceeds maximum length of {self.config.max_chars} characters"
        
        if request.voice not in self.config.supported_voices:
            return False, f"Voice '{request.voice}' not supported. Available: {self.config.supported_voices}"
        
        return True, ""
    
    async def measure_ping_latency(self) -> float:
        """Measure pure network latency (RTT) without TTS processing"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                # Send a minimal HEAD or OPTIONS request to measure pure network latency
                async with session.head(
                    self.config.base_url,
                    headers={"api-key": self.api_key} if "murf" in self.provider_id else {"Authorization": f"Token {self.api_key}"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    return latency_ms
        except:
            # If HEAD doesn't work, fallback to minimal GET/POST
            try:
                start_time = time.time()
                async with aiohttp.ClientSession(connector=get_connector()) as session:
                    async with session.get(
                        self.config.base_url.replace("/v1/speech/", "/").replace("turbo-stream", "").replace("stream", "").rstrip("/"),
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        latency_ms = (time.time() - start_time) * 1000
                        return latency_ms
            except:
                return 0.0  # Return 0 if ping fails

class MurfFalconOct23TTSProvider(TTSProvider):
    """Murf Falcon Oct 23 TTS provider implementation (Global Stream Endpoint)"""
    
    def __init__(self):
        super().__init__("murf_falcon_oct23")
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using Murf Falcon Oct 23 API (Global Stream)"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Murf Falcon API payload structure (matching API docs)
        # Extract locale from voice_id (e.g., "en-US-matthew" -> "en-US")
        voice_locale = request.voice.split("-", 2)[0] + "-" + request.voice.split("-", 2)[1] if "-" in request.voice else "en-US"
        
        payload = {
            "voice_id": request.voice,
            "text": request.text,
            "multi_native_locale": voice_locale,
            "model": "FALCON",
            "format": "MP3",
            "sampleRate": 24000,
            "channelType": "MONO"
        }
        
        # Add speed/rate if specified
        if request.speed and request.speed != 1.0:
            payload["rate"] = request.speed
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        file_size = len(audio_data)
                        
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=file_size,
                            error_message=None,
                            metadata={
                                "provider": self.provider_id,
                                "model": "FALCON",
                                "voice": request.voice,
                                "format": request.format or "mp3"
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available Murf Falcon Oct 23 voices"""
        return self.config.supported_voices

class DeepgramTTSProvider(TTSProvider):
    """Deepgram Aura 1 TTS provider implementation"""
    
    def __init__(self):
        super().__init__("deepgram")
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using Deepgram TTS API"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Deepgram TTS API payload structure
        payload = {
            "text": request.text
        }
        
        # Add query parameters to URL
        params = {
            "model": request.voice,
            "encoding": "mp3" if request.format == "mp3" else "linear16"
        }
        
        # Only add sample_rate for non-MP3 formats
        if request.format != "mp3":
            params["sample_rate"] = "24000"
        
        # Build URL with parameters
        url_with_params = f"{self.config.base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    url_with_params,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # Deepgram returns audio data directly
                        audio_data = await response.read()
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "speed": request.speed,
                                "format": request.format,
                                "provider": self.provider_id,
                                "model": request.voice,
                                "sample_rate": 24000
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available Deepgram voices"""
        return self.config.supported_voices

class DeepgramAura2TTSProvider(TTSProvider):
    """Deepgram Aura 2 TTS provider implementation"""
    
    def __init__(self):
        super().__init__("deepgram_aura2")
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using Deepgram Aura 2 TTS API"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Deepgram Aura 2 TTS API payload structure
        payload = {
            "text": request.text
        }
        
        # Add query parameters to URL
        params = {
            "model": request.voice,
            "encoding": "mp3" if request.format == "mp3" else "linear16"
        }
        
        # Only add sample_rate for non-MP3 formats
        if request.format != "mp3":
            params["sample_rate"] = "24000"
        
        # Build URL with parameters
        url_with_params = f"{self.config.base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    url_with_params,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # Deepgram returns audio data directly
                        audio_data = await response.read()
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "speed": request.speed,
                                "format": request.format,
                                "provider": self.provider_id,
                                "model": request.voice,
                                "sample_rate": 24000
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available Deepgram Aura 2 voices"""
        return self.config.supported_voices

class ElevenLabsFlashTTSProvider(TTSProvider):
    """ElevenLabs Flash TTS provider implementation"""
    
    def __init__(self):
        super().__init__("elevenlabs_flash")
        # Map friendly voice names to voice IDs (based on Artificial Analysis methodology)
        # Only voices listed on https://artificialanalysis.ai/text-to-speech/methodology
        # Turbo v2.5: Laura, Jessica, Liam, Elizabeth, Shelley, Dan, Nathaniel
        # Fallback voice IDs (from Artificial Analysis - may not work for all accounts)
        self.fallback_voice_id_map = {
            "Laura": "FGY2WhTYpPnrIDTdsKH5",
            "Jessica": "cgSgspJ2msm6clMCkdW9",
            "Liam": "TX3LPaxmHKxFdv7VOQHJ",
            "Elizabeth": "MF3mGyEYCl7XYWbV9V6O",
            "Shelley": "DWAVQCwqGrmKZMpKIqGa",
            "Dan": "TxGEqnHWrfWFTfGW9XjX",
            "Nathaniel": "N2lVS1w4EtoT3dr4eOWO"
        }
        # Will be populated with actual voice IDs from user's account
        self.voice_id_map = {}
        self._voices_fetched = False
    
    async def _fetch_voices_from_api(self):
        """Fetch available voices from ElevenLabs API and map them by name"""
        if self._voices_fetched:
            return
        
        try:
            headers = {"xi-api-key": self.api_key}
            voices_url = "https://api.elevenlabs.io/v1/voices"
            
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.get(
                    voices_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        voices_data = await response.json()
                        # Map voice names to their IDs
                        for voice in voices_data.get("voices", []):
                            voice_name = voice.get("name", "")
                            voice_id = voice.get("voice_id", "")
                            if voice_name and voice_id:
                                self.voice_id_map[voice_name] = voice_id
                        
                        # If we found voices, use them; otherwise fall back to hardcoded IDs
                        if not self.voice_id_map:
                            print("Warning: No voices found from API, using fallback IDs")
                            self.voice_id_map = self.fallback_voice_id_map.copy()
                        else:
                            print(f"Successfully fetched {len(self.voice_id_map)} voices from ElevenLabs API")
                            # Also check if any expected voices are missing
                            missing_voices = set(self.fallback_voice_id_map.keys()) - set(self.voice_id_map.keys())
                            if missing_voices:
                                print(f"Warning: Some expected voices not found in account: {missing_voices}")
                    else:
                        print(f"Failed to fetch voices from API (status {response.status}), using fallback IDs")
                        self.voice_id_map = self.fallback_voice_id_map.copy()
        except Exception as e:
            print(f"Error fetching voices from API: {e}, using fallback IDs")
            self.voice_id_map = self.fallback_voice_id_map.copy()
        
        self._voices_fetched = True
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using ElevenLabs TTS API"""
        start_time = time.time()
        
        # Fetch voices from API if not already fetched
        if not self._voices_fetched:
            await self._fetch_voices_from_api()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        # Validate voice exists in supported voices
        if request.voice not in self.config.supported_voices:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=f"Voice '{request.voice}' not in supported voices: {self.config.supported_voices}",
                metadata={"provider": self.provider_id}
            )
        
        # Get voice ID from map - try fetched IDs first, then fallback
        voice_id = self.voice_id_map.get(request.voice)
        if not voice_id:
            # Try fallback map
            voice_id = self.fallback_voice_id_map.get(request.voice)
            if not voice_id:
                return TTSResult(
                    success=False,
                    audio_data=None,
                    latency_ms=0,
                    file_size_bytes=0,
                    error_message=f"Voice '{request.voice}' not found in your ElevenLabs account. Available voices: {list(self.voice_id_map.keys())}",
                    metadata={"provider": self.provider_id, "available_voices": list(self.voice_id_map.keys())}
                )
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # ElevenLabs API payload structure
        payload = {
            "text": request.text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Build URL with voice ID
        url = f"{self.config.base_url}/{voice_id}"
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # ElevenLabs returns audio data directly
                        audio_data = await response.read()
                        if len(audio_data) == 0:
                            return TTSResult(
                                success=False,
                                audio_data=None,
                                latency_ms=latency_ms,
                                file_size_bytes=0,
                                error_message="Empty audio response from API",
                                metadata={"provider": self.provider_id, "voice": request.voice, "voice_id": voice_id}
                            )
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "voice_id": voice_id,
                                "model": "eleven_flash_v2_5",
                                "provider": self.provider_id,
                                "format": "mp3_44100_128"
                            }
                        )
                    elif response.status == 404:
                        # Voice ID not found - try to fetch available voices and find matching voice
                        try:
                            async with session.get(
                                f"{self.config.base_url.replace('/text-to-speech', '/voices')}",
                                headers={"xi-api-key": self.api_key},
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as voices_response:
                                if voices_response.status == 200:
                                    voices_data = await voices_response.json()
                                    # Try to find voice by name
                                    for voice in voices_data.get("voices", []):
                                        if voice.get("name") == request.voice:
                                            # Found matching voice, retry with correct ID
                                            correct_voice_id = voice.get("voice_id")
                                            if correct_voice_id:
                                                # Retry with correct voice ID
                                                retry_url = f"{self.config.base_url}/{correct_voice_id}"
                                                async with session.post(
                                                    retry_url,
                                                    headers=headers,
                                                    json=payload,
                                                    timeout=aiohttp.ClientTimeout(total=30)
                                                ) as retry_response:
                                                    if retry_response.status == 200:
                                                        audio_data = await retry_response.read()
                                                        if len(audio_data) > 0:
                                                            return TTSResult(
                                                                success=True,
                                                                audio_data=audio_data,
                                                                latency_ms=(time.time() - start_time) * 1000,
                                                                file_size_bytes=len(audio_data),
                                                                error_message=None,
                                                                metadata={
                                                                    "voice": request.voice,
                                                                    "voice_id": correct_voice_id,
                                                                    "model": "eleven_flash_v2_5",
                                                                    "provider": self.provider_id,
                                                                    "format": "mp3_44100_128"
                                                                }
                                                            )
                        except:
                            pass  # Fall through to error
                        
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"Voice '{request.voice}' not found in your account. Voice ID {voice_id} doesn't exist. Please check your ElevenLabs account has this voice available.",
                            metadata={"provider": self.provider_id, "voice": request.voice, "voice_id": voice_id, "status": response.status}
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text[:200]} (Voice: {request.voice}, Voice ID: {voice_id})",
                            metadata={"provider": self.provider_id, "voice": request.voice, "voice_id": voice_id, "status": response.status}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Request timeout (Voice: {request.voice})",
                metadata={"provider": self.provider_id, "voice": request.voice}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)} (Voice: {request.voice}, Voice ID: {voice_id})",
                metadata={"provider": self.provider_id, "voice": request.voice, "voice_id": voice_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available ElevenLabs Flash voices - returns actual voices from account if fetched, otherwise config voices"""
        # If voices have been fetched from API, return those (account-specific voices)
        if self.voice_id_map:
            return list(self.voice_id_map.keys())
        # Otherwise return config voices (fallback)
        return self.config.supported_voices

class ElevenLabsV3TTSProvider(TTSProvider):
    """ElevenLabs v3 TTS provider implementation"""
    
    def __init__(self):
        super().__init__("elevenlabs_v3")
        # Map friendly voice names to voice IDs (based on Artificial Analysis methodology)
        # Only voices listed on https://artificialanalysis.ai/text-to-speech/methodology
        # Turbo v2.5: Laura, Jessica, Liam, Elizabeth, Shelley, Dan, Nathaniel
        # Fallback voice IDs (from Artificial Analysis - may not work for all accounts)
        self.fallback_voice_id_map = {
            "Laura": "FGY2WhTYpPnrIDTdsKH5",
            "Jessica": "cgSgspJ2msm6clMCkdW9",
            "Liam": "TX3LPaxmHKxFdv7VOQHJ",
            "Elizabeth": "MF3mGyEYCl7XYWbV9V6O",
            "Shelley": "DWAVQCwqGrmKZMpKIqGa",
            "Dan": "TxGEqnHWrfWFTfGW9XjX",
            "Nathaniel": "N2lVS1w4EtoT3dr4eOWO"
        }
        # Will be populated with actual voice IDs from user's account
        self.voice_id_map = {}
        self._voices_fetched = False
    
    async def _fetch_voices_from_api(self):
        """Fetch available voices from ElevenLabs API and map them by name"""
        if self._voices_fetched:
            return
        
        try:
            headers = {"xi-api-key": self.api_key}
            voices_url = "https://api.elevenlabs.io/v1/voices"
            
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.get(
                    voices_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        voices_data = await response.json()
                        # Map voice names to their IDs
                        for voice in voices_data.get("voices", []):
                            voice_name = voice.get("name", "")
                            voice_id = voice.get("voice_id", "")
                            if voice_name and voice_id:
                                self.voice_id_map[voice_name] = voice_id
                        
                        # If we found voices, use them; otherwise fall back to hardcoded IDs
                        if not self.voice_id_map:
                            print("Warning: No voices found from API, using fallback IDs")
                            self.voice_id_map = self.fallback_voice_id_map.copy()
                        else:
                            print(f"Successfully fetched {len(self.voice_id_map)} voices from ElevenLabs API")
                            # Also check if any expected voices are missing
                            missing_voices = set(self.fallback_voice_id_map.keys()) - set(self.voice_id_map.keys())
                            if missing_voices:
                                print(f"Warning: Some expected voices not found in account: {missing_voices}")
                    else:
                        print(f"Failed to fetch voices from API (status {response.status}), using fallback IDs")
                        self.voice_id_map = self.fallback_voice_id_map.copy()
        except Exception as e:
            print(f"Error fetching voices from API: {e}, using fallback IDs")
            self.voice_id_map = self.fallback_voice_id_map.copy()
        
        self._voices_fetched = True
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using ElevenLabs v3 TTS API"""
        start_time = time.time()
        
        # Fetch voices from API if not already fetched
        if not self._voices_fetched:
            await self._fetch_voices_from_api()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        # Get voice ID from map - try fetched IDs first, then fallback
        voice_id = self.voice_id_map.get(request.voice)
        if not voice_id:
            voice_id = self.fallback_voice_id_map.get(request.voice)
            if not voice_id:
                return TTSResult(
                    success=False,
                    audio_data=None,
                    latency_ms=0,
                    file_size_bytes=0,
                    error_message=f"Voice '{request.voice}' not found in your ElevenLabs account. Available voices: {list(self.voice_id_map.keys())}",
                    metadata={"provider": self.provider_id, "available_voices": list(self.voice_id_map.keys())}
                )
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # ElevenLabs v3 API payload structure
        payload = {
            "text": request.text,
            "model_id": "eleven_v3",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Build URL with voice ID
        url = f"{self.config.base_url}/{voice_id}"
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # ElevenLabs returns audio data directly
                        audio_data = await response.read()
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "voice_id": voice_id,
                                "model": "eleven_v3",
                                "provider": self.provider_id,
                                "format": "mp3_44100_128"
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available ElevenLabs v3 voices - returns actual voices from account if fetched, otherwise config voices"""
        # If voices have been fetched from API, return those (account-specific voices)
        if self.voice_id_map:
            return list(self.voice_id_map.keys())
        # Otherwise return config voices (fallback)
        return self.config.supported_voices

class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider implementation"""
    
    def __init__(self):
        super().__init__("openai")
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using OpenAI TTS API"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenAI TTS API payload structure
        payload = {
            "model": "gpt-4o-mini-tts",  # GPT-4o Mini TTS model
            "input": request.text,
            "voice": request.voice.lower(),  # alloy, echo, fable, onyx, nova, shimmer
            "response_format": "mp3",
            "speed": request.speed if request.speed else 1.0
        }
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # OpenAI returns audio data directly
                        audio_data = await response.read()
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "model": "tts-1-hd",
                                "provider": self.provider_id,
                                "format": "mp3",
                                "speed": payload["speed"]
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available OpenAI voices"""
        return self.config.supported_voices

class CartesiaTTSProvider(TTSProvider):
    """Base class for Cartesia TTS providers"""
    
    def __init__(self, provider_id: str, model_id: str):
        super().__init__(provider_id)
        self.model_id = model_id
        # Map friendly voice names to Cartesia voice IDs
        self.voice_id_map = {
            "British Lady": "79a125e8-cd45-4c13-8a67-188112f4dd22",
            "Conversational Lady": "a0e99841-438c-4a64-b679-ae501e7d6091",
            "Classy British Man": "63ff761f-c1e8-414b-b969-d1833d1c870c",
            "Friendly Reading Man": "5619d38c-cf51-4d8e-9575-48f61a280413",
            "Midwestern Woman": "a3520a8f-226a-428d-9fcd-b0a4711a6829",
            "Professional Man": "41534e16-2966-4c6b-9670-111411def906",
            "Newsman": "daf747c6-6bc2-45c9-b3e6-d99d48c6697e"
        }
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using Cartesia TTS API"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        # Get voice ID from friendly name
        voice_id = self.voice_id_map.get(request.voice, self.voice_id_map["Conversational Lady"])
        
        headers = {
            "X-API-Key": self.api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        }
        
        # Cartesia API payload structure
        payload = {
            "model_id": self.model_id,
            "transcript": request.text,
            "voice": {
                "mode": "id",
                "id": voice_id
            },
            "language": "en",
            "output_format": {
                "container": "mp3",
                "encoding": "mp3",
                "sample_rate": 44100
            }
        }
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # Cartesia returns audio data directly
                        audio_data = await response.read()
                        return TTSResult(
                            success=True,
                            audio_data=audio_data,
                            latency_ms=latency_ms,
                            file_size_bytes=len(audio_data),
                            error_message=None,
                            metadata={
                                "voice": request.voice,
                                "voice_id": voice_id,
                                "model": self.model_id,
                                "provider": self.provider_id,
                                "format": "mp3",
                                "sample_rate": 44100
                            }
                        )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available Cartesia voices"""
        return self.config.supported_voices

class CartesiaSonic2Provider(CartesiaTTSProvider):
    """Cartesia Sonic 2.0 TTS provider"""
    
    def __init__(self):
        super().__init__("cartesia_sonic2", "sonic-2")

class CartesiaTurboProvider(CartesiaTTSProvider):
    """Cartesia Sonic Turbo TTS provider"""
    
    def __init__(self):
        super().__init__("cartesia_turbo", "sonic-turbo")

class CartesiaSonic3Provider(CartesiaTTSProvider):
    """Cartesia Sonic 3.0 TTS provider"""
    
    def __init__(self):
        super().__init__("cartesia_sonic3", "sonic-3")

class SarvamTTSProvider(TTSProvider):
    """Sarvam AI TTS provider implementation"""
    
    def __init__(self):
        super().__init__("sarvam")
    
    async def generate_speech(self, request: TTSRequest) -> TTSResult:
        """Generate speech using Sarvam AI API"""
        start_time = time.time()
        
        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=0,
                file_size_bytes=0,
                error_message=error_msg,
                metadata={}
            )
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Determine language based on voice selection
        language = "en-IN" if "en-IN" in request.voice else "hi-IN"
        
        # Sarvam AI API payload structure
        payload = {
            "text": request.text,
            "model": "bulbul:v2",
            "language": language
        }
        
        try:
            async with aiohttp.ClientSession(connector=get_connector()) as session:
                async with session.post(
                    self.config.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        # Check content type to determine response format
                        content_type = response.headers.get('content-type', '').lower()
                        
                        if 'application/json' in content_type:
                            # JSON response - might contain audio URL or base64 data
                            response_data = await response.json()
                            
                            if "audios" in response_data:
                                # Sarvam AI returns base64 encoded audio in 'audios' array
                                import base64
                                # audios is typically an array, get the first one
                                audio_base64 = response_data["audios"][0] if isinstance(response_data["audios"], list) else response_data["audios"]
                                audio_data = base64.b64decode(audio_base64)
                                return TTSResult(
                                    success=True,
                                    audio_data=audio_data,
                                    latency_ms=latency_ms,
                                    file_size_bytes=len(audio_data),
                                    error_message=None,
                                    metadata={
                                        "voice": request.voice,
                                        "language": language,
                                        "model": "bulbul:v2",
                                        "provider": self.provider_id,
                                        "format": "mp3",
                                        "request_id": response_data.get("request_id", "")
                                    }
                                )
                            elif "audioContent" in response_data:
                                # Base64 encoded audio data
                                import base64
                                audio_data = base64.b64decode(response_data["audioContent"])
                                return TTSResult(
                                    success=True,
                                    audio_data=audio_data,
                                    latency_ms=latency_ms,
                                    file_size_bytes=len(audio_data),
                                    error_message=None,
                                    metadata={
                                        "voice": request.voice,
                                        "language": language,
                                        "model": "bulbul:v2",
                                        "provider": self.provider_id,
                                        "format": "mp3"
                                    }
                                )
                            elif "audio" in response_data:
                                # Alternative base64 field name
                                import base64
                                audio_data = base64.b64decode(response_data["audio"])
                                return TTSResult(
                                    success=True,
                                    audio_data=audio_data,
                                    latency_ms=latency_ms,
                                    file_size_bytes=len(audio_data),
                                    error_message=None,
                                    metadata={
                                        "voice": request.voice,
                                        "language": language,
                                        "model": "bulbul:v2",
                                        "provider": self.provider_id,
                                        "format": "mp3"
                                    }
                                )
                            else:
                                return TTSResult(
                                    success=False,
                                    audio_data=None,
                                    latency_ms=latency_ms,
                                    file_size_bytes=0,
                                    error_message=f"Unexpected JSON response format: {list(response_data.keys())}",
                                    metadata={"provider": self.provider_id, "response": response_data}
                                )
                        else:
                            # Direct audio data response
                            audio_data = await response.read()
                            return TTSResult(
                                success=True,
                                audio_data=audio_data,
                                latency_ms=latency_ms,
                                file_size_bytes=len(audio_data),
                                error_message=None,
                                metadata={
                                    "voice": request.voice,
                                    "language": language,
                                    "model": "bulbul:v2",
                                    "provider": self.provider_id,
                                    "format": "mp3",
                                    "content_type": content_type
                                }
                            )
                    else:
                        error_text = await response.text()
                        return TTSResult(
                            success=False,
                            audio_data=None,
                            latency_ms=latency_ms,
                            file_size_bytes=0,
                            error_message=f"API Error {response.status}: {error_text}",
                            metadata={"provider": self.provider_id}
                        )
        
        except asyncio.TimeoutError:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message="Request timeout",
                metadata={"provider": self.provider_id}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                audio_data=None,
                latency_ms=(time.time() - start_time) * 1000,
                file_size_bytes=0,
                error_message=f"Error: {str(e)}",
                metadata={"provider": self.provider_id}
            )
    
    def get_available_voices(self) -> list:
        """Get available Sarvam AI voices"""
        return self.config.supported_voices

class TTSProviderFactory:
    """Factory for creating TTS providers"""
    
    @staticmethod
    def create_provider(provider_id: str) -> TTSProvider:
        """Create a TTS provider instance"""
        if provider_id == "murf_falcon_oct23":
            return MurfFalconOct23TTSProvider()
        elif provider_id == "deepgram":
            return DeepgramTTSProvider()
        elif provider_id == "deepgram_aura2":
            return DeepgramAura2TTSProvider()
        elif provider_id == "elevenlabs_flash":
            return ElevenLabsFlashTTSProvider()
        elif provider_id == "elevenlabs_v3":
            return ElevenLabsV3TTSProvider()
        elif provider_id == "openai":
            return OpenAITTSProvider()
        elif provider_id == "cartesia_sonic2":
            return CartesiaSonic2Provider()
        elif provider_id == "cartesia_turbo":
            return CartesiaTurboProvider()
        elif provider_id == "cartesia_sonic3":
            return CartesiaSonic3Provider()
        elif provider_id == "sarvam":
            return SarvamTTSProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_id}")
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available provider IDs"""
        return list(TTS_PROVIDERS.keys())
    
    @staticmethod
    def create_all_providers() -> Dict[str, TTSProvider]:
        """Create instances of all available providers"""
        providers = {}
        for provider_id in TTSProviderFactory.get_available_providers():
            try:
                providers[provider_id] = TTSProviderFactory.create_provider(provider_id)
            except Exception as e:
                print(f"Failed to create provider {provider_id}: {e}")
        return providers
