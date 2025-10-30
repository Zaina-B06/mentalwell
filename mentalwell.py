import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import random
from typing import Dict, List, Optional
import google.generativeai as genai

# 🌸 Configure your Gemini API key here
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Placeholder imports for future integrations
# import firebase_admin
# from firebase_admin import firestore
# import sqlite3
# import speech_recognition as sr

# Configure the page
st.set_page_config(
    page_title="Emotional Wellness — Your Mind Matters Too",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        animation: gradientShift 15s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    .emotion-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .emotion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .emotion-card.selected {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #ff6b9d;
    }
    
    .floating {
        animation: floating 3s ease-in-out infinite;
    }
    
    @keyframes floating {
        0% { transform: translate(0, 0px); }
        50% { transform: translate(0, 10px); }
        100% { transform: translate(0, -0px); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .success-message {
        background: linear-gradient(45deg, #FFD6E7, #C2E9FB);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Emotion configurations with colors and messages
EMOTION_CONFIG = {
    "😌 Calm": {
        "color": "linear-gradient(135deg, #E3F2FD, #BBDEFB)",
        "message": "You're feeling calm today — that's wonderful! Let's build on this peaceful energy.",
        "gradient": ["#E3F2FD", "#BBDEFB"]
    },
    "😤 Irritable": {
        "color": "linear-gradient(135deg, #FFEBEE, #FFCDD2)",
        "message": "You're feeling irritable today — it's okay to feel this way. Let's explore what might help.",
        "gradient": ["#FFEBEE", "#FFCDD2"]
    },
    "😴 Exhausted": {
        "color": "linear-gradient(135deg, #F3E5F5, #E1BEE7)",
        "message": "You're feeling exhausted today — your body might need rest. Let's find gentle ways to recharge.",
        "gradient": ["#F3E5F5", "#E1BEE7"]
    },
    "💪 Motivated": {
        "color": "linear-gradient(135deg, #E8F5E8, #C8E6C9)",
        "message": "You're feeling motivated today — that's fantastic energy! Let's channel this productively.",
        "gradient": ["#E8F5E8", "#C8E6C9"]
    },
    "😞 Overwhelmed": {
        "color": "linear-gradient(135deg, #FFF3E0, #FFE0B2)",
        "message": "You're feeling overwhelmed today — take a deep breath. Let's break things down together.",
        "gradient": ["#FFF3E0", "#FFE0B2"]
    },
    "🌸 Hopeful": {
        "color": "linear-gradient(135deg, #FCE4EC, #F8BBD0)",
        "message": "You're feeling hopeful today — beautiful! Let's nurture this positive outlook.",
        "gradient": ["#FCE4EC", "#F8BBD0"]
    }
}

# Placeholder for Gemini API integration
def call_gemini_api(prompt: str, context: Dict = None) -> str:
    """
    Calls Gemini API to generate customized responses:
    - Journal Prompt → one short reflective question
    - Recommendations → 3 brief bullet points
    - Summary → slightly longer text (up to 100 words)
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  # fast, cost-effective

        # 🧠 Smart prompt tuning based on content type
        lower_prompt = prompt.lower()

        if "journal" in lower_prompt or "reflection" in lower_prompt:
            style_instruction = (
                "Give only one short reflective journal prompt (1 sentence). "
                "Make it motivational and related to fitness, mood, or wellness."
            )

        elif "recommendation" in lower_prompt or "tips" in lower_prompt:
            style_instruction = (
                "Provide exactly 9 bullet-point lifestyle recommendations related to PCOS. "
                "Each point under 10 words, simple, positive, and actionable."
            )

        elif "summary" in lower_prompt:
            style_instruction = (
                "Write a concise weekly progress summary (about 9–10 sentences). "
                "Encourage the user, note consistency, and suggest one small improvement."
            )

        else:
            style_instruction = "Respond briefly in under 60 words."

        # 🔗 Combine context and style instructions
        full_prompt = (
            f"Context: {json.dumps(context)}\n\nUser prompt: {prompt}\n\n{style_instruction}"
            if context
            else f"{prompt}\n\n{style_instruction}"
        )

        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        return f"⚠️ Gemini API error: {e}"




# Database placeholder functions
def save_emotion_log(emotion_data: Dict):
    """Save emotion log to database (placeholder)"""
    if 'emotion_logs' not in st.session_state:
        st.session_state.emotion_logs = []
    
    emotion_data['timestamp'] = datetime.now()
    st.session_state.emotion_logs.append(emotion_data)
    return True

def get_emotion_logs():
    """Retrieve emotion logs from database (placeholder)"""
    if 'emotion_logs' not in st.session_state:
        # Generate sample data for demonstration
        sample_emotions = list(EMOTION_CONFIG.keys())
        sample_data = []
        
        for i in range(30):
            sample_data.append({
                'timestamp': datetime.now() - timedelta(days=30-i),
                'emotion': random.choice(sample_emotions),
                'sleep_quality': random.randint(3, 10),
                'water_intake': random.choice(['Low', 'Moderate', 'High']),
                'menstrual_phase': random.choice(['Follicular', 'Ovulatory', 'Luteal', 'Menstrual', 'Irregular']),
                'stress_level': random.randint(1, 10),
                'notes': f"Sample note {i}"
            })
        
        st.session_state.emotion_logs = sample_data
    
    return st.session_state.emotion_logs

def save_journal_entry(entry_data: Dict):
    """Save journal entry to database (placeholder)"""
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    
    entry_data['timestamp'] = datetime.now()
    st.session_state.journal_entries.append(entry_data)
    return True

# Initialize session state
if 'selected_emotion' not in st.session_state:
    st.session_state.selected_emotion = None

if 'show_journal' not in st.session_state:
    st.session_state.show_journal = False

if 'submission_success' not in st.session_state:
    st.session_state.submission_success = False

# Main app
def main():
    # Header Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #ff6b9d; font-size: 3rem; margin-bottom: 0.5rem;'>🌸 Emotional Wellness</h1>
            <h2 style='color: #666; font-weight: 300;'>Your Mind Matters Too</h2>
            <p style='color: #888; max-width: 600px; margin: 0 auto;'>
                A compassionate space to track, reflect, and nurture your emotional wellbeing through your PCOS journey
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Emotion Picker Section
    st.markdown("### How are you feeling today?")
    
    # Create emotion cards
    cols = st.columns(6)
    emotions = list(EMOTION_CONFIG.keys())
    
    for i, emotion in enumerate(emotions):
        with cols[i]:
            is_selected = st.session_state.selected_emotion == emotion
            card_class = "emotion-card selected" if is_selected else "emotion-card"
            
            st.markdown(f"""
            <div class='{card_class}' onclick='selectEmotion("{emotion}")'>
                <div style='text-align: center; font-size: 2.5rem;'>{emotion.split()[0]}</div>
                <div style='text-align: center; font-size: 0.9rem; margin-top: 0.5rem;'>{emotion.split()[1]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Select", key=f"btn_{i}", use_container_width=True):
                st.session_state.selected_emotion = emotion
                st.rerun()
    
    # Display emotion message
    if st.session_state.selected_emotion:
        emotion_data = EMOTION_CONFIG[st.session_state.selected_emotion]
        st.markdown(f"""
        <div class='success-message floating'>
            <p style='margin: 0; font-size: 1.1rem;'>{emotion_data['message']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Update background based on emotion
        st.markdown(f"""
        <style>
            .main {{
                background: {emotion_data['color']};
                animation: gradientShift 15s ease infinite;
                background-size: 200% 200%;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    # Context Input Section
    st.markdown("### 📝 Tell me more about your day")
    
    with st.form("context_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sleep_quality = st.slider("😴 Sleep Quality", 1, 10, 7, 
                                     help="How restful was your sleep last night?")
            water_intake = st.selectbox("💧 Water Intake", 
                                       ["Low", "Moderate", "High"],
                                       help="How hydrated do you feel today?")
        
        with col2:
            menstrual_phase = st.selectbox("🩸 Menstrual Phase",
                                          ["Follicular", "Ovulatory", "Luteal", "Menstrual", "Irregular", "Not sure"],
                                          help="Where are you in your cycle?")
            stress_level = st.slider("😥 Stress Level", 1, 10, 5,
                                   help="How stressed do you feel today?")
        
        notes = st.text_area("📝 Notes / Triggers", 
                           placeholder="Anything specific affecting your mood today? Any wins or challenges?",
                           height=100)
        
        submitted = st.form_submit_button("✨ Save Today's Check-in", use_container_width=True)
        
        if submitted and st.session_state.selected_emotion:
            emotion_data = {
                'emotion': st.session_state.selected_emotion,
                'sleep_quality': sleep_quality,
                'water_intake': water_intake,
                'menstrual_phase': menstrual_phase,
                'stress_level': stress_level,
                'notes': notes
            }
            
            if save_emotion_log(emotion_data):
                st.session_state.submission_success = True
                st.rerun()
        elif submitted:
            st.warning("Please select an emotion first!")
    
    # Success message
    if st.session_state.submission_success:
        st.markdown("""
        <div class='success-message pulse'>
            <h3 style='color: #ff6b9d; margin: 0;'>✓ Check-in Saved!</h3>
            <p style='margin: 0.5rem 0 0 0;'>Thank you for honoring your feelings today.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset after display
        if st.button("Continue"):
            st.session_state.submission_success = False
            st.rerun()
    
    # Journal and AI Features Section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🪶 Reflective Journal")
        if st.button("✨ Open My Journal", use_container_width=True):
            st.session_state.show_journal = True
        
        if st.session_state.show_journal:
            with st.container():
                st.markdown('<div class="glass-effect slide-in" style="padding: 1.5rem;">', unsafe_allow_html=True)
                
                # Generate journal prompt using AI
                context = {
                    'emotion': st.session_state.selected_emotion,
                    'phase': menstrual_phase
                }
                journal_prompt = call_gemini_api("Generate a reflective journal prompt", context)
                
                st.markdown(f"**Journal Prompt:** {journal_prompt}")
                
                journal_response = st.text_area("Your response:", height=150,
                                              placeholder="Take a moment to reflect here...")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Save Entry", use_container_width=True):
                        if journal_response:
                            save_journal_entry({
                                'prompt': journal_prompt,
                                'response': journal_response,
                                'emotion': st.session_state.selected_emotion
                            })
                            st.success("Journal entry saved!")
                
                with col_btn2:
                    if st.button("🤖 Get AI Reflection", use_container_width=True):
                        if journal_response:
                            ai_reflection = call_gemini_api("Generate empathetic reflection", 
                                                          {'response': journal_response})
                            st.markdown(f"**AI Reflection:** {ai_reflection}")
                
                if st.button("Close Journal"):
                    st.session_state.show_journal = False
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💖 Self-Care Recommendations")
        
        # Generate AI recommendations
        if st.session_state.selected_emotion:
            context = {
                'emotion': st.session_state.selected_emotion,
                'sleep': sleep_quality,
                'stress': stress_level,
                'phase': menstrual_phase
            }
            
            recommendations = [
                call_gemini_api("Generate self-care recommendation", context) 
                for _ in range(1)
            ]
            
            for i, rec in enumerate(recommendations):
                with st.container():
                    st.markdown(f"""
                    <div class='glass-effect' style='padding: 1rem; margin: 0.5rem 0;'>
                        <div style='display: flex; align-items: center; gap: 0.5rem;'>
                            <span style='font-size: 1.2rem;'>{"🌿🍵🧘"[i]}</span>
                            <span>{rec}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Analytics Dashboard
    st.markdown("---")
    st.markdown("### 📊 Your Emotional Trends")
    
    emotion_logs = get_emotion_logs()
    if emotion_logs:
        df = pd.DataFrame(emotion_logs)
        
        # Emotion frequency chart
        col1, col2 = st.columns(2)
        
        with col1:
            emotion_counts = df['emotion'].value_counts()
            fig_emotion = px.pie(values=emotion_counts.values, 
                               names=emotion_counts.index,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_emotion.update_layout(title="Emotion Distribution")
            st.plotly_chart(fig_emotion, use_container_width=True)
        
        with col2:
            # Time series of emotions
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            daily_emotions = df.groupby('date').size()
            
            fig_trend = px.line(x=daily_emotions.index, y=daily_emotions.values,
                              labels={'x': 'Date', 'y': 'Check-ins'},
                              title="Daily Check-in Trend")
            fig_trend.update_traces(line=dict(color='#ff6b9d', width=3))
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Correlations section
        st.markdown("#### 🔍 Patterns & Correlations")
        
        # Mock correlation insights (in production, these would be calculated)
        insights = [
            "Your calm days often follow 7+ hours of quality sleep",
            "Irritability tends to increase during high-stress periods",
            "Better hydration correlates with more hopeful moods",
            "Exhaustion peaks during the luteal phase for you"
        ]
        
        for insight in insights[:2]:  # Show top 2 insights
            st.markdown(f"• {insight}")
    
    # Weekly Summary Section
    st.markdown("---")
    st.markdown("### 📋 Your Week at a Glance")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # Generate weekly summary using AI
        weekly_context = {
            'emotions': [log['emotion'] for log in emotion_logs[-7:]] if emotion_logs else [],
            'avg_sleep': np.mean([log['sleep_quality'] for log in emotion_logs[-7:]]) if emotion_logs else 7,
            'avg_stress': np.mean([log['stress_level'] for log in emotion_logs[-7:]]) if emotion_logs else 5
        }
        
        weekly_summary = call_gemini_api("Generate weekly wellness summary", weekly_context)
        
        st.markdown(f"""
        <div class='glass-effect' style='padding: 1.5rem;'>
            <p style='font-size: 1.1rem; line-height: 1.6;'>{weekly_summary}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Regenerate Summary", use_container_width=True):
            st.rerun()
    
    # Community Corner (Sidebar)
    with st.sidebar:
        st.markdown("### 🌷 Shared Reflections")
        st.markdown("*AI-moderated for kindness and support*")
        
        community_posts = [
            {"text": "Felt anxious this week but morning meditation helped center me", "reactions": "💗 12"},
            {"text": "PCOS fatigue is real today. Taking it slow and being kind to myself", "reactions": "🌸 8"},
            {"text": "Found that light yoga before bed improves my sleep quality!", "reactions": "🧘‍♀️ 15"}
        ]
        
        for post in community_posts:
            with st.container():
                st.markdown(f"""
                <div class='glass-effect' style='padding: 1rem; margin: 0.5rem 0;'>
                    <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem;'>{post['text']}</p>
                    <p style='margin: 0; font-size: 0.8rem; color: #666;'>{post['reactions']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎙️ Voice Entry")
        
        if st.button("🎤 Speak Your Thoughts", use_container_width=True):
            st.info("Voice feature placeholder - would integrate speech recognition in production")
            
            # Placeholder for voice functionality
            voice_text = st.text_area("Voice transcription would appear here:",
                                    placeholder="[Voice-to-text transcription]",
                                    height=100)
            
            if st.button("Save Voice Entry"):
                st.success("Voice entry saved!")

# JavaScript for emotion selection
st.markdown("""
<script>
function selectEmotion(emotion) {
    // This would be handled by Streamlit buttons in the actual implementation
    console.log("Selected emotion:", emotion);
}
</script>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
