"""
检查乐云泰App实际页面结构
"""
import uiautomator2 as u2
import re
import time

d = u2.connect()

# 检查当前页面
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]

print("=== 当前页面文本 ===")
for t in non_empty:
    print(f"  [{t}]")

# 检查底部Tab区域
print("\n=== 查找Tab相关元素 ===")
tab_texts = ["首页", "订单", "商品", "我的"]
for tab in tab_texts:
    exists = any(tab in t for t in non_empty)
    print(f"  '{tab}': {'存在' if exists else '不存在'}")

# 查找底部区域的可点击元素
print("\n=== 底部区域元素 ===")
all_elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for text, x1, y1, x2, y2 in all_elements:
    y = int(y1)
    if y > 2200 and y < 2400:  # 底部区域
        print(f"  text='{text}': [{x1},{y1}][{x2},{y2}]")

# 尝试点击Tab
print("\n=== 尝试切换Tab ===")
# 点击首页
d.click(135, 2280)
time.sleep(1)
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]
print(f"切换后页面文本 ({len(non_empty)}个):")
for t in non_empty[:10]:
    print(f"  [{t}]")

# 点击商品
d.click(675, 2280)
time.sleep(1)
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]
print(f"\n商品页文本 ({len(non_empty)}个):")
for t in non_empty[:10]:
    print(f"  [{t}]")

# 点击订单
d.click(405, 2280)
time.sleep(1)
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]
print(f"\n订单页文本 ({len(non_empty)}个):")
for t in non_empty[:10]:
    print(f"  [{t}]")

# 点击我的
d.click(945, 2280)
time.sleep(1)
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
non_empty = [t for t in texts if t.strip()]
print(f"\n我的页文本 ({len(non_empty)}个):")
for t in non_empty[:10]:
    print(f"  [{t}]")
