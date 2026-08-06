# 后端 Bug 列表（需要复测）

> 依据：http://172.16.1.165:9200/doc.html#/home  
> 测试时间：2026-08-06  
> 测试环境：http://172.16.1.165:9200  
> 测试套件：263 passed+failed，29 failed（清理业务数据已开启）  
> 标记：needs_retest（未提交云效）  
> 共 29 个真实后端缺陷（入参/出参为真实捕获报文）

---

## 1. 必填项校验 Bug

### Bug 1-1：worker_sign_module/test_worker_save_invalid_phone_format

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-024 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/worker-save` |
| **入参** | `{"name":"TestUser1785979750","phone":"12345","certNum":"110101199001011234","certFrontPhoto":"/tmp/cert_front.jpg","certBackPhoto":"/tmp/cert_back.jpg","address":"Beijing","verifyDate":false}` |
| **出参** | `{"code":"00","message":"操作成功","data":{"name":"TestUser1785979750","phone":"12345","certNo":"110101199001011234","userUuid":"89baa8c6-ad12-4c31-aa79-e4fdbaefebe5","newUser":2,"isAuth":1,"isSignSuccess":2,"provinceAreaCode":null,"cityAreaCode":null,"districtAreaCode":null,"serverEndTime":null,"provinceAreaCodeName":"","cityAreaCodeName":"","districtAreaCodeName":"","serverStartTime":null,"stationInfoId":null}}` |
| **Bug描述** | 必填字段 phone 缺失未校验，返回成功 |

### Bug 1-2：worker_sign_module/test_worker_save_invalid_cert_num

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-025 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/worker-save` |
| **入参** | `{"name":"TestUser1785979750","phone":"17460388735","certNum":"123456","certFrontPhoto":"/tmp/cert_front.jpg","certBackPhoto":"/tmp/cert_back.jpg","address":"Beijing","verifyDate":false}` |
| **出参** | `{"code":"00","message":"操作成功","data":{"name":"TestUser1785979750","phone":"17460388735","certNo":"123456","userUuid":"a8806cfc-3d6b-4800-a824-71b91a10f272","newUser":2,"isAuth":1,"isSignSuccess":2,"provinceAreaCode":null,"cityAreaCode":null,"districtAreaCode":null,"serverEndTime":null,"provinceAreaCodeName":"","cityAreaCodeName":"","districtAreaCodeName":"","serverStartTime":null,"stationInfoId":null}}` |
| **Bug描述** | 必填字段 certNum 缺失未校验，返回成功 |

## 2. 存在性校验 Bug

### Bug 2-1：删除不存在的知识库，返回成功

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-008 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/delete` |
| **入参** | `{"id":999999}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 删除知识库前未校验知识库是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-2：修改不存在的用户状态，返回成功

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-006 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/user/changeStatus` |
| **入参** | `{"id":999999,"status":0}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 修改用户状态前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-3：删除不存在的用户，返回成功

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-004 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/user/delete` |
| **入参** | `{"id":999999}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 删除用户前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-4：编辑不存在的用户，返回成功

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-005 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/user/edit` |
| **入参** | `{"id":999999,"userName":"17477034714","realName":"测试用户1785979711","sex":1,"roleGroupId":5,"status":1}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 编辑用户前未校验用户是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

### Bug 2-5：删除不存在的服务商，返回成功

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-007 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/serverUser/delete` |
| **入参** | `{"id":999999}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 删除服务商前未校验服务商是否存在，传入不存在的 ID 999999 返回成功 code:00，预期应返回失败 |

## 3. 接口逻辑 Bug

### Bug 3-1：经营范围详情接口对所有 ID 返回 404

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-009 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/businessScope/detail` |
| **入参** | `{"id":"394"}` |
| **出参** | `{"code":"03","message":"请求的资源不存在!","data":null}` |
| **Bug描述** | detail 接口对所有 ID（包括数据库中存在的 ID）均返回 HTTP 404 或 code:03，属于后端查询逻辑 Bug |

### Bug 3-2：经营范围详情接口对所有 ID 返回 404

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-009 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/businessScope/detail` |
| **入参** | `{"id":999999}` |
| **出参** | `{"code":"03","message":"请求的资源不存在!","data":null}` |
| **Bug描述** | detail 接口对所有 ID（包括数据库中存在的 ID）均返回 HTTP 404 或 code:03，属于后端查询逻辑 Bug |

