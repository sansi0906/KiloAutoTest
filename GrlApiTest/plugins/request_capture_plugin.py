"""
临时插件：在每个测试后打印 request_history 中的最后一次请求/响应
用于捕获真实的 HTTP 请求/响应数据
"""
import json
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

def pytest_runtest_makereport(item, call):
    """在每个测试后捕获并打印请求历史"""
    if call.when == "call":
        instance = getattr(item, "instance", None)
        if instance and hasattr(instance, "client"):
            client = instance.client
            history = getattr(client, "_request_history", [])
            if history:
                # 打印最后 3 条请求记录（通常最后一次是关键请求）
                for i, entry in enumerate(history[-3:]):
                    print(f"\n{'='*80}")
                    print(f"REQUEST/RESPONSE #{i+1} (from _request_history)")
                    print(f"  Method: {entry.get('method', 'N/A')}")
                    print(f"  URL: {entry.get('url', 'N/A')}")
                    body = entry.get('body')
                    if body is not None:
                        try:
                            print(f"  Request Body: {json.dumps(body, ensure_ascii=False) if isinstance(body, (dict, list)) else body}")
                        except Exception:
                            print(f"  Request Body: {body}")
                    else:
                        print("  Request Body: (none)")
                    resp = entry.get("response", {})
                    print(f"  Response Status: {resp.get('status', 'N/A')}")
                    resp_json = resp.get("json")
                    if resp_json is not None:
                        try:
                            print(f"  Response Body: {json.dumps(resp_json, ensure_ascii=False) if isinstance(resp_json, (dict, list)) else resp_json}")
                        except Exception:
                            print(f"  Response Body: {resp_json}")
                    else:
                        print("  Response Body: (none)")
                    print(f"{'='*80}")
