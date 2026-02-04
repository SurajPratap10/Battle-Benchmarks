"""
Configuration settings for the TTS Benchmarking Tool
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class VoiceInfo:
    """Voice metadata with gender information"""
    id: str
    name: str
    gender: str  # "male" or "female"
    accent: str = "US"  # "US" or "UK"

@dataclass
class TTSConfig:
    """Configuration for TTS providers"""
    name: str
    api_key_env: str
    base_url: str
    supported_voices: List[str]
    max_chars: int
    supports_streaming: bool
    model_name: str = ""  # Full model name for display
    voice_info: Dict[str, VoiceInfo] = field(default_factory=dict)  # Voice metadata with gender

# TTS Provider Configurations with voice gender info (based on Artificial Analysis methodology)
TTS_PROVIDERS = {
    "murf_falcon_oct23": TTSConfig(
        name="Murf",
        api_key_env="MURF_API_KEY",
        base_url="https://global.api.murf.ai/v1/speech/stream",
        # All Falcon voices available in Murf API
        supported_voices=[
            # US English - Male
            "en-US-matthew", "en-US-carter", "en-US-terrell", "en-US-david", "en-US-james", "en-US-michael", 
            "en-US-william", "en-US-chris", "en-US-alex", "en-US-ryan", "en-US-brandon", "en-US-joshua",
            # US English - Female
            "en-US-phoebe", "en-US-natalie", "en-US-sarah", "en-US-emily", "en-US-jessica", "en-US-olivia",
            "en-US-sophia", "en-US-isabella", "en-US-ava", "en-US-mia", "en-US-charlotte", "en-US-amelia",
            # UK English - Male
            "en-UK-theo", "en-UK-mason", "en-UK-henry", "en-UK-arthur", "en-UK-oscar", "en-UK-george",
            "en-UK-noah", "en-UK-oliver", "en-UK-leo", "en-UK-charlie", "en-UK-harry", "en-UK-jack",
            # UK English - Female
            "en-UK-ruby", "en-UK-hazel", "en-UK-lily", "en-UK-emma", "en-UK-chloe", "en-UK-grace",
            "en-UK-ella", "en-UK-freya", "en-UK-sophia", "en-UK-isabella", "en-UK-mia", "en-UK-amelia",
            # Australian English - Male
            "en-AU-lucas", "en-AU-ethan", "en-AU-lachlan", "en-AU-jackson", "en-AU-thomas", "en-AU-william",
            # Australian English - Female
            "en-AU-charlotte", "en-AU-olivia", "en-AU-amelia", "en-AU-isla", "en-AU-ava", "en-AU-grace",
            # Indian English - Male
            "en-IN-arjun", "en-IN-rahul", "en-IN-vikram", "en-IN-aditya", "en-IN-karan", "en-IN-raj",
            # Indian English - Female
            "en-IN-priya", "en-IN-ananya", "en-IN-kavya", "en-IN-meera", "en-IN-aditi", "en-IN-sneha",
        ],
        max_chars=3000,
        supports_streaming=True,
        model_name="Falcon",
        voice_info={
            # US English - Male
            "en-US-matthew": VoiceInfo("en-US-matthew", "Matthew", "male", "US"),
            "en-US-carter": VoiceInfo("en-US-carter", "Carter", "male", "US"),
            "en-US-terrell": VoiceInfo("en-US-terrell", "Terrell", "male", "US"),
            "en-US-david": VoiceInfo("en-US-david", "David", "male", "US"),
            "en-US-james": VoiceInfo("en-US-james", "James", "male", "US"),
            "en-US-michael": VoiceInfo("en-US-michael", "Michael", "male", "US"),
            "en-US-william": VoiceInfo("en-US-william", "William", "male", "US"),
            "en-US-chris": VoiceInfo("en-US-chris", "Chris", "male", "US"),
            "en-US-alex": VoiceInfo("en-US-alex", "Alex", "male", "US"),
            "en-US-ryan": VoiceInfo("en-US-ryan", "Ryan", "male", "US"),
            "en-US-brandon": VoiceInfo("en-US-brandon", "Brandon", "male", "US"),
            "en-US-joshua": VoiceInfo("en-US-joshua", "Joshua", "male", "US"),
            # US English - Female
            "en-US-phoebe": VoiceInfo("en-US-phoebe", "Phoebe", "female", "US"),
            "en-US-natalie": VoiceInfo("en-US-natalie", "Natalie", "female", "US"),
            "en-US-sarah": VoiceInfo("en-US-sarah", "Sarah", "female", "US"),
            "en-US-emily": VoiceInfo("en-US-emily", "Emily", "female", "US"),
            "en-US-jessica": VoiceInfo("en-US-jessica", "Jessica", "female", "US"),
            "en-US-olivia": VoiceInfo("en-US-olivia", "Olivia", "female", "US"),
            "en-US-sophia": VoiceInfo("en-US-sophia", "Sophia", "female", "US"),
            "en-US-isabella": VoiceInfo("en-US-isabella", "Isabella", "female", "US"),
            "en-US-ava": VoiceInfo("en-US-ava", "Ava", "female", "US"),
            "en-US-mia": VoiceInfo("en-US-mia", "Mia", "female", "US"),
            "en-US-charlotte": VoiceInfo("en-US-charlotte", "Charlotte", "female", "US"),
            "en-US-amelia": VoiceInfo("en-US-amelia", "Amelia", "female", "US"),
            # UK English - Male
            "en-UK-theo": VoiceInfo("en-UK-theo", "Theo", "male", "UK"),
            "en-UK-mason": VoiceInfo("en-UK-mason", "Mason", "male", "UK"),
            "en-UK-henry": VoiceInfo("en-UK-henry", "Henry", "male", "UK"),
            "en-UK-arthur": VoiceInfo("en-UK-arthur", "Arthur", "male", "UK"),
            "en-UK-oscar": VoiceInfo("en-UK-oscar", "Oscar", "male", "UK"),
            "en-UK-george": VoiceInfo("en-UK-george", "George", "male", "UK"),
            "en-UK-noah": VoiceInfo("en-UK-noah", "Noah", "male", "UK"),
            "en-UK-oliver": VoiceInfo("en-UK-oliver", "Oliver", "male", "UK"),
            "en-UK-leo": VoiceInfo("en-UK-leo", "Leo", "male", "UK"),
            "en-UK-charlie": VoiceInfo("en-UK-charlie", "Charlie", "male", "UK"),
            "en-UK-harry": VoiceInfo("en-UK-harry", "Harry", "male", "UK"),
            "en-UK-jack": VoiceInfo("en-UK-jack", "Jack", "male", "UK"),
            # UK English - Female
            "en-UK-ruby": VoiceInfo("en-UK-ruby", "Ruby", "female", "UK"),
            "en-UK-hazel": VoiceInfo("en-UK-hazel", "Hazel", "female", "UK"),
            "en-UK-lily": VoiceInfo("en-UK-lily", "Lily", "female", "UK"),
            "en-UK-emma": VoiceInfo("en-UK-emma", "Emma", "female", "UK"),
            "en-UK-chloe": VoiceInfo("en-UK-chloe", "Chloe", "female", "UK"),
            "en-UK-grace": VoiceInfo("en-UK-grace", "Grace", "female", "UK"),
            "en-UK-ella": VoiceInfo("en-UK-ella", "Ella", "female", "UK"),
            "en-UK-freya": VoiceInfo("en-UK-freya", "Freya", "female", "UK"),
            "en-UK-sophia": VoiceInfo("en-UK-sophia", "Sophia", "female", "UK"),
            "en-UK-isabella": VoiceInfo("en-UK-isabella", "Isabella", "female", "UK"),
            "en-UK-mia": VoiceInfo("en-UK-mia", "Mia", "female", "UK"),
            "en-UK-amelia": VoiceInfo("en-UK-amelia", "Amelia", "female", "UK"),
            # Australian English - Male
            "en-AU-lucas": VoiceInfo("en-AU-lucas", "Lucas", "male", "AU"),
            "en-AU-ethan": VoiceInfo("en-AU-ethan", "Ethan", "male", "AU"),
            "en-AU-lachlan": VoiceInfo("en-AU-lachlan", "Lachlan", "male", "AU"),
            "en-AU-jackson": VoiceInfo("en-AU-jackson", "Jackson", "male", "AU"),
            "en-AU-thomas": VoiceInfo("en-AU-thomas", "Thomas", "male", "AU"),
            "en-AU-william": VoiceInfo("en-AU-william", "William", "male", "AU"),
            # Australian English - Female
            "en-AU-charlotte": VoiceInfo("en-AU-charlotte", "Charlotte", "female", "AU"),
            "en-AU-olivia": VoiceInfo("en-AU-olivia", "Olivia", "female", "AU"),
            "en-AU-amelia": VoiceInfo("en-AU-amelia", "Amelia", "female", "AU"),
            "en-AU-isla": VoiceInfo("en-AU-isla", "Isla", "female", "AU"),
            "en-AU-ava": VoiceInfo("en-AU-ava", "Ava", "female", "AU"),
            "en-AU-grace": VoiceInfo("en-AU-grace", "Grace", "female", "AU"),
            # Indian English - Male
            "en-IN-arjun": VoiceInfo("en-IN-arjun", "Arjun", "male", "IN"),
            "en-IN-rahul": VoiceInfo("en-IN-rahul", "Rahul", "male", "IN"),
            "en-IN-vikram": VoiceInfo("en-IN-vikram", "Vikram", "male", "IN"),
            "en-IN-aditya": VoiceInfo("en-IN-aditya", "Aditya", "male", "IN"),
            "en-IN-karan": VoiceInfo("en-IN-karan", "Karan", "male", "IN"),
            "en-IN-raj": VoiceInfo("en-IN-raj", "Raj", "male", "IN"),
            # Indian English - Female
            "en-IN-priya": VoiceInfo("en-IN-priya", "Priya", "female", "IN"),
            "en-IN-ananya": VoiceInfo("en-IN-ananya", "Ananya", "female", "IN"),
            "en-IN-kavya": VoiceInfo("en-IN-kavya", "Kavya", "female", "IN"),
            "en-IN-meera": VoiceInfo("en-IN-meera", "Meera", "female", "IN"),
            "en-IN-aditi": VoiceInfo("en-IN-aditi", "Aditi", "female", "IN"),
            "en-IN-sneha": VoiceInfo("en-IN-sneha", "Sneha", "female", "IN"),
        }
    ),
    "deepgram": TTSConfig(
        name="Deepgram Aura 1",
        api_key_env="DEEPGRAM_API_KEY",
        base_url="https://api.deepgram.com/v1/speak",
        supported_voices=["aura-asteria-en", "aura-luna-en", "aura-stella-en", "aura-athena-en", "aura-hera-en", "aura-orion-en"],
        max_chars=2000,
        supports_streaming=True,
        model_name="aura-1",
        voice_info={
            "aura-asteria-en": VoiceInfo("aura-asteria-en", "Asteria", "female", "US"),
            "aura-luna-en": VoiceInfo("aura-luna-en", "Luna", "female", "US"),
            "aura-stella-en": VoiceInfo("aura-stella-en", "Stella", "female", "US"),
            "aura-athena-en": VoiceInfo("aura-athena-en", "Athena", "female", "US"),
            "aura-hera-en": VoiceInfo("aura-hera-en", "Hera", "female", "US"),
            "aura-orion-en": VoiceInfo("aura-orion-en", "Orion", "male", "US"),
        }
    ),
    "deepgram_aura2": TTSConfig(
        name="Deepgram Aura 2",
        api_key_env="DEEPGRAM_API_KEY",
        base_url="https://api.deepgram.com/v1/speak",
        supported_voices=["aura-2-asteria-en", "aura-2-luna-en", "aura-2-stella-en", "aura-2-athena-en", "aura-2-hera-en", "aura-2-orion-en"],
        max_chars=2000,
        supports_streaming=True,
        model_name="aura-2",
        voice_info={
            "aura-2-asteria-en": VoiceInfo("aura-2-asteria-en", "Asteria", "female", "US"),
            "aura-2-luna-en": VoiceInfo("aura-2-luna-en", "Luna", "female", "US"),
            "aura-2-stella-en": VoiceInfo("aura-2-stella-en", "Stella", "female", "US"),
            "aura-2-athena-en": VoiceInfo("aura-2-athena-en", "Athena", "female", "US"),
            "aura-2-hera-en": VoiceInfo("aura-2-hera-en", "Hera", "female", "US"),
            "aura-2-orion-en": VoiceInfo("aura-2-orion-en", "Orion", "male", "US"),
        }
    ),
    "elevenlabs_flash": TTSConfig(
        name="ElevenLabs Flash",
        api_key_env="ELEVENLABS_API_KEY",
        base_url="https://api.elevenlabs.io/v1/text-to-speech",
        supported_voices=["Laura", "Jessica", "Liam", "Elizabeth", "Shelley", "Dan", "Nathaniel"],
        max_chars=5000,
        supports_streaming=True,
        model_name="eleven_flash_v2_5",
        voice_info={
            "Laura": VoiceInfo("Laura", "Laura", "female", "US"),
            "Jessica": VoiceInfo("Jessica", "Jessica", "female", "US"),
            "Liam": VoiceInfo("Liam", "Liam", "male", "US"),
            "Elizabeth": VoiceInfo("Elizabeth", "Elizabeth", "female", "UK"),
            "Shelley": VoiceInfo("Shelley", "Shelley", "female", "UK"),
            "Dan": VoiceInfo("Dan", "Dan", "male", "UK"),
            "Nathaniel": VoiceInfo("Nathaniel", "Nathaniel", "male", "UK"),
        }
    ),
    "elevenlabs_v3": TTSConfig(
        name="ElevenLabs v3",
        api_key_env="ELEVENLABS_API_KEY",
        base_url="https://api.elevenlabs.io/v1/text-to-speech",
        supported_voices=["Laura", "Jessica", "Liam", "Elizabeth", "Shelley", "Dan", "Nathaniel"],
        max_chars=5000,
        supports_streaming=True,
        model_name="eleven_v3",
        voice_info={
            "Laura": VoiceInfo("Laura", "Laura", "female", "US"),
            "Jessica": VoiceInfo("Jessica", "Jessica", "female", "US"),
            "Liam": VoiceInfo("Liam", "Liam", "male", "US"),
            "Elizabeth": VoiceInfo("Elizabeth", "Elizabeth", "female", "UK"),
            "Shelley": VoiceInfo("Shelley", "Shelley", "female", "UK"),
            "Dan": VoiceInfo("Dan", "Dan", "male", "UK"),
            "Nathaniel": VoiceInfo("Nathaniel", "Nathaniel", "male", "UK"),
        }
    ),
    "openai": TTSConfig(
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1/audio/speech",
        # Only voices from https://artificialanalysis.ai/text-to-speech/methodology
        # TTS-1: echo, alloy, nova, shimmer, onyx, fable
        supported_voices=["echo", "alloy", "nova", "shimmer", "onyx", "fable"],
        max_chars=4096,
        supports_streaming=True,
        model_name="gpt-4o-mini-tts",
        voice_info={
            "echo": VoiceInfo("echo", "Echo", "male", "US"),
            "alloy": VoiceInfo("alloy", "Alloy", "female", "US"),
            "nova": VoiceInfo("nova", "Nova", "female", "US"),
            "shimmer": VoiceInfo("shimmer", "Shimmer", "female", "US"),
            "onyx": VoiceInfo("onyx", "Onyx", "male", "US"),
            "fable": VoiceInfo("fable", "Fable", "male", "UK"),
        }
    ),
    "cartesia_sonic2": TTSConfig(
        name="Cartesia Sonic 2.0",
        api_key_env="CARTESIA_API_KEY",
        base_url="https://api.cartesia.ai/tts/bytes",
        supported_voices=["British Lady", "Conversational Lady", "Classy British Man", "Friendly Reading Man", "Midwestern Woman", "Professional Man"],
        max_chars=5000,
        supports_streaming=True,
        model_name="Cartesia Sonic 2.0",
        voice_info={
            "British Lady": VoiceInfo("British Lady", "British Lady", "female", "UK"),
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "female", "US"),
            "Classy British Man": VoiceInfo("Classy British Man", "Classy British Man", "male", "UK"),
            "Friendly Reading Man": VoiceInfo("Friendly Reading Man", "Friendly Reading Man", "male", "US"),
            "Midwestern Woman": VoiceInfo("Midwestern Woman", "Midwestern Woman", "female", "US"),
            "Professional Man": VoiceInfo("Professional Man", "Professional Man", "male", "US"),
        }
    ),
    "cartesia_turbo": TTSConfig(
        name="Cartesia Sonic Turbo",
        api_key_env="CARTESIA_API_KEY",
        base_url="https://api.cartesia.ai/tts/bytes",
        supported_voices=["British Lady", "Conversational Lady", "Classy British Man", "Friendly Reading Man", "Midwestern Woman", "Professional Man"],
        max_chars=5000,
        supports_streaming=True,
        model_name="Cartesia Sonic Turbo",
        voice_info={
            "British Lady": VoiceInfo("British Lady", "British Lady", "female", "UK"),
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "female", "US"),
            "Classy British Man": VoiceInfo("Classy British Man", "Classy British Man", "male", "UK"),
            "Friendly Reading Man": VoiceInfo("Friendly Reading Man", "Friendly Reading Man", "male", "US"),
            "Midwestern Woman": VoiceInfo("Midwestern Woman", "Midwestern Woman", "female", "US"),
            "Professional Man": VoiceInfo("Professional Man", "Professional Man", "male", "US"),
        }
    ),
    "cartesia_sonic3": TTSConfig(
        name="Cartesia Sonic 3",
        api_key_env="CARTESIA_API_KEY",
        base_url="https://api.cartesia.ai/tts/bytes",
        supported_voices=["British Lady", "Conversational Lady", "Classy British Man", "Friendly Reading Man", "Midwestern Woman", "Professional Man"],
        max_chars=5000,
        supports_streaming=True,
        model_name="Cartesia Sonic 3.0",
        voice_info={
            "British Lady": VoiceInfo("British Lady", "British Lady", "female", "UK"),
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "female", "US"),
            "Classy British Man": VoiceInfo("Classy British Man", "Classy British Man", "male", "UK"),
            "Friendly Reading Man": VoiceInfo("Friendly Reading Man", "Friendly Reading Man", "male", "US"),
            "Midwestern Woman": VoiceInfo("Midwestern Woman", "Midwestern Woman", "female", "US"),
            "Professional Man": VoiceInfo("Professional Man", "Professional Man", "male", "US"),
        }
    ),
    "sarvam": TTSConfig(
        name="Sarvam AI",
        api_key_env="SARVAM_API_KEY",
        base_url="https://api.sarvam.ai/text-to-speech",
        supported_voices=["en-IN-male", "en-IN-female", "hi-IN-male", "hi-IN-female"],
        max_chars=5000,
        supports_streaming=False,
        model_name="bulbul:v2",
        voice_info={
            "en-IN-male": VoiceInfo("en-IN-male", "Male (Indian English)", "male", "US"),
            "en-IN-female": VoiceInfo("en-IN-female", "Female (Indian English)", "female", "US"),
            "hi-IN-male": VoiceInfo("hi-IN-male", "Male (Hindi)", "male", "US"),
            "hi-IN-female": VoiceInfo("hi-IN-female", "Female (Hindi)", "female", "US"),
        }
    )
}

def get_voice_gender(provider_id: str, voice_id: str) -> str:
    """Get the gender of a voice for a provider"""
    if provider_id in TTS_PROVIDERS:
        voice_info = TTS_PROVIDERS[provider_id].voice_info.get(voice_id)
        if voice_info:
            return voice_info.gender
    return "unknown"

def get_voices_by_gender(provider_id: str, gender: str) -> List[str]:
    """Get voices filtered by gender for a provider - returns only voices matching the gender"""
    if provider_id in TTS_PROVIDERS:
        voices = []
        supported_voices_set = set(TTS_PROVIDERS[provider_id].supported_voices)
        for voice_id, info in TTS_PROVIDERS[provider_id].voice_info.items():
            # Only include voices that match gender AND are in supported_voices
            if info.gender == gender and voice_id in supported_voices_set:
                voices.append(voice_id)
        # Return only matching voices - don't fall back to all voices
        return voices
    return []

# Benchmarking Configuration
BENCHMARK_CONFIG = {
    "default_iterations": 3,
    "timeout_seconds": 30,
    "quality_metrics": ["duration", "file_size", "sample_rate"],
    "latency_percentiles": [50, 90, 95, 99],
    "elo_k_factor": 32,
    "initial_elo_rating": 1000
}

# Test Dataset Configuration  
DATASET_CONFIG = {
    "sentence_lengths": {
        "short": (10, 30),    # 10-30 words
        "medium": (31, 80),   # 31-80 words  
        "long": (81, 150),    # 81-150 words
        "very_long": (151, 200) # 151-200 words
    },
    "categories": ["news", "literature", "conversation", "technical", "narrative"],
    "total_samples": 100
}

# UI Configuration
UI_CONFIG = {
    "page_title": "TTS Benchmarking Tool",
    "page_icon": None,
    "layout": "wide",
    "sidebar_width": 300,
    "chart_height": 400,
    "max_file_size_mb": 10
}

def get_api_key(provider: str) -> str:
    """Get API key for a provider from environment variables"""
    if provider not in TTS_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")
    
    env_var = TTS_PROVIDERS[provider].api_key_env
    api_key = os.getenv(env_var)
    
    if not api_key:
        raise ValueError(f"API key not found for {provider}. Please set {env_var} environment variable.")
    
    return api_key

def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    status = {
        "providers": {},
        "valid": False,
        "errors": [],
        "configured_count": 0
    }
    
    for provider_id, config in TTS_PROVIDERS.items():
        try:
            api_key = get_api_key(provider_id)
            status["providers"][provider_id] = {
                "configured": True,
                "api_key_length": len(api_key) if api_key else 0
            }
            status["configured_count"] += 1
        except ValueError as e:
            status["providers"][provider_id] = {
                "configured": False,
                "error": str(e)
            }
            status["errors"].append(str(e))
    
    # Consider valid if at least one provider is configured
    status["valid"] = status["configured_count"] > 0
    
    return status
