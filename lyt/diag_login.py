"""诊断登录失败原因"""
import uiautomator2 as u2
import time
import re

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
SHOT_DIR = "E:/KiloAutoTest/lyt/explore_dual/screenshots"

# 清除app数据
import os
os.system(f"adb shell pm clear {PACKAGE}")
time.sleep(2)

# 启动app
d.app_start(PACKAGE, stop=False)
time.sleep(4)
d.screenshot(f"{SHOT_DIR}/diag_01_launch.png")

# 点击同意
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for t, x1, y1, x2, y2 in texts:
    if t == "同意":
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"点击同意 @({cx},{cy})")
        d.click(cx, cy)
        break
time.sleep(2)
d.screenshot(f"{SHOT_DIR}/diag_02_after_agree.png")

# 点击开始使用
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
for t, x1, y1, x2, y2 in texts:
    if "开始使用" in t:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"点击开始使用 @({cx},{cy})")
        d.click(cx, cy)
        break
time.sleep(2)
d.screenshot(f"{SHOT_DIR}/diag_03_after_guide.png")

# 打印当前页面所有文本
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print("\n登录页面元素:")
for t, x1, y1, x2, y2 in texts:
    if t.strip():
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"  [{t}] @({cx},{cy})")

# 点击短信验证码登录
for t, x1, y1, x2, y2 in texts:
    if "短信验证码" in t:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"\n点击短信验证码登录 @({cx},{cy})")
        d.click(cx, cy)
        break
time.sleep(2)
d.screenshot(f"{SHOT_DIR}/diag_04_sms_login.png")

# 输入手机号
el = d(className="android.widget.EditText")
if el.exists(timeout=2):
    el.click()
    time.sleep(0.5)
    d.clear_text()
    time.sleep(0.3)
    el.set_text("17472686748")
    time.sleep(1)
    print(f"\n手机号输入: {el.get_text()}")
d.screenshot(f"{SHOT_DIR}/diag_05_phone.png")

# 勾选协议
d.click(261, 1754)
time.sleep(0.5)
d.screenshot(f"{SHOT_DIR}/diag_06_agreement.png")

# 打印协议状态
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print("\n协议勾选后页面:")
for t, x1, y1, x2, y2 in texts:
    if t.strip() and ("协议" in t or "同意" in t or "登录" in t or "验证码" in t or "获取" in t):
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"  [{t}] @({cx},{cy})")

# 查找checkbox状态
checkboxes = re.findall(r'checkable="true"[^>]*checked="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print(f"\nCheckbox状态: {checkboxes}")

# 点击获取验证码
for t, x1, y1, x2, y2 in texts:
    if "获取验证码" in t or ("获取" in t and int(y1) > 1000):
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"\n点击获取验证码 @({cx},{cy})")
        d.click(cx, cy)
        break
time.sleep(3)
d.screenshot(f"{SHOT_DIR}/diag_07_after_getcode.png")

# 打印获取验证码后的页面
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print("\n获取验证码后:")
for t, x1, y1, x2, y2 in texts:
    if t.strip():
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"  [{t}] @({cx},{cy})")

# 输入验证码
edit_texts = d(className="android.widget.EditText")
count = edit_texts.count
print(f"\n找到{count}个输入框")
if count >= 2:
    edit_texts[1].click()
    time.sleep(0.3)
    d.clear_text()
    edit_texts[1].set_text("000000")
elif count == 1:
    edit_texts[0].click()
    time.sleep(0.3)
    d.clear_text()
    edit_texts[0].set_text("000000")
time.sleep(1)
d.screenshot(f"{SHOT_DIR}/diag_08_code_entered.png")

# 打印输入验证码后页面
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print("\n验证码输入后:")
for t, x1, y1, x2, y2 in texts:
    if t.strip():
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"  [{t}] @({cx},{cy})")

# 找到登录按钮
login_btn = None
for t, x1, y1, x2, y2 in texts:
    if t == "登录" and int(y1) > 1300:
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        login_btn = (cx, cy, int(x1), int(y1), int(x2), int(y2))
        print(f"\n登录按钮: [{t}] @({cx},{cy}) bounds=[{x1},{y1}][{x2},{y2}]")
        break

if login_btn:
    d.click(login_btn[0], login_btn[1])
else:
    print("\n未找到登录按钮，使用默认坐标")
    d.click(332, 1437)

time.sleep(8)
d.screenshot(f"{SHOT_DIR}/diag_09_after_login.png")

# 打印登录后页面
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
print("\n登录点击后:")
for t, x1, y1, x2, y2 in texts:
    if t.strip():
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"  [{t}] @({cx},{cy})")

# 检查是否有错误提示
for t, x1, y1, x2, y2 in texts:
    if any(k in t for k in ["错误", "失败", "无效", "过期", "不正确", "请"]):
        cx, cy = (int(x1)+int(x2))//2, (int(y1)+int(y2))//2
        print(f"\n⚠️ 错误提示: [{t}] @({cx},{cy})")

print(f"\n当前App: {d.app_current().get('package','')}")
print("诊断完成!")
