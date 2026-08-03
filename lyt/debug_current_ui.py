"""
调试脚本 - 查看乐云泰App当前UI结构
"""
import uiautomator2 as u2
import re
import time

d = u2.connect()
d.app_start("com.grl.leyuntai", stop=False)
time.sleep(3)

# 获取页面XML
xml = d.dump_hierarchy()

# 提取所有文本
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]
print('=== 当前页面所有文本 ===')
for t in non_empty:
    print(f'  {t}')

# 提取可点击元素
clickable = re.findall(r'clickable="true"[^>]*text="([^"]*)"', xml)
print('\n=== 可点击元素 ===')
for c in clickable:
    if c.strip():
        print(f'  {c}')

# 提取resource-id
res_ids = list(set(re.findall(r'resource-id="([^"]*)"', xml)))
print('\n=== Resource IDs ===')
for r in res_ids:
    if ':id/' in r:
        print(f'  {r}')

# 提取EditText
edittexts = re.findall(r'class="android\.widget\.EditText"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print('\n=== 输入框位置 ===')
for i, (x1, y1, x2, y2) in enumerate(edittexts):
    print(f'  EditText[{i}]: [{x1},{y1}][{x2},{y2}] 中心: ({(int(x1)+int(x2))//2}, {(int(y1)+int(y2))//2})')

# 提取按钮
buttons = re.findall(r'class="android\.widget\.Button"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
if not buttons:
    # 尝试其他方式查找按钮
    buttons = re.findall(r'text="([^"]*)"[^>]*clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    
print('\n=== 按钮/可点击元素 ===')
for b in buttons[:20]:
    if len(b) >= 4:
        text, x1, y1, x2, y2 = b[0], b[1], b[2], b[3], b[4]
        print(f'  {text}: [{x1},{y1}][{x2},{y2}] 中心: ({(int(x1)+int(x2))//2}, {(int(y1)+int(y2))//2})')

print('\n=== 页面XML前3000字符 ===')
print(xml[:3000])
