import re

with open(r'E:\KiloAutoTest\grl_cjgt\screenshots\ui_after_login2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the "超级个体" section with its parent bounds
# Look for the ViewGroup containing "超级个体"
pattern = r'<node index="2" text="" resource-id="" class="android\.view\.ViewGroup"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"><node index="0" text="" resource-id="image"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]" /><node index="1" text="超级个体"[^>]*>'
matches = re.findall(pattern, content)
if matches:
    for m in matches:
        x1, y1, x2, y2, ix1, iy1, ix2, iy2 = m
        print(f"超级个体按钮容器: [{x1},{y1}]-[{x2},{y2}] 中心: ({(int(x1)+int(x2))//2}, {(int(y1)+int(y2))//2})")
        print(f"  图标: [{ix1},{iy1}]-[{ix2},{iy2}]")

# Also try finding by text directly
text_matches = re.finditer(r'text="超级个体"', content)
for tm in text_matches:
    pos = tm.start()
    # Find the nearest parent bounds before this position
    before = content[:pos]
    # Find the last bounds
    bounds_match = re.findall(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', before[-2000:])
    if bounds_match:
        last = bounds_match[-1]
        print(f"Found near 超级个体: [{last[0]},{last[1]}]-[{last[2]},{last[3]}] 中心: ({(int(last[0])+int(last[2]))//2}, {(int(last[1])+int(last[3]))//2})")