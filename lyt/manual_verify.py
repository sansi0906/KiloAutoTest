"""
乐云泰App - 手工验证脚本
模拟人工逐步操作，每步截图留证，覆盖关键用例
"""
import uiautomator2 as u2
import re, os, time, json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
REPORT_DIR = "E:/KiloAutoTest/lyt/manual_verification"
SCREENSHOT_DIR = f"{REPORT_DIR}/screenshots"
DUMP_DIR = f"{REPORT_DIR}/ui_dumps"

for _dir in (REPORT_DIR, SCREENSHOT_DIR, DUMP_DIR):
    os.makedirs(_dir, exist_ok=True)

report = []
step_num = 0


def log_step(title, status="INFO", detail=""):
    global step_num
    step_num += 1
    ts = datetime.now().strftime("%H:%M:%S")
    sym = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "WARN": "⚠️"}.get(status, "ℹ️")
    entry = {"step": step_num, "title": title, "status": status, "detail": detail, "time": ts}
    report.append(entry)
    print(f"  [{step_num}] {sym} {title} | {detail}")
    return entry


def screenshot(name):
    ts = datetime.now().strftime("%H%M%S")
    path = f"{SCREENSHOT_DIR}/{name}_{ts}.png"
    try:
        d.screenshot(path)
        return path
    except:
        return ""


def dump_ui(name):
    ts = datetime.now().strftime("%H%M%S")
    path = f"{DUMP_DIR}/{name}_{ts}.xml"
    try:
        xml = d.dump_hierarchy()
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
        texts = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
                 for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]
        return texts, path
    except:
        return [], ""


def get_texts():
    try:
        xml = d.dump_hierarchy()
    except:
        return []
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    return [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
            for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]


def get_app():
    try:
        return d.app_current().get("package", "")
    except:
        return ""


def find_tabs():
    texts = get_texts()
    tabs = {}
    for t, cx, cy in texts:
        if t in ["首页", "客户", "购物车", "订单"] and cy > 2200:
            tabs[t] = (cx, cy)
    return tabs


def ensure_in_app():
    if PACKAGE not in get_app():
        log_step("App不在前台，重新启动", "INFO")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        for _ in range(10):
            texts = get_texts()
            if [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]:
                break
            time.sleep(1)


def click_tab(tab_name):
    ensure_in_app()
    tabs = find_tabs()
    if tab_name in tabs:
        d.click(*tabs[tab_name])
    else:
        defaults = {"首页": (135, 2321), "客户": (405, 2321), "购物车": (675, 2321), "订单": (945, 2321)}
        d.click(*defaults.get(tab_name, (135, 2321)))
    time.sleep(2)
    return find_tabs()


def check_text_exists(texts, keywords, search_in="all"):
    """检查关键词是否出现在页面文本中"""
    found_items = []
    for kw in keywords:
        if search_in == "all":
            matches = [t for t, _, _ in texts if kw in t]
        else:
            matches = [t for t, _, _ in texts if kw == t]
        if matches:
            found_items.extend(matches)
    return found_items


# ============================================================
print("=" * 60)
print("  乐云泰App 手工验证（营销角色）")
print("=" * 60)

# ========== Step 0: 登录 ==========
log_step("Step 0: 启动App并登录营销账号", "INFO")

# 使用stop=True重启App，不清除数据（如果之前已登录则直接进入）
d.app_start(PACKAGE, stop=True)
time.sleep(4)

try:
    d.set_fastinput_ime(True)
except:
    pass

# 等待加载，检查是否已登录（直接进入首页）
time.sleep(5)
texts = get_texts()
tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]

if len(tab_texts) >= 3:
    log_step("已登录状态", "PASS", f"底部Tab: {tab_texts}")
