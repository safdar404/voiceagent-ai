"""Rainbow Voice Studio — browser-based, turn-by-turn OpenAI voice assistant."""
import io
import json
import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

load_dotenv()
st.set_page_config(page_title="Rainbow Voice Studio", page_icon="🌈", layout="wide")
st.markdown('''<style>
.stApp{background:radial-gradient(ellipse at top left,#242043 0%,#111526 55%,#101827 100%);color:#edf2ff}
.block-container{max-width:1150px;padding-top:2rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:#151b30}
h1,h2,h3{letter-spacing:-.025em} .hero{display:flex;align-items:center;gap:18px;padding:22px;border:1px solid #454468;border-radius:22px;background:linear-gradient(120deg,#272144,#182c40);margin-bottom:18px}
.orb{flex-shrink:0;width:66px;height:66px;border-radius:22px;display:grid;place-items:center;font-size:32px;background:linear-gradient(135deg,#ff526f,#ffb84d,#65d8b1,#51afff,#b074ff);box-shadow:0 8px 30px #b074ff33}
.hero h1{font-size:1.9rem;margin:0}.hero p{margin:4px 0;color:#c2cce5}.eyebrow{font-size:.7rem;letter-spacing:.15em;color:#a6e7e2}
.stButton>button[kind="primary"]{background:linear-gradient(110deg,#9c49d8,#d84683,#db7654);border:0;color:white}
.stButton>button,.stDownloadButton>button{border-radius:12px;border-color:#555475}
[data-testid="stChatMessage"]{border:1px solid #373e59;border-radius:16px;background:#1a2034}
[data-testid="stMetric"]{background:#1a2136;border-radius:14px;padding:12px;border-top:3px solid #a775ee}
</style>''', unsafe_allow_html=True)

PROFILES = {
    "Travel advisor": "Help plan practical trips. Ask for destination, dates, budget and preferences when needed. Do not claim to make bookings or know live fares or visa rules.",
    "GeoAI & GIS tutor": "Explain GIS, remote sensing and GeoAI clearly with practical examples. Ask about software and data when relevant.",
    "Interview coach": "Coach the user for interviews. Ask one relevant question at a time and give constructive feedback.",
    "General assistant": "Help with everyday questions and practical planning.",
}
VOICES = ["coral", "alloy", "ash", "ballad", "echo", "fable", "nova", "onyx", "sage", "shimmer"]
for key, default in {"messages": [], "capture": 0, "elapsed": 0.0}.items():
    st.session_state.setdefault(key, default)

if st.session_state.pop("reset_draft", False):
    st.session_state.draft = ""

def secret_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ""

def explain_error(exc):
    if isinstance(exc, AuthenticationError):
        return "Your API key was rejected. Check the key and its project permissions."
    if isinstance(exc, RateLimitError):
        return "API quota or rate limit reached. Check billing and usage, then retry."
    if isinstance(exc, APIConnectionError):
        return "Could not connect to OpenAI. Check your internet connection and retry."
    if isinstance(exc, APIStatusError):
        return f"OpenAI returned HTTP {exc.status_code}. Check model access, selected settings and audio format."
    return "Processing failed. Check the audio file, model settings and network, then retry."

def speak(client, text, model, voice):
    response = client.audio.speech.create(model=model, voice=voice, input=text[:4000], response_format="mp3")
    return response.content

