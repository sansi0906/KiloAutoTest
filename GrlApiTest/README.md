# GrlApiTest - Python API Testing Framework

基于 pytest + requests + allure 的自动化接口测试框架，支持 JeecgBoot 业务系统的全量接口测试。

## 环境要求

- Python >= 3.8
- pip install -r requirements.txt

## 快速开始

```bash
# 设置 PYTHONPATH
$env:PYTHONPATH = "D:\dev\python-packages"

# 运行全部测试
cd E:\KiloAutoTest\GrlApiTest
python -m pytest -v --tb=short

# 运行冒烟测试
python -m pytest -m smoke -v --tb=short

# 运行特定模块
python -m pytest test_cases/login_module/ -v --tb=short
```

## 测试标记

| 标记 | 说明 | 使用场景 |
|------|------|----------|
| `@pytest.mark.smoke` | 冒烟测试 | 核心流程快速验证 |
| `@pytest.mark.regression` | 回归测试 | 全量业务场景 |
| `@pytest.mark.slow` | 慢速测试 | 包含等待或大量数据处理 |

## 项目结构

```
├── config.py                      # 全局配置（BASE_URL、数据库、账号等）
├── conftest.py                    # pytest 全局固件
├── pytest.ini                     # pytest 配置（标记、路径等）
├── requirements.txt               # 依赖包
├── README.md                      # 项目说明
├── api_clients/                   # API 客户端
│   ├── base_client.py             # 基础 HTTP 客户端
│   └── jeecgboot_client.py        # 业务 API 客户端
├── utils/                         # 工具类
│   ├── token_manager.py           # Token 管理（自动刷新）
│   ├── db_helper.py               # 163 MySQL 数据库操作
│   ├── pg_cleanup.py              # 165 PostgreSQL 清理工具
│   ├── cleanup_pricing.py         # service_item/pricing 手动清理
│   ├── base_test.py               # 通用测试基类
│   └── validator.py               # 响应验证器
├── test_cases/                     # 测试用例
│   ├── login_module/              # 登录模块
│   ├── platform_user_module/      # 平台用户管理
│   ├── business_scope_module/     # 经营范围配置
│   ├── knowledge_base_module/     # 知识库管理
│   ├── service_item_module/       # 服务项目配置
│   ├── service_provider_module/   # 服务商管理
│   └── pricing_module/            # 服务定价配置
├── data/                          # 测试数据
│   └── 服务定价数据.xlsx
└── reports/                       # 测试报告
```

## 模块覆盖

| 模块 | 接口数 | 用例数 | 状态 |
|------|--------|--------|------|
| 登录模块 | 3 | 13 | ✅ |
| 平台用户管理 | 7 | 26 | ✅ |
| 经营范围配置 | 6 | 15 | ✅ |
| 知识库管理 | 6 | 13 | ✅ |
| 服务项目配置 | 5 | 11 | ✅ |
| 服务商管理 | 7 | 15 | ✅ |
| 服务定价配置 | 4 | 10 | ✅ |
| **合计** | **38** | **103** | - |

## 数据库说明

### 163 MySQL（test_cjgt）- 测试框架数据

| 表 | 说明 | 自动清理 |
|----|------|----------|
| test_modules | 测试模块 | 否 |
| test_cases | 测试用例 | 否 |
| test_results | 测试结果 | 否 |
| test_data | 测试数据 | 是 |
| test_logs | 测试日志 | 是 |
| api_definitions | API 定义 | 否 |

### 165 PostgreSQL（cjgt）- 业务数据

使用 `utils/pg_cleanup.py` 按 `create_user_uuid` 清理测试数据：

```bash
# 查看待清理数据
python utils/pg_cleanup.py --dry-run

# 执行清理
python utils/pg_cleanup.py
```

## 清理数据

### 自动清理（配置开关）

在 `config.py` 中配置：

```python
# 163 MySQL 测试数据自动清理
DB_CLEANUP_AFTER_TEST = True
DB_CLEANUP_MODULES = ["platform_user_module", "service_provider_module", ...]

# 165 PostgreSQL 业务数据自动清理
PG_CLEANUP_ENABLED = True
PG_CLEANUP_UUID = "f4f44ea8-6713-4c96-9782-a06c2fa3d51d"
```

### 手动清理

```bash
# 清理 service_item/pricing（无 delete 接口）
python utils/cleanup_pricing.py --dry-run
python utils/cleanup_pricing.py
```

## 配置说明

编辑 `config.py`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| BASE_URL | API 服务器地址 | http://172.16.1.165:9200 |
| USERNAME | 登录用户名 | 15522719628 |
| PASSWORD | 登录密码 | 123456 |
| LOGIN_TYPE | 登录类型 | 1（密码登录） |
| WEB_TYPE | 终端类型 | 0（管理后台） |
| DB_CONFIG | 163 MySQL 配置 | - |
| PG_CONFIG | 165 PostgreSQL 配置 | - |

## 测试框架特性

- 自动登录并复用 Token
- 测试用例自动记录到 163 MySQL
- 测试数据自动清理
- 统一断言方法（`assert_save_success` / `assert_save_failure`）
- 支持 pytest 标记分类运行
- UTF-8 编码支持

## 注意事项

1. 测试前请确认 163/165 数据库可连接
2. 155 手机号对应 UUID：`f4f44ea8-6713-4c96-9782-a06c2fa3d51d`
3. 验证码发送有 60 秒频率限制，已标记为 `@pytest.mark.slow`
4. service_item 和 pricing 模块无 delete 接口，需使用手动清理脚本
