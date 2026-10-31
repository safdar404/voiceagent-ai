"""Rainbow Voice Studio — browser-based, turn-by-turn OpenAI voice assistant."""
import io
import json
import os
import time
import base64
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

load_dotenv()
st.set_page_config(page_title="Rainbow Voice Studio", page_icon="🌈", layout="wide")
ASSETS = Path(__file__).resolve().parent / "assets"
logo = base64.b64encode((ASSETS / "agent-logo.svg").read_bytes()).decode()
st.markdown('''<style>
:root{color-scheme:light}
.stApp{background:radial-gradient(ellipse at 5% 0%,#f4e7ff 0%,transparent 40%),radial-gradient(ellipse at 95% 10%,#def8fb 0%,transparent 40%),#f7f8fd;color:#202b49}
[data-testid="stHeader"]{background:rgba(247,248,253,.95)}
.block-container{max-width:1140px;padding-top:1.5rem;padding-bottom:1.5rem}
[data-testid="stSidebar"]{background:linear-gradient(165deg,#f0ebff,#eaf5ff 65%,#e3f8f3);border-right:1px solid #d7ddef}
[data-testid="stSidebar"] .block-container{padding-top:1rem}
h1,h2,h3{letter-spacing:-.035em;color:#202b49}
[data-testid="stMarkdownContainer"] p,[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"],label{color:#354467}
[data-testid="stCaptionContainer"]{font-size:.82rem}
.hero{position:relative;overflow:hidden;display:flex;align-items:center;gap:20px;padding:25px 28px;border:1px solid #dedcf6;border-radius:24px;background:linear-gradient(110deg,#fff9f1,#faf2ff 45%,#e7f7ff);box-shadow:0 10px 32px #6050b00d;margin-bottom:14px}
.hero:before{content:"";position:absolute;left:0;top:0;right:0;height:5px;background:linear-gradient(90deg,#f55077,#f5a238,#e8c94d,#39bd96,#318beb,#9255dd)}
.orb{flex-shrink:0;width:72px;height:72px;border-radius:23px;display:grid;place-items:center;font-size:35px;background:linear-gradient(135deg,#ff727c,#ffd16b,#67d9bc,#6caeff,#b28af3);box-shadow:0 8px 22px #8955dd26}
.hero h1{font-size:2rem;line-height:1.2;margin:5px 0 7px;color:#253054}.hero p{margin:0;color:#52617c;font-size:.95rem}.eyebrow{font-size:.68rem;font-weight:800;letter-spacing:.17em;color:#7350b5}
[data-testid="stMetric"]{background:linear-gradient(130deg,#fff,#f4efff);border:1px solid #e0dcf2;border-radius:17px;padding:14px 18px;box-shadow:0 5px 16px #55459608;border-top:3px solid #975de1}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p{color:#58617c!important;font-size:.8rem}
[data-testid="stMetricValue"]{color:#28365c!important;font-size:1.55rem;font-weight:750}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#dfdef1;border-radius:19px}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stFileUploader"] button{
 background:#ece4ff!important;color:#503187!important;border:1px solid #c8b3ed!important;border-radius:12px!important;font-weight:650;box-shadow:0 3px 8px #8d62c010;transition:all .18s}
.stButton>button p,.stDownloadButton>button p,[data-testid="stFormSubmitButton"] button p,[data-testid="stFileUploader"] button p{color:inherit!important}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFileUploader"] button:hover{background:#ded0fc!important;border-color:#9770d4!important;color:#39216a!important}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{background:linear-gradient(105deg,#7040ca,#aa358f,#bd405f)!important;color:#fff!important;border:0!important;box-shadow:0 6px 16px #9b44b12b}
[data-testid="stFormSubmitButton"] button:hover{filter:brightness(1.08)}
button:disabled{background:#e7e8f2!important;color:#6a728b!important;border-color:#cfd3e2!important;opacity:1!important;box-shadow:none!important}
button:focus-visible{outline:3px solid #258fa4!important;outline-offset:3px}
[data-testid="stTabs"] [role="tablist"]{gap:8px;border:0}
[data-testid="stTabs"] [role="tab"]{background:#eae5fa;color:#584477;border-radius:12px;padding:9px 18px;height:auto}
[data-testid="stTabs"] [role="tab"] p{color:inherit!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#7450bd;color:#fff;box-shadow:0 4px 10px #7450bd20}
[data-baseweb="tab-highlight"]{background:transparent}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{background:#f0edfb!important;color:#263759!important;border-color:#d2cbe8!important;border-radius:11px}
input,textarea,[data-baseweb="select"] span{color:#263759!important;caret-color:#7040ca!important}
input::placeholder,textarea::placeholder{color:#6b7790!important}
[data-baseweb="input"] button{background:#e4ddf6!important;color:#514271!important}
[data-baseweb="popover"] ul,[role="listbox"]{background:#f6f2ff!important;color:#263759!important}
[data-testid="stFileUploaderDropzone"]{background:#eff3ff;border:1px dashed #a9a9d6;border-radius:14px}
[data-testid="stAudioInput"]{border:1px solid #d9d0ef;border-radius:14px;background:#efebfa;padding:5px}
[data-testid="stAudioInput"] button{background:#ddd2f8!important;color:#503187!important;border-radius:50%}
[data-testid="stChatMessage"]{border:1px solid #dddff0;border-radius:17px;background:#f0f3ff}
[data-testid="stForm"]{background:#faf9ff;border:1px solid #e0daf0;border-radius:16px;padding:16px}
[data-testid="stExpander"]{background:#edeafa;border-color:#d4cbea;border-radius:13px}
@media(max-width:640px){.hero{padding:20px 16px;gap:12px}.hero h1{font-size:1.45rem}.orb{width:54px;height:54px;font-size:28px}.block-container{padding:1rem}.hero p{font-size:.82rem}}

/* Compact studio layout with deliberate spacing and stronger color rhythm. */
.block-container{max-width:1240px;padding-top:3.2rem;padding-bottom:1rem}
[data-testid="stVerticalBlock"]{gap:.65rem}
[data-testid="stSidebar"]{background:linear-gradient(155deg,#eae3ff 0%,#eaf2ff 52%,#dcf7f0 100%)}
[data-testid="stSidebarUserContent"]{padding:1.1rem 1.2rem}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.55rem}
.hero{padding:19px 23px;margin-bottom:3px;border-radius:22px;background:linear-gradient(105deg,#f4e7ff,#e8efff 55%,#dcf7f1);box-shadow:0 7px 24px #6744b512}
.hero h1{font-size:1.9rem;letter-spacing:-.045em}.hero p{font-size:.88rem}
.agent-logo{width:70px;height:70px;flex-shrink:0;filter:drop-shadow(0 7px 12px #934bb128)}
.hero-copy{flex:1}.hero-badge{background:#ffffffaa;border:1px solid #cbbde9;color:#5c3a91;border-radius:30px;padding:7px 12px;font-size:.72rem;font-weight:700;white-space:nowrap}
.sidebar-brand{display:flex;align-items:center;gap:10px;margin-bottom:8px}.sidebar-brand img{width:37px;height:37px}.sidebar-brand strong{display:block;color:#33264e;font-size:1rem}.sidebar-brand small{color:#645377;font-size:.7rem}
[data-testid="stMetric"]{padding:10px 15px;background:#eee8ff;border-top-color:#8957dc;border-radius:14px}
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{background:#e0f5ee;border-top-color:#209b82}
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{background:#fff0e6;border-top-color:#e98a49}
[data-testid="stMetricValue"]{font-size:1.35rem}
[data-testid="stForm"]{padding:12px;background:#f0edfc;border-radius:15px}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{min-height:2.5rem}
[data-testid="stTabs"] [role="tab"]{padding:7px 15px}
.workspace-label{font-size:.72rem;font-weight:800;letter-spacing:.11em;color:#6d4b9b;margin:4px 0 0}
@media(max-width:640px){.block-container{padding-top:3.5rem}.hero{padding:16px;gap:12px}.hero h1{font-size:1.35rem}.agent-logo{width:53px;height:53px}.hero-badge{display:none}}

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
    st.markdown(f'<div class="sidebar-brand"><img src="data:image/svg+xml;base64,{logo}" alt="AI agent"><div><strong>Voice Agent AI</strong><small>YOUR CONVERSATION STUDIO</small></div></div>', unsafe_allow_html=True)
    entered_key = st.text_input("🔑 OpenAI API key", type="password", help="Used only by this server session. Never included in downloads.")
    api_key = entered_key.strip() or os.getenv("OPENAI_API_KEY", "") or secret_key()
    st.caption("Key supplied · access checked on request" if api_key else "Enter your key to enable the assistant")
    profile = st.selectbox("🧠 Assistant specialty", list(PROFILES))
    language = st.selectbox("🌍 Reply language", ["Match the user", "English", "Urdu", "Portuguese", "Arabic"])
    voice = st.selectbox("🎵 Voice", VOICES)
    voice_on = st.toggle("🔊 Generate spoken replies", value=True)
    autoplay = st.toggle("▶️ Autoplay new reply", value=False)
    length = st.select_slider("📏 Response length", ["Brief", "Balanced", "Detailed"], value="Brief")
    with st.expander("⚙️ Model & instruction settings"):
        chat_model = st.text_input("🧠 Response model", value="gpt-5.4-mini")
        stt_model = st.text_input("👂 Transcription model", value="gpt-4o-mini-transcribe")
        tts_model = st.text_input("🗣️ Speech model", value="gpt-4o-mini-tts")
        extra = st.text_area("📝 Additional instructions", placeholder="Example: Use simple language and local examples.")
    if st.button("🧹 New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.capture += 1
        st.session_state.elapsed = 0.0
        st.session_state.reset_draft = True
        st.rerun()
    export = [{k: v for k, v in m.items() if k in ("role", "content")} for m in st.session_state.messages]
    st.download_button("📥 Download conversation", json.dumps(export, ensure_ascii=False, indent=2), "conversation.json", "application/json", disabled=not export, use_container_width=True)
    st.caption("Audio and text are sent to OpenAI when you submit. API usage is billed separately. History is kept in this server session until cleared or the session ends.")

st.markdown(f'''<div class="hero"><img class="agent-logo" src="data:image/svg+xml;base64,{logo}" alt="Voice AI agent logo"><div class="hero-copy"><div class="eyebrow">YOUR IDEAS. A VOICE THAT CONNECTS.</div><h1>Voice Agent <span style="color:#8b42bd">AI</span></h1><p>Speak, discover and create with your personal AI companion.</p></div><span class="hero-badge">✦ Rainbow Studio</span></div>''', unsafe_allow_html=True)
a,b,c = st.columns(3)
a.metric("💬 Conversation turns", sum(m["role"] == "assistant" for m in st.session_state.messages))
b.metric("🎛️ Studio mode", "Voice + text" if voice_on else "Text replies")
c.metric("⏱️ Last response", f"{st.session_state.elapsed:.1f}s" if st.session_state.elapsed else "Ready")
st.caption("🎙️ Record & stop  ·  ✍️ Review transcript  ·  🚀 Send & listen  |  AI-generated voice · Turn-based conversation")

for index, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
            st.download_button("🎧 Download voice reply", msg["audio"], f"reply-{index}.mp3", "audio/mpeg", key=f"download-{index}")
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
    st.markdown('<div class="workspace-label">🎙️ YOUR VOICE WORKSPACE</div>', unsafe_allow_html=True)
    source = st.radio("Input method", ["🎙️ Record", "📂 Upload audio", "⌨️ Type a message"], horizontal=True, label_visibility="collapsed")
    selected = None
    if source == "🎙️ Record":
        selected = st.audio_input("🎙️ Record your message", key=f"mic-{st.session_state.capture}", sample_rate=16000, disabled=not api_key)
    elif source == "📂 Upload audio":
        selected = st.file_uploader("WAV, MP3, M4A, WEBM, MP4 or OGG · up to 20 MB", type=["wav","mp3","m4a","webm","mp4","ogg"], key=f"upload-{st.session_state.capture}", disabled=not api_key)
        if selected:
            st.audio(selected)
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
        text = st.text_area("📝 Review the transcript or type your message", key="draft", placeholder="Ask about a trip, practice an interview, or explore GIS…", max_chars=12000, height=100)
        send = st.form_submit_button("🚀 Send to voice agent", type="primary", disabled=not api_key, use_container_width=True)

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

st.caption("✦ Voice Agent AI · AI-generated voice · Microphone works on localhost or HTTPS")

