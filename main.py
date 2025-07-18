import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

import schemas

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        print("Usage: uv run main.py <prompt for llm>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    messages = [ types.Content(role="user", parts=[types.Part(text=user_prompt)]) ]
    available_functions = types.Tool(
        function_declarations=[
            schemas.schema_get_files_info,
            schemas.schema_get_file_content,
            schemas.schema_write_file,
            schemas.schema_run_python_file,
        ]
    )
    content = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    text = content.text
    prompt_tokens = content.usage_metadata.prompt_token_count
    response_tokens = content.usage_metadata.candidates_token_count
    function_call_part = content.function_calls

    if len(sys.argv) > 2:
       if sys.argv[2] == "--verbose":
            print(f"User prompt: : {user_prompt}\n")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Response tokens: {response_tokens}")
       else:
           print("Error: invalid arguments passed")
    else:
        if function_call_part:
            for func in function_call_part:
                print(f"Calling function: {func.name}({func.args})")
            print(text)
        else:
            print(text)

if __name__ == "__main__":
    main()
