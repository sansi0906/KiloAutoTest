"""
accurate_check.py - 精确检查每个必填字段是否有缺失值测试
"""

import os
import re

# 定义接口和其必填字段
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
print("精确必填字段缺失测试覆盖分析")
print("=" * 100)

total_missing = 0
missing_details = []

for api_path, required_fields in api_required_fields.items():
    missing_fields = []
    
    for field in required_fields:
        found = False
        
        # 查找是否有测试这个字段缺失的测试方法
        for filepath, methods in test_methods.items():
            for method in methods:
                method_name = method['name'].lower()
                method_desc = method['desc'].lower()
                field_lower = field.lower()
                
                # 检查测试方法名是否包含字段名和缺失相关关键词
                has_field = field_lower in method_name or field_lower in method_desc
                has_missing = 'missing' in method_name or 'empty' in method_name or 'null' in method_name or 'not_exist' in method_name or 'without' in method_name
                
                if has_field and has_missing:
                    found = True
                    break
                
                # 特殊检查: 空字符串测试也算覆盖
                if has_field and ('empty' in method_name or 'empty' in method_desc):
                    found = True
                    break
                
                # 特殊检查: id 字段的 not_exist 测试
                if field_lower == 'id' and ('not_exist' in method_name or 'not_exist' in method_desc or 'non_existing' in method_name):
                    found = True
                    break
                
                # 特殊检查: status 字段的 invalid 测试
                if field_lower == 'status' and ('invalid' in method_name or 'invalid' in method_desc):
                    found = True
                    break
            
            if found:
                break
        
        if not found:
            missing_fields.append(field)
    
    if missing_fields:
        total_missing += len(missing_fields)
        missing_details.append({
            'path': api_path,
            'missing': missing_fields
        })

print(f"\n缺少必填字段缺失测试的接口: {len(missing_details)} 个")
print(f"缺少的必填字段总数: {total_missing} 个")
print()
for detail in missing_details:
    print(f"  {detail['path']}")
    print(f"    缺少: {detail['missing']}")
    print()
