import requests

# --- API Info ---
URL = "https://onecompiler-apis.p.rapidapi.com/api/v1/run"
HEADERS = {
    "x-rapidapi-key": "6468a334b0mshf879f7f7800d45fp1f925bjsn2e507d63953f",
    "x-rapidapi-host": "onecompiler-apis.p.rapidapi.com",
    "Content-Type": "application/json"
}

# --- User submission ---
user_function_code = """
def sum_two_numbers(a, b):
    return a + b
"""

# --- Function name (you can auto-extract this later) ---
function_name = "sum_two_numbers"

# --- Test cases ---
test_cases = [
    {"input": [2, 3], "expected": "5"},
    {"input": [-1, 1], "expected": "0"},
    {"input": [10, 15], "expected": "25"},
]

results = []

# --- Run each test case ---
for case in test_cases:
    stdin_input = " ".join(map(str, case["input"]))

    # Automatically build the code that runs the user's function
    wrapped_code = f"""{user_function_code}

if __name__ == "__main__":
    import sys
    inputs = list(map(int, sys.stdin.read().split()))
    print({function_name}(*inputs))
"""

    payload = {
        "language": "python",
        "stdin": stdin_input,
        "files": [
            {"name": "main.py", "content": wrapped_code}
        ]
    }

    response = requests.post(URL, json=payload, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        continue

    result_json = response.json()
    output = result_json.get("stdout", "").strip()
    expected = str(case["expected"]).strip()

    results.append({
        "input": case["input"],
        "expected": expected,
        "actual": output,
        "passed": output == expected
    })

# --- Display results ---
for i, r in enumerate(results, 1):
    print(f"Test {i}: input={r['input']} | expected={r['expected']} | got={r['actual']} | passed={r['passed']}")
