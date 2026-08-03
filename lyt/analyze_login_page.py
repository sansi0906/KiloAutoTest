"""
详细检查乐云泰App登录页面结构
"""
import uiautomator2 as u2
import re
import time

d = u2.connect()

# 获取当前页面XML
xml = d.dump_hierarchy()

# 提取所有节点信息
print("=== 登录页面详细结构 ===\n")

# 提取所有文本和坐标
elements = re.findall(r'text="([^"]*)"[^>]*class="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for text, cls, x1, y1, x2, y2 in elements:
    if text.strip():
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  [{cls}] text='{text}' 位置: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")

print("\n=== 可点击元素 ===")
clickable = re.findall(r'clickable="true"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for text, x1, y1, x2, y2 in clickable:
    cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
    print(f"  text='{text}' 位置: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")

print("\n=== CheckBox元素 ===")
checkboxes = re.findall(r'class="android\.widget\.CheckBox"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for x1, y1, x2, y2 in checkboxes:
    cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
    print(f"  CheckBox: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")

print("\n=== EditText元素 ===")
edittexts = re.findall(r'class="android\.widget\.EditText"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for text, x1, y1, x2, y2 in edittexts:
    cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
    print(f"  EditText text='{text}': [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")

# 尝试点击登录按钮
print("\n=== 尝试点击登录按钮 ===")
if d(text="登录").exists(timeout=1):
    print("  找到'登录'按钮")
    info = d(text="登录").info
    print(f"  信息: {info}")
    
    # 检查是否可点击
    if info.get('clickable', False):
        print("  登录按钮可点击")
    else:
        print("  登录按钮不可点击")
else:
    print("  未找到'登录'文本")

# 检查协议相关
print("\n=== 协议相关元素 ===")
agreement_elements = re.findall(r'(?:协议|同意)[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
if agreement_elements:
    for x1, y1, x2, y2 in agreement_elements[:5]:
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  协议元素: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")
else:
    print("  未找到协议相关元素")

# 打印部分XML查看结构
print("\n=== XML结构片段 ===")
# 搜索登录相关的节点
login_pattern = re.findall(r'<node[^>]*(?:登录|协议|同意)[^>]*>', xml)
for p in login_pattern[:5]:
    print(f"  {p[:200]}")
