"""
TTS Benchmarking Tool - Streamlit Application
"""
import streamlit as st
import streamlit.components.v1 as components
import asyncio
import pandas as pd
import plotly.express as px
import json
import base64
import time 
from datetime import datetime
from typing import Dict, List, Any

from dotenv import load_dotenv
load_dotenv()

from config import TTS_PROVIDERS, UI_CONFIG, validate_config
from dataset import DatasetGenerator, TestSample
from benchmarking_engine import BenchmarkEngine, BenchmarkResult
from tts_providers import TTSProviderFactory, TTSRequest
import visualizations
from security import session_manager
from geolocation import geo_service
from database import BenchmarkDatabase

st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state="expanded"
)

def load_css():
    with open('styles.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

if "benchmark_engine" not in st.session_state:
    st.session_state.benchmark_engine = BenchmarkEngine()

if "dataset_generator" not in st.session_state:
    st.session_state.dataset_generator = DatasetGenerator()

if "results" not in st.session_state:
    st.session_state.results = []

db = BenchmarkDatabase()

if "config_valid" not in st.session_state:
    st.session_state.config_valid = False

if "navigate_to" not in st.session_state:
    st.session_state.navigate_to = None

def get_model_name(provider: str) -> str:
    """Helper function to get model name from config"""
    return TTS_PROVIDERS.get(provider).model_name if provider in TTS_PROVIDERS else provider

def get_provider_display_name(provider_id: str) -> str:
    """Get display name for provider - shows 'Murf' instead of 'Murf Falcon Oct 23'"""
    if provider_id in TTS_PROVIDERS:
        return TTS_PROVIDERS[provider_id].name
    return provider_id.title()

def get_location_display(result: BenchmarkResult = None, country: str = None, city: str = None) -> str:
    """Helper function to format location display with flag"""
    if result:
        country = result.location_country
        city = result.location_city
    
    if not country or country == 'Unknown':
        return '🌍 Unknown'
    
    flag = geo_service.get_country_flag(getattr(result, 'location_country', None) if result else None)
    
    if city and city != 'Unknown':
        return f"{flag} {city}, {country}"
    return f"{flag} {country}"

def check_configuration():
    """Check if API keys are configured"""
    config_status = validate_config()
    st.session_state.config_valid = config_status["valid"]
    return config_status

def main():
    """Main application function"""
    
    st.markdown("""
    <style>
    @keyframes catchyPulse {
        0% { 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7);
        }
        50% { 
            transform: scale(1.15);
            box-shadow: 0 0 10px 5px rgba(255, 75, 75, 0);
        }
        100% { 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 75, 75, 0);
        }
    }
    .feature-banner {
        padding: 0;
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: flex-end;
        position: relative;
    }
    .new-badge {
        animation: catchyPulse 1.5s ease-in-out infinite;
        display: inline-block;
        background: #ff4b4b;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .feature-text {
        color: #262730;
        font-size: 15px;
        margin: 0;
        position: relative;
        display: inline-block;
    }
    .feature-text strong {
        position: relative;
        display: inline-block;
        padding-bottom: 5px;
    }
    .feature-text strong::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        overflow: hidden;
        background: repeating-linear-gradient(
            to right,
            #808080 0px,
            #808080 6px,
            transparent 6px,
            transparent 12px
        );
        background-size: 12px 2px;
        animation: moveDots 1.5s linear infinite;
    }
    @keyframes moveDots {
        0% { 
            background-position: 0 0;
        }
        100% { 
            background-position: 12px 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("TTS Benchmarking Tool")
    st.markdown("Compare Text-to-Speech providers with comprehensive metrics and analysis")
    
    with st.sidebar:
        default_page = "Blind Test"
        
        st.subheader("Navigator")
        
        pages = ["Blind Test", "Leaderboard", "Quick Test"]
        
        for i, page_name in enumerate(pages):
            if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        if "navigate_to" in st.session_state and st.session_state.navigate_to:
            page = st.session_state.navigate_to
            st.session_state.navigate_to = None
        else:
            page = st.session_state.get("current_page", "Blind Test")
        
        st.divider()
        
        st.subheader("Models Configured")
        
        config_status = check_configuration()
        
        if config_status["valid"]:
            for provider_id, status in config_status["providers"].items():
                provider_name = TTS_PROVIDERS[provider_id].name
                # Show "Murf Falcon" in configuration sidebar for Murf
                if provider_id == "murf_falcon_oct23":
                    display_name = "Murf Falcon"
                else:
                    display_name = provider_name
                if status["configured"]:
                    st.write(f"🟢 {display_name}")
                else:
                    st.write(f"🔴 {display_name}")
        else:
            st.error("❌ No API keys configured")
            st.markdown("**Set at least one API key:**")
            for provider_id, status in config_status["providers"].items():
                if not status["configured"]:
                    env_var = TTS_PROVIDERS[provider_id].api_key_env
                    provider_name = TTS_PROVIDERS[provider_id].name
                    # Show "Murf Falcon" in configuration sidebar for Murf
                    if provider_id == "murf_falcon_oct23":
                        display_name = "Murf Falcon"
                    else:
                        display_name = provider_name
                    st.code(f"export {env_var}=your_api_key_here")
                    st.caption(f"For {display_name}")
    
    if page == "Quick Test":
        quick_test_page()
    elif page == "Blind Test":
        blind_test_page()
    elif page == "Leaderboard":
        leaderboard_page()

def quick_test_page():
    """Quick test page for single TTS comparisons"""
    
    st.header("Quick Test")
    st.markdown("Test a single text prompt across multiple TTS providers")
    
    if "quick_test_results" not in st.session_state:
        st.session_state.quick_test_results = None
    
    config_status = check_configuration()
    
    if not st.session_state.config_valid:
        st.warning("Please configure at least one API key in the sidebar first.")
        return
    
    configured_providers = [
        provider_id for provider_id, status in config_status["providers"].items() 
        if status["configured"]
    ]
    
    if not configured_providers:
        st.error("No providers are configured. Please set API keys in the sidebar.")
        return
    
    text_input = st.text_area(
        "Enter text to synthesize:",
        value="Just to confirm, the co-applicant's name is spelled M-A-R-I-S-A, correct? I'll need her consent before I can proceed with income verification.",
        height=100,
        max_chars=1000
    )
    
    word_count = len(text_input.split())
    
    # Create display names for multiselect
    provider_display_options = []
    for p in configured_providers:
        # Show "Murf Falcon" in quick test dropdown for Murf
        if p == "murf_falcon_oct23":
            display_name = "Murf Falcon"
        else:
            display_name = get_provider_display_name(p)
        provider_display_options.append(display_name)
    
    selected_display_names = st.multiselect(
        "Select providers:",
        provider_display_options,
        default=provider_display_options,
        help=f"Available providers: {', '.join(provider_display_options)}"
    )
    
    # Map back to provider IDs
    selected_providers = []
    for display_name in selected_display_names:
        for p in configured_providers:
            # Handle "Murf Falcon" mapping
            if display_name == "Murf Falcon" and p == "murf_falcon_oct23":
                selected_providers.append(p)
                break
            elif get_provider_display_name(p) == display_name:
                selected_providers.append(p)
                break
        
    voice_options = {}
    if selected_providers:
        st.markdown("**Voice Selection:**")
        
        for i in range(0, len(selected_providers), 4):
            cols = st.columns(4)
            for j, provider in enumerate(selected_providers[i:i+4]):
                with cols[j]:
                    voices = TTS_PROVIDERS[provider].supported_voices
                    # Show "Murf Falcon" in quick test dropdown for Murf
                    if provider == "murf_falcon_oct23":
                        provider_display = "Murf Falcon"
                    else:
                        provider_display = get_provider_display_name(provider)
                    voice_options[provider] = st.selectbox(
                        f"{provider_display} voice:",
                        voices,
                        key=f"voice_{provider}"
                    )
        
    if st.button("Generate & Compare", type="primary"):
        if text_input and selected_providers:
            valid, error_msg = session_manager.validate_request(text_input)
            if valid:
                run_quick_test(text_input, selected_providers, voice_options)
            else:
                st.error(f"❌ {error_msg}")
        else:
            st.warning("Please enter text and select at least one provider.")
    
    if st.session_state.quick_test_results is not None:
        st.markdown("---")  # Separator line
        display_quick_test_results(st.session_state.quick_test_results)

def run_quick_test(text: str, providers: List[str], voice_options: Dict[str, str]):
    """Run quick test for selected providers"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    async def test_provider(provider_id: str, voice: str):
        try:
            provider = TTSProviderFactory.create_provider(provider_id)
            
            # Create test sample
            sample = TestSample(
                id="quick_test",
                text=text,
                word_count=len(text.split()),
                category="user_input",
                length_category="custom",
                complexity_score=0.5
            )
            
            result = await st.session_state.benchmark_engine.run_single_test(
                provider, sample, voice
            )
            return result
            
        except Exception as e:
            st.error(f"Error testing {provider_id}: {str(e)}")
            return None
    
    # Run tests
    for i, provider_id in enumerate(providers):
        status_text.text(f"Testing {provider_id}...")
        
        voice = voice_options[provider_id]
        result = asyncio.run(test_provider(provider_id, voice))
        
        if result:
            results.append(result)
        
        progress_bar.progress((i + 1) / len(providers))
    
    status_text.text("✅ Tests completed!")
    
    # Clean up progress indicators after a moment
    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    # Store results in session state for display
    if results:
        st.session_state.quick_test_results = results
    else:
        st.error("No successful results to display.")
        st.session_state.quick_test_results = None

def display_quick_test_results(results: List[BenchmarkResult]):
    """Display quick test results"""
    
    st.subheader("Test Results")
    
    data = []
    for result in results:
        provider_display = get_provider_display_name(result.provider)
        data.append({
            "Provider": provider_display,
            "Model": result.model_name,
            "Location": get_location_display(result),
            "Success": "✅" if result.success else "❌",
            "TTFB (ms)": f"{result.ttfb:.1f}" if result.success and result.ttfb > 0 else "N/A",
            "File Size (KB)": f"{result.file_size_bytes / 1024:.1f}" if result.success else "N/A",
            "Voice": result.voice,
            "Error": result.error_message if not result.success else ""
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    successful_results = [r for r in results if r.success]
    
    if len(successful_results) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ttfb = px.bar(
                x=[get_provider_display_name(r.provider) for r in successful_results],
                y=[r.ttfb for r in successful_results],
                title="TTFB Comparison",
                labels={"x": "Provider", "y": "TTFB (ms)"}
            )
            st.plotly_chart(fig_ttfb, use_container_width=True)
        
        with col2:
            fig_size = px.bar(
                x=[get_provider_display_name(r.provider) for r in successful_results],
                y=[r.file_size_bytes / 1024 for r in successful_results],
                title="File Size Comparison",
                labels={"x": "Provider", "y": "File Size (KB)"}
            )
            st.plotly_chart(fig_size, use_container_width=True)
    
    st.subheader("Audio Playback")
    
    if len(successful_results) >= 1:
        st.markdown("**Listen to the audio samples:**")
        
        for i in range(0, len(successful_results), 4):
            cols = st.columns(4)
            for j, result in enumerate(successful_results[i:i+4]):
                with cols[j]:
                    provider_display = get_provider_display_name(result.provider)
                    st.markdown(f"**{provider_display}**")
                    st.caption(f"Model: {result.model_name}")
                    
                    if result.audio_data:
                        audio_base64 = base64.b64encode(result.audio_data).decode()
                        audio_html = f"""
                        <audio controls controlsList="nodownload" style="width: 100%;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                        </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.caption(f"TTFB: {result.ttfb:.1f}ms")
                        st.caption(f"Size: {result.file_size_bytes/1024:.1f} KB")
                        
                        st.download_button(
                            label="Download MP3",
                            data=result.audio_data,
                            file_name=f"{result.provider}_{result.voice}.mp3",
                            mime="audio/mpeg",
                            key=f"download_{result.provider}_{i}_{j}"
                        )

def blind_test_page():
    """Blind test page for unbiased audio quality comparison - Voice Battles style"""
    
    st.header("Voice Battles - Blind Test")
    st.markdown("Compare TTS providers head-to-head. Listen to at least 3 seconds of each sample before voting.")
    
    config_status = check_configuration()
    
    if not st.session_state.config_valid:
        st.warning("Please configure at least one API key in the sidebar first.")
        return
    
    configured_providers = [
        provider_id for provider_id, status in config_status["providers"].items() 
        if status["configured"]
    ]
    
    if len(configured_providers) < 2:
        st.warning("⚠️ Blind test requires at least 2 configured providers. Please configure more API keys.")
        return
    
    # Initialize session state for progressive blind test
    if "blind_test_sentences" not in st.session_state:
        st.session_state.blind_test_sentences = []
    if "blind_test_current_pair" not in st.session_state:
        st.session_state.blind_test_current_pair = None
    if "blind_test_comparison_count" not in st.session_state:
        st.session_state.blind_test_comparison_count = 0
    if "blind_test_max_comparisons" not in st.session_state:
        st.session_state.blind_test_max_comparisons = 25
    if "blind_test_results_history" not in st.session_state:
        st.session_state.blind_test_results_history = []
    if "blind_test_selected_competitors" not in st.session_state:
        st.session_state.blind_test_selected_competitors = []
    if "blind_test_murf_voice" not in st.session_state:
        st.session_state.blind_test_murf_voice = None
    if "blind_test_murf_voices" not in st.session_state:
        st.session_state.blind_test_murf_voices = []  # List of selected MURF voices (up to 4)
    if "blind_test_gender_filter" not in st.session_state:
        st.session_state.blind_test_gender_filter = "female"
    if "blind_test_setup_complete" not in st.session_state:
        st.session_state.blind_test_setup_complete = False
    if "blind_test_audio_played" not in st.session_state:
        st.session_state.blind_test_audio_played = {"A": 0, "B": 0}
    if "show_final_results" not in st.session_state:
        st.session_state.show_final_results = False
    
    # If final results should be shown, display them directly
    if st.session_state.get("show_final_results", False):
        display_final_results()
        return
    
    # Show setup or comparison view
    # Preserve test state: if test is in progress, show comparison view (even if error occurred)
    # This ensures that if user navigates away and comes back, they continue where they left off
    test_in_progress = (
        st.session_state.blind_test_setup_complete or 
        st.session_state.blind_test_comparison_count > 0 or 
        st.session_state.blind_test_current_pair is not None or
        len(st.session_state.blind_test_results_history) > 0
    )
    
    if test_in_progress:
        # Test is in progress - show comparison view (will handle errors gracefully)
        display_blind_test_comparison()
    else:
        # No test in progress - show setup
        display_blind_test_setup(configured_providers)

def display_blind_test_setup(configured_providers: List[str]):
    """Display the blind test setup page"""
    from config import get_voices_by_gender, get_voice_gender
    import random
    
    # Get Murf providers and other providers
    murf_providers = [p for p in configured_providers if "murf" in p.lower()]
    other_providers = [p for p in configured_providers if "murf" not in p.lower()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**1. Select Competitor**")
        
        # Create dropdown options for competitors
        competitor_options = []
        competitor_ids = []
        for provider_id in other_providers:
            provider_name = TTS_PROVIDERS[provider_id].name
            model_name = TTS_PROVIDERS[provider_id].model_name
            competitor_options.append(f"{provider_name} ({model_name})")
            competitor_ids.append(provider_id)
        
        if competitor_options:
            selected_competitor_display = st.selectbox(
                "Test Murf against:",
                competitor_options,
                key="competitor_select"
            )
            
            # Map back to provider ID
            selected_idx = competitor_options.index(selected_competitor_display)
            selected_competitor_id = competitor_ids[selected_idx]
            st.session_state.blind_test_selected_competitors = [selected_competitor_id]
            
            # Show competitor voice info
            competitor_voice_info = TTS_PROVIDERS[selected_competitor_id].voice_info
            female_count = sum(1 for v in competitor_voice_info.values() if v.gender == "female")
            male_count = sum(1 for v in competitor_voice_info.values() if v.gender == "male")
            st.caption(f"Available voices: {female_count} female, {male_count} male")
        else:
            st.warning("No competitors configured")
        
        # Test Parameters below competitor dropdown (uses empty space)
        st.markdown("**Test Parameters**")
        max_comparisons = st.slider(
            "Number of comparisons:",
            min_value=5,
            max_value=50,
            value=25,
            step=5,
            help="How many head-to-head comparisons to run"
        )
        st.session_state.blind_test_max_comparisons = max_comparisons
    
    with col2:
        st.markdown("**2. Select Murf Voice**")
        
        # Murf provider dropdown
        if murf_providers:
            murf_options = []
            murf_ids = []
            for p in murf_providers:
                murf_options.append(f"{TTS_PROVIDERS[p].name} ({TTS_PROVIDERS[p].model_name})")
                murf_ids.append(p)
            
            selected_murf_display = st.selectbox(
                "Provider:",
                murf_options,
                key="murf_provider_select"
            )
            
            selected_murf_idx = murf_options.index(selected_murf_display)
            murf_provider = murf_ids[selected_murf_idx]
            st.session_state.blind_test_murf_provider = murf_provider
            
            murf_voice_info = TTS_PROVIDERS[murf_provider].voice_info
            
            # Initialize gender filter if not set
            if "blind_test_gender_filter" not in st.session_state:
                st.session_state.blind_test_gender_filter = "female"
            
            # Gender selection - text labels side by side using radio
            selected_gender_radio = st.radio(
                "**Gender:**",
                ["Male", "Female"],
                index=0 if st.session_state.blind_test_gender_filter == "female" else 1,
                horizontal=True,
                key="gender_radio"
            )
            
            new_gender = selected_gender_radio.lower()
            selected_gender = st.session_state.blind_test_gender_filter
            
            # Only update if gender actually changed (not on every rerun)
            if new_gender != selected_gender:
                st.session_state.blind_test_gender_filter = new_gender
                # Reset voice to first voice of new gender only when gender changes
                filtered_voices_new = [(v, info) for v, info in murf_voice_info.items() if info.gender == new_gender]
                if filtered_voices_new:
                    st.session_state.blind_test_murf_voice = filtered_voices_new[0][0]
                selected_gender = new_gender
            
            # Filter voices by selected gender
            filtered_voices = [(v, info) for v, info in murf_voice_info.items() if info.gender == selected_gender]
            
            # Initialize voice if not set or if current voice is not valid for selected gender
            if "blind_test_murf_voice" not in st.session_state:
                if filtered_voices:
                    st.session_state.blind_test_murf_voice = filtered_voices[0][0]
            elif st.session_state.blind_test_murf_voice not in [v for v, _ in filtered_voices]:
                # Current voice doesn't match gender, reset to first voice of current gender
                if filtered_voices:
                    st.session_state.blind_test_murf_voice = filtered_voices[0][0]
            
            # Voice multiselect (up to 4 voices)
            voice_options = [f"{info.name} ({info.accent})" for v, info in filtered_voices]
            voice_ids = [v for v, info in filtered_voices]
            
            if voice_options:
                # Initialize selected voices if not set
                if "blind_test_murf_voices" not in st.session_state or not st.session_state.blind_test_murf_voices:
                    # Default to first voice if none selected
                    st.session_state.blind_test_murf_voices = [voice_ids[0]] if voice_ids else []
                
                # Find currently selected voice indices for multiselect
                current_selected_indices = []
                for voice_id in st.session_state.blind_test_murf_voices:
                    if voice_id in voice_ids:
                        current_selected_indices.append(voice_ids.index(voice_id))
                
                # Use multiselect to allow selecting up to 4 voices
                selected_voice_displays = st.multiselect(
                    "Select MURF voices (up to 4, will shuffle during comparisons):",
                    voice_options,
                    default=[voice_options[i] for i in current_selected_indices if i < len(voice_options)],
                    max_selections=4,
                    key="murf_voices_multiselect"
                )
                
                # Update session state with selected voice IDs
                selected_voice_ids = []
                for display in selected_voice_displays:
                    idx = voice_options.index(display)
                    selected_voice_ids.append(voice_ids[idx])
                
                st.session_state.blind_test_murf_voices = selected_voice_ids
                
                # Keep backward compatibility: set single voice to first selected for legacy code
                if selected_voice_ids:
                    st.session_state.blind_test_murf_voice = selected_voice_ids[0]
                else:
                    # If no voices selected, default to first voice
                    if voice_ids:
                        st.session_state.blind_test_murf_voices = [voice_ids[0]]
                        st.session_state.blind_test_murf_voice = voice_ids[0]
            
            # Show selected voices info
            if st.session_state.blind_test_murf_voices:
                selected_names = []
                for voice_id in st.session_state.blind_test_murf_voices:
                    voice_info = murf_voice_info.get(voice_id)
                    if voice_info:
                        selected_names.append(voice_info.name)
                if selected_names:
                    st.caption(f"Selected: **{', '.join(selected_names)}** • Will shuffle during comparisons • Will compare with {selected_gender} voices")
        else:
            st.warning("No Murf provider configured")
    
    st.divider()
    
    # Sentence upload section - full width
    st.markdown("**3. Upload Test Sentences** (System will pick randomly)")
    
    sentences_text = st.text_area(
        "Enter sentences (one per line):",
        value="""The quick brown fox jumps over the lazy dog.
The wine glass fills again and laughter breaks through the pressure that had been building quietly for hours.
Just to confirm, the co-applicant's name is spelled M-A-R-I-S-A, correct?
Scientists have made a groundbreaking discovery that could revolutionize renewable energy.
Hello, how can I assist you today with your account inquiry?""",
        height=200,
        help="Enter multiple sentences, one per line. The system will randomly select sentences for each test."
    )
    
    sentences = [s.strip() for s in sentences_text.strip().split('\n') if s.strip()]
    
    # Check if sentences have changed - if so, clear current pair to force regeneration
    if "blind_test_sentences_hash" not in st.session_state:
        st.session_state.blind_test_sentences_hash = None
    
    import hashlib
    sentences_hash = hashlib.md5(str(sorted(sentences)).encode()).hexdigest()
    
    # If sentences changed and there's a current pair, clear it
    if (st.session_state.blind_test_sentences_hash is not None and 
        st.session_state.blind_test_sentences_hash != sentences_hash and
        st.session_state.blind_test_current_pair is not None):
        st.session_state.blind_test_current_pair = None
        st.session_state.blind_test_comparison_count = 0
        st.session_state.blind_test_results_history = []
    
    st.session_state.blind_test_sentences = sentences
    st.session_state.blind_test_sentences_hash = sentences_hash
    st.caption(f"📝 {len(sentences)} sentences loaded")
    
    can_start = (
        len(st.session_state.get("blind_test_selected_competitors", [])) >= 1 and 
        (st.session_state.blind_test_murf_voice or 
         (st.session_state.blind_test_murf_voices and len(st.session_state.blind_test_murf_voices) > 0)) and 
        len(st.session_state.blind_test_sentences) >= 1
    )
    
    # Center the button and make it smaller
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Voice Battle", type="primary", disabled=not can_start):
            st.session_state.blind_test_setup_complete = True
            st.session_state.blind_test_comparison_count = 0
            st.session_state.blind_test_results_history = []
            st.session_state.blind_test_current_pair = None  # Clear any existing pair
            st.rerun()
    
    if not can_start:
        st.caption("Select a competitor and ensure sentences are loaded")


def display_blind_test_comparison():
    """Display the active blind test comparison"""
    from config import get_voices_by_gender, get_voice_gender
    import random
    
    # Check if we should show final results (either completed or user clicked End Test)
    if st.session_state.get("show_final_results", False):
        # Clear the comparison view first to ensure full-width display
        st.session_state.blind_test_current_pair = None
        # Display full-width final results
        display_final_results()
        return
    
    # Check if we need to generate a new pair
    force_regen = st.session_state.get("force_regenerate", False)
    if st.session_state.blind_test_current_pair is None or force_regen:
        # Clear the force flag
        st.session_state.force_regenerate = False
        # Force clear any cached audio state before generating new comparison
        if "blind_test_audio_played" in st.session_state:
            st.session_state.blind_test_audio_played = {"A": 0, "B": 0}
        # CRITICAL: Clear the pair again to ensure no stale data
        st.session_state.blind_test_current_pair = None
        print(f"[DEBUG] Generating new comparison (force_regen={force_regen})")
        generate_next_comparison()
        return
    
    pair = st.session_state.blind_test_current_pair
    
    # Validate that the current pair's text is still in the sentences list
    # If sentences were changed, the pair might have old text - regenerate it
    if pair and pair.get("text"):
        current_text = pair.get("text")
        sentences = st.session_state.get("blind_test_sentences", [])
        if sentences and current_text not in sentences:
            # Current pair has text that's no longer in sentences - regenerate
            st.session_state.blind_test_current_pair = None
            generate_next_comparison()
            return
        
        # Additional validation: Check if this pair was generated with a different comparison count
        # This ensures we don't show stale audio from a previous comparison
        pair_comparison_id = pair.get("comparison_id", "")
        expected_comparison_id = f"{st.session_state.blind_test_comparison_count}_"
        if pair_comparison_id and not pair_comparison_id.startswith(expected_comparison_id):
            # Pair is from a different comparison - regenerate
            st.session_state.blind_test_current_pair = None
            generate_next_comparison()
            return
    
    if pair is None or pair.get("error"):
        error_msg = pair.get("message", "Failed to generate comparison.") if pair else "Failed to generate comparison."
        st.error(f"⚠️ {error_msg}")
        if st.button("Retry", type="primary"):
            st.session_state.blind_test_current_pair = None
            st.rerun()
        return
    
    # Create unique key for this comparison using generation timestamp
    generated_at = pair.get("generated_at", 0)
    comparison_key = f"{st.session_state.blind_test_comparison_count}_{int(generated_at)}"
    
    # CRITICAL DEBUG: Log what we're about to display
    print(f"[DISPLAY DEBUG] Displaying pair:")
    print(f"  - Text: '{pair['text'][:60]}...'")
    print(f"  - Comparison key: {comparison_key}")
    print(f"  - Generated at: {generated_at}")
    if pair.get('sample_a') and hasattr(pair['sample_a'], 'text'):
        print(f"  - Sample A text: '{pair['sample_a'].text[:60] if pair['sample_a'].text else 'N/A'}...'")
    if pair.get('sample_b') and hasattr(pair['sample_b'], 'text'):
        print(f"  - Sample B text: '{pair['sample_b'].text[:60] if pair['sample_b'].text else 'N/A'}...'")
    
    # Progress indicator
    progress = st.session_state.blind_test_comparison_count / st.session_state.blind_test_max_comparisons
    st.progress(progress)
    st.caption(f"Comparison {st.session_state.blind_test_comparison_count + 1} of {st.session_state.blind_test_max_comparisons}")
    
    # Display the prompt/sentence - sleek gray design (no purple border)
    st.markdown(f"""
    <div style="background: #f5f5f5; padding: 12px 16px; border-radius: 8px; margin: 8px 0;">
        <span style="color: #666; font-size: 0.85em; font-weight: 500;">PROMPT</span>
        <p style="color: #333; font-size: 1em; margin: 4px 0 0 0; line-height: 1.5;">{pair['text']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #888; font-size: 0.9em; margin: 16px 0 8px 0;'>Vote to reveal your model preference</p>", unsafe_allow_html=True)
    
    # Audio players side by side with unique keys
    col1, col2 = st.columns(2)
    
    with col1:
        display_audio_player(pair['sample_a'], "A", "left", comparison_key)
        # Add spacing and center the button
        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
        with button_col2:
            if st.button("Vote A", type="primary", key="vote_a", use_container_width=True):
                handle_vote("A", pair)
    
    with col2:
        # Validate audio text matches displayed text before displaying
        sample_b = pair['sample_b']
        if sample_b and hasattr(sample_b, 'metadata') and sample_b.metadata:
            audio_text = sample_b.metadata.get('generated_text', '')
            if audio_text and audio_text != pair['text']:
                st.error(f"⚠️ Audio text mismatch detected! Regenerating...")
                st.session_state.blind_test_current_pair = None
                st.rerun()
                return
        display_audio_player(pair['sample_b'], "B", "right", comparison_key)
        # Add spacing and center the button
        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
        with button_col2:
            if st.button("Vote B", type="primary", key="vote_b", use_container_width=True):
                handle_vote("B", pair)
    
    st.divider()
    
    # Action button - End Test only (centered, medium size)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("End Test", use_container_width=True, type="secondary"):
            # Set flag to show final results, but keep setup_complete True so we stay in comparison view
            st.session_state.show_final_results = True
            st.session_state.blind_test_current_pair = None
            st.rerun()
            return


def display_audio_player(result, label: str, side: str, unique_key: str = ""):
    """Display an audio player using Streamlit's native audio component"""
    import time
    
    has_audio = (result and 
                 hasattr(result, 'audio_data') and 
                 result.audio_data and 
                 hasattr(result, 'success') and 
                 result.success)
    
    if not has_audio:
        error_msg = ""
        if result and hasattr(result, 'error_message') and result.error_message:
            error_msg = f": {result.error_message}"
        st.error(f"Sample {label} failed to generate{error_msg}")
        return
    
    # CRITICAL DEBUG: Log audio data info
    audio_size = len(result.audio_data) if result.audio_data else 0
    text_in_result = result.text if hasattr(result, 'text') else 'N/A'
    print(f"[AUDIO DEBUG] Sample {label}: size={audio_size} bytes, text='{text_in_result[:50] if text_in_result != 'N/A' else 'N/A'}...'")
    
    # Display label
    st.markdown(f"**Sample {label}**")
    
    # Use Streamlit's native audio component - this avoids browser caching issues
    st.audio(result.audio_data, format="audio/mp3")


def generate_next_comparison():
    """Generate the next comparison pair - ALWAYS generates fresh audio"""
    from config import get_voices_by_gender, get_voice_gender
    import random
    import time
    
    print(f"[GENERATE DEBUG] Starting generate_next_comparison for comparison #{st.session_state.blind_test_comparison_count}")
    
    # Check if we've reached max comparisons
    if st.session_state.blind_test_comparison_count >= st.session_state.blind_test_max_comparisons:
        st.session_state.show_final_results = True
        st.rerun()
        return
    
    # FORCE CLEAR any existing pair first to prevent stale audio
    st.session_state.blind_test_current_pair = None
    
    # Generate a unique generation ID for this comparison
    generation_id = f"gen_{int(time.time() * 1000)}_{st.session_state.blind_test_comparison_count}"
    print(f"[GENERATE DEBUG] Generation ID: {generation_id}")
    
    # Get a random sentence
    sentences = st.session_state.blind_test_sentences
    if not sentences:
        st.error("No sentences available")
        return
    
    # CRITICAL: Track which sentences have been used to ensure variety
    if "used_sentences" not in st.session_state:
        st.session_state.used_sentences = []
    
    # Get available sentences (ones not used yet, or all if all have been used)
    available_sentences = [s for s in sentences if s not in st.session_state.used_sentences]
    
    # If all sentences have been used, reset and start fresh
    if not available_sentences:
        st.session_state.used_sentences = []
        available_sentences = sentences
    
    # Select a random sentence from available ones
    text = random.choice(available_sentences)
    
    # Mark this sentence as used
    st.session_state.used_sentences.append(text)
    
    # CRITICAL DEBUG: Log the selected text
    print(f"[CRITICAL DEBUG] Selected sentence #{len(st.session_state.used_sentences)}: '{text[:80]}...'")
    print(f"[CRITICAL DEBUG] Available sentences: {len(available_sentences)}, Total: {len(sentences)}")
    
    # Get configured Murf provider
    config_status = check_configuration()
    murf_providers = [
        p for p, status in config_status["providers"].items() 
        if status["configured"] and "murf" in p.lower()
    ]
    murf_provider_id = "murf_falcon_oct23" if "murf_falcon_oct23" in murf_providers else (murf_providers[0] if murf_providers else None)
    
    if not murf_provider_id:
        st.error("No Murf provider configured. Please set MURF_API_KEY.")
        return
    
    # Get Murf voice - SHUFFLE through selected voices
    gender_filter = st.session_state.blind_test_gender_filter
    comparison_index = st.session_state.blind_test_comparison_count
    
    # Get selected MURF voices (up to 4)
    selected_murf_voices = st.session_state.blind_test_murf_voices if st.session_state.blind_test_murf_voices else []
    
    # If no voices selected, fall back to single voice or get first voice of selected gender
    if not selected_murf_voices:
        murf_voice = st.session_state.blind_test_murf_voice
        if not murf_voice or murf_voice not in TTS_PROVIDERS[murf_provider_id].supported_voices:
            murf_voice_info = TTS_PROVIDERS[murf_provider_id].voice_info
            filtered_voices = [(v, info) for v, info in murf_voice_info.items() if info.gender == gender_filter]
            if filtered_voices:
                murf_voice = filtered_voices[0][0]
                st.session_state.blind_test_murf_voice = murf_voice
                selected_murf_voices = [murf_voice]
        voice_index = 0  # Only one voice selected
    else:
        # Cycle through selected voices based on comparison count
        # Use modulo to cycle through the list
        voice_index = comparison_index % len(selected_murf_voices)
        murf_voice = selected_murf_voices[voice_index]
        
        # Ensure selected voice is still valid
        if murf_voice not in TTS_PROVIDERS[murf_provider_id].supported_voices:
            # Voice is invalid, filter and use first valid one
            murf_voice_info = TTS_PROVIDERS[murf_provider_id].voice_info
            filtered_voices = [(v, info) for v, info in murf_voice_info.items() if info.gender == gender_filter]
            valid_voice_ids = [v for v in selected_murf_voices if v in TTS_PROVIDERS[murf_provider_id].supported_voices]
            if valid_voice_ids:
                voice_index = comparison_index % len(valid_voice_ids)
                murf_voice = valid_voice_ids[voice_index]
            elif filtered_voices:
                murf_voice = filtered_voices[0][0]
                selected_murf_voices = [murf_voice]
                st.session_state.blind_test_murf_voices = selected_murf_voices
                voice_index = 0
    
    print(f"[MURF VOICE DEBUG] Comparison #{comparison_index + 1}: Using MURF voice: {murf_voice} (voice {voice_index + 1} of {len(selected_murf_voices)} selected)")
    
    # Get the selected competitor (single selection now)
    competitors = st.session_state.blind_test_selected_competitors
    if not competitors:
        st.error("No competitor selected")
        return
    
    competitor_id = competitors[0]  # Single competitor selected
    
    # Get a voice with matching gender from competitor - MUST MATCH GENDER
    # Get the actual gender of the selected Murf voice to ensure perfect match
    murf_voice_info = TTS_PROVIDERS[murf_provider_id].voice_info.get(murf_voice)
    if murf_voice_info:
        actual_gender = murf_voice_info.gender
        # Use the actual gender from the voice, not just the filter
        gender_filter = actual_gender
        print(f"[GENDER DEBUG] Murf voice: {murf_voice} is {actual_gender}")
    else:
        print(f"[GENDER DEBUG] WARNING: Could not find Murf voice info for {murf_voice}, using filter: {gender_filter}")
    
    # Get competitor voices matching gender - ensure they're in supported_voices too
    competitor_voices = get_voices_by_gender(competitor_id, gender_filter)
    print(f"[GENDER DEBUG] Competitor {competitor_id} voices matching '{gender_filter}': {competitor_voices}")
    
    # Additional validation: ensure voices are in supported_voices list
    if competitor_id in TTS_PROVIDERS:
        supported_voices_set = set(TTS_PROVIDERS[competitor_id].supported_voices)
        competitor_voices = [v for v in competitor_voices if v in supported_voices_set]
    
    # If no voices found for this gender, try to find any voice with matching gender from voice_info
    if not competitor_voices and competitor_id in TTS_PROVIDERS:
        competitor_voice_info = TTS_PROVIDERS[competitor_id].voice_info
        supported_voices_set = set(TTS_PROVIDERS[competitor_id].supported_voices)
        competitor_voices = [
            v for v, info in competitor_voice_info.items() 
            if info.gender == gender_filter and v in supported_voices_set
        ]
    
    # If still no voices, this is an error - competitor doesn't have voices of this gender
    if not competitor_voices:
        st.error(f"Competitor {TTS_PROVIDERS[competitor_id].name} doesn't have any {gender_filter} voices available. Please select a different competitor.")
        st.session_state.blind_test_current_pair = None
        return
    
    # Select from matching gender voices only
    # If only 1 voice available, use it; otherwise randomly pick one
    if len(competitor_voices) == 1:
        competitor_voice = competitor_voices[0]
        print(f"[GENDER DEBUG] Only 1 {gender_filter} voice available for competitor: {competitor_voice}")
    else:
        competitor_voice = random.choice(competitor_voices)
        print(f"[GENDER DEBUG] Selected {gender_filter} voice for competitor: {competitor_voice} (from {len(competitor_voices)} options)")
    
    # Special handling for Cartesia providers - validate voice exists in voice_id_map
    # CRITICAL: Must ensure gender is maintained when validating Cartesia voices
    if competitor_id in ["cartesia_sonic2", "cartesia_turbo", "cartesia_sonic3"]:
        try:
            provider_obj = TTSProviderFactory.create_provider(competitor_id)
            if hasattr(provider_obj, 'voice_id_map'):
                # First verify the selected voice is in map AND matches gender
                voice_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice)
                voice_in_map = competitor_voice in provider_obj.voice_id_map
                gender_matches = voice_info and voice_info.gender == gender_filter
                
                if not voice_in_map or not gender_matches:
                    # Find voices that are: 1) in voice_id_map, 2) match gender, 3) in supported_voices
                    valid_voices = [
                        v for v in competitor_voices 
                        if v in provider_obj.voice_id_map and
                        TTS_PROVIDERS[competitor_id].voice_info.get(v) and
                        TTS_PROVIDERS[competitor_id].voice_info[v].gender == gender_filter
                    ]
                    
                    if valid_voices:
                        competitor_voice = random.choice(valid_voices)
                        print(f"[CARTESIA DEBUG] Selected valid voice {competitor_voice} (gender: {gender_filter})")
                    else:
                        # Last resort: find any voice matching gender from voice_id_map
                        all_matching = [
                            v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items()
                            if info.gender == gender_filter and 
                            v in provider_obj.voice_id_map and 
                            v in TTS_PROVIDERS[competitor_id].supported_voices
                        ]
                        if all_matching:
                            competitor_voice = random.choice(all_matching)
                            print(f"[CARTESIA DEBUG] Found alternative voice {competitor_voice} (gender: {gender_filter})")
                        else:
                            st.error(f"No {gender_filter} voice found in Cartesia voice mapping. Available: {list(provider_obj.voice_id_map.keys())}")
                            st.session_state.blind_test_current_pair = None
                            return
                else:
                    print(f"[CARTESIA DEBUG] Voice {competitor_voice} is valid (in map, gender: {gender_filter})")
        except Exception as e:
            print(f"Warning: Could not validate Cartesia voice: {e}")
    
    # Special handling for Sarvam - ensure voice matches gender
    if competitor_id == "sarvam":
        voice_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice)
        if not voice_info or voice_info.gender != gender_filter:
            print(f"[SARVAM DEBUG] Gender check: voice={competitor_voice}, expected={gender_filter}, got={voice_info.gender if voice_info else 'None'}")
            # Find correct gender voice
            correct_voices = [
                v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items()
                if info.gender == gender_filter and v in TTS_PROVIDERS[competitor_id].supported_voices
            ]
            if correct_voices:
                competitor_voice = random.choice(correct_voices)
                print(f"[SARVAM DEBUG] Fixed gender mismatch, using {competitor_voice}")
            else:
                st.error(f"No {gender_filter} voice available for Sarvam AI")
                st.session_state.blind_test_current_pair = None
                return
    
    # FINAL STRICT GENDER VERIFICATION - Ensure competitor voice gender matches Murf voice gender
    if competitor_id in TTS_PROVIDERS:
        selected_voice_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice)
        
        # Verify gender match
        if selected_voice_info and selected_voice_info.gender != gender_filter:
            print(f"[GENDER DEBUG] ERROR: Gender mismatch! Expected {gender_filter}, got {selected_voice_info.gender}")
            # Force find a voice with correct gender
            competitor_voices = [
                v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items() 
                if info.gender == gender_filter and v in TTS_PROVIDERS[competitor_id].supported_voices
            ]
            if competitor_voices:
                competitor_voice = competitor_voices[0]
                selected_voice_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice)
                print(f"[GENDER DEBUG] Fixed! Using {competitor_voice} ({selected_voice_info.gender if selected_voice_info else 'unknown'})")
            else:
                st.error(f"No {gender_filter} voice available for {TTS_PROVIDERS[competitor_id].name}")
                return
        elif selected_voice_info:
            print(f"[GENDER DEBUG] ✓ Verified: Competitor voice {competitor_voice} is {selected_voice_info.gender} (matches Murf's {gender_filter})")
        
        if not selected_voice_info:
            # Voice not found in voice_info, find a valid one
            competitor_voices = [
                v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items() 
                if info.gender == gender_filter and v in TTS_PROVIDERS[competitor_id].supported_voices
            ]
            if competitor_voices:
                competitor_voice = random.choice(competitor_voices)
            else:
                st.error(f"Voice validation error: Could not find valid {gender_filter} voice for {TTS_PROVIDERS[competitor_id].name}")
                return
        elif selected_voice_info.gender != gender_filter:
            # Gender mismatch - this should never happen, but fix it if it does
            competitor_voices = [
                v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items() 
                if info.gender == gender_filter and v in TTS_PROVIDERS[competitor_id].supported_voices
            ]
            if competitor_voices:
                competitor_voice = random.choice(competitor_voices)
            else:
                st.error(f"Gender mismatch error: Selected voice doesn't match {gender_filter} gender")
                return
    
    # IMPORTANT: Murf voice stays FIXED - use the one from session state, don't change it
    # The murf_voice is already set from the setup page and should never change during comparisons
    
    # FINAL GENDER CHECK LOG - CRITICAL VERIFICATION BEFORE GENERATION
    murf_final_info = TTS_PROVIDERS[murf_provider_id].voice_info.get(murf_voice)
    comp_final_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice) if competitor_id in TTS_PROVIDERS else None
    
    # ABSOLUTE FINAL CHECK - if genders don't match, force fix it
    if murf_final_info and comp_final_info and murf_final_info.gender != comp_final_info.gender:
        print(f"[GENDER FINAL] CRITICAL ERROR: Gender mismatch detected! Murf: {murf_final_info.gender}, Competitor: {comp_final_info.gender}")
        # Force find correct gender voice
        correct_gender_voices = [
            v for v, info in TTS_PROVIDERS[competitor_id].voice_info.items()
            if info.gender == murf_final_info.gender and v in TTS_PROVIDERS[competitor_id].supported_voices
        ]
        if correct_gender_voices:
            competitor_voice = random.choice(correct_gender_voices)
            comp_final_info = TTS_PROVIDERS[competitor_id].voice_info.get(competitor_voice)
            print(f"[GENDER FINAL] FORCED FIX: Changed competitor voice to {competitor_voice} (gender: {comp_final_info.gender if comp_final_info else '?'})")
        else:
            st.error(f"CRITICAL: Cannot find {murf_final_info.gender} voice for {TTS_PROVIDERS[competitor_id].name}. Cannot proceed.")
            st.session_state.blind_test_current_pair = None
            return
    
    print(f"[GENDER FINAL] ✓ Verified: Murf: {murf_voice} ({murf_final_info.gender if murf_final_info else '?'}) vs Competitor: {competitor_voice} ({comp_final_info.gender if comp_final_info else '?'})")
    
    # Additional safety check - this should never trigger if above logic works correctly
    if murf_final_info and comp_final_info and murf_final_info.gender != comp_final_info.gender:
        print(f"[GENDER FINAL] ❌ CRITICAL ERROR: Gender mismatch detected! Aborting.")
        st.error(f"Gender mismatch: Murf ({murf_final_info.gender}) vs Competitor ({comp_final_info.gender})")
        return
    else:
        print(f"[GENDER FINAL] ✓ Gender match confirmed: {murf_final_info.gender if murf_final_info else gender_filter}")
    
    # Show loading placeholder while generating
    loading_placeholder = st.empty()
    loading_placeholder.info(f"Generating audio samples... This may take a few seconds.")
    
    # Generate samples (runs in parallel for speed)
    # IMPORTANT: Log the text being used to ensure it's correct
    print(f"[DEBUG] Generating audio for text: '{text[:50]}...' (Comparison #{st.session_state.blind_test_comparison_count})")
    
    try:
        sample_a, sample_b = asyncio.run(generate_comparison_samples(
            text, murf_provider_id, murf_voice, competitor_id, competitor_voice
        ))
        
        # Validate that samples were generated with the correct text
        if sample_a and hasattr(sample_a, 'metadata') and sample_a.metadata:
            generated_text_a = sample_a.metadata.get('text', '')
            if generated_text_a and generated_text_a != text:
                print(f"[WARNING] Sample A text mismatch! Expected: '{text[:50]}', Got: '{generated_text_a[:50]}'")
        
        if sample_b and hasattr(sample_b, 'metadata') and sample_b.metadata:
            generated_text_b = sample_b.metadata.get('text', '')
            if generated_text_b and generated_text_b != text:
                print(f"[WARNING] Sample B text mismatch! Expected: '{text[:50]}', Got: '{generated_text_b[:50]}'")
                
    except Exception as e:
        loading_placeholder.error(f"Error generating samples: {str(e)}")
        sample_a, sample_b = None, None
    
    # Clear loading message
    loading_placeholder.empty()
    
    # Check if either sample failed
    if sample_a is None or sample_b is None or not (sample_a.success if sample_a else False) or not (sample_b.success if sample_b else False):
        # Show detailed error and allow retry
        error_msg = "Both samples failed to generate."
        error_details = []
        
        if sample_a:
            if not sample_a.success:
                error_details.append(f"Sample A ({TTS_PROVIDERS[murf_provider_id].name}): {sample_a.error_message if hasattr(sample_a, 'error_message') and sample_a.error_message else 'Unknown error'}")
        else:
            error_details.append(f"Sample A ({TTS_PROVIDERS[murf_provider_id].name}): Failed to generate")
            
        if sample_b:
            if not sample_b.success:
                error_details.append(f"Sample B ({TTS_PROVIDERS[competitor_id].name}): {sample_b.error_message if hasattr(sample_b, 'error_message') and sample_b.error_message else 'Unknown error'}")
        else:
            error_details.append(f"Sample B ({TTS_PROVIDERS[competitor_id].name}): Failed to generate")
        
        if error_details:
            error_msg = " | ".join(error_details)
        
        st.session_state.blind_test_current_pair = {"error": True, "message": error_msg}
        st.rerun()
        return
    
    # CRITICAL FIX: Validate text matches before storing
    # Ensure samples were generated with the correct text
    if sample_a and sample_a.success:
        # Store text in metadata for validation
        if not hasattr(sample_a, 'metadata') or sample_a.metadata is None:
            sample_a.metadata = {}
        sample_a.metadata['generated_text'] = text
        sample_a.metadata['comparison_num'] = st.session_state.blind_test_comparison_count
    
    if sample_b and sample_b.success:
        # Store text in metadata for validation
        if not hasattr(sample_b, 'metadata') or sample_b.metadata is None:
            sample_b.metadata = {}
        sample_b.metadata['generated_text'] = text
        sample_b.metadata['comparison_num'] = st.session_state.blind_test_comparison_count
    
    # Randomize order (50/50 chance Murf is A or B)
    murf_is_a = random.random() > 0.5
    
    # Generate a unique timestamp for this comparison to prevent caching
    import time
    unique_timestamp = time.time()
    comparison_id = f"{st.session_state.blind_test_comparison_count}_{unique_timestamp}"
    
    # Log for debugging
    print(f"[DEBUG] Storing pair - Text: '{text[:60]}...', Comparison #{st.session_state.blind_test_comparison_count}")
    
    if murf_is_a:
        st.session_state.blind_test_current_pair = {
            "sample_a": sample_a, "sample_b": sample_b,
            "provider_a": murf_provider_id, "provider_b": competitor_id,
            "voice_a": murf_voice, "voice_b": competitor_voice,
            "text": text, "murf_is": "A", "generated_at": unique_timestamp,
            "comparison_id": comparison_id
        }
    else:
        st.session_state.blind_test_current_pair = {
            "sample_a": sample_b, "sample_b": sample_a,
            "provider_a": competitor_id, "provider_b": murf_provider_id,
            "voice_a": competitor_voice, "voice_b": murf_voice,
            "text": text, "murf_is": "B", "generated_at": unique_timestamp,
            "comparison_id": comparison_id
        }
    
    st.session_state.blind_test_audio_played = {"A": 0, "B": 0}
    st.rerun()


