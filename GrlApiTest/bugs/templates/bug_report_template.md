# 缺陷报告 - {{execution_id}}

> 测试时间：{{test_date}}
> 测试环境：{{environment}}
> 测试套件：{{test_summary}}
> 执行批次：{{execution_order}}

---

## 缺陷列表

{{bug_entries}}

---

## 汇总

| 类别 | 数量 |
|------|------|
| 必填项校验 | {{required_field_count}} |
| 存在性校验 | {{existence_count}} |
| 接口逻辑 | {{logic_count}} |
| 安全漏洞 | {{security_count}} |
| 边界值 | {{boundary_count}} |
| **总计** | **{{total_count}}** |

---

## 云效提交状态

| 状态 | 数量 |
|------|------|
| 已提交云效 | {{yunxiao_submitted}} |
| 未提交云效 | {{yunxiao_pending}} |

## 修复状态

| 状态 | 数量 |
|------|------|
| 已修复 | {{fixed_count}} |
| 未修复 | {{unfixed_count}} |
| 已验证 | {{verified_count}} |