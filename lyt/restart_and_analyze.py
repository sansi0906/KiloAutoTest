"""
重新启动乐云泰App并分析登录页面协议勾选
"""
import uiautomator2 as u2
import re
import time
import os

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
SCREENSHOT_DIR = "E:/KiloAutoTest/lyt/screenshots"

# 强制重启App
print("重启乐云泰App...")
d.app_stop(PACKAGE)
time.sleep(2)
d.app_start(PACKAGE)
time.sleep(4)

# 处理可能出现的弹窗
for text in ["同意", "关闭", "允许", "确定", "忽略本次", "我知道了", "拒绝并退出", "取消"]:
    try:
        if d(text=text).exists(timeout=0.3):
            d(text=text).click()
            time.sleep(0.3)
    except:
        pass

# 检查是否有隐私政策页面
texts = re.findall(r'text="([^"]*)"', d.dump_hierarchy())
texts = [t for t in texts if t.strip()]
print(f"初始页面: {texts[:8]}")

# 如果有隐私政策，同意它
if any("同意" in t for t in texts) and any("拒绝" in t for t in texts):
    print("点击同意隐私政策...")
    d.click(760, 1580)
    time.sleep(2)

# 检查引导页
texts = re.findall(r'text="([^"]*)"', d.dump_hierarchy())
texts = [t for t in texts if t.strip()]
print(f"当前页面: {texts[:8]}")

if any("开始使用" in t for t in texts):
    print("跳过引导页...")
    for i in range(4):
        d.swipe(0.8, 0.5, 0.1, 0.5, duration=0.3)
        time.sleep(0.8)
    # 点击开始使用按钮
    d.click(540, 1927)
    time.sleep(2)

# 截一张图看看
d.screenshot(f"{SCREENSHOT_DIR}/fresh_start.png")
print("已截图: fresh_start.png")

# 获取登录页面结构
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
texts = [t for t in texts if t.strip()]
print(f"\n登录页面文本: {texts[:15]}")

# 如果已经在登录页面，分析协议勾选
if any("登录" in t for t in texts):
    print("\n分析登录页面结构...")
    
    # 提取所有节点
    all_elements = re.findall(
        r'text="([^"]*)"[^>]*'
        r'class="([^"]*)"[^>]*'
        r'clickable="([^"]*)"[^>]*'
        r'checked="([^"]*)"[^>]*'
        r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
        xml
    )
    
    for text, cls, clickable, checked, x1, y1, x2, y2 in all_elements:
        if text.strip():
            cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
            print(f"  [{cls}] '{text}' clickable={clickable} checked={checked} ({cx},{cy})")
    
    # 检查协议相关
    print("\n检查协议元素...")
    agreement_related = re.findall(r'(?:同意|协议|勾选|agree)[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    for x1, y1, x2, y2 in agreement_related[:5]:
        cx, cy = (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2
        print(f"  协议元素: [{x1},{y1}][{x2},{y2}] 中心: ({cx},{cy})")
    
    # 检查登录按钮状态
    login_info = d(text="登录").info
    print(f"\n登录按钮状态: clickable={login_info.get('clickable')}, checked={login_info.get('checked')}")
    
    # 尝试找到协议勾选框
    # 可能在协议文本左侧有一个圆形或方形的勾选框
    print("\n尝试各种勾选方式...")
    
    # 方式1: 尝试点击协议文本区域（可能整个区域都是勾选框）
    print("方式1: 点击协议文本中心...")
    d.click(566, 1754)
    time.sleep(1)
    login_info = d(text="登录").info
    print(f"  登录按钮: clickable={login_info.get('clickable')}")
    
    if login_info.get('clickable', False):
        print("  ✅ 成功！")
    else:
        # 方式2: 点击协议文本左侧
        print("方式2: 点击协议文本左侧...")
        # 先返回（因为方式1可能打开了协议详情）
        d.press("back")
        time.sleep(1)
        d.click(350, 1754)  # 左侧
        time.sleep(1)
        login_info = d(text="登录").info
        print(f"  登录按钮: clickable={login_info.get('clickable')}")
        
        if login_info.get('clickable', False):
            print("  ✅ 成功！")
        else:
            # 方式3: 更左侧
            print("方式3: 点击更左侧...")
            d.click(200, 1754)
            time.sleep(1)
            login_info = d(text="登录").info
            print(f"  登录按钮: clickable={login_info.get('clickable')}")
            
            if login_info.get('clickable', False):
                print("  ✅ 成功！")
else:
    print(f"当前不在登录页面: {texts[:5]}")

d.screenshot(f"{SCREENSHOT_DIR}/after_agreement_test.png")