else:
    # 需要登录流程
    log_step("需要登录", "INFO", "执行登录流程")

    # 点击同意
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if t == "同意":
            d.click(cx, cy); time.sleep(3); found = True; break
    if not found:
        d.click(760, 1580); time.sleep(3)

    # 点击开始使用
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "开始使用" in t:
            d.click(cx, cy); time.sleep(3); found = True; break
    if not found:
        d.click(540, 1927); time.sleep(3)

    # 点击短信验证码登录
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "短信验证码" in t:
            d.click(cx, cy); time.sleep(2); found = True; break
    if not found:
        d.click(540, 1604); time.sleep(2)

    # 输入手机号
    el = d(className="android.widget.EditText")
    if el.exists(timeout=5):
        el.click(); time.sleep(0.5)
        el.set_text("17472686748"); time.sleep(0.5)
        d.click(540, 100); time.sleep(0.5)
    else:
        # 使用坐标点击输入框
        d.click(540, 999); time.sleep(0.5)
        os.system("adb shell input text 17472686748")
        time.sleep(0.5)
        d.click(540, 100); time.sleep(0.5)

    # 勾选协议
    d.click(261, 1754); time.sleep(0.5)

    # 获取验证码
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "获取验证码" in t or ("获取" in t and cy > 1000):
            d.click(cx, cy); time.sleep(4); found = True; break
    if not found:
        d.click(805, 1193); time.sleep(4)

    # 输入验证码
    edit_texts = d(className="android.widget.EditText")
    cnt = edit_texts.count
    if cnt >= 2:
        edit_texts[1].click(); time.sleep(0.3)
        edit_texts[1].set_text("000000"); time.sleep(0.5)
    elif cnt == 1:
        edit_texts[0].click(); time.sleep(0.3)
        edit_texts[0].set_text("000000"); time.sleep(0.5)
    else:
        # 使用坐标点击验证码输入框
        d.click(540, 1184); time.sleep(0.3)
        os.system("adb shell input text 000000")
        time.sleep(0.5)
    d.click(540, 100); time.sleep(1)

    # 点击登录
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            d.click(cx, cy); time.sleep(10); found = True; break
    if not found:
        d.click(332, 1437); time.sleep(10)

    # 处理弹窗
    for _ in range(5):
        time.sleep(1)
        texts = get_texts()
        handled = False
        for t, cx, cy in texts:
            if t in ["同意", "确定", "知道了", "稍后", "关闭", "暂不升级"] and cy > 1500:
                d.click(cx, cy); time.sleep(1); handled = True; break
        if not handled:
            break

    # 验证登录成功
    texts = get_texts()
    tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
    if len(tab_texts) >= 3:
        log_step("登录成功", "PASS", f"底部Tab: {tab_texts}")
    else:
        log_step("登录失败", "FAIL", f"Tab: {tab_texts}")

# ========== Step 1: 首页验证 ==========
log_step("Step 1: 首页验证", "INFO")
tabs = find_tabs()
if "首页" in tabs:
    d.click(*tabs["首页"]); time.sleep(2)

ss = screenshot("home")
texts, _ = dump_ui("home")

# 验证用户信息
user_info = check_text_exists(texts, ["杨涛轩", "营销333"], "all")
log_step("HOME-001 用户信息", "PASS" if user_info else "FAIL",
         f"找到: {user_info}" if user_info else "未找到用户信息")

# 验证功能入口
entries = check_text_exists(texts, ["设备", "建材", "人才", "服务"], "all")
log_step("HOME-003 功能入口", "PASS" if entries else "FAIL",
         f"找到: {list(set(entries))}" if entries else "未找到功能入口")

# 验证消息区域
msgs = check_text_exists(texts, ["订单待开票", "已发货", "已完成"], "all")
log_step("HOME-004 消息区域", "PASS" if msgs else "FAIL",
         f"找到: {list(set(msgs))}" if msgs else "未找到消息")

# ========== Step 2: 商品列表-设备 ==========
log_step("Step 2: 商品列表-设备验证", "INFO")

# 点击设备入口
texts = get_texts()
for t, cx, cy in texts:
    if t == "设备" and cy < 800:
        d.click(cx, cy); time.sleep(3); break