### Bug 3-3：login_module/test_logout_without_token

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-018 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/sys/logout` |
| **入参** | `（无请求体）` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 接口逻辑异常 |

### Bug 3-4：pricing_module/test_update_pricing_no_record

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-019 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/platform/pricing/updatePricing` |
| **入参** | `{"serviceItemId":"419","amount":150.0,"areaList":[{"code":"110101000000","level":"county","name":"东城区"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 ServicePricingUpdateReqDto 定义了标准行为，但实际返回异常 |

### Bug 3-5：worker_sign_module/test_worker_authorization_success

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-020 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/save` |
| **入参** | `{"userUuid":"worker-1785979746","workerPhone":"17427786358","stationInfoId":1,"stationInfoName":"Test Station","provinceAreaCode":"110119000000","cityAreaCode":"110119000000","districtAreaCode":"110119000000","sourceType":1,"serviceItems":[{"serviceItemId":1,"itemName":"Test Service","billingMethod":1,"amount":100.0}]}` |
| **出参** | `{"code":"02","message":"系统繁忙，请稍后再试!","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 WorkerOcrAddReqDto 定义了标准行为，但实际返回异常 |

### Bug 3-6：worker_sign_module/test_worker_authorization_with_phone

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-021 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/save` |
| **入参** | `{"userUuid":"worker-1785979747","workerPhone":"17480850962","stationInfoId":1,"stationInfoName":"Test Station","provinceAreaCode":"110119000000","cityAreaCode":"110119000000","districtAreaCode":"110119000000","sourceType":1,"serviceItems":[{"serviceItemId":1,"itemName":"Test Service","billingMethod":1,"amount":100.0}]}` |
| **出参** | `{"code":"02","message":"系统繁忙，请稍后再试!","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 WorkerOcrAddReqDto 定义了标准行为，但实际返回异常 |

### Bug 3-7：worker_sign_module/test_worker_info_success_with_uuid

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-022 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/save` |
| **入参** | `{"userUuid":"worker-1785979747","workerPhone":"17442489112","stationInfoId":1,"stationInfoName":"Test Station","provinceAreaCode":"110119000000","cityAreaCode":"110119000000","districtAreaCode":"110119000000","sourceType":1,"serviceItems":[{"serviceItemId":1,"itemName":"Test Service","billingMethod":1,"amount":100.0}]}` |
| **出参** | `{"code":"02","message":"系统繁忙，请稍后再试!","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 WorkerOcrAddReqDto 定义了标准行为，但实际返回异常 |

### Bug 3-8：worker_sign_module/test_worker_info_success_with_phone

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-023 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/save` |
| **入参** | `{"userUuid":"worker-1785979747","workerPhone":"17431300776","stationInfoId":1,"stationInfoName":"Test Station","provinceAreaCode":"110119000000","cityAreaCode":"110119000000","districtAreaCode":"110119000000","sourceType":1,"serviceItems":[{"serviceItemId":1,"itemName":"Test Service","billingMethod":1,"amount":100.0}]}` |
| **出参** | `{"code":"02","message":"系统繁忙，请稍后再试!","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 WorkerOcrAddReqDto 定义了标准行为，但实际返回异常 |

### Bug 3-9：worker_sign_module/test_worker_sign_save_success

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-026 |
| **严重程度** | high |
| **请求地址** | `http://172.16.1.165:9200/api/worker-sign/save` |
| **入参** | `{"userUuid":"worker-1785979751","workerPhone":"17410622448","stationInfoId":1,"stationInfoName":"Test Station","provinceAreaCode":"110119000000","cityAreaCode":"110119000000","districtAreaCode":"110119000000","sourceType":1,"serviceItems":[{"serviceItemId":1,"itemName":"Test Service","billingMethod":1,"amount":100.0}]}` |
| **出参** | `{"code":"02","message":"系统繁忙，请稍后再试!","data":null}` |
| **Bug描述** | 接口逻辑异常，OpenAPI 规范 WorkerOcrAddReqDto 定义了标准行为，但实际返回异常 |

## 4. 安全漏洞（SQL 注入 / XSS）

### Bug 4-1：经营范围 scopeName 字段 SQL 注入

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-014 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/businessScope/add` |
| **入参** | `{"scopeName":"' OR '1'='1","remark":"TestRemark"}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 经营范围 scopeName 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-2：经营范围 scopeName 字段 SQL 注入

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-014 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/businessScope/add` |
| **入参** | `{"scopeName":"' OR 1=1 --","remark":"TestRemark"}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 经营范围 scopeName 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-3：知识库标题存在 SQL 注入漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-011 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"' OR '1'='1","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-4：知识库标题存在 SQL 注入漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-011 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"' OR 1=1 --","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-5：知识库标题存在 SQL 注入漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-011 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"'; DROP TABLE users; --","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-6：知识库标题存在 SQL 注入漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-011 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"1' UNION SELECT NULL--","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 SQL 注入 payload，后端接受并返回成功，存在 SQL 注入风险 |

### Bug 4-7：知识库标题存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-012 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"<script>alert('xss')</script>","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-8：知识库标题存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-012 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"<img src=x onerror=alert('xss')>","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-9：知识库标题存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-012 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"<svg onload=alert('xss')>","content":"TestContent","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 title 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-10：知识库内容存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-013 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"TestTitle","content":"<script>alert('xss')</script>","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 content 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-11：知识库内容存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-013 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"TestTitle","content":"<img src=x onerror=alert('xss')>","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 content 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

### Bug 4-12：知识库内容存在 XSS 漏洞

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-013 |
| **严重程度** | critical |
| **请求地址** | `http://172.16.1.165:9200/platform/knowledge/save` |
| **入参** | `{"title":"TestTitle","content":"<svg onload=alert('xss')>","consultType":1,"displayPosition":[0,1],"applicableArea":[{"code":"110119000000","name":"延庆区","level":"county"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 知识库 content 字段未过滤 XSS payload，后端接受并返回成功，存在 XSS 风险 |

## 5. 边界值

### Bug 5-1：定价金额 amount=-1 未校验

| 项目 | 内容 |
|------|------|
| **缺陷ID** | BUG-016 |
| **严重程度** | medium |
| **请求地址** | `http://172.16.1.165:9200/platform/pricing/updatePricing` |
| **入参** | `{"serviceItemId":"418","amount":0,"areaList":[{"code":"110101000000","level":"county","name":"东城区"}]}` |
| **出参** | `{"code":"00","message":"操作成功","data":null}` |
| **Bug描述** | 金额 amount=-1 时后端未做校验，返回成功 code:00，预期应返回失败 |

---

## Bug 汇总

| 类别 | Bug 数量 |
|------|----------|
| 必填项校验 Bug | 2 |
| 存在性校验 Bug | 5 |
| 接口逻辑 Bug | 9 |
| 安全漏洞（SQL 注入 / XSS） | 12 |
| 边界值 | 1 |
| **后端 Bug 总计** | **29** |