"""
yunxiao_submitter.py - 云效 Bug 提交脚本

功能：
1. 从 bug_tracking.json 读取缺陷
2. 查询云效已有 Bug（ListWorkitems API），进行 API 级去重
3. 自动去重（跳过已提交的 Bug + 云效模糊匹配）
4. 创建云效工作项（标题前缀：【超级个体-接口测试】等）
5. 更新 bug_tracking.json 和 existing_bugs.json

用法：
    # 提交所有待提交的 Bug（含查询云效去重）
    python bugs/yunxiao_submitter.py

    # 仅预览（不实际提交）
    python bugs/yunxiao_submitter.py --dry-run

    # 提交指定执行批次的 Bug
    python bugs/yunxiao_submitter.py --execution-id exec_20260806

    # 重新提交所有 Bug（忽略去重）
    python bugs/yunxiao_submitter.py --force

    # 仅同步云效已有 Bug 到本地（不提交新 Bug）
    python bugs/yunxiao_submitter.py --sync-yunxiao

    # 跳过查询云效 API（仅用本地 existing_bugs.json 去重）
    python bugs/yunxiao_submitter.py --no-yunxiao-query
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime

import requests

# ========== 路径配置 ==========
BUGS_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BUGS_DIR, "bug_tracking.json")
EXISTING_BUGS_FILE = os.path.join(BUGS_DIR, "existing_bugs.json")

# ========== 云效配置 ==========
YUNXIAO_TOKEN = "pt-o9Bs7j157DMSrxaolmxiz9EJ_4028aa2b-557c-4b2d-8ea8-a0343bb0077a"
ORGANIZATION_ID = "681dc36041ad8bef38ae0822"
PROJECT_ID = "6bc965ffd5ac5a28dfb230bb82"
WORKITEM_TYPE_ID = "37da3a07df4d08aef2e3b393"
ASSIGNED_TO = "64d1cedb87b86df20e7f4d06"
SERIOUS_LEVEL = "4471da138fe64b3b819b6be0ce"

URL = f"https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{ORGANIZATION_ID}/workitems"
HEADERS = {
    "Content-Type": "application/json",
    "x-yunxiao-token": YUNXIAO_TOKEN,
}
CATEGORY = "Bug"
ENV_BASE = "http://172.16.1.165:9200"

# 查询云效已有 Bug 的 API（SearchWorkitems - 新版推荐）
SEARCH_URL = f"https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{ORGANIZATION_ID}/workitems:search"

# Bug 标题前缀
TITLE_PREFIX = {
    "required_field_validation": "【超级个体-接口测试】",
    "existence_validation": "【超级个体-接口测试】",
    "logic_bug": "【超级个体-接口测试】",
    "security_sql_injection": "【超级个体-安全测试】",
    "security_xss": "【超级个体-安全测试】",
    "boundary_value": "【超级个体-边界测试】",
    "unknown": "【超级个体-接口测试】",
}


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


def load_existing_bugs():
    """加载已有 Bug 记录（用于去重）"""
    if os.path.exists(EXISTING_BUGS_FILE):
        with open(EXISTING_BUGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_existing_bugs(bugs):
    """保存已有 Bug 记录"""
    with open(EXISTING_BUGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bugs, f, ensure_ascii=False, indent=2)


def generate_bug_key(api_path, request_body):
    """生成 Bug 唯一键"""
    key = f"{api_path}_{request_body}"
    return hashlib.md5(key.encode()).hexdigest()


def fetch_yunxiao_bugs(max_pages=10):
    """查询云效已有的 Bug 列表
    
    通过 SearchWorkitems API 获取项目中所有 Bug 类型的工作项，
    用于在提交前去重（避免重复创建标题相似的 Bug）。
    
    Returns:
        list: 云效已有的 Bug 列表，每项包含 identifier, subject, status 等
    """
    all_bugs = []
    page = 0
    
    while page < max_pages:
        page += 1
        payload = {
            "category": "Bug",
            "spaceId": PROJECT_ID,
            "spaceType": "Project",
            "page": page,
            "perPage": 200,
            "orderBy": "gmtCreate",
            "sort": "desc",
        }
        
        try:
            resp = requests.post(SEARCH_URL, json=payload, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                print(f"  ⚠️ 查询云效 Bug 列表失败 (HTTP {resp.status_code}): {resp.text[:200]}")
                break
            
            data = resp.json()
            
            # SearchWorkitems API 直接返回列表
            if isinstance(data, list):
                workitems = data
            elif isinstance(data, dict):
                workitems = data.get("workitems", [])
                if not data.get("success", True):
                    print(f"  ⚠️ 查询云效 Bug 列表失败: {data.get('errorMsg', '未知错误')}")
                    break
            else:
                print(f"  ⚠️ 查询云效 Bug 列表失败: 未知的响应格式")
                break
            
            # 统一字段名（API 返回 id/subject/status 对象，统一为 identifier/subject/status 字符串）
            for item in workitems:
                normalized = {
                    "identifier": item.get("id", ""),
                    "subject": item.get("subject", ""),
                    "serialNumber": item.get("serialNumber", ""),
                    "status": item.get("status", {}).get("displayName", "") if isinstance(item.get("status"), dict) else str(item.get("status", "")),
                    "assignedTo": item.get("assignedTo", {}).get("name", "") if isinstance(item.get("assignedTo"), dict) else str(item.get("assignedTo", "")),
                    "creator": item.get("creator", {}).get("name", "") if isinstance(item.get("creator"), dict) else str(item.get("creator", "")),
                    "gmtCreate": item.get("gmtCreate", 0),
                    "logicalStatus": item.get("logicalStatus", ""),
                }
                all_bugs.append(normalized)
            
            # 如果返回数量少于 perPage，说明没有下一页
            if len(workitems) < 200:
                break
            
            time.sleep(0.5)  # 避免频率限制
        except Exception as e:
            print(f"  ⚠️ 查询云效 Bug 列表异常: {e}")
            break
    
    return all_bugs


def generate_bug_title(bug):
    """根据 bug 数据生成云效 Bug 标题
    
    标题格式：【前缀】POST /path 描述
    
    示例：
    - 【超级个体-接口测试】POST /platform/user/save 必填项 status 未校验
    - 【超级个体-安全测试】POST /platform/knowledge/save title 字段 SQL 注入
    - 【超级个体-边界测试】POST /platform/pricing/updatePricing amount=0 未校验
    """
    category = bug.get("category", "unknown")
    prefix = TITLE_PREFIX.get(category, "【超级个体-接口测试】")
    
    # 提取 API 路径
    api_path = bug.get("api_path", "")
    path = extract_path(api_path)
    method = "POST"
    if " " in api_path:
        method = api_path.split(" ", 1)[0]
    
    # 生成描述部分
    field = bug.get("field", "")
    tag = bug.get("tag", "")
    description = bug.get("description", "")
    test_case = bug.get("test_case", "")
    
    # 根据类别生成描述
    if category == "required_field_validation":
        desc_part = f"必填项 {field} 未校验"
    elif category == "existence_validation":
        desc_part = f"对不存在记录操作返回成功"
    elif category == "security_sql_injection":
        desc_part = f"{field} 字段 SQL 注入"
    elif category == "security_xss":
        desc_part = f"{field} 字段 XSS 注入"
    elif category == "boundary_value":
        desc_part = f"{field}={tag} 未校验"
    elif category == "logic_bug":
        if field == "token":
            desc_part = "无Token登出返回成功"
        elif tag == "no record":
            desc_part = "未导入数据时更新返回成功"
        elif tag == "exception":
            desc_part = f"接口返回异常"
        else:
            desc_part = description[:40] if description else "接口逻辑异常"
    else:
        desc_part = description[:40] if description else test_case
    
    return f"{prefix}{method} {path} {desc_part}"


def match_yunxiao_bug(bug_title, yunxiao_bugs):
    """检查 Bug 标题是否与云效已有 Bug 匹配
    
    通过标题关键词进行模糊匹配，避免重复创建相似的 Bug。
    
    Args:
        bug_title: 生成的 Bug 标题
        yunxiao_bugs: 云效已有的 Bug 列表
    
    Returns:
        str: 匹配到的云效 Bug ID，未匹配返回 None
    """
    if not yunxiao_bugs:
        return None
    
    # 提取标题中的关键信息（去除前缀后的部分）
    # 例如: "【超级个体-接口测试】POST /platform/user/save 必填项 status 未校验"
    # 关键信息: "POST /platform/user/save 必填项 status 未校验"
    title_core = bug_title
    for prefix in TITLE_PREFIX.values():
        if title_core.startswith(prefix):
            title_core = title_core[len(prefix):]
            break
    
    # 同时匹配旧前缀（【接口测试】【安全测试】【边界测试】）
    old_prefixes = ["【接口测试】", "【安全测试】", "【边界测试】"]
    for prefix in old_prefixes:
        if title_core.startswith(prefix):
            title_core = title_core[len(prefix):]
            break
    
    # 提取路径部分用于匹配
    path_match = re.search(r'(POST|GET|PUT|DELETE|PATCH)\s+(/\S+)', title_core)
    if not path_match:
        return None
    
    match_path = path_match.group(2)
    
    for yx_bug in yunxiao_bugs:
        yx_subject = yx_bug.get("subject", "")
        
        # 去除前缀
        yx_core = yx_subject
        for prefix in list(TITLE_PREFIX.values()) + old_prefixes:
            if yx_core.startswith(prefix):
                yx_core = yx_core[len(prefix):]
                break
        
        # 提取云效 Bug 的路径
        yx_path_match = re.search(r'(POST|GET|PUT|DELETE|PATCH)\s+(/\S+)', yx_core)
        if not yx_path_match:
            continue
        
        yx_path = yx_path_match.group(2)
        
        # 路径相同且描述部分也相似（包含相同的关键词）
        if yx_path == match_path:
            # 进一步检查描述部分是否相似
            # 提取描述中的关键词
            title_desc = title_core[path_match.end():].strip()
            yx_desc = yx_core[yx_path_match.end():].strip()
            
            # 如果描述中包含相同的关键字段名
            if field_keyword_match(title_desc, yx_desc):
                return yx_bug.get("identifier")
    
    return None


def field_keyword_match(desc1, desc2):
    """检查两个描述是否包含相同的关键词
    
    用于判断两个 Bug 描述是否指向同一个问题。
    """
    # 提取可能的字段名关键词
    keywords = re.findall(r'[a-zA-Z_]+', desc1 + " " + desc2)
    if not keywords:
        # 如果没有英文关键词，检查中文关键词
        return desc1[:10] == desc2[:10]  # 前10个字符相同
    
    # 统计两个描述中共同的关键词
    words1 = set(re.findall(r'[a-zA-Z_]+', desc1.lower()))
    words2 = set(re.findall(r'[a-zA-Z_]+', desc2.lower()))
    
    # 如果有共同的字段名关键词（长度>2），认为是同一个 Bug
    common = words1 & words2
    significant_common = [w for w in common if len(w) > 2]
    
    if significant_common:
        return True
    
    # 如果没有英文关键词，检查中文关键词相似性
    # 提取中文关键词
    cn_words1 = set(re.findall(r'[\u4e00-\u9fff]+', desc1))
    cn_words2 = set(re.findall(r'[\u4e00-\u9fff]+', desc2))
    cn_common = cn_words1 & cn_words2
    
    # 如果有共同的中文关键词（长度>2），认为是同一个 Bug
    significant_cn = [w for w in cn_common if len(w) > 2]
    if significant_cn:
        return True
    
    return False


def sync_to_key(method, path, desc_part):
    """从云效 Bug 标题描述部分提取 existing_bugs.json 的 key
    
    标题格式: 【前缀】POST /path 描述
    描述部分示例:
    - "必填项 status 未校验" -> key: "POST /path_status null"
    - "title 字段 SQL 注入" -> key: "POST /path_title SQL注入"
    - "amount=0 未校验" -> key: "POST /path_amount 0"
    - "删除不存在的用户返回成功" -> key: "POST /path_id 999999"
    - "无Token登出返回成功" -> key: "POST /path_no token"
    """
    # 必填项校验: "必填项 status 未校验"
    m = re.search(r'必填项\s+(\w+)\s+未校验', desc_part)
    if m:
        return f"{method} {path}_{m.group(1)} null"
    
    # 安全测试: "title 字段 SQL 注入" / "content 字段 XSS 注入"
    m = re.search(r'(\w+)\s+字段\s+(SQL|XSS)\s+注入', desc_part)
    if m:
        return f"{method} {path}_{m.group(1)} {m.group(2)}注入" if m.group(2) == "SQL" else f"{method} {path}_{m.group(1)} XSS"
    
    # 边界值: "amount=0 未校验" / "amount=-1 未校验"
    m = re.search(r'(\w+)=(-?\d+)\s+未校验', desc_part)
    if m:
        return f"{method} {path}_{m.group(1)} {m.group(2)}"
    
    # 不存在记录: "删除不存在的..." / "编辑不存在的..." / "修改不存在的..."
    if "不存在" in desc_part:
        return f"{method} {path}_id 999999"
    
    # 对所有ID返回404
    if "404" in desc_part:
        return f"{method} {path}_id 1"
    
    # 无Token
    if "无Token" in desc_part or "无 Token" in desc_part:
        return f"{method} {path}_no token"
    
    # 未导入数据
    if "未导入" in desc_part:
        return f"{method} {path}_no record"
    
    return None


def extract_path(api_path):
    """从 API path 中提取纯路径部分
    
    输入: "POST /platform/user/save" 或 "POST http://host:port/platform/user/save"
    输出: "/platform/user/save"
    """
    path = api_path.strip()
    # 去除方法前缀
    for method in ["POST ", "GET ", "PUT ", "DELETE ", "PATCH "]:
        if path.startswith(method):
            path = path[len(method):]
            break
    # 如果包含 URL scheme，提取路径
    if "://" in path:
        path = "/" + path.split("://", 1)[1].split("/", 1)[1]
    return path.rstrip("/") or path


def generate_yunxiao_key(bug):
    """从 bug 数据生成 existing_bugs.json 的 key
    
    格式: "METHOD /path_field tag"
    
    existing_bugs.json 中的 key 格式示例:
    - POST /platform/user/save_status null
    - POST /platform/user/delete_id 999999
    """
    api_path = bug.get("api_path", "")
    field = bug.get("field", "")
    tag = bug.get("tag", "")
    title = bug.get("title", "")
    description = bug.get("description", "")
    test_case = bug.get("test_case", "")
    
    # 从 api_path 中提取方法和路径
    if " " in api_path:
        method, raw_path = api_path.split(" ", 1)
    else:
        method = "POST"
        raw_path = api_path
    
    # 提取纯路径（去除 host 和 URL scheme）
    path = extract_path(raw_path)
    
    # 如果 field 和 tag 缺失，尝试从 title/description/test_case 推断
    if not field:
        field = infer_field_from_title(title, description, test_case, path)
    if not tag:
        tag = infer_tag_from_title(title, description, test_case)
    
    # 构造 key: METHOD /path_field tag
    key_parts = [f"{method} {path}"]
    if field:
        key_parts[0] += f"_{field}"
    if tag:
        key_parts.append(tag)
    
    return " ".join(key_parts)


def infer_field_from_title(title, description, test_case, path):
    """从 title/description/test_case 推断字段名
    
    例如:
    - title: "保存用户时缺少 status 必填项" -> field = "status"
    - test_case: "test_save_null_status" -> field = "status"
    - test_case: "test_delete_knowledge_non_existing" -> field = "id" (删除操作通常用 id)
    """
    # 常见字段名映射
    field_map = {
        "status": "status",
        "id": "id",
        "areaList": "areaList",
        "smsCode": "smsCode",
        "amount": "amount",
        "title": "title",
        "code": "code",
        "token": "token",
    }
    
    # 从 test_case 推断
    if test_case:
        # test_case 格式: test_action_target_condition
        # 例如: test_save_null_status, test_delete_id_999999, test_delete_knowledge_non_existing
        parts = test_case.replace("test_", "").split("_")
        for i, part in enumerate(parts):
            if part in field_map:
                return field_map[part]
    
    # 从 title 推断
    if title:
        for key, val in field_map.items():
            if key in title.lower():
                return val
    
    # 从 description 推断
    if description:
        for key, val in field_map.items():
            if key in description.lower():
                return val
    
    # 从 path 推断（最后一段可能是操作名）
    path_parts = [p for p in path.split("/") if p]
    if path_parts:
        last_part = path_parts[-1]
        # 如果最后一段是常见的字段名
        if last_part in field_map:
            return field_map[last_part]
    
    # 根据操作类型推断默认字段
    # 删除、编辑、查询操作通常使用 id
    if path_parts:
        action = path_parts[-1].lower()
        if action in ("delete", "del", "remove", "edit", "update", "detail", "get", "query"):
            return "id"
    
    return ""


def infer_tag_from_title(title, description, test_case):
    """从 title/description/test_case 推断标签
    
    标签可能是: null, 999999, SQL注入, XSS, 0, -1
    注意：existing_bugs.json 中使用的是中文标签如 "SQL注入", "XSS"
    """
    # 检查 test_case
    if test_case:
        # test_case 示例: test_sql_injection_knowledge_title[' OR '1'='1]
        # test_sql_injection_knowledge_title['; DROP TABLE users; --]
        if "sql" in test_case.lower():
            return "SQL注入"
        if "xss" in test_case.lower():
            return "XSS"
        
        # 检查数字标签
        parts = test_case.split("_")
        for part in parts:
            if part in ("null", "999999", "0", "-1"):
                return part
            if "nonexist" in part.lower() or "non_existing" in part.lower() or "non_exist" in part.lower():
                return "999999"
    
    # 检查 title
    if title:
        if "null" in title.lower():
            return "null"
        if "999999" in title:
            return "999999"
        if "sql" in title.lower():
            return "SQL注入"
        if "xss" in title.lower():
            return "XSS"
        if "无" in title or "不存在" in title or "nonexist" in title.lower() or "non_existing" in title.lower():
            return "999999"  # 不存在的记录通常用 999999
        if "未登录" in title or "无token" in title:
            return "null"
    
    # 检查 description
    if description:
        if "null" in description.lower():
            return "null"
        if "999999" in description:
            return "999999"
        if "sql" in description.lower() or "注入" in description:
            return "SQL注入"
        if "xss" in description.lower() or "脚本" in description:
            return "XSS"
        if "不存在" in description:
            return "999999"
    
    return ""


def create_bug(subject, description, assigned_to=None):
    """创建云效 Bug"""
    payload = {
        "spaceId": PROJECT_ID,
        "subject": subject,
        "category": CATEGORY,
        "workitemTypeId": WORKITEM_TYPE_ID,
        "assignedTo": assigned_to or ASSIGNED_TO,
        "customFieldValues": {
            "seriousLevel": SERIOUS_LEVEL,
        },
        "description": description,
    }

    resp = requests.post(URL, json=payload, headers=HEADERS, timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        workitem_id = data.get("id")
        print(f"  ✅ 创建成功，缺陷ID：{workitem_id}")
        print(f"     链接：https://devops.aliyun.com/workitem/{workitem_id}?organizationId={ORGANIZATION_ID}")
        return workitem_id
    else:
        print(f"  ❌ 创建失败 (HTTP {resp.status_code}): {resp.text[:200]}")
        return None


def format_bug_description(bug):
    """格式化 Bug 描述"""
    description = bug.get("description", "")
    request_body = bug.get("request_body", "")
    response_body = bug.get("response_body", "")
    api_path = bug.get("api_path", "")
    severity = bug.get("severity", "high")
    
    severity_map = {"high": "高", "medium": "中", "low": "低"}
    severity_text = severity_map.get(severity, severity)
    
    # 格式化请求/响应
    def compact_json(obj):
        if obj is None:
            return "无"
        try:
            if isinstance(obj, str):
                parsed = json.loads(obj)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except Exception:
            return str(obj)
    
    desc = f"""## Bug 描述

