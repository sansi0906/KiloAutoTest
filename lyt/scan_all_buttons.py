"""
乐云台 App - 全量按钮扫描
遍历所有页面，收集所有可操作按钮
"""
import uiautomator2 as u2
import time
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

PACKAGE = "com.grl.leyuntai"
DINGTALK = "com.alibaba.android.rimet"

TAB_HOME = (135, 2256)
TAB_CUSTOMER = (405, 2256)
TAB_CART = (675, 2256)
TAB_ORDER = (945, 2256)
MY_BUTTON = (1011, 138)

print("连接设备...", flush=True)
d = u2.connect()
d.implicitly_wait(10.0)
print(f"✓ 设备: {d.info.get('productName', 'unknown')}", flush=True)

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all_buttons")
os.makedirs(screenshot_dir, exist_ok=True)

def restart_app():
    current = d.app_current()
    if current.get('package') == DINGTALK:
        d.app_stop(DINGTALK)
        time.sleep(1)
    d.app_start(PACKAGE, stop=True)
    time.sleep(4)
    d.click(*TAB_HOME)
    time.sleep(2)

def get_texts():
    xml = d.dump_hierarchy()
    texts = re.findall(r'text="([^"]*)"', xml)
    return [t for t in texts if t.strip()]

def screenshot(name):
    d.screenshot(os.path.join(screenshot_dir, f"{name}.png"))

# 收集所有按钮
all_buttons = {
    "首页": [],
    "设备列表": [],
    "设备详情": [],
    "建材列表": [],
    "人才列表": [],
    "服务列表": [],
    "客户列表": [],
    "客户详情": [],
    "手动录入": [],
    "购物车": [],
    "购物车管理": [],
    "订单类型选择": [],
    "客户订单表单": [],
    "记录订单表单": [],
    "客户选择": [],
    "订单列表": [],
    "订单详情": [],
    "草稿订单编辑": [],
    "上传协议": [],
    "我的页面": [],
    "意见反馈": [],
    "关于我们": [],
    "系统设置": [],
    "公司资质": [],
}

def collect_buttons(page_name):
    """收集当前页面的所有可操作按钮"""
    xml = d.dump_hierarchy()
    texts = get_texts()
    
    # 过滤掉状态栏、导航栏等无关文本
    exclude = ['KB/s', 'MB/s', '100', '4G', '5G', 'WiFi', ' statusBar', ':']
    
    buttons = []
    for t in texts:
        if t and not any(ex in t for ex in exclude) and len(t) > 0:
            # 查找该文本的位置
            pattern = f'text="{re.escape(t)}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
            matches = re.findall(pattern, xml)
            for x1, y1, x2, y2 in matches:
                center_x = (int(x1) + int(x2)) // 2
                center_y = (int(y1) + int(y2)) // 2
                buttons.append({
                    "text": t,
                    "位置": f"({center_x}, {center_y})",
                    "bounds": f"[{x1},{y1}][{x2},{y2}]"
                })
                break  # 只取第一个匹配
    
    # 去重
    seen = set()
    unique_buttons = []
    for btn in buttons:
        if btn["text"] not in seen:
            seen.add(btn["text"])
            unique_buttons.append(btn)
    
    all_buttons[page_name] = unique_buttons
    print(f"  {page_name}: {len(unique_buttons)} 个按钮", flush=True)
    return unique_buttons

# ============================================================
# 开始扫描
# ============================================================
print("\n" + "="*60, flush=True)
print("乐云台 App - 全量按钮扫描", flush=True)
print("="*60)

restart_app()

# 1. 首页
print("\n--- 扫描首页 ---", flush=True)
collect_buttons("首页")

# 2. 设备列表
print("\n--- 扫描设备列表 ---", flush=True)
d(text="设备").click()
time.sleep(2)
collect_buttons("设备列表")
screenshot("01_device_list")

