"""
init_db_data.py - 初始化 163 MySQL 测试框架数据
===================================================
向 api_definitions、test_data、test_logs 表写入初始数据。
"""

import json
import sys

sys.path.insert(0, ".")

from utils.db_helper import DatabaseHelper
from config import DB_CONFIG


def get_module_id(helper, module_name):
    """获取或创建模块ID"""
    result = helper.fetch_one(
        "SELECT id FROM test_modules WHERE module_name = %s",
        (module_name,)
    )
    if result:
        return result["id"]
    # 如果模块不存在，创建它
    return helper.insert("test_modules", {
        "module_name": module_name,
        "module_desc": module_name
    })


def init_api_definitions(helper):
    """初始化 API 定义数据"""
    print("Initializing api_definitions...")
    
    # 先清空现有数据
    helper.execute("DELETE FROM api_definitions")
    
    modules = {
        "login_module": [
            ("/sys/login", "POST", "用户密码登录", json.dumps({"username": "string", "password": "string", "loginType": 1, "webType": 0}, ensure_ascii=False)),
            ("/sys/logout", "POST", "用户登出", None),
            ("/sys/sendCode", "POST", "发送短信验证码", json.dumps({"phone": "string", "webType": 0}, ensure_ascii=False)),
        ],
        "platform_user_module": [
            ("/platform/sysUser/save", "POST", "保存平台用户", json.dumps({"userName": "string", "realName": "string", "sex": 1, "roleGroupId": 5, "status": 1}, ensure_ascii=False)),
            ("/platform/sysUser/page", "POST", "分页查询平台用户", None),
            ("/platform/sysUser/getUserInfo", "POST", "获取用户详情", None),
            ("/platform/sysUser/edit", "POST", "编辑平台用户", None),
            ("/platform/sysUser/delete", "POST", "删除平台用户", None),
            ("/platform/sysUser/changeStatus", "POST", "修改用户状态", None),
            ("/platform/sysUser/resetPassword", "POST", "重置用户密码", None),
        ],
        "business_scope_module": [
            ("/platform/businessScope/save", "POST", "保存经营范围", json.dumps({"scopeName": "string", "remark": "string"}, ensure_ascii=False)),
            ("/platform/businessScope/page", "POST", "分页查询经营范围", None),
            ("/platform/businessScope/getDetail", "POST", "获取经营范围详情", None),
            ("/platform/businessScope/edit", "POST", "编辑经营范围", None),
            ("/platform/businessScope/updateStatus", "POST", "修改经营范围状态", None),
            ("/platform/businessScope/delete", "POST", "删除经营范围", None),
        ],
        "knowledge_base_module": [
            ("/platform/knowledgeBase/save", "POST", "保存知识库", json.dumps({"title": "string", "content": "string", "consultType": 1, "displayPosition": [0, 1], "applicableArea": [{"code": "string", "name": "string", "level": "string"}]}, ensure_ascii=False)),
            ("/platform/knowledgeBase/page", "POST", "分页查询知识库", None),
            ("/platform/knowledgeBase/getDetail", "POST", "获取知识库详情", None),
            ("/platform/knowledgeBase/edit", "POST", "编辑知识库", None),
            ("/platform/knowledgeBase/changeStatus", "POST", "修改知识库状态", None),
            ("/platform/knowledgeBase/delete", "POST", "删除知识库", None),
        ],
        "service_item_module": [
            ("/platform/serviceItem/save", "POST", "保存服务项目", json.dumps({"itemName": "string", "billingMethod": 1, "subtitle": "string", "itemDesc": "string"}, ensure_ascii=False)),
            ("/platform/serviceItem/page", "POST", "分页查询服务项目", None),
            ("/platform/serviceItem/listDisplay", "POST", "获取展示状态的服务项目列表", None),
            ("/platform/serviceItem/updateStatus", "POST", "修改服务项目展示状态", None),
            ("/platform/serviceItem/edit", "POST", "编辑服务项目", None),
        ],
        "service_provider_module": [
            ("/platform/serverUser/save", "POST", "保存服务商", json.dumps({"companyName": "string", "unifiedSocialCode": "string", "officeAddress": [{"code": "string", "level": "string", "name": "string"}], "serviceArea": [{"code": "string", "level": "string", "name": "string"}], "serviceItems": [1]}, ensure_ascii=False)),
            ("/platform/serverUser/page", "POST", "分页查询服务商", None),
            ("/platform/serverUser/getDetail", "POST", "获取服务商详情", None),
            ("/platform/serverUser/edit", "POST", "编辑服务商", None),
            ("/platform/serverUser/changeStatus", "POST", "修改服务商状态", None),
            ("/platform/serverUser/resetPassword", "POST", "重置服务商密码", None),
            ("/platform/serverUser/delete", "POST", "删除服务商", None),
        ],
        "pricing_module": [
            ("/platform/pricing/importPricing", "POST", "导入服务定价", None),
            ("/platform/pricing/getPricingTree", "POST", "获取服务定价树", None),
            ("/platform/pricing/getPricingTreeByAreas", "POST", "根据区域获取服务定价树", None),
            ("/platform/pricing/updatePricing", "POST", "更新服务定价", None),
        ],
    }
    
    count = 0
    for module_name, apis in modules.items():
        module_id = get_module_id(helper, module_name)
        if not module_id:
            print(f"  Warning: could not create module {module_name}")
            continue
        
        for api_path, api_method, api_desc, request_schema in apis:
            helper.save_api_definition(
                module_id=module_id,
                api_path=api_path,
                api_method=api_method,
                api_desc=api_desc,
                request_schema=request_schema
            )
            count += 1
    
    print(f"  Added {count} API definitions")
    return count


