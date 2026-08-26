# TaskPilot AI 🗂️

**Track 3 Submission — Automate Daily Operations with a Productivity Agent**

TaskPilot AI is an AI productivity agent that automates daily operations for a busy
professional: managing tasks, checking meetings, drafting emails, and generating
daily briefings. It uses real tool/function calling to take actions on a live
workspace, not just chat about them.

## Features (Tools the agent can call)
- `list_tasks(status)` — list pending/completed tasks
- `add_task(title, priority, due)` — add a new task
- `complete_task(task_id)` — mark a task done
- `get_todays_meetings()` — check today's schedule
- `draft_email(recipient_context, purpose, key_points)` — log and prepare an email draft
- `generate_daily_brief()` — full daily operations summary

## Tech Stack
- **Frontend/App:** Streamlit
- **LLM:** Groq (LLaMA 3.1 8B Instant) with native tool calling
- **State:** In-memory workspace (simulates a real task/calendar backend)

## Run Locally
```bash
pip install -r requirements.txt
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

## Deploy on Render
1. Push this folder to a GitHub repo.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Add environment variable `GROQ_API_KEY`.
6. Deploy — you'll get a live URL like `https://taskpilot-ai.onrender.com`.
