"""
check_missing_tests.py - 精确统计每个接口缺少的必填字段测试
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

# 收集所有测试方法
test_methods = {}
for root, dirs, files in os.walk('test_cases'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.finditer(r'def (test_\w+)\(self\)', content)
            for match in matches:
                test_name = match.group(1)
                if filepath not in test_methods:
                    test_methods[filepath] = []
                test_methods[filepath].append(test_name)

# 检查每个接口的必填字段是否有对应的缺失测试
print("=" * 100)
print("每个接口必填字段缺失测试覆盖情况")
print("=" * 100)

total_missing = 0
missing_details = []

for api_path, required_fields in api_required_fields.items():
    missing_fields = []
    
    for field in required_fields:
        # 查找是否有测试这个字段缺失的测试方法
        found = False
        
        # 模式1: test_*_missing_{field}
        # 模式2: test_*_missing_* (包含字段名)
        # 模式3: 对于 id 字段，检查是否有 missing_id 或 not_exist
        
        field_lower = field.lower()
        
        for filepath, methods in test_methods.items():
            for method in methods:
                method_lower = method.lower()
                
                # 精确匹配: missing_{field}
                if f'missing_{field_lower}' in method_lower:
                    found = True
                    break
                
                # 对于 id 字段，not_exist 也算
                if field_lower == 'id' and ('missing_id' in method_lower or 'not_exist' in method_lower):
                    found = True
                    break
                
                # 特殊映射
                field_aliases = {
                    'userName': ['user_name', 'username'],
                    'realName': ['real_name'],
                    'roleGroupId': ['role_group_id', 'rolegroupid'],
                    'billingMethod': ['billing_method'],
                    'isDisplay': ['is_display', 'isdisplay'],
                    'isEnabled': ['is_enabled', 'isenabled'],
                    'serviceItemId': ['service_item_id'],
                    'areaList': ['area_list'],
                    'consultType': ['consult_type'],
                    'displayPosition': ['display_position'],
                    'applicableArea': ['applicable_area'],
                    'contactPerson': ['contact_person'],
                    'contactPhone': ['contact_phone'],
                    'officeAddress': ['office_address'],
                    'serviceArea': ['service_area'],
                    'serviceItems': ['service_items'],
                    'unifiedSocialCode': ['unified_social_code'],
                    'workerPhone': ['worker_phone'],
                    'signerIdCard': ['signer_id_card'],
                    'signerMobile': ['signer_mobile'],
                    'signerName': ['signer_name'],
                    'stationInfoId': ['station_info_id'],
                    'stationInfoName': ['station_info_name'],
                    'cityAreaCode': ['city_area_code'],
                    'provinceAreaCode': ['province_area_code'],
                    'sourceType': ['source_type'],
                    'userUuid': ['user_uuid'],
                    'certNum': ['cert_num'],
                    'certFrontPhoto': ['cert_front_photo'],
                    'certBackPhoto': ['cert_back_photo'],
                    'validStartDate': ['valid_start_date'],
                    'validEndDate': ['valid_end_date'],
                    'verifyDate': ['verify_date'],
                    'agencyLicenseUrl': ['agency_license_url'],
                    'agencyPlatformScreenshotUrl': ['agency_platform_screenshot_url'],
                    'taxCreditScreenshotUrl': ['tax_credit_screenshot_url'],
                    'annualInspectionUrl': ['annual_inspection_url'],
                    'businessLicenseUrl': ['business_license_url'],
                    'parentId': ['parent_id'],
                    'menuName': ['menu_name'],
                    'menuType': ['menu_type'],
                    'routeUrl': ['route_url'],
                    'componentPath': ['component_path'],
                    'componentName': ['component_name'],
                    'orderNum': ['order_num'],
                    'keepAlive': ['keep_alive'],
                    'permsType': ['perms_type'],
                    'frameSrc': ['frame_src'],
                    'districtAreaCode': ['district_area_code'],
                    'nationCode': ['nation_code'],
                }
                
                aliases = field_aliases.get(field, [])
                for alias in aliases:
                    if f'missing_{alias}' in method_lower:
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