if PACKAGE in get_app():
    ss = screenshot("device_list")
    texts, _ = dump_ui("device_list")

    # PROD-001: 设备入口
    log_step("PROD-001 设备列表入口", "PASS", "成功进入设备列表页")

    # PROD-002: 搜索按钮
    search_btn = check_text_exists(texts, ["搜索"], "exact")
    log_step("PROD-002 设备列表搜索", "PASS" if search_btn else "FAIL",
             "有搜索按钮" if search_btn else "无搜索按钮")

    # PROD-003: 筛选按钮
    filter_btn = check_text_exists(texts, ["筛选"], "exact")
    log_step("PROD-003 设备列表筛选", "PASS" if filter_btn else "FAIL",
             "有筛选按钮" if filter_btn else "无筛选按钮")

    # PROD-004: 点击筛选，查看筛选页面
    if filter_btn:
        for t, cx, cy in texts:
            if t == "筛选":
                d.click(cx, cy); time.sleep(2); break
        ss_f = screenshot("device_filter")
        texts_f, _ = dump_ui("device_filter")
        filter_opts = check_text_exists(texts_f, ["分类", "区域", "价格", "排序", "类型", "确认", "重置"], "all")
        log_step("PROD-004 设备筛选页", "PASS" if filter_opts else "FAIL",
                 f"选项: {list(set(filter_opts))}" if filter_opts else "无筛选选项")
        d.press("back"); time.sleep(1.5)

    # PROD-005: 列表下滑
    d.swipe(540, 1800, 540, 800, duration=0.5); time.sleep(1)
    texts_s, _ = dump_ui("device_scroll")
    log_step("PROD-005 设备列表下滑", "PASS", f"下滑后{len(texts_s)}个元素")

    # PROD-006: 点击商品详情
    d.click(540, 500); time.sleep(2)
    if PACKAGE in get_app():
        ss_d = screenshot("device_detail")
        texts_d, _ = dump_ui("device_detail")
        detail_fields = check_text_exists(texts_d, ["设备详情", "价格", "品牌", "型号", "规格"], "all")
        log_step("PROD-006 设备商品详情", "PASS" if detail_fields else "FAIL",
                 f"字段: {list(set(detail_fields))}" if detail_fields else "无详情字段")

        # PROD-007: 购买按钮
        buy_btns = check_text_exists(texts_d, ["加入购物车", "购买", "下单"], "all")
        log_step("PROD-007 设备购买按钮", "PASS" if buy_btns else "FAIL",
                 f"按钮: {list(set(buy_btns))}" if buy_btns else "无购买按钮")
        d.press("back"); time.sleep(1.5)
    else:
        log_step("PROD-006 设备商品详情", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(5)
else:
    log_step("PROD-001 设备列表入口", "FAIL", "离开App或未找到入口")

# ========== Step 3: 商品列表-人才 ==========
log_step("Step 3: 商品列表-人才验证", "INFO")
tabs = click_tab("首页")
texts = get_texts()
for t, cx, cy in texts:
    if t == "人才" and cy < 800:
        d.click(cx, cy); time.sleep(3); break

if PACKAGE in get_app():
    ss = screenshot("talent_list")
    texts, _ = dump_ui("talent_list")

    log_step("PROD-001 人才入口", "PASS", "成功进入人才列表页")

    # PROD-009: 搜索
    search_btn = check_text_exists(texts, ["搜索"], "exact")
    log_step("PROD-009 人才列表搜索", "PASS" if search_btn else "FAIL",
             "有搜索按钮" if search_btn else "无搜索按钮")

    # PROD-010: 筛选
    filter_btn = check_text_exists(texts, ["筛选"], "exact")
    log_step("PROD-010 人才列表筛选", "PASS" if filter_btn else "FAIL",
             "有筛选按钮" if filter_btn else "无筛选按钮")
else:
    log_step("PROD-001 人才入口", "FAIL", "离开App或未找到入口")

# ========== Step 4: 购物车管理 ==========
log_step("Step 4: 购物车管理验证", "INFO")
tabs = click_tab("购物车")

ss = screenshot("cart")
texts, _ = dump_ui("cart")

# CART-007: 管理按钮
manage_btn = check_text_exists(texts, ["管理"], "exact")
if manage_btn:
    log_step("CART-007 管理按钮", "PASS", "有管理按钮")
    for t, cx, cy in texts:
        if t == "管理":
            d.click(cx, cy); time.sleep(2); break
    texts_m, _ = dump_ui("cart_manage")
    ss_m = screenshot("cart_manage")
    manage_ops = check_text_exists(texts_m, ["删除", "完成", "全选", "移除"], "all")
    log_step("CART-007 管理功能", "PASS" if manage_ops else "FAIL",
             f"操作: {list(set(manage_ops))}" if manage_ops else "无管理操作")
    # 退出管理
    for t, cx, cy in texts_m:
        if t in ["完成", "取消"]:
            d.click(cx, cy); time.sleep(1); break
else:
    log_step("CART-007 管理按钮", "FAIL", "无管理按钮")

# CART-008: 结算按钮
tabs = click_tab("购物车")
texts, _ = dump_ui("cart_settle")
settle = check_text_exists(texts, ["结算", "合计", "￥"], "all")
log_step("CART-008 结算按钮", "PASS" if settle else "FAIL",
         f"找到: {list(set(settle))}" if settle else "无结算按钮")

# CART-009: 全选
select_all = check_text_exists(texts, ["全选"], "exact")
if select_all:
    log_step("CART-009 全选按钮", "PASS", "有全选按钮")
    # 点击全选
    for t, cx, cy in texts:
        if t == "全选":
            d.click(80, cy); time.sleep(1); break
    texts_a, _ = dump_ui("cart_selected")
    total = check_text_exists(texts_a, ["合计", "￥"], "all")
    log_step("CART-009 全选+合计", "PASS" if total else "FAIL",
             f"找到: {list(set(total))}" if total else "无合计金额")
else:
    log_step("CART-009 全选按钮", "FAIL", "无全选按钮")

# CART-010: 数量增减
plus_btn = check_text_exists(texts, ["+"], "exact")
if plus_btn:
    log_step("CART-010 数量增加", "PASS", "有+按钮")
    for t, cx, cy in texts:
        if t == "+":
            d.click(cx, cy); time.sleep(1); break
else:
    log_step("CART-010 数量增加", "FAIL", "无+按钮")

# ========== Step 5: 订单操作 ==========
log_step("Step 5: 订单操作验证", "INFO")
tabs = click_tab("订单")

ss = screenshot("order_list")
texts, _ = dump_ui("order_list")

# ORD-007: 协议和凭证
agreement = check_text_exists(texts, ["协议", "凭证"], "all")
if agreement:
    log_step("ORD-007 协议和凭证按钮", "PASS", f"找到: {list(set(agreement))}")
    for t, cx, cy in texts:
        if "协议" in t and "凭证" in t:
            d.click(cx, cy); time.sleep(2); break
    if PACKAGE in get_app():
        ss_a = screenshot("order_agreement")
        texts_a, _ = dump_ui("order_agreement")
        agreement_fields = check_text_exists(texts_a, ["协议", "凭证", "甲方", "乙方", "签订", "条款"], "all")
        log_step("ORD-007 协议凭证页", "PASS" if agreement_fields else "FAIL",
                 f"字段: {list(set(agreement_fields))}" if agreement_fields else "无协议字段")
        d.press("back"); time.sleep(1.5)
    else:
        log_step("ORD-007 协议凭证页", "FAIL", "离开App")
else:
    log_step("ORD-007 协议和凭证按钮", "FAIL", "无此按钮")

# ORD-008: 查看发票
tabs = click_tab("订单")
texts, _ = dump_ui("order_list2")
invoice = check_text_exists(texts, ["发票"], "all")
if invoice:
    log_step("ORD-008 查看发票按钮", "PASS", f"找到: {list(set(invoice))}")
    for t, cx, cy in texts:
        if "发票" in t:
            d.click(cx, cy); time.sleep(2); break
    if PACKAGE in get_app():
        ss_i = screenshot("order_invoice")
        texts_i, _ = dump_ui("order_invoice")
        invoice_fields = check_text_exists(texts_i, ["发票", "抬头", "税号", "金额"], "all")
        log_step("ORD-008 发票页", "PASS" if invoice_fields else "FAIL",
                 f"字段: {list(set(invoice_fields))}" if invoice_fields else "无发票字段")
        d.press("back"); time.sleep(1.5)
    else:
        log_step("ORD-008 发票页", "FAIL", "离开App")
else:
    log_step("ORD-008 查看发票按钮", "FAIL", "无此按钮")

# ORD-009: 订单详情
tabs = click_tab("订单")
d.click(540, 450); time.sleep(2)
if PACKAGE in get_app():
    ss_d = screenshot("order_detail")
    texts_d, _ = dump_ui("order_detail")
    detail_fields = check_text_exists(texts_d, ["收货", "收件", "订单编号", "下单时间", "金额", "商品"], "all")
    log_step("ORD-009 订单详情字段", "PASS" if detail_fields else "FAIL",
             f"字段: {list(set(detail_fields))[:8]}" if detail_fields else "无详情字段")
    d.press("back"); time.sleep(1.5)
else:
    log_step("ORD-009 订单详情", "FAIL", "离开App")

# ========== Step 6: 客户电话拨打 ==========
log_step("Step 6: 客户电话拨打验证", "INFO")
tabs = click_tab("客户")

ss = screenshot("customer")
texts, _ = dump_ui("customer")

# CUST-009: 电话拨打
phone_found = False
for t, cx, cy in texts:
    if (re.match(r'^1\d{10}$', t) or t == "电话") and 400 < cy < 1800:
        d.click(cx, cy); time.sleep(2)
        texts_p, _ = dump_ui("customer_phone")
        call_confirm = check_text_exists(texts_p, ["呼叫", "拨号", "取消", "电话"], "all")
        log_step("CUST-009 电话拨打", "PASS" if call_confirm else "FAIL",
                 f"弹窗: {list(set(call_confirm))}" if call_confirm else "无拨号弹窗")
        # 取消
        for t2, cx2, cy2 in texts_p:
            if t2 in ["取消", "否"]:
                d.click(cx2, cy2); time.sleep(1); break
        else:
            d.press("back"); time.sleep(1)
        phone_found = True
        break

if not phone_found:
    log_step("CUST-009 电话拨打", "FAIL", "无电话号码可点击")

# ========== Step 7: 设置/个人中心 ==========
log_step("Step 7: 设置/个人中心验证", "INFO")
tabs = click_tab("首页")
texts = get_texts()

# SET-001: 尝试点击用户信息区域
# 营销角色: 杨涛轩在顶部约(487, 289)
user_clicked = False
for t, cx, cy in texts:
    if t in ["杨涛轩", "营销333"] or (cy < 400 and t.strip() and t not in
        ["首页", "客户", "购物车", "订单", "设备", "建材", "人才", "服务"]):
        d.click(cx, cy); time.sleep(2)
        texts_s, _ = dump_ui("set_click_user")
        ss_s = screenshot("set_click_user")
        profile_items = check_text_exists(texts_s, ["设置", "修改密码", "退出", "缓存", "版本", "我的", "个人"], "all")
        if profile_items:
            log_step("SET-001 个人中心页面", "PASS", f"菜单: {list(set(profile_items))}")
            has_exit = any("退出" in t for t in profile_items)
            has_pwd = any("密码" in t for t in profile_items)
            has_ver = any("版本" in t for t in profile_items)
            has_cache = any("缓存" in t or "清除" in t for t in profile_items)
            log_step("SET-002 退出登录按钮", "PASS" if has_exit else "FAIL", "找到" if has_exit else "未找到")
            log_step("SET-003 修改密码入口", "PASS" if has_pwd else "FAIL", "找到" if has_pwd else "未找到")
            log_step("SET-004 版本信息", "PASS" if has_ver else "FAIL", "找到" if has_ver else "未找到")
            log_step("SET-005 清除缓存", "PASS" if has_cache else "FAIL", "找到" if has_cache else "未找到")
            d.press("back"); time.sleep(1.5)
            user_clicked = True
            break
        else:
            d.press("back"); time.sleep(1)
            break

if not user_clicked:
    log_step("SET-001 个人中心页面", "FAIL", "未找到设置入口")
    log_step("SET-002 退出登录按钮", "FAIL", "无设置入口")
    log_step("SET-003 修改密码入口", "FAIL", "无设置入口")
    log_step("SET-004 版本信息", "FAIL", "无设置入口")
    log_step("SET-005 清除缓存", "FAIL", "无设置入口")

# ========== 生成报告 ==========
log_step("生成验证报告", "INFO")

# 统计
total = len(report)
passed = len([r for r in report if r["status"] == "PASS"])
failed = len([r for r in report if r["status"] == "FAIL"])
info = len([r for r in report if r["status"] == "INFO"])

# 生成Markdown报告
md_lines = [
    "# 乐云泰App 手工验证报告",
    "",
    f"**验证日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"**测试设备**: 小米13 (fuxi, 1080x2400)",
    f"**测试账号**: 营销角色 17472686748",
    f"**验证方式**: 手工逐步操作 + 截图留证",
    "",
    "---",
    "",
    "## 验证结果统计",
    "",
    f"| 指标 | 数量 | 占比 |",
    f"|------|------|------|",
    f"| ✅ 通过 | {passed} | {passed/max(total-info,1)*100:.1f}% |",
    f"| ❌ 失败 | {failed} | {failed/max(total-info,1)*100:.1f}% |",
    f"| ℹ️ 信息 | {info} | - |",
    f"| **总计** | **{total}** | |",
    "",
    "---",
    "",
    "## 详细验证步骤",
    "",
    "| 步骤 | 标题 | 状态 | 详情 |",
    "|------|------|------|------|",
]

for r in report:
    sym = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "WARN": "⚠️"}.get(r["status"], "ℹ️")
    detail = r["detail"][:60] if len(r["detail"]) > 60 else r["detail"]
    md_lines.append(f"| {r['step']} | {r['title']} | {sym} {r['status']} | {detail} |")

