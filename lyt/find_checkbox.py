"""
找到乐云泰App真正的协议勾选框
"""
import uiautomator2 as u2
import re
import time

d = u2.connect()

# 先返回登录页面
d.press("back")
time.sleep(1)
d.press("back")
time.sleep(1)

# 检查是否在登录页
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
login_texts = [t for t in texts if t.strip()]
print(f"当前页面: {login_texts[:10]}")

# 提取所有节点，包括不可见的
print("\n=== 所有UI元素（包括不可点击的）===")
all_elements = re.findall(
    r'text="([^"]*)"[^>]*'
    r'(?:resource-id="([^"]*)")?[^>]*'
    r'class="([^"]*)"[^>]*'
    r'clickable="([^"]*)"[^>]*'
    r'checked="([^"]*)"[^>]*'
    r'enabled="([^"]*)"[^>]*'
    r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', 
    xml
)

for text, res_id, cls, clickable, checked, enabled, x1, y1, x2, y2 in all_elements:
    if text.strip() or cls in ['android.widget.CheckBox', 'android.widget.EditText', 'android.widget.Button']:
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  [{cls}] text='{text}' resId='{res_id}' clickable={clickable} checked={checked} enabled={enabled} 位置: ({cx},{cy})")

# 专门查找CheckBox或类似勾选的元素
print("\n=== 查找勾选相关元素 ===")
# 查找有checkable属性的元素
checkable_elements = re.findall(r'checkable="true"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
if checkable_elements:
    for text, x1, y1, x2, y2 in checkable_elements:
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  checkable元素: text='{text}' 位置: ({cx},{cy})")
else:
    print("  未找到checkable元素")

# 查找所有checkable属性的节点
checkable_nodes = re.findall(r'checkable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print(f"\n  checkable节点数量: {len(checkable_nodes)}")
for x1, y1, x2, y2 in checkable_nodes:
    cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
    print(f"    位置: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")

# 查看协议文本附近的区域
print("\n=== 协议文本位置详情 ===")
agreement_match = re.findall(r'已阅读并同意[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
if agreement_match:
    for x1, y1, x2, y2 in agreement_match:
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  协议文本: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")
        
        # 检查协议文本左侧10-50像素的区域
        print(f"  检查左侧区域...")
        for dx in [10, 30, 50]:
            check_x = max(50, int(x1) - dx)
            print(f"    尝试点击: ({check_x}, {cy})")

# 尝试点击协议文本左侧的小圆圈位置
print("\n=== 尝试点击协议左侧 ===")
# 协议文本在 [278,1732][854,1776]，中心: (566,1754)
# 左侧可能有一个小圆圈勾选框
test_x_positions = [150, 180, 200, 220, 250, 270]
for tx in test_x_positions:
    print(f"  尝试点击 ({tx}, 1754)...")
    d.click(tx, 1754)
    time.sleep(0.3)
    
    # 检查登录按钮状态
    try:
        info = d(text="登录").info
        if info.get('clickable', False):
            print(f"    ✅ 登录按钮已可点击!")
            break
    except:
        pass

# 如果还是不行，尝试其他方式
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
print(f"\n当前文本: {[t for t in texts if t.strip()][:10]}")

# 再次分析
print("\n=== 分析可点击区域 ===")
clickable_areas = re.findall(r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print(f"可点击区域数量: {len(clickable_areas)}")
for x1, y1, x2, y2 in clickable_areas[:20]:
    cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
    print(f"  [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")
