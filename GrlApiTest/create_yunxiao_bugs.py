"""
create_yunxiao_bugs.py - 自动创建云效 Bug（带去重逻辑）

接口地址：POST https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{organizationId}/workitems
认证方式：Header x-yunxiao-token: pt-个人访问令牌
文档：https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem
"""

import hashlib
import json
import os
import sys
import time

import requests

# ========== 云效配置 ==========
YUNXIAO_TOKEN = "pt-o9Bs7j157DMSrxaolmxiz9EJ_4028aa2b-557c-4b2d-8ea8-a0343bb0077a"
ORGANIZATION_ID = "681dc36041ad8bef38ae0822"
PROJECT_ID = "6bc965ffd5ac5a28dfb230bb82"
WORKITEM_TYPE_ID = "37da3a07df4d08aef2e3b393"
ASSIGNED_TO = "64d1cedb87b86df20e7f4d06"
SERIOUS_LEVEL = "4471da138fe64b3b819b6be0ce"
# =============================

URL = f"https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{ORGANIZATION_ID}/workitems"

HEADERS = {
    "Content-Type": "application/json",
    "x-yunxiao-token": YUNXIAO_TOKEN,
}

CATEGORY = "Bug"

# 已有 Bug 记录，用于去重
# 格式: { "接口地址_入参_hash": {"id": "云效工作项ID", "title": "标题"} }
EXISTING_BUGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "existing_bugs.json")

# 默认已有 Bug 列表（从之前创建的 Bug 中整理）
DEFAULT_EXISTING_BUGS = {
    "POST /platform/user/save_status null": {"id": "dce2f925faa3b53603db2460d1", "title": "【接口测试】POST /platform/user/save 必填项 status 未校验"},
    "POST /platform/user/delete_id 999999": {"id": "d389fd96cef59b15f41251521d", "title": "【接口测试】POST /platform/user/delete 删除不存在的用户返回成功"},
    "POST /platform/pricing/treeByAreas_areaList null": {"id": "5dd908f5c2582eefefa26adf27", "title": "【接口测试】POST /platform/pricing/treeByAreas 必填项 areaList 未校验"},
    "POST /sys/login_smsCode null": {"id": "5ebc8cea3ea74d3ce7759910c5", "title": "【接口测试】POST /sys/login 密码登录模式下必填项 smsCode 未校验"},
    "POST /platform/user/edit_id 999999": {"id": "d39c228b55f204f2a43bd63077", "title": "【接口测试】POST /platform/user/edit 编辑不存在的用户返回成功"},
    "POST /platform/user/changeStatus_id 999999": {"id": "8b90551cfe42f9f883970c8af8", "title": "【接口测试】POST /platform/user/changeStatus 修改不存在的用户状态返回成功"},
    "POST /platform/serverUser/delete_id 999999": {"id": "ac11fdb3887d2de0ff95e4589c", "title": "【接口测试】POST /platform/serverUser/delete 删除不存在的服务商返回成功"},
    "POST /platform/knowledge/delete_id 999999": {"id": "499106236bc668aea8ba74276e", "title": "【接口测试】POST /platform/knowledge/delete 删除不存在的知识库返回成功"},
    "POST /platform/businessScope/detail_id 1": {"id": "99cefbe9af3c614deeb024948c", "title": "【接口测试】POST /platform/businessScope/detail 对所有ID返回404"},
    "POST /sys/logout_no token": {"id": "183e0c66fd1600590ed01fdf00", "title": "【接口测试】POST /sys/logout 无Token登出返回成功"},
    "POST /platform/knowledge/save_title SQL注入": {"id": "0999a0cb97ce7cb683a0be9990", "title": "【安全测试】POST /platform/knowledge/save title 字段 SQL 注入"},
    "POST /platform/knowledge/save_title XSS": {"id": "a0451a395b149aeacf2e05f6c9", "title": "【安全测试】POST /platform/knowledge/save title 字段 XSS 注入"},
    "POST /platform/knowledge/save_content XSS": {"id": "0e07fd9ffe9286a3c1331bc4a5", "title": "【安全测试】POST /platform/knowledge/save content 字段 XSS 注入"},
    "POST /platform/businessScope/add_scopeName SQL注入": {"id": "e27c0ff9f0402137a8cbb6cdaa", "title": "【安全测试】POST /platform/businessScope/add scopeName 字段 SQL 注入"},
    "POST /platform/pricing/updatePricing_amount 0": {"id": "56c9a19e92378dc9c635f46e8e", "title": "【边界测试】POST /platform/pricing/updatePricing amount=0 未校验"},
    "POST /platform/pricing/updatePricing_amount -1": {"id": "69896f6a2dc6d3e391410fc4bf", "title": "【边界测试】POST /platform/pricing/updatePricing amount=-1 未校验"},
    "POST /platform/pricing/updatePricing_no record": {"id": "4d1dda9da0d84b86f7640b8ff5", "title": "【接口测试】POST /platform/pricing/updatePricing 未导入定价数据更新返回成功"},
}


