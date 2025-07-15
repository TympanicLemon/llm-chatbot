import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        print("Usage: uv run main.py <prompt for llm>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    messages = [ types.Content(role="user", parts=[types.Part(text=user_prompt)]) ]
    content = client.models.generate_content(model="gemini-2.0-flash-001", contents=messages)

    text = content.text
    prompt_tokens = content.usage_metadata.prompt_token_count
    response_tokens = content.usage_metadata.candidates_token_count

    print(f"User prompt: : {user_prompt}\n")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")

if __name__ == "__main__":
    main()
