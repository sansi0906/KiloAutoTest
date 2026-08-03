"""
乐云泰App - 精确探索首页功能入口和子页面
"""
import uiautomator2 as u2
import re
import os
import time
from datetime import datetime

d = u2.connect()
DUMP_DIR = "E:/KiloAutoTest/lyt/ui_dumps"
os.makedirs(DUMP_DIR, exist_ok=True)

def dump_page(step_name):
    ts = datetime.now().strftime("%H%M%S")
    xml = d.dump_hierarchy()
    xml_path = f"{DUMP_DIR}/{step_name}_{ts}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)
    
    texts = re.findall(r'text="([^"]*)"', xml)
    non_empty = [t for t in texts if t.strip()]
    
    # 带bounds的文本元素
    elements = re.findall(
        r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    app_elements = [(t, int(x1), int(y1), int(x2), int(y2)) 
                    for t, x1, y1, x2, y2 in elements 
                    if t.strip() and int(y1) > 104]
    
    print(f"\n{'='*60}")
    print(f"  📄 {step_name}")
    print(f"{'='*60}")
    print(f"  📝 文本元素 ({len(non_empty)}个):")
    for t in non_empty[:25]:
        print(f"    [{t}]")
    
    # 可点击区域
    clickable_bounds = re.findall(
        r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    print(f"\n  👆 可点击区域 ({len(clickable_bounds)}个):")
    for x1, y1, x2, y2 in clickable_bounds[:20]:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"    ({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
    
    shot_path = f"{DUMP_DIR}/{step_name}_{ts}.png"
    d.screenshot(shot_path)
    print(f"\n  💾 XML: {xml_path}")
    return non_empty

def get_current_app():
    try:
        return d.app_current().get("package", "")
    except:
        return ""

# 底部Tab坐标
TABS = {
    "首页": (135, 2321),
    "客户": (405, 2321),
    "购物车": (675, 2321),
    "订单": (945, 2321),
}

PACKAGE = "com.grl.leyuntai"

print("=" * 60)
print("  乐云泰App 精确探索")
print("=" * 60)

# === 1. 重新探索首页设备入口 ===
print("\n" + "=" * 40)
print("  1. 设备入口详情页")
print("=" * 40)

# 回到首页
d.app_start(PACKAGE, stop=False)
time.sleep(2)
d.click(*TABS["首页"])
time.sleep(1.5)

# 点击设备入口
# 设备入口bounds: [35,873][528,1075] 中心(281,974)
print("\n🔄 点击设备入口")
d.click(281, 974)
time.sleep(2)

# 检查是否在乐云泰App
current = get_current_app()
print(f"  当前App: {current}")
if PACKAGE in current:
    dump_page("device_list")
    
    # 在设备列表页滑动
    d.swipe(540, 1800, 540, 600, duration=0.5)
    time.sleep(1)
    dump_page("device_list_scrolled")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    print(f"  ⚠️ 离开了App，当前: {current}")
    d.app_start(PACKAGE, stop=False)
    time.sleep(2)
    d.click(*TABS["首页"])
    time.sleep(1)

# === 2. 订单详情精确探索 ===
print("\n" + "=" * 40)
print("  2. 订单详情精确探索")
print("=" * 40)

d.click(*TABS["订单"])
time.sleep(1.5)

# 根据之前的XML，第一个订单项大约在 y=400-600
# 订单卡片有"风风光光"、"待代理确认"等文字
# 点击订单标题区域
print("\n🔄 点击订单列表项")
# 先滑动一点确保能看到第一个完整订单
d.swipe(540, 1000, 540, 800, duration=0.3)
time.sleep(0.5)

# 点击第一个订单的标题文字区域
d.click(540, 450)
time.sleep(2)

current = get_current_app()
print(f"  当前App: {current}")
if PACKAGE in current:
    dump_page("order_detail_v2")
    
    # 查看更多 - 滑动
    d.swipe(540, 1800, 540, 600, duration=0.5)
    time.sleep(1)
    dump_page("order_detail_v2_scrolled")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    print(f"  ⚠️ 离开了App，当前: {current}")
    d.app_start(PACKAGE, stop=False)
    time.sleep(2)
    d.click(*TABS["订单"])
    time.sleep(1)

# === 3. 客户列表精确探索 ===
print("\n" + "=" * 40)
print("  3. 客户列表精确探索")
print("=" * 40)

d.click(*TABS["客户"])
time.sleep(1.5)
dump_page("customer_list_v2")

# 点击搜索框
# 搜索框bounds: [164,170][846,239] 中心(505,204)
print("\n🔄 点击客户搜索框")
d.click(505, 204)
time.sleep(1)

# 输入搜索词
try:
    el = d(className="android.widget.EditText")
    if el.exists(timeout=1):
        el.click()
        el.set_text("工人乐")
        time.sleep(0.5)
        dump_page("customer_search")
        
        # 搜索
        d.press("enter")
        time.sleep(2)
        dump_page("customer_search_result")
        
        # 返回
        d.press("back")
        time.sleep(1)
except Exception as e:
    print(f"  搜索失败: {e}")

# === 4. 购物车详情精确探索 ===
print("\n" + "=" * 40)
print("  4. 购物车详情精确探索")
print("=" * 40)

d.click(*TABS["购物车"])
time.sleep(1.5)
dump_page("cart_v2")

# 点击商品详情
# 商品项大约在 y=600-800
print("\n🔄 点击购物车商品")
d.click(540, 700)
time.sleep(2)

current = get_current_app()
print(f"  当前App: {current}")
if PACKAGE in current:
    dump_page("cart_item_detail")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    print(f"  ⚠️ 离开了App")
    d.app_start(PACKAGE, stop=False)
    time.sleep(2)

# === 5. 首页消息项点击 ===
print("\n" + "=" * 40)
print("  5. 首页消息项探索")
print("=" * 40)

d.click(*TABS["首页"])
time.sleep(1.5)

# 消息项 - "你有一笔订单已完成" 等
# bounds大约在 y=1491-1684
print("\n🔄 点击首页消息项")
d.click(540, 1600)
time.sleep(2)

current = get_current_app()
print(f"  当前App: {current}")
if PACKAGE in current:
    dump_page("home_message_detail")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    print(f"  ⚠️ 离开了App")
    d.app_start(PACKAGE, stop=False)
    time.sleep(2)

# === 6. "更多消息"入口 ===
print("\n" + "=" * 40)
print("  6. 更多消息入口")
print("=" * 40)

d.click(*TABS["首页"])
time.sleep(1)
# 滑到消息底部
d.swipe(540, 1800, 540, 1000, duration=0.3)
time.sleep(0.5)

# "更多消息" bounds=[447,2168][599,2219] 中心(523,2193)
print("\n🔄 点击'更多消息'")
d.click(523, 2193)
time.sleep(2)

current = get_current_app()
print(f"  当前App: {current}")
if PACKAGE in current:
    dump_page("more_messages")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    print(f"  ⚠️ 离开了App")
    d.app_start(PACKAGE, stop=False)
    time.sleep(2)

# 回到首页
d.click(*TABS["首页"])
time.sleep(1)

print("\n✅ 精确探索完成")
