# 津筑网 App 自动化测试配置文件（模板）
# 使用时请复制为 config.py 并填入真实信息

# ADB配置
adb_device_id = ""  # 留空自动连接第一个设备
adb_timeout = 30

# 测试配置
test_case_file = "testCase/app_test_cases.md"
app_package = "com.tjxinyu.fz"
app_activity = "com.tarodemo.PrivacyActivity"

# APK配置
apk_path = "apk/your_test_apk.apk"
reinstall_apk = True

# 截图配置
screenshot_enabled = True
screenshot_format = "png"

# 报告配置
report_format = "html"
report_include_screenshots = True

# 测试执行配置
test_execution_delay = 1
page_load_timeout = 3
element_find_timeout = 5

# 重试配置
max_retry_count = 2
retry_delay = 2

# 登录状态管理
auto_relogin = True
default_account_index = 0

# 日志配置
log_level = "INFO"
log_to_file = True
log_file = "logs/test_execution.log"

# 设备配置
device_width = 1080
device_height = 2400

# 测试账号配置（请替换为你的测试账号）
test_accounts = [
    {
        "phone": "YOUR_TEST_PHONE_1",
        "code": "YOUR_TEST_CODE_1",
        "name": "测试账号1"
    },
    {
        "phone": "YOUR_TEST_PHONE_2",
        "code": "YOUR_TEST_CODE_2",
        "name": "测试账号2"
    }
]

# 坐标映射（1080x2400分辨率）
coordinates = {
    "privacy_agree": [760, 1580],
    "privacy_disagree": [320, 1580],
    "guide_start": [540, 1927],
    "phone_input": [540, 1000],
    "code_input": [540, 1185],
    "get_code": [805, 1193],
    "login_button": [540, 1437],
    "agreement_checkbox": [257, 1754],
    "nav_home": [135, 2358],
    "nav_order": [405, 2358],
    "nav_goods": [675, 2358],
    "nav_mine": [945, 2358],
}
