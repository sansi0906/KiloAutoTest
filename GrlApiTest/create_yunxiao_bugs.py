"""
create_yunxiao_bugs.py - 自动创建云效 Bug

接口地址：POST https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{organizationId}/workitems
认证方式：Header x-yunxiao-token: pt-个人访问令牌
文档：https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem
"""

import requests
import json
import time

# ========== 云效配置 ==========
YUNXIAO_TOKEN = "pt-o9Bs7j157DMSrxaolmxiz9EJ_4028aa2b-557c-4b2d-8ea8-a0343bb0077a"
ORGANIZATION_ID = "681dc36041ad8bef38ae0822"
PROJECT_ID = "6bc965ffd5ac5a28dfb230bb82"
WORKITEM_TYPE_ID = "37da3a07df4d08aef2e3b393"
ASSIGNED_TO = "64d1cedb87b86df20e7f4d06"  # 负责人
SERIOUS_LEVEL = "4471da138fe64b3b819b6be0ce"  # 严重程度字段值
# =============================

URL = f"https://openapi-rdc.aliyuncs.com/oapi/v1/projex/organizations/{ORGANIZATION_ID}/workitems"

HEADERS = {
    "Content-Type": "application/json",
    "x-yunxiao-token": YUNXIAO_TOKEN,
}

CATEGORY = "Bug"


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
| **测试时间** | 2026-07-31 |

---

## 建议

{bug.get('suggestion', '建议后端增加必填项校验或存在性校验。')}
"""
    return desc


if __name__ == "__main__":
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
    ]

    print(f"开始创建 {len(bugs)} 个 Bug...\n")
    for i, bug in enumerate(bugs, 1):
        print(f"[{i}/{len(bugs)}] {bug['title']}")
        desc = format_bug_description(bug)
        create_bug(bug["title"], desc)
        if i < len(bugs):
            time.sleep(1)  # 避免请求过快
        print()
