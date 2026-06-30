"""
运行测试并生成报告的主脚本
用法:
    python run_tests.py --tester "测试人员姓名" --remark "测试备注"
    python run_tests.py --screenshot-all  # 对所有测试截图
"""
import os
import sys
import subprocess
import argparse
import shutil
import datetime
from pathlib import Path


def clean_reports(reports_dir: str) -> None:
    """清理旧的报告文件"""
    print("清理旧报告...")
    
    # 清理 Allure 结果
    allure_results = os.path.join(reports_dir, "allure-results")
    if os.path.exists(allure_results):
        shutil.rmtree(allure_results)
    os.makedirs(allure_results, exist_ok=True)
    
    # 保留截图文件夹结构，不删除旧的截图文件夹


def run_tests(tester: str = "", remark: str = "", screenshot_all: bool = False, 
              reports_dir: str = "", viewport_width: int = 1920, viewport_height: int = 1080,
              test_url: str = "") -> int:
    """运行测试"""
    print("\n" + "=" * 60)
    print("开始运行测试...")
    if screenshot_all:
        print("截图模式: 全部测试截图")
    if test_url:
        print(f"测试地址: {test_url}")
    print(f"视口尺寸: {viewport_width}x{viewport_height}")
    print("=" * 60 + "\n")
    
    # 生成报告名称（用于创建截图文件夹）
    report_name = f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 设置环境变量，传递报告名称给 pytest
    env = os.environ.copy()
    env["REPORT_NAME"] = report_name
    env["SCREENSHOT_DIR"] = os.path.join(reports_dir, "screenshots", report_name)
    
    # 构建 pytest 命令
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--alluredir", os.path.join(reports_dir, "allure-results"),
        "--viewport-width", str(viewport_width),
        "--viewport-height", str(viewport_height),
    ]
    
    # 添加自定义参数
    if tester:
        cmd.extend(["--tester", tester])
    if remark:
        cmd.extend(["--remark", remark])
    if screenshot_all:
        cmd.append("--screenshot-all")
    if test_url:
        cmd.extend(["--test-url", test_url])
    
    # 运行测试（传递环境变量）
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__), env=env)
    
    return result.returncode


def generate_html_report(tester: str = "", remark: str = "", reports_dir: str = "") -> str:
    """生成 HTML 报告"""
    print("\n" + "=" * 60)
    print("生成测试报告...")
    print("=" * 60 + "\n")
    
    # 导入报告生成器
    from generate_report import TestReportGenerator
    
    generator = TestReportGenerator(reports_dir)
    generator.parse_allure_results()
    
    output_file = generator.generate_html_report(
        tester=tester,
        remark=remark
    )
    
    return output_file


def open_report(report_file: str) -> None:
    """打开报告"""
    import webbrowser
    print(f"\n正在打开报告: {report_file}")
    webbrowser.open(f"file://{os.path.abspath(report_file)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="运行测试并生成报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python run_tests.py
    python run_tests.py --tester "张三" --remark "冒烟测试"
    python run_tests.py --screenshot-all  # 对所有测试截图
    python run_tests.py --no-open  # 不自动打开报告
    python run_tests.py --viewport-width 1366 --viewport-height 768  # 设置视口尺寸
    python run_tests.py --test-url "http://172.16.1.165:3200/"  # 指定测试地址
        """
    )
    
    parser.add_argument("--tester", default="", help="测试人员姓名")
    parser.add_argument("--remark", default="", help="测试备注信息")
    parser.add_argument("--screenshot-all", action="store_true", default=False,
                        help="对所有测试截图（包括通过的测试）")
    parser.add_argument("--no-clean", action="store_true", help="不清理旧报告")
    parser.add_argument("--no-open", action="store_true", help="不自动打开报告")
    parser.add_argument("--reports-dir", default=None, help="报告目录")
    parser.add_argument("--viewport-width", type=int, default=1920, 
                        help="浏览器视口宽度，默认1920")
    parser.add_argument("--viewport-height", type=int, default=1080, 
                        help="浏览器视口高度，默认1080")
    parser.add_argument("--test-url", default="", 
                        help="测试地址，默认使用配置文件中的地址")
    
    args = parser.parse_args()
    
    # 设置报告目录
    script_dir = os.path.dirname(__file__)
    reports_dir = args.reports_dir or os.path.join(script_dir, "reports")
    
    # 清理旧报告
    if not args.no_clean:
        clean_reports(reports_dir)
    
    # 运行测试
    exit_code = run_tests(
        tester=args.tester,
        remark=args.remark,
        screenshot_all=args.screenshot_all,
        reports_dir=reports_dir,
        viewport_width=args.viewport_width,
        viewport_height=args.viewport_height,
        test_url=args.test_url
    )
    
    # 生成报告
    report_file = generate_html_report(
        tester=args.tester,
        remark=args.remark,
        reports_dir=reports_dir
    )
    
    # 打开报告
    if not args.no_open and report_file:
        open_report(report_file)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print(f"报告路径: {report_file}")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