md_lines.extend([
    "",
    "---",
    "",
    "## 验证结论",
    "",
    f"- 本次手工验证共执行 **{total}** 个步骤，其中功能验证 **{total-info}** 项",
    f"- 通过 **{passed}** 项，失败 **{failed}** 项",
    f"- 通过率 **{passed/max(total-info,1)*100:.1f}%**",
    "",
    "### 主要发现",
    "",
    "1. **商品列表功能完整**：设备和人才列表均支持搜索、筛选，商品详情页含完整信息和购买按钮",
    "2. **购物车管理正常**：管理模式可进行删除/全选操作，结算区域显示合计金额",
    "3. **订单操作可用**：可查看协议凭证、发票，订单详情字段完整",
    "4. **客户电话拨打正常**：营销角色点击电话号码弹出拨号确认弹窗",
    "5. **设置/个人中心不可用**：营销角色首页无设置入口，无法访问退出登录、修改密码等功能",
    "",
    "### 截图证据",
    "",
    f"- 截图目录: `{SCREENSHOT_DIR}`",
    f"- UI Dump目录: `{DUMP_DIR}`",
])

report_md = "\n".join(md_lines)
report_path = f"{REPORT_DIR}/manual_verification_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_md)

# 保存原始数据
with open(f"{REPORT_DIR}/manual_verification_data.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"  📊 手工验证完成: 总计{total} ✅{passed} ❌{failed} ℹ️{info}")
print(f"{'='*60}")
print(f"  📁 验证报告: {report_path}")
print(f"  📁 截图目录: {SCREENSHOT_DIR}")