with st.sidebar:
    st.markdown("### 🎛️ Studio controls")
    entered_key = st.text_input("OpenAI API key", type="password", help="Used only by this server session. Never included in downloads.")
    api_key = entered_key.strip() or os.getenv("OPENAI_API_KEY", "") or secret_key()
    st.caption("Key supplied · access checked on request" if api_key else "Enter your key to enable the assistant")
    profile = st.selectbox("Assistant specialty", list(PROFILES))
    language = st.selectbox("Reply language", ["Match the user", "English", "Urdu", "Portuguese", "Arabic"])
    voice = st.selectbox("Voice", VOICES)
    voice_on = st.toggle("Generate spoken replies", value=True)
    autoplay = st.toggle("Autoplay new reply", value=False)
    length = st.select_slider("Response length", ["Brief", "Balanced", "Detailed"], value="Brief")
    with st.expander("Model & instruction settings"):
        chat_model = st.text_input("Response model", value="gpt-5.4-mini")
        stt_model = st.text_input("Transcription model", value="gpt-4o-mini-transcribe")
        tts_model = st.text_input("Speech model", value="gpt-4o-mini-tts")
        extra = st.text_area("Additional instructions", placeholder="Example: Use simple language and local examples.")
    if st.button("🧹 New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.capture += 1
        st.session_state.elapsed = 0.0
        st.rerun()
    export = [{k: v for k, v in m.items() if k in ("role", "content")} for m in st.session_state.messages]
    st.download_button("↓ Download conversation", json.dumps(export, ensure_ascii=False, indent=2), "conversation.json", "application/json", disabled=not export, use_container_width=True)
    st.caption("Audio and text are sent to OpenAI when you submit. API usage is billed separately. History is kept in this server session until cleared or the session ends.")

st.markdown('''<div class="hero"><div class="orb">🎙️</div><div><div class="eyebrow">LISTEN · THINK · RESPOND</div><h1>Rainbow Voice Studio</h1><p>Your voice. A thoughtful conversation.</p></div></div>''', unsafe_allow_html=True)
a,b,c = st.columns(3)
a.metric("Conversation turns", sum(m["role"] == "assistant" for m in st.session_state.messages))
b.metric("Studio mode", "Voice + text" if voice_on else "Text replies")
c.metric("Last response", f"{st.session_state.elapsed:.1f}s" if st.session_state.elapsed else "Ready")
st.caption("Record → stop → transcribe → review → send. Replies use an AI-generated voice. This is turn-based conversation, with no live interruption or background listening.")

for index, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
            st.download_button("Download voice reply", msg["audio"], f"reply-{index}.mp3", "audio/mpeg", key=f"download-{index}")
        elif msg["role"] == "assistant" and api_key:
            if st.button("🔊 Generate / retry voice", key=f"voice-{index}"):
                try:
                    with st.spinner("Creating voice reply…"):
                        with OpenAI(api_key=api_key, timeout=90, max_retries=1) as client:
                            msg["audio"] = speak(client, msg["content"], tts_model, voice)
                    st.rerun()
                except Exception as exc:
                    st.error(explain_error(exc))

with st.container(border=True):
    record_tab, upload_tab = st.tabs(["🎙️ Record", "📂 Upload audio"])
    with record_tab:
        recording = st.audio_input("Record your message", key=f"mic-{st.session_state.capture}", sample_rate=16000, disabled=not api_key)
    with upload_tab:
        uploaded = st.file_uploader("WAV, MP3, M4A, WEBM, MP4 or OGG · up to 20 MB", type=["wav","mp3","m4a","webm","mp4","ogg"], key=f"upload-{st.session_state.capture}", disabled=not api_key)
        if uploaded:
            st.audio(uploaded)
    source = st.radio("Audio source", ["Recording", "Uploaded file"], horizontal=True)
    selected = recording if source == "Recording" else uploaded
    if st.button("✍️ Transcribe selected audio", disabled=not (api_key and selected), use_container_width=True):
        if selected.size > 20_000_000 or selected.size == 0:
            st.error("Please use a non-empty audio file smaller than 20 MB.")
        else:
            try:
                with st.spinner("Transcribing your audio…"):
                    audio = io.BytesIO(selected.getvalue())
                    audio.name = selected.name
                    with OpenAI(api_key=api_key, timeout=90, max_retries=1) as client:
                        transcript = client.audio.transcriptions.create(model=stt_model, file=audio).text
                    if transcript.strip():
                        st.session_state.draft = transcript.strip()
                    else:
                        st.warning("No speech detected. Please record again.")
            except Exception as exc:
                st.error(explain_error(exc))
    with st.form("send_message", clear_on_submit=False):
        text = st.text_area("Review the transcript or type your message", key="draft", placeholder="Ask about a trip, practice an interview, or explore GIS…", max_chars=12000)
        send = st.form_submit_button("Send to voice agent →", type="primary", disabled=not api_key, use_container_width=True)

if send:
    if not text.strip():
        st.warning("Record and transcribe a message, or type one before sending.")
    elif not chat_model.strip() or not stt_model.strip() or not tts_model.strip():
        st.error("Model names cannot be empty.")
    else:
        start = time.monotonic()
        instructions = ("You are a professional conversational voice assistant. " + PROFILES[profile]
                        + f" Reply language: {language}. Response style: {length}. "
                        + "Keep replies suitable for speech and below 350 words. Do not invent current facts or claim external actions. " + extra)
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-20:]]
        try:
            with st.status("Thinking…", expanded=True) as status:
                st.write("Preparing your conversation context")
                with OpenAI(api_key=api_key, timeout=90, max_retries=1) as client:
                    result = client.responses.create(model=chat_model.strip(), instructions=instructions,
                        input=history + [{"role":"user", "content":text.strip()}], max_output_tokens=1800, store=False)
                    answer = result.output_text.strip()
                    if not answer:
                        raise ValueError("No text returned")
                    if getattr(result, "status", None) == "incomplete":
                        answer += "\n\n[Response reached the output limit. Ask me to continue.]"
                    st.session_state.messages.extend([{"role":"user", "content":text.strip()}, {"role":"assistant", "content":answer}])
                    if voice_on:
                        st.write("Generating your voice reply")
                        try:
                            st.session_state.messages[-1]["audio"] = speak(client, answer, tts_model.strip(), voice)
                        except Exception as exc:
                            st.session_state.voice_error = explain_error(exc)
                status.update(label="Reply ready", state="complete", expanded=False)
            st.session_state.elapsed = time.monotonic() - start
            st.session_state.reset_draft = True
            st.session_state.play_new = autoplay
            st.rerun()
        except Exception as exc:
            st.error(explain_error(exc))

if st.session_state.pop("voice_error", None):
    st.warning("Your text reply was saved, but speech generation failed. Use ‘Generate / retry voice’ above.")
if st.session_state.pop("play_new", False) and st.session_state.messages and st.session_state.messages[-1].get("audio"):
    st.audio(st.session_state.messages[-1]["audio"], format="audio/mp3", autoplay=True)

st.caption("Rainbow Voice Studio · Built for clear conversations · Browser microphone access requires localhost or HTTPS")
