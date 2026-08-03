"""
analyze_required_fields_coverage.py - 逐个接口分析必填字段校验覆盖情况
"""

import json
import urllib.request
import os
import re

# 1. 获取 OpenAPI 规范
url = 'http://172.16.1.165:9200/v3/api-docs'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=30) as resp:
    spec = json.loads(resp.read())

paths = spec.get('paths', {})
schemas = spec.get('components', {}).get('schemas', {})

# 2. 收集所有有 requestBody 的 POST 接口
apis = []
for path, methods in paths.items():
    if 'post' not in methods:
        continue
    api = methods['post']
    if not api.get('requestBody'):
        continue
    
    schema_ref = api.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('$ref', '')
    if not schema_ref:
        continue
    
    schema_name = schema_ref.replace('#/components/schemas/', '')
    if schema_name not in schemas:
        continue
    
    schema = schemas[schema_name]
    required = schema.get('required', [])
    properties = schema.get('properties', {})
    optional = [f for f in properties.keys() if f not in required]
    
    apis.append({
        'path': path,
        'method': 'POST',
        'schema': schema_name,
        'required': required,
        'optional': optional,
        'summary': api.get('summary', '')
    })

# 3. 收集所有测试文件中的测试方法
test_methods = {}
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有测试方法名
            matches = re.finditer(r'def (test_\w+)\(self\)', content)
            for match in matches:
                test_name = match.group(1)
                if filepath not in test_methods:
                    test_methods[filepath] = []
                test_methods[filepath].append(test_name)

# 4. 逐个接口分析必填字段测试覆盖情况
print("=" * 100)
print("逐个接口必填字段校验覆盖分析")
print("=" * 100)

uncovered_apis = []

for api in apis:
    path = api['path']
    required = api['required']
    optional = api['optional']
    schema_name = api['schema']
    
    print(f"\n{path}")
    print(f"  Schema: {schema_name}")
    print(f"  必填字段: {required}")
    print(f"  非必填字段: {optional}")
    
    if not required:
        print(f"  状态: 无必填字段")
        continue
    
    # 检查每个必填字段是否有对应的缺失测试
    missing_field_tests = []
    for field in required:
        # 查找是否有测试这个字段缺失的测试方法
        # 模式: test_*_missing_{field} 或 test_*_missing_*
        found = False
        for filepath, methods in test_methods.items():
            for method in methods:
                # 检查测试方法名是否包含字段名
                if field.lower() in method.lower() and 'missing' in method.lower():
                    found = True
                    break
                # 特殊检查: id 字段的测试
                if field == 'id' and ('missing_id' in method.lower() or 'not_exist' in method.lower()):
                    found = True
                    break
            if found:
                break
        
        if not found:
            missing_field_tests.append(field)
    
    if missing_field_tests:
        print(f"  状态: [WARN] 缺少必填字段测试: {missing_field_tests}")
        uncovered_apis.append({
            'path': path,
            'schema': schema_name,
            'required': required,
            'missing_tests': missing_field_tests
        })
    else:
        print(f"  状态: [OK] 必填字段测试已覆盖")

# 5. 汇总
print("\n" + "=" * 100)
print("汇总")
print("=" * 100)

total_apis = len(apis)
covered_apis = total_apis - len(uncovered_apis)
total_required = sum(len(api['required']) for api in apis)
covered_required = total_required - sum(len(api['missing_tests']) for api in uncovered_apis)

print(f"\n总接口数: {total_apis}")
print(f"已覆盖接口数: {covered_apis}")
print(f"未覆盖接口数: {len(uncovered_apis)}")
print(f"\n总必填字段数: {total_required}")
print(f"已测试必填字段数: {covered_required}")
print(f"未测试必填字段数: {total_required - covered_required}")
print(f"\n必填字段校验覆盖率: {covered_required}/{total_required} = {covered_required/total_required*100:.1f}%")

if uncovered_apis:
    print(f"\n未覆盖必填字段的接口:")
    for api in uncovered_apis:
        print(f"  {api['path']} - 缺少: {api['missing_tests']}")
