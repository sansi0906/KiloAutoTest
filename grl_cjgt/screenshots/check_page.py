import re

with open(r'E:\KiloAutoTest\grl_cjgt\screenshots\ui_current.xml', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'text="([^"]*)"', content)
print('当前页面文本内容:')
for i, m in enumerate(matches):
    if m.strip():
        print(f'  [{i}]: {m}')