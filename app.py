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
    <div class="feature-banner">
        <span class="new-badge">LIVE NOW</span>
        <p class="feature-text">
            <strong>Streaming Race</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.title("TTS Benchmarking Tool")
    st.markdown("Compare Text-to-Speech providers with comprehensive metrics and analysis")
    
    with st.sidebar:
        default_page = "Quick Test"
        
        st.subheader("Navigator")
        
        pages = ["Leaderboard", "Quick Test", "Blind Test", "Streaming Race", "Batch Benchmark", "Results Analysis", "ROI Calculator"]
        
        for i, page_name in enumerate(pages):
            if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        if "navigate_to" in st.session_state and st.session_state.navigate_to:
            page = st.session_state.navigate_to
            st.session_state.navigate_to = None
        else:
            page = st.session_state.get("current_page", "Leaderboard")
        
        st.divider()
        
        st.subheader("Configuration")
        
        config_status = check_configuration()
        
        if config_status["valid"]:
            for provider_id, status in config_status["providers"].items():
                provider_name = TTS_PROVIDERS[provider_id].name
                if status["configured"]:
                    st.write(f"🟢 {provider_name}")
                else:
                    st.write(f"🔴 {provider_name}")
        else:
            st.error("❌ No API keys configured")
            st.markdown("**Set at least one API key:**")
            for provider_id, status in config_status["providers"].items():
                if not status["configured"]:
                    env_var = TTS_PROVIDERS[provider_id].api_key_env
                    provider_name = TTS_PROVIDERS[provider_id].name
                    st.code(f"export {env_var}=your_api_key_here")
                    st.caption(f"For {provider_name}")
    
    if page == "Quick Test":
        quick_test_page()
    elif page == "Blind Test":
        blind_test_page()
    elif page == "Streaming Race":
        streaming_race_page()
    elif page == "Batch Benchmark":
        batch_benchmark_page()
    elif page == "Results Analysis":
        results_analysis_page()
    elif page == "Leaderboard":
        leaderboard_page()
    elif page == "ROI Calculator":
        roi_calculator_page() 

