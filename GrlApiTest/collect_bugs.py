"""
collect_bugs.py - 收集所有后端Bug测试
"""

import os
import re

bug_tests = []
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.finditer(r'@pytest\.mark\.backend_bug\s+def (test_\w+)\(self\):\s+"""(.*?)"""', content, re.DOTALL)
            for match in matches:
                bug_tests.append({
                    'file': filepath,
                    'test_name': match.group(1),
                    'desc': match.group(2).strip()
                })

print(f'找到 {len(bug_tests)} 个 backend_bug 测试:')
for bug in bug_tests:
    print(f"  {bug['file']}::{bug['test_name']}")
    print(f"    描述: {bug['desc']}")
    print()
