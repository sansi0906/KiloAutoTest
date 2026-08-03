"""
collect_all_bugs.py - 收集所有失败测试对应的Bug
"""

import os
import re

# 1. backend_bug 测试
backend_bugs = []
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.finditer(r'@pytest\.mark\.backend_bug\s+def (test_\w+)\(self\):\s+"""(.*?)"""', content, re.DOTALL)
            for match in matches:
                backend_bugs.append({
                    'file': filepath,
                    'test_name': match.group(1),
                    'desc': match.group(2).strip()
                })

# 2. security 测试中的失败（知识库SQL/XSS）
security_bugs = []
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'test_security' in filepath or 'TestSecurity' in content:
                matches = re.finditer(r'def (test_sql_injection_knowledge_title|test_xss_knowledge_title|test_xss_content_field)\(self[^)]*\):\s+"""(.*?)"""', content, re.DOTALL)
                for match in matches:
                    security_bugs.append({
                        'file': filepath,
                        'test_name': match.group(1),
                        'desc': match.group(2).strip()
                    })

print("=" * 80)
print("所有后端Bug列表")
print("=" * 80)

print("\n## 1. backend_bug 标记的缺陷（8个）\n")
for i, bug in enumerate(backend_bugs, 1):
    print(f"Bug {i}: {bug['test_name']}")
    print(f"  文件: {bug['file']}")
    print(f"  描述: {bug['desc']}")
    print()

print("\n## 2. 安全漏洞（知识库SQL/XSS，10个参数化用例）\n")
for i, bug in enumerate(security_bugs, 1):
    print(f"Bug {i}: {bug['test_name']}")
    print(f"  文件: {bug['file']}")
    print(f"  描述: {bug['desc']}")
    print()

print(f"\n总计: {len(backend_bugs)} 个后端逻辑Bug + {len(security_bugs)} 个安全漏洞 = {len(backend_bugs) + len(security_bugs)} 个Bug")
