from functions.get_files_info import get_file_content

print("=== Test Case 1: calculator/main.py ===")
print(get_file_content("calculator", "main.py"))
print("\n")

print("=== Test Case 2: calculator/pkg/calculator.py ===")
print(get_file_content("calculator", "pkg/calculator.py"))
print("\n")

print("=== Test Case 3: calculator//bin/cat ===")
print(get_file_content("calculator", "/bin/cat"))
print("\n")

print("=== Test Case 4: calculator/pkg/does_not_exist.py ===")
print(get_file_content("calculator", "pkg/does_not_exist.py"))
