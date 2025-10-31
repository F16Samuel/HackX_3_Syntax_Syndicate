from openai import OpenAI
import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

QUESTION_INFO = ""
RUBRIC_INFO = ""
CANDIDATE_HISTORY_PATH = "candidate_history.json"
INTERVIEWER_HISTORY_PATH = "interviewer_history.json"

SYSTEM_PROMPT = (
    "You are Scorer Bot for the assessment. Your job is to quantify the candidate's performance "
    "based on provided artifacts and metadata. Follow these rules strictly:\n"
    "- You evaluate only; do not provide coaching, hints, or improvements.\n"
    "- Time does NOT affect scoring. Ignore elapsed time.\n"
    "- Score prompt quality/structure, answer accuracy, and creativity/innovation using the rubric below.\n"
    "- Be objective, concise, and reproducible; avoid chain-of-thought.\n"
    "- Output a compact JSON object matching the required schema.\n"
    "Inputs may include: candidate_answer, expected_answer, prompt_count, and any notes.\n"
    + ("Question info: " + QUESTION_INFO + "\n" if QUESTION_INFO else "")
    + ("Additional rubric info: " + RUBRIC_INFO + "\n" if RUBRIC_INFO else "")
    + (
        "Scoring dimensions and guidance (each 0-10; total out of 30):\n"
        "1) Prompt Quality and Structure (0-10):\n"
        "   - Consider BOTH number of prompts (prompt_count) and their quality.\n"
        "   - If prompt_count == 0: assign FULL MARKS (10/10) for prompt efficiency.\n"
        "   - Prefer fewer, higher-quality prompts; however, two good, smart prompts are BETTER than one bad prompt.\n"
        "   - 0: Vague ('help me'); 5: moderately structured; 10: clear, concise, constraints/examples, iteration-aware.\n"
        "2) Answer Accuracy (0-10): Compare candidate_answer vs expected_answer.\n"
        "   - 0: Incorrect/irrelevant; 5: partially correct; 10: fully correct or better while consistent with requirements.\n"
        "3) Creativity and Innovation (0-10): Assess based on candidate's interactions and doubts in interviewer history.\n"
        "   - Consider whether questions show initiative, thoughtful problem framing, constraints awareness, or testing strategy.\n"
        "   - Reward original, constructive inquiry (e.g., clarifying I/O constraints, edge cases, evaluation).\n"
        "   - Penalize trivial, irrelevant, or exploitative questions (e.g., fishing for hints or answers).\n"
        "Provide brief, non-speculative justifications for each score without revealing hidden solutions.\n"
        "Return ONLY the JSON object described below, and set overall.score to the sum (0-30)."
    )
)

OUTPUT_SCHEMA_HINT = {
    "prompt_quality": {
        "score": None,
        "justification": ""
    },
    "answer_accuracy": {
        "score": None,
        "justification": ""
    },
    "creativity_innovation": {
        "score": None,
        "justification": ""
    },
    "overall": {
        "score": None,
        "justification": ""
    }
}

def scorer_respond(user_input):
    """
    user_input: string. Recommended to pass a JSON string with fields like:
      {
        "candidate_answer": "...",
        "expected_answer": "...",
        "elapsed_seconds": 123,
        "prompt_count": 5,
        "notes": "optional context"
      }
    The function returns the model's textual content (expected to be a JSON object per schema).
    """
    # Load candidate conversation to use as evaluation context
    try:
        with open(CANDIDATE_HISTORY_PATH, "r", encoding="utf-8") as f:
            candidate_history = json.load(f)
            if not isinstance(candidate_history, list):
                candidate_history = []
    except Exception:
        candidate_history = []

    # Load interviewer conversation to evaluate creativity/innovation via doubts
    try:
        with open(INTERVIEWER_HISTORY_PATH, "r", encoding="utf-8") as f:
            interviewer_history = json.load(f)
            if not isinstance(interviewer_history, list):
                interviewer_history = []
    except Exception:
        interviewer_history = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": "Candidate conversation history (JSON):"},
        {"role": "system", "content": json.dumps(candidate_history)},
        {"role": "system", "content": "Interviewer conversation history (JSON):"},
        {"role": "system", "content": json.dumps(interviewer_history)}
    ]

    if user_input:
        messages.append({"role": "user", "content": user_input})

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

    # Provide a tool hint of the expected output shape as system-visible content
    messages.extend([
        {"role": "system", "content": "Output schema hint:"},
        {"role": "system", "content": json.dumps(OUTPUT_SCHEMA_HINT)}
    ])

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3.1:free",
        messages=messages,
        temperature=0.3,
        top_p=0.8,
        max_tokens=700,
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

    return content


app = FastAPI()

class ScoreRequest(BaseModel):
    payload: dict

@app.post("/score")
def score_endpoint(body: ScoreRequest):
    # Pass through the payload as JSON string to the scorer
    reply_text = scorer_respond(json.dumps(body.payload))

    # Normalize markdown-fenced JSON blocks to parsed JSON
    normalized = reply_text.strip()
    if normalized.startswith("```"):
        # strip fences like ```json ... ```
        parts = normalized.split("\n", 1)
        if len(parts) == 2:
            normalized = parts[1]
        if normalized.endswith("```"):
            normalized = normalized[:-3]
        normalized = normalized.strip()

    def _extract_first_json(text: str):
        # Find the first JSON object or array and return its substring
        if not text:
            return None
        start_candidates = []
        try:
            first_obj = text.index('{')
            start_candidates.append((first_obj, '{', '}'))
        except ValueError:
            pass
        try:
            first_arr = text.index('[')
            start_candidates.append((first_arr, '[', ']'))
        except ValueError:
            pass
        if not start_candidates:
            return None
        start_idx, open_ch, close_ch = min(start_candidates, key=lambda x: x[0])
        i = start_idx
        depth_obj = 0
        depth_arr = 0
        in_str = False
        esc = False
        while i < len(text):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == '\\':
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == '{':
                    depth_obj += 1
                elif ch == '}':
                    depth_obj -= 1
                elif ch == '[':
                    depth_arr += 1
                elif ch == ']':
                    depth_arr -= 1
                if depth_obj == 0 and depth_arr == 0 and i >= start_idx:
                    segment = text[start_idx:i+1]
                    return segment
            i += 1
        return None

    parsed = None
    # First try direct parse
    try:
        parsed = json.loads(normalized)
    except Exception:
        # Try extracting the first JSON-looking segment
        segment = _extract_first_json(normalized)
        if segment is not None:
            try:
                parsed = json.loads(segment)
            except Exception:
                parsed = None


