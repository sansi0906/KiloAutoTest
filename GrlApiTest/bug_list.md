# 后端 Bug 列表

> 依据：http://172.16.1.165:9200/doc.html#/home  
> 测试时间：2026-07-31  
> 测试环境：E:\GrlApiTest  
> 测试套件：217 passed, 19 failed（含 10 个安全漏洞 + 8 个后端 Bug + 1 个环境限制）

---

## 1. 必填项校验 Bug

### Bug 1-1：保存用户时缺少 status 必填项，后端未校验

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/user/save |
| **入参** | `{"userName": "174xxxxxxxx", "realName": "测试用户", "sex": 1, "roleGroupId": 5, "status": null}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | OpenAPI 规范中 `PlatformUserSaveReqDto` 标记 `status` 为必填项，但传 `null` 时后端未做校验，返回成功 code:00 |

### Bug 1-2：区域定价树查询缺少 areaList 必填项，后端未校验

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/pricing/treeByAreas |
| **入参** | `{"serviceItemId": 1, "areaList": null}` |
| **出参** | `{"code": "00", "message": "成功", "data": {"serviceItemId": "151", "serviceItemName": null, "servicePricingTree": []}}` |
| **Bug描述** | OpenAPI 规范中 `ServicePricingAreaTreeQueryReqDto` 标记 `areaList` 为必填项，但传 `null` 时后端未做校验，返回成功 code:00 |

### Bug 1-3：密码登录模式下缺少 smsCode 必填项，后端未校验

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /sys/login |
| **入参** | `{"username": "admin", "password": "xxxx", "loginType": 1, "webType": 0, "smsCode": null}` |
| **出参** | `{"code": "00", "message": "成功", "data": {"token": "xxx"}}` |
| **Bug描述** | OpenAPI 规范中 `LoginReqDto` 标记 `smsCode` 为必填项，但密码登录模式下传 `null` 时后端未做校验，返回成功 code:00 |

---

## 2. 存在性校验 Bug（删除/编辑/改状态未校验记录是否存在）

### Bug 2-1：删除不存在的用户，返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/user/delete |
| **入参** | `{"id": 999999}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 删除用户前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-2：编辑不存在的用户，返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/user/edit |
| **入参** | `{"id": 999999, "userName": "174xxxxxxxx", "realName": "测试用户", "sex": 1, "roleGroupId": 5, "status": 1}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 编辑用户前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-3：修改不存在的用户状态，返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/user/changeStatus |
| **入参** | `{"id": 999999, "status": 0}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 修改用户状态前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-4：删除不存在的服务商，返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/serverUser/delete |
| **入参** | `{"id": 999999}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 删除服务商前未校验服务商是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-5：删除不存在的知识库，返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/knowledge/delete |
| **入参** | `{"id": 999999}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 删除知识库前未校验知识库是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

---

## 3. 接口逻辑 Bug

### Bug 3-1：经营范围详情接口对所有 ID 返回 404

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/businessScope/detail |
| **入参（存在的 ID）** | `{"id": 1}` |
| **出参** | HTTP 404 / `{"code": "03", "message": "服务不存在", "data": null}` |
| **Bug描述** | detail 接口对所有 ID（包括数据库中存在的 ID）均返回 HTTP 404 或 code:03，属于后端查询逻辑 Bug |

### Bug 3-2：无 Token 登出返回成功

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /sys/logout |
| **入参** | 无 Token 请求头 |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 登出接口未校验 Token，无 Token 时返回成功 code:00，预期应返回认证失败 |

---

## 4. 安全漏洞（SQL 注入 / XSS）

### Bug 4-1：知识库标题存在 SQL 注入漏洞

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/knowledge/save |
| **入参** | `{"title": "' OR '1'='1", "content": "TestContent", "consultType": 1, "displayPosition": [0, 1], "applicableArea": [...]}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-2：知识库标题存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/knowledge/save |
| **入参** | `{"title": "<script>alert('xss')</script>", "content": "TestContent", ...}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 知识库 title 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-3：知识库内容存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /platform/knowledge/save |
| **入参** | `{"title": "TestTitle", "content": "<script>alert('xss')</script>", ...}` |
| **出参** | `{"code": "00", "message": "成功", "data": null}` |
| **Bug描述** | 知识库 content 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

---

## 5. 环境限制（非 Bug）

### 限制 5-1：短信发送每日上限

| 项目 | 内容 |
|------|------|
| **请求地址** | POST /sys/sendCode |
| **入参** | `{"phone": "17695729351"}` |
| **出参** | `{"code": "01000044", "message": "the number of sms messages sent from a single mobile number every day exceeds the upper limit", "data": null}` |
| **说明** | 测试手机号 17695729351 当日发送短信次数超过系统上限，属于测试环境限制，非后端 Bug |

---

## Bug 汇总

| 类别 | Bug 数量 | 涉及接口 |
|------|----------|----------|
| 必填项校验 Bug | 3 | /platform/user/save, /platform/pricing/treeByAreas, /sys/login |
| 存在性校验 Bug | 5 | /platform/user/delete, /platform/user/edit, /platform/user/changeStatus, /platform/serverUser/delete, /platform/knowledge/delete |
| 接口逻辑 Bug | 2 | /platform/businessScope/detail, /sys/logout |
| 安全漏洞（SQL 注入 / XSS） | 3 | /platform/knowledge/save |
| **后端 Bug 总计** | **13** | - |
| 环境限制 | 1 | /sys/sendCode |
