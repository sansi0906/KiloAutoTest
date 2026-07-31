# GrlApiTest 配置文件（模板）
# 使用时请复制为 config.py 并填入真实信息

# API配置
BASE_URL = "http://YOUR_API_HOST:PORT"
LOGIN_URL = "/sys/login"
LOGOUT_URL = "/sys/logout"

# 测试账号
USERNAME = "YOUR_TEST_USERNAME"
PASSWORD = "YOUR_TEST_PASSWORD"

# Token缓存
TOKEN_FILE = "token.json"

# MySQL数据库配置
MYSQL_CONFIG = {
    "host": "YOUR_MYSQL_HOST",
    "port": 3306,
    "user": "YOUR_MYSQL_USER",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "YOUR_DATABASE",
    "charset": "utf8mb4"
}

# PostgreSQL数据库配置
PG_CONFIG = {
    "host": "YOUR_PG_HOST",
    "port": 5432,
    "user": "YOUR_PG_USER",
    "password": "YOUR_PG_PASSWORD",
    "database": "YOUR_DATABASE"
}