# 3. 设备详情
print("\n--- 扫描设备详情 ---", flush=True)
# 找到第一个"加入购物车"按钮，点击其上方的商品图片
if d(text="加入购物车").exists(timeout=2):
    elem = d(text="加入购物车")
    bounds = elem.info.get('bounds', {})
    if bounds:
        x = (bounds['left'] + bounds['right']) // 2
        y = bounds['top'] - 100
        d.click(x, y)
        time.sleep(3)
        collect_buttons("设备详情")
        screenshot("02_device_detail")
        d.press("back")
        time.sleep(1)

# 4. 建材列表
print("\n--- 扫描建材列表 ---", flush=True)
restart_app()
d(text="建材").click()
time.sleep(2)
collect_buttons("建材列表")
screenshot("03_building_list")

# 5. 人才列表
print("\n--- 扫描人才列表 ---", flush=True)
restart_app()
d(text="人才").click()
time.sleep(2)
collect_buttons("人才列表")
screenshot("04_talent_list")

# 6. 服务列表
print("\n--- 扫描服务列表 ---", flush=True)
restart_app()
d(text="服务").click()
time.sleep(2)
collect_buttons("服务列表")
screenshot("05_service_list")

# 7. 客户列表
print("\n--- 扫描客户列表 ---", flush=True)
restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)
collect_buttons("客户列表")
screenshot("06_customer_list")

# 8. 客户详情
print("\n--- 扫描客户详情 ---", flush=True)
d.click(540, 400)
time.sleep(2)
collect_buttons("客户详情")
screenshot("07_customer_detail")
d.press("back")
time.sleep(1)

# 9. 手动录入
print("\n--- 扫描手动录入 ---", flush=True)
d.click(*TAB_CUSTOMER)
time.sleep(2)
if d(textContains="手动录入").exists(timeout=1):
    d(textContains="手动录入").click()
    time.sleep(2)
    collect_buttons("手动录入")
    screenshot("08_manual_input")
    d.press("back")
    time.sleep(1)

# 10. 购物车
print("\n--- 扫描购物车 ---", flush=True)
restart_app()
d.click(*TAB_CART)
time.sleep(3)
collect_buttons("购物车")
screenshot("09_cart")

# 11. 购物车管理
print("\n--- 扫描购物车管理模式 ---", flush=True)
if d(text="管理").exists(timeout=1):
    d(text="管理").click()
    time.sleep(1)
    collect_buttons("购物车管理")
    screenshot("10_cart_manage")
    if d(text="完成").exists(timeout=1):
        d(text="完成").click()
        time.sleep(1)

# 12. 订单类型选择
print("\n--- 扫描订单类型选择 ---", flush=True)
if d(text="全选").exists(timeout=1):
    d(text="全选").click()
    time.sleep(1)
if d(text="生成订单").exists(timeout=1):
    d(text="生成订单").click()
    time.sleep(2)
    collect_buttons("订单类型选择")
    screenshot("11_order_type")

# 13. 客户订单表单
print("\n--- 扫描客户订单表单 ---", flush=True)
if d(text="客户订单").exists(timeout=1):
    d(text="客户订单").click()
    time.sleep(2)
    collect_buttons("客户订单表单")
    screenshot("12_customer_order_form")

# 14. 客户选择
print("\n--- 扫描客户选择 ---", flush=True)
if d(textContains="选择客户").exists(timeout=1):
    d(textContains="选择客户").click()
    time.sleep(2)
    collect_buttons("客户选择")
    screenshot("13_customer_select")
    d.press("back")
    time.sleep(1)

# 15. 记录订单表单
print("\n--- 扫描记录订单表单 ---", flush=True)
restart_app()
d.click(*TAB_CART)
time.sleep(3)
if d(text="全选").exists(timeout=1):
    d(text="全选").click()
    time.sleep(1)
if d(text="生成订单").exists(timeout=1):
    d(text="生成订单").click()
    time.sleep(2)
