import requests
import json
import os
from fastapi import FastAPI
from pydantic import BaseModel

url = "https://api.futurixai.com/api/lara/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 69033e6a3bb9326d465663f0"
}

HISTORY_PATH = "interviewer_history.json"
QUESTION_INFO = ""

SYSTEM_PROMPT = (
    "You are Interviewer Bot for an assessment. Your sole role is to clarify rules, "
    "logistics, and process. Follow these constraints strictly:\n"
    "- Do not provide hints, strategies, code, algorithms, or partial solutions.\n"
    "- Do not improve, critique, or analyze a candidate's solution.\n"
    "- The marking rubric consists of Prompt Efficiency, Creativity and Innovation(Both under one rubric) and Answer Correctness.\n"
    "- If asked about content help, politely refuse and redirect to interview rules.\n"
    "- Keep a professional, neutral, and concise tone.\n"
    "- Summarize relevant instructions when helpful, without giving competitive advantage.\n"
    "Context you may disclose: time limits, prompt quotas, scoring rubric at a high level, "
    "allowed tools/policies, submission format, and how evaluation happens.\n"
    "Assessment details: Time limit is 10 minutes. Prompt usage is limited by backend. "
    "Scoring considers time/prompts (backend), prompt quality/structure, and answer accuracy "
    "against the expected answer. The question context is known to the system but you must not "
    "share any approach to solving it." 
    + ("\nQuestion info: " + QUESTION_INFO if QUESTION_INFO else "")
)

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

def save_history(history):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def interviewer_respond(user_input: str, question_info: str | None = None) -> str:
    history = load_history()

    # Build a request-specific system message that can include question_info
    system_with_q = SYSTEM_PROMPT + ("\nQuestion info: " + question_info if question_info else "")

    # Replace the first system message with the request-specific one
    messages = history[:]
    if messages and messages[0].get("role") == "system":
        messages[0] = {"role": "system", "content": system_with_q}
    else:
        messages.insert(0, {"role": "system", "content": system_with_q})

    if user_input:
        messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "shivaay",
        "messages": messages,
        "temperature": 0.3,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "max_tokens": 512,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    content = None
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = None

    if not content:
        content = json.dumps({"debug": "empty_content", "raw": data})

    if content:
        history.append({"role": "assistant", "content": content})
        save_history(history)

    return content

app = FastAPI()

class InterviewerRequest(BaseModel):
    prompt: str
    question_info: str | None = None

@app.post("/interviewer")
def interviewer_endpoint(body: InterviewerRequest):
    reply = interviewer_respond(body.prompt, body.question_info)
    return {"reply": reply}