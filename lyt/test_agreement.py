"""
尝试勾选乐云泰App登录协议
"""
import uiautomator2 as u2
import time

d = u2.connect()

# 协议文本位置: [278,1732][854,1776] 中心: (566,1754)
# 尝试点击协议文本左侧可能的勾选框位置
print("尝试勾选协议...")

# 尝试点击协议文本区域
d.click(566, 1754)
time.sleep(1)

# 检查登录按钮状态
info = d(text="登录").info
print(f"登录按钮状态: clickable={info.get('clickable')}, checked={info.get('checked')}")

# 如果仍不可点击，尝试点击协议文本的左侧
if not info.get('clickable', False):
    print("尝试点击协议文本左侧...")
    d.click(300, 1754)  # 协议文本左侧
    time.sleep(0.5)
    
    info = d(text="登录").info
    print(f"登录按钮状态: clickable={info.get('clickable')}")

# 尝试点击更左侧
if not info.get('clickable', False):
    print("尝试点击更左侧...")
    d.click(150, 1754)  # 更左侧
    time.sleep(0.5)
    
    info = d(text="登录").info
    print(f"登录按钮状态: clickable={info.get('clickable')}")

# 尝试点击更靠上的位置
if not info.get('clickable', False):
    print("尝试点击协议上方...")
    d.click(150, 1700)  # 协议上方
    time.sleep(0.5)
    
    info = d(text="登录").info
    print(f"登录按钮状态: clickable={info.get('clickable')}")

# 查看当前页面所有可点击元素
xml = d.dump_hierarchy()
import re
clickable = re.findall(r'clickable="true"[^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print(f"\n当前可点击元素: {len(clickable)}个")
for text, x1, y1, x2, y2 in clickable[:10]:
    print(f"  text='{text}' 位置: [{x1},{y1}][{x2},{y2}]")

# 再次尝试点击协议文本本身
print("\n再次尝试点击协议文本中心...")
d.click(566, 1754)
time.sleep(1)

# 检查是否有变化
info = d(text="登录").info
print(f"登录按钮状态: clickable={info.get('clickable')}")

# 如果仍不行，尝试用ADB命令
if not info.get('clickable', False):
    print("\n尝试ADB点击...")
    import subprocess
    subprocess.run("adb shell input tap 566 1754", shell=True, capture_output=True)
    time.sleep(0.5)
    
    info = d(text="登录").info
    print(f"登录按钮状态: clickable={info.get('clickable')}")

# 截屏
d.screenshot("E:/KiloAutoTest/lyt/screenshots/agreement_test.png")
print("\n截图已保存")
