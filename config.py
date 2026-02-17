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
        # All Falcon voices from Murf API
        supported_voices=[
            "pa-IN-harman", "en-US-alina", "en-UK-hazel", "en-US-cooper", "en-US-imani",
            "mr-IN-rujuta", "en-US-wayne", "kn-IN-rajesh", "en-US-daniel", "hr-HR-marija",
            "en-IN-samar", "bn-IN-anwesha", "hi-IN-khyati", "es-MX-alejandro", "en-AU-joyce",
            "en-US-zion", "en-IN-isha", "en-US-riley", "en-US-carter", "ta-IN-sarvesh",
            "en-UK-gabriel", "en-UK-juliet", "en-IN-arohi", "de-DE-josephine", "en-UK-hugo",
            "en-US-samantha", "de-DE-erna", "en-IN-nikhil", "en-IN-anisha", "zh-CN-baolin",
            "pt-BR-isadora", "en-US-terrell", "en-US-denzel", "en-UK-heidi", "en-US-miles",
            "en-US-abigail", "mr-IN-vaibhav", "en-AU-shane", "ta-IN-murali", "en-UK-peter",
            "it-IT-giulia", "nl-NL-famke", "en-AU-ivy", "nl-NL-dirk", "fr-FR-axel",
            "fr-FR-guillaume", "es-ES-carla", "en-US-claire", "ko-KR-jangmi", "ko-KR-sanghoon",
            "ja-JP-denki", "es-ES-elvira", "es-ES-enrique", "en-UK-aiden", "en-US-ronnie",
            "en-UK-amber", "en-AU-jimm", "en-UK-pearl", "pt-BR-benício", "en-UK-freddie",
            "en-US-ryan", "pt-BR-eloa", "hi-IN-karan", "en-US-charlotte", "hi-IN-namrita",
            "de-DE-lia", "en-US-natalie", "ta-IN-suresh", "en-US-michelle", "en-US-phoebe",
            "es-ES-carmen", "en-US-caleb", "en-US-iris", "en-UK-harrison", "en-US-marcus",
            "en-US-josie", "en-US-ariana", "en-US-daisy", "en-US-charles", "en-UK-reggie",
            "en-US-julia", "en-SCOTT-emily", "en-US-dylan", "es-MX-valeria", "en-IN-eashwar",
            "en-AU-evelyn", "hi-IN-sunaina", "de-DE-lara", "en-US-evander", "en-IN-tanushree",
            "en-SCOTT-rory", "pt-BR-yago", "ta-IN-iniya", "en-AU-leyton", "zh-CN-wei",
            "de-DE-matthias", "it-IT-angelo", "en-IN-rohan", "en-US-delilah", "en-US-paul",
            "en-US-lucas", "bn-IN-abhik", "en-US-angela", "en-US-naomi", "es-MX-carlos",
            "nl-NL-merel", "ja-JP-kenji", "en-US-alicia", "en-IN-alia", "zh-CN-jiao",
            "en-US-june", "en-AU-ashton", "en-UK-finley", "pl-PL-blazej", "el-GR-stavros",
            "zh-CN-zhang", "en-AU-sophia", "en-AU-kylie", "en-US-jayden", "en-IN-aarav",
            "en-US-matthew", "de-DE-björn", "zh-CN-yuxan", "ko-KR-jong-su", "en-AU-harper",
            "ta-IN-abirami", "en-UK-ruby", "ja-JP-kimi", "en-US-ken", "pt-BR-silvio",
            "de-DE-ralf", "en-UK-jaxon", "en-US-river", "en-IN-priya", "en-UK-theo",
            "en-UK-katie", "pl-PL-jacek", "en-US-maverick", "en-US-will", "hi-IN-aman",
            "en-US-amara", "en-UK-mason", "pt-BR-gustavo", "es-ES-javier", "en-AU-mitch",
            "pt-BR-heitor", "fr-CA-alexis", "en-US-edmund", "en-IN-anusha", "pl-PL-kasia",
            "es-MX-luisa", "zh-CN-tao", "en-US-molly"
        ],
        max_chars=3000,
        supports_streaming=True,
        model_name="Falcon",
        voice_info={
            "pa-IN-harman": VoiceInfo("pa-IN-harman", "Harman", "male", "IN"),
            "en-US-alina": VoiceInfo("en-US-alina", "Alina", "female", "US"),
            "en-UK-hazel": VoiceInfo("en-UK-hazel", "Hazel", "female", "UK"),
            "en-US-cooper": VoiceInfo("en-US-cooper", "Cooper", "male", "US"),
            "en-US-imani": VoiceInfo("en-US-imani", "Imani", "female", "US"),
            "mr-IN-rujuta": VoiceInfo("mr-IN-rujuta", "Rujuta", "female", "IN"),
            "en-US-wayne": VoiceInfo("en-US-wayne", "Wayne", "male", "US"),
            "kn-IN-rajesh": VoiceInfo("kn-IN-rajesh", "Rajesh", "male", "IN"),
            "en-US-daniel": VoiceInfo("en-US-daniel", "Daniel", "male", "US"),
            "hr-HR-marija": VoiceInfo("hr-HR-marija", "Marija", "female", "HR"),
            "en-IN-samar": VoiceInfo("en-IN-samar", "Samar", "male", "IN"),
            "bn-IN-anwesha": VoiceInfo("bn-IN-anwesha", "Anwesha", "female", "IN"),
            "hi-IN-khyati": VoiceInfo("hi-IN-khyati", "Khyati", "female", "IN"),
            "es-MX-alejandro": VoiceInfo("es-MX-alejandro", "Alejandro", "male", "MX"),
            "en-AU-joyce": VoiceInfo("en-AU-joyce", "Joyce", "female", "AU"),
            "en-US-zion": VoiceInfo("en-US-zion", "Zion", "male", "US"),
            "en-IN-isha": VoiceInfo("en-IN-isha", "Isha", "female", "IN"),
            "en-US-riley": VoiceInfo("en-US-riley", "Riley", "female", "US"),
            "en-US-carter": VoiceInfo("en-US-carter", "Carter", "male", "US"),
            "ta-IN-sarvesh": VoiceInfo("ta-IN-sarvesh", "Sarvesh", "male", "IN"),
            "en-UK-gabriel": VoiceInfo("en-UK-gabriel", "Gabriel", "male", "UK"),
            "en-UK-juliet": VoiceInfo("en-UK-juliet", "Juliet", "female", "UK"),
            "en-IN-arohi": VoiceInfo("en-IN-arohi", "Arohi", "female", "IN"),
            "de-DE-josephine": VoiceInfo("de-DE-josephine", "Josephine", "female", "DE"),
            "en-UK-hugo": VoiceInfo("en-UK-hugo", "Hugo", "male", "UK"),
            "en-US-samantha": VoiceInfo("en-US-samantha", "Samantha", "female", "US"),
            "de-DE-erna": VoiceInfo("de-DE-erna", "Erna", "female", "DE"),
            "en-IN-nikhil": VoiceInfo("en-IN-nikhil", "Nikhil", "male", "IN"),
            "en-IN-anisha": VoiceInfo("en-IN-anisha", "Anisha", "female", "IN"),
            "zh-CN-baolin": VoiceInfo("zh-CN-baolin", "Baolin", "female", "CN"),
            "pt-BR-isadora": VoiceInfo("pt-BR-isadora", "Isadora", "female", "BR"),
            "en-US-terrell": VoiceInfo("en-US-terrell", "Terrell", "male", "US"),
            "en-US-denzel": VoiceInfo("en-US-denzel", "Denzel", "male", "US"),
            "en-UK-heidi": VoiceInfo("en-UK-heidi", "Heidi", "female", "UK"),
            "en-US-miles": VoiceInfo("en-US-miles", "Miles", "male", "US"),
            "en-US-abigail": VoiceInfo("en-US-abigail", "Abigail", "female", "US"),
            "mr-IN-vaibhav": VoiceInfo("mr-IN-vaibhav", "Vaibhav", "male", "IN"),
            "en-AU-shane": VoiceInfo("en-AU-shane", "Shane", "male", "AU"),
            "ta-IN-murali": VoiceInfo("ta-IN-murali", "Murali", "male", "IN"),
            "en-UK-peter": VoiceInfo("en-UK-peter", "Peter", "male", "UK"),
            "it-IT-giulia": VoiceInfo("it-IT-giulia", "Giulia", "female", "IT"),
            "nl-NL-famke": VoiceInfo("nl-NL-famke", "Famke", "female", "NL"),
            "en-AU-ivy": VoiceInfo("en-AU-ivy", "Ivy", "female", "AU"),
            "nl-NL-dirk": VoiceInfo("nl-NL-dirk", "Dirk", "male", "NL"),
            "fr-FR-axel": VoiceInfo("fr-FR-axel", "Axel", "male", "FR"),
            "fr-FR-guillaume": VoiceInfo("fr-FR-guillaume", "Guillaume", "male", "FR"),
            "es-ES-carla": VoiceInfo("es-ES-carla", "Carla", "female", "ES"),
            "en-US-claire": VoiceInfo("en-US-claire", "Claire", "female", "US"),
            "ko-KR-jangmi": VoiceInfo("ko-KR-jangmi", "Jangmi", "female", "KR"),
            "ko-KR-sanghoon": VoiceInfo("ko-KR-sanghoon", "SangHoon", "male", "KR"),
            "ja-JP-denki": VoiceInfo("ja-JP-denki", "Denki", "male", "JP"),
            "es-ES-elvira": VoiceInfo("es-ES-elvira", "Elvira", "female", "ES"),
            "es-ES-enrique": VoiceInfo("es-ES-enrique", "Enrique", "male", "ES"),
            "en-UK-aiden": VoiceInfo("en-UK-aiden", "Aiden", "male", "UK"),
            "en-US-ronnie": VoiceInfo("en-US-ronnie", "Ronnie", "male", "US"),
            "en-UK-amber": VoiceInfo("en-UK-amber", "Amber", "female", "UK"),
            "en-AU-jimm": VoiceInfo("en-AU-jimm", "Jimm", "male", "AU"),
            "en-UK-pearl": VoiceInfo("en-UK-pearl", "Pearl", "female", "UK"),
            "pt-BR-benício": VoiceInfo("pt-BR-benício", "Benício", "male", "BR"),
            "en-UK-freddie": VoiceInfo("en-UK-freddie", "Freddie", "male", "UK"),
            "en-US-ryan": VoiceInfo("en-US-ryan", "Ryan", "male", "US"),
            "pt-BR-eloa": VoiceInfo("pt-BR-eloa", "Eloa", "female", "BR"),
            "hi-IN-karan": VoiceInfo("hi-IN-karan", "Karan", "male", "IN"),
            "en-US-charlotte": VoiceInfo("en-US-charlotte", "Charlotte", "female", "US"),
            "hi-IN-namrita": VoiceInfo("hi-IN-namrita", "Namrita", "female", "IN"),
            "de-DE-lia": VoiceInfo("de-DE-lia", "Lia", "female", "DE"),
            "en-US-natalie": VoiceInfo("en-US-natalie", "Natalie", "female", "US"),
            "ta-IN-suresh": VoiceInfo("ta-IN-suresh", "Suresh", "male", "IN"),
            "en-US-michelle": VoiceInfo("en-US-michelle", "Michelle", "female", "US"),
            "en-US-phoebe": VoiceInfo("en-US-phoebe", "Phoebe", "female", "US"),
            "es-ES-carmen": VoiceInfo("es-ES-carmen", "Carmen", "female", "ES"),
            "en-US-caleb": VoiceInfo("en-US-caleb", "Caleb", "male", "US"),
            "en-US-iris": VoiceInfo("en-US-iris", "Iris", "female", "US"),
            "en-UK-harrison": VoiceInfo("en-UK-harrison", "Harrison", "male", "UK"),
            "en-US-marcus": VoiceInfo("en-US-marcus", "Marcus", "male", "US"),
            "en-US-josie": VoiceInfo("en-US-josie", "Josie", "female", "US"),
            "en-US-ariana": VoiceInfo("en-US-ariana", "Ariana", "female", "US"),
            "en-US-daisy": VoiceInfo("en-US-daisy", "Daisy", "female", "US"),
            "en-US-charles": VoiceInfo("en-US-charles", "Charles", "male", "US"),
            "en-UK-reggie": VoiceInfo("en-UK-reggie", "Reggie", "male", "UK"),
            "en-US-julia": VoiceInfo("en-US-julia", "Julia", "female", "US"),
            "en-SCOTT-emily": VoiceInfo("en-SCOTT-emily", "Emily", "female", "SCOTT"),
            "en-US-dylan": VoiceInfo("en-US-dylan", "Dylan", "male", "US"),
            "es-MX-valeria": VoiceInfo("es-MX-valeria", "Valeria", "female", "MX"),
            "en-IN-eashwar": VoiceInfo("en-IN-eashwar", "Eashwar", "male", "IN"),
            "en-AU-evelyn": VoiceInfo("en-AU-evelyn", "Evelyn", "female", "AU"),
            "hi-IN-sunaina": VoiceInfo("hi-IN-sunaina", "Sunaina", "female", "IN"),
            "de-DE-lara": VoiceInfo("de-DE-lara", "Lara", "female", "DE"),
            "en-US-evander": VoiceInfo("en-US-evander", "Evander", "male", "US"),
            "en-IN-tanushree": VoiceInfo("en-IN-tanushree", "Tanushree", "female", "IN"),
            "en-SCOTT-rory": VoiceInfo("en-SCOTT-rory", "Rory", "male", "SCOTT"),
            "pt-BR-yago": VoiceInfo("pt-BR-yago", "Yago", "male", "BR"),
            "ta-IN-iniya": VoiceInfo("ta-IN-iniya", "Iniya", "female", "IN"),
            "en-AU-leyton": VoiceInfo("en-AU-leyton", "Leyton", "male", "AU"),
            "zh-CN-wei": VoiceInfo("zh-CN-wei", "Wei", "female", "CN"),
            "de-DE-matthias": VoiceInfo("de-DE-matthias", "Matthias", "male", "DE"),
            "it-IT-angelo": VoiceInfo("it-IT-angelo", "Angelo", "male", "IT"),
            "en-IN-rohan": VoiceInfo("en-IN-rohan", "Rohan", "male", "IN"),
            "en-US-delilah": VoiceInfo("en-US-delilah", "Delilah", "female", "US"),
            "en-US-paul": VoiceInfo("en-US-paul", "Paul", "male", "US"),
            "en-US-lucas": VoiceInfo("en-US-lucas", "Lucas", "male", "US"),
            "bn-IN-abhik": VoiceInfo("bn-IN-abhik", "Abhik", "male", "IN"),
            "en-US-angela": VoiceInfo("en-US-angela", "Angela", "female", "US"),
            "en-US-naomi": VoiceInfo("en-US-naomi", "Naomi", "female", "US"),
            "es-MX-carlos": VoiceInfo("es-MX-carlos", "Carlos", "male", "MX"),
            "nl-NL-merel": VoiceInfo("nl-NL-merel", "Merel", "female", "NL"),
            "ja-JP-kenji": VoiceInfo("ja-JP-kenji", "Kenji", "male", "JP"),
            "en-US-alicia": VoiceInfo("en-US-alicia", "Alicia", "female", "US"),
            "en-IN-alia": VoiceInfo("en-IN-alia", "Alia", "female", "IN"),
            "zh-CN-jiao": VoiceInfo("zh-CN-jiao", "Jiao", "female", "CN"),
            "en-US-june": VoiceInfo("en-US-june", "June", "female", "US"),
            "en-AU-ashton": VoiceInfo("en-AU-ashton", "Ashton", "male", "AU"),
            "en-UK-finley": VoiceInfo("en-UK-finley", "Finley", "male", "UK"),
            "pl-PL-blazej": VoiceInfo("pl-PL-blazej", "Blazej", "male", "PL"),
            "el-GR-stavros": VoiceInfo("el-GR-stavros", "Stavros", "male", "GR"),
            "zh-CN-zhang": VoiceInfo("zh-CN-zhang", "Zhang", "male", "CN"),
            "en-AU-sophia": VoiceInfo("en-AU-sophia", "Sophia", "female", "AU"),
            "en-AU-kylie": VoiceInfo("en-AU-kylie", "Kylie", "female", "AU"),
            "en-US-jayden": VoiceInfo("en-US-jayden", "Jayden", "male", "US"),
            "en-IN-aarav": VoiceInfo("en-IN-aarav", "Aarav", "male", "IN"),
            "en-US-matthew": VoiceInfo("en-US-matthew", "Matthew", "male", "US"),
            "de-DE-björn": VoiceInfo("de-DE-björn", "Björn", "male", "DE"),
            "zh-CN-yuxan": VoiceInfo("zh-CN-yuxan", "Yuxan", "male", "CN"),
            "ko-KR-jong-su": VoiceInfo("ko-KR-jong-su", "Jong-su", "male", "KR"),
            "en-AU-harper": VoiceInfo("en-AU-harper", "Harper", "male", "AU"),
            "ta-IN-abirami": VoiceInfo("ta-IN-abirami", "Abirami", "female", "IN"),
            "en-UK-ruby": VoiceInfo("en-UK-ruby", "Ruby", "female", "UK"),
            "ja-JP-kimi": VoiceInfo("ja-JP-kimi", "Kimi", "female", "JP"),
            "en-US-ken": VoiceInfo("en-US-ken", "Ken", "male", "US"),
            "pt-BR-silvio": VoiceInfo("pt-BR-silvio", "Silvio", "male", "BR"),
            "de-DE-ralf": VoiceInfo("de-DE-ralf", "Ralf", "male", "DE"),
            "en-UK-jaxon": VoiceInfo("en-UK-jaxon", "Jaxon", "male", "UK"),
            "en-US-river": VoiceInfo("en-US-river", "River", "nonbinary", "US"),
            "en-IN-priya": VoiceInfo("en-IN-priya", "Priya", "female", "IN"),
            "en-UK-theo": VoiceInfo("en-UK-theo", "Theo", "male", "UK"),
            "en-UK-katie": VoiceInfo("en-UK-katie", "Katie", "female", "UK"),
            "pl-PL-jacek": VoiceInfo("pl-PL-jacek", "Jacek", "male", "PL"),
            "en-US-maverick": VoiceInfo("en-US-maverick", "Maverick", "male", "US"),
            "en-US-will": VoiceInfo("en-US-will", "Will", "male", "US"),
            "hi-IN-aman": VoiceInfo("hi-IN-aman", "Aman", "male", "IN"),
            "en-US-amara": VoiceInfo("en-US-amara", "Amara", "female", "US"),
            "en-UK-mason": VoiceInfo("en-UK-mason", "Mason", "male", "UK"),
            "pt-BR-gustavo": VoiceInfo("pt-BR-gustavo", "Gustavo", "male", "BR"),
            "es-ES-javier": VoiceInfo("es-ES-javier", "Javier", "male", "ES"),
            "en-AU-mitch": VoiceInfo("en-AU-mitch", "Mitch", "male", "AU"),
            "pt-BR-heitor": VoiceInfo("pt-BR-heitor", "Heitor", "male", "BR"),
            "fr-CA-alexis": VoiceInfo("fr-CA-alexis", "Alexis", "male", "CA"),
            "en-US-edmund": VoiceInfo("en-US-edmund", "Edmund", "male", "US"),
            "en-IN-anusha": VoiceInfo("en-IN-anusha", "Anusha", "female", "IN"),
            "pl-PL-kasia": VoiceInfo("pl-PL-kasia", "Kasia", "female", "PL"),
            "es-MX-luisa": VoiceInfo("es-MX-luisa", "Luisa", "female", "MX"),
            "zh-CN-tao": VoiceInfo("zh-CN-tao", "Tao", "male", "CN"),
            "en-US-molly": VoiceInfo("en-US-molly", "Molly", "female", "US"),
        }
    ),
    "murf_zeroshot": TTSConfig(
        name="Murf Zeroshot",
        api_key_env="MURF_DEV_API_KEY",  # Dev endpoint may require separate API key
        base_url="https://api.dev.murf.ai/v1/speech/stream",
        # All Falcon voices from Murf API (same as falcon)
        supported_voices=[
            "pa-IN-harman", "en-US-alina", "en-UK-hazel", "en-US-cooper", "en-US-imani",
            "mr-IN-rujuta", "en-US-wayne", "kn-IN-rajesh", "en-US-daniel", "hr-HR-marija",
            "en-IN-samar", "bn-IN-anwesha", "hi-IN-khyati", "es-MX-alejandro", "en-AU-joyce",
            "en-US-zion", "en-IN-isha", "en-US-riley", "en-US-carter", "ta-IN-sarvesh",
            "en-UK-gabriel", "en-UK-juliet", "en-IN-arohi", "de-DE-josephine", "en-UK-hugo",
            "en-US-samantha", "de-DE-erna", "en-IN-nikhil", "en-IN-anisha", "zh-CN-baolin",
            "pt-BR-isadora", "en-US-terrell", "en-US-denzel", "en-UK-heidi", "en-US-miles",
            "en-US-abigail", "mr-IN-vaibhav", "en-AU-shane", "ta-IN-murali", "en-UK-peter",
            "it-IT-giulia", "nl-NL-famke", "en-AU-ivy", "nl-NL-dirk", "fr-FR-axel",
            "fr-FR-guillaume", "es-ES-carla", "en-US-claire", "ko-KR-jangmi", "ko-KR-sanghoon",
            "ja-JP-denki", "es-ES-elvira", "es-ES-enrique", "en-UK-aiden", "en-US-ronnie",
            "en-UK-amber", "en-AU-jimm", "en-UK-pearl", "pt-BR-benício", "en-UK-freddie",
            "en-US-ryan", "pt-BR-eloa", "hi-IN-karan", "en-US-charlotte", "hi-IN-namrita",
            "de-DE-lia", "en-US-natalie", "ta-IN-suresh", "en-US-michelle", "en-US-phoebe",
            "es-ES-carmen", "en-US-caleb", "en-US-iris", "en-UK-harrison", "en-US-marcus",
            "en-US-josie", "en-US-ariana", "en-US-daisy", "en-US-charles", "en-UK-reggie",
            "en-US-julia", "en-SCOTT-emily", "en-US-dylan", "es-MX-valeria", "en-IN-eashwar",
            "en-AU-evelyn", "hi-IN-sunaina", "de-DE-lara", "en-US-evander", "en-IN-tanushree",
            "en-SCOTT-rory", "pt-BR-yago", "ta-IN-iniya", "en-AU-leyton", "zh-CN-wei",
            "de-DE-matthias", "it-IT-angelo", "en-IN-rohan", "en-US-delilah", "en-US-paul",
            "en-US-lucas", "bn-IN-abhik", "en-US-angela", "en-US-naomi", "es-MX-carlos",
            "nl-NL-merel", "ja-JP-kenji", "en-US-alicia", "en-IN-alia", "zh-CN-jiao",
            "en-US-june", "en-AU-ashton", "en-UK-finley", "pl-PL-blazej", "el-GR-stavros",
            "zh-CN-zhang", "en-AU-sophia", "en-AU-kylie", "en-US-jayden", "en-IN-aarav",
            "en-US-matthew", "de-DE-björn", "zh-CN-yuxan", "ko-KR-jong-su", "en-AU-harper",
            "ta-IN-abirami", "en-UK-ruby", "ja-JP-kimi", "en-US-ken", "pt-BR-silvio",
            "de-DE-ralf", "en-UK-jaxon", "en-US-river", "en-IN-priya", "en-UK-theo",
            "en-UK-katie", "pl-PL-jacek", "en-US-maverick", "en-US-will", "hi-IN-aman",
            "en-US-amara", "en-UK-mason", "pt-BR-gustavo", "es-ES-javier", "en-AU-mitch",
            "pt-BR-heitor", "fr-CA-alexis", "en-US-edmund", "en-IN-anusha", "pl-PL-kasia",
            "es-MX-luisa", "zh-CN-tao", "en-US-molly"
        ],
        max_chars=3000,
        supports_streaming=True,
        model_name="Zeroshot",
        voice_info={
            "pa-IN-harman": VoiceInfo("pa-IN-harman", "Harman", "male", "IN"),
            "en-US-alina": VoiceInfo("en-US-alina", "Alina", "female", "US"),
            "en-UK-hazel": VoiceInfo("en-UK-hazel", "Hazel", "female", "UK"),
            "en-US-cooper": VoiceInfo("en-US-cooper", "Cooper", "male", "US"),
            "en-US-imani": VoiceInfo("en-US-imani", "Imani", "female", "US"),
            "mr-IN-rujuta": VoiceInfo("mr-IN-rujuta", "Rujuta", "female", "IN"),
            "en-US-wayne": VoiceInfo("en-US-wayne", "Wayne", "male", "US"),
            "kn-IN-rajesh": VoiceInfo("kn-IN-rajesh", "Rajesh", "male", "IN"),
            "en-US-daniel": VoiceInfo("en-US-daniel", "Daniel", "male", "US"),
            "hr-HR-marija": VoiceInfo("hr-HR-marija", "Marija", "female", "HR"),
            "en-IN-samar": VoiceInfo("en-IN-samar", "Samar", "male", "IN"),
            "bn-IN-anwesha": VoiceInfo("bn-IN-anwesha", "Anwesha", "female", "IN"),
            "hi-IN-khyati": VoiceInfo("hi-IN-khyati", "Khyati", "female", "IN"),
            "es-MX-alejandro": VoiceInfo("es-MX-alejandro", "Alejandro", "male", "MX"),
            "en-AU-joyce": VoiceInfo("en-AU-joyce", "Joyce", "female", "AU"),
            "en-US-zion": VoiceInfo("en-US-zion", "Zion", "male", "US"),
            "en-IN-isha": VoiceInfo("en-IN-isha", "Isha", "female", "IN"),
            "en-US-riley": VoiceInfo("en-US-riley", "Riley", "female", "US"),
            "en-US-carter": VoiceInfo("en-US-carter", "Carter", "male", "US"),
            "ta-IN-sarvesh": VoiceInfo("ta-IN-sarvesh", "Sarvesh", "male", "IN"),
            "en-UK-gabriel": VoiceInfo("en-UK-gabriel", "Gabriel", "male", "UK"),
            "en-UK-juliet": VoiceInfo("en-UK-juliet", "Juliet", "female", "UK"),
            "en-IN-arohi": VoiceInfo("en-IN-arohi", "Arohi", "female", "IN"),
            "de-DE-josephine": VoiceInfo("de-DE-josephine", "Josephine", "female", "DE"),
            "en-UK-hugo": VoiceInfo("en-UK-hugo", "Hugo", "male", "UK"),
            "en-US-samantha": VoiceInfo("en-US-samantha", "Samantha", "female", "US"),
            "de-DE-erna": VoiceInfo("de-DE-erna", "Erna", "female", "DE"),
            "en-IN-nikhil": VoiceInfo("en-IN-nikhil", "Nikhil", "male", "IN"),
            "en-IN-anisha": VoiceInfo("en-IN-anisha", "Anisha", "female", "IN"),
            "zh-CN-baolin": VoiceInfo("zh-CN-baolin", "Baolin", "female", "CN"),
            "pt-BR-isadora": VoiceInfo("pt-BR-isadora", "Isadora", "female", "BR"),
            "en-US-terrell": VoiceInfo("en-US-terrell", "Terrell", "male", "US"),
            "en-US-denzel": VoiceInfo("en-US-denzel", "Denzel", "male", "US"),
            "en-UK-heidi": VoiceInfo("en-UK-heidi", "Heidi", "female", "UK"),
            "en-US-miles": VoiceInfo("en-US-miles", "Miles", "male", "US"),
            "en-US-abigail": VoiceInfo("en-US-abigail", "Abigail", "female", "US"),
            "mr-IN-vaibhav": VoiceInfo("mr-IN-vaibhav", "Vaibhav", "male", "IN"),
            "en-AU-shane": VoiceInfo("en-AU-shane", "Shane", "male", "AU"),
            "ta-IN-murali": VoiceInfo("ta-IN-murali", "Murali", "male", "IN"),
            "en-UK-peter": VoiceInfo("en-UK-peter", "Peter", "male", "UK"),
            "it-IT-giulia": VoiceInfo("it-IT-giulia", "Giulia", "female", "IT"),
            "nl-NL-famke": VoiceInfo("nl-NL-famke", "Famke", "female", "NL"),
            "en-AU-ivy": VoiceInfo("en-AU-ivy", "Ivy", "female", "AU"),
            "nl-NL-dirk": VoiceInfo("nl-NL-dirk", "Dirk", "male", "NL"),
            "fr-FR-axel": VoiceInfo("fr-FR-axel", "Axel", "male", "FR"),
            "fr-FR-guillaume": VoiceInfo("fr-FR-guillaume", "Guillaume", "male", "FR"),
            "es-ES-carla": VoiceInfo("es-ES-carla", "Carla", "female", "ES"),
            "en-US-claire": VoiceInfo("en-US-claire", "Claire", "female", "US"),
            "ko-KR-jangmi": VoiceInfo("ko-KR-jangmi", "Jangmi", "female", "KR"),
            "ko-KR-sanghoon": VoiceInfo("ko-KR-sanghoon", "SangHoon", "male", "KR"),
            "ja-JP-denki": VoiceInfo("ja-JP-denki", "Denki", "male", "JP"),
            "es-ES-elvira": VoiceInfo("es-ES-elvira", "Elvira", "female", "ES"),
            "es-ES-enrique": VoiceInfo("es-ES-enrique", "Enrique", "male", "ES"),
            "en-UK-aiden": VoiceInfo("en-UK-aiden", "Aiden", "male", "UK"),
            "en-US-ronnie": VoiceInfo("en-US-ronnie", "Ronnie", "male", "US"),
            "en-UK-amber": VoiceInfo("en-UK-amber", "Amber", "female", "UK"),
            "en-AU-jimm": VoiceInfo("en-AU-jimm", "Jimm", "male", "AU"),
            "en-UK-pearl": VoiceInfo("en-UK-pearl", "Pearl", "female", "UK"),
            "pt-BR-benício": VoiceInfo("pt-BR-benício", "Benício", "male", "BR"),
            "en-UK-freddie": VoiceInfo("en-UK-freddie", "Freddie", "male", "UK"),
            "en-US-ryan": VoiceInfo("en-US-ryan", "Ryan", "male", "US"),
            "pt-BR-eloa": VoiceInfo("pt-BR-eloa", "Eloa", "female", "BR"),
            "hi-IN-karan": VoiceInfo("hi-IN-karan", "Karan", "male", "IN"),
            "en-US-charlotte": VoiceInfo("en-US-charlotte", "Charlotte", "female", "US"),
            "hi-IN-namrita": VoiceInfo("hi-IN-namrita", "Namrita", "female", "IN"),
            "de-DE-lia": VoiceInfo("de-DE-lia", "Lia", "female", "DE"),
            "en-US-natalie": VoiceInfo("en-US-natalie", "Natalie", "female", "US"),
            "ta-IN-suresh": VoiceInfo("ta-IN-suresh", "Suresh", "male", "IN"),
            "en-US-michelle": VoiceInfo("en-US-michelle", "Michelle", "female", "US"),
            "en-US-phoebe": VoiceInfo("en-US-phoebe", "Phoebe", "female", "US"),
            "es-ES-carmen": VoiceInfo("es-ES-carmen", "Carmen", "female", "ES"),
            "en-US-caleb": VoiceInfo("en-US-caleb", "Caleb", "male", "US"),
            "en-US-iris": VoiceInfo("en-US-iris", "Iris", "female", "US"),
            "en-UK-harrison": VoiceInfo("en-UK-harrison", "Harrison", "male", "UK"),
            "en-US-marcus": VoiceInfo("en-US-marcus", "Marcus", "male", "US"),
            "en-US-josie": VoiceInfo("en-US-josie", "Josie", "female", "US"),
            "en-US-ariana": VoiceInfo("en-US-ariana", "Ariana", "female", "US"),
            "en-US-daisy": VoiceInfo("en-US-daisy", "Daisy", "female", "US"),
            "en-US-charles": VoiceInfo("en-US-charles", "Charles", "male", "US"),
            "en-UK-reggie": VoiceInfo("en-UK-reggie", "Reggie", "male", "UK"),
            "en-US-julia": VoiceInfo("en-US-julia", "Julia", "female", "US"),
            "en-SCOTT-emily": VoiceInfo("en-SCOTT-emily", "Emily", "female", "SCOTT"),
            "en-US-dylan": VoiceInfo("en-US-dylan", "Dylan", "male", "US"),
            "es-MX-valeria": VoiceInfo("es-MX-valeria", "Valeria", "female", "MX"),
            "en-IN-eashwar": VoiceInfo("en-IN-eashwar", "Eashwar", "male", "IN"),
            "en-AU-evelyn": VoiceInfo("en-AU-evelyn", "Evelyn", "female", "AU"),
            "hi-IN-sunaina": VoiceInfo("hi-IN-sunaina", "Sunaina", "female", "IN"),
            "de-DE-lara": VoiceInfo("de-DE-lara", "Lara", "female", "DE"),
            "en-US-evander": VoiceInfo("en-US-evander", "Evander", "male", "US"),
            "en-IN-tanushree": VoiceInfo("en-IN-tanushree", "Tanushree", "female", "IN"),
            "en-SCOTT-rory": VoiceInfo("en-SCOTT-rory", "Rory", "male", "SCOTT"),
            "pt-BR-yago": VoiceInfo("pt-BR-yago", "Yago", "male", "BR"),
            "ta-IN-iniya": VoiceInfo("ta-IN-iniya", "Iniya", "female", "IN"),
            "en-AU-leyton": VoiceInfo("en-AU-leyton", "Leyton", "male", "AU"),
            "zh-CN-wei": VoiceInfo("zh-CN-wei", "Wei", "female", "CN"),
            "de-DE-matthias": VoiceInfo("de-DE-matthias", "Matthias", "male", "DE"),
            "it-IT-angelo": VoiceInfo("it-IT-angelo", "Angelo", "male", "IT"),
            "en-IN-rohan": VoiceInfo("en-IN-rohan", "Rohan", "male", "IN"),
            "en-US-delilah": VoiceInfo("en-US-delilah", "Delilah", "female", "US"),
            "en-US-paul": VoiceInfo("en-US-paul", "Paul", "male", "US"),
            "en-US-lucas": VoiceInfo("en-US-lucas", "Lucas", "male", "US"),
            "bn-IN-abhik": VoiceInfo("bn-IN-abhik", "Abhik", "male", "IN"),
            "en-US-angela": VoiceInfo("en-US-angela", "Angela", "female", "US"),
            "en-US-naomi": VoiceInfo("en-US-naomi", "Naomi", "female", "US"),
            "es-MX-carlos": VoiceInfo("es-MX-carlos", "Carlos", "male", "MX"),
            "nl-NL-merel": VoiceInfo("nl-NL-merel", "Merel", "female", "NL"),
            "ja-JP-kenji": VoiceInfo("ja-JP-kenji", "Kenji", "male", "JP"),
            "en-US-alicia": VoiceInfo("en-US-alicia", "Alicia", "female", "US"),
            "en-IN-alia": VoiceInfo("en-IN-alia", "Alia", "female", "IN"),
            "zh-CN-jiao": VoiceInfo("zh-CN-jiao", "Jiao", "female", "CN"),
            "en-US-june": VoiceInfo("en-US-june", "June", "female", "US"),
            "en-AU-ashton": VoiceInfo("en-AU-ashton", "Ashton", "male", "AU"),
            "en-UK-finley": VoiceInfo("en-UK-finley", "Finley", "male", "UK"),
            "pl-PL-blazej": VoiceInfo("pl-PL-blazej", "Blazej", "male", "PL"),
            "el-GR-stavros": VoiceInfo("el-GR-stavros", "Stavros", "male", "GR"),
            "zh-CN-zhang": VoiceInfo("zh-CN-zhang", "Zhang", "male", "CN"),
            "en-AU-sophia": VoiceInfo("en-AU-sophia", "Sophia", "female", "AU"),
            "en-AU-kylie": VoiceInfo("en-AU-kylie", "Kylie", "female", "AU"),
            "en-US-jayden": VoiceInfo("en-US-jayden", "Jayden", "male", "US"),
            "en-IN-aarav": VoiceInfo("en-IN-aarav", "Aarav", "male", "IN"),
            "en-US-matthew": VoiceInfo("en-US-matthew", "Matthew", "male", "US"),
            "de-DE-björn": VoiceInfo("de-DE-björn", "Björn", "male", "DE"),
            "zh-CN-yuxan": VoiceInfo("zh-CN-yuxan", "Yuxan", "male", "CN"),
            "ko-KR-jong-su": VoiceInfo("ko-KR-jong-su", "Jong-su", "male", "KR"),
            "en-AU-harper": VoiceInfo("en-AU-harper", "Harper", "male", "AU"),
            "ta-IN-abirami": VoiceInfo("ta-IN-abirami", "Abirami", "female", "IN"),
            "en-UK-ruby": VoiceInfo("en-UK-ruby", "Ruby", "female", "UK"),
            "ja-JP-kimi": VoiceInfo("ja-JP-kimi", "Kimi", "female", "JP"),
            "en-US-ken": VoiceInfo("en-US-ken", "Ken", "male", "US"),
            "pt-BR-silvio": VoiceInfo("pt-BR-silvio", "Silvio", "male", "BR"),
            "de-DE-ralf": VoiceInfo("de-DE-ralf", "Ralf", "male", "DE"),
            "en-UK-jaxon": VoiceInfo("en-UK-jaxon", "Jaxon", "male", "UK"),
            "en-US-river": VoiceInfo("en-US-river", "River", "nonbinary", "US"),
            "en-IN-priya": VoiceInfo("en-IN-priya", "Priya", "female", "IN"),
            "en-UK-theo": VoiceInfo("en-UK-theo", "Theo", "male", "UK"),
            "en-UK-katie": VoiceInfo("en-UK-katie", "Katie", "female", "UK"),
            "pl-PL-jacek": VoiceInfo("pl-PL-jacek", "Jacek", "male", "PL"),
            "en-US-maverick": VoiceInfo("en-US-maverick", "Maverick", "male", "US"),
            "en-US-will": VoiceInfo("en-US-will", "Will", "male", "US"),
            "hi-IN-aman": VoiceInfo("hi-IN-aman", "Aman", "male", "IN"),
            "en-US-amara": VoiceInfo("en-US-amara", "Amara", "female", "US"),
            "en-UK-mason": VoiceInfo("en-UK-mason", "Mason", "male", "UK"),
            "pt-BR-gustavo": VoiceInfo("pt-BR-gustavo", "Gustavo", "male", "BR"),
            "es-ES-javier": VoiceInfo("es-ES-javier", "Javier", "male", "ES"),
            "en-AU-mitch": VoiceInfo("en-AU-mitch", "Mitch", "male", "AU"),
            "pt-BR-heitor": VoiceInfo("pt-BR-heitor", "Heitor", "male", "BR"),
            "fr-CA-alexis": VoiceInfo("fr-CA-alexis", "Alexis", "male", "CA"),
            "en-US-edmund": VoiceInfo("en-US-edmund", "Edmund", "male", "US"),
            "en-IN-anusha": VoiceInfo("en-IN-anusha", "Anusha", "female", "IN"),
            "pl-PL-kasia": VoiceInfo("pl-PL-kasia", "Kasia", "female", "PL"),
            "es-MX-luisa": VoiceInfo("es-MX-luisa", "Luisa", "female", "MX"),
            "zh-CN-tao": VoiceInfo("zh-CN-tao", "Tao", "male", "CN"),
            "en-US-molly": VoiceInfo("en-US-molly", "Molly", "female", "US"),
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
        supported_voices=["aura-2-asteria-en", "aura-2-luna-en", "aura-2-athena-en", "aura-2-hera-en", "aura-2-orion-en", "aura-2-apollo-en"],
        max_chars=2000,
        supports_streaming=True,
        model_name="aura-2",
        voice_info={
            "aura-2-asteria-en": VoiceInfo("aura-2-asteria-en", "Asteria", "female", "US"),
            "aura-2-luna-en": VoiceInfo("aura-2-luna-en", "Luna", "female", "US"),
            "aura-2-athena-en": VoiceInfo("aura-2-athena-en", "Athena", "female", "US"),
            "aura-2-hera-en": VoiceInfo("aura-2-hera-en", "Hera", "female", "US"),
            "aura-2-orion-en": VoiceInfo("aura-2-orion-en", "Orion", "male", "US"),
            "aura-2-apollo-en": VoiceInfo("aura-2-apollo-en", "Apollo", "male", "US"),
        }
    ),
    "elevenlabs_flash": TTSConfig(
        name="ElevenLabs Flash",
        api_key_env="ELEVENLABS_API_KEY",
        base_url="https://api.elevenlabs.io/v1/text-to-speech",
        supported_voices=["Laura", "Jessica", "Liam", "Elizabeth", "Jarnathan", "Dan", "Nathaniel"],
        max_chars=5000,
        supports_streaming=True,
        model_name="eleven_flash_v2_5",
        voice_info={
            "Laura": VoiceInfo("Laura", "Laura", "female", "US"),
            "Jessica": VoiceInfo("Jessica", "Jessica", "female", "US"),
            "Liam": VoiceInfo("Liam", "Liam", "male", "US"),
            "Elizabeth": VoiceInfo("Elizabeth", "Elizabeth", "female", "UK"),
            "Jarnathan": VoiceInfo("Jarnathan", "Jarnathan", "male", "US"),
            "Dan": VoiceInfo("Dan", "Dan", "male", "UK"),
            "Nathaniel": VoiceInfo("Nathaniel", "Nathaniel", "male", "UK"),
        }
    ),
    "elevenlabs_v3": TTSConfig(
        name="ElevenLabs v3",
        api_key_env="ELEVENLABS_API_KEY",
        base_url="https://api.elevenlabs.io/v1/text-to-speech",
        supported_voices=["Laura", "Jessica", "Liam", "Elizabeth", "Jarnathan", "Dan", "Nathaniel"],
        max_chars=5000,
        supports_streaming=True,
        model_name="eleven_v3",
        voice_info={
            "Laura": VoiceInfo("Laura", "Laura", "female", "US"),
            "Jessica": VoiceInfo("Jessica", "Jessica", "female", "US"),
            "Liam": VoiceInfo("Liam", "Liam", "male", "US"),
            "Elizabeth": VoiceInfo("Elizabeth", "Elizabeth", "female", "UK"),
            "Jarnathan": VoiceInfo("Jarnathan", "Jarnathan", "male", "US"),
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
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "male", "US"),
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
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "male", "US"),
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
            "Conversational Lady": VoiceInfo("Conversational Lady", "Conversational Lady", "male", "US"),
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
    ),
    "sarvam_bulbul_v3": TTSConfig(
        name="Sarvam AI Bulbul v3",
        api_key_env="SARVAM_API_KEY",
        base_url="https://api.sarvam.ai/text-to-speech",
        supported_voices=["en-IN-male", "en-IN-female", "hi-IN-male", "hi-IN-female"],
        max_chars=5000,
        supports_streaming=False,
        model_name="bulbul:v3",
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

def get_voices_by_gender_and_locale(provider_id: str, gender: str, locale: str = None) -> List[str]:
    """Get voices filtered by gender and locale/language for a provider
    
    Locale options:
    - "US" for US English (en-US)
    """
    if provider_id in TTS_PROVIDERS:
        voices = []
        supported_voices_set = set(TTS_PROVIDERS[provider_id].supported_voices)
        for voice_id, info in TTS_PROVIDERS[provider_id].voice_info.items():
            # Only include voices that match gender AND are in supported_voices
            if info.gender == gender and voice_id in supported_voices_set:
                if locale is None:
                    # No locale filter - include all
                    voices.append(voice_id)
                elif locale == "US":
                    # US English - check accent field or voice ID pattern
                    if info.accent == "US" or "en-US" in voice_id or "en-US" in voice_id.lower():
                        voices.append(voice_id)
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
    
    # Special handling for murf_zeroshot - use dev API key
    if provider == "murf_zeroshot":
        # First try MURF_DEV_API_KEY from env
        if api_key:
            return api_key
        # Fallback to hardcoded dev API key for zeroshot
        return "REDACTED_API_KEY_REMOVED"
    
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