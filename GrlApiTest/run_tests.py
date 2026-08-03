"""
run_tests.py - 运行测试并生成带时间戳的报告
"""

import datetime
import os
import sys
import subprocess

# 生成时间戳
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 报告目录
reports_dir = "reports"
allure_results = os.path.join(reports_dir, f"allure-results_{timestamp}")
allure_report = os.path.join(reports_dir, f"allure-report_{timestamp}")
coverage_dir = os.path.join(reports_dir, f"coverage_{timestamp}")

# 确保 reports 目录存在
os.makedirs(reports_dir, exist_ok=True)

# 构建 pytest 命令
cmd = [
    sys.executable, "-m", "pytest",
    "-v",
    "--alluredir", allure_results,
    "--cov=api_clients",
    "--cov=utils",
    "--cov-report=term-missing",
    "--cov-report=html:" + coverage_dir,
    "test_cases",
]

print(f"时间戳: {timestamp}")
print(f"Allure 结果目录: {allure_results}")
print(f"Allure 报告目录: {allure_report}")
print(f"Coverage 报告目录: {coverage_dir}")
print(f"\n执行命令: {' '.join(cmd)}\n")

# 执行 pytest
result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

# 生成 allure 报告
if result.returncode == 0 or result.returncode == 1:  # 0=成功, 1=部分测试失败
    print(f"\n生成 Allure 报告...")
    subprocess.run([
        "allure", "generate", allure_results,
        "-o", allure_report,
        "--clean",
    ])
    print(f"\n报告已生成: {allure_report}")
    print(f"可用以下命令查看: allure open {allure_report}")

sys.exit(result.returncode)
