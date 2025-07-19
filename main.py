import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

import config
from functions import get_files_info
import schemas

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = function_call_part.args

    functions = {
        "get_files_info": get_files_info.get_files_info,
        "get_file_content": get_files_info.get_file_content,
        "write_file": get_files_info.write_file,
        "run_python_file": get_files_info.run_python_file
    }

    if not function_name in functions:
        print(f"Function called {function_name} does not exist")
    else:
        func = functions[function_name]

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function_args["working_directory"] = "./calculator"
    result = func(**function_args)

    if not function_name in functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": result},
                )
            ],
        )


def main():
    _ = load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        print("Usage: uv run main.py <prompt for llm>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a detailed plan of action on what steps need to be taken
    to address said question or task. If the task involves changing code in some way, shape or form, then make sure
    to first scan the appropriate files or directories, and use that context to drive your next steps or actions.

    Here are some function calls you can use to help:

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

    for _ in range(config.MAX_LLM_ITERATIONS):
        content = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        function_call_parts = content.function_calls

        candidates = content.candidates
        for candidate in candidates:
            messages.append(candidate.content)

        if function_call_parts:
            for func in function_call_parts:
                try:
                    if len(sys.argv) > 2:
                        if sys.argv[2] == "--verbose":
                            function_call_result = call_function(func, True)
                            messages.append(function_call_result)
                        else:
                            print("Error: invalid argument[s] passed, usage: uv run main.py <prompt>")
                    elif len(sys.argv) == 2:
                        function_call_result = call_function(func)
                        messages.append(function_call_result)
                    else:
                        print("Error: invalid argument[s] passed, usage: uv run main.py <prompt>")
                except Exception as e:
                    print(f"Error: {e}")
                    sys.exit(1)

        # Used to be if content.text
        if not function_call_parts:
            break

    if len(sys.argv) > 2:
        if sys.argv[2] == "--verbose":
            print(f"User prompt: : {user_prompt}\n")
            print(f"Prompt tokens: {content.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {content.usage_metadata.candidates_token_count}")
            print("\nFinal response:")
            print(content.text)
        else:
            print("Error: invalid argument[s] passed, usage: uv run main.py <prompt>")
    elif len(sys.argv) == 2:
        print("\nFinal response:")
        print(content.text)
    else:
        print("Error: invalid argument[s] passed, usage: uv run main.py <prompt>")


if __name__ == "__main__":
    main()
