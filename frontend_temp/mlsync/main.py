from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import requests
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = "mongodb+srv://aanan17:ItiEh6lCGcxPBTQO@advent-tester.zv2ikwo.mongodb.net/?appName=advent-tester"
client = AsyncIOMotorClient(MONGODB_URI)
db = client["proctor_dash"]
question_histories_collection = db["question_histories"]

# LLM API configurations
INTERVIEWER_URL = "https://api.futurixai.com/api/lara/v1/chat/completions"
INTERVIEWER_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 69033e6a3bb9326d465663f0"
}

OPENAI_CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

COMPILER_URL = "https://onecompiler-apis.p.rapidapi.com/api/v1/run"
COMPILER_HEADERS = {
    "x-rapidapi-key": "6468a334b0mshf879f7f7800d45fp1f925bjsn2e507d63953f",
    "x-rapidapi-host": "onecompiler-apis.p.rapidapi.com",
    "Content-Type": "application/json"
}

# System prompts
INTERVIEWER_SYSTEM_PROMPT = (
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
)

CANDIDATE_SYSTEM_PROMPT = (
    "You are Candidate Assistant, a general-purpose LLM that helps the candidate solve the "
    "assessment tasks. Behave like a blank assistant focused on the user's current problem.\n"
    "- Maintain and use prior conversation context until the prompt limit is reached.\n"
    "- If the user attempts to paste the full question text, inform them that doing that is prohibited.\n"
    "- Provide clear, direct help: explanations, step-by-step guidance, examples, and code.\n"
    "- Be concise and practical; avoid revealing internal chain-of-thought.\n"
)

