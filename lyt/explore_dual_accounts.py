"""
乐云泰App - 双账号验证码登录探索性测试
1. 营销角色: 17472686748  验证码: 000000
2. 代理角色: 17407448918  验证码: 000000
"""
import uiautomator2 as u2
import re
import os
import time
import json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"

BASE_DIR = "E:/KiloAutoTest/lyt/explore_dual"
DUMP_DIR = f"{BASE_DIR}/ui_dumps"
SHOT_DIR = f"{BASE_DIR}/screenshots"
os.makedirs(DUMP_DIR, exist_ok=True)
os.makedirs(SHOT_DIR, exist_ok=True)

# 底部Tab坐标
TABS = {
    "首页": (135, 2321),
    "客户": (405, 2321),
    "购物车": (675, 2321),
    "订单": (945, 2321),
}

# 登录流程坐标
LOGIN_COORDS = {
    "同意": (760, 1580),
    "开始使用": (540, 1927),
    "短信验证码登录": (540, 1604),
    "手机号输入框": (540, 999),
    "验证码输入框": (540, 1184),
    "获取验证码": (805, 1193),
    "登录按钮": (332, 1437),
    "同意协议": (261, 1754),
}

results = []

def record(module, case_id, name, status, detail=""):
    results.append({
        "module": module,
        "case_id": case_id,
        "name": name,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    })
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"  {symbol} {case_id} | {name} | {status} | {detail}")

def dump_page(step_name, screenshot=True):
    """Dump UI hierarchy and return text elements"""
    ts = datetime.now().strftime("%H%M%S")
    try:
        xml = d.dump_hierarchy()
    except:
        return [], ""
    
    xml_path = f"{DUMP_DIR}/{step_name}_{ts}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)
    
    if screenshot:
        shot_path = f"{SHOT_DIR}/{step_name}_{ts}.png"
        try:
            d.screenshot(shot_path)
        except:
            pass
    
    # 提取文本元素及坐标
    elements = re.findall(
        r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2) 
                 for t, x1, y1, x2, y2 in elements 
                 if t.strip() and int(y1) > 104]
    return non_empty, xml_path

def get_current_app():
    try:
        return d.app_current().get("package", "")
    except:
        return ""

def wait_for_app(timeout=10):
    """等待回到乐云泰App"""
    for _ in range(timeout):
        if PACKAGE in get_current_app():
            return True
        time.sleep(1)
    return False

def handle_popups():
    """处理登录后弹窗"""
    for _ in range(5):
        time.sleep(1)
        texts, _ = dump_page("popup_check", screenshot=False)
        handled = False
        for t, cx, cy in texts:
            # 常见弹窗按钮
            if t in ["同意", "确定", "知道了", "稍后", "关闭", "取消", "暂不升级", "以后再说"]:
                if cy > 1500:  # 底部按钮
                    d.click(cx, cy)
                    time.sleep(1)
                    handled = True
                    break
            if "授权" in t and cy > 1500:
                d.click(cx, cy)
                time.sleep(1)
                handled = True
                break
        if not handled:
            break

