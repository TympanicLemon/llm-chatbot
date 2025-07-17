import os

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