def init_test_data(helper):
    """初始化测试数据"""
    print("Initializing test_data...")
    
    modules = {
        "login_module": [
            ("test_username", "15522719628", "string", "测试登录用户名"),
            ("test_password", "123456", "string", "测试登录密码"),
            ("test_invalid_username", "wrong_user", "string", "无效用户名"),
            ("test_invalid_phone", "12345", "string", "无效手机号"),
            ("test_empty_phone", "", "string", "空手机号"),
        ],
        "platform_user_module": [
            ("test_role_group_id", "5", "string", "默认角色组ID"),
            ("test_user_sex", "1", "string", "默认性别"),
            ("test_user_status", "1", "string", "默认用户状态"),
        ],
        "business_scope_module": [
            ("test_scope_name_prefix", "Scope", "string", "经营范围名称前缀"),
            ("test_scope_remark", "TestRemark", "string", "测试备注"),
        ],
        "knowledge_base_module": [
            ("test_kb_title_prefix", "TestKB", "string", "知识库标题前缀"),
            ("test_kb_content", "TestContent", "string", "测试内容"),
            ("test_kb_consult_type", "1", "string", "咨询类型"),
        ],
        "service_item_module": [
            ("test_item_name_prefix", "Test", "string", "服务项目名称前缀"),
            ("test_item_billing_method", "1", "string", "计费方式"),
        ],
        "service_provider_module": [
            ("test_provider_company_prefix", "测试服务商", "string", "服务商名称前缀"),
            ("test_provider_address_code", "110119000000", "string", "办公地址编码"),
            ("test_provider_area_code", "110000000000", "string", "服务区域编码"),
        ],
        "pricing_module": [
            ("test_pricing_excel", "data/服务定价数据.xlsx", "string", "测试定价数据文件"),
        ],
    }
    
    count = 0
    for module_name, data_items in modules.items():
        module_id = get_module_id(helper, module_name)
        if not module_id:
            print(f"  Warning: could not create module {module_name}")
            continue
        
        for data_key, data_value, data_type, description in data_items:
            helper.save_test_data(
                module_id=module_id,
                data_key=data_key,
                data_value=data_value,
                data_type=data_type,
                description=description
            )
            count += 1
    
    print(f"  Added {count} test data items")
    return count


def init_test_logs(helper):
    """初始化测试日志"""
    print("Initializing test_logs...")
    
    execution_id = "init-execution-001"
    logs = [
        ("INFO", "测试框架初始化完成", "login_module", "test_login_success"),
        ("INFO", "用户登录成功", "login_module", "test_login_success"),
        ("INFO", "测试数据初始化完成", "platform_user_module", "test_save_user_success"),
        ("INFO", "测试用例执行完成", "business_scope_module", "test_add_business_scope_success"),
        ("DEBUG", "API 定义数据已加载", "knowledge_base_module", "test_save_knowledge_success"),
        ("INFO", "服务商数据初始化完成", "service_provider_module", "test_save_service_provider_success"),
        ("INFO", "服务项目数据初始化完成", "service_item_module", "test_add_service_item_success"),
        ("INFO", "定价数据初始化完成", "pricing_module", "test_import_pricing_success"),
    ]
    
    count = 0
    for level, message, module, case_name in logs:
        helper.save_test_log(
            execution_id=execution_id,
            level=level,
            message=message,
            module=module,
            case_name=case_name
        )
        count += 1
    
    print(f"  Added {count} log entries")
    return count


def main():
    print("Initializing 163 MySQL test framework data...")
    print("=" * 50)
    
    helper = DatabaseHelper(DB_CONFIG)
    
    try:
        api_count = init_api_definitions(helper)
        data_count = init_test_data(helper)
        log_count = init_test_logs(helper)
        
        print("=" * 50)
        print(f"Summary:")
        print(f"  API definitions: {api_count}")
        print(f"  Test data items: {data_count}")
        print(f"  Log entries: {log_count}")
        print(f"Total: {api_count + data_count + log_count}")
        print("Initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise


if __name__ == "__main__":
    main()