if d(text="记录订单").exists(timeout=1):
    d(text="记录订单").click()
    time.sleep(2)
    collect_buttons("记录订单表单")
    screenshot("14_record_order_form")

# 16. 订单列表
print("\n--- 扫描订单列表 ---", flush=True)
restart_app()
d.click(*TAB_ORDER)
time.sleep(3)
collect_buttons("订单列表")
screenshot("15_order_list")

# 17. 订单详情
print("\n--- 扫描订单详情 ---", flush=True)
d.click(540, 500)
time.sleep(2)
collect_buttons("订单详情")
screenshot("16_order_detail")
d.press("back")
time.sleep(1)

# 18. 草稿订单编辑
print("\n--- 扫描草稿订单编辑 ---", flush=True)
d.click(*TAB_ORDER)
time.sleep(2)
# 滚动查找草稿订单
for _ in range(3):
    if d(text="草稿").exists(timeout=1):
        elem = d(text="草稿")
        bounds = elem.info.get('bounds', {})
        if bounds:
            y = (bounds['top'] + bounds['bottom']) // 2
            d.click(540, y)
            time.sleep(2)
            collect_buttons("草稿订单编辑")
            screenshot("17_draft_edit")
            
            # 19. 上传协议
            if d(textContains="上传协议").exists(timeout=1):
                d(textContains="上传协议").click()
                time.sleep(2)
                collect_buttons("上传协议")
                screenshot("18_upload_agreement")
                d.press("back")
                time.sleep(1)
            break
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)

# 20. 我的页面
print("\n--- 扫描我的页面 ---", flush=True)
restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
collect_buttons("我的页面")
screenshot("19_my_page")

# 21. 意见反馈
print("\n--- 扫描意见反馈 ---", flush=True)
if d(text="意见反馈").exists(timeout=1):
    d(text="意见反馈").click()
    time.sleep(2)
    collect_buttons("意见反馈")
    screenshot("20_feedback")
    d.press("back")
    time.sleep(1)

# 22. 关于我们
print("\n--- 扫描关于我们 ---", flush=True)
d.click(*MY_BUTTON)
time.sleep(2)
if d(text="关于我们").exists(timeout=1):
    d(text="关于我们").click()
    time.sleep(2)
    collect_buttons("关于我们")
    screenshot("21_about")
    d.press("back")
    time.sleep(1)

# 23. 系统设置
print("\n--- 扫描系统设置 ---", flush=True)
d.click(*MY_BUTTON)
time.sleep(2)
if d(text="系统设置").exists(timeout=1):
    d(text="系统设置").click()
    time.sleep(2)
    collect_buttons("系统设置")
    screenshot("22_settings")
    d.press("back")
    time.sleep(1)

# 24. 公司资质
print("\n--- 扫描公司资质 ---", flush=True)
d.click(*MY_BUTTON)
time.sleep(2)
if d(text="公司资质").exists(timeout=1):
    d(text="公司资质").click()
    time.sleep(2)
    collect_buttons("公司资质")
    screenshot("23_qualification")

# ============================================================
# 输出结果
# ============================================================
print("\n" + "="*60, flush=True)
print("全量按钮扫描结果", flush=True)
print("="*60)

total_buttons = 0
for page, buttons in all_buttons.items():
    if buttons:
        total_buttons += len(buttons)
        print(f"\n【{page}】({len(buttons)}个)", flush=True)
        for btn in buttons:
            print(f"  - {btn['text']}  {btn['位置']}", flush=True)

print(f"\n总计: {total_buttons} 个按钮", flush=True)

# 保存JSON
with open(os.path.join(screenshot_dir, "all_buttons.json"), "w", encoding="utf-8") as f:
    json.dump({
        "扫描时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "总按钮数": total_buttons,
        "页面数": len([k for k, v in all_buttons.items() if v]),
        "详细按钮": all_buttons
    }, f, ensure_ascii=False, indent=2)

print(f"\n详细结果: {os.path.join(screenshot_dir, 'all_buttons.json')}", flush=True)