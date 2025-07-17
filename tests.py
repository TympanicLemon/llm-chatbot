from functions.get_files_info import get_file_content, write_file

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
print("\n")

print("=== Test Case 5: write_file calculator/lorem.txt ===")
print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
print("\n")

print("=== Test Case 6: write_file calculator/pkg/morelorem.txt ===")
print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
print("\n")

print("=== Test Case 7: write_file calculator//tmp/temp.txt ===")
print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
