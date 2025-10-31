from openai import OpenAI
import json
import os
from fastapi import FastAPI
from pydantic import BaseModel

HISTORY_PATH = "candidate_history.json"
QUESTION_INFO = ""
SYSTEM_PROMPT = (
    "You are Candidate Assistant, a general-purpose LLM that helps the candidate solve the "
    "assessment tasks. Behave like a blank assistant focused on the user's current problem.\n"
    "- Maintain and use prior conversation context until the prompt limit is reached.\n"
    "- If the user attempts to paste the full question text, inform them that doing that is prohibited.\n"
    "- Provide clear, direct help: explanations, step-by-step guidance, examples, and code.\n"
    "- Be concise and practical; avoid revealing internal chain-of-thought.\n"
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

def candidate_respond(user_input, question_info: str | None = None):
    history = load_history()

    # Inject per-request question info into the system prompt
    system_with_q = SYSTEM_PROMPT + ("\nQuestion info: " + question_info if question_info else "")
    messages = history[:]
    if messages and messages[0].get("role") == "system":
        messages[0] = {"role": "system", "content": system_with_q}
    else:
        messages.insert(0, {"role": "system", "content": system_with_q})

    if user_input:
        messages.append({"role": "user", "content": user_input})

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024,
    )

    content = ""
    try:
        content = completion.choices[0].message.content if completion.choices else ""
    except Exception:
        pass

    if not content:
        try:
            content = json.dumps({
                "debug": "empty_content",
                "raw": completion.model_dump()
            })
        except Exception:
            content = json.dumps({"error": "no content and cannot serialize response"})

    if content:
        history.append({"role": "assistant", "content": content})
        save_history(history)

    return content

app = FastAPI()

class CandidateRequest(BaseModel):
    prompt: str
    question_info: str | None = None

@app.post("/candidate")
def candidate_endpoint(body: CandidateRequest):
    reply = candidate_respond(body.prompt, body.question_info)
    return {"reply": reply}