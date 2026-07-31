"""
db_helper.py - 数据库工具
===========================
提供 MySQL/PostgreSQL 数据库操作封装，用于存储测试用例、
测试数据、测试结果等。
"""

import json
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from config import DB_CONFIG


class DatabaseHelper:
    """数据库操作封装，支持 MySQL 和 PostgreSQL"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or DB_CONFIG
        self.db_type = self.config.get("db_type", "mysql")
        self._ensure_database()

    def _get_connection(self):
        """获取数据库连接"""
        if self.db_type == "postgresql":
            import psycopg2
            return psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=self.config.get("connect_timeout", 10),
            )
        else:
            import pymysql
            return pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=self.config.get("connect_timeout", 10),
            )

    def _ensure_database(self):
        """确保数据库存在，不存在则创建"""
        try:
            conn = self._get_connection()
            conn.close()
        except Exception:
            if self.db_type == "postgresql":
                import psycopg2
                conn = psycopg2.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    user=self.config["user"],
                    password=self.config["password"],
                    connect_timeout=self.config.get("connect_timeout", 10),
                )
                conn.autocommit = True
                cursor = conn.cursor()
                cursor.execute(
                    f"CREATE DATABASE {self.config['database']} "
                    "WITH ENCODING 'UTF8' TEMPLATE template1"
                )
                conn.close()
            cursor.execute(
                f"CREATE DATABASE {self.config['database']} "
                "WITH ENCODING 'UTF8' TEMPLATE template1"
            )
            conn.close()

    @contextmanager
    def get_cursor(self):
        """上下文管理器，自动处理连接和游标"""
        conn = self._get_connection()
        try:
            if self.db_type == "postgresql":
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def execute(self, sql: str, params: tuple = None) -> int:
        """执行 SQL 并返回影响行数"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount

    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict]:
        """查询单条记录"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if self.db_type == "mysql" and row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return row

    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict]:
        """查询多条记录"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            if self.db_type == "mysql" and rows:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return rows

    def insert(self, table: str, data: Dict) -> int:
        """插入数据并返回自增ID"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.get_cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            if self.db_type == "postgresql":
                return cursor.fetchone()["id"]
            else:
                return cursor.lastrowid

    def update(self, table: str, data: Dict, where: str, params: tuple = None) -> int:
        """更新数据"""
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        all_params = tuple(data.values()) + (params or ())
        return self.execute(sql, all_params)

    def delete(self, table: str, where: str, params: tuple = None) -> int:
        """删除数据"""
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, params)

    # ==================== 测试专用方法 ====================

    def save_test_module(self, module_name: str, module_desc: str = "") -> int:
        """保存或获取测试模块ID"""
        result = self.fetch_one(
            "SELECT id FROM test_modules WHERE module_name = %s",
            (module_name,)
        )
        if result:
            return result["id"]
        return self.insert("test_modules", {
            "module_name": module_name,
            "module_desc": module_desc
        })

    def save_test_case(self, module_id: int, case_name: str, case_desc: str = "",
                       priority: str = "P1", tags: str = "") -> int:
        """保存或获取测试用例ID"""
        result = self.fetch_one(
            "SELECT id FROM test_cases WHERE module_id = %s AND case_name = %s",
            (module_id, case_name)
        )
        if result:
            return result["id"]
        return self.insert("test_cases", {
            "module_id": module_id,
            "case_name": case_name,
            "case_desc": case_desc,
            "priority": priority,
            "tags": tags
        })

    def save_test_result(self, case_id: int, execution_id: str, status: str,
                         duration_ms: int = None, error_message: str = None,
                         request_data: str = None, response_data: str = None,
                         assertion_details: str = None, environment: str = None):
        """保存测试执行结果"""
        return self.insert("test_results", {
            "case_id": case_id,
            "execution_id": execution_id,
            "status": status,
            "duration_ms": duration_ms,
            "error_message": error_message,
            "request_data": request_data,
            "response_data": response_data,
            "assertion_details": assertion_details,
            "environment": environment
        })

    def save_test_data(self, module_id: int, data_key: str, data_value: Any,
                       data_type: str = "json", description: str = ""):
        """保存或更新测试数据"""
        if not isinstance(data_value, str):
            data_value = json.dumps(data_value, ensure_ascii=False)
        sql = """
            INSERT INTO test_data (module_id, data_key, data_value, data_type, description)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE data_value = VALUES(data_value), updated_at = NOW()
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, (module_id, data_key, data_value, data_type, description))
            return cursor.lastrowid

    def save_test_log(self, execution_id: str, level: str, message: str,
                      module: str = None, case_name: str = None):
        """保存测试日志"""
        return self.insert("test_logs", {
            "execution_id": execution_id,
            "level": level,
            "message": message,
            "module": module,
            "case_name": case_name
        })

    def save_api_definition(self, module_id: int, api_path: str, api_method: str,
                            api_desc: str = "", request_schema: str = None,
                            response_schema: str = None):
        """保存或更新API定义"""
        sql = """
            INSERT INTO api_definitions (module_id, api_path, api_method, api_desc, request_schema, response_schema)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE api_method = VALUES(api_method), api_desc = VALUES(api_desc), updated_at = NOW()
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, (module_id, api_path, api_method, api_desc, request_schema, response_schema))
            return cursor.lastrowid

    def cleanup_test_data(self, module_name: str = None, execution_id: str = None):
        """清理测试数据"""
        conditions = []
        params = []
        if module_name:
            conditions.append("m.module_name = %s")
            params.append(module_name)
        if execution_id:
            conditions.append("r.execution_id = %s")
            params.append(execution_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self.get_cursor() as cursor:
            cursor.execute(f"""
                DELETE FROM test_logs
                WHERE execution_id IN (
                    SELECT r.execution_id FROM test_results r
                    JOIN test_cases c ON r.case_id = c.id
                    JOIN test_modules m ON c.module_id = m.id
                    WHERE {where_clause}
                )
            """, tuple(params))

            cursor.execute(f"""
                DELETE FROM test_results
                WHERE case_id IN (
                    SELECT id FROM test_cases
                    WHERE module_id IN (
                        SELECT id FROM test_modules
                        WHERE {where_clause}
                    )
                )
            """, tuple(params))

            if execution_id:
                cursor.execute("DELETE FROM test_logs WHERE execution_id = %s", (execution_id,))

            cursor.execute(f"""
                DELETE FROM test_data
                WHERE module_id IN (
                    SELECT id FROM test_modules
                    WHERE {where_clause}
                )
            """, tuple(params))

            cursor.execute(f"""
                DELETE FROM test_cases
                WHERE module_id IN (
                    SELECT id FROM test_modules
                    WHERE {where_clause}
                )
            """, tuple(params))

            if module_name:
                cursor.execute("DELETE FROM test_modules WHERE module_name = %s", (module_name,))

        return True
