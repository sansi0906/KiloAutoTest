"""
compare_bugs.py - 缺陷对比分析脚本

功能：
1. 对比所有缺陷是否都已提交云效
2. 对比所有缺陷是否已修复
3. 生成对比报告

用法：
    python bugs/compare_bugs.py
    python bugs/compare_bugs.py --execution-id exec_20260731
    python bugs/compare_bugs.py --fix-status
"""

import json
import os
import sys
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUGS_DIR = os.path.join(PROJECT_ROOT, "bugs")
TRACKING_FILE = os.path.join(BUGS_DIR, "bug_tracking.json")
REPORTS_DIR = os.path.join(BUGS_DIR, "reports")


def load_tracking():
    """加载缺陷跟踪主文件"""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {}, "executions": [], "bugs": [], "summary": {}}


def compare_yunxiao_submission(data, execution_id=None):
    """对比所有缺陷的云效提交状态"""
    bugs = data.get("bugs", [])

    # 筛选指定执行的缺陷
    if execution_id:
        bugs = [b for b in bugs if b.get("execution_id") == execution_id]

    submitted = []
    not_submitted = []

    for bug in bugs:
        yx = bug.get("yunxiao", {})
        if yx.get("submitted"):
            submitted.append(bug)
        else:
            not_submitted.append(bug)

    return submitted, not_submitted


def compare_fix_status(data, execution_id=None):
    """对比所有缺陷的修复状态"""
    bugs = data.get("bugs", [])

    # 筛选指定执行的缺陷
    if execution_id:
        bugs = [b for b in bugs if b.get("execution_id") == execution_id]

    fixed = []
    unfixed = []
    verified = []

    for bug in bugs:
        fix = bug.get("fix", {})
        if fix.get("verified"):
            verified.append(bug)
        elif fix.get("fixed"):
            fixed.append(bug)
        else:
            unfixed.append(bug)

    return fixed, unfixed, verified


