"""
final_check.py - 最终精确检查缺失的必填字段测试
"""

import os
import re

# 定义接口和其必填字段（基于OpenAPI规范）
api_required_fields = {
    '/sys/sendCode': ['phone', 'webType'],
    '/sys/login': ['loginType', 'password', 'smsCode', 'username', 'webType'],
    '/platform/user/save': ['userName', 'realName', 'sex', 'roleGroupId', 'status'],
    '/platform/user/edit': ['id', 'userName', 'realName', 'sex', 'roleGroupId', 'status'],
    '/platform/user/detail': ['id'],
    '/platform/user/delete': ['id'],
    '/platform/user/changeStatus': ['id', 'status'],
    '/platform/user/resetPwd': ['id'],
    '/platform/serviceItem/add': ['itemName', 'billingMethod'],
    '/platform/serviceItem/edit': ['id', 'itemName', 'billingMethod'],
    '/platform/serviceItem/updateStatus': ['id', 'isDisplay'],
    '/platform/serverUser/save': ['companyName', 'unifiedSocialCode', 'officeAddress', 'serviceArea', 'contactPerson', 'contactPhone', 'serviceItems'],
    '/platform/serverUser/edit': ['id', 'companyName', 'unifiedSocialCode', 'officeAddress', 'serviceArea', 'contactPerson', 'contactPhone', 'serviceItems'],
    '/platform/serverUser/detail': ['id'],
    '/platform/serverUser/delete': ['id'],
    '/platform/serverUser/changeStatus': ['id', 'status'],
    '/platform/serverUser/resetPwd': ['id'],
    '/platform/pricing/updatePricing': ['serviceItemId', 'amount', 'areaList'],
    '/platform/pricing/tree': ['serviceItemId'],
    '/platform/pricing/treeByAreas': ['serviceItemId', 'areaList'],
    '/platform/knowledge/save': ['title', 'content', 'consultType', 'displayPosition', 'applicableArea'],
    '/platform/knowledge/edit': ['id', 'title', 'content', 'consultType', 'displayPosition', 'applicableArea'],
    '/platform/knowledge/detail': ['id'],
    '/platform/knowledge/delete': ['id'],
    '/platform/knowledge/changeStatus': ['id', 'status'],
    '/platform/businessScope/add': ['scopeName'],
    '/platform/businessScope/edit': ['id', 'scopeName'],
    '/platform/businessScope/del': ['id'],
    '/platform/businessScope/updateStatus': ['id', 'isEnabled'],
}

# 收集所有测试方法及其内容
test_methods = {}
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.finditer(r'def (test_\w+)\(self\):\s+"""(.*?)"""', content, re.DOTALL)
            for match in matches:
                test_name = match.group(1)
                test_desc = match.group(2).strip()
                if filepath not in test_methods:
                    test_methods[filepath] = []
                test_methods[filepath].append({
                    'name': test_name,
                    'desc': test_desc,
                    'content': content
                })

# 检查每个接口的必填字段是否有对应的缺失测试
print("=" * 100)
print("最终精确必填字段缺失测试覆盖分析")
print("=" * 100)

missing_tests = []

for api_path, required_fields in api_required_fields.items():
    missing_fields = []
    
    for field in required_fields:
        found = False
        
        for filepath, methods in test_methods.items():
            for method in methods:
                method_name = method['name'].lower()
                method_desc = method['desc'].lower()
                content = method['content'].lower()
                field_lower = field.lower()
                
                # 检查测试是否针对这个字段的缺失/空值
                # 方法名包含字段名，且描述或方法名包含缺失相关关键词
                has_field = field_lower in method_name or field_lower in method_desc
                has_missing_keyword = (
                    'missing' in method_name or 
                    'empty' in method_name or 
                    'null' in method_name or 
                    'not_exist' in method_name or 
                    'non_existing' in method_name or
                    'without' in method_name or
                    'invalid' in method_name
                )
                
                # 特殊检查：如果测试内容中确实发送了该字段的空值
                if has_field and not has_missing_keyword:
                    # 检查测试方法体中是否发送了该字段的空值
                    # 例如：user_name="" 或 user_name=None
                    field_patterns = [
                        f'{field_lower}.*=.*""',
                        f'{field_lower}.*=.*None',
                        f'{field_lower}.*=.*null',
                    ]
                    for pattern in field_patterns:
                        if re.search(pattern, content):
                            has_missing_keyword = True
                            break
                
                if has_field and has_missing_keyword:
                    found = True
                    break
            
            if found:
                break
        
        if not found:
            missing_fields.append(field)
    
    if missing_fields:
        missing_tests.append({
            'path': api_path,
            'missing': missing_fields
        })

print(f"\n缺少必填字段缺失测试的接口: {len(missing_tests)} 个")
total_missing = sum(len(item['missing']) for item in missing_tests)
print(f"缺少的必填字段总数: {total_missing} 个")
print()
for item in missing_tests:
    print(f"  {item['path']}")
    print(f"    缺少: {item['missing']}")
    print()
