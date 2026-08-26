"""
TaskPilot AI — Automate Daily Operations with a Productivity Agent
Track 3: Automate Daily Operations with a Productivity Agent Codelab
Built with Streamlit + Groq (LLaMA 3.1) with real tool/function calling.
An AI agent that manages tasks, drafts emails, preps meetings, and
generates daily briefings — taking real actions, not just chatting.
"""

import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="TaskPilot AI", page_icon="🗂️", layout="centered")

# ---------------------------------------------------------
# IN-MEMORY "WORKSPACE" STATE (simulates a real productivity backend)
# ---------------------------------------------------------
def init_state():
    if "tasks" not in st.session_state:
        st.session_state.tasks = [
            {"id": "T1", "title": "Review Q3 marketing report", "priority": "High", "due": "Today", "status": "Pending"},
            {"id": "T2", "title": "Prepare slides for client demo", "priority": "High", "due": "Tomorrow", "status": "Pending"},
            {"id": "T3", "title": "Reply to vendor invoice email", "priority": "Medium", "due": "Today", "status": "Pending"},
            {"id": "T4", "title": "Update team standup notes", "priority": "Low", "due": "This week", "status": "Completed"},
        ]
    if "meetings" not in st.session_state:
        st.session_state.meetings = [
            {"title": "Client Demo Call", "time": "3:00 PM Today", "attendees": "Client team, Sales lead", "notes": "Show new dashboard features"},
            {"title": "Weekly Team Sync", "time": "10:00 AM Tomorrow", "attendees": "Full team", "notes": "Sprint review + blockers"},
        ]
    if "drafts" not in st.session_state:
        st.session_state.drafts = []


init_state()

# ---------------------------------------------------------
# TOOL FUNCTIONS (the agent — real actions on the workspace)
# ---------------------------------------------------------
def list_tasks(status: str = "all") -> str:
    tasks = st.session_state.tasks
    if status.lower() != "all":
        tasks = [t for t in tasks if t["status"].lower() == status.lower()]
    return json.dumps(tasks)


def add_task(title: str, priority: str = "Medium", due: str = "Today") -> str:
    new_id = f"T{len(st.session_state.tasks) + 1}"
    task = {"id": new_id, "title": title, "priority": priority, "due": due, "status": "Pending"}
    st.session_state.tasks.append(task)
    return json.dumps({"created": task})


def complete_task(task_id: str) -> str:
    for t in st.session_state.tasks:
        if t["id"].upper() == task_id.upper():
            t["status"] = "Completed"
            return json.dumps({"updated": t})
    return json.dumps({"error": f"No task found with ID {task_id}"})


def get_todays_meetings() -> str:
    today_meetings = [m for m in st.session_state.meetings if "Today" in m["time"]]
    return json.dumps(today_meetings if today_meetings else {"message": "No meetings scheduled for today"})


def draft_email(recipient_context: str, purpose: str, key_points: str) -> str:
    draft = {
        "id": f"D{len(st.session_state.drafts) + 1}",
        "recipient_context": recipient_context,
        "purpose": purpose,
        "key_points": key_points,
        "created_at": datetime.now().strftime("%H:%M"),
    }
    st.session_state.drafts.append(draft)
    return json.dumps({"draft_saved": draft, "note": "Draft logged. Compose the actual email text in your reply to the user."})


def generate_daily_brief() -> str:
    pending = [t for t in st.session_state.tasks if t["status"] == "Pending"]
    high_priority = [t for t in pending if t["priority"] == "High"]
    today_meetings = [m for m in st.session_state.meetings if "Today" in m["time"]]
    return json.dumps({
        "date": datetime.now().strftime("%A, %d %b %Y"),
        "pending_tasks": len(pending),
        "high_priority_tasks": high_priority,
        "todays_meetings": today_meetings,
    })


TOOL_FUNCTIONS = {
    "list_tasks": list_tasks,
    "add_task": add_task,
    "complete_task": complete_task,
    "get_todays_meetings": get_todays_meetings,
    "draft_email": draft_email,
    "generate_daily_brief": generate_daily_brief,
}

TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "list_tasks",
        "description": "List tasks, optionally filtered by status (Pending, Completed, or all).",
        "parameters": {"type": "object", "properties": {
            "status": {"type": "string", "description": "Filter: Pending, Completed, or all"}
        }, "required": []},
    }},
    {"type": "function", "function": {
        "name": "add_task",
        "description": "Add a new task to the workspace.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string", "description": "Task title"},
            "priority": {"type": "string", "description": "High, Medium, or Low"},
            "due": {"type": "string", "description": "Due date, e.g. Today, Tomorrow, This week"},
        }, "required": ["title"]},
    }},
    {"type": "function", "function": {
        "name": "complete_task",
        "description": "Mark a task as completed using its task ID (e.g. T1).",
        "parameters": {"type": "object", "properties": {
            "task_id": {"type": "string", "description": "The task ID, e.g. T1"}
        }, "required": ["task_id"]},
    }},
    {"type": "function", "function": {
        "name": "get_todays_meetings",
        "description": "Get meetings scheduled for today.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "draft_email",
        "description": "Log and prepare a draft email for a given purpose. Use this when the user asks you to write/draft an email.",
        "parameters": {"type": "object", "properties": {
            "recipient_context": {"type": "string", "description": "Who this email is for, e.g. 'the vendor', 'my manager'"},
            "purpose": {"type": "string", "description": "Purpose of the email"},
            "key_points": {"type": "string", "description": "Key points to include"},
        }, "required": ["recipient_context", "purpose", "key_points"]},
    }},
    {"type": "function", "function": {
        "name": "generate_daily_brief",
        "description": "Generate a daily operations briefing: pending tasks, high priority items, and today's meetings.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
]

SYSTEM_PROMPT = """You are TaskPilot, an AI productivity agent that automates daily operations for a busy 
professional. You have access to real tools to manage tasks, check meetings, log email drafts, and generate 
daily briefings.

Rules:
1. ALWAYS use tools to get or change real data — never guess task lists or meeting details.
2. When asked to draft an email, call draft_email to log it AND write the actual email text in your reply.
3. When asked for a daily briefing, call generate_daily_brief and present it as a clear, actionable summary.
4. Be concise and action-oriented — this is a productivity tool, not a chatty assistant.
5. If asked something outside task/meeting/email management, politely say that's outside your scope.
"""

def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found. Add it in Render → Environment.")
        st.stop()
    return Groq(api_key=api_key)


def run_agent(client, messages):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto",
        max_tokens=900,
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            fn = TOOL_FUNCTIONS.get(fn_name)
            result = fn(**args) if fn else json.dumps({"error": "Unknown tool"})
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": fn_name,
                "content": result,
            })
        follow_up = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=900,
        )
        final_msg = follow_up.choices[0].message.content
        messages.append({"role": "assistant", "content": final_msg})
        return final_msg
    else:
        messages.append({"role": "assistant", "content": msg.content})
        return msg.content


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("🗂️ TaskPilot AI")
st.caption("Your AI productivity agent — automating daily operations with Groq LLaMA 3.1")

with st.sidebar:
    st.header("📋 Today's Workspace")
    pending = [t for t in st.session_state.tasks if t["status"] == "Pending"]
    st.metric("Pending Tasks", len(pending))
    st.metric("Meetings Today", len([m for m in st.session_state.meetings if "Today" in m["time"]]))

    st.divider()
    st.subheader("Quick actions")
    if st.button("📌 Give me today's briefing"):
        st.session_state.setdefault("pending_prompt", "Give me my daily briefing")
    if st.button("✅ What are my high priority tasks?"):
        st.session_state.setdefault("pending_prompt", "What are my pending high priority tasks?")
    if st.button("✉️ Draft an email to the vendor about the invoice"):
        st.session_state.setdefault("pending_prompt", "Draft an email to the vendor asking for a corrected invoice by end of week")
    if st.button("📅 What meetings do I have today?"):
        st.session_state.setdefault("pending_prompt", "What meetings do I have today and what should I prepare?")

    st.divider()
    st.caption("Built for Track 3: Automate Daily Operations with a Productivity Agent")

# --- Task board ---
st.subheader("Task Board")
for t in st.session_state.tasks:
    icon = "✅" if t["status"] == "Completed" else "🔲"
    priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(t["priority"], "⚪")
    st.markdown(f"{icon} **{t['title']}** — {priority_color} {t['priority']} · Due: {t['due']} · `{t['id']}`")

st.divider()

# --- Chat ---
st.subheader("Ask TaskPilot AI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for m in st.session_state.messages:
    if m["role"] in ("user", "assistant") and m.get("content"):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

prompt = st.chat_input("Ask about tasks, meetings, or request an email draft...")
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Working on it..."):
            client = get_client()
            reply = run_agent(client, st.session_state.messages)
            st.markdown(reply)