{description}

---

## 复现信息

| 项目 | 内容 |
|------|------|
| **缺陷ID** | {bug.get('id', 'N/A')} |
| **请求地址** | `{api_path}` |
| **严重程度** | {severity_text} |
| **入参** | ```json
{compact_json(request_body)}
``` |
| **出参** | ```json
{compact_json(response_body)}
``` |
| **测试环境** | {ENV_BASE} |
| **测试时间** | {datetime.now().strftime('%Y-%m-%d')} |

---

## 建议

建议后端增加相应的校验逻辑。
"""
    return desc


def get_bugs_to_submit(data, execution_id=None, force=False):
    """获取需要提交的 Bug 列表
    
    Args:
        data: bug_tracking.json 数据
        execution_id: 仅提交指定执行批次的 Bug
        force: 是否强制重新提交（忽略已提交状态）
    
    Returns:
        list: 需要提交的 Bug 列表
    """
    bugs = data.get("bugs", [])
    
    result = []
    for bug in bugs:
        # 过滤指定执行批次
        if execution_id and bug.get("execution_id") != execution_id:
            continue
        
        # 检查是否已提交
        yunxiao = bug.get("yunxiao", {})
        if not force and yunxiao.get("submitted"):
            continue
        
        # 检查 Bug 状态
        if bug.get("status") in ("fixed", "verified"):
            continue  # 已修复或已验证的 Bug 不需要提交
        
        result.append(bug)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="提交 Bug 到云效")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际提交")
    parser.add_argument("--execution-id", type=str, help="仅提交指定执行批次的 Bug")
    parser.add_argument("--force", action="store_true", help="强制重新提交所有 Bug")
    parser.add_argument("--bug-ids", nargs="+", help="仅提交指定 ID 的 Bug（如 BUG-001 BUG-002）")
    parser.add_argument("--sync-yunxiao", action="store_true", help="仅查询云效已有 Bug 并同步到本地，不提交新 Bug")
    parser.add_argument("--no-yunxiao-query", action="store_true", help="跳过查询云效 API（仅用本地 existing_bugs.json 去重）")
    args = parser.parse_args()
    
    # 加载数据
    data = load_tracking()
    existing_bugs = load_existing_bugs()
    
    # ========== 查询云效已有 Bug ==========
    yunxiao_bugs = []
    if not args.no_yunxiao_query:
        print("=" * 60)
        print("📡 查询云效已有 Bug 列表...")
        print("=" * 60)
        yunxiao_bugs = fetch_yunxiao_bugs()
        print(f"   云效已有 Bug 数量: {len(yunxiao_bugs)}")
        
        if yunxiao_bugs:
            print(f"\n   云效已有 Bug 标题列表:")
            for i, yb in enumerate(yunxiao_bugs[:10], 1):
                status = yb.get("status", "")
                print(f"   {i}. [{status}] {yb.get('subject', '')}")
            if len(yunxiao_bugs) > 10:
                print(f"   ... 共 {len(yunxiao_bugs)} 个")
        print()
    
    # ========== 仅同步模式 ==========
    if args.sync_yunxiao:
        print("=" * 60)
        print("同步云效已有 Bug 到本地...")
        print("=" * 60)
        
        # 将云效 Bug 同步到 existing_bugs.json
        synced_count = 0
        for yb in yunxiao_bugs:
            subject = yb.get("subject", "")
            identifier = yb.get("identifier", "")
            
            # 尝试从标题中提取 key 信息
            # 标题格式: 【前缀】POST /path 描述
            core = subject
            for prefix in list(TITLE_PREFIX.values()) + ["【接口测试】", "【安全测试】", "【边界测试】"]:
                if core.startswith(prefix):
                    core = core[len(prefix):]
                    break
            
            # 提取路径
            path_match = re.search(r'(POST|GET|PUT|DELETE|PATCH)\s+(/\S+)', core)
            if path_match:
                method = path_match.group(1)
                path = path_match.group(2)
                desc_part = core[path_match.end():].strip()
                
                # 尝试匹配 existing_bugs.json 的 key 格式
                # 格式: "METHOD /path_field tag"
                # 从描述中提取 field 和 tag
                key = sync_to_key(method, path, desc_part)
                if key and key not in existing_bugs:
                    existing_bugs[key] = {
                        "id": identifier,
                        "title": subject
                    }
                    synced_count += 1
        
        save_existing_bugs(existing_bugs)
        print(f"\n✅ 同步完成！新增 {synced_count} 条记录到 existing_bugs.json")
        print(f"   总记录数: {len(existing_bugs)}")
        return
    
    # ========== 正常提交模式 ==========
    # 获取待提交的 Bug
    bugs_to_submit = get_bugs_to_submit(data, args.execution_id, args.force)
    
    # 如果指定了 Bug ID，进一步过滤
    if args.bug_ids:
        bugs_to_submit = [b for b in bugs_to_submit if b.get("id") in args.bug_ids]
    
    print("=" * 60)
    print("云效 Bug 提交")
    print("=" * 60)
    print(f"待提交 Bug 数量: {len(bugs_to_submit)}")
    print(f"本地已有记录: {len(existing_bugs)}")
    print(f"云效已有 Bug: {len(yunxiao_bugs)}")
    print(f"模式: {'预览' if args.dry_run else '实际提交'}")
    if args.execution_id:
        print(f"执行批次: {args.execution_id}")
    print("=" * 60)
    
    if not bugs_to_submit:
        print("\n✅ 没有需要提交的 Bug。")
        return
    
    # 去重检查
    new_bugs = []
    skipped_bugs = []
    
    for bug in bugs_to_submit:
        bug_key = generate_yunxiao_key(bug)
        
        # 检查 1: 是否已在本地 existing_bugs 中
        if bug_key in existing_bugs and not args.force:
            existing_id = existing_bugs[bug_key].get("id", "")
            if not bug.get("yunxiao", {}).get("submitted"):
                bug["yunxiao"] = {
                    "submitted": True,
                    "workitem_id": existing_id,
                    "title": existing_bugs[bug_key].get("title", bug.get("title", "")),
                    "submitted_date": datetime.now().strftime("%Y-%m-%d"),
                    "url": f"https://devops.aliyun.com/workitem/{existing_id}?organizationId={ORGANIZATION_ID}"
                }
                skipped_bugs.append({"id": bug["id"], "workitem_id": existing_id, "reason": "本地记录"})
            continue
        
        # 检查 2: bug_tracking.json 中已有 yunxiao 记录
        if bug.get("yunxiao", {}).get("submitted") and not args.force:
            skipped_bugs.append({
                "id": bug["id"],
                "workitem_id": bug["yunxiao"]["workitem_id"],
                "reason": "已提交"
            })
            continue
        
        # 检查 3: 查询云效 API 进行模糊匹配
        if yunxiao_bugs and not args.force:
            bug_title = generate_bug_title(bug)
            matched_id = match_yunxiao_bug(bug_title, yunxiao_bugs)
            if matched_id:
                bug["yunxiao"] = {
                    "submitted": True,
                    "workitem_id": matched_id,
                    "title": bug_title,
                    "submitted_date": datetime.now().strftime("%Y-%m-%d"),
                    "url": f"https://devops.aliyun.com/workitem/{matched_id}?organizationId={ORGANIZATION_ID}"
                }
                # 同时更新 existing_bugs.json
                existing_bugs[bug_key] = {
                    "id": matched_id,
                    "title": bug_title
                }
                skipped_bugs.append({"id": bug["id"], "workitem_id": matched_id, "reason": "云效匹配"})
                continue
        
        new_bugs.append(bug)
    
    print(f"\n📊 去重结果:")
    print(f"   - 跳过（已提交）: {len(skipped_bugs)}")
    print(f"   - 待创建: {len(new_bugs)}")
    
    if skipped_bugs:
        print(f"\n📋 已提交的 Bug:")
        for item in skipped_bugs[:10]:
            print(f"   - {item['id']} -> 云效 ID: {item['workitem_id']} ({item.get('reason', '')})")
        if len(skipped_bugs) > 10:
            print(f"   ... 共 {len(skipped_bugs)} 个")
    
    if not new_bugs:
        print("\n✅ 所有 Bug 都已提交，没有新的 Bug 需要创建。")
        save_tracking(data)
        save_existing_bugs(existing_bugs)
        return
    
    if args.dry_run:
        print(f"\n🔍 预览模式 - 将提交以下 {len(new_bugs)} 个 Bug:")
        for i, bug in enumerate(new_bugs[:15], 1):
            title = generate_bug_title(bug)
            print(f"   {i}. [{bug['id']}] {title}")
        if len(new_bugs) > 15:
            print(f"   ... 共 {len(new_bugs)} 个")
        return
    
    # 实际提交
    print(f"\n🚀 开始提交 {len(new_bugs)} 个新 Bug...\n")
    
    for i, bug in enumerate(new_bugs, 1):
        bug_id = bug.get("id", "N/A")
        title = generate_bug_title(bug)
        print(f"[{i}/{len(new_bugs)}] {bug_id}: {title}")
        
        # 生成描述
        desc = format_bug_description(bug)
        
        # 创建云效 Bug
        workitem_id = create_bug(title, desc)
        
        if workitem_id:
            # 更新 bug 数据
            bug["yunxiao"] = {
                "submitted": True,
                "workitem_id": workitem_id,
                "title": title,
                "submitted_date": datetime.now().strftime("%Y-%m-%d"),
                "url": f"https://devops.aliyun.com/workitem/{workitem_id}?organizationId={ORGANIZATION_ID}"
            }
            bug["status"] = "submitted"
            
            # 更新 existing_bugs.json
            bug_key = generate_yunxiao_key(bug)
            existing_bugs[bug_key] = {
                "id": workitem_id,
                "title": title
            }
        
        if i < len(new_bugs):
            time.sleep(1)  # 避免频率限制
        print()
    
    # 保存更新
    save_tracking(data)
    save_existing_bugs(existing_bugs)
    
    print("=" * 60)
    print(f"✅ 提交完成！")
    print(f"   - 成功提交: {len([b for b in new_bugs if b.get('yunxiao', {}).get('submitted')])}")
    print(f"   - 保存位置:")
    print(f"     - {TRACKING_FILE}")
    print(f"     - {EXISTING_BUGS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
