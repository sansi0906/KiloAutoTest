"""
cleanup_pricing.py - 服务定价/项目清理脚本
=============================================
由于 service_item 和 pricing 模块没有 delete 接口，
提供手动清理脚本。
"""

import argparse
import sys

sys.path.insert(0, ".")

import pymysql
from config import DB_CONFIG


def get_mysql_connection():
    """获取 MySQL 连接（163）"""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        connect_timeout=DB_CONFIG.get("connect_timeout", 10),
    )


def cleanup_pricing_data(dry_run=False):
    """清理 service_item 和 pricing 相关测试数据"""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    results = {}

    try:
        # 清理 pricing 数据（通过接口测试产生的数据，create_user_name 为测试用户）
        cursor.execute("SELECT COUNT(*) FROM cjgt_service_pricing WHERE create_user_name = '测试管理员'")
        pricing_count = cursor.fetchone()[0]
        results["cjgt_service_pricing"] = pricing_count

        cursor.execute("SELECT COUNT(*) FROM cjgt_service_pricing_history WHERE create_user_name = '测试管理员'")
        pricing_history_count = cursor.fetchone()[0]
        results["cjgt_service_pricing_history"] = pricing_history_count

        cursor.execute("SELECT COUNT(*) FROM cjgt_service_pricing_import_log WHERE create_user_name = '测试管理员'")
        import_log_count = cursor.fetchone()[0]
        results["cjgt_service_pricing_import_log"] = import_log_count

        if not dry_run:
            cursor.execute("DELETE FROM cjgt_service_pricing WHERE create_user_name = '测试管理员'")
            cursor.execute("DELETE FROM cjgt_service_pricing_history WHERE create_user_name = '测试管理员'")
            cursor.execute("DELETE FROM cjgt_service_pricing_import_log WHERE create_user_name = '测试管理员'")
            conn.commit()

        # 清理 service_item 数据（通过接口测试产生的数据）
        cursor.execute("SELECT COUNT(*) FROM cjgt_service_item WHERE create_user_name = '测试管理员'")
        item_count = cursor.fetchone()[0]
        results["cjgt_service_item"] = item_count

        if not dry_run:
            cursor.execute("DELETE FROM cjgt_service_item WHERE create_user_name = '测试管理员'")
            conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="清理 service_item/pricing 测试数据")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不实际删除")
    args = parser.parse_args()

    print("Dry run:", args.dry_run)
    print("-" * 50)

    results = cleanup_pricing_data(dry_run=args.dry_run)

    print("-" * 50)
    print("Summary:")
    total = 0
    for table, count in results.items():
        print(f"  {table}: {count}")
        total += count
    print(f"Total: {total} rows")


if __name__ == "__main__":
    main()
