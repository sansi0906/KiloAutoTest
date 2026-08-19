"""
run_tests.py - 运行测试并生成 Allure 报告
"""

import datetime
import os
import sys
import subprocess

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

reports_dir = "reports"
allure_results = os.path.join(reports_dir, f"allure-results_{timestamp}")
allure_report = os.path.join(reports_dir, f"allure-report_{timestamp}")

os.makedirs(reports_dir, exist_ok=True)

cmd = [
    sys.executable, "-m", "pytest",
    "test_cases",
    f"--alluredir={allure_results}",
]

print(f"时间戳: {timestamp}")
print(f"Allure 结果目录: {allure_results}")
print(f"Allure 报告目录: {allure_report}")
print(f"\n执行命令: {' '.join(cmd)}\n")

result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

if result.returncode == 0 or result.returncode == 1:
    print(f"\n生成 Allure 报告...")
    subprocess.run([
        "allure", "generate", allure_results,
        "-o", allure_report,
        "--clean",
    ])
    print(f"\n报告已生成: {allure_report}")
    print(f"可用以下命令查看: allure open {allure_report}")

    report_md = os.path.join(reports_dir, f"test_report_{timestamp}.md")
    with open(report_md, "w", encoding="utf-8") as f:
        f.write(f"# 测试报告 {timestamp}\n\n")
        f.write(f"- Allure 报告: `{allure_report}`\n")
        f.write(f"- 结果目录: `{allure_results}`\n")
        f.write(f"- 查看命令: `allure open {allure_report}`\n")

sys.exit(result.returncode)
