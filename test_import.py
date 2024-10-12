# test_import.py
from utils.prompt_builder import build_manual_query_prompt

def test_prompt():
    prompt = build_manual_query_prompt("What courses do I need?", "CS101")
    print(f"Test prompt: {prompt}")

if __name__ == "__main__":
    test_prompt()
