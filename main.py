import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

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
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}()")

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
    function_call_parts = content.function_calls

    if len(sys.argv) > 2:
        if sys.argv[2] == "--verbose":
            if function_call_parts:
                print(f"User prompt: : {user_prompt}\n")
                print(f"Prompt tokens: {prompt_tokens}")
                print(f"Response tokens: {response_tokens}")

                for func in function_call_parts:
                    try:
                        function_call_result = call_function(func, True)
                        response_dict = function_call_result.parts[0].function_response.response
                        print(f"->\n{response_dict['result']}")
                    except Exception:
                        sys.exit(1)
            else:
                print(text)
        else:
            print("Error: invalid arguments passed")
    else:
        if function_call_parts:
            for func in function_call_parts:
                function_call_result = call_function(func)
                response_dict = function_call_result.parts[0].function_response.response
                print(f"->\n{response_dict['result']}")
        else:
            print(text)

if __name__ == "__main__":
    main()
