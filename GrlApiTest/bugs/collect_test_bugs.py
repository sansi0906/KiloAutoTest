# -*- coding: utf-8 -*-
"""
collect_test_bugs.py - 收集全量测试失败用例为缺陷，打标 needs_retest，生成 bug_list.md

参考历史约定（collect_bugs.py / track_bugs.py / bug_list.md / existing_bugs.json）：
1. 分类与历史 bug_list.md 一致：必填项校验 / 存在性校验 / 接口逻辑 / 安全漏洞（SQL注入/XSS）/ 边界值 / 环境限制
2. bug_tracking.json 字段：request_body, response_body, category, title, api_path, description, severity, status, yunxiao, fix
3. 去重：沿用 existing_bugs.json 的 "POST /path_field tag" 签名，通过 yunxiao.workitem_id 关联已有缺陷，
   复用 BUG-00X 编号，避免重复创建
4. 不调用云效，仅标记 status="needs_retest"

产物（复用已有）：
  reports/full_junit.xml        - 全量测试 junit 结果
  reports/requests_capture.json - 各用例真实请求/响应报文
输出：
  bugs/bug_tracking.json        - 更新后的缺陷主文件（去重 + 真实报文 + needs_retest）
  bugs/latest_bug_list.md       - 历史格式缺陷清单（含真实入参/出参）
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# 修复 Windows GBK 终端编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

# 解析命令行参数
parser = argparse.ArgumentParser(description="收集测试缺陷并可选提交到云效")
parser.add_argument("--submit-to-yunxiao", action="store_true", help="收集完成后自动提交到云效")
parser.add_argument("--dry-run", action="store_true", help="仅收集缺陷，预览模式")
args = parser.parse_args()

ROOT = r"E:\KiloAutoTest\GrlApiTest"
JUNIT = os.path.join(ROOT, "reports", "full_junit.xml")
CAP = os.path.join(ROOT, "reports", "requests_capture.json")
TRACKING = os.path.join(ROOT, "bugs", "bug_tracking.json")
EXISTING = os.path.join(ROOT, "bugs", "existing_bugs.json")
OUT = os.path.join(ROOT, "bugs", "latest_bug_list.md")
TODAY = "2026-08-06"
EXEC_ID = "exec_20260806"
ENV = "http://172.16.1.165:9200"
OPENAPI_URL = f"{ENV}/v3/api-docs"

# ---------- 0. 获取 OpenAPI 规范，构建 API-DTO 映射 ----------
print("正在获取 OpenAPI 规范...")
API_DTO_MAP = {}  # {api_path: {"dto": "DtoName", "required_fields": [...], "summary": "..."}}
try:
    req = urllib.request.Request(OPENAPI_URL)
    with urllib.request.urlopen(req, timeout=10) as resp:
        spec = json.loads(resp.read())
        paths = spec.get("paths", {})
        schemas = spec.get("components", {}).get("schemas", {})
        
        for path, methods in paths.items():
            for method, api in methods.items():
                if method not in ['post', 'get', 'put', 'delete']:
                    continue
                if not api.get('requestBody'):
                    continue
                
                schema_ref = api.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('$ref', '')
                if not schema_ref:
                    continue
                
                schema_name = schema_ref.replace('#/components/schemas/', '')
                if schema_name not in schemas:
                    continue
                
                schema = schemas[schema_name]
                required = schema.get('required', [])
                API_DTO_MAP[path] = {
                    "dto": schema_name,
                    "required_fields": required,
                    "summary": api.get('summary', ''),
                    "method": method.upper()
                }
        print(f"已加载 {len(API_DTO_MAP)} 个 API-DTO 映射")
except Exception as e:
    print(f"获取 OpenAPI 规范失败: {e}")
    print("将使用静态映射作为备选")
    # 静态备选映射（基于已知接口）
    API_DTO_MAP = {
        "/platform/user/save": {"dto": "PlatformUserSaveReqDto", "required_fields": ["userName", "realName", "sex", "roleGroupId", "status"], "summary": "保存平台用户", "method": "POST"},
        "/platform/user/edit": {"dto": "PlatformUserEditReqDto", "required_fields": ["id", "userName", "realName", "sex", "roleGroupId", "status"], "summary": "编辑平台用户", "method": "POST"},
        "/platform/user/changeStatus": {"dto": "PlatformUserStatusReqDto", "required_fields": ["id", "status"], "summary": "修改用户状态", "method": "POST"},
        "/platform/user/delete": {"dto": "IdReqDto", "required_fields": ["id"], "summary": "删除用户", "method": "POST"},
        "/platform/user/detail": {"dto": "IdReqDto", "required_fields": ["id"], "summary": "查询用户详情", "method": "POST"},
        "/platform/knowledge/save": {"dto": "KnowledgeSaveReqDto", "required_fields": ["title", "content", "consultType", "displayPosition", "applicableArea"], "summary": "保存知识库", "method": "POST"},
        "/platform/knowledge/delete": {"dto": "IdReqDto", "required_fields": ["id"], "summary": "删除知识库", "method": "POST"},
        "/platform/businessScope/add": {"dto": "BusinessScopeAddReqDto", "required_fields": ["scopeName"], "summary": "添加经营范围", "method": "POST"},
        "/platform/pricing/updatePricing": {"dto": "ServicePricingUpdateReqDto", "required_fields": ["serviceItemId", "amount", "areaList"], "summary": "更新定价", "method": "POST"},
        "/platform/pricing/treeByAreas": {"dto": "ServicePricingAreaTreeQueryReqDto", "required_fields": ["serviceItemId", "areaList"], "summary": "按地区查询定价树", "method": "POST"},
        "/platform/serverUser/save": {"dto": "ServerUserSaveReqDto", "required_fields": ["companyName", "unifiedSocialCode", "officeAddress", "serviceArea", "contactPerson", "contactPhone", "serviceItems"], "summary": "保存服务商", "method": "POST"},
        "/sys/login": {"dto": "LoginReqDto", "required_fields": ["loginType", "password", "smsCode", "username", "webType"], "summary": "登录", "method": "POST"},
        "/sys/logout": {"dto": "LogoutReqDto", "required_fields": [], "summary": "登出", "method": "POST"},
        "/api/worker-sign/worker-save": {"dto": "WorkerSaveReqDto", "required_fields": ["name", "phone", "certNum", "certFrontPhoto", "certBackPhoto", "address"], "summary": "工人信息保存", "method": "POST"},
        "/api/worker-sign/worker-sign-save": {"dto": "WorkerSignReqDto", "required_fields": [], "summary": "工人入驻签署", "method": "POST"},
    }

# ---------- 1. 解析 junit，得到失败用例 ----------
tree = ET.parse(JUNIT)
root = tree.getroot()
suites = root.findall("testsuite")
if suites:
    total = sum(int(float(s.get("tests", 0))) for s in suites)
    fail = sum(int(float(s.get("failures", 0))) for s in suites)
    err = sum(int(float(s.get("errors", 0))) for s in suites)
    skip = sum(int(float(s.get("skipped", 0))) for s in suites)
else:
    total = int(float(root.get("tests", 0)))
    fail = int(float(root.get("failures", 0)))
    err = int(float(root.get("errors", 0)))
    skip = int(float(root.get("skipped", 0)))

failures = []
for tc in root.iter("testcase"):
    f = tc.find("failure")
    if f is None:
        f = tc.find("error")
    if f is None:
        continue
    cls = tc.get("classname", "")
    name = tc.get("name", "")
    msg = " ".join((f.text or "").split())
    failures.append({"nodeid": f"{cls}::{name}", "cls": cls, "name": name, "msg": msg})

# ---------- 2. 加载真实请求/响应 ----------
cap = json.load(open(CAP, "r", encoding="utf-8"))

def get_io(nodeid):
    method = nodeid.split("::")[-1]
    reqs = cap.get(nodeid) or next((v for k, v in cap.items() if k.endswith("::" + method)), None)
    if not reqs:
        return None, None, None
    last = reqs[-1]
    body = last.get("body")
    resp = last.get("response", {})
    inp = body if body is not None else None
    robj = resp.get("json")
    if isinstance(robj, (dict, list)):
        out = robj
    elif robj is None:
        out = {"_http_status": resp.get("status")}
    else:
        out = robj
    return inp, out, last.get("url", "")

# ---------- 3. 分类 + 提取字段/签名（对齐历史 existing_bugs.json） ----------
def norm_path(url):
    if "://" in url:
        return "/" + url.split("://", 1)[1].split("/", 1)[1]
    return url

def get_api_info(api_path):
    """根据 API 路径获取 DTO 信息"""
    # 尝试精确匹配
    if api_path in API_DTO_MAP:
        return API_DTO_MAP[api_path]
    
    # 尝试模糊匹配（去除查询参数等）
    clean_path = api_path.split("?")[0].rstrip("/")
    if clean_path in API_DTO_MAP:
        return API_DTO_MAP[clean_path]
    
    # 尝试添加 / 前缀
    if not api_path.startswith("/") and "/" + api_path in API_DTO_MAP:
        return API_DTO_MAP["/" + api_path]
    
    return None

def build_description(category, field, api_info, extra_info=""):
    """构建详细的 Bug 描述，整合 OpenAPI 信息"""
    if api_info:
        dto = api_info.get("dto", "未知")
        required = api_info.get("required_fields", [])
        summary = api_info.get("summary", "")
        
        if category == "required_field_validation":
            if field in required:
                return f"OpenAPI 规范中 {dto} 标记 {field} 为必填项，但传 null 时后端未做校验，返回成功"
            else:
                return f"字段 {field} 缺失未校验，OpenAPI 规范 {dto} 中该字段{'是' if field in required else '不是'}必填项，返回成功"
        
        elif category == "existence_validation":
            return f"对不存在记录操作未返回失败，OpenAPI 规范 {dto} 标记 {field} 为必填项，但未校验存在性"
        
        elif category == "boundary_value":
            return f"{field} 边界/格式值未校验，OpenAPI 规范 {dto} 标记 {field} 为必填项，需增加边界值校验"
        
        elif category in ("security_sql_injection", "security_xss"):
            vuln_type = "SQL 注入" if "sql" in category else "XSS"
            return f"{field} 字段未过滤 {vuln_type} payload，OpenAPI 规范 {dto} 定义了该字段，后端接受并返回成功"
        
        elif category == "logic_bug":
            if "404" in extra_info or "资源不存在" in extra_info:
                return f"接口返回 404，OpenAPI 规范 {dto} 定义了该接口，疑似路径变更或后端查询逻辑问题"
            elif "token" in field.lower():
                return f"未校验 Token，OpenAPI 规范 {dto} 定义了认证机制，但后端未做校验"
            else:
                return f"接口逻辑异常，OpenAPI 规范 {dto} 定义了标准行为，但实际返回异常"
        else:
            return f"字段 {field} 存在问题，OpenAPI 规范 {dto} 定义了该接口{summary}，需要人工确认"
    else:
        # 无 API 信息时的降级描述
        if category == "required_field_validation":
            return f"必填字段 {field} 缺失未校验，返回成功"
        elif category == "existence_validation":
            return f"对不存在记录操作未返回失败"
        elif category == "boundary_value":
            return f"{field} 边界/格式值未校验"
        elif category in ("security_sql_injection", "security_xss"):
            vuln_type = "SQL 注入" if "sql" in category else "XSS"
            return f"{field} 字段未过滤 {vuln_type} payload，后端接受并返回成功"
        elif category == "logic_bug":
            return extra_info or "接口逻辑异常"
        else:
            return "需人工确认"

def snake_to_camel(field_name):
    """将下划线分隔的字段名转换为驼峰式
    
    例如: area_list -> areaList, cert_num -> certNum
    """
    if not field_name or "_" not in field_name:
        return field_name
    parts = field_name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])

def infer(nodeid, cls, name, msg):
    """返回 (category_key, display_section, api_path, field, tag, severity, description)"""
    module = cls.split(".")[1] if "." in cls else cls
    low = name.lower()
    
    # 先推断 API 路径
    api_path_hint = f"/{module.replace('_module', '')}"
    
    # 测试脚本问题（非后端缺陷）：服务方模块地址校验
    if module == "service_provider_module" and "01000006" in msg:
        return ("environment", "环境限制（非 Bug）", "POST /platform/serverUser/*",
                "officeAddress", "script", "low",
                "后端已增加公司地址必填校验(code 01000006)，测试未传地址导致批量失败，属测试脚本问题")
    
    # 推断具体 API 路径
    actual_api_path = ""
    for path in API_DTO_MAP.keys():
        if module.replace("_module", "") in path or path.endswith(module.replace("_module", "")):
            actual_api_path = path
            break
    
    api_info = get_api_info(actual_api_path) if actual_api_path else None
    
    if "sql_injection" in low:
        field = "title" if "scope_name" not in low and "businessscope" not in module else ("scopeName" if "scope" in low else "title")
        if "knowledge" in module or "scope" in low:
            field = "scopeName" if "scope" in low else "title"
        api = "POST /platform/knowledge/save" if "knowledge" in module else "POST /platform/businessScope/add"
        # 获取实际的 API 信息
        actual_info = get_api_info(api)
        desc = build_description("security_sql_injection", field, actual_info)
        return ("security_sql_injection", "安全漏洞（SQL 注入 / XSS）", api, field, "SQL", "high", desc)
    
    if "xss" in low:
        field = "content" if "content" in low else "title"
        api = "POST /platform/knowledge/save"
        actual_info = get_api_info(api)
        desc = build_description("security_xss", field, actual_info)
        return ("security_xss", "安全漏洞（SQL 注入 / XSS）", api, field, "XSS", "high", desc)
    
    if "404" in msg:
        api = f"POST /{module.replace('_module','')}/*"
        actual_info = get_api_info(actual_api_path) if actual_api_path else None
        desc = build_description("logic_bug", "id", actual_info, "接口返回 HTTP 404 / 资源不存在")
        return ("logic_bug", "接口逻辑 Bug", api, "id", "exception", "high", desc)
    
    if "code': '02'" in msg or 'code":"02' in msg:
        api = "POST /api/worker-sign/*"
        actual_info = get_api_info("/api/worker-sign/worker-save") or get_api_info("/api/worker-sign/worker-sign-save")
        desc = build_description("logic_bug", "uuid", actual_info, "接口返回 code:02 系统繁忙（未捕获异常）")
        return ("logic_bug", "接口逻辑 Bug", api, "uuid", "exception", "high", desc)
    
    if "Expected failure" in msg or ("code': '00'" in msg and "got success" in msg):
        # 无 Token 登出
        if "without_token" in low or "no_token" in low:
            api = "POST /sys/logout"
            actual_info = get_api_info("/sys/logout")
            desc = build_description("logic_bug", "token", actual_info)
            return ("logic_bug", "接口逻辑 Bug", api, "token", "notoken", "high", desc)
        
        # 不存在记录操作
        if "non_existing" in low or "not_exist" in low:
            api = f"POST /{module.replace('_module','')}/*"
            actual_info = get_api_info(actual_api_path) if actual_api_path else None
            desc = build_description("existence_validation", "id", actual_info)
            return ("existence_validation", "存在性校验 Bug", api, "id", "nonexist", "high", desc)
        
        # 无记录更新（如 test_update_pricing_no_record）
        if "no_record" in low:
            api = f"POST /{module.replace('_module','')}/*"
            actual_info = get_api_info(actual_api_path) if actual_api_path else None
            desc = build_description("logic_bug", "id", actual_info, "未导入数据时更新返回成功")
            return ("logic_bug", "接口逻辑 Bug", api, "id", "no record", "high", desc)
        
        # 边界值测试用例（如 test_pricing_amount_zero, test_pricing_amount_negative）
        if ("amount" in low or "zero" in low or "boundary" in low or "negative" in low or "minus" in low) and not "invalid" in low:
            fld = "amount"
            tag = "0" if "zero" in low else ("-1" if ("negative" in low or "minus" in low) else "boundary")
            category = "boundary_value"
            section = "边界值"
            api = f"POST /{module.replace('_module','')}/*"
            actual_info = get_api_info(actual_api_path) if actual_api_path else None
            desc = build_description(category, fld, actual_info)
            return (category, section, api, fld, tag, "high", desc)
        
        # 缺少必填项（如 test_get_pricing_tree_by_areas_missing_area_list）
        m = re.search(r"missing_(\w+)", low)
        if m:
            fld = snake_to_camel(m.group(1))
            api = f"POST /{module.replace('_module','')}/*"
            actual_info = get_api_info(actual_api_path) if actual_api_path else None
            desc = build_description("required_field_validation", fld, actual_info)
            return ("required_field_validation", "必填项校验 Bug", api, fld, "missing", "high", desc)
        
        if "invalid" in low:
            fld = "amount" if ("amount" in low or "zero" in low or "boundary" in low) else ("phone" if "phone" in low else ("certNum" if "cert" in low else "field"))
            tag = "boundary0" if fld == "amount" else "missing"
            category = "boundary_value" if fld == "amount" else "required_field_validation"
            section = "边界值" if fld == "amount" else "必填项校验 Bug"
            api = f"POST /{module.replace('_module','')}/*"
            actual_info = get_api_info(actual_api_path) if actual_api_path else None
            desc = build_description(category, fld, actual_info)
            return (category, section, api, fld, tag, "high", desc)
        
        # 默认识别为必填项缺失
        fld = "field"
        api = f"POST /{module.replace('_module','')}/*"
        actual_info = get_api_info(actual_api_path) if actual_api_path else None
        desc = build_description("required_field_validation", fld, actual_info)
        return ("required_field_validation", "必填项校验 Bug", api, fld, "missing", "high", desc)
    
    if "without_token" in low or "no token" in msg.lower():
        api = "POST /sys/logout"
        actual_info = get_api_info("/sys/logout")
        desc = build_description("logic_bug", "token", actual_info)
        return ("logic_bug", "接口逻辑 Bug", api, "token", "notoken", "high", desc)
    
    return ("unknown", "其他", "POST /" + module, "field", "other", "medium", "需人工确认")

# 历史签名：用于去重关联
# existing_bugs.json 格式: "POST /path_field tag"
def parse_existing_key(key):
    """解析 existing_bugs.json 的 key
    key 格式: "POST /platform/user/save_status null"
    返回: ("/platform/user/save", "status", "missing")
    """
    # 分割 "METHOD /path_field tag"
    # 用第一个空格分离方法和路径
    parts = key.split(" ", 1)
    if len(parts) < 2:
        return "", "", None
    
    rest = parts[1]  # "/path_field tag"
    
    # 分离路径部分和 tag
    # 格式: "/path_field tag" 或 "/path_field"
    space_idx = rest.rfind(" ")
    if space_idx > 0:
        path_field_with_underscore = rest[:space_idx]  # "/path_field"
        tag_raw = rest[space_idx+1:]   # "tag"
    else:
        path_field_with_underscore = rest
        tag_raw = None
    
    # 分离路径和字段: "/path_field" -> ("/path", "field")
    # 用最后一个 _ 分离 path 和 field
    # 注意：path_field_with_underscore 格式是 "/platform/user/save_status"
    last_underscore = path_field_with_underscore.rfind("_")
    if last_underscore > 0:
        path = path_field_with_underscore[:last_underscore]  # "/platform/user/save"
        field = path_field_with_underscore[last_underscore+1:]  # "status"
    else:
        path = path_field_with_underscore
        field = ""
    
    # 标准化 tag
    norm = {"null": "missing", "999999": "nonexist", "SQL注入": "SQL", "XSS": "XSS",
            "0": "boundary0", "-1": "boundary-1", "no record": "norecord", "no token": "notoken"}
    normalized_tag = norm.get(tag_raw, tag_raw) if tag_raw else None
    
    return path, field, normalized_tag

# 统一的 API path 规范化（用于 match_existing）
def extract_path(api_path):
    """从 API path 中提取纯路径部分
    输入: "POST /platform/user/save" 或 "GET /api/test"
    输出: "/platform/user/save"
    """
    # 如果包含方法前缀，去除它
    path = api_path.strip()
    for method in ["POST ", "GET ", "PUT ", "DELETE ", "PATCH "]:
        if path.startswith(method):
            path = path[len(method):]
            break
    # 如果包含 URL scheme，提取路径
    if "://" in path:
        path = "/" + path.split("://", 1)[1].split("/", 1)[1]
    return path.rstrip("/") or path

# 加载已有签名
existing_sigs = {}  # (path, field, tag_or_None) -> yunxiao workitem_id
if os.path.exists(EXISTING):
    ej = json.load(open(EXISTING, "r", encoding="utf-8"))
    for k, v in ej.items():
        p, f, t = parse_existing_key(k)
        # 安全类 bug 保留 tag，非安全类统一为 None
        normalized_tag = t if t in ("SQL", "XSS") else None
        existing_sigs[(p, f, normalized_tag)] = v.get("id")

def match_existing(api_path, field, tag, is_security):
    """匹配已提交的 bug
    api_path: "POST /platform/user/save"
    field: "status"
    tag: "SQL" / "XSS" / "missing" / "nonexist" / ...
    is_security: True / False
    """
    path = extract_path(api_path)
    if is_security:
        return existing_sigs.get((path, field, tag))
    return existing_sigs.get((path, field, None))

# ---------- 4. 加载 bug_tracking，去重更新 ----------
data = json.load(open(TRACKING, "r", encoding="utf-8"))
bugs = [b for b in data.get("bugs", []) if b.get("id", "BUG-000") and int(b["id"].split("-")[1]) <= 17]
by_yunxiao = {b.get("yunxiao", {}).get("workitem_id"): b for b in bugs}

classified = []
new_bugs = []
max_num = 17
for f in failures:
    cat, section, api, field, tag, sev, desc = infer(f["nodeid"], f["cls"], f["name"], f["msg"])
    if cat == "environment":
        classified.append({"env": True, "section": section, "method": f["name"], "desc": desc, "api": api})
        continue
    inp, out, url = get_io(f["nodeid"])
    real_api = url if "://" in url else api
    is_sec = cat in ("security_sql_injection", "security_xss")
    # 使用实际的 API 路径进行匹配
    yx_id = match_existing(real_api, field, tag, is_sec)
    if yx_id and yx_id in by_yunxiao:
        b = by_yunxiao[yx_id]
        b["request_body"] = inp
        b["response_body"] = out
        b["status"] = "needs_retest"
        b["last_execution"] = EXEC_ID
        b["last_seen"] = TODAY
        # 更新 field 和 tag（如果缺失）
        if field and not b.get("field"):
            b["field"] = field
        if tag and not b.get("tag"):
            b["tag"] = tag
        classified.append({"bug": b, "section": section, "real_api": real_api, "inp": inp, "out": out})
    else:
        max_num += 1
        bid = f"BUG-{max_num:03d}"
        b = {
            "id": bid, "execution_id": EXEC_ID, "category": cat,
            "title": f"{f['cls'].split('.')[1]}/{f['name']}",
            "api_path": real_api, "test_case": f["name"], "nodeid": f["nodeid"],
            "description": desc, "severity": sev, "status": "needs_retest",
            "request_body": inp, "response_body": out,
            "field": field, "tag": tag,
            "yunxiao": {"submitted": False, "workitem_id": None, "title": None,
                        "submitted_date": None, "url": None},
            "fix": {"fixed": False, "fixed_date": None, "verified": False, "verified_date": None},
            "created_at": datetime.now().isoformat(),
        }
        bugs.append(b)
        new_bugs.append(bid)
        classified.append({"bug": b, "section": section, "real_api": real_api, "inp": inp, "out": out})

data["bugs"] = bugs
data.setdefault("executions", []).append({
    "execution_id": EXEC_ID, "date": TODAY, "environment": ENV,
    "test_suite": f"{total} tests, {fail} failed, {err} error, {skip} skipped (pass rate {100.0*(total-fail-err)/total:.1f}%)",
    "notes": "全量接口测试；清理业务数据已开启；不提交云效，仅标记 needs_retest",
    "created_at": datetime.now().isoformat(),
})
data["meta"]["last_updated"] = TODAY
json.dump(data, open(TRACKING, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------- 5. 生成历史格式 bug_list.md（真实入参/出参） ----------
SECTIONS = [
    ("必填项校验 Bug", "required_field_validation"),
    ("存在性校验 Bug", "existence_validation"),
    ("接口逻辑 Bug", "logic_bug"),
    ("安全漏洞（SQL 注入 / XSS）", "security_sql_injection"),
    ("边界值", "boundary_value"),
    ("环境限制（非 Bug）", "environment"),
]
real_bugs = [c for c in classified if not c.get("env")]
env_bugs = [c for c in classified if c.get("env")]

def compact(o):
    try:
        return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        return str(o)

lines = []
lines.append("# 后端 Bug 列表（需要复测）\n")
lines.append(f"> 依据：{ENV}/doc.html#/home  ")
lines.append(f"> 测试时间：{TODAY}  ")
lines.append(f"> 测试环境：{ENV}  ")
lines.append(f"> 测试套件：{total} passed+failed，{fail} failed（清理业务数据已开启）  ")
lines.append(f"> 标记：needs_retest（未提交云效）  ")
lines.append(f"> 共 {len(real_bugs)} 个真实后端缺陷（入参/出参为真实捕获报文）\n")
lines.append("---\n")

sec = 0
for sname, skey in SECTIONS:
    group = [c for c in classified if c.get("section") == sname]
    if not group:
        continue
    sec += 1
    lines.append(f"## {sec}. {sname}\n")
    for i, c in enumerate(group, 1):
        if c.get("env"):
            lines.append(f"### 限制 {sec}-{i}：{c['method']}\n")
            lines.append("| 项目 | 内容 |")
            lines.append("|------|------|")
            lines.append(f"| **请求地址** | `{c['api']}` |")
            lines.append(f"| **说明** | {c['desc']} |")
            lines.append("")
            continue
        b = c["bug"]
        lines.append(f"### Bug {sec}-{i}：{b.get('title', b.get('test_case',''))}\n")
        lines.append("| 项目 | 内容 |")
        lines.append("|------|------|")
        lines.append(f"| **缺陷ID** | {b['id']} |")
        lines.append(f"| **严重程度** | {b.get('severity','high')} |")
        lines.append(f"| **请求地址** | `{c['real_api']}` |")
        lines.append(f"| **入参** | `{compact(c['inp']) if c['inp'] is not None else '（无请求体）'}` |")
        lines.append(f"| **出参** | `{compact(c['out']) if c['out'] is not None else '（无响应）'}` |")
        lines.append(f"| **Bug描述** | {b.get('description','')} |")
        lines.append("")

# 汇总
from collections import Counter
cnt = Counter(c["section"] for c in real_bugs)
lines.append("---\n")
lines.append("## Bug 汇总\n")
lines.append("| 类别 | Bug 数量 |")
lines.append("|------|----------|")
order = ["必填项校验 Bug", "存在性校验 Bug", "接口逻辑 Bug", "安全漏洞（SQL 注入 / XSS）", "边界值"]
for s in order:
    if cnt.get(s):
        lines.append(f"| {s} | {cnt[s]} |")
if env_bugs:
    lines.append(f"| 环境限制（非 Bug） | {len(env_bugs)} |")
lines.append(f"| **后端 Bug 总计** | **{len(real_bugs)}** |")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))

print(f"TOTAL={total} FAIL={fail} REAL_BUGS={len(real_bugs)} ENV={len(env_bugs)} NEW={len(new_bugs)}")
print("NEW_IDS=", new_bugs)

# ---------- 6. 可选：提交到云效 ----------
if args.submit_to_yunxiao and new_bugs:
    print("\n" + "=" * 60)
    print("🚀 准备提交 Bug 到云效...")
    print("=" * 60)
    
    if args.dry_run:
        print("(预览模式，不会实际提交)")
    
    # 调用 yunxiao_submitter.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yunxiao_submitter.py")
    cmd = [sys.executable, script_path]
    if args.dry_run:
        cmd.append("--dry-run")
    if EXEC_ID:
        cmd.extend(["--execution-id", EXEC_ID])
    
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        if result.returncode != 0:
            print(f"⚠️ 云效提交脚本返回非零退出码: {result.returncode}")
        else:
            print("✅ 云效提交完成")
    except Exception as e:
        print(f"❌ 调用云效提交脚本失败: {e}")
        print("请手动运行: python bugs/yunxiao_submitter.py --execution-id", EXEC_ID)
elif not args.submit_to_yunxiao:
    print("\n💡 提示: 使用 --submit-to-yunxiao 参数可自动提交到云效")
    print(f"   例如: python bugs/collect_test_bugs.py --submit-to-yunxiao")
    print(f"   或:   python bugs/yunxiao_submitter.py --execution-id {EXEC_ID}")
