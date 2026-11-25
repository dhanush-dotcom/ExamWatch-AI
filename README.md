# ExamWatch AI
Local academic demonstration, not a cheating detector. No identity matching, gaze inference, audio capture or saved images. Use only consenting demo participants. No authentication: do not expose to a network or use for actual examinations.

## Windows 10/11 setup (PowerShell)
1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/windows/ (check Add Python to PATH). Install VS Code from https://code.visualstudio.com/ and its Python extension. Git is not required. Install Chrome if needed. Install Ollama from https://ollama.com/download/windows and launch it.
2. In Windows PowerShell verify installations: `py -3.11 --version` (or `py -3.12 --version`), `ollama --version`. Expect version numbers. Run `ollama pull llama3.2:3b` to download the model, then `ollama list` to verify it. Run `ollama run llama3.2:3b` to test a prompt, then `/bye` to exit. Ollama normally runs in the background; if not, run `ollama serve` in a separate terminal.
3. Extract the ZIP using File Explorer (Extract All). All folders and files already exist. Open the extracted ExamWatch_AI folder in VS Code using File > Open Folder. Open Terminal > New Terminal; select PowerShell. Run the following commands individually in that terminal:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "from event_manager import Store; Store(); print('Database ready')"
python app.py
```
Use `py -3.12` instead if installed. The first command creates an isolated environment; the second activates it (expect `.venv` in prompt); pip installs dependencies; the database command initializes tables; the last command starts Flask on http://127.0.0.1:5000. Keep terminal open. If activation is blocked, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or invoke `.\.venv\Scripts\python.exe` directly instead of `python`.
4. Open http://127.0.0.1:5000 in Chrome. Click Start examination, tick consent, start monitoring and allow camera. Move out of frame, then return; wait at least three seconds per observation. With another consenting adult, demonstrate multiple visible faces. Stop camera or end session. Open dashboard, refresh, review an event, save comments. End session to see a summary. Ask the assistant “How do I allow webcam access?” and inspect sources and response mode. Submit feedback.
5. Open http://127.0.0.1:5000/api/health to see dataset count, vision and Ollama availability. If Ollama is off, assistant uses retrieved answers. No relevant records produces a no-match response.
6. In a second VS Code PowerShell terminal, activate the environment and run `python -m pytest -q`. Tests use temporary databases, synthetic images and mocked Ollama; no camera required.

## Optional phone detector
See models/README.md. Core face detection uses the Haar cascade bundled with OpenCV; no download needed. Face position change is not head pose or gaze; face count change does not prove entry/exit. No snapshots are saved. Missing OpenCV reports unavailable rather than inventing detections. Optional YOLO uses CPU and may be slow.

## Troubleshooting
- Python not found: reopen terminal after installation; use `py -0p` to list installed versions.
- Missing modules: activate the correct environment and repeat pip install.
- Camera denied: Chrome site settings > Camera > Allow; check Windows Privacy & security > Camera and close competing apps.
- Ollama unavailable: run `ollama list`, pull model if absent, start Ollama. Retrieval still works.
- Port busy: stop the other Flask instance with Ctrl+C.
- No events: ensure monitoring is active and wait for capture; duplicate event types have a 15-second cooldown.
- Database reset: stop Flask, delete `database/examwatch.db` (permanently removes demo sessions, feedback and events), then restart. No automatic retention policy. Sessions abandoned by closing the tab can remain active; reset the demo database if necessary.

## Checklist and demo
- [ ] Dependencies installed and health endpoint checked
- [ ] Consent and camera preview demonstrated
- [ ] Face observations and cooldown demonstrated
- [ ] Dashboard review and comments saved
- [ ] Session ended and summary shown
- [ ] Assistant sources and fallback demonstrated
- [ ] Tests run and actual screenshots captured

Professor demo: explain local browser capture → Flask → OpenCV → SQLite → human review. Then ask a camera question, explain TF-IDF similarity and top-three retrieval, show Ollama response mode, and explain that neither model decides misconduct. Show test output and limitations.

## Files
app.py routes; config.py paths; vision.py image decoding and observations; event_manager.py SQLite; retrieval.py TF-IDF; ai_assistant.py Ollama and fallback; templates/static browser UI; data JSON/CSV; tests automated checks; docs report and viva. Source URLs are reference pointers, not live-verified in the build environment.