def quick_test_page():
    """Quick test page for single TTS comparisons"""
    
    st.header("🔥 Quick Test")
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
    
    selected_providers = st.multiselect(
        "Select providers:",
        configured_providers,
        default=configured_providers,
        help=f"Available providers: {', '.join([TTS_PROVIDERS[p].name for p in configured_providers])}"
    )
        
    voice_options = {}
    if selected_providers:
        st.markdown("**Voice Selection:**")
        
        for i in range(0, len(selected_providers), 4):
            cols = st.columns(4)
            for j, provider in enumerate(selected_providers[i:i+4]):
                with cols[j]:
                    voices = TTS_PROVIDERS[provider].supported_voices
                    voice_options[provider] = st.selectbox(
                        f"{provider.title()} voice:",
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
    
    st.subheader("📊 Test Results")
    
    data = []
    for result in results:
        data.append({
            "Provider": result.provider.title(),
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
                x=[r.provider.title() for r in successful_results],
                y=[r.ttfb for r in successful_results],
                title="TTFB Comparison",
                labels={"x": "Provider", "y": "TTFB (ms)"}
            )
            st.plotly_chart(fig_ttfb, use_container_width=True)
        
        with col2:
            fig_size = px.bar(
                x=[r.provider.title() for r in successful_results],
                y=[r.file_size_bytes / 1024 for r in successful_results],
                title="File Size Comparison",
                labels={"x": "Provider", "y": "File Size (KB)"}
            )
            st.plotly_chart(fig_size, use_container_width=True)
    
    st.subheader("🎧 Audio Playback")
    
    if len(successful_results) >= 1:
        st.markdown("**Listen to the audio samples:**")
        
        for i in range(0, len(successful_results), 4):
            cols = st.columns(4)
            for j, result in enumerate(successful_results[i:i+4]):
                with cols[j]:
                    st.markdown(f"**{result.provider.title()}**")
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
    """Blind test page for unbiased audio quality comparison"""
    
    st.header("🎯 Blind Test")
    st.markdown("Compare TTS audio quality without knowing which provider generated each sample")
    
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
    
    if "blind_test_samples" not in st.session_state:
        st.session_state.blind_test_samples = []
    
    if "blind_test_results" not in st.session_state:
        st.session_state.blind_test_results = []
    
    if "blind_test_voted" not in st.session_state:
        st.session_state.blind_test_voted = False
    
    if "blind_test_vote_choice" not in st.session_state:
        st.session_state.blind_test_vote_choice = None
    
    st.subheader("⚙️ Test Setup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text_input = st.text_area(
            "Enter text to test:",
            value="The quick brown fox jumps over the lazy dog. This is a test of speech synthesis quality.",
            height=100,
            max_chars=500
        )
        
        word_count = len(text_input.split())
    
    with col2:
        st.markdown("""
        **How Blind Testing Works:**
        1. Enter text to synthesize
        2. Audio generated from all providers
        3. Samples randomized (labeled A, B, etc.)
        4. Listen and vote for your favorite
        5. Results revealed after voting
        """)
    
    if st.button("Generate Blind Test", type="primary"):
        if text_input and len(configured_providers) >= 2:
            valid, error_msg = session_manager.validate_request(text_input)
            if valid:
                generate_blind_test_samples(text_input, configured_providers)
            else:
                st.error(f"❌ {error_msg}")
        else:
            st.error("Please enter text. At least 2 providers must be configured.")
    
    if st.session_state.blind_test_samples:
        display_blind_test_samples()

def generate_blind_test_samples(text: str, providers: List[str]):
    """Generate audio samples for blind testing"""
    
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
    """Handle blind test vote and update ELO ratings"""
    
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

def streaming_race_page():
    """Streaming race page - visualize real-time TTS generation"""
    
    st.header("⚡ Streaming Race")
    st.markdown("Watch TTS providers race in real-time! See Time to First Byte (TTFB) for each provider.")
    
    config_status = check_configuration()
    
    if not st.session_state.config_valid:
        st.warning("Please configure at least one API key in the sidebar first.")
        return
    
    configured_providers = [
        provider_id for provider_id, status in config_status["providers"].items() 
        if status["configured"]
    ]
    
    if len(configured_providers) < 2:
        st.warning("⚠️ Streaming race requires at least 2 configured providers.")
        return
    
    if "race_running" not in st.session_state:
        st.session_state.race_running = False
    
    if "race_results" not in st.session_state:
        st.session_state.race_results = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text_input = st.text_area(
            "Enter text to synthesize:",
            value="The quick brown fox jumps over the lazy dog. This is a test of real-time speech synthesis speed.",
            height=100,
            max_chars=500
        )
        
        word_count = len(text_input.split())
        st.caption(f"Word count: {word_count}")
    
    with col2:
        st.markdown("""
        **How Streaming Race Works:**
        1. Enter text to synthesize
        2. Select providers to race
        3. Click START RACE
        4. Watch live progress bars
        5. See TTFB and Latencies
        """)
    
    default_race_providers = []
    if "murf_falcon_oct23" in configured_providers:
        default_race_providers.append("murf_falcon_oct23")
    if "deepgram_aura2" in configured_providers:
        default_race_providers.append("deepgram_aura2")
    if len(default_race_providers) < 2:
        default_race_providers = configured_providers[:min(2, len(configured_providers))]
    
    selected_providers = st.multiselect(
        "Select providers to race (minimum 2):",
        configured_providers,
        default=default_race_providers,
        help="Select 2-6 providers for the race"
    )
    
    if st.button("START RACE", type="primary", disabled=len(selected_providers) < 2):
        if text_input and len(selected_providers) >= 2:
            valid, error_msg = session_manager.validate_request(text_input)
            if valid:
                st.session_state.race_running = True
                run_streaming_race(text_input, selected_providers)
            else:
                st.error(f"❌ {error_msg}")
        else:
            st.warning("Please enter text and select at least 2 providers.")
    
    if st.session_state.race_results is not None:
        display_race_results(st.session_state.race_results)

def run_streaming_race(text: str, providers: List[str]):
    """Run the streaming race with real-time tracking"""
    
    st.markdown("---")
    st.subheader("🏁 Race in Progress...")
    
    race_placeholders = {}
    status_placeholders = {}
    
    for provider_id in providers:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{provider_id.replace('_', ' ').title()}**")
            race_placeholders[provider_id] = st.progress(0)
        with col2:
            status_placeholders[provider_id] = st.empty()
    
    race_results = {}
    
    async def race_provider(provider_id: str):
        """Race a single provider with streaming tracking"""
        try:
            provider = TTSProviderFactory.create_provider(provider_id)
            
            voices = TTS_PROVIDERS[provider_id].supported_voices
            voice = voices[0] if voices else "default"
            
            sample = TestSample(
                id="streaming_race",
                text=text,
                word_count=len(text.split()),
                category="race",
                length_category="custom",
                complexity_score=0.5
            )
            
            status_placeholders[provider_id].text(f"Starting...")
            
            benchmark_result = await st.session_state.benchmark_engine.run_single_test(
                provider, sample, voice, iteration=1
            )
            
            if benchmark_result.success:
                progress_steps = 20
                for step in range(progress_steps + 1):
                    progress = step / progress_steps
                    race_placeholders[provider_id].progress(progress)
                    
                    elapsed = (step / progress_steps) * benchmark_result.latency_ms
                    bytes_so_far = int((step / progress_steps) * benchmark_result.file_size_bytes)
                    
                    if step == 0:
                        status_placeholders[provider_id].text(f"⚡ TTFB: {benchmark_result.ttfb:.0f}ms")
                    elif step < progress_steps:
                        status_placeholders[provider_id].text(f"{bytes_so_far / 1024:.1f}KB")
                    else:
                        status_placeholders[provider_id].text(f"✅ Done: {benchmark_result.ttfb:.0f}ms")
                    
                    await asyncio.sleep(benchmark_result.latency_ms / progress_steps / 1000)
                
                race_results[provider_id] = {
                    'success': True,
                    'ttfb': benchmark_result.ttfb,
                    'total_time': benchmark_result.latency_ms,
                    'file_size': benchmark_result.file_size_bytes,
                    'audio_data': benchmark_result.audio_data,
                    'voice': voice,
                    'ping': benchmark_result.latency_1,
                    'text': text
                }
            else:
                race_placeholders[provider_id].progress(0)
                status_placeholders[provider_id].text(f"❌ Failed")
                race_results[provider_id] = {
                    'success': False,
                    'error': benchmark_result.error_message
                }
            
        except Exception as e:
            race_placeholders[provider_id].progress(0)
            status_placeholders[provider_id].text(f"❌ Error")
            race_results[provider_id] = {
                'success': False,
                'error': str(e)
            }
    
    async def race_all():
        tasks = [race_provider(provider_id) for provider_id in providers]
        await asyncio.gather(*tasks)
    
    asyncio.run(race_all())
    
    st.session_state.race_results = race_results
    st.session_state.race_running = False
    
    successful_races = {k: v for k, v in race_results.items() if v.get('success')}
    if len(successful_races) >= 2:
        sorted_by_ttfb = sorted(successful_races.items(), key=lambda x: x[1]['ttfb'])
        
        winner_provider = sorted_by_ttfb[0][0]
        for loser_provider, _ in sorted_by_ttfb[1:]:
            try:
                db.update_elo_ratings(winner_provider, loser_provider, k_factor=32)
            except:
                pass
    
    import time as time_module
    time_module.sleep(0.5)
    
    st.rerun()

def display_race_results(race_results: Dict[str, Any]):
    """Display race results with winner and detailed metrics"""
    
    st.markdown("---")
    st.subheader("🏆 Race Results")
    
    successful_results = {k: v for k, v in race_results.items() if v.get('success')}
    
    if not successful_results:
        st.error("❌ No providers completed successfully.")
        return
    
    winner = min(successful_results.items(), key=lambda x: x[1]['ttfb'])
    winner_provider = winner[0]
    winner_data = winner[1]
    
    st.success(f"**WINNER: {winner_provider.replace('_', ' ').title()}** - TTFB: {winner_data['ttfb']:.0f}ms")
    
    st.markdown("### 📊 Detailed Results")
    
    results_data = []
    for provider, data in sorted(successful_results.items(), key=lambda x: x[1]['ttfb']):
        text_length = len(data.get('text', ''))
        speed = (text_length / (data['total_time'] / 1000)) if data['total_time'] > 0 else 0
        
        results_data.append({
            "Rank": len(results_data) + 1,
            "Provider": provider.replace('_', ' ').title(),
            "Model": get_model_name(provider),
            "TTFB (ms)": f"{data['ttfb']:.1f}",
            "Speed (char/s)": f"{speed:.1f}",
            "File Size (KB)": f"{data['file_size'] / 1024:.1f}"
        })
    
    df = pd.DataFrame(results_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ttfb = px.bar(
            x=[r['Provider'] for r in results_data],
            y=[float(r['TTFB (ms)']) for r in results_data],
            title="Time to First Byte (TTFB)",
            labels={"x": "Provider", "y": "TTFB (ms)"},
            color=[float(r['TTFB (ms)']) for r in results_data],
            color_continuous_scale="RdYlGn_r"
        )
        fig_ttfb.update_layout(showlegend=False)
        st.plotly_chart(fig_ttfb, use_container_width=True)
    
    with col2:
        fig_size = px.bar(
            x=[r['Provider'] for r in results_data],
            y=[float(r['File Size (KB)']) for r in results_data],
            title="File Size Comparison",
            labels={"x": "Provider", "y": "File Size (KB)"},
            color=[float(r['File Size (KB)']) for r in results_data],
            color_continuous_scale="Blues"
        )
        fig_size.update_layout(showlegend=False)
        st.plotly_chart(fig_size, use_container_width=True)
    
    st.subheader("🎧 Audio Samples")
    
    audio_cols = st.columns(min(4, len(successful_results)))
    for idx, (provider, data) in enumerate(sorted(successful_results.items(), key=lambda x: x[1]['ttfb'])):
        with audio_cols[idx % 4]:
            if provider == winner_provider:
                st.markdown(f"**🥇 {provider.replace('_', ' ').title()}**")
            elif idx == 1:
                st.markdown(f"**🥈 {provider.replace('_', ' ').title()}**")
            elif idx == 2:
                st.markdown(f"**🥉 {provider.replace('_', ' ').title()}**")
            else:
                st.markdown(f"{provider.replace('_', ' ').title()}")
            st.caption(f"TTFB: {data['ttfb']:.0f}ms")
            
            if data.get('audio_data'):
                audio_base64 = base64.b64encode(data['audio_data']).decode()
                audio_html = f"""
                <audio controls controlsList="nodownload" style="width: 100%;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                
                st.download_button(
                    label="Download MP3",
                    data=data['audio_data'],
                    file_name=f"{provider}_race.mp3",
                    mime="audio/mpeg",
                    key=f"download_race_{provider}"
                )
    
    st.markdown("---")
    if st.button("Race Again", type="primary", use_container_width=True):
        st.session_state.race_results = None
        st.rerun()

def batch_benchmark_page():
    """Batch benchmark page for comprehensive testing"""
    
    st.header("⚙️ Batch Benchmark")
    st.markdown("Run comprehensive benchmarks across multiple samples and providers")
    
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Test Configuration")
        
        selected_providers = st.multiselect(
            "Select providers:",
            configured_providers,
            default=configured_providers,
            help=f"Available providers: {', '.join([TTS_PROVIDERS[p].name for p in configured_providers])}"
        )
        
        sample_count = st.slider("Number of samples:", 5, 50, 20)
        
        categories = ["news", "literature", "conversation", "technical", "narrative"]
        selected_categories = st.multiselect(
            "Categories:",
            categories,
            default=categories
        )
        
        length_categories = ["short", "medium", "long", "very_long"]
        selected_lengths = st.multiselect(
            "Length categories:",
            length_categories,
            default=length_categories
        )
        
        iterations = st.slider("Iterations per test:", 1, 5, 3)
    
    with col2:
        st.subheader("Voice Configuration")
        
        voice_config = {}
        for provider in selected_providers:
            voices = TTS_PROVIDERS[provider].supported_voices
            voice_config[provider] = st.multiselect(
                f"{provider.title()} voices:",
                voices,
                default=[voices[0]] if voices else [],
                key=f"batch_voices_{provider}"
            )
    
    if st.button("Run Benchmark", type="primary"):
        if selected_providers:
            prepare_test_dataset(sample_count, selected_categories, selected_lengths)
            run_batch_benchmark(selected_providers, voice_config, iterations)
        else:
            st.error("Please select at least one provider first.")

def prepare_test_dataset(sample_count: int, categories: List[str], lengths: List[str]):
    """Prepare test dataset for batch benchmarking"""
    
    with st.spinner("Preparing test dataset..."):
        final_samples = []
        
        all_samples = st.session_state.dataset_generator.generate_dataset(sample_count * 4)
            
        matching_samples = []
        for sample in all_samples:
            if (sample.category in categories and 
                sample.length_category in lengths):
                matching_samples.append(sample)
        
        attempts = 0
        while len(matching_samples) < sample_count and attempts < 3:
            additional_samples = st.session_state.dataset_generator.generate_dataset(sample_count * 2)
            for sample in additional_samples:
                if (sample.category in categories and 
                    sample.length_category in lengths and 
                    len(matching_samples) < sample_count * 2):
                    matching_samples.append(sample)
            attempts += 1
        
        final_samples = matching_samples[:sample_count]
        
        st.session_state.test_samples = final_samples
    
    if final_samples:
        st.success(f"Prepared {len(final_samples)} test samples")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Samples", len(final_samples))
        
        with col2:
            avg_words = sum(s.word_count for s in final_samples) / len(final_samples)
            st.metric("Avg Words", f"{avg_words:.1f}")
        
        with col3:
            avg_complexity = sum(s.complexity_score for s in final_samples) / len(final_samples)
            st.metric("Avg Complexity", f"{avg_complexity:.2f}")
        
    
    else:
        st.warning("No samples match the selected criteria. Try adjusting your filters.")

def run_batch_benchmark(providers: List[str], voice_config: Dict[str, List[str]], iterations: int):
    """Run batch benchmark"""
    
    samples = st.session_state.get("test_samples", [])
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_callback(completed: int, total: int):
        progress = completed / total
        progress_bar.progress(progress)
        status_text.text(f"Progress: {completed}/{total} tests completed ({progress*100:.1f}%)")
    
    with st.spinner("Running benchmark..."):
        results = asyncio.run(
            st.session_state.benchmark_engine.run_benchmark_suite(
                providers=providers,
                samples=samples,
                voices_per_provider=voice_config,
                iterations=iterations,
                progress_callback=progress_callback
            )
        )
    
    st.session_state.results.extend(results)
    
    st.session_state.benchmark_engine.update_elo_ratings(results)
    
    st.success(f"Benchmark completed! {len(results)} tests run.")
    
    display_benchmark_summary(results)

def display_benchmark_summary(results: List[BenchmarkResult]):
    """Display benchmark summary"""
    
    st.subheader("📊 Benchmark Summary")
    
    summaries = st.session_state.benchmark_engine.calculate_summary_stats(results)
    
    current_location = geo_service.get_location_string()
    
    ttfb_by_provider = {}
    for result in results:
        if result.success and result.ttfb > 0:
            if result.provider not in ttfb_by_provider:
                ttfb_by_provider[result.provider] = []
            ttfb_by_provider[result.provider].append(result.ttfb)
    
    summary_data = []
    for provider, summary in summaries.items():
        avg_ttfb = sum(ttfb_by_provider.get(provider, [0])) / len(ttfb_by_provider.get(provider, [1])) if provider in ttfb_by_provider else 0
        summary_data.append({
            "Provider": provider.title(),
            "Model": get_model_name(provider),
            "Location": f"{geo_service.get_country_flag()} {current_location}",
            "Success Rate": f"{summary.success_rate:.1f}%",
            "Avg TTFB": f"{avg_ttfb:.1f}ms",
            "P95 TTFB": f"{summary.p95_latency_ms:.1f}ms",
            "Avg File Size": f"{summary.avg_file_size_bytes/1024:.1f}KB",
            "Total Errors": summary.total_errors
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True)

def results_analysis_page():
    """Results analysis page"""
    
    st.header("📈 Results Analysis")
    st.markdown("Analyze benchmark results with detailed metrics and comparisons")
    
    db_results = db.get_recent_results(limit=1000)
    
    if db_results.empty:
        st.info("No benchmark results available. Run a benchmark first.")
        return
    
    results = []
    for _, row in db_results.iterrows():
        result = BenchmarkResult(
            test_id=row.get('test_id', ''),
            provider=row.get('provider', ''),
            sample_id=row.get('sample_id', ''),
            text=row.get('text', ''),
            voice=row.get('voice', ''),
            success=bool(row.get('success', False)),
            latency_ms=float(row.get('latency_ms', 0)),
            file_size_bytes=int(row.get('file_size_bytes', 0)),
            error_message=row.get('error_message'),
            timestamp=row.get('timestamp', ''),
            metadata=json.loads(row.get('metadata', '{}')) if row.get('metadata') else {},
            iteration=0,
            location_country=row.get('location_country', ''),
            location_city=row.get('location_city', ''),
            location_region=row.get('location_region', ''),
            ttfb=float(row.get('ttfb', 0))
        )
        results.append(result)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        providers = list(set(r.provider for r in results))
        selected_providers = st.multiselect("Filter by provider:", providers, default=providers)
    
    with col2:
        categories = list(set(r.metadata.get("category", "unknown") for r in results))
        selected_categories = st.multiselect("Filter by category:", categories, default=categories)
    
    with col3:
        success_filter = st.selectbox("Success filter:", ["All", "Successful only", "Failed only"])
    
    filtered_results = results
    
    if selected_providers:
        filtered_results = [r for r in filtered_results if r.provider in selected_providers]
    
    if selected_categories:
        filtered_results = [r for r in filtered_results if r.metadata.get("category") in selected_categories]
    
    if success_filter == "Successful only":
        filtered_results = [r for r in filtered_results if r.success]
    elif success_filter == "Failed only":
        filtered_results = [r for r in filtered_results if not r.success]
    
    if not filtered_results:
        st.warning("No results match the selected filters.")
        return
    
    display_analysis_charts(filtered_results)

def display_analysis_charts(results: List[BenchmarkResult]):
    """Display analysis charts"""
    
    successful_results = [r for r in results if r.success]
    
    if not successful_results:
        st.warning("No successful results to analyze.")
        return
    
    st.subheader("⏰ TTFB Distribution")
    ttfb_data = []
    for result in successful_results:
        if result.success and result.ttfb > 0:
            ttfb_data.append({
                "provider": result.provider.title(),
                "ttfb": result.ttfb,
                "category": result.metadata.get("category", "unknown")
            })
    
    if ttfb_data:
        import pandas as pd
        df_ttfb = pd.DataFrame(ttfb_data)
        fig_ttfb = px.box(
            df_ttfb,
            x="provider",
            y="ttfb",
            color="provider",
            title="TTFB Distribution by Provider",
            labels={"ttfb": "TTFB (ms)", "provider": "Provider"}
        )
        fig_ttfb.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ttfb, use_container_width=True)
    
    st.subheader("✅ Success Rate Analysis")
    fig_success = visualizations.create_success_rate_chart(results)
    st.plotly_chart(fig_success, use_container_width=True)

def leaderboard_page():
    """ELO leaderboard page with persistent data"""
    
    st.header("🏆 Leaderboard")
    st.markdown("ELO-based rankings of TTS providers")
    
    leaderboard = st.session_state.benchmark_engine.get_leaderboard()
    
    if not leaderboard:
        st.info("No leaderboard data available. Run benchmarks to generate rankings.")
        return
    
    try:
        fig_leaderboard = visualizations.create_leaderboard_chart(leaderboard)
        st.plotly_chart(fig_leaderboard, use_container_width=True)
    except:
        pass
    
    st.subheader("📊 Current Rankings")
    
    from database import db
    try:
        ttfb_stats = db.get_ttfb_stats_by_provider()
    except Exception:
        ttfb_stats = {}
    
    current_location = geo_service.get_location_string()
    location_display = f"{geo_service.get_country_flag()} {current_location}"
    
    df_leaderboard = pd.DataFrame(leaderboard)
    df_leaderboard["Provider"] = df_leaderboard["provider"].str.title()
    
    df_leaderboard["Model"] = df_leaderboard["provider"].apply(get_model_name)
    df_leaderboard["Location"] = location_display
    df_leaderboard["Avg TTFB (ms)"] = df_leaderboard["provider"].apply(
        lambda p: f"{ttfb_stats.get(p, {}).get('avg_ttfb', 0):.1f}"
    )
    df_leaderboard["P95 TTFB (ms)"] = df_leaderboard["provider"].apply(
        lambda p: f"{ttfb_stats.get(p, {}).get('p95_ttfb', 0):.1f}"
    )
    
    display_df = df_leaderboard[[
        "rank", "Provider", "Model", "Location", "elo_rating", "Avg TTFB (ms)", "P95 TTFB (ms)",
        "games_played", "wins", "losses", "win_rate"
    ]].copy()
    
    display_df.columns = [
        "Rank", "Provider", "Model", "Location", "ELO Rating", "Avg TTFB", "P95 TTFB",
        "Games", "Wins", "Losses", "Win Rate %"
    ]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.subheader("📈 Provider Statistics")
    
    from database import db
    provider_stats = db.get_provider_stats()
    
    if provider_stats:
        stats_data = []
        location_display = f"{geo_service.get_country_flag()} {geo_service.get_location_string()}"
        
        for provider, stats in provider_stats.items():
            stats_data.append({
                "Provider": provider.title(),
                "Model": get_model_name(provider),
                "Location": location_display,
                "Total Tests": stats['total_tests'],
                "Success Rate %": f"{stats['success_rate']:.1f}%",
                "Avg File Size (KB)": f"{stats['avg_file_size']/1024:.1f}"
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    st.subheader("🗳️ User Voting Statistics")
    vote_stats = db.get_vote_statistics()
    
    if vote_stats['total_votes'] > 0:
        st.metric("Total User Votes", vote_stats['total_votes'])
        
        if vote_stats['wins']:
            vote_data = []
            location_display = f"{geo_service.get_country_flag()} {geo_service.get_location_string()}"
            
            for provider, wins in vote_stats['wins'].items():
                losses = vote_stats['losses'].get(provider, 0)
                total = wins + losses
                win_rate = (wins / total * 100) if total > 0 else 0
                
                vote_data.append({
                    "Provider": provider.title(),
                    "Model": get_model_name(provider),
                    "Location": location_display,
                    "User Votes Won": wins,
                    "User Win Rate %": f"{win_rate:.1f}%"
                })
            
            vote_df = pd.DataFrame(vote_data)
            st.dataframe(vote_df, use_container_width=True, hide_index=True)
    else:
        st.info("No user votes yet. Vote in Quick Test to start building preference data!")

def roi_calculator_page():
    """ROI Calculator page for TTS provider cost analysis"""
    
    st.header("💰 ROI Calculator")
    st.markdown("Calculate the return on investment for different TTS providers based on your usage patterns.")
    
    roi_calculator_html = '''
    <div id="tts-tool"></div>
    <script src="https://cdn.jsdelivr.net/gh/ShreyashCJ/roi_calculator/3.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const roiNamespace = window["roi-calculator"];
        if (roiNamespace && typeof roiNamespace.default === "function") {
          roiNamespace.default(document.getElementById("tts-tool"), {});
        } else if (typeof roiNamespace === "function") {
          roiNamespace(document.getElementById("tts-tool"), {});
        } else {
          console.error("roi-calculator function not loaded.", roiNamespace);
        }
      });
    </script>
    '''
    
    components.html(roi_calculator_html, height=1400, scrolling=False)
    
    st.markdown("---")
    st.markdown("### 💡 Tips for Using the ROI Calculator")
    
    st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Technology Selection**
        - Choose between Highest Quality, Balanced, or Cost Effective tabs
        - Compare different LLM, TTS, and STT providers
        - See real-time cost updates as you change selections
        """)
    
    with col2:
        st.markdown("""
        **Cost Breakdown**
        - Switch between per minute, per 1k characters, or custom pricing
        - View detailed cost breakdowns for each component
        - Optimize your configuration for best ROI
        """)
    
    with col3:
        st.markdown("""
        **Parameters**
        - Adjust LLM input size and call duration
        - Set AI agent talk time percentage
        - Fine-tune your usage patterns for accurate calculations
        """)
    
    st.markdown('<div style="margin-bottom: 3rem;"></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()