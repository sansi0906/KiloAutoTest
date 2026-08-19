import os
import re

def remove_redundant_login(filepath):
    """移除测试方法中冗余的 login/set_token 调用"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    removed_count = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a test method definition
        if re.match(r'\s+def test_', line):
            # We're in a test method, skip lines until next method or class
            method_start = i
            method_lines = []
            j = i
            while j < len(lines):
                if j > method_start and re.match(r'\s+def ', lines[j]) and not re.match(r'\s+def test_', lines[j]):
                    break
                method_lines.append(lines[j])
                j += 1

            # Process method lines to remove redundant login
            cleaned_method = []
            k = 0
            while k < len(method_lines):
                current_line = method_lines[k]
                # Check for token = self.login() pattern
                if re.match(r'\s+token\s*=\s*self\.login\(\)', current_line):
                    # Check if next line is self.client.set_token(token)
                    if k + 1 < len(method_lines) and re.match(r'\s+self\.client\.set_token\(token\)', method_lines[k + 1]):
                        # Remove both lines
                        removed_count += 1
                        k += 2
                        continue
                cleaned_method.append(current_line)
                k += 1

            new_lines.extend(cleaned_method)
            i = j
        else:
            new_lines.append(line)
            i += 1

    if removed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Removed {removed_count} redundant login calls from {filepath}")

    return removed_count

# Process all test files
test_files = []
for root, dirs, files in os.walk('test_cases'):
    for f in files:
        if f.startswith('test_') and f.endswith('.py'):
            test_files.append(os.path.join(root, f))

total_removed = 0
for filepath in test_files:
    removed = remove_redundant_login(filepath)
    total_removed += removed

print(f"\nTotal redundant login calls removed: {total_removed}")
