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
st.markdown('\n<style>\n@import url(\'https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap\');\n:root{--space:#090818;--glass:#15132D;--glass2:#1C1940;--line:#2C2860;--text:#F2F0FF;--muted:#A9A5D6;\n--red:#FF5E7E;--orange:#FF9F43;--yellow:#FFD93D;--green:#3DDC97;--sky:#2EC5FF;--violet:#8B6CFF;--pink:#FF5FD2;\n--rainbow:linear-gradient(90deg,#FF5E7E,#FF9F43,#FFD93D,#3DDC97,#2EC5FF,#8B6CFF,#FF5FD2);}\nhtml,body,[class*="css"],.stMarkdown,.stTextInput,.stTextArea,.stSelectbox,button{font-family:\'DM Sans\',system-ui,sans-serif;}\nh1,h2,h3,h4{font-family:\'Sora\',\'DM Sans\',sans-serif!important;letter-spacing:-.015em;}\n.stApp{color:var(--text);background:\n  radial-gradient(900px 420px at 92% -8%,rgba(255,95,210,.16),transparent 60%),\n  radial-gradient(800px 420px at -8% 10%,rgba(46,197,255,.14),transparent 60%),\n  radial-gradient(700px 420px at 50% 115%,rgba(255,217,61,.08),transparent 60%),var(--space)!important;background-attachment:fixed!important}\n.stApp::before{content:"";position:fixed;inset:0 0 auto 0;height:3px;background:var(--rainbow);background-size:200% 100%;\n  animation:mm-flow 8s linear infinite;z-index:999991}\n[data-testid="stHeader"]{background:rgba(9,8,24,.6)!important;backdrop-filter:blur(10px)}\nsection[data-testid="stSidebar"]{background:linear-gradient(180deg,#100E26,#090818)!important;border-right:1px solid var(--line)}\nsection[data-testid="stSidebar"] .block-container,section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:.4rem}\n.block-container{padding-top:1.2rem;padding-bottom:1.5rem;max-width:1280px;}\n.stApp h2{font-size:1.25rem}.stApp h3{font-size:1.05rem;margin-top:.4rem}\n[data-testid="stVerticalBlock"]{gap:.6rem}\n\n/* ---------- hero ---------- */\n.mm-hero{position:relative;display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;padding:16px 20px;border-radius:18px;\n  background:linear-gradient(135deg,rgba(139,108,255,.14),rgba(46,197,255,.06) 50%,rgba(255,95,210,.10));margin-bottom:10px;isolation:isolate}\n.mm-hero::before{content:"";position:absolute;inset:0;border-radius:18px;padding:1.5px;background:var(--rainbow);background-size:200% 100%;\n  animation:mm-flow 10s linear infinite;-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);\n  -webkit-mask-composite:xor;mask-composite:exclude;z-index:-1}\n.mm-hero .agent{width:78px;height:78px;filter:drop-shadow(0 6px 18px rgba(139,108,255,.45));animation:mm-float 5s ease-in-out infinite}\n.mm-hero h1{font-size:2.05rem;line-height:1.05;margin:0 0 .25rem;font-weight:800;padding:0;\n  background:var(--rainbow);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:mm-flow 12s linear infinite}\n.mm-hero p{color:var(--muted);font-size:.93rem;max-width:68ch;margin:0;line-height:1.45}\n.mm-hero .tags{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;}\n.mm-tag{font-size:.72rem;padding:3px 9px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--text);white-space:nowrap}\n.mm-ring{--p:0;width:74px;height:74px;border-radius:50%;display:grid;place-items:center;\n  background:conic-gradient(from 0deg,#FF5E7E,#FF9F43,#FFD93D,#3DDC97,#2EC5FF,#8B6CFF,#FF5FD2 calc(var(--p)*1%),#24204A 0);}\n.mm-ring div{width:58px;height:58px;border-radius:50%;background:var(--space);display:grid;place-items:center;text-align:center;\n  font-family:\'Sora\';font-weight:800;font-size:1rem;line-height:1}\n.mm-ring small{display:block;font-family:\'DM Sans\';font-weight:500;font-size:.58rem;color:var(--muted);margin-top:2px}\n@media (max-width:760px){.mm-hero{grid-template-columns:auto 1fr}.mm-ring{display:none}.mm-hero .agent{width:56px;height:56px}.mm-hero h1{font-size:1.6rem}}\n\n/* ---------- stepper ---------- */\n.mm-steps{display:flex;gap:4px;margin:2px 0 4px;overflow-x:auto;scrollbar-width:none}\n.mm-step{flex:1;min-width:84px;padding:6px 8px;border-radius:10px;background:var(--glass);border:1px solid var(--line);\n  font-size:.74rem;color:var(--muted);white-space:nowrap;text-align:center;font-weight:600}\n.mm-step.done{color:var(--text);border-color:rgba(61,220,151,.45);background:rgba(61,220,151,.08)}\n.mm-step.now{color:#fff;border-color:transparent;background:linear-gradient(var(--glass2),var(--glass2)) padding-box,var(--rainbow) border-box;\n  border:1.5px solid transparent;box-shadow:0 0 18px -6px rgba(139,108,255,.8)}\n.mm-bar{height:4px;border-radius:99px;background:#1E1B40;overflow:hidden;margin-bottom:10px}\n.mm-bar i{display:block;height:100%;background:var(--rainbow);border-radius:99px;transition:width .5s}\n\n/* ---------- stat chips ---------- */\n.mm-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;margin:2px 0 10px}\n.mm-stat{position:relative;background:var(--glass);border:1px solid var(--line);border-radius:12px;padding:8px 12px;overflow:hidden}\n.mm-stat::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c,var(--violet))}\n.mm-stat small{display:block;color:var(--muted);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em}\n.mm-stat b{font-family:\'Sora\';font-size:1.1rem}\n.mm-stat em{font-style:normal;color:var(--muted);font-size:.72rem;margin-left:4px}\n\n/* ---------- cards & badges ---------- */\n.mm-card{background:linear-gradient(160deg,rgba(28,25,64,.9),rgba(21,19,45,.9));border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:8px;}\n.mm-card h4{margin:0 0 6px;font-size:.95rem}\n.mm-kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;}\n.mm-kv div{background:rgba(255,255,255,.03);border-radius:10px;padding:8px 10px;border:1px solid var(--line)}\n.mm-kv small{color:var(--muted);display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.04em}\n.mm-kv span{font-weight:600;font-size:.9rem}\n.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.7rem;font-weight:700;border:1px solid;margin-right:5px;white-space:nowrap}\n.b-fact,.b-ok{color:var(--green);border-color:rgba(61,220,151,.5);background:rgba(61,220,151,.1)}\n.b-inference{color:#B9A6FF;border-color:rgba(139,108,255,.6);background:rgba(139,108,255,.14)}\n.b-recommendation{color:var(--sky);border-color:rgba(46,197,255,.5);background:rgba(46,197,255,.1)}\n.b-uncertainty,.b-medium{color:var(--yellow);border-color:rgba(255,217,61,.5);background:rgba(255,217,61,.08)}\n.b-high{color:var(--red);border-color:rgba(255,94,126,.5);background:rgba(255,94,126,.1)}\n.b-low,.b-open{color:var(--muted);border-color:var(--line);background:rgba(255,255,255,.03)}\n.verdict{padding:9px 14px;border-radius:12px;font-family:\'Sora\';font-weight:700;font-size:.92rem;margin-bottom:8px}\n.v-pass{background:rgba(61,220,151,.1);border:1px solid rgba(61,220,151,.45);color:var(--green)}\n.v-fail{background:rgba(255,94,126,.1);border:1px solid rgba(255,94,126,.5);color:var(--red)}\n.v-warn{background:rgba(255,217,61,.08);border:1px solid rgba(255,217,61,.45);color:var(--yellow)}\n.v-info{background:rgba(46,197,255,.08);border:1px solid rgba(46,197,255,.4);color:var(--sky)}\ntable.mm-matrix{border-collapse:separate;border-spacing:3px;width:100%;font-size:.78rem}\ntable.mm-matrix th{color:var(--muted);font-weight:600;text-align:left;padding:4px 6px}\ntable.mm-matrix td{background:var(--glass2);border-radius:8px;padding:6px 8px;vertical-align:top;border:1px solid var(--line)}\ntd.ne{color:#6E6A99;background:repeating-linear-gradient(45deg,#14122c,#14122c 6px,#1a1838 6px,#1a1838 12px)!important;font-style:italic}\ntd.cf{border-color:rgba(255,217,61,.6)!important}\n.mm-wrap{overflow-x:auto}\n.ev-line{padding:7px 10px;border-left:3px solid var(--c,var(--line));margin:5px 0;background:rgba(255,255,255,.025);border-radius:0 10px 10px 0;font-size:.88rem}\n.mm-muted{color:var(--muted)}\n.mm-id{font-family:\'JetBrains Mono\',monospace;font-size:.78rem;color:var(--sky)}\n.mm-doc{background:var(--glass);border:1px solid var(--line);border-radius:12px;padding:8px 12px;margin-bottom:6px;font-size:.86rem}\n.mm-doc b{font-family:\'Sora\'}\nmark{background:rgba(255,217,61,.28);color:#FFF6CC;border-radius:3px;padding:0 2px}\n.mm-foot{text-align:center;margin-top:1.4rem;font-size:.8rem;color:var(--muted)}\n.mm-foot span{background:var(--rainbow);-webkit-background-clip:text;background-clip:text;color:transparent;font-weight:700}\n\n/* ---------- streamlit widgets ---------- */\ndiv[data-testid="stMetric"]{background:var(--glass);border:1px solid var(--line);border-radius:12px;padding:6px 12px}\ndiv[data-testid="stMetricValue"]{font-size:1.25rem;font-family:\'Sora\'}\n[data-testid="stExpander"] details{background:rgba(21,19,45,.7);border:1px solid var(--line)!important;border-radius:12px!important}\n[data-testid="stExpander"] summary{padding:.45rem .8rem}\n.stTabs [data-baseweb="tab-list"]{gap:3px;flex-wrap:wrap;background:var(--glass);padding:4px;border-radius:12px;border:1px solid var(--line)}\n.stTabs [data-baseweb="tab"]{height:auto;background:transparent;border-radius:9px;padding:5px 11px;font-size:.84rem}\n.stTabs [data-baseweb="tab"] p{font-size:.84rem}\n.stTabs [aria-selected="true"]{background:linear-gradient(110deg,rgba(255,94,126,.35),rgba(139,108,255,.4),rgba(46,197,255,.35))!important}\n.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}\n.stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:600;border:1px solid var(--line);background:var(--glass2);\n  padding:.3rem .8rem;min-height:2.2rem;transition:transform .15s,box-shadow .15s}\n.stButton>button:not(:disabled):hover,.stDownloadButton>button:not(:disabled):hover{border-color:var(--violet);transform:translateY(-1px);box-shadow:0 6px 18px -8px rgba(139,108,255,.8)}\n.stButton>button[kind="primary"]{background:linear-gradient(100deg,#FF5E7E,#FF9F43 30%,#8B6CFF 70%,#2EC5FF);background-size:180% 100%;border:0;color:#fff;\n  text-shadow:0 1px 2px rgba(0,0,0,.35);animation:mm-flow 6s linear infinite}\n.stButton>button[kind="primary"]:disabled{filter:grayscale(.85) brightness(.6);animation:none}\n.stButton>button:focus-visible{outline:2px solid var(--yellow);outline-offset:2px}\n[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{background:#100E26!important;border-color:var(--line)!important;border-radius:10px!important}\n[data-testid="stAlert"]{border-radius:12px;padding:.1rem .2rem}\n[data-testid="stProgress"] [role="progressbar"]>div>div>div{background:var(--rainbow)!important}\n@keyframes mm-flow{0%{background-position:0% 50%}100%{background-position:200% 50%}}\n@keyframes mm-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}\n@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n\n:root{color-scheme:dark}\n.block-container{padding-top:3.1rem;padding-bottom:1rem;max-width:1280px}\n[data-testid="stSidebarUserContent"]{padding:1rem 1.1rem}\n[data-testid="stMarkdownContainer"] p,[data-testid="stWidgetLabel"] p,label{color:#F2F0FF}\n[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:#BBB7DF}\n.hero{position:relative;display:flex;align-items:center;gap:17px;padding:17px 20px;border:1px solid transparent;border-radius:18px;background:linear-gradient(120deg,#251942,#141c38) padding-box,var(--rainbow) border-box;box-shadow:0 10px 26px #00000035;margin-bottom:4px}\n.agent-logo{width:70px;height:70px;flex-shrink:0;filter:drop-shadow(0 5px 14px #8B6CFF70)}\n.hero-copy{flex:1}.hero h1{margin:4px 0;font-size:2rem;font-weight:800;line-height:1.1;background:var(--rainbow);background-clip:text;-webkit-background-clip:text;color:transparent}\n.hero h1 span{color:inherit!important}.hero p{margin:0;color:#BBB7DF;font-size:.9rem}\n.eyebrow{font-size:.65rem;letter-spacing:.15em;color:#2EC5FF;font-weight:700}\n.hero-badge{border:1px solid #775baa;border-radius:24px;padding:6px 10px;color:#FFD93D;background:#292044;font-size:.7rem;white-space:nowrap}\n.sidebar-brand{display:flex;align-items:center;gap:10px;margin-bottom:6px}.sidebar-brand img{width:39px;height:39px}.sidebar-brand strong{display:block;font-size:1.05rem;color:#F2F0FF}.sidebar-brand small{color:#A9A5D6;font-size:.65rem}\n[data-testid="stMetric"]{background:linear-gradient(140deg,#241c47,#15132D)!important;border:1px solid #44316f!important;border-left:3px solid #FF5E7E!important;box-shadow:0 6px 18px #00000024}\n[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{border-left-color:#3DDC97!important}\n[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{border-left-color:#2EC5FF!important}\n[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p{color:#BBB7DF!important;font-size:.74rem}\n[data-testid="stMetricValue"]{color:#F2F0FF!important;font-size:1.3rem!important}\n.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stFileUploader"] button{background:#29214F;color:#F2F0FF;border:1px solid #685193;border-radius:11px;min-height:2.35rem}\n.stButton>button p,.stDownloadButton>button p,[data-testid="stFormSubmitButton"] button p,[data-testid="stFileUploader"] button p{color:inherit!important}\n[data-testid="stFormSubmitButton"] button[kind="primary"],.stButton>button[kind="primary"]{background:linear-gradient(100deg,#FF5E7E,#FF9F43 30%,#8B6CFF 70%,#2EC5FF)!important;border:0;color:#fff;text-shadow:0 1px 3px #000}\nbutton:disabled{background:#25213F!important;color:#A9A5C4!important;border-color:#48415F!important;opacity:1}\nbutton:focus-visible{outline:2px solid #FFD93D!important;outline-offset:2px}\ninput,textarea,[data-baseweb="select"] span{color:#F2F0FF!important;caret-color:#2EC5FF!important}\ninput::placeholder,textarea::placeholder{color:#A9A5D6!important}\n[data-baseweb="input"] button{background:#241D45;color:#D7CFFF}\n[data-baseweb="popover"] ul,[role="listbox"]{background:#1C1940!important;color:#F2F0FF!important}\n[data-testid="stForm"]{background:linear-gradient(130deg,#201938,#15152F);border:1px solid #443566;border-radius:15px;padding:12px}\n[data-testid="stFileUploaderDropzone"],[data-testid="stAudioInput"]{background:#1C1940;border:1px solid #514175;border-radius:12px}\n[data-testid="stAudioInput"] button{background:#39265F;color:#FFD93D;border-radius:50%}\n[data-testid="stChatMessage"]{background:linear-gradient(135deg,#201B3F,#15172F);border:1px solid #3E3266;border-radius:15px}\n.workspace-label{font-size:.72rem;font-weight:800;letter-spacing:.1em;color:#2EC5FF;margin:0}\n[data-testid="stExpander"]{border-color:#443566;border-radius:12px}\n@media(max-width:640px){.block-container{padding-top:3.4rem}.hero{padding:14px;gap:11px}.hero h1{font-size:1.4rem}.agent-logo{width:52px;height:52px}.hero-badge{display:none}.hero p{font-size:.8rem}}\n\n</style>\n', unsafe_allow_html=True)

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

