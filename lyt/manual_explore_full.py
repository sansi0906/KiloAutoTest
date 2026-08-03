"""
乐云泰App - 完整手动探索脚本
系统性探索所有模块：登录、首页、客户、购物车、订单、各功能入口
"""
import uiautomator2 as u2
import re
import os
import time
from datetime import datetime

d = u2.connect()
DUMP_DIR = "E:/KiloAutoTest/lyt/ui_dumps"
SHOT_DIR = "E:/KiloAutoTest/lyt/screenshots/explore_full"
os.makedirs(DUMP_DIR, exist_ok=True)
os.makedirs(SHOT_DIR, exist_ok=True)

PACKAGE = "com.grl.leyuntai"

# 底部Tab坐标（基于之前探索的确认结果）
TABS = {
    "首页": (135, 2321),
    "客户": (405, 2321),
    "购物车": (675, 2321),
    "订单": (945, 2321),
}

def dump_page(step_name, verbose=True):
    """dump当前页面UI，并保存XML和截图"""
    ts = datetime.now().strftime("%H%M%S")
    try:
        xml = d.dump_hierarchy()
    except Exception as e:
        print(f"  ❌ dump失败: {e}")
        return [], []

    xml_path = f"{DUMP_DIR}/{step_name}_{ts}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)

    shot_path = f"{SHOT_DIR}/{step_name}_{ts}.png"
    try:
        d.screenshot(shot_path)
    except:
        pass

    # 提取文本元素
    texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2) 
                 for t, x1, y1, x2, y2 in texts 
                 if t.strip() and int(y1) > 104]

    # 可点击元素
    clickable = re.findall(
        r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    click_centers = [((int(x1)+int(x2))//2, (int(y1)+int(y2))//2) 
                     for x1, y1, x2, y2 in clickable]

    if verbose:
        print(f"\n{'='*60}")
        print(f"  📄 {step_name}")
        print(f"{'='*60}")
        print(f"  📝 文本元素 ({len(non_empty)}个):")
        for t, cx, cy in non_empty[:30]:
            print(f"    [{t}] @({cx},{cy})")
        print(f"\n  👆 可点击元素 ({len(click_centers)}个)")
        print(f"  💾 XML: {xml_path}")
        print(f"  📷 截图: {shot_path}")

    return non_empty, click_centers


def get_current_app():
    try:
        return d.app_current().get("package", "")
    except:
        return ""


def safe_back_to_app():
    """返回直到回到乐云泰App"""
    for _ in range(3):
        cur = get_current_app()
        if PACKAGE in cur:
            return True
        d.press("back")
        time.sleep(1.5)
    # 如果还是不在app，重启
    if PACKAGE not in get_current_app():
        print("  ⚠️ 不在App内，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(3)
    return PACKAGE in get_current_app()


def ensure_app():
    """确保在乐云泰App内"""
    cur = get_current_app()
    if PACKAGE not in cur:
        print(f"  ⚠️ 不在App内（{cur}），重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(3)
    return PACKAGE in get_current_app()


print("=" * 60)
print("  乐云泰App 完整手动探索")
print("=" * 60)

# ============== 阶段1：首页 ==============
print("\n" + "🚀 阶段1：首页")
ensure_app()
time.sleep(1)

# 点击首页Tab
d.click(*TABS["首页"])
time.sleep(2)
dump_page("01_home_main")

# 首页向下滚动
print("\n🔄 首页下滑1")
d.swipe(540, 1800, 540, 800, duration=0.5)
time.sleep(1)
dump_page("01_home_scroll_1")

# 继续下滑
print("\n🔄 首页下滑2")
d.swipe(540, 1800, 540, 800, duration=0.5)
time.sleep(1)
dump_page("01_home_scroll_2")

# 回到顶部
d.swipe(540, 400, 540, 1800, duration=0.8)
time.sleep(1)

# ============== 阶段2：首页功能入口探索 ==============
print("\n" + "🚀 阶段2：首页功能入口（设备/建材/人才/服务）")

# 先重新dump首页，找到功能入口的准确位置
texts, clicks = dump_page("01_home_entries", verbose=False)
# 根据之前的探索：设备(281,974)、建材、人才、服务 入口
# 尝试识别四个入口
entries_found = []
for t, cx, cy in texts:
    if t in ["设备", "建材", "人才", "服务"]:
        entries_found.append((t, cx, cy))
        print(f"  ✅ 找到入口：{t} @({cx},{cy})")

if not entries_found:
    print("  ⚠️ 未找到功能入口文本，使用默认坐标")
    entries_found = [
        ("设备", 281, 974),
        ("建材", 800, 974),
        ("人才", 281, 1180),
        ("服务", 800, 1180),
    ]

# 逐个探索每个入口
for entry_name, ex, ey in entries_found:
    print(f"\n--- 探索入口：{entry_name} @({ex},{ey}) ---")
    ensure_app()
    d.click(*TABS["首页"])
    time.sleep(1.5)
    
    # 点击入口
    print(f"  🔄 点击 {entry_name}")
    d.click(ex, ey)
    time.sleep(3)
    
    cur = get_current_app()
    if PACKAGE in cur:
        print(f"  ✅ 仍在App内")
        dump_page(f"02_entry_{entry_name}")
        
        # 在子页面下滑
        d.swipe(540, 1800, 540, 800, duration=0.5)
        time.sleep(1)
        dump_page(f"02_entry_{entry_name}_scroll")
        
        # 返回
        d.press("back")
        time.sleep(1.5)
    else:
        print(f"  ⚠️ 跳出App，当前: {cur}")
        safe_back_to_app()

# ============== 阶段3：客户页 ==============
print("\n" + "🚀 阶段3：客户页")
ensure_app()
time.sleep(1)

d.click(*TABS["客户"])
time.sleep(2)
dump_page("03_customer_main")

# 滑动
print("\n🔄 客户页下滑")
d.swipe(540, 1800, 540, 800, duration=0.5)
time.sleep(1)
dump_page("03_customer_scroll")

# 查找并点击搜索框
texts, _ = dump_page("03_customer_for_search", verbose=False)
search_y = None
for t, cx, cy in texts:
    if "搜索" in t or "客户" in t and cy < 300:
        search_y = cy
        print(f"  🔍 可能的搜索框: [{t}] @({cx},{cy})")

# 点击顶部搜索区域
print("\n🔄 点击搜索框")
d.click(505, 204)
time.sleep(1.5)
dump_page("03_customer_search_input")

# 输入搜索词
try:
    el = d(className="android.widget.EditText")
    if el.exists(timeout=1):
        el.set_text("工人乐")
        time.sleep(0.5)
        dump_page("03_customer_search_typed")
        
        # 触发搜索
        d.press("enter")
        time.sleep(2)
        dump_page("03_customer_search_result")
        
        # 返回
        d.press("back")
        time.sleep(1)
        d.press("back")
        time.sleep(1)
except Exception as e:
    print(f"  搜索失败: {e}")

# ============== 阶段4：购物车 ==============
print("\n" + "🚀 阶段4：购物车")
ensure_app()
time.sleep(1)

d.click(*TABS["购物车"])
time.sleep(2)
dump_page("04_cart_main")

# 滑动
print("\n🔄 购物车下滑")
d.swipe(540, 1800, 540, 800, duration=0.5)
time.sleep(1)
dump_page("04_cart_scroll")

# 尝试点击第一个商品（如果有）
texts, clicks = dump_page("04_cart_check", verbose=False)
# 找商品项的点击区域 - 通常是 y > 400 的元素
item_clicked = False
for cx, cy in clicks:
    if 400 < cy < 1500:
        print(f"  🔄 点击商品项 @({cx},{cy})")
        d.click(cx, cy)
        time.sleep(2)
        cur = get_current_app()
        if PACKAGE in cur:
            dump_page("04_cart_item_detail")
            d.press("back")
            time.sleep(1.5)
            item_clicked = True
            break
        else:
            safe_back_to_app()

if not item_clicked:
    # 尝试点击商品名称附近
    print("  🔄 尝试默认位置点击商品")
    d.click(540, 700)
    time.sleep(2)
    if PACKAGE in get_current_app():
        dump_page("04_cart_item_detail")
        d.press("back")
        time.sleep(1.5)

# ============== 阶段5：订单页 ==============
print("\n" + "🚀 阶段5：订单页")
ensure_app()
time.sleep(1)

d.click(*TABS["订单"])
time.sleep(2)
dump_page("05_orders_main")

# 查找订单状态Tab
texts, _ = dump_page("05_orders_tabs", verbose=False)
order_tabs = []
for t, cx, cy in texts:
    if t in ["全部", "待付款", "待发货", "待收货", "已完成", "已取消"]:
        order_tabs.append((t, cx, cy))
        print(f"  📑 订单Tab: [{t}] @({cx},{cy})")

# 点击每个订单状态Tab
for tab_name, tx, ty in order_tabs[:3]:  # 最多测试3个
    print(f"\n  🔄 点击订单Tab: {tab_name}")
    d.click(tx, ty)
    time.sleep(1.5)
    dump_page(f"05_orders_tab_{tab_name}")

# 点击第一个订单查看详情
print("\n🔄 点击订单详情")
# 先回到"全部"Tab
if order_tabs:
    for tab_name, tx, ty in order_tabs:
        if tab_name == "全部":
            d.click(tx, ty)
            time.sleep(1)
            break

# 点击第一个订单
# 订单项通常在 y=400-600
d.click(540, 500)
time.sleep(2)
cur = get_current_app()
if PACKAGE in cur:
    print(f"  ✅ 进入订单详情")
    dump_page("05_order_detail")
    
    # 滑动查看更多
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    dump_page("05_order_detail_scroll")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
else:
    safe_back_to_app()

# ============== 阶段6：消息中心 ==============
print("\n" + "🚀 阶段6：消息中心")
ensure_app()
d.click(*TABS["首页"])
time.sleep(1.5)

# 查找消息入口 - 通常是顶部或侧边的消息图标
texts, clicks = dump_page("06_home_for_msg", verbose=False)
msg_found = False
for t, cx, cy in texts:
    if "消息" in t or "通知" in t:
        print(f"  🔔 找到消息入口: [{t}] @({cx},{cy})")
        d.click(cx, cy)
        time.sleep(2)
        if PACKAGE in get_current_app():
            dump_page("06_messages")
            d.press("back")
            time.sleep(1)
            msg_found = True
            break

if not msg_found:
    # 尝试右上角消息图标
    print("  🔄 尝试右上角消息图标")
    d.click(1000, 200)
    time.sleep(2)
    if PACKAGE in get_current_app():
        dump_page("06_messages_topright")
        d.press("back")
        time.sleep(1)

# ============== 阶段7：个人中心 ==============
print("\n" + "🚀 阶段7：个人中心")
ensure_app()
d.click(*TABS["首页"])
time.sleep(1.5)

# 查找个人中心入口 - 通常是顶部右侧头像或菜单
texts, clicks = dump_page("07_home_for_user", verbose=False)
user_found = False
for t, cx, cy in texts:
    if t in ["我的", "个人中心", "设置"]:
        print(f"  👤 找到用户入口: [{t}] @({cx},{cy})")
        d.click(cx, cy)
        time.sleep(2)
        if PACKAGE in get_current_app():
            dump_page("07_user_center")
            d.press("back")
            time.sleep(1)
            user_found = True
            break

if not user_found:
    # 滑动查看底部
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts, _ = dump_page("07_home_scroll_user", verbose=False)
    for t, cx, cy in texts:
        if t in ["我的", "个人中心", "设置"]:
            print(f"  👤 找到用户入口: [{t}] @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(2)
            if PACKAGE in get_current_app():
                dump_page("07_user_center")
                d.press("back")
                time.sleep(1)
                user_found = True
                break

# 回到首页
ensure_app()
d.click(*TABS["首页"])
time.sleep(1)

print("\n" + "=" * 60)
print("  ✅ 完整手动探索完成")
print("=" * 60)
print(f"\n📁 XML dump: {DUMP_DIR}")
print(f"📷 截图: {SHOT_DIR}")
