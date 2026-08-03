"""
乐云泰App - 逐页探索各Tab内容
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
    
    # 带bounds的文本元素（只取乐云泰App的）
    elements = re.findall(
        r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    app_elements = [(t, int(x1), int(y1), int(x2), int(y2)) 
                    for t, x1, y1, x2, y2 in elements 
                    if t.strip() and int(y1) > 104]
    
    # 底部Tab区域 (y > 2240)
    tab_elements = [(t, x1, y1, x2, y2) for t, x1, y1, x2, y2 in app_elements if y1 > 2240]
    
    # 可点击元素bounds
    clickable_bounds = re.findall(
        r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    
    print(f"\n{'='*60}")
    print(f"  📄 {step_name}")
    print(f"{'='*60}")
    print(f"  📝 文本元素 ({len(non_empty)}个):")
    for t in non_empty[:25]:
        print(f"    [{t}]")
    
    print(f"\n  📍 底部Tab ({len(tab_elements)}个):")
    for t, x1, y1, x2, y2 in tab_elements:
        cx, cy = (x1+x2)//2, (y1+y2)//2
        print(f"    [{t}] 中心:({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
    
    print(f"\n  👆 可点击区域 ({len(clickable_bounds)}个):")
    for x1, y1, x2, y2 in clickable_bounds[:20]:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"    ({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
    
    # 截图
    shot_path = f"{DUMP_DIR}/{step_name}_{ts}.png"
    d.screenshot(shot_path)
    print(f"\n  💾 XML: {xml_path}")
    print(f"  📸 截图: {shot_path}")
    return non_empty

# 底部Tab坐标（基于实际XML分析）
TABS = [
    ("首页", 135, 2321),
    ("客户", 405, 2321),
    ("购物车", 675, 2321),
    ("订单", 945, 2321),
]

print("=" * 60)
print("  乐云泰App 逐Tab探索")
print("=" * 60)

# 探索每个Tab
for tab_name, tx, ty in TABS:
    print(f"\n🔄 点击 [{tab_name}] Tab @ ({tx},{ty})")
    d.click(tx, ty)
    time.sleep(2)
    
    # 处理弹窗
    for text in ["忽略本次", "下次再说", "稍后再说", "确定", "同意", "关闭", "允许", "取消"]:
        try:
            if d(text=text).exists(timeout=0.3):
                d(text=text).click()
                time.sleep(0.3)
        except:
            pass
    
    dump_page(f"tab_{tab_name}")
    
    # 滑动查看更多
    d.swipe(540, 1800, 540, 600, duration=0.5)
    time.sleep(1)
    dump_page(f"tab_{tab_name}_scrolled")
    
    # 回到顶部
    d.swipe(540, 600, 540, 1800, duration=0.5)
    time.sleep(0.5)

# 回到首页
d.click(135, 2321)
time.sleep(1)
print("\n✅ 探索完成")
