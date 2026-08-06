"""
track_bugs.py - 缺陷跟踪脚本

功能：
1. 从测试结果中提取缺陷信息
2. 按执行顺序记录缺陷
3. 生成带时间戳的缺陷报告
4. 更新 bug_tracking.json 主文件

用法：
    python bugs/track_bugs.py --execution-id exec_20260805 --date 2026-08-05
"""

import json
import os
import sys
import argparse
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUGS_DIR = os.path.join(PROJECT_ROOT, "bugs")
TRACKING_FILE = os.path.join(BUGS_DIR, "bug_tracking.json")
REPORTS_DIR = os.path.join(BUGS_DIR, "reports")
TEMPLATE_FILE = os.path.join(BUGS_DIR, "templates", "bug_report_template.md")


def load_tracking():
    """加载缺陷跟踪主文件"""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {}, "executions": [], "bugs": [], "summary": {}}


def save_tracking(data):
    """保存缺陷跟踪主文件"""
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_bug_id(data):
    """生成新的缺陷ID"""
    existing_ids = [b["id"] for b in data.get("bugs", [])]
    max_num = 0
    for bid in existing_ids:
        try:
            num = int(bid.split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass
    return f"BUG-{max_num + 1:03d}"


def add_execution(data, execution_id, test_date, environment, test_summary, notes=""):
    """添加一次测试执行记录"""
    execution = {
        "execution_id": execution_id,
        "date": test_date,
        "environment": environment,
        "test_suite": test_summary,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    data["executions"].append(execution)
    data["meta"]["last_updated"] = test_date
    return execution


def add_bug(data, execution_id, category, title, api_path, request_body,
            response_body, description, severity, yunxiao_info=None):
    """添加一条缺陷记录"""
    bug_id = generate_bug_id(data)
    bug = {
        "id": bug_id,
        "execution_id": execution_id,
        "category": category,
        "title": title,
        "api_path": api_path,
        "request_body": request_body,
        "response_body": response_body,
        "description": description,
        "severity": severity,
        "status": "submitted" if yunxiao_info and yunxiao_info.get("submitted") else "pending",
        "yunxiao": yunxiao_info or {
            "submitted": False,
            "workitem_id": None,
            "title": None,
            "submitted_date": None,
            "url": None
        },
        "fix": {
            "fixed": False,
            "fixed_date": None,
            "verified": False,
            "verified_date": None
        },
        "created_at": datetime.now().isoformat()
    }
    data["bugs"].append(bug)
    return bug


def update_bug_fix_status(data, bug_id, fixed=True, fixed_date=None, verified=False, verified_date=None):
    """更新缺陷修复状态"""
    for bug in data.get("bugs", []):
        if bug["id"] == bug_id:
            bug["fix"]["fixed"] = fixed
            bug["fix"]["fixed_date"] = fixed_date or datetime.now().strftime("%Y-%m-%d")
            bug["fix"]["verified"] = verified
            bug["fix"]["verified_date"] = verified_date
            bug["status"] = "verified" if verified else ("fixed" if fixed else bug["status"])
            return bug
    return None


def update_yunxiao_submission(data, bug_id, workitem_id, title, url, submitted_date=None):
    """更新云效提交信息"""
    for bug in data.get("bugs", []):
        if bug["id"] == bug_id:
            bug["yunxiao"] = {
                "submitted": True,
                "workitem_id": workitem_id,
                "title": title,
                "submitted_date": submitted_date or datetime.now().strftime("%Y-%m-%d"),
                "url": url
            }
            bug["status"] = "submitted"
            return bug
    return None


def generate_report(data, execution_id=None):
    """生成缺陷报告 Markdown 文件"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 筛选指定执行的缺陷
    if execution_id:
        bugs = [b for b in data.get("bugs", []) if b.get("execution_id") == execution_id]
        execution = next((e for e in data.get("executions", []) if e["execution_id"] == execution_id), None)
    else:
        bugs = data.get("bugs", [])
        execution = data.get("executions", [])[-1] if data.get("executions") else None

    if not execution:
        print("未找到执行记录")
        return None

    # 统计各类别数量
    categories = {}
    for bug in bugs:
        cat = bug.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # 统计云效提交状态
    yunxiao_submitted = sum(1 for b in bugs if b.get("yunxiao", {}).get("submitted"))
    yunxiao_pending = len(bugs) - yunxiao_submitted

    # 统计修复状态
    fixed_count = sum(1 for b in bugs if b.get("fix", {}).get("fixed"))
    unfixed_count = len(bugs) - fixed_count
    verified_count = sum(1 for b in bugs if b.get("fix", {}).get("verified"))

    # 生成缺陷条目
    bug_entries = ""
    for bug in bugs:
        yx = bug.get("yunxiao", {})
        fix = bug.get("fix", {})
        bug_entries += f"""### {bug['id']}: {bug['title']}

| 项目 | 内容 |
|------|------|
| **缺陷ID** | {bug['id']} |
| **接口** | `{bug['api_path']}` |
| **严重程度** | {bug.get('severity', 'unknown')} |
| **类别** | {bug.get('category', 'unknown')} |
| **请求地址** | `{bug['api_path']}` |
| **入参** | `{json.dumps(bug['request_body'], ensure_ascii=False)}` |
| **出参** | `{json.dumps(bug['response_body'], ensure_ascii=False)}` |
| **描述** | {bug.get('description', '')} |
| **云效提交** | {'✅ 已提交' if yx.get('submitted') else '❌ 未提交'} |
| **云效ID** | {yx.get('workitem_id', 'N/A')} |
| **修复状态** | {'✅ 已修复' if fix.get('fixed') else '❌ 未修复'} |
| **验证状态** | {'✅ 已验证' if fix.get('verified') else '❌ 未验证'} |

---

"""

    # 读取模板
    template = ""
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            template = f.read()

    # 替换模板变量
    report = template.replace("{{execution_id}}", execution.get("execution_id", "unknown"))
    report = report.replace("{{test_date}}", execution.get("date", "unknown"))
    report = report.replace("{{environment}}", execution.get("environment", "unknown"))
    report = report.replace("{{test_summary}}", execution.get("test_suite", "unknown"))
    report = report.replace("{{execution_order}}", str(len(data.get("executions", []))))
    report = report.replace("{{bug_entries}}", bug_entries)
    report = report.replace("{{required_field_count}}", str(categories.get("required_field_validation", 0)))
    report = report.replace("{{existence_count}}", str(categories.get("existence_validation", 0)))
    report = report.replace("{{logic_count}}", str(categories.get("logic_bug", 0)))
    report = report.replace("{{security_count}}", str(categories.get("security_sql_injection", 0) + categories.get("security_xss", 0)))
    report = report.replace("{{boundary_count}}", str(categories.get("boundary_value", 0)))
    report = report.replace("{{total_count}}", str(len(bugs)))
    report = report.replace("{{yunxiao_submitted}}", str(yunxiao_submitted))
    report = report.replace("{{yunxiao_pending}}", str(yunxiao_pending))
    report = report.replace("{{fixed_count}}", str(fixed_count))
    report = report.replace("{{unfixed_count}}", str(unfixed_count))
    report = report.replace("{{verified_count}}", str(verified_count))

    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(REPORTS_DIR, f"{execution.get('execution_id', 'unknown')}_{timestamp}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"缺陷报告已生成: {report_file}")
    return report_file


def main():
    parser = argparse.ArgumentParser(description="缺陷跟踪脚本")
    parser.add_argument("--execution-id", required=True, help="执行批次ID")
    parser.add_argument("--date", required=True, help="测试日期 (YYYY-MM-DD)")
    parser.add_argument("--environment", default="http://172.16.1.165:9200", help="测试环境地址")
    parser.add_argument("--test-summary", default="", help="测试套件摘要")
    parser.add_argument("--notes", default="", help="备注")
    parser.add_argument("--generate-report", action="store_true", help="生成缺陷报告")
    parser.add_argument("--execution-order", type=int, default=1, help="执行顺序编号")

    args = parser.parse_args()

    data = load_tracking()

    # 添加执行记录
    add_execution(
        data,
        args.execution_id,
        args.date,
        args.environment,
        args.test_summary,
        args.notes
    )

    # 保存更新
    save_tracking(data)
    print(f"执行记录已添加: {args.execution_id}")

    # 生成报告
    if args.generate_report:
        generate_report(data, args.execution_id)

    # 打印汇总
    bugs = [b for b in data.get("bugs", []) if b.get("execution_id") == args.execution_id]
    print(f"本次执行共记录 {len(bugs)} 个缺陷")


if __name__ == "__main__":
    main()