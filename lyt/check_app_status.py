"""
快速检查 App 当前状态
"""
import uiautomator2 as u2
import time
import os

PACKAGE = "com.grl.leyuntai"

def check_app_status():
    print("连接设备...", flush=True)
    d = u2.connect()
    print(f"✓ 设备: {d.info.get('productName', 'unknown')}", flush=True)
    
    # 检查当前前台应用
    current = d.app_current()
    print(f"当前应用: {current.get('package')}", flush=True)
    
    # 如果不是目标 App，启动它
    if current.get('package') != PACKAGE:
        print(f"启动 {PACKAGE}...", flush=True)
        d.app_start(PACKAGE)
        time.sleep(3)
    
    # 截图
    screenshot_dir = os.path.join(os.path.dirname(__file__), "tmpidea")
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "app_current_state.png")
    d.screenshot(screenshot_path)
    print(f"截图已保存: {screenshot_path}", flush=True)
    
    # 导出 UI 层次
    xml = d.dump_hierarchy()
    xml_path = os.path.join(screenshot_dir, "app_ui_hierarchy.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"UI 层次已保存: {xml_path}", flush=True)
    
    # 提取所有文本
    import re
    texts = re.findall(r'text="([^"]*)"', xml)
    print(f"\n当前界面包含的文本 (前50个):", flush=True)
    for i, t in enumerate(texts[:50], 1):
        print(f"  {i}. {t}", flush=True)
    
    # 检查关键元素
    print(f"\n关键元素检查:", flush=True)
    checks = [
        ("首页", "首页 Tab"),
        ("订单", "订单 Tab"),
        ("我的", "我的 Tab"),
        ("登录", "登录按钮"),
        ("密码登录", "密码登录入口"),
        ("同意", "同意按钮"),
        ("开始使用", "引导页按钮"),
    ]
    
    for text, desc in checks:
        exists = d(text=text).exists(timeout=0.5)
        status = "✓ 存在" if exists else "✗ 不存在"
        print(f"  {status}: {desc} ({text})", flush=True)
    
    # 判断当前状态
    print(f"\n状态判断:", flush=True)
    if d(text="首页").exists() or d(text="订单").exists():
        print("  → 已登录，在主页", flush=True)
    elif d(text="同意").exists():
        print("  → 隐私政策页面", flush=True)
    elif d(text="开始使用").exists():
        print("  → 引导页", flush=True)
    elif d(text="密码登录").exists() or d(text="请输入密码").exists():
        print("  → 登录页面", flush=True)
    else:
        print("  → 未知状态，请查看截图", flush=True)

if __name__ == "__main__":
    check_app_status()