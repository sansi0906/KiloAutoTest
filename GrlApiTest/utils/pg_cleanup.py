"""
pg_cleanup.py - PostgreSQL 业务数据清理工具
=============================================
用于清理接口测试产生的业务数据，基于 create_user_uuid 识别。
默认清理 create_user_uuid = 'f4f44ea8-6713-4c96-9782-a06c2fa3d51d' 当天新增的数据。
"""

import argparse
import sys
from datetime import date

sys.path.insert(0, ".")

import psycopg2
from config import PG_CONFIG


TEST_CREATOR_UUID = "f4f44ea8-6713-4c96-9782-a06c2fa3d51d"

# 需要清理的业务表
CLEANUP_TABLES = [
    "cjgt_service_pricing_history",
    "cjgt_service_pricing_import_log",
    "cjgt_service_pricing",
    "cjgt_knowledge_base",
    "cjgt_service_provider",
    "cjgt_business_scope",
    "cjgt_service_item",
    "cjgt_platform_user",
    "cjgt_worker_base_info",
    "cjgt_worker_sign",
]

# 各表的清理 SQL，默认过滤当天数据
CLEANUP_SQL = {
    "cjgt_service_pricing_history": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_service_pricing_import_log": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_service_pricing": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_knowledge_base": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_service_provider": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_business_scope": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_service_item": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_platform_user": "DELETE FROM {table} WHERE create_user_uuid = %s AND is_super_admin != 1 AND create_time >= %s",
    "cjgt_worker_base_info": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
    "cjgt_worker_sign": "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s",
}


def get_pg_connection():
    """获取 PostgreSQL 连接"""
    return psycopg2.connect(
        host=PG_CONFIG["host"],
        port=PG_CONFIG["port"],
        database=PG_CONFIG["database"],
        user=PG_CONFIG["user"],
        password=PG_CONFIG["password"],
        connect_timeout=PG_CONFIG.get("connect_timeout", 10),
    )


def cleanup_test_data(creator_uuid=None, dry_run=False, cleanup_date=None):
    """清理测试数据

    Args:
        creator_uuid: 创建者UUID，默认使用 TEST_CREATOR_UUID
        dry_run: 如果 True，只打印将要删除的数据，不实际删除
        cleanup_date: 清理指定日期的数据，默认今天（格式: YYYY-MM-DD）

    Returns:
        清理结果字典
    """
    creator_uuid = creator_uuid or TEST_CREATOR_UUID
    cleanup_date = cleanup_date or date.today().isoformat()
    # 计算当天的起始时间
    date_start = f"{cleanup_date} 00:00:00"

    results = {}

    conn = get_pg_connection()
    cursor = conn.cursor()

    try:
        for table in CLEANUP_TABLES:
            sql = CLEANUP_SQL.get(table, "DELETE FROM {table} WHERE create_user_uuid = %s AND create_time >= %s").format(table=table)
            cursor.execute(sql, (creator_uuid, date_start))
            count = cursor.rowcount
            results[table] = count
            if dry_run:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE create_user_uuid = %s AND create_time >= %s", (creator_uuid, date_start))
                actual_count = cursor.fetchone()[0]
                print(f"[预览] {table}: {actual_count} 行数据将被删除")
            else:
                print(f"已删除 {table}: {count} 行")

        if not dry_run:
            conn.commit()
        else:
            conn.rollback()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="清理接口测试业务数据")
    parser.add_argument("--uuid", default=TEST_CREATOR_UUID, help=f"创建者UUID，默认: {TEST_CREATOR_UUID}")
    parser.add_argument("--date", default=None, help="清理指定日期的数据，默认今天 (格式: YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不实际删除")
    parser.add_argument("--list-creators", action="store_true", help="列出所有 create_user_uuid")
    args = parser.parse_args()

    if args.list_creators:
        conn = get_pg_connection()
        cursor = conn.cursor()
        for table in CLEANUP_TABLES:
            try:
                cursor.execute(f"SELECT DISTINCT create_user_uuid FROM {table} WHERE create_user_uuid IS NOT NULL")
                rows = cursor.fetchall()
                print(f"{table}: {[r[0] for r in rows]}")
            except Exception as e:
                print(f"{table}: 错误 {e}")
        cursor.close()
        conn.close()
        return

    cleanup_date = args.date or date.today().isoformat()
    print(f"清理测试数据 - UUID: {args.uuid}")
    print(f"清理日期: {cleanup_date}")
    print(f"预览模式: {'是' if args.dry_run else '否'}")
    print("-" * 50)

    results = cleanup_test_data(creator_uuid=args.uuid, dry_run=args.dry_run, cleanup_date=cleanup_date)

    print("-" * 50)
    print("清理汇总:")
    total = 0
    for table, count in results.items():
        print(f"  {table}: {count} 行")
        total += count
    print(f"合计: {total} 行")


if __name__ == "__main__":
    main()