def generate_comparison_report(data, execution_id=None):
    """生成对比分析报告"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    bugs = data.get("bugs", [])
    if execution_id:
        bugs = [b for b in bugs if b.get("execution_id") == execution_id]

    # 云效提交对比
    submitted, not_submitted = compare_yunxiao_submission(data, execution_id)

    # 修复状态对比
    fixed, unfixed, verified = compare_fix_status(data, execution_id)

    # 获取执行信息
    execution = None
    if execution_id:
        execution = next((e for e in data.get("executions", []) if e["execution_id"] == execution_id), None)
    else:
        execution = data.get("executions", [])[-1] if data.get("executions") else None

    # 生成报告内容
    report_lines = []
    report_lines.append(f"# 缺陷对比分析报告")
    report_lines.append(f"")
    report_lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if execution:
        report_lines.append(f"> 执行批次：{execution.get('execution_id', 'unknown')}")
        report_lines.append(f"> 测试日期：{execution.get('date', 'unknown')}")
        report_lines.append(f"> 测试环境：{execution.get('environment', 'unknown')}")
    report_lines.append(f"")
    report_lines.append(f"---")
    report_lines.append(f"")

    # 汇总统计
    total = len(bugs)
    report_lines.append(f"## 📊 汇总统计")
    report_lines.append(f"")
    report_lines.append(f"| 指标 | 数量 | 占比 |")
    report_lines.append(f"|------|------|------|")
    report_lines.append(f"| 总缺陷数 | {total} | 100% |")
    report_lines.append(f"| 已提交云效 | {len(submitted)} | {len(submitted)/total*100:.1f}% |")
    report_lines.append(f"| 未提交云效 | {len(not_submitted)} | {len(not_submitted)/total*100:.1f}% |")
    report_lines.append(f"| 已修复 | {len(fixed)} | {len(fixed)/total*100:.1f}% |")
    report_lines.append(f"| 已验证 | {len(verified)} | {len(verified)/total*100:.1f}% |")
    report_lines.append(f"| 未修复 | {len(unfixed)} | {len(unfixed)/total*100:.1f}% |")
    report_lines.append(f"")

    # 云效提交详情
    report_lines.append(f"## 📋 云效提交状态详情")
    report_lines.append(f"")
    if not_submitted:
        report_lines.append(f"### ❌ 未提交云效的缺陷 ({len(not_submitted)} 个)")
        report_lines.append(f"")
        for bug in not_submitted:
            report_lines.append(f"- **{bug['id']}**: {bug['title']}")
            report_lines.append(f"  - 接口: `{bug['api_path']}`")
            report_lines.append(f"  - 严重程度: {bug.get('severity', 'unknown')}")
            report_lines.append(f"  - 类别: {bug.get('category', 'unknown')}")
            report_lines.append(f"")
    else:
        report_lines.append(f"✅ 所有缺陷都已提交云效")
        report_lines.append(f"")

    if submitted:
        report_lines.append(f"### ✅ 已提交云效的缺陷 ({len(submitted)} 个)")
        report_lines.append(f"")
        for bug in submitted:
            yx = bug.get("yunxiao", {})
            report_lines.append(f"- **{bug['id']}**: {bug['title']}")
            report_lines.append(f"  - 云效ID: `{yx.get('workitem_id', 'N/A')}`")
            report_lines.append(f"  - 链接: {yx.get('url', 'N/A')}")
            report_lines.append(f"")

    # 修复状态详情
    report_lines.append(f"## 🔧 修复状态详情")
    report_lines.append(f"")
    if unfixed:
        report_lines.append(f"### ❌ 未修复的缺陷 ({len(unfixed)} 个)")
        report_lines.append(f"")
        for bug in unfixed:
            report_lines.append(f"- **{bug['id']}**: {bug['title']}")
            report_lines.append(f"  - 接口: `{bug['api_path']}`")
            report_lines.append(f"  - 严重程度: {bug.get('severity', 'unknown')}")
            report_lines.append(f"  - 云效ID: {bug.get('yunxiao', {}).get('workitem_id', 'N/A')}")
            report_lines.append(f"")
    else:
        report_lines.append(f"✅ 所有缺陷都已修复")
        report_lines.append(f"")

    if fixed:
        report_lines.append(f"### 🔶 已修复待验证的缺陷 ({len(fixed)} 个)")
        report_lines.append(f"")
        for bug in fixed:
            report_lines.append(f"- **{bug['id']}**: {bug['title']}")
            report_lines.append(f"  - 修复日期: {bug.get('fix', {}).get('fixed_date', 'N/A')}")
            report_lines.append(f"  - 云效ID: {bug.get('yunxiao', {}).get('workitem_id', 'N/A')}")
            report_lines.append(f"")

    if verified:
        report_lines.append(f"### ✅ 已验证修复的缺陷 ({len(verified)} 个)")
        report_lines.append(f"")
        for bug in verified:
            report_lines.append(f"- **{bug['id']}**: {bug['title']}")
            report_lines.append(f"  - 修复日期: {bug.get('fix', {}).get('fixed_date', 'N/A')}")
            report_lines.append(f"  - 验证日期: {bug.get('fix', {}).get('verified_date', 'N/A')}")
            report_lines.append(f"  - 云效ID: {bug.get('yunxiao', {}).get('workitem_id', 'N/A')}")
            report_lines.append(f"")

    # 按类别统计
    report_lines.append(f"## 📁 按类别统计")
    report_lines.append(f"")
    categories = {}
    for bug in bugs:
        cat = bug.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "submitted": 0, "fixed": 0, "verified": 0}
        categories[cat]["total"] += 1
        if bug.get("yunxiao", {}).get("submitted"):
            categories[cat]["submitted"] += 1
        if bug.get("fix", {}).get("verified"):
            categories[cat]["verified"] += 1
        elif bug.get("fix", {}).get("fixed"):
            categories[cat]["fixed"] += 1

    report_lines.append(f"| 类别 | 总数 | 已提交云效 | 已修复 | 已验证 |")
    report_lines.append(f"|------|------|-----------|--------|--------|")
    for cat, stats in sorted(categories.items()):
        report_lines.append(f"| {cat} | {stats['total']} | {stats['submitted']} | {stats['fixed']} | {stats['verified']} |")
    report_lines.append(f"")

    # 按严重程度统计
    report_lines.append(f"## 🔴 按严重程度统计")
    report_lines.append(f"")
    severities = {}
    for bug in bugs:
        sev = bug.get("severity", "unknown")
        if sev not in severities:
            severities[sev] = {"total": 0, "unfixed": 0}
        severities[sev]["total"] += 1
        if not bug.get("fix", {}).get("fixed"):
            severities[sev]["unfixed"] += 1

    report_lines.append(f"| 严重程度 | 总数 | 未修复 |")
    report_lines.append(f"|----------|------|--------|")
    for sev in ["critical", "high", "medium", "low", "unknown"]:
        if sev in severities:
            stats = severities[sev]
            report_lines.append(f"| {sev} | {stats['total']} | {stats['unfixed']} |")
    report_lines.append(f"")

    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exec_suffix = f"_{execution_id}" if execution_id else ""
    report_file = os.path.join(REPORTS_DIR, f"comparison_report{exec_suffix}_{timestamp}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"对比分析报告已生成: {report_file}")
    return report_file


def print_summary(data, execution_id=None):
    """打印终端摘要"""
    bugs = data.get("bugs", [])
    if execution_id:
        bugs = [b for b in bugs if b.get("execution_id") == execution_id]

    submitted, not_submitted = compare_yunxiao_submission(data, execution_id)
    fixed, unfixed, verified = compare_fix_status(data, execution_id)

    print("=" * 60)
    print("缺陷对比分析摘要")
    print("=" * 60)
    print(f"总缺陷数: {len(bugs)}")
    print(f"已提交云效: {len(submitted)} ({len(submitted)/len(bugs)*100:.1f}%)")
    print(f"未提交云效: {len(not_submitted)} ({len(not_submitted)/len(bugs)*100:.1f}%)")
    print(f"已修复: {len(fixed)} ({len(fixed)/len(bugs)*100:.1f}%)")
    print(f"已验证: {len(verified)} ({len(verified)/len(bugs)*100:.1f}%)")
    print(f"未修复: {len(unfixed)} ({len(unfixed)/len(bugs)*100:.1f}%)")
    print("=" * 60)

    if not_submitted:
        print(f"\n⚠️  未提交云效的缺陷 ({len(not_submitted)} 个):")
        for bug in not_submitted:
            print(f"  - {bug['id']}: {bug['title']}")

    if unfixed:
        print(f"\n🔴 未修复的缺陷 ({len(unfixed)} 个):")
        for bug in unfixed:
            print(f"  - {bug['id']}: {bug['title']}")


def main():
    parser = argparse.ArgumentParser(description="缺陷对比分析脚本")
    parser.add_argument("--execution-id", default=None, help="指定执行批次ID")
    parser.add_argument("--fix-status", action="store_true", help="仅显示修复状态")
    parser.add_argument("--yunxiao-status", action="store_true", help="仅显示云效提交状态")
    parser.add_argument("--report", action="store_true", help="生成对比报告文件")

    args = parser.parse_args()

    data = load_tracking()

    if not data.get("bugs"):
        print("未找到任何缺陷记录")
        sys.exit(1)

    if args.report:
        generate_comparison_report(data, args.execution_id)
    else:
        print_summary(data, args.execution_id)


if __name__ == "__main__":
    main()