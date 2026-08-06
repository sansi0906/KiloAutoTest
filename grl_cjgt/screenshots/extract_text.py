import re

with open(r'E:\KiloAutoTest\grl_cjgt\screenshots\ui_super_individual.xml', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'text="([^"]*)"', content)
print('页面文本内容:')
for i, m in enumerate(matches):
    if m.strip():
        print(f'  [{i}]: {m}')

# Also find clickable elements
clickables = re.findall(r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', content)
print('\n可点击元素坐标:')
for i, (x1, y1, x2, y2) in enumerate(clickables[:20]):
    print(f'  [{i}]: [{x1},{y1}]-[{x2},{y2}] 中心: ({(int(x1)+int(x2))//2}, {(int(y1)+int(y2))//2})')