"""
乐云泰App - 深入探索首页功能入口和订单详情
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
    
    print(f"\n  📍 文本元素坐标:")
    for t, x1, y1, x2, y2 in app_elements[:25]:
        cx, cy = (x1+x2)//2, (y1+y2)//2
        print(f"    [{t}] ({cx},{cy})")
    
    # 可点击区域
    clickable_bounds = re.findall(
        r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    print(f"\n  👆 可点击区域 ({len(clickable_bounds)}个):")
    for x1, y1, x2, y2 in clickable_bounds[:15]:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"    ({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
    
    shot_path = f"{DUMP_DIR}/{step_name}_{ts}.png"
    d.screenshot(shot_path)
    print(f"\n  💾 XML: {xml_path}")
    print(f"  📸 截图: {shot_path}")
    return non_empty

# 底部Tab坐标
TABS = {
    "首页": (135, 2321),
    "客户": (405, 2321),
    "购物车": (675, 2321),
    "订单": (945, 2321),
}

print("=" * 60)
print("  乐云泰App 深入探索")
print("=" * 60)

# === 1. 首页功能入口探索 ===
print("\n" + "=" * 40)
print("  1. 首页功能入口探索")
print("=" * 40)

d.click(*TABS["首页"])
time.sleep(1.5)

# 首页有4个功能入口：设备、建材、人才、服务
# 根据XML分析:
# 设备: bounds=[35,873][528,1075] 中心(281,974)
# 建材: bounds=[553,873][1046,1075] 中心(799,974)
# 人才: bounds=[35,1098][528,1299] 中心(281,1198)
# 服务: bounds=[553,1098][1046,1299] 中心(799,1198)
entries = [
    ("设备", 281, 974),
    ("建材", 799, 974),
    ("人才", 281, 1198),
    ("服务", 799, 1198),
]

for entry_name, ex, ey in entries:
    print(f"\n🔄 点击首页功能入口 [{entry_name}] @ ({ex},{ey})")
    d.click(ex, ey)
    time.sleep(2)
    
    # 处理弹窗
    for text in ["忽略本次", "下次再说", "稍后再说", "确定", "同意", "关闭", "允许", "取消"]:
        try:
            if d(text=text).exists(timeout=0.3):
                d(text=text).click()
                time.sleep(0.3)
        except:
            pass
    
    dump_page(f"entry_{entry_name}")
    
    # 返回
    d.press("back")
    time.sleep(1.5)
    
    # 确保回到首页
    d.click(*TABS["首页"])
    time.sleep(1)

# === 2. 订单详情探索 ===
print("\n" + "=" * 40)
print("  2. 订单详情探索")
print("=" * 40)

d.click(*TABS["订单"])
time.sleep(1.5)

# 点击第一个订单 - 根据XML，订单项大约在y=400附近
print("\n🔄 点击第一个订单项")
d.click(540, 400)
time.sleep(2)

# 处理弹窗
for text in ["忽略本次", "下次再说", "稍后再说", "确定", "同意", "关闭", "允许", "取消"]:
    try:
        if d(text=text).exists(timeout=0.3):
            d(text=text).click()
            time.sleep(0.3)
    except:
        pass

dump_page("order_detail")

# 返回
d.press("back")
time.sleep(1.5)

# === 3. 客户详情探索 ===
print("\n" + "=" * 40)
print("  3. 客户详情探索")
print("=" * 40)

d.click(*TABS["客户"])
time.sleep(1.5)

# 点击第一个客户项
print("\n🔄 点击第一个客户项")
d.click(540, 500)
time.sleep(2)

for text in ["忽略本次", "下次再说", "稍后再说", "确定", "同意", "关闭", "允许", "取消"]:
    try:
        if d(text=text).exists(timeout=0.3):
            d(text=text).click()
            time.sleep(0.3)
    except:
        pass

dump_page("customer_detail")

# 返回
d.press("back")
time.sleep(1.5)

# === 4. 购物车操作探索 ===
print("\n" + "=" * 40)
print("  4. 购物车操作探索")
print("=" * 40)

d.click(*TABS["购物车"])
time.sleep(1.5)

dump_page("cart_detail")

# 回到首页
d.click(*TABS["首页"])
time.sleep(1)

print("\n✅ 深入探索完成")
print(f"\n📁 所有XML和截图保存在: {DUMP_DIR}")
