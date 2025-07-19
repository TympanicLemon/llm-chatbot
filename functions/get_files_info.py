import os
import subprocess
import config

def get_files_info(working_directory, directory="."):
    working_path = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_path, directory))

    if not full_path.startswith(working_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'

    try:
        dir_contents = os.listdir(full_path)
        content_data = ""

        for item in dir_contents:
            file_size = os.path.getsize(os.path.join(full_path, item))
            item_full_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_full_path)
            formatted_string = f' - {item}: file_size={file_size} bytes, is_dir={is_dir}\n'
            content_data += formatted_string
    except OSError as e:
        return f'Error: {e}'
    else:
        return content_data

def get_file_content(working_directory, file_path):
    working_dir_path = os.path.abspath(working_directory)
    file_path_abs = os.path.abspath(os.path.join(working_dir_path, file_path))

    if not file_path_abs.startswith(working_dir_path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_path_abs):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(file_path_abs, "r") as f:
            file_content_string = f.read()

            if len(file_content_string) > config.MAX_CHARS:
                return file_content_string[:config.MAX_CHARS] + f' [...File "{file_path}" truncated at 10000 characters]'
    except Exception as e:
        return f'Error: {e}'
    else:
        return file_content_string

def write_file(working_directory, file_path, content):
    working_dir_path = os.path.abspath(working_directory)
    file_path_abs = os.path.abspath(os.path.join(working_dir_path, file_path))
    dir = os.path.dirname(file_path_abs)

    if not file_path_abs.startswith(working_dir_path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError as e:
        return f'Error: {e}'
    else:
        with open(file_path_abs, 'w') as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

def run_python_file(working_directory, file_path, args=[]):
    working_dir_path = os.path.abspath(working_directory)
    file_path_abs = os.path.abspath(os.path.join(working_dir_path, file_path))
    dir = os.path.dirname(file_path_abs)

    if not file_path_abs.startswith(working_dir_path):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_path_abs):
        return f'Error: File "{file_path}" not found.'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    output = ""

    try:
        command = [ "python3", file_path ] + args
        processes = subprocess.run(command, capture_output=True, text=True, cwd=dir, timeout=30)
    except Exception as e:
        return f"Error: executing Python file: {e}"
    else:
        if not processes.stdout and not processes.stderr:
            return "No output produced"

        output += f'STDOUT: {processes.stdout}\nSTDERR: {processes.stderr}'
        if processes.returncode != 0:
            output += f'\nReturn code: {processes.returncode}'
            return output
        else:
            return output
