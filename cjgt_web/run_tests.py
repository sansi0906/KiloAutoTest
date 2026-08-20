"""
超级个体后台管理系统 - 测试主入口
运行智能服务配置和内容管理模块的页面功能测试
生成测试报告

优化说明:
  - 共享单个浏览器实例（只启动一次 Chromium 浏览器）
  - 登录一次，所有模块复用登录状态，避免重复打开浏览器
  - 按模块顺序执行测试用例
"""
import asyncio
import json
import os
from datetime import datetime
from test_smart_service_config import SmartServiceConfigTests
from test_content_management import ContentManagementTests
from test_provider_management import ProviderManagementTests
from test_customer_management import CustomerManagementTests
from test_order_contract_management import OrderManagementTests, ContractManagementTests
from test_base import TestBase, SCREENSHOT_DIR

REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

# 测试用例清单（按模块归类、按先后顺序）
TEST_CASES = {
    "智能服务配置": [
        ("服务项目配置", "test_project_config_page_load"),
        ("服务项目配置", "test_project_config_search"),
        ("服务项目配置", "test_project_config_search_reset"),
        ("服务项目配置", "test_project_config_billing_method_filter"),
        ("服务项目配置", "test_project_config_display_status_filter"),
        ("服务项目配置", "test_project_config_date_range_filter"),
        ("服务项目配置", "test_project_config_add_form_validation"),
        ("服务项目配置", "test_project_config_add_with_data"),
        ("服务项目配置", "test_project_config_edit"),
        ("服务项目配置", "test_project_config_toggle_display"),
        ("服务项目配置", "test_project_config_pagination"),
        ("服务定价配置", "test_project_price_page_load"),
        ("服务定价配置", "test_project_price_region_filter"),
        ("服务定价配置", "test_project_price_price_data_verification"),
        ("服务定价配置", "test_project_price_edit_price"),
        ("服务定价配置", "test_project_price_download_template"),
        ("合同服务配置", "test_contract_service_page_load"),
        ("合同服务配置", "test_contract_service_search"),
        ("合同服务配置", "test_contract_service_project_filter"),
        ("合同服务配置", "test_contract_service_add_form"),
        ("合同服务配置", "test_contract_service_add_with_data"),
        ("合同服务配置", "test_contract_service_edit"),
        ("合同服务配置", "test_contract_service_delete_confirm"),
        ("合同服务配置", "test_contract_service_pagination"),
    ],
    "内容管理": [
        ("知识库", "test_knowledge_page_load"),
        ("知识库", "test_knowledge_search_by_title"),
        ("知识库", "test_knowledge_search_reset"),
        ("知识库", "test_knowledge_search_by_location"),
        ("知识库", "test_knowledge_search_by_type"),
        ("知识库", "test_knowledge_search_by_status"),
        ("知识库", "test_knowledge_add_form_validation"),
        ("知识库", "test_knowledge_add_with_data"),
        ("知识库", "test_knowledge_detail_view"),
        ("知识库", "test_knowledge_edit"),
        ("知识库", "test_knowledge_disable"),
        ("知识库", "test_knowledge_table_pagination"),
    ],
    "服务商管理": [
        ("代理记账公司管理", "test_provider_page_load"),
        ("代理记账公司管理", "test_provider_search"),
        ("代理记账公司管理", "test_provider_search_reset"),
        ("代理记账公司管理", "test_provider_add_form_validation"),
        ("代理记账公司管理", "test_provider_add_with_license"),
        ("代理记账公司管理", "test_provider_edit"),
        ("代理记账公司管理", "test_provider_detail"),
        ("代理记账公司管理", "test_provider_disable"),
        ("代理记账公司管理", "test_provider_reset_password"),
        ("代理记账公司管理", "test_provider_pagination"),
    ],
    "客户管理": [
        ("超级个体档案", "test_customer_archive_page_load"),
        ("超级个体档案", "test_customer_archive_search"),
        ("超级个体档案", "test_customer_archive_search_reset"),
        ("超级个体档案", "test_customer_archive_detail"),
        ("超级个体档案", "test_customer_archive_view_contract"),
        ("超级个体档案", "test_customer_archive_pagination"),
        ("服务工单管理", "test_work_order_page_load"),
        ("服务工单管理", "test_work_order_search"),
        ("服务工单管理", "test_work_order_search_reset"),
        ("服务工单管理", "test_work_order_detail"),
        ("服务工单管理", "test_work_order_pagination"),
    ],
    "订单管理": [
        ("订单管理", "test_order_page_load"),
        ("订单管理", "test_order_search"),
        ("订单管理", "test_order_search_reset"),
        ("订单管理", "test_order_filter_by_payment_status"),
        ("订单管理", "test_order_filter_by_source"),
        ("订单管理", "test_order_filter_by_date_range"),
        ("订单管理", "test_order_combined_filter"),
        ("订单管理", "test_order_detail"),
        ("订单管理", "test_order_pagination"),
    ],
    "合同管理": [
        ("合同管理", "test_contract_page_load"),
        ("合同管理", "test_contract_search"),
        ("合同管理", "test_contract_search_reset"),
        ("合同管理", "test_contract_filter_by_party_a_name"),
        ("合同管理", "test_contract_filter_by_validity_date"),
        ("合同管理", "test_contract_combined_filter"),
        ("合同管理", "test_contract_expand"),
        ("合同管理", "test_contract_agreement_button_exists"),
        ("合同管理", "test_contract_agreement_opens_new_tab"),
        ("合同管理", "test_contract_agreement_returns_to_list"),
        ("合同管理", "test_contract_pagination"),
    ],
}


