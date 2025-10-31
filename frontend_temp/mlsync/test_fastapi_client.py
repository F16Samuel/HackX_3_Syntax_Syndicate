import os
import json
import requests

CANDIDATE_URL = os.getenv("CANDIDATE_URL", "http://127.0.0.1:8003/candidate")
INTERVIEWER_URL = os.getenv("INTERVIEWER_URL", "http://127.0.0.1:8001/interviewer")
SCORER_URL = os.getenv("SCORER_URL", "http://127.0.0.1:8002/score")


def test_candidate():
    payload = {
        "prompt": "Give me a high-level plan to reverse a string without built-ins."
    }
    r = requests.post(CANDIDATE_URL, json=payload, timeout=60)
    r.raise_for_status()
    print("Candidate reply:\n", r.json())


def test_interviewer():
    payload = {
        "prompt": "What is the time limit and how many prompts can I use?"
    }
    r = requests.post(INTERVIEWER_URL, json=payload, timeout=60)
    r.raise_for_status()
    print("Interviewer reply:\n", r.json())


def test_scorer():
    scoring_payload = {
        "candidate_answer": "Two-pointer reverse; swap ends inward. O(n) time, O(1) space.",
        "expected_answer": "Manual reverse via indices, no built-ins; handle empty/single-char.",
        "elapsed_seconds": 300,
        "prompt_count": 2,
        "notes": "Handled edge cases."
    }
    r = requests.post(SCORER_URL, json={"payload": scoring_payload}, timeout=60)
    r.raise_for_status()
    print("Scorer reply:\n", r.json())


if __name__ == "__main__":
    try:
        test_candidate()
    except Exception as e:
        print("Candidate test failed:", e)

    try:
        test_interviewer()
    except Exception as e:
        print("Interviewer test failed:", e)

    try:
        test_scorer()
    except Exception as e:
        print("Scorer test failed:", e)



