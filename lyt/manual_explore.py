"""
乐云泰App - 手动探索工具
逐页dump UI结构，便于分析
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
    """dump当前页面UI结构"""
    ts = datetime.now().strftime("%H%M%S")
    xml = d.dump_hierarchy()
    
    # 保存原始XML
    xml_path = f"{DUMP_DIR}/{step_name}_{ts}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)
    
    # 解析关键信息
    texts = re.findall(r'text="([^"]*)"', xml)
    non_empty = [t for t in texts if t.strip()]
    
    # 可点击元素
    clickable = re.findall(r'clickable="true"[^>]*text="([^"]*)"', xml)
    clickable = [c for c in clickable if c.strip()]
    
    # EditText
    edittexts = re.findall(
        r'class="android\.widget\.EditText"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    
    # 带bounds的文本元素
    elements_with_bounds = re.findall(
        r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    
    # 可点击元素的bounds
    clickable_bounds = re.findall(
        r'clickable="true"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    
    print(f"\n{'='*60}")
    print(f"  📄 {step_name}")
    print(f"{'='*60}")
    print(f"  📝 文本元素 ({len(non_empty)}个):")
    for t in non_empty[:20]:
        print(f"    [{t}]")
    
    print(f"\n  👆 可点击元素 ({len(clickable)}个):")
    for c in clickable[:15]:
        print(f"    [{c}]")
    
    print(f"\n  📝 EditText ({len(edittexts)}个):")
    for text, x1, y1, x2, y2 in edittexts:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"    text='{text}' 中心:({cx},{cy})")
    
    print(f"\n  📐 可点击元素坐标:")
    for text, x1, y1, x2, y2 in clickable_bounds[:15]:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"    [{text}] ({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
    
    # 截图
    shot_path = f"{DUMP_DIR}/{step_name}_{ts}.png"
    d.screenshot(shot_path)
    
    print(f"\n  💾 XML: {xml_path}")
    print(f"  📸 截图: {shot_path}")
    
    return non_empty, clickable, edittexts

# ==================== 开始探索 ====================
print("=" * 60)
print("  乐云泰App 手动探索工具")
print("=" * 60)

# 探索当前页面
dump_page("01_current")