def print_test_plan():
    """打印测试用例清单"""
    print("\n" + "=" * 60)
    print("测试用例清单（按模块归类）")
    print("=" * 60)
    idx = 0
    for module, cases in TEST_CASES.items():
        print(f"\n  [{module}]")
        for sub_module, case_name in cases:
            idx += 1
            # 查找对应方法的docstring
            print(f"    {idx:2d}. {case_name}")
    print(f"\n  总计: {sum(len(c) for c in TEST_CASES.values())} 个测试用例")
    print()


def generate_report(all_results):
    """生成测试报告"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 统计
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    failed = sum(1 for r in all_results if not r["passed"])
    pass_rate = f"{passed/total*100:.1f}%" if total > 0 else "0%"

    # 按模块分组
    modules = {}
    for r in all_results:
        module = r["module"]
        if module not in modules:
            modules[module] = {"total": 0, "passed": 0, "failed": 0, "tests": []}
        modules[module]["total"] += 1
        if r["passed"]:
            modules[module]["passed"] += 1
        else:
            modules[module]["failed"] += 1
        modules[module]["tests"].append(r)

    # 生成JSON报告
    json_report = {
        "test_time": timestamp,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
        },
        "modules": modules,
    }
    json_path = os.path.join(REPORT_DIR, f"test_report_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)

    # 生成Markdown报告
    md_lines = [
        f"# 超级个体后台管理系统 - 测试报告",
        f"",
        f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"**测试环境:** http://172.16.1.165:9100",
        f"",
        f"## 测试概览",
        f"",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 测试总数 | {total} |",
        f"| 通过 | {passed} |",
        f"| 失败 | {failed} |",
        f"| 通过率 | {pass_rate} |",
        f"",
    ]

    for module_name, module_data in modules.items():
        md_lines.append(f"## {module_name}")
        md_lines.append(f"")
        md_lines.append(f"- 总数: {module_data['total']}")
        md_lines.append(f"- 通过: {module_data['passed']}")
        md_lines.append(f"- 失败: {module_data['failed']}")
        md_lines.append(f"")
        md_lines.append(f"| 测试项 | 结果 | 预期 | 实际 |")
        md_lines.append(f"|--------|------|------|------|")
        for test in module_data["tests"]:
            status = "PASS" if test["passed"] else "FAIL"
            expected = test["expected"].replace("|", "\\|")
            actual = test["actual"].replace("|", "\\|")
            md_lines.append(f"| {test['test_name']} | {status} | {expected} | {actual} |")
        md_lines.append(f"")

    md_path = os.path.join(REPORT_DIR, f"test_report_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # 打印摘要
    print("\n" + "=" * 60)
    print("测试报告摘要")
    print("=" * 60)
    print(f"测试总数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {pass_rate}")
    print()
    for module_name, module_data in modules.items():
        print(f"  {module_name}: {module_data['passed']}/{module_data['total']}")
    print()
    print(f"JSON报告: {json_path}")
    print(f"MD报告: {md_path}")

    return json_path, md_path


async def main():
    print("=" * 60)
    print("超级个体后台管理系统 - 页面功能测试")
    print("=" * 60)

    # 打印测试用例清单
    print_test_plan()

    # 共享浏览器实例 — 只启动一次，所有模块复用
    base = TestBase()
    await base.setup()

    all_results = []

    try:
        # 登录一次 — 所有模块共享登录状态
        print("登录系统...")
        await base.login()
        print("登录成功！\n")

        # 1. 智能服务配置模块测试
        print("=" * 60)
        print("运行智能服务配置模块测试")
        print("=" * 60)
        smart = SmartServiceConfigTests()
        smart_results = await smart.run_all(base=base)
        all_results.extend(smart_results)

        # 2. 内容管理模块测试
        print("\n" + "=" * 60)
        print("运行内容管理模块测试")
        print("=" * 60)
        content = ContentManagementTests()
        content_results = await content.run_all(base=base)
        all_results.extend(content_results)

        # 3. 服务商管理模块测试
        print("\n" + "=" * 60)
        print("运行服务商管理模块测试")
        print("=" * 60)
        provider = ProviderManagementTests()
        provider_results = await provider.run_all(base=base)
        all_results.extend(provider_results)

        # 4. 客户管理模块测试
        print("\n" + "=" * 60)
        print("运行客户管理模块测试")
        print("=" * 60)
        customer = CustomerManagementTests()
        customer_results = await customer.run_all(base=base)
        all_results.extend(customer_results)

        # 5. 订单管理模块测试
        print("\n" + "=" * 60)
        print("运行订单管理模块测试")
        print("=" * 60)
        order = OrderManagementTests()
        order_results = await order.run_all(base=base)
        all_results.extend(order_results)

        # 6. 合同管理模块测试
        print("\n" + "=" * 60)
        print("运行合同管理模块测试")
        print("=" * 60)
        contract = ContractManagementTests()
        contract_results = await contract.run_all(base=base)
        all_results.extend(contract_results)

        # 生成报告
        generate_report(all_results)

        print("\n测试完成!")
    finally:
        await base.teardown()


if __name__ == "__main__":
    asyncio.run(main())
