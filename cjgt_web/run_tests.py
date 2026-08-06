"""
超级个体后台管理系统 - 测试主入口
运行智能服务配置和内容管理模块的页面功能测试
生成测试报告
"""
import asyncio
import json
import os
from datetime import datetime
from test_smart_service_config import SmartServiceConfigTests
from test_content_management import ContentManagementTests

REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")


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

    all_results = []

    # 1. 智能服务配置模块测试
    print("\n" + "=" * 60)
    print("运行智能服务配置模块测试")
    print("=" * 60)
    smart_tests = SmartServiceConfigTests()
    smart_results = await smart_tests.run_all()
    all_results.extend(smart_results)

    # 2. 内容管理模块测试
    print("\n" + "=" * 60)
    print("运行内容管理模块测试")
    print("=" * 60)
    content_tests = ContentManagementTests()
    content_results = await content_tests.run_all()
    all_results.extend(content_results)

    # 生成报告
    json_path, md_path = generate_report(all_results)

    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(main())
