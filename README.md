# Rainbow Voice Studio

A browser-based Streamlit voice assistant with a rainbow accent theme, recording,
audio uploads, editable transcripts, multi-turn history, spoken replies, voice
selection, specialty profiles, Urdu/English options and downloadable conversations.

## Windows setup (PowerShell)
Extract this folder into `C:\Users\GA GROUP\Desktop\Huawei_AI` and run:

```powershell
cd "C:\Users\GA GROUP\Desktop\Huawei_AI\rainbow-voice-agent"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Python 3.12 is the suggested environment; install it if `py -3.12` is unavailable.
Open the URL printed by Streamlit. Supply your OpenAI API key in the sidebar, or
copy `.env.example` to `.env` and fill in the key. Never commit secrets.

## Use
1. Choose specialty, reply language, voice and response length.
2. Allow the browser microphone, record and stop; or upload audio and select
   Uploaded file as the source.
3. Click Transcribe selected audio. Review/edit the transcript.
4. Click Send to voice agent. The answer and MP3 appear in conversation history.
5. Download replies or export the conversation. New conversation clears history.

Typed input works without microphone permission. Speech generation can be disabled.
If voice generation fails, the text answer remains and voice can be retried.
Browser autoplay may be blocked; use the audio player's Play button.

## Deployment on Streamlit Community Cloud
Push the folder contents to GitHub, choose `app.py` as the entry point and configure
`OPENAI_API_KEY` in app secrets if you want a server-managed key. A server-managed
key pays for every visitor's usage: deploy privately or require authentication for
shared use. Visitors can instead supply their own key. Use HTTPS for microphone
permission on remote deployments. Localhost works for development.

## Architecture and limits
Browser WAV/upload -> OpenAI transcription -> Responses API with last 20 messages
-> OpenAI speech -> browser MP3 playback. This deliberately replaces desktop-only
sounddevice and the Agents SDK VoicePipeline with a simpler sequential pipeline.
It is a conversational assistant, not a tool-using autonomous agent. It does not
book travel, browse live data, or perform external actions.

Default response model preserves the original `gpt-5.4-mini`; model access depends
on your account. Change names in advanced settings if unavailable. Defaults for
audio are `gpt-4o-mini-transcribe` and `gpt-4o-mini-tts`.

This is turn-based audio, not a full-duplex Realtime API implementation. Speech
starts after text generation. Input is capped at 20 MB and 12,000 typed characters.
Speech input is capped at 4,000 characters. The app is intended for short turns.
History and MP3s are held in Streamlit session memory, not a database. Refreshes,
server restarts or session expiry may reset it. Download important conversations.

Audio/text are transmitted to OpenAI only on explicit submission; no trace export
is configured. `store=False` is used on Responses requests. Provider retention
policies still apply. API usage requires billing independently of ChatGPT plans.

## Review of the uploaded script
- Desktop sounddevice uses the server microphone/speakers and cannot capture a
  remote Streamlit visitor's audio. Replaced with browser audio input and playback.
- Blocking input() is incompatible with web interaction. Replaced with explicit controls.
- np.concatenate(chunks) can fail on empty recordings. New input validation added.
- The source has no conversation history, error handling, editable transcript,
  upload path, downloadable output, or API-key UI. Added all these features.
- Duplicate dotenv loading removed; no secret values are logged or exported.
- Original output stream lacks guaranteed cleanup after exceptions; browser audio
  avoids the native device lifecycle entirely.
- Original access to total_output_text was SDK-version dependent. New code uses
  the documented Responses output_text field.

## Validation
Python syntax and offline Streamlit smoke tests are run before packaging. API
calls are not live-tested because no API key was supplied. A valid key with access
to the selected models is required to verify transcription and speech end to end.

## Documentation
- https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
- https://developers.openai.com/api/docs/guides/speech-to-text
- https://developers.openai.com/api/docs/guides/text-to-speech