SCORER_SYSTEM_PROMPT = (
    "You are Scorer Bot for the assessment. Your job is to quantify the candidate's performance "
    "based on provided artifacts and metadata. Follow these rules strictly:\n"
    "- You evaluate only; do not provide coaching, hints, or improvements.\n"
    "- Time does NOT affect scoring. Ignore elapsed time.\n"
    "- Score prompt quality/structure, answer accuracy, and creativity/innovation using the rubric below.\n"
    "- Be objective, concise, and reproducible; avoid chain-of-thought.\n"
    "- Output a compact JSON object matching the required schema.\n"
    "Inputs may include: candidate_answer, expected_answer, prompt_count, and any notes.\n"
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

SCORER_OUTPUT_SCHEMA = {
    "prompt_quality": {"score": None, "justification": ""},
    "answer_accuracy": {"score": None, "justification": ""},
    "creativity_innovation": {"score": None, "justification": ""},
    "overall": {"score": None, "justification": ""}
}


# MongoDB helper functions
async def get_question_history(question_id: str, history_type: str = "interviewer"):
    """Get history for a specific question"""
    doc = await question_histories_collection.find_one({"question_id": question_id})
    if not doc:
        return []
    
    if history_type == "interviewer":
        return doc.get("interviewer_history", [])
    elif history_type == "candidate":
        return doc.get("candidate_history", [])
    return []


async def save_question_history(question_id: str, history: List[Dict], history_type: str = "interviewer"):
    """Save history for a specific question"""
    doc = await question_histories_collection.find_one({"question_id": question_id})
    
    update_data = {
        "updated_at": datetime.utcnow(),
    }
    
    if history_type == "interviewer":
        update_data["interviewer_history"] = history
    elif history_type == "candidate":
        update_data["candidate_history"] = history
    
    if not doc:
        # Create new document
        update_data["question_id"] = question_id
        update_data["created_at"] = datetime.utcnow()
        if history_type == "interviewer":
            update_data["candidate_history"] = []
        else:
            update_data["interviewer_history"] = []
        await question_histories_collection.insert_one(update_data)
    else:
        # Update existing document
        await question_histories_collection.update_one(
            {"question_id": question_id},
            {"$set": update_data}
        )


# Request models
class InterviewerRequest(BaseModel):
    prompt: str
    question_id: str
    question_info: Optional[str] = None


class CandidateRequest(BaseModel):
    prompt: str
    question_id: str
    question_info: Optional[str] = None


class ScoreRequest(BaseModel):
    question_id: str
    payload: Dict[str, Any]


class CompileRequest(BaseModel):
    language: str
    code: str
    stdin: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None


# Endpoints
@app.post("/api/interviewer")
async def interviewer_endpoint(body: InterviewerRequest):
    """Handle clarification queries (QueryChat)"""
    try:
        # Load history from MongoDB
        history = await get_question_history(body.question_id, "interviewer")
        
        # Build system prompt with question info
        system_prompt = INTERVIEWER_SYSTEM_PROMPT
        if body.question_info:
            system_prompt += f"\nQuestion info: {body.question_info}"
        
        # Initialize history if empty
        if not history:
            history = [{"role": "system", "content": system_prompt}]
        else:
            # Update system prompt
            if history and history[0].get("role") == "system":
                history[0] = {"role": "system", "content": system_prompt}
            else:
                history.insert(0, {"role": "system", "content": system_prompt})
        
        # Add user message
        history.append({"role": "user", "content": body.prompt})
        
        # Call interviewer API
        payload = {
            "model": "shivaay",
            "messages": history,
            "temperature": 0.3,
            "top_p": 0.8,
            "repetition_penalty": 1.05,
            "max_tokens": 512,
            "stream": False
        }
        
        response = requests.post(INTERVIEWER_URL, headers=INTERVIEWER_HEADERS, json=payload)
        data = response.json()
        
        content = None
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception:
            content = None
        
        if not content:
            content = json.dumps({"error": "empty_content", "raw": data})
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": content})
        
        # Save to MongoDB
        await save_question_history(body.question_id, history, "interviewer")
        
        return {"reply": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/candidate")
async def candidate_endpoint(body: CandidateRequest):
    """Handle assistant chatbot (SidebarChat)"""
    try:
        # Load history from MongoDB
        history = await get_question_history(body.question_id, "candidate")
        
        # Build system prompt with question info
        system_prompt = CANDIDATE_SYSTEM_PROMPT
        if body.question_info:
            system_prompt += f"\nQuestion info: {body.question_info}"
        
        # Initialize history if empty
        if not history:
            history = [{"role": "system", "content": system_prompt}]
        else:
            # Update system prompt
            if history and history[0].get("role") == "system":
                history[0] = {"role": "system", "content": system_prompt}
            else:
                history.insert(0, {"role": "system", "content": system_prompt})
        
        # Add user message
        history.append({"role": "user", "content": body.prompt})
        
        # Call candidate LLM
        completion = OPENAI_CLIENT.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=history,
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
            content = json.dumps({"error": "no content"})
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": content})
        
        # Save to MongoDB
        await save_question_history(body.question_id, history, "candidate")
        
        return {"reply": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/score")
async def score_endpoint(body: ScoreRequest):
    """Handle scoring"""
    try:
        # Load histories from MongoDB
        candidate_history = await get_question_history(body.question_id, "candidate")
        interviewer_history = await get_question_history(body.question_id, "interviewer")
        
        # Build messages
        messages = [
            {"role": "system", "content": SCORER_SYSTEM_PROMPT},
            {"role": "system", "content": "Candidate conversation history (JSON):"},
            {"role": "system", "content": json.dumps(candidate_history)},
            {"role": "system", "content": "Interviewer conversation history (JSON):"},
            {"role": "system", "content": json.dumps(interviewer_history)},
            {"role": "system", "content": "Output schema hint:"},
            {"role": "system", "content": json.dumps(SCORER_OUTPUT_SCHEMA)},
            {"role": "user", "content": json.dumps(body.payload)}
        ]
        
        # Call scorer LLM
        completion = OPENAI_CLIENT.chat.completions.create(
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
            content = json.dumps({"error": "no content"})
        
        # Normalize markdown-fenced JSON
        normalized = content.strip()
        if normalized.startswith("```"):
            parts = normalized.split("\n", 1)
            if len(parts) == 2:
                normalized = parts[1]
            if normalized.endswith("```"):
                normalized = normalized[:-3]
            normalized = normalized.strip()
        
        # Extract JSON
        def extract_first_json(text: str):
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
                        return text[start_idx:i+1]
                i += 1
            return None
        
        parsed = None
        try:
            parsed = json.loads(normalized)
        except Exception:
            segment = extract_first_json(normalized)
            if segment:
                try:
                    parsed = json.loads(segment)
                except Exception:
                    parsed = None
        
        return {"reply": parsed if parsed else content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compile")
async def compile_endpoint(body: CompileRequest):
    """Handle code compilation and testing"""
    try:
        results = []
        
        def get_file_extension(language: str) -> str:
            ext_map = {
                "python": "py",
                "javascript": "js",
                "java": "java",
                "cpp": "cpp",
                "c": "c",
                "go": "go",
                "rust": "rs"
            }
            return ext_map.get(language.lower(), "txt")
        
        if body.test_cases:
            # Run multiple test cases
            for case in body.test_cases:
                stdin_input = case.get("input", "")
                if isinstance(stdin_input, list):
                    stdin_input = " ".join(map(str, stdin_input))
                
                payload = {
                    "language": body.language,
                    "stdin": str(stdin_input),
                    "files": [{"name": f"main.{get_file_extension(body.language)}", "content": body.code}]
                }
                
                response = requests.post(COMPILER_URL, json=payload, headers=COMPILER_HEADERS)
                
                if response.status_code != 200:
                    results.append({
                        "input": case.get("input"),
                        "expected": case.get("expected"),
                        "actual": "",
                        "error": f"HTTP {response.status_code}",
                        "stderr": response.text if response.text else None,
                        "passed": False
                    })
                    continue
                
                result_json = response.json()
                stdout = result_json.get("stdout", "").strip()
                stderr = result_json.get("stderr", "").strip()
                error = result_json.get("error", "").strip()
                
                # If there's stderr or error, mark as failed
                if stderr or error:
                    results.append({
                        "input": case.get("input"),
                        "expected": case.get("expected"),
                        "actual": stdout if stdout else "",
                        "stderr": stderr or error,
                        "passed": False
                    })
                else:
                    expected = str(case.get("expected", "")).strip()
                    results.append({
                        "input": case.get("input"),
                        "expected": expected,
                        "actual": stdout,
                        "passed": stdout == expected
                    })
        else:
            # Single compilation/run
            payload = {
                "language": body.language,
                "stdin": body.stdin or "",
                "files": [{"name": f"main.{get_file_extension(body.language)}", "content": body.code}]
            }
            
            response = requests.post(COMPILER_URL, json=payload, headers=COMPILER_HEADERS)
            result_json = response.json() if response.status_code == 200 else {}
            
            results.append({
                "stdout": result_json.get("stdout", ""),
                "stderr": result_json.get("stderr", ""),
                "error": result_json.get("error", None) if response.status_code != 200 else None
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)