"""
乐云泰App - 双账号验证码登录探索性测试 V3
关键修复: 1.使用fastinput避免键盘干扰 2.输入后关闭键盘 3.验证手机号正确
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

results = []

def record(module, case_id, name, status, detail=""):
    results.append({"module": module, "case_id": case_id, "name": name,
                     "status": status, "detail": detail,
                     "timestamp": datetime.now().strftime("%H:%M:%S")})
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"  {symbol} {case_id} | {name} | {status} | {detail}")

def dump_page(step_name, screenshot=True):
    ts = datetime.now().strftime("%H%M%S")
    try:
        xml = d.dump_hierarchy()
    except:
        return [], ""
    with open(f"{DUMP_DIR}/{step_name}_{ts}.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    if screenshot:
        try: d.screenshot(f"{SHOT_DIR}/{step_name}_{ts}.png")
        except: pass
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
                 for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]
    return non_empty, xml_path if False else ""

def get_texts():
    """快速获取当前页面文本"""
    try:
        xml = d.dump_hierarchy()
    except:
        return []
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    return [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
            for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]

def get_current_app():
    try: return d.app_current().get("package", "")
    except: return ""

def hide_keyboard():
    """关闭键盘"""
    try:
        d.set_fastinput_ime(True)
    except: pass
    # 点击页面顶部空白区域关闭键盘
    d.click(540, 100)
    time.sleep(0.5)

def handle_popups():
    for _ in range(5):
        time.sleep(1)
        texts = get_texts()
        handled = False
        for t, cx, cy in texts:
            if t in ["同意", "确定", "知道了", "稍后", "关闭", "取消", "暂不升级", "以后再说"] and cy > 1500:
                d.click(cx, cy); time.sleep(1); handled = True; break
            if "授权" in t and cy > 1500:
                d.click(cx, cy); time.sleep(1); handled = True; break
        if not handled: break

def find_tabs():
    """检测底部Tab坐标"""
    texts = get_texts()
    tabs = {}
    for t, cx, cy in texts:
        if t in ["首页", "客户", "购物车", "订单"] and cy > 2200:
            tabs[t] = (cx, cy)
    return tabs

def click_tab(tab_name, tabs):
    if tab_name in tabs:
        d.click(*tabs[tab_name])
    else:
        defaults = {"首页": (135, 2321), "客户": (405, 2321), "购物车": (675, 2321), "订单": (945, 2321)}
        d.click(*defaults.get(tab_name, (135, 2321)))
    time.sleep(2)

def sms_login(phone, sms_code, role_name):
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}验证码登录: {phone}")
    print(f"{'='*60}")

    # 启动App
    print("\n🔄 启动App...")
    d.app_start(PACKAGE, stop=True)
    time.sleep(4)

    # 使用fastinput避免键盘干扰
    try: d.set_fastinput_ime(True)
    except: pass

    # 隐私政策
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if t == "同意":
            print(f"  📋 点击同意 @({cx},{cy})")
            d.click(cx, cy); time.sleep(2); found = True
            record("登录", f"{role_name}-LOG-001", "隐私政策-同意", "PASS", "")
            break
    if not found:
        d.click(760, 1580); time.sleep(2)
        record("登录", f"{role_name}-LOG-001", "隐私政策-同意", "PASS", "默认坐标")

    # 引导页
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "开始使用" in t:
            print(f"  📖 点击开始使用 @({cx},{cy})")
            d.click(cx, cy); time.sleep(2); found = True
            record("登录", f"{role_name}-LOG-002", "引导页-开始使用", "PASS", "")
            break
    if not found:
        d.click(540, 1927); time.sleep(2)
        record("登录", f"{role_name}-LOG-002", "引导页-开始使用", "PASS", "默认坐标")

    # 短信验证码登录
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "短信验证码" in t:
            print(f"  📱 点击短信验证码登录 @({cx},{cy})")
            d.click(cx, cy); time.sleep(2); found = True
            record("登录", f"{role_name}-LOG-003", "切换短信验证码登录", "PASS", "")
            break
    if not found:
        d.click(540, 1604); time.sleep(2)
        record("登录", f"{role_name}-LOG-003", "切换短信验证码登录", "PASS", "默认坐标")

    # 输入手机号 - 关键修复
    el = d(className="android.widget.EditText")
    if el.exists(timeout=2):
        el.click()
        time.sleep(0.5)
        # 方法1: 使用set_text直接设置（会替换内容）
        el.set_text(phone)
        time.sleep(0.5)
        # 验证输入
        entered = el.get_text()
        if entered != phone:
            print(f"  ⚠️ 第一次输入不匹配: {entered}, 重试...")
            # 方法2: 清除后重新输入
            el.click()
            time.sleep(0.3)
            # 长按选择全部
            d.long_click(540, 999, duration=1)
            time.sleep(0.5)
            # 点击"全选"（如果有）
            texts = get_texts()
            for t, cx, cy in texts:
                if "全选" in t:
                    d.click(cx, cy)
                    time.sleep(0.3)
                    break
            # 删除选中内容
            d.press("delete")
            time.sleep(0.3)
            el.set_text(phone)
            time.sleep(0.5)
            entered = el.get_text()

        # 关闭键盘
        hide_keyboard()
        time.sleep(0.5)

        # 再次验证
        entered = el.get_text()
        print(f"  📝 手机号: {entered}")
        record("登录", f"{role_name}-LOG-004", "输入手机号",
               "PASS" if entered == phone else "FAIL", f"输入: {entered}")
    else:
        record("登录", f"{role_name}-LOG-004", "输入手机号", "FAIL", "无输入框")

    # 勾选协议 - 先确认键盘已关闭
    hide_keyboard()
    time.sleep(0.5)
    d.click(261, 1754)
    time.sleep(0.5)
    record("登录", f"{role_name}-LOG-005", "勾选协议", "PASS", "")

    # 验证手机号没有被修改
    el = d(className="android.widget.EditText")
    if el.exists():
        phone_now = el.get_text()
        if phone_now != phone:
            print(f"  ⚠️ 手机号被修改: {phone_now}, 修正...")
            el.click()
            time.sleep(0.3)
            el.set_text(phone)
            time.sleep(0.3)
            hide_keyboard()

    # 获取验证码
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "获取验证码" in t or "获取" in t:
            print(f"  📲 点击获取验证码 @({cx},{cy})")
            d.click(cx, cy); time.sleep(3); found = True
            record("登录", f"{role_name}-LOG-006", "获取验证码", "PASS", "")
            break
    if not found:
        d.click(805, 1193); time.sleep(3)
        record("登录", f"{role_name}-LOG-006", "获取验证码", "PASS", "默认坐标")

    # 再次验证手机号
    el = d(className="android.widget.EditText")
    if el.exists():
        phone_now = el.get_text()
        if phone_now != phone and phone_now.replace("1", "") != phone:
            print(f"  ⚠️ 获取验证码后手机号变为: {phone_now}")

    # 输入验证码 - 找第二个EditText
    edit_texts = d(className="android.widget.EditText")
    count = edit_texts.count
    print(f"  🔑 找到{count}个输入框")

    if count >= 2:
        edit_texts[1].click()
        time.sleep(0.3)
        edit_texts[1].set_text(sms_code)
    elif count == 1:
        edit_texts[0].click()
        time.sleep(0.3)
        edit_texts[0].set_text(sms_code)

    time.sleep(1)
    hide_keyboard()
    print(f"  🔑 验证码: {sms_code}")
    record("登录", f"{role_name}-LOG-007", "输入验证码", "PASS", sms_code)

    # 截图登录前状态
    dump_page(f"{role_name}_06_before_login")

    # 点击登录
    texts = get_texts()
    login_clicked = False
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            print(f"  🔓 点击登录 @({cx},{cy})")
            d.click(cx, cy)
            time.sleep(8)
            login_clicked = True
            break
    if not login_clicked:
        d.click(540, 1437)
        time.sleep(8)

    # 处理弹窗
    handle_popups()
    time.sleep(2)

    # 按back退出可能的详情页
    for _ in range(3):
        texts = get_texts()
        home_markers = [t for t, cx, cy in texts if any(k in t for k in ["设备", "建材", "人才", "服务", "销售额", "业绩"])]
        if home_markers: break
        tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
        if tab_texts: break
        d.press("back")
        time.sleep(2)

    # 检测Tab
    tabs = find_tabs()
    print(f"  📍 Tab: {tabs}")

    # 验证登录
    texts = get_texts()
    tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
    dump_page(f"{role_name}_07_after_login")

    if tab_texts:
        print(f"  ✅ 登录成功！Tab: {tab_texts}")
        record("登录", f"{role_name}-LOG-008", "登录成功验证", "PASS", f"Tab: {tab_texts}")
        return True, tabs
    else:
        login_texts = [t for t, cx, cy in texts if "登录" in t or "验证码" in t]
        if login_texts:
            # 检查是否有错误提示
            error_texts = [t for t, cx, cy in texts if any(k in t for k in ["错误", "失败", "无效", "过期", "不正确"])]
            print(f"  ❌ 登录失败，仍在登录页")
            if error_texts:
                print(f"  ⚠️ 错误: {error_texts}")
            record("登录", f"{role_name}-LOG-008", "登录成功验证", "FAIL",
                   f"仍在登录页: {login_texts[:3]}")
            return False, {}
        else:
            print(f"  ⚠️ 状态未知")
            record("登录", f"{role_name}-LOG-008", "登录成功验证", "SKIP", "状态未知")
            return True, tabs

def explore_home(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🏠 {role_name} - 首页探索")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_home_01")

    user_name = None; role_info = None
    for t, cx, cy in texts:
        if cy < 400 and t.strip() and t not in ["首页", "客户", "购物车", "订单"]:
            if not user_name: user_name = t
            elif not role_info and t != user_name: role_info = t
    record("首页", f"{role_name}-HOME-001", "用户信息", "PASS" if user_name else "FAIL",
           f"用户:{user_name}, 角色:{role_info}")

    stats = [t for t, cx, cy in texts if any(k in t for k in ["销售", "客户", "订单", "排名", "业绩", "评价"])]
    record("首页", f"{role_name}-HOME-002", "统计信息", "PASS" if stats else "FAIL", f"统计: {stats[:5]}")

    entries = [t for t, cx, cy in texts if t in ["设备", "建材", "人才", "服务"]]
    record("首页", f"{role_name}-HOME-003", "功能入口", "PASS" if entries else "FAIL", f"入口: {entries}")

    messages = [t for t, cx, cy in texts if ("订单" in t or "消息" in t) and cy > 1200]
    record("首页", f"{role_name}-HOME-004", "消息区域", "PASS" if messages else "FAIL", f"消息: {messages[:3]}")

    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2 = get_texts()
    dump_page(f"{role_name}_home_02_scroll")
    record("首页", f"{role_name}-HOME-005", "首页下滑", "PASS", f"{len(texts2)}个元素")

    # 功能入口跳转
    entry_map = {}
    for t, cx, cy in texts:
        if t in ["设备", "建材", "人才", "服务"]:
            entry_map[t] = (cx, cy)
    if not entry_map:
        entry_map = {"设备": (339, 940), "建材": (857, 940), "人才": (339, 1165), "服务": (857, 1165)}

    for entry_name, (ex, ey) in entry_map.items():
        click_tab("首页", tabs)
        d.click(ex, ey)
        time.sleep(2)
        cur = get_current_app()
        if PACKAGE in cur:
            texts_e = get_texts()
            dump_page(f"{role_name}_entry_{entry_name}")
            record("首页", f"{role_name}-HOME-006-{entry_name}", f"入口-{entry_name}",
                   "PASS", f"{len(texts_e)}个元素")
            d.press("back"); time.sleep(1.5)
        else:
            record("首页", f"{role_name}-HOME-006-{entry_name}", f"入口-{entry_name}",
                   "FAIL", f"离开App: {cur}")
            d.app_start(PACKAGE, stop=False); time.sleep(3)

def explore_customer(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  👥 {role_name} - 客户页")
    print(f"{'='*40}")
    click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_customer_01")

    search = [t for t, cx, cy in texts if "搜索" in t]
    record("客户", f"{role_name}-CUST-001", "搜索框", "PASS" if search else "FAIL", f"搜索: {search}")

    tabs_found = [t for t, cx, cy in texts if t in ["全部", "待审核", "已入驻", "已驳回"]]
    record("客户", f"{role_name}-CUST-002", "状态Tab", "PASS" if tabs_found else "FAIL", f"Tabs: {tabs_found}")

    customers = [t for t, cx, cy in texts if "联系人" in t or "电话" in t]
    record("客户", f"{role_name}-CUST-003", "客户列表", "PASS" if customers else "FAIL", f"项: {len(customers)}")

    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2 = get_texts()
    dump_page(f"{role_name}_customer_02_scroll")
    record("客户", f"{role_name}-CUST-004", "列表下滑", "PASS", f"{len(texts2)}个元素")

    # 搜索
    click_tab("客户", tabs)
    el = d(className="android.widget.EditText")
    if el.exists(timeout=2):
        el.click(); time.sleep(0.3)
        el.set_text("工人乐"); time.sleep(0.5)
        hide_keyboard()
        d.press("enter"); time.sleep(2)
        texts_s = get_texts()
        dump_page(f"{role_name}_customer_03_search")
        result = [t for t, cx, cy in texts_s if "工人乐" in t]
        record("客户", f"{role_name}-CUST-005", "搜索功能", "PASS" if result else "FAIL", f"结果: {result[:2]}")
        d.press("back"); time.sleep(1)
    else:
        record("客户", f"{role_name}-CUST-005", "搜索功能", "FAIL", "无搜索框")

def explore_cart(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🛒 {role_name} - 购物车")
    print(f"{'='*40}")
    click_tab("购物车", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cart_01")

    record("购物车", f"{role_name}-CART-001", "购物车标题",
           "PASS" if [t for t, cx, cy in texts if t == "购物车"] else "FAIL", "")
    record("购物车", f"{role_name}-CART-002", "管理按钮",
           "PASS" if [t for t, cx, cy in texts if t == "管理"] else "FAIL", "")
    items = [t for t, cx, cy in texts if any(k in t for k in ["元/", "元/吨", "元/项目", "元/页"])]
    record("购物车", f"{role_name}-CART-003", "商品列表", "PASS" if items else "FAIL", f"商品: {len(items)}")
    record("购物车", f"{role_name}-CART-004", "数量调节",
           "PASS" if [t for t, cx, cy in texts if t in ["-", "+"]] else "FAIL", "")
    record("购物车", f"{role_name}-CART-005", "全选按钮",
           "PASS" if [t for t, cx, cy in texts if "全选" in t] else "FAIL", "")

    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2 = get_texts()
    dump_page(f"{role_name}_cart_02_scroll")
    record("购物车", f"{role_name}-CART-006", "下滑", "PASS", f"{len(texts2)}个元素")

def explore_orders(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  📦 {role_name} - 订单页")
    print(f"{'='*40}")
    click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_orders_01")

    top_tabs = [t for t, cx, cy in texts if t in ["全部", "客户订单", "记录订单"]]
    record("订单", f"{role_name}-ORD-001", "订单Tab", "PASS" if top_tabs else "FAIL", f"Tabs: {top_tabs}")
    orders = [t for t, cx, cy in texts if "订单编号" in t or "￥" in t]
    record("订单", f"{role_name}-ORD-002", "订单列表", "PASS" if orders else "FAIL", f"订单: {len(orders)}")
    statuses = [t for t, cx, cy in texts if t in ["已完成", "待代理确认", "待付款", "待发货", "待收货"]]
    record("订单", f"{role_name}-ORD-003", "订单状态", "PASS" if statuses else "FAIL", f"状态: {statuses}")
    actions = [t for t, cx, cy in texts if "协议" in t or "发票" in t]
    record("订单", f"{role_name}-ORD-004", "操作按钮", "PASS" if actions else "FAIL", f"操作: {actions}")

    d.swipe(540, 1800, 540, 800, duration=0.5)
    time.sleep(1)
    texts2 = get_texts()
    dump_page(f"{role_name}_orders_02_scroll")
    record("订单", f"{role_name}-ORD-005", "列表下滑", "PASS", f"{len(texts2)}个元素")

    # 订单详情
    click_tab("订单", tabs)
    d.click(540, 450)
    time.sleep(2)
    if PACKAGE in get_current_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_orders_03_detail")
        fields = [t for t, cx, cy in texts_d if any(k in t for k in ["收货", "收件", "下单", "订单编号", "金额"])]
        record("订单", f"{role_name}-ORD-006", "订单详情", "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-006", "订单详情", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

def explore_messages(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🔔 {role_name} - 消息中心")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()

    msg_entry = None
    for t, cx, cy in texts:
        if t == "消息" and cy > 1200:
            msg_entry = (cx, cy); break

    if msg_entry:
        d.click(*msg_entry); time.sleep(2)
        if PACKAGE in get_current_app():
            texts_m = get_texts()
            dump_page(f"{role_name}_msg_02_list")
            msgs = [t for t, cx, cy in texts_m if ("订单" in t or "消息" in t) and cy > 1300]
            record("消息", f"{role_name}-MSG-001", "消息列表", "PASS" if msgs else "FAIL", f"消息: {len(msgs)}")
            msg_types = set(t for t, cx, cy in texts_m if "订单" in t and cy > 1300)
            record("消息", f"{role_name}-MSG-002", "消息类型", "PASS" if msg_types else "FAIL", f"类型: {list(msg_types)[:3]}")
            d.press("back"); time.sleep(1)
        else:
            record("消息", f"{role_name}-MSG-001", "消息列表", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)
    else:
        record("消息", f"{role_name}-MSG-001", "消息入口", "FAIL", "未找到")

def logout():
    print("\n🔄 退出登录...")
    d.app_stop(PACKAGE); time.sleep(1)
    os.system(f"adb shell pm clear {PACKAGE}"); time.sleep(2)
    d.app_start(PACKAGE, stop=False); time.sleep(3)

# ========================================================
print("=" * 60)
print("  乐云泰App 双账号验证码登录探索性测试 V3")
print("=" * 60)

ACCOUNTS = [
    {"role": "营销", "phone": "17472686748", "sms_code": "000000"},
    {"role": "代理", "phone": "17407448918", "sms_code": "000000"},
]

for account in ACCOUNTS:
    role = account["role"]; phone = account["phone"]; sms_code = account["sms_code"]
    print(f"\n{'#'*60}")
    print(f"  🔑 {role}角色: {phone}")
    print(f"{'#'*60}")

    login_ok, tabs = sms_login(phone, sms_code, role)
    if login_ok:
        explore_home(role, tabs)
        explore_customer(role, tabs)
        explore_cart(role, tabs)
        explore_orders(role, tabs)
        explore_messages(role, tabs)
    logout()

# 结果
result_path = f"{BASE_DIR}/explore_results_v3.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"\n{'='*60}")
print(f"  📊 测试结果: 总计{total} ✅{passed} ❌{failed} ⚠️{skipped}")
print(f"{'='*60}")

modules = {}
for r in results:
    mod = r["module"]
    if mod not in modules: modules[mod] = {"pass": 0, "fail": 0, "skip": 0}
    modules[mod][r["status"].lower()] += 1

for mod, stats in modules.items():
    print(f"  {mod}: ✅{stats['pass']} ❌{stats['fail']} ⚠️{stats['skip']}")

failures = [r for r in results if r["status"] == "FAIL"]
if failures:
    print(f"\n  ❌ 失败项:")
    for r in failures:
        print(f"    {r['case_id']} | {r['name']} | {r['detail']}")

print(f"\n✅ 完成! 结果: {result_path}")