async def generate_comparison_samples(text: str, provider_a: str, voice_a: str, provider_b: str, voice_b: str):
    """Generate audio samples for comparison - runs both in parallel for speed"""
    
    # Validate voices exist in supported voices
    if provider_a in TTS_PROVIDERS and voice_a not in TTS_PROVIDERS[provider_a].supported_voices:
        print(f"Warning: Voice '{voice_a}' not in supported voices for {provider_a}. Available: {TTS_PROVIDERS[provider_a].supported_voices}")
    
    if provider_b in TTS_PROVIDERS and voice_b not in TTS_PROVIDERS[provider_b].supported_voices:
        print(f"Warning: Voice '{voice_b}' not in supported voices for {provider_b}. Available: {TTS_PROVIDERS[provider_b].supported_voices}")
    
    # CRITICAL: Create TestSample with unique ID and ensure text is set correctly
    import time
    unique_sample_id = f"blind_comparison_{int(time.time() * 1000)}"
    
    sample = TestSample(
        id=unique_sample_id,
        text=text,  # CRITICAL: This text MUST be used for generation
        word_count=len(text.split()),
        category="blind_test",
        length_category="custom",
        complexity_score=0.5
    )
    
    # CRITICAL DEBUG: Verify text is correct
    print(f"[CRITICAL DEBUG] TestSample created with text: '{sample.text[:80]}...'")
    assert sample.text == text, f"Text mismatch! Expected '{text[:50]}', got '{sample.text[:50]}'"
    
    async def generate_sample(provider_id: str, voice: str):
        """Generate a single sample"""
        try:
            # CRITICAL DEBUG: Log the text being used for generation
            print(f"[CRITICAL DEBUG] Generating for {provider_id} with text: '{sample.text[:60]}...'")
            
            provider_obj = TTSProviderFactory.create_provider(provider_id)
            result = await st.session_state.benchmark_engine.run_single_test(
                provider_obj, sample, voice
            )
            
            # CRITICAL: Store the text in result metadata immediately
            if result:
                if not hasattr(result, 'metadata') or result.metadata is None:
                    result.metadata = {}
                result.metadata['text'] = sample.text
                result.metadata['generated_text'] = sample.text
                print(f"[CRITICAL DEBUG] Generated result for {provider_id} - text in metadata: '{result.metadata.get('text', '')[:60]}...'")
            
            if not result.success:
                print(f"Sample generation failed for {provider_id} with voice {voice}: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
            return result
        except Exception as e:
            print(f"Error generating sample ({provider_id} with voice {voice}): {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Run both generations in parallel for faster loading
    results = await asyncio.gather(
        generate_sample(provider_a, voice_a),
        generate_sample(provider_b, voice_b),
        return_exceptions=True
    )
    
    result_a = results[0] if not isinstance(results[0], Exception) else None
    result_b = results[1] if not isinstance(results[1], Exception) else None
    
    return result_a, result_b


def handle_vote(choice: str, pair: dict):
    """Handle a user vote from blind test and update ELO ratings
    
    IMPORTANT: ELO ratings should ONLY be updated from blind test votes (user preferences),
    NOT from quick test results (latency, TTFB, etc.). Quick test is for technical metrics only.
    """
    from database import db
    
    # Prevent double voting on same comparison
    current_comparison = st.session_state.blind_test_comparison_count
    if st.session_state.get("last_voted_comparison") == current_comparison:
        return  # Already voted on this comparison
    
    # Mark this comparison as voted
    st.session_state.last_voted_comparison = current_comparison
    
    # CRITICAL FIX: Clear ALL audio-related state to force fresh generation
    st.session_state.blind_test_current_pair = None
    
    # Force the next comparison to generate fresh audio
    st.session_state.force_regenerate = True
    
    print(f"[VOTE DEBUG] Vote recorded. Cleared pair. Next comparison will generate fresh audio.")
    
    # Determine winner and loser based on choice
    # IMPORTANT: choice "A" means sample A won, choice "B" means sample B won
    if choice == "A":
        winner_provider = pair["provider_a"]
        loser_provider = pair["provider_b"]
        winner_voice = pair["voice_a"]
        loser_voice = pair["voice_b"]
    else:  # choice == "B"
        winner_provider = pair["provider_b"]
        loser_provider = pair["provider_a"]
        winner_voice = pair["voice_b"]
        loser_voice = pair["voice_a"]
    
    # Debug: Print winner/loser to verify
    print(f"Vote: {choice} | Winner: {winner_provider} | Loser: {loser_provider}")
    
    # Update ELO ratings - winner should get higher rating, loser should get lower
    try:
        new_winner_rating, new_loser_rating = db.update_elo_ratings(
            winner_provider, loser_provider, k_factor=32
        )
        print(f"ELO Updated - Winner ({winner_provider}): {new_winner_rating:.1f}, Loser ({loser_provider}): {new_loser_rating:.1f}")
        
        # Save vote
        db.save_user_vote(
            winner_provider,
            loser_provider,
            pair["text"][:100],
            session_id=f"blind_battle_{current_comparison}"
        )
    except Exception as e:
        print(f"Error updating ratings: {e}")
    
    # Record result
    result_record = {
        "comparison_num": current_comparison + 1,
        "winner": winner_provider,
        "winner_voice": winner_voice,
        "loser": loser_provider,
        "loser_voice": loser_voice,
        "text": pair["text"],
        "murf_won": (pair["murf_is"] == choice),
        "user_choice": choice
    }
    st.session_state.blind_test_results_history.append(result_record)
    
    # Move to next comparison
    st.session_state.blind_test_comparison_count += 1
    
    # Check if we're done
    if st.session_state.blind_test_comparison_count >= st.session_state.blind_test_max_comparisons:
        st.session_state.show_final_results = True
        st.session_state.blind_test_current_pair = None
    else:
        # Force clear the pair to ensure fresh audio generation
        st.session_state.blind_test_current_pair = None
        # Clear any cached audio state
        if "blind_test_audio_played" in st.session_state:
            st.session_state.blind_test_audio_played = {"A": 0, "B": 0}
    
    st.rerun()


def display_interim_results():
    """Display interim results during the blind test"""
    st.subheader("Current Results")
    
    results = st.session_state.blind_test_results_history
    
    if not results:
        st.info("No comparisons completed yet.")
        return
    
    # Calculate win rates
    provider_wins = {}
    provider_losses = {}
    
    for r in results:
        winner = r["winner"]
        loser = r["loser"]
        
        provider_wins[winner] = provider_wins.get(winner, 0) + 1
        provider_losses[loser] = provider_losses.get(loser, 0) + 1
    
    # Create summary table
    all_providers = set(provider_wins.keys()) | set(provider_losses.keys())
    summary_data = []
    
    for provider in all_providers:
        wins = provider_wins.get(provider, 0)
        losses = provider_losses.get(provider, 0)
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        
        summary_data.append({
            "Provider": TTS_PROVIDERS.get(provider, {}).name if provider in TTS_PROVIDERS else provider.title(),
            "Model": get_model_name(provider),
            "Wins": wins,
            "Losses": losses,
            "Win Rate": f"{win_rate:.1f}%",
            "Samples": total
        })
    
    # Sort by win rate
    summary_data.sort(key=lambda x: float(x["Win Rate"].replace("%", "")), reverse=True)
    
    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Murf specific stats
    murf_wins = sum(1 for r in results if r.get("murf_won", False))
    murf_total = len(results)
    murf_win_rate = (murf_wins / murf_total * 100) if murf_total > 0 else 0
    
    st.metric(
        "Murf Win Rate",
        f"{murf_win_rate:.1f}%",
        delta=f"{murf_wins} wins / {murf_total} comparisons"
    )
    
    if st.button("Continue Testing", type="primary"):
        st.session_state.show_interim_results = False
        st.rerun()


def display_final_results():
    """Display final results after all comparisons"""
    st.markdown("---")
    st.header("Final Results")
    
    results = st.session_state.blind_test_results_history
    
    if not results:
        st.info("No comparisons completed.")
        if st.button("Start New Test"):
            reset_blind_test()
        return
    
    # Calculate comprehensive stats
    provider_wins = {}
    provider_losses = {}
    
    for r in results:
        winner = r["winner"]
        loser = r["loser"]
        
        provider_wins[winner] = provider_wins.get(winner, 0) + 1
        provider_losses[loser] = provider_losses.get(loser, 0) + 1
    
    # Calculate ELO for this test session only (starting from 1000 for all)
    # This ensures ELO reflects performance in this specific test, not cumulative history
    test_session_elo = {}
    for provider in set(provider_wins.keys()) | set(provider_losses.keys()):
        test_session_elo[provider] = 1000.0  # Start all at 1000 for this test
    
    # Replay all comparisons to calculate ELO for this test session
    for r in results:
        winner = r["winner"]
        loser = r["loser"]
        
        winner_rating = test_session_elo[winner]
        loser_rating = test_session_elo[loser]
        
        # Calculate expected scores using EXACT standard ELO formula
        # E_X = 1 / (1 + 10^((R_Y - R_X) / 400))
        import math
        expected_winner = 1 / (1 + math.pow(10, (loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + math.pow(10, (winner_rating - loser_rating) / 400))
        
        # Update ELO using EXACT formula: R'_X = R_X + K(S_X - E_X)
        # Winner: S_X = 1, Loser: S_X = 0
        k_factor = 32
        test_session_elo[winner] = winner_rating + k_factor * (1 - expected_winner)
        test_session_elo[loser] = loser_rating + k_factor * (0 - expected_loser)
    
    # Create leaderboard
    all_providers = set(provider_wins.keys()) | set(provider_losses.keys())
    leaderboard_data = []
    
    for provider in all_providers:
        wins = provider_wins.get(provider, 0)
        losses = provider_losses.get(provider, 0)
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # Use ELO from this test session only (not cumulative)
        session_elo = test_session_elo.get(provider, 1000.0)
        
        # Samples should be from current test only (wins + losses), not cumulative database data
        samples = total
        
        leaderboard_data.append({
            "Rank": 0,
            "Provider": TTS_PROVIDERS.get(provider, {}).name if provider in TTS_PROVIDERS else provider.title(),
            "Model": get_model_name(provider),
            "ELO": round(session_elo, 1),
            "Wins": wins,
            "Losses": losses,
            "Win Rate": f"{win_rate:.1f}%",
            "Samples": samples
        })
    
    # Sort by ELO and assign ranks (ELO now reflects this test session only)
    leaderboard_data.sort(key=lambda x: x["ELO"], reverse=True)
    for i, item in enumerate(leaderboard_data):
        item["Rank"] = i + 1
    
    df = pd.DataFrame(leaderboard_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Comparisons", len(results))
    
    with col2:
        murf_wins = sum(1 for r in results if r.get("murf_won", False))
        st.metric("Murf Wins", murf_wins)
    
    with col3:
        murf_win_rate = (murf_wins / len(results) * 100) if results else 0
        st.metric("Murf Win Rate", f"{murf_win_rate:.1f}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start New Test", type="primary", use_container_width=True):
            reset_blind_test()
    
    with col2:
        if st.button("View Full Leaderboard", use_container_width=True):
            st.session_state.current_page = "Leaderboard"
            st.rerun()


def reset_blind_test():
    """Reset all blind test state"""
    st.session_state.blind_test_setup_complete = False
    st.session_state.blind_test_current_pair = None
    st.session_state.blind_test_comparison_count = 0
    st.session_state.blind_test_results_history = []
    st.session_state.show_interim_results = False
    st.session_state.show_final_results = False
    st.rerun()


def generate_blind_test_samples(text: str, providers: List[str]):
    """Generate audio samples for blind testing (legacy function for backward compatibility)"""
    
    import random
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    async def test_provider(provider_id: str):
        try:
            provider = TTSProviderFactory.create_provider(provider_id)
            
            voices = TTS_PROVIDERS[provider_id].supported_voices
            voice = voices[0] if voices else "default"
            
            sample = TestSample(
                id="blind_test",
                text=text,
                word_count=len(text.split()),
                category="blind_test",
                length_category="custom",
                complexity_score=0.5
            )
            
            result = await st.session_state.benchmark_engine.run_single_test(
                provider, sample, voice
            )
            return result
            
        except Exception as e:
            st.error(f"Error testing provider: {str(e)}")
            return None
    
    # Run tests
    for i, provider_id in enumerate(providers):
        status_text.text(f"Generating sample {i+1}/{len(providers)}...")
        
        result = asyncio.run(test_provider(provider_id))
        
        if result and result.success:
            results.append(result)
        
        progress_bar.progress((i + 1) / len(providers))
    
    status_text.text("Samples generated!")
    
    if len(results) < 2:
        st.error("❌ Not enough successful samples generated. Please try again.")
        st.session_state.blind_test_samples = []
        return
    
    random.shuffle(results)
    
    labels = [chr(65 + i) for i in range(len(results))]
    for i, result in enumerate(results):
        result.blind_label = labels[i]
    
    st.session_state.blind_test_samples = results
    st.session_state.blind_test_voted = False
    st.session_state.blind_test_vote_choice = None
    
    st.success(f"✅ Generated {len(results)} blind test samples!")
    st.rerun()

def display_blind_test_samples():
    """Display blind test samples for voting"""
    
    samples = st.session_state.blind_test_samples
    
    if not st.session_state.blind_test_voted:
        st.subheader("🎧 Listen and Vote")
        st.markdown("**Listen to each sample and vote for the one with the best quality:**")
        
        for i in range(0, len(samples), 4):
            cols = st.columns(4)
            for j, result in enumerate(samples[i:i+4]):
                with cols[j]:
                    st.markdown(f"### Sample {result.blind_label}")
                    
                    if result.audio_data:
                        audio_base64 = base64.b64encode(result.audio_data).decode()
                        audio_html = f"""
                        <audio controls controlsList="nodownload" style="width: 100%;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                        </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.caption(f"Sample {result.blind_label}")
                        
                        st.download_button(
                            label="Download MP3",
                            data=result.audio_data,
                            file_name=f"sample_{result.blind_label}.mp3",
                            mime="audio/mpeg",
                            key=f"download_blind_{result.blind_label}_{i}_{j}"
                        )
        
        st.divider()
        
        st.markdown("### 🗳️ Cast Your Vote")
        
        vote_options = [f"Sample {r.blind_label}" for r in samples]
        selected_sample = st.radio(
            "Which sample sounds best to you?",
            vote_options,
            key="blind_vote_radio"
        )
        
        if st.button("Submit Vote", type="primary"):
            selected_label = selected_sample.split()[1]
            st.session_state.blind_test_vote_choice = selected_label
            st.session_state.blind_test_voted = True
            
            winner_result = next(r for r in samples if r.blind_label == selected_label)
            
            losers = [r for r in samples if r.blind_label != selected_label]
            if losers:
                for loser_result in losers:
                    handle_blind_test_vote(winner_result, loser_result, save_vote=False)
                
                handle_blind_test_vote(winner_result, losers[0], save_vote=True)
            
            st.rerun()
    
    else:
        st.subheader("🎉 Results Revealed!")
        
        voted_sample = next(r for r in samples if r.blind_label == st.session_state.blind_test_vote_choice)
        
        st.success(f"**You voted for Sample {st.session_state.blind_test_vote_choice}**")
        st.info(f"**Sample {st.session_state.blind_test_vote_choice} was generated by: {voted_sample.provider.title()} ({voted_sample.model_name})**")
        
        st.divider()
        
        st.subheader("🔓 All Samples Revealed")
        
        comparison_data = []
        for result in sorted(samples, key=lambda r: r.blind_label):
            is_winner = result.blind_label == st.session_state.blind_test_vote_choice
            comparison_data.append({
                "Sample": result.blind_label,
                "Provider": result.provider.title(),
                "Model": result.model_name,
                "Location": get_location_display(result),
                "TTFB (ms)": f"{result.ttfb:.1f}" if result.ttfb > 0 else "N/A",
                "File Size (KB)": f"{result.file_size_bytes / 1024:.1f}",
                "Your Choice": "🏆 Winner" if is_winner else ""
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.subheader("🎧 Listen Again (with provider names)")
        
        sorted_samples = sorted(samples, key=lambda r: r.blind_label)
        for i in range(0, len(sorted_samples), 4):
            cols = st.columns(4)
            for j, result in enumerate(sorted_samples[i:i+4]):
                with cols[j]:
                    is_winner = result.blind_label == st.session_state.blind_test_vote_choice
                    if is_winner:
                        st.markdown(f"### 🏆 Sample {result.blind_label}")
                    else:
                        st.markdown(f"### Sample {result.blind_label}")
                    
                    st.markdown(f"**{result.provider.title()}**")
                    st.caption(result.model_name)
                    
                    if result.audio_data:
                        audio_base64 = base64.b64encode(result.audio_data).decode()
                        audio_html = f"""
                        <audio controls controlsList="nodownload" style="width: 100%;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                        </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.caption(f"TTFB: {result.ttfb:.1f}ms")
                        st.caption(f"Size: {result.file_size_bytes/1024:.1f} KB")
                        
                        st.download_button(
                            label="Download MP3",
                            data=result.audio_data,
                            file_name=f"{result.provider}_{result.blind_label}.mp3",
                            mime="audio/mpeg",
                            key=f"download_revealed_{result.blind_label}_{i}_{j}"
                        )
        
        st.divider()
        
    col1, col2 = st.columns(2)
        
    with col1:
            if st.button("Start New Blind Test", type="primary", use_container_width=True):
                st.session_state.blind_test_samples = []
                st.session_state.blind_test_voted = False
                st.session_state.blind_test_vote_choice = None
                st.rerun()
        
    with col2:
            if st.button("View Leaderboard", use_container_width=True):
                st.session_state.current_page = "Leaderboard"
                st.rerun()

def handle_blind_test_vote(winner_result: BenchmarkResult, loser_result: BenchmarkResult, save_vote: bool = True):
    """Handle blind test vote and update ELO ratings
    
    IMPORTANT: This is the ONLY way ELO should be updated for the leaderboard.
    Quick test results (latency, TTFB) should NOT affect ELO ratings.
    """
    
    from database import db
    
    try:
        winner_rating_before = db.get_elo_rating(winner_result.provider)
        loser_rating_before = db.get_elo_rating(loser_result.provider)
        
        new_winner_rating, new_loser_rating = db.update_elo_ratings(
            winner_result.provider, loser_result.provider, k_factor=32
        )
        
        if save_vote:
            db.save_user_vote(
                winner_result.provider, 
                loser_result.provider, 
                winner_result.text[:100] + "..." if len(winner_result.text) > 100 else winner_result.text,
                session_id="blind_test_session"
            )
        
    except Exception as e:
        st.error(f"Error updating ratings: {e}")

def leaderboard_page():
    """ELO leaderboard page with persistent data - styled like Artificial Analysis"""
    
    st.header("Leaderboard")
    st.markdown("ELO-based rankings of TTS providers based on blind test comparisons")
    
    leaderboard = st.session_state.benchmark_engine.get_leaderboard()
    
    if not leaderboard:
        st.info("No leaderboard data available. Run blind tests or benchmarks to generate rankings.")
        
        if st.button("Start Blind Test", type="primary", use_container_width=True):
            st.session_state.current_page = "Blind Test"
            st.rerun()
        return
    
    from database import db
    
    # Prepare data for display
    display_data = []
    for item in leaderboard:
        provider = item["provider"]
        provider_config = TTS_PROVIDERS.get(provider)
        provider_name = provider_config.name if provider_config else provider.title()
        model_name = get_model_name(provider)
        
        display_data.append({
            "Rank": f"#{item['rank']}",
            "Provider": provider_name,
            "Model": model_name,
            "ELO": round(item["elo_rating"]),
            "Samples": item["games_played"],
            "Wins": item["wins"],
            "Losses": item["losses"],
            "Win Rate": f"{item['win_rate']:.1f}%"
        })
    
    # Create DataFrame
    df = pd.DataFrame(display_data)
    
    # Add custom CSS for better styling - remove scroll, let page scroll instead
    st.markdown("""
    <style>
    .stDataFrame {
        border-radius: 8px;
        overflow: visible !important;
    }
    .stDataFrame > div {
        overflow: visible !important;
        max-height: none !important;
    }
    .stDataFrame > div > div {
        overflow: visible !important;
        max-height: none !important;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame thead th {
        background-color: #f8f9fa;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.5px;
        padding: 12px 16px;
        border-bottom: 2px solid #dee2e6;
    }
    .stDataFrame tbody td {
        padding: 14px 16px;
        border-bottom: 1px solid #f1f3f5;
    }
    .stDataFrame tbody tr:hover {
        background-color: #f8f9fa;
    }
    /* Remove scrollbar from dataframe container */
    div[data-testid="stDataFrame"] > div {
        overflow: visible !important;
        max-height: none !important;
    }
    div[data-testid="stDataFrame"] > div > div {
        overflow: visible !important;
        max-height: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display table without height limit - use 'content' to show all rows
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height="content",
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Provider": st.column_config.TextColumn("Provider", width="medium"),
            "Model": st.column_config.TextColumn("Model", width="medium"),
            "ELO": st.column_config.NumberColumn("ELO", format="%d", width="small"),
            "Samples": st.column_config.NumberColumn("Samples", format="%d", width="small"),
            "Wins": st.column_config.NumberColumn("Wins", format="%d", width="small"),
            "Losses": st.column_config.NumberColumn("Losses", format="%d", width="small"),
            "Win Rate": st.column_config.TextColumn("Win Rate", width="small")
        }
    )

if __name__ == "__main__":
    main()