def load_existing_bugs():
    """加载已有 Bug 记录"""
    if os.path.exists(EXISTING_BUGS_FILE):
        with open(EXISTING_BUGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_EXISTING_BUGS.copy()


def save_existing_bugs(bugs):
    """保存 Bug 记录"""
    with open(EXISTING_BUGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bugs, f, ensure_ascii=False, indent=2)


def generate_bug_key(api_path, request_body):
    """生成 Bug 唯一键：接口地址 + 入参"""
    key = f"{api_path}_{request_body}"
    return hashlib.md5(key.encode()).hexdigest()


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
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

    if resp.status_code == 200:
        data = resp.json()
        workitem_id = data.get("id")
        print(f"[OK] 创建成功，缺陷ID：{workitem_id}")
        print(f"链接：https://devops.aliyun.com/workitem/{workitem_id}?organizationId={ORGANIZATION_ID}")
        return workitem_id
    else:
        print("[FAIL] 创建失败")
        return None


def format_bug_description(bug):
    """格式化 Bug 描述，包含请求地址、入参、出参、问题"""
    desc = f"""## Bug 描述

{bug.get('description', '')}

---

## 复现信息

| 项目 | 内容 |
|------|------|
| **请求地址** | {bug.get('request_url', '')} |
| **入参** | ```json\n{bug.get('request_body', '')}``` |
| **出参** | ```json\n{bug.get('response_body', '')}``` |
| **问题** | {bug.get('problem', '')} |
| **测试环境** | http://172.16.1.165:9200 |
| **测试时间** | 2026-08-03 |

---

## 建议

{bug.get('suggestion', '建议后端增加必填项校验或存在性校验。')}
"""
    return desc


if __name__ == "__main__":
    # 加载已有 Bug 记录
    existing_bugs = load_existing_bugs()
    print(f"已加载 {len(existing_bugs)} 个已有 Bug 记录\n")

    bugs = [
        {
            "title": "【接口测试】POST /platform/pricing/treeByAreas 必填项 areaList 未校验",
            "description": "OpenAPI 规范中 ServicePricingAreaTreeQueryReqDto 标记 areaList 为必填项，但传 null 时后端未做校验，返回成功 code:00",
            "request_url": "POST /platform/pricing/treeByAreas",
            "request_body": '{"serviceItemId": 1, "areaList": null}',
            "response_body": '{"code": "00", "message": "成功", "data": {"serviceItemId": "151", "serviceItemName": null, "servicePricingTree": []}}',
            "problem": "必填项 areaList 传 null 时后端未校验，返回成功",
        },
        {
            "title": "【接口测试】POST /sys/login 密码登录模式下必填项 smsCode 未校验",
            "description": "OpenAPI 规范中 LoginReqDto 标记 smsCode 为必填项，但密码登录模式下传 null 时后端未做校验，返回成功 code:00",
            "request_url": "POST /sys/login",
            "request_body": '{"username": "admin", "password": "xxxx", "loginType": 1, "webType": 0, "smsCode": null}',
            "response_body": '{"code": "00", "message": "成功", "data": {"token": "xxx"}}',
            "problem": "必填项 smsCode 在密码登录模式下传 null 时后端未校验，返回成功",
        },
        {
            "title": "【接口测试】POST /platform/user/edit 编辑不存在的用户返回成功",
            "description": "编辑用户前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/user/edit",
            "request_body": '{"id": 999999, "userName": "174xxxxxxxx", "realName": "测试用户", "sex": 1, "roleGroupId": 5, "status": 1}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "编辑用户前未校验用户是否存在，传入不存在的 ID 返回成功",
        },
        {
            "title": "【接口测试】POST /platform/user/changeStatus 修改不存在的用户状态返回成功",
            "description": "修改用户状态前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/user/changeStatus",
            "request_body": '{"id": 999999, "status": 0}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "修改用户状态前未校验用户是否存在，传入不存在的 ID 返回成功",
        },
        {
            "title": "【接口测试】POST /platform/serverUser/delete 删除不存在的服务商返回成功",
            "description": "删除服务商前未校验服务商是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/serverUser/delete",
            "request_body": '{"id": 999999}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "删除服务商前未校验服务商是否存在，传入不存在的 ID 返回成功",
        },
        {
            "title": "【接口测试】POST /platform/knowledge/delete 删除不存在的知识库返回成功",
            "description": "删除知识库前未校验知识库是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/knowledge/delete",
            "request_body": '{"id": 999999}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "删除知识库前未校验知识库是否存在，传入不存在的 ID 返回成功",
        },
        {
            "title": "【接口测试】POST /platform/businessScope/detail 对所有ID返回404",
            "description": "detail 接口对所有 ID（包括数据库中存在的 ID）均返回 HTTP 404 或 code:03，属于后端查询逻辑 Bug",
            "request_url": "POST /platform/businessScope/detail",
            "request_body": '{"id": 1}',
            "response_body": 'HTTP 404 / {"code": "03", "message": "服务不存在", "data": null}',
            "problem": "detail 接口对所有 ID 均返回 404，包括存在的 ID",
        },
        {
            "title": "【接口测试】POST /sys/logout 无Token登出返回成功",
            "description": "登出接口未校验 Token，无 Token 时返回成功 code:00，预期应返回认证失败",
            "request_url": "POST /sys/logout",
            "request_body": "无 Token 请求头",
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "登出接口未校验 Token，无 Token 时返回成功",
        },
        {
            "title": "【安全测试】POST /platform/knowledge/save title 字段 SQL 注入",
            "description": "知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险",
            "request_url": "POST /platform/knowledge/save",
            "request_body": '{"title": "\' OR \'1\'=\'1", "content": "TestContent", "consultType": 1, "displayPosition": [0, 1], "applicableArea": [...]}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "title 字段未过滤 SQL 注入 payload，存在 SQL 注入风险",
        },
        {
            "title": "【安全测试】POST /platform/knowledge/save title 字段 XSS 注入",
            "description": "知识库 title 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险",
            "request_url": "POST /platform/knowledge/save",
            "request_body": '{"title": "<script>alert(\'xss\')</script>", "content": "TestContent", ...}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "title 字段未过滤 XSS payload，存在 XSS 风险",
        },
        {
            "title": "【安全测试】POST /platform/knowledge/save content 字段 XSS 注入",
            "description": "知识库 content 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险",
            "request_url": "POST /platform/knowledge/save",
            "request_body": '{"title": "TestTitle", "content": "<script>alert(\'xss\')</script>", ...}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "content 字段未过滤 XSS payload，存在 XSS 风险",
        },
        {
            "title": "【安全测试】POST /platform/businessScope/add scopeName 字段 SQL 注入",
            "description": "经营范围 scopeName 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险",
            "request_url": "POST /platform/businessScope/add",
            "request_body": '{"scopeName": "\' OR \'1\'=\'1", "remark": "TestRemark"}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "scopeName 字段未过滤 SQL 注入 payload，存在 SQL 注入风险",
        },
        {
            "title": "【边界测试】POST /platform/pricing/updatePricing amount=0 未校验",
            "description": "金额 amount=0 时后端未做校验，返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/pricing/updatePricing",
            "request_body": '{"serviceItemId": 1, "amount": 0, "areaList": [{"code": "110101000000", "level": "county", "name": "东城区"}]}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "金额为 0 时后端未校验，应禁止金额为 0 或负数",
        },
        {
            "title": "【边界测试】POST /platform/pricing/updatePricing amount=-1 未校验",
            "description": "金额 amount=-1 时后端未做校验，返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/pricing/updatePricing",
            "request_body": '{"serviceItemId": 1, "amount": -1, "areaList": [{"code": "110101000000", "level": "county", "name": "东城区"}]}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "金额为负数时后端未校验，应禁止金额为负数",
        },
        {
            "title": "【接口测试】POST /platform/pricing/updatePricing 未导入定价数据更新返回成功",
            "description": "对未导入定价数据的服务项目更新定价，后端未做校验返回成功 code:00，预期应返回失败",
            "request_url": "POST /platform/pricing/updatePricing",
            "request_body": '{"serviceItemId": 新建服务项ID, "amount": 150.0, "areaList": [{"code": "110101000000", "level": "county", "name": "东城区"}]}',
            "response_body": '{"code": "00", "message": "成功", "data": null}',
            "problem": "对不存在定价记录的服务项目更新定价，后端未校验返回成功",
        },
    ]

    new_bugs = []
    skipped_bugs = []

    for bug in bugs:
        # 生成唯一键
        bug_key = generate_bug_key(bug["request_url"], bug["request_body"])

        if bug_key in existing_bugs:
            skipped_bugs.append({
                "title": bug["title"],
                "existing_id": existing_bugs[bug_key]["id"],
            })
            print(f"[SKIP] 已存在 Bug，跳过: {bug['title']}")
            print(f"       已有 ID: {existing_bugs[bug_key]['id']}")
        else:
            new_bugs.append(bug)

    print(f"\n去重结果: 已有 {len(existing_bugs)} 个 Bug，跳过 {len(skipped_bugs)} 个，待创建 {len(new_bugs)} 个\n")

    if not new_bugs:
        print("没有新的 Bug 需要创建。")
        sys.exit(0)

    print(f"开始创建 {len(new_bugs)} 个新 Bug...\n")
    for i, bug in enumerate(new_bugs, 1):
        print(f"[{i}/{len(new_bugs)}] {bug['title']}")
        desc = format_bug_description(bug)
        workitem_id = create_bug(bug["title"], desc)

        if workitem_id:
            # 保存到已有 Bug 记录
            bug_key = generate_bug_key(bug["request_url"], bug["request_body"])
            existing_bugs[bug_key] = {
                "id": workitem_id,
                "title": bug["title"],
            }

        if i < len(new_bugs):
            time.sleep(1)
        print()

    # 保存更新后的 Bug 记录
    save_existing_bugs(existing_bugs)
    print(f"\nBug 记录已保存到: {EXISTING_BUGS_FILE}")
