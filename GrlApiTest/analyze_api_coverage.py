"""
analyze_api_coverage.py - 分析 API 必填/非必填字段测试覆盖情况
"""

import json
import urllib.request

# Fetch OpenAPI spec
url = 'http://172.16.1.165:9200/v3/api-docs'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=30) as resp:
    spec = json.loads(resp.read())

paths = spec.get('paths', {})
schemas = spec.get('components', {}).get('schemas', {})

print('=' * 80)
print('API 必填/非必填字段校验覆盖分析')
print('=' * 80)

# 定义已有测试覆盖的 API 和字段
tested_apis = {
    # platform_user_module
    '/platform/user/save': ['userName', 'realName', 'sex', 'roleGroupId', 'status'],
    '/platform/user/edit': ['id', 'userName', 'realName', 'sex', 'roleGroupId', 'status'],
    '/platform/user/detail': ['id'],
    '/platform/user/delete': ['id'],
    '/platform/user/changeStatus': ['id', 'status'],
    '/platform/user/resetPwd': ['id'],
    # business_scope_module
    '/platform/businessScope/add': ['scopeName'],
    '/platform/businessScope/edit': ['id', 'scopeName'],
    '/platform/businessScope/del': ['id'],
    '/platform/businessScope/updateStatus': ['id', 'isEnabled'],
    # knowledge_base_module
    '/platform/knowledge/save': ['title', 'content', 'consultType', 'displayPosition', 'applicableArea'],
    '/platform/knowledge/edit': ['id', 'title', 'content', 'consultType', 'displayPosition', 'applicableArea'],
    '/platform/knowledge/detail': ['id'],
    '/platform/knowledge/delete': ['id'],
    '/platform/knowledge/changeStatus': ['id', 'status'],
    # service_item_module
    '/platform/serviceItem/add': ['itemName', 'billingMethod'],
    '/platform/serviceItem/edit': ['id', 'itemName', 'billingMethod'],
    '/platform/serviceItem/updateStatus': ['id', 'isDisplay'],
    # service_provider_module
    '/platform/serverUser/save': ['companyName', 'unifiedSocialCode', 'officeAddress', 'serviceArea', 'contactPerson', 'contactPhone', 'serviceItems'],
    '/platform/serverUser/edit': ['id', 'companyName', 'unifiedSocialCode', 'officeAddress', 'serviceArea', 'contactPerson', 'contactPhone', 'serviceItems'],
    '/platform/serverUser/detail': ['id'],
    '/platform/serverUser/delete': ['id'],
    '/platform/serverUser/changeStatus': ['id', 'status'],
    '/platform/serverUser/resetPwd': ['id'],
    # pricing_module
    '/platform/pricing/updatePricing': ['serviceItemId', 'amount', 'areaList'],
    '/platform/pricing/tree': ['serviceItemId'],
    '/platform/pricing/treeByAreas': ['serviceItemId', 'areaList'],
}

# 分析所有有 requestBody 的 API
for path, methods in paths.items():
    for method, api in methods.items():
        if method not in ['post']:
            continue
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
        
        # 检查是否已测试
        is_tested = path in tested_apis
        tested_fields = tested_apis.get(path, [])
        
        print(f'\n{method.upper()} {path}')
        print(f'  Schema: {schema_name}')
        print(f'  必填字段: {required}')
        print(f'  非必填字段: {optional}')
        
        if is_tested:
            missing_tests = [f for f in required if f not in tested_fields]
            if missing_tests:
                print(f'  [WARN] 缺少必填字段测试: {missing_tests}')
            else:
                print(f'  [OK] 必填字段测试已覆盖')
        else:
            print(f'  [WARN] 未测试')

print('\n' + '=' * 80)
print('统计')
print('=' * 80)

total_required = 0
covered_required = 0
for path, fields in tested_apis.items():
    total_required += len(fields)
    covered_required += len(fields)

print(f'已有测试覆盖的 API 数: {len(tested_apis)}')
print(f'已有测试覆盖的必填字段数: {total_required}')
print(f'覆盖率: {covered_required}/{total_required} = {covered_required/total_required*100:.1f}%')