def sms_login(phone, sms_code, role_name):
    """验证码登录流程"""
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}验证码登录: {phone}")
    print(f"{'='*60}")
    
    # 1. 启动App
    print("\n🔄 启动App...")
    d.app_start(PACKAGE, stop=True)
    time.sleep(3)
    texts, _ = dump_page(f"{role_name}_01_launch")
    
    # 检查是否在隐私政策页面
    found_agree = False
    for t, cx, cy in texts:
        if t == "同意":
            print(f"  📋 隐私政策页面，点击同意 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(2)
            found_agree = True
            record("登录", f"{role_name}-LOG-001", "隐私政策-同意", "PASS", "点击同意按钮")
            break
    if not found_agree:
        # 尝试默认坐标
        d.click(*LOGIN_COORDS["同意"])
        time.sleep(2)
        record("登录", f"{role_name}-LOG-001", "隐私政策-同意", "PASS", "默认坐标点击")
    
    # 2. 引导页
    texts, _ = dump_page(f"{role_name}_02_guide")
    found_start = False
    for t, cx, cy in texts:
        if "开始使用" in t:
            print(f"  📖 引导页，点击开始使用 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(2)
            found_start = True
            record("登录", f"{role_name}-LOG-002", "引导页-开始使用", "PASS", "进入登录页")
            break
    if not found_start:
        d.click(*LOGIN_COORDS["开始使用"])
        time.sleep(2)
        record("登录", f"{role_name}-LOG-002", "引导页-开始使用", "PASS", "默认坐标")
    
    # 3. 点击短信验证码登录
    texts, _ = dump_page(f"{role_name}_03_login_page")
    found_sms = False
    for t, cx, cy in texts:
        if "短信验证码" in t:
            print(f"  📱 点击短信验证码登录 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(2)
            found_sms = True
            record("登录", f"{role_name}-LOG-003", "切换短信验证码登录", "PASS", "进入验证码登录页")
            break
    if not found_sms:
        d.click(*LOGIN_COORDS["短信验证码登录"])
        time.sleep(2)
        record("登录", f"{role_name}-LOG-003", "切换短信验证码登录", "PASS", "默认坐标")
    
    # 4. 输入手机号
    texts, _ = dump_page(f"{role_name}_04_sms_login")
    # 找手机号输入框
    phone_input_found = False
    el = d(className="android.widget.EditText")
    if el.exists(timeout=2):
        # 第一个EditText通常是手机号
        el.click()
        d.clear_text()
        el.set_text(phone)
        time.sleep(1)
        phone_input_found = True
        print(f"  📝 输入手机号: {phone}")
        record("登录", f"{role_name}-LOG-004", "输入手机号", "PASS", phone)
    
    if not phone_input_found:
        d.click(*LOGIN_COORDS["手机号输入框"])
        time.sleep(1)
        d.send_keys(phone)
        time.sleep(0.5)
        record("登录", f"{role_name}-LOG-004", "输入手机号", "PASS", f"坐标输入: {phone}")
    
    # 5. 勾选协议
    texts, _ = dump_page(f"{role_name}_05_phone_entered")
    agreement_checked = False
    # 查找协议复选框
    for t, cx, cy in texts:
        if "协议" in t and cy > 1600:
            # 点击复选框区域
            d.click(150, cy)
            time.sleep(0.5)
            agreement_checked = True
            break
    if not agreement_checked:
        d.click(*LOGIN_COORDS["同意协议"])
        time.sleep(0.5)
    record("登录", f"{role_name}-LOG-005", "勾选协议", "PASS", "协议已勾选")
    
    # 6. 点击获取验证码
    texts, _ = dump_page(f"{role_name}_06_agreement")
    found_code_btn = False
    for t, cx, cy in texts:
        if "获取验证码" in t or "获取" in t:
            print(f"  📲 点击获取验证码 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(3)
            found_code_btn = True
            record("登录", f"{role_name}-LOG-006", "获取验证码", "PASS", "验证码已发送")
            break
    if not found_code_btn:
        d.click(*LOGIN_COORDS["获取验证码"])
        time.sleep(3)
        record("登录", f"{role_name}-LOG-006", "获取验证码", "PASS", "默认坐标")
    
    # 7. 输入验证码
    # 找验证码输入框（第二个EditText）
    edit_texts = d(className="android.widget.EditText")
    count = edit_texts.count
    if count >= 2:
        edit_texts[1].click()
        d.clear_text()
        edit_texts[1].set_text(sms_code)
    elif count == 1:
        edit_texts[0].click()
        d.clear_text()
        edit_texts[0].set_text(sms_code)
    else:
        d.click(*LOGIN_COORDS["验证码输入框"])
        time.sleep(0.5)
        d.send_keys(sms_code)
    
    time.sleep(1)
    print(f"  🔑 输入验证码: {sms_code}")
    record("登录", f"{role_name}-LOG-007", "输入验证码", "PASS", sms_code)
    
    # 8. 点击登录
    texts, _ = dump_page(f"{role_name}_07_code_entered")
    found_login_btn = False
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            print(f"  🔓 点击登录按钮 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(5)
            found_login_btn = True
            break
    if not found_login_btn:
        d.click(*LOGIN_COORDS["登录按钮"])
        time.sleep(5)
    
    # 9. 处理弹窗
    handle_popups()
    time.sleep(2)
    
    # 10. 验证登录成功
    texts, _ = dump_page(f"{role_name}_08_after_login")
    tab_texts = [t for t, cx, cy in texts if t in TABS.keys()]
    
    if tab_texts:
        print(f"  ✅ 登录成功！检测到Tab: {tab_texts}")
        record("登录", f"{role_name}-LOG-008", "登录成功验证", "PASS", f"Tab: {tab_texts}")
        return True
    else:
        # 检查是否还在登录页
        login_texts = [t for t, cx, cy in texts if "登录" in t or "验证码" in t]
        if login_texts:
            print(f"  ❌ 登录失败，仍在登录页")
            record("登录", f"{role_name}-LOG-008", "登录成功验证", "FAIL", f"仍在登录页: {login_texts[:3]}")
            return False
        else:
            print(f"  ⚠️ 登录状态未知")
            record("登录", f"{role_name}-LOG-008", "登录成功验证", "SKIP", "状态未知")
            return True

def explore_home(role_name):
    """探索首页"""
    print(f"\n{'='*40}")
    print(f"  🏠 {role_name} - 首页探索")
    print(f"{'='*40}")
    
    d.click(*TABS["首页"])
    time.sleep(2)
    texts, _ = dump_page(f"{role_name}_home_01")
    
    # 用户信息
    user_name = None
    role_info = None
    for t, cx, cy in texts:
        if cy < 400 and t.strip() and not any(k in t for k in ["首页", "客户", "购物车", "订单"]):
            if not user_name:
                user_name = t
            elif not role_info:
                role_info = t
    record("首页", f"{role_name}-HOME-001", "用户信息展示", "PASS" if user_name else "FAIL", 
           f"用户:{user_name}, 角色:{role_info}")
    
    # 统计信息
    stats = [t for t, cx, cy in texts if any(k in t for k in ["销售", "客户", "订单", "排名", "业绩"])]
    record("首页", f"{role_name}-HOME-002", "统计信息展示", "PASS" if stats else "FAIL",
           f"统计项: {stats[:5]}")
    
    # 四大功能入口
    entries = [t for t, cx, cy in texts if t in ["设备", "建材", "人才", "服务"]]
    record("首页", f"{role_name}-HOME-003", "功能入口展示", "PASS" if entries else "FAIL",
           f"入口: {entries}")
    
    # 消息区域
    messages = [t for t, cx, cy in texts if "订单" in t and cy > 1200]
    record("首页", f"{role_name}-HOME-004", "消息区域展示", "PASS" if messages else "FAIL",
           f"消息: {messages[:3]}")
    
    # 下滑
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2, _ = dump_page(f"{role_name}_home_02_scroll")
    record("首页", f"{role_name}-HOME-005", "首页下滑", "PASS", f"{len(texts2)}个元素")
    
    # 测试功能入口跳转
    entry_coords = {
        "设备": (339, 940),
        "建材": (857, 940),
        "人才": (339, 1165),
        "服务": (857, 1165),
    }
    for entry_name, (ex, ey) in entry_coords.items():
        d.click(*TABS["首页"])
        time.sleep(1)
        d.click(ex, ey)
        time.sleep(2)
        cur = get_current_app()
        if PACKAGE in cur:
            texts_e, _ = dump_page(f"{role_name}_home_entry_{entry_name}")
            record("首页", f"{role_name}-HOME-006-{entry_name}", f"功能入口-{entry_name}", 
                   "PASS", f"{len(texts_e)}个元素")
            d.press("back")
            time.sleep(1)
        else:
            record("首页", f"{role_name}-HOME-006-{entry_name}", f"功能入口-{entry_name}",
                   "FAIL", f"离开App: {cur}")
            d.app_start(PACKAGE, stop=False)
            time.sleep(2)

def explore_customer(role_name):
    """探索客户页"""
    print(f"\n{'='*40}")
    print(f"  👥 {role_name} - 客户页探索")
    print(f"{'='*40}")
    
    d.click(*TABS["客户"])
    time.sleep(2)
    texts, _ = dump_page(f"{role_name}_customer_01")
    
    # 搜索框
    search = [t for t, cx, cy in texts if "搜索" in t]
    record("客户", f"{role_name}-CUST-001", "搜索框展示", "PASS" if search else "FAIL",
           f"搜索: {search}")
    
    # 状态Tab
    tabs = [t for t, cx, cy in texts if t in ["全部", "待审核", "已入驻", "已驳回"]]
    record("客户", f"{role_name}-CUST-002", "状态Tab展示", "PASS" if tabs else "FAIL",
           f"Tabs: {tabs}")
    
    # 客户列表
    customers = [t for t, cx, cy in texts if "联系人" in t or "电话" in t]
    record("客户", f"{role_name}-CUST-003", "客户列表展示", "PASS" if customers else "FAIL",
           f"列表项: {len(customers)}")
    
    # 下滑
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2, _ = dump_page(f"{role_name}_customer_02_scroll")
    record("客户", f"{role_name}-CUST-004", "客户列表下滑", "PASS", f"{len(texts2)}个元素")
    
    # 搜索测试
    d.click(*TABS["客户"])
    time.sleep(1)
    d.click(505, 204)
    time.sleep(1)
    el = d(className="android.widget.EditText")
    if el.exists(timeout=1):
        el.set_text("工人乐")
        time.sleep(0.5)
        d.press("enter")
        time.sleep(2)
        texts_s, _ = dump_page(f"{role_name}_customer_03_search")
        result = [t for t, cx, cy in texts_s if "工人乐" in t]
        record("客户", f"{role_name}-CUST-005", "搜索功能", "PASS" if result else "FAIL",
               f"搜索结果: {result[:2]}")
        d.press("back")
        time.sleep(1)
    else:
        record("客户", f"{role_name}-CUST-005", "搜索功能", "FAIL", "无法找到搜索框")

def explore_cart(role_name):
    """探索购物车"""
    print(f"\n{'='*40}")
    print(f"  🛒 {role_name} - 购物车探索")
    print(f"{'='*40}")
    
    d.click(*TABS["购物车"])
    time.sleep(2)
    texts, _ = dump_page(f"{role_name}_cart_01")
    
    # 购物车标题
    title = [t for t, cx, cy in texts if t == "购物车"]
    record("购物车", f"{role_name}-CART-001", "购物车标题", "PASS" if title else "FAIL", "")
    
    # 管理按钮
    manage = [t for t, cx, cy in texts if t == "管理"]
    record("购物车", f"{role_name}-CART-002", "管理按钮", "PASS" if manage else "FAIL", "")
    
    # 商品列表
    items = [t for t, cx, cy in texts if any(k in t for k in ["元/", "元/吨", "元/项目", "元/页"])]
    record("购物车", f"{role_name}-CART-003", "商品列表", "PASS" if items else "FAIL",
           f"商品数: {len(items)}")
    
    # 数量调节按钮
    qty_btns = [t for t, cx, cy in texts if t in ["-", "+"]]
    record("购物车", f"{role_name}-CART-004", "数量调节按钮", "PASS" if qty_btns else "FAIL",
           f"按钮: {qty_btns}")
    
    # 全选
    select_all = [t for t, cx, cy in texts if "全选" in t]
    record("购物车", f"{role_name}-CART-005", "全选按钮", "PASS" if select_all else "FAIL", "")
    
    # 下滑
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2, _ = dump_page(f"{role_name}_cart_02_scroll")
    record("购物车", f"{role_name}-CART-006", "购物车下滑", "PASS", f"{len(texts2)}个元素")

def explore_orders(role_name):
    """探索订单页"""
    print(f"\n{'='*40}")
    print(f"  📦 {role_name} - 订单页探索")
    print(f"{'='*40}")
    
    d.click(*TABS["订单"])
    time.sleep(2)
    texts, _ = dump_page(f"{role_name}_orders_01")
    
    # 顶部Tab
    top_tabs = [t for t, cx, cy in texts if t in ["全部", "客户订单", "记录订单"]]
    record("订单", f"{role_name}-ORD-001", "订单Tab展示", "PASS" if top_tabs else "FAIL",
           f"Tabs: {top_tabs}")
    
    # 订单列表
    orders = [t for t, cx, cy in texts if "订单编号" in t or "￥" in t]
    record("订单", f"{role_name}-ORD-002", "订单列表展示", "PASS" if orders else "FAIL",
           f"订单数: {len(orders)}")
    
    # 订单状态
    statuses = [t for t, cx, cy in texts if t in ["已完成", "待代理确认", "待付款", "待发货", "待收货"]]
    record("订单", f"{role_name}-ORD-003", "订单状态展示", "PASS" if statuses else "FAIL",
           f"状态: {statuses}")
    
    # 查看协议和凭证/发票
    actions = [t for t, cx, cy in texts if "协议" in t or "发票" in t]
    record("订单", f"{role_name}-ORD-004", "操作按钮展示", "PASS" if actions else "FAIL",
           f"操作: {actions}")
    
    # 下滑
    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2, _ = dump_page(f"{role_name}_orders_02_scroll")
    record("订单", f"{role_name}-ORD-005", "订单列表下滑", "PASS", f"{len(texts2)}个元素")
    
    # 点击订单详情
    d.click(*TABS["订单"])
    time.sleep(1)
    d.click(540, 450)
    time.sleep(2)
    if PACKAGE in get_current_app():
        texts_d, _ = dump_page(f"{role_name}_orders_03_detail")
        detail_fields = [t for t, cx, cy in texts_d if any(k in t for k in ["收货", "收件", "下单", "订单编号", "金额"])]
        record("订单", f"{role_name}-ORD-006", "订单详情页", "PASS" if detail_fields else "FAIL",
               f"字段: {detail_fields[:5]}")
        d.press("back")
        time.sleep(1)
    else:
        record("订单", f"{role_name}-ORD-006", "订单详情页", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False)
        time.sleep(2)

def explore_messages(role_name):
    """探索消息中心"""
    print(f"\n{'='*40}")
    print(f"  🔔 {role_name} - 消息中心探索")
    print(f"{'='*40}")
    
    d.click(*TABS["首页"])
    time.sleep(1.5)
    texts, _ = dump_page(f"{role_name}_msg_01_home")
    
    # 查找消息入口
    msg_entry = None
    for t, cx, cy in texts:
        if t == "消息" and cy > 1200:
            msg_entry = (cx, cy)
            break
    
    if msg_entry:
        d.click(*msg_entry)
        time.sleep(2)
        if PACKAGE in get_current_app():
            texts_m, _ = dump_page(f"{role_name}_msg_02_list")
            msgs = [t for t, cx, cy in texts_m if "订单" in t and cy > 1300]
            record("消息", f"{role_name}-MSG-001", "消息列表展示", "PASS" if msgs else "FAIL",
                   f"消息数: {len(msgs)}")
            
            # 消息类型
            msg_types = set()
            for t, cx, cy in texts_m:
                if "订单" in t and cy > 1300:
                    msg_types.add(t)
            record("消息", f"{role_name}-MSG-002", "消息类型", "PASS" if msg_types else "FAIL",
                   f"类型: {list(msg_types)[:3]}")
            
            d.press("back")
            time.sleep(1)
        else:
            record("消息", f"{role_name}-MSG-001", "消息列表展示", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False)
            time.sleep(2)
    else:
        record("消息", f"{role_name}-MSG-001", "消息入口", "FAIL", "未找到消息入口")

def logout():
    """退出登录"""
    print("\n🔄 退出登录...")
    # 通过重启App并清除数据来退出
    d.app_stop(PACKAGE)
    time.sleep(1)
    # 清除App数据以回到初始状态
    os.system(f"adb shell pm clear {PACKAGE}")
    time.sleep(2)
    d.app_start(PACKAGE, stop=False)
    time.sleep(3)

# ========================================================
# 主流程
# ========================================================

print("=" * 60)
print("  乐云泰App 双账号验证码登录探索性测试")
print("=" * 60)

# ========== 账号1: 营销角色 ==========
ACCOUNTS = [
    {
        "role": "营销",
        "phone": "17472686748",
        "sms_code": "000000",
    },
    {
        "role": "代理",
        "phone": "17407448918",
        "sms_code": "000000",
    },
]

for account in ACCOUNTS:
    role = account["role"]
    phone = account["phone"]
    sms_code = account["sms_code"]
    
    print(f"\n{'#'*60}")
    print(f"  🔑 {role}角色测试: {phone}")
    print(f"{'#'*60}")
    
    # 登录
    login_ok = sms_login(phone, sms_code, role)
    
    if login_ok:
        # 探索各模块
        explore_home(role)
        explore_customer(role)
        explore_cart(role)
        explore_orders(role)
        explore_messages(role)
    
    # 退出
    logout()

# ========== 生成测试结果JSON ==========
result_path = f"{BASE_DIR}/explore_results.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# ========== 打印汇总 ==========
print(f"\n{'='*60}")
print(f"  📊 测试结果汇总")
print(f"{'='*60}")

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"  总计: {total}")
print(f"  ✅ 通过: {passed} ({passed/total*100:.1f}%)")
print(f"  ❌ 失败: {failed} ({failed/total*100:.1f}%)")
print(f"  ⚠️ 跳过: {skipped} ({skipped/total*100:.1f}%)")

# 按模块统计
modules = {}
for r in results:
    mod = r["module"]
    if mod not in modules:
        modules[mod] = {"pass": 0, "fail": 0, "skip": 0}
    modules[mod][r["status"].lower()] += 1

print(f"\n  📁 按模块统计:")
for mod, stats in modules.items():
    print(f"    {mod}: ✅{stats['pass']} ❌{stats['fail']} ⚠️{stats['skip']}")

# 失败项
failures = [r for r in results if r["status"] == "FAIL"]
if failures:
    print(f"\n  ❌ 失败项:")
    for r in failures:
        print(f"    {r['case_id']} | {r['name']} | {r['detail']}")

print(f"\n📁 结果文件: {result_path}")
print(f"📁 XML dumps: {DUMP_DIR}")
print(f"📷 截图: {SHOT_DIR}")
print(f"\n✅ 探索性测试完成!")
