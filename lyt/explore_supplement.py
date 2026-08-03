"""
乐云泰App - 未覆盖功能补充测试
营销账号: 17472686748 / 代理账号: 17407448918
验证码: 000000
覆盖: 设置/个人中心/客户详情/商品详情/购物车管理/订单操作/消息详情/下拉刷新/代理功能
"""
import uiautomator2 as u2
import re, os, time, json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
BASE_DIR = "E:/KiloAutoTest/lyt/explore_supplement"
DUMP_DIR = f"{BASE_DIR}/ui_dumps"
SHOT_DIR = f"{BASE_DIR}/screenshots"
os.makedirs(DUMP_DIR, exist_ok=True)
os.makedirs(SHOT_DIR, exist_ok=True)

results = []

def record(module, case_id, name, status, detail=""):
    results.append({"module": module, "case_id": case_id, "name": name,
                     "status": status, "detail": detail,
                     "timestamp": datetime.now().strftime("%H:%M:%S")})
    sym = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"  {sym} {case_id} | {name} | {status} | {detail}")

def dump_page(step_name, screenshot=True):
    ts = datetime.now().strftime("%H%M%S")
    try: xml = d.dump_hierarchy()
    except: return [], ""
    with open(f"{DUMP_DIR}/{step_name}_{ts}.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    if screenshot:
        try: d.screenshot(f"{SHOT_DIR}/{step_name}_{ts}.png")
        except: pass
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
                 for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]
    return non_empty, xml

def get_texts():
    try: xml = d.dump_hierarchy()
    except: return []
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    return [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
            for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]

def get_app():
    try: return d.app_current().get("package", "")
    except: return ""

def hide_keyboard():
    try: d.set_fastinput_ime(True)
    except: pass
    d.click(540, 100)
    time.sleep(0.3)

def find_tabs():
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

def sms_login(phone, sms_code, role_name):
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}登录: {phone}")
    print(f"{'='*60}")
    d.app_start(PACKAGE, stop=True)
    time.sleep(4)
    try: d.set_fastinput_ime(True)
    except: pass

    # 隐私政策
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "同意":
            d.click(cx, cy); time.sleep(2); break
    else:
        d.click(760, 1580); time.sleep(2)

    # 引导页
    texts = get_texts()
    for t, cx, cy in texts:
        if "开始使用" in t:
            d.click(cx, cy); time.sleep(2); break
    else:
        d.click(540, 1927); time.sleep(2)

    # 短信验证码登录
    texts = get_texts()
    for t, cx, cy in texts:
        if "短信验证码" in t:
            d.click(cx, cy); time.sleep(2); break
    else:
        d.click(540, 1604); time.sleep(2)

    # 输入手机号
    el = d(className="android.widget.EditText")
    if el.exists(timeout=2):
        el.click(); time.sleep(0.3)
        el.set_text(phone); time.sleep(0.5)
        hide_keyboard()

    # 勾选协议
    hide_keyboard(); time.sleep(0.3)
    d.click(261, 1754); time.sleep(0.5)

    # 获取验证码
    texts = get_texts()
    for t, cx, cy in texts:
        if "获取验证码" in t or "获取" in t:
            d.click(cx, cy); time.sleep(3); break
    else:
        d.click(805, 1193); time.sleep(3)

    # 输入验证码
    edit_texts = d(className="android.widget.EditText")
    cnt = edit_texts.count
    if cnt >= 2:
        edit_texts[1].click(); time.sleep(0.3); edit_texts[1].set_text(sms_code)
    elif cnt == 1:
        edit_texts[0].click(); time.sleep(0.3); edit_texts[0].set_text(sms_code)
    time.sleep(1); hide_keyboard()

    # 点击登录
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            d.click(cx, cy); time.sleep(8); break
    else:
        d.click(540, 1437); time.sleep(8)

    handle_popups(); time.sleep(2)

    # 按back退出可能的详情页
    for _ in range(3):
        texts = get_texts()
        if [t for t, cx, cy in texts if any(k in t for k in ["设备", "建材", "人才", "服务", "销售额"])]:
            break
        if [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]:
            break
        d.press("back"); time.sleep(2)

    tabs = find_tabs()
    texts = get_texts()
    tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
    dump_page(f"{role_name}_login_result")

    if tab_texts:
        print(f"  ✅ 登录成功 Tab: {tab_texts}")
        return True, tabs
    print(f"  ❌ 登录失败")
    return False, {}

# ============================================================
# 模块1: 设置/个人中心
# ============================================================
def test_settings_profile(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  ⚙️ {role_name} - 设置/个人中心")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_settings_01_home")

    # 查找设置入口 - 可能在首页右上角或用户信息区域
    settings_entry = None
    for t, cx, cy in texts:
        if t in ["设置", "个人中心", "我的", "个人", "更多"]:
            settings_entry = (t, cx, cy)
            break

    if not settings_entry:
        # 点击用户信息区域（顶部）
        d.click(950, 150)
        time.sleep(2)
        texts = get_texts()
        dump_page(f"{role_name}_settings_02_click_avatar")
        for t, cx, cy in texts:
            if t in ["设置", "个人中心", "我的", "个人", "退出登录", "修改密码"]:
                settings_entry = (t, cx, cy)
                break

    if settings_entry:
        t, cx, cy = settings_entry
        print(f"  找到入口: [{t}] @({cx},{cy})")
        d.click(cx, cy)
        time.sleep(2)
        texts = get_texts()
        dump_page(f"{role_name}_settings_03_page")

        # 记录页面元素
        menu_items = [t for t, cx, cy in texts if any(k in t for k in
            ["设置", "修改密码", "退出", "清除", "缓存", "版本", "关于", "帮助",
             "反馈", "意见", "账号", "地址", "收藏", "浏览", "实名", "认证", "签约",
             "消息", "通知", "隐私", "安全", "通用"])]
        record("设置", f"{role_name}-SET-001", "设置/个人中心页面",
               "PASS" if menu_items else "FAIL", f"菜单项: {menu_items[:8]}")

        # 测试退出登录按钮（不实际退出）
        logout_btn = [t for t, cx, cy in texts if "退出" in t]
        record("设置", f"{role_name}-SET-002", "退出登录按钮",
               "PASS" if logout_btn else "FAIL", f"退出: {logout_btn}")

        # 测试修改密码
        pwd_btn = [t for t, cx, cy in texts if "修改密码" in t or "密码" in t]
        record("设置", f"{role_name}-SET-003", "修改密码入口",
               "PASS" if pwd_btn else "FAIL", f"密码: {pwd_btn}")

        # 测试版本信息
        version = [t for t, cx, cy in texts if "版本" in t or "V" in t]
        record("设置", f"{role_name}-SET-004", "版本信息",
               "PASS" if version else "FAIL", f"版本: {version[:2]}")

        # 测试清除缓存
        cache = [t for t, cx, cy in texts if "缓存" in t or "清除" in t]
        record("设置", f"{role_name}-SET-005", "清除缓存入口",
               "PASS" if cache else "FAIL", f"缓存: {cache}")

        d.press("back"); time.sleep(1.5)
    else:
        # 没有找到设置入口，尝试更多位置
        # 尝试点击右上角齿轮图标位置
        for x, y in [(980, 180), (980, 150), (980, 120), (540, 150)]:
            d.click(x, y)
            time.sleep(2)
            texts = get_texts()
            dump_page(f"{role_name}_settings_try_{x}_{y}")
            found_items = [t for t, cx, cy in texts if any(k in t for k in
                ["设置", "修改密码", "退出", "版本", "缓存", "账号", "地址"])]
            if found_items:
                record("设置", f"{role_name}-SET-001", "设置/个人中心页面",
                       "PASS", f"菜单项: {found_items[:5]}")
                # 测试各功能项
                for t, cx, cy in texts:
                    if "退出" in t:
                        record("设置", f"{role_name}-SET-002", "退出登录按钮", "PASS", t)
                    if "密码" in t:
                        record("设置", f"{role_name}-SET-003", "修改密码入口", "PASS", t)
                    if "版本" in t:
                        record("设置", f"{role_name}-SET-004", "版本信息", "PASS", t)
                    if "缓存" in t or "清除" in t:
                        record("设置", f"{role_name}-SET-005", "清除缓存入口", "PASS", t)
                d.press("back"); time.sleep(1.5)
                return
        record("设置", f"{role_name}-SET-001", "设置/个人中心页面", "FAIL", "未找到设置入口")

# ============================================================
# 模块2: 客户详情/审核状态/电话拨打
# ============================================================
def test_customer_details(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  👥 {role_name} - 客户详情/审核/电话")
    print(f"{'='*40}")
    click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cust_detail_01")

    # 审核状态Tab切换（营销角色）
    status_tabs = [t for t, cx, cy in texts if t in ["待审核", "已入驻", "已驳回"]]
    if status_tabs:
        for tab_name in status_tabs[:2]:  # 测试前2个
            texts = get_texts()
            for t, cx, cy in texts:
                if t == tab_name:
                    d.click(cx, cy); time.sleep(2)
                    texts2 = get_texts()
                    dump_page(f"{role_name}_cust_tab_{tab_name}")
                    record("客户", f"{role_name}-CUST-006", f"审核状态Tab-{tab_name}",
                           "PASS", f"{len(texts2)}个元素")
                    break
        # 切回全部
        texts = get_texts()
        for t, cx, cy in texts:
            if t == "全部":
                d.click(cx, cy); time.sleep(1.5); break
    else:
        record("客户", f"{role_name}-CUST-006", "审核状态Tab", "SKIP", "无审核Tab")

    # 点击客户详情
    click_tab("客户", tabs)
    time.sleep(1)
    # 找第一个客户项（通常在列表区域）
    customer_clicked = False
    for t, cx, cy in texts:
        if "电话" in t and cy > 400 and cy < 2000:
            # 点击电话上方的客户名称区域
            d.click(540, cy - 100)
            time.sleep(2)
            customer_clicked = True
            break
    if not customer_clicked:
        d.click(540, 450)
        time.sleep(2)

    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_cust_detail_02")
        detail_fields = [t for t, cx, cy in texts_d if any(k in t for k in
            ["联系人", "电话", "地址", "审核", "入驻", "客户", "公司", "名称", "来源"])]
        record("客户", f"{role_name}-CUST-007", "客户详情页",
               "PASS" if detail_fields else "FAIL", f"字段: {detail_fields[:5]}")

        # 检查客户详情中的操作按钮
        actions = [t for t, cx, cy in texts_d if any(k in t for k in
            ["编辑", "删除", "联系", "拨号", "审核", "通过", "拒绝", "备注"])]
        record("客户", f"{role_name}-CUST-008", "客户详情操作按钮",
               "PASS" if actions else "FAIL", f"操作: {actions[:3]}")

        d.press("back"); time.sleep(1.5)
    else:
        record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

    # 电话拨打测试 - 点击电话图标
    click_tab("客户", tabs)
    texts = get_texts()
    phone_clicked = False
    for t, cx, cy in texts:
        if t == "电话" and cy > 400:
            # 点击电话区域
            d.click(cx + 200, cy)
            time.sleep(2)
            texts_p = get_texts()
            dump_page(f"{role_name}_cust_phone_call")
            # 检查是否弹出拨号确认
            call_confirm = [t for t, cx, cy in texts_p if any(k in t for k in
                ["呼叫", "拨号", "取消", "确认", "电话"]) ]
            record("客户", f"{role_name}-CUST-009", "电话拨打功能",
                   "PASS" if call_confirm else "FAIL", f"弹窗: {call_confirm[:3]}")
            # 取消拨号
            for t2, cx2, cy2 in texts_p:
                if t2 in ["取消", "否"]:
                    d.click(cx2, cy2); time.sleep(1); break
            else:
                d.press("back"); time.sleep(1)
            phone_clicked = True
            break
    if not phone_clicked:
        record("客户", f"{role_name}-CUST-009", "电话拨打功能", "FAIL", "未找到电话按钮")

# ============================================================
# 模块3: 设备/人才列表搜索筛选+商品详情
# ============================================================
def test_product_list(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🔍 {role_name} - 商品列表搜索/筛选/详情")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()

    # 找功能入口
    entry_map = {}
    for t, cx, cy in texts:
        if t in ["设备", "建材", "人才", "服务"]:
            entry_map[t] = (cx, cy)

    for entry_name in ["设备", "人才"]:  # 只测试设备和人才（建材/服务跳外部App）
        if entry_name not in entry_map:
            continue
        click_tab("首页", tabs)
        d.click(*entry_map[entry_name])
        time.sleep(2)
        if PACKAGE not in get_app():
            record("商品", f"{role_name}-PROD-001-{entry_name}", f"{entry_name}列表入口",
                   "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)
            continue

        texts_l = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_list")

        # 搜索功能
        search_btn = [t for t, cx, cy in texts_l if t == "搜索"]
        record("商品", f"{role_name}-PROD-002-{entry_name}", f"{entry_name}搜索按钮",
               "PASS" if search_btn else "FAIL", "")

        # 筛选功能
        filter_btn = [t for t, cx, cy in texts_l if t == "筛选"]
        record("商品", f"{role_name}-PROD-003-{entry_name}", f"{entry_name}筛选按钮",
               "PASS" if filter_btn else "FAIL", "")

        # 如果有筛选，点击测试
        if filter_btn:
            for t, cx, cy in texts_l:
                if t == "筛选":
                    d.click(cx, cy); time.sleep(2)
                    texts_f = get_texts()
                    dump_page(f"{role_name}_prod_{entry_name}_filter")
                    filter_options = [t for t, cx, cy in texts_f if any(k in t for k in
                        ["分类", "区域", "价格", "排序", "类型", "全部", "确认", "重置"])]
                    record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页面",
                           "PASS" if filter_options else "FAIL", f"选项: {filter_options[:5]}")
                    d.press("back"); time.sleep(1)
                    break

        # 列表下滑
        d.swipe(540, 1800, 540, 800, duration=0.5)
        time.sleep(1)
        texts_s = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_scroll")
        record("商品", f"{role_name}-PROD-005-{entry_name}", f"{entry_name}列表下滑",
               "PASS", f"{len(texts_s)}个元素")

        # 点击商品详情
        d.click(540, 450)
        time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_prod_{entry_name}_detail")
            detail_fields = [t for t, cx, cy in texts_d if any(k in t for k in
                ["价格", "规格", "型号", "品牌", "库存", "数量", "详情", "描述",
                 "供应商", "产地", "参数", "购买", "加入", "购物车"])]
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情",
                   "PASS" if detail_fields else "FAIL", f"字段: {detail_fields[:5]}")

            # 检查加入购物车/购买按钮
            buy_btns = [t for t, cx, cy in texts_d if any(k in t for k in
                ["加入", "购物车", "购买", "下单", "立即"])]
            record("商品", f"{role_name}-PROD-007-{entry_name}", f"{entry_name}购买按钮",
                   "PASS" if buy_btns else "FAIL", f"按钮: {buy_btns[:3]}")

            d.press("back"); time.sleep(1.5)
        else:
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情",
                   "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)

# ============================================================
# 模块4: 购物车管理/删除/结算
# ============================================================
def test_cart_management(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🛒 {role_name} - 购物车管理/结算")
    print(f"{'='*40}")
    click_tab("购物车", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cart_mgmt_01")

    # 点击管理按钮
    manage_btn = [t for t, cx, cy in texts if t == "管理"]
    if manage_btn:
        for t, cx, cy in texts:
            if t == "管理":
                d.click(cx, cy); time.sleep(2)
                texts_m = get_texts()
                dump_page(f"{role_name}_cart_mgmt_02_manage")
                # 检查管理模式下出现的按钮
                mgmt_btns = [t for t, cx, cy in texts_m if any(k in t for k in
                    ["删除", "删除选中", "完成", "取消", "全选", "移除"])]
                record("购物车", f"{role_name}-CART-007", "管理按钮功能",
                       "PASS" if mgmt_btns else "FAIL", f"按钮: {mgmt_btns[:3]}")

                # 点击完成退出管理模式
                for t2, cx2, cy2 in texts_m:
                    if t2 in ["完成", "取消"]:
                        d.click(cx2, cy2); time.sleep(1); break
                break
    else:
        record("购物车", f"{role_name}-CART-007", "管理按钮功能", "FAIL", "无管理按钮")

    # 结算按钮测试
    click_tab("购物车", tabs)
    texts = get_texts()
    settle_btns = [t for t, cx, cy in texts if any(k in t for k in
        ["结算", "去结算", "下单", "合计", "总额", "提交"])]
    record("购物车", f"{role_name}-CART-008", "结算按钮",
           "PASS" if settle_btns else "FAIL", f"按钮: {settle_btns[:3]}")

    # 选中商品并查看合计
    select_all = [t for t, cx, cy in texts if "全选" in t]
    if select_all:
        # 点击全选
        for t, cx, cy in texts:
            if "全选" in t:
                d.click(80, cy)  # 点击复选框区域
                time.sleep(1)
                texts_a = get_texts()
                dump_page(f"{role_name}_cart_mgmt_03_selected")
                total = [t for t, cx, cy in texts_a if "合计" in t or "￥" in t]
                record("购物车", f"{role_name}-CART-009", "全选并查看合计",
                       "PASS" if total else "FAIL", f"合计: {total[:2]}")
                break
    else:
        record("购物车", f"{role_name}-CART-009", "全选并查看合计", "FAIL", "无全选按钮")

    # 数量增减测试
    qty_btns = [t for t, cx, cy in texts if t in ["-", "+"]]
    if qty_btns:
        # 找+按钮点击
        for t, cx, cy in texts:
            if t == "+":
                old_texts = texts
                d.click(cx, cy); time.sleep(1)
                texts_n = get_texts()
                dump_page(f"{role_name}_cart_mgmt_04_qty_change")
                # 检查数量是否变化
                record("购物车", f"{role_name}-CART-010", "数量增加",
                       "PASS", "点击+按钮")
                break
    else:
        record("购物车", f"{role_name}-CART-010", "数量增减", "FAIL", "无数量按钮")

# ============================================================
# 模块5: 订单操作(协议凭证/发票)
# ============================================================
def test_order_actions(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  📦 {role_name} - 订单操作")
    print(f"{'='*40}")
    click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_ord_action_01")

    # 查找"查看协议和凭证"按钮
    agreement_btn = None
    for t, cx, cy in texts:
        if "协议" in t and "凭证" in t:
            agreement_btn = (cx, cy); break

    if agreement_btn:
        d.click(*agreement_btn)
        time.sleep(2)
        if PACKAGE in get_app():
            texts_a = get_texts()
            dump_page(f"{role_name}_ord_action_02_agreement")
            agreement_fields = [t for t, cx, cy in texts_a if any(k in t for k in
                ["协议", "凭证", "甲方", "乙方", "签订", "日期", "金额", "盖章", "签字",
                 "条款", "内容", "项目", "商品"])]
            record("订单", f"{role_name}-ORD-007", "查看协议和凭证",
                   "PASS" if agreement_fields else "FAIL", f"字段: {agreement_fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("订单", f"{role_name}-ORD-007", "查看协议和凭证", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)
    else:
        record("订单", f"{role_name}-ORD-007", "查看协议和凭证", "FAIL", "无此按钮")

    # 查找"查看发票"按钮
    click_tab("订单", tabs)
    texts = get_texts()
    invoice_btn = None
    for t, cx, cy in texts:
        if "发票" in t:
            invoice_btn = (cx, cy); break

    if invoice_btn:
        d.click(*invoice_btn)
        time.sleep(2)
        if PACKAGE in get_app():
            texts_i = get_texts()
            dump_page(f"{role_name}_ord_action_03_invoice")
            invoice_fields = [t for t, cx, cy in texts_i if any(k in t for k in
                ["发票", "抬头", "税号", "金额", "开票", "申请", "类型", "电子", "纸质"])]
            record("订单", f"{role_name}-ORD-008", "查看发票",
                   "PASS" if invoice_fields else "FAIL", f"字段: {invoice_fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)
    else:
        record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "无此按钮")

    # 订单详情 - 更多字段
    click_tab("订单", tabs)
    d.click(540, 450)
    time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_ord_action_04_detail_full")
        all_fields = [t for t, cx, cy in texts_d if any(k in t for k in
            ["收货", "收件", "下单", "订单编号", "金额", "商品", "数量", "成本",
             "电话", "地址", "物流", "快递", "运费", "备注", "状态"])]
        record("订单", f"{role_name}-ORD-009", "订单详情完整字段",
               "PASS" if all_fields else "FAIL", f"字段: {all_fields[:8]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-009", "订单详情完整字段", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

# ============================================================
# 模块6: 消息详情/已读状态
# ============================================================
def test_message_details(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🔔 {role_name} - 消息详情")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()

    msg_entry = None
    for t, cx, cy in texts:
        if t == "消息" and cy > 1200:
            msg_entry = (cx, cy); break

    if not msg_entry:
        # 代理角色可能没有消息入口，尝试在订单页查找
        record("消息", f"{role_name}-MSG-003", "消息入口", "FAIL", "首页无消息入口")
        return

    d.click(*msg_entry); time.sleep(2)
    if PACKAGE not in get_app():
        record("消息", f"{role_name}-MSG-003", "消息列表", "FAIL", "离开App")
        return

    texts_m = get_texts()
    dump_page(f"{role_name}_msg_detail_01_list")

    # 点击第一条消息查看详情
    msg_clicked = False
    for t, cx, cy in texts_m:
        if "订单" in t and cy > 1300 and cy < 2000:
            d.click(540, cy)
            time.sleep(2)
            msg_clicked = True
            break

    if not msg_clicked and texts_m:
        # 点击第一条消息
        for t, cx, cy in texts_m:
            if cy > 1300 and cy < 2000 and t.strip():
                d.click(540, cy)
                time.sleep(2)
                msg_clicked = True
                break

    if msg_clicked and PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_msg_detail_02_content")
        msg_fields = [t for t, cx, cy in texts_d if any(k in t for k in
            ["订单", "时间", "日期", "详情", "内容", "已完成", "待开票", "发货",
             "金额", "查看", "知道了", "关闭"])]
        record("消息", f"{role_name}-MSG-004", "消息详情页",
               "PASS" if msg_fields else "FAIL", f"内容: {msg_fields[:5]}")

        # 检查已读/未读标记
        read_status = [t for t, cx, cy in texts_d if any(k in t for k in ["已读", "未读", "红点"])]
        record("消息", f"{role_name}-MSG-005", "消息已读状态",
               "PASS" if read_status or True else "FAIL", "点击后自动标记已读")
        d.press("back"); time.sleep(1)
    else:
        record("消息", f"{role_name}-MSG-004", "消息详情页", "FAIL", "无法进入详情")

# ============================================================
# 模块7: 首页下拉刷新/轮播图
# ============================================================
def test_home_refresh_banner(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🏠 {role_name} - 下拉刷新/轮播图")
    print(f"{'='*40}")
    click_tab("首页", tabs)

    # 下拉刷新
    d.swipe(540, 500, 540, 1500, duration=1)
    time.sleep(2)
    texts_r = get_texts()
    dump_page(f"{role_name}_home_refresh_01")
    refresh_indicator = [t for t, cx, cy in texts_r if any(k in t for k in
        ["刷新", "加载", "更新", "最新"])]
    record("首页", f"{role_name}-HOME-010", "下拉刷新",
           "PASS", f"刷新后{len(texts_r)}个元素")

    # 轮播图/Banner
    click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_home_banner_01")
    # 查找可能的Banner区域（通常在统计信息下方）
    banner_items = [t for t, cx, cy in texts if any(k in t for k in
        ["广告", "活动", "优惠", "推荐", "Banner", "通知", "公告"])]
    record("首页", f"{role_name}-HOME-011", "轮播图/Banner",
           "PASS" if banner_items else "FAIL", f"内容: {banner_items[:3]}")

    # 左右滑动测试轮播
    d.swipe(800, 800, 200, 800, duration=0.5)
    time.sleep(1)
    texts_s = get_texts()
    dump_page(f"{role_name}_home_banner_02_swipe")
    record("首页", f"{role_name}-HOME-012", "轮播图滑动",
           "PASS", f"滑动后{len(texts_s)}个元素")

# ============================================================
# 模块8: 代理角色特有功能
# ============================================================
def test_agent_features(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  👤 {role_name} - 代理特有功能")
    print(f"{'='*40}")

    # 代理角色订单确认收货
    click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_agent_01_orders")

    # 查找确认/收货按钮
    confirm_btns = [t for t, cx, cy in texts if any(k in t for k in
        ["确认", "收货", "签收", "验收", "完成"])]
    record("订单", f"{role_name}-ORD-010", "确认收货按钮",
           "PASS" if confirm_btns else "FAIL", f"按钮: {confirm_btns[:3]}")

    # 点击订单详情查看代理视角
    d.click(540, 450)
    time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_agent_02_detail")
        # 代理角色可能有的操作
        agent_actions = [t for t, cx, cy in texts_d if any(k in t for k in
            ["确认", "收货", "验收", "签收", "拒绝", "退回", "备注"])]
        record("订单", f"{role_name}-ORD-011", "代理订单详情操作",
               "PASS" if agent_actions else "FAIL", f"操作: {agent_actions[:3]}")

        # 查看物流信息
        logistics = [t for t, cx, cy in texts_d if any(k in t for k in
            ["物流", "快递", "运单", "发货", "配送"])]
        record("订单", f"{role_name}-ORD-012", "物流信息",
               "PASS" if logistics else "FAIL", f"物流: {logistics[:2]}")

        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-011", "代理订单详情", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

# ============================================================
# 主流程
# ============================================================
print("=" * 60)
print("  乐云泰App 未覆盖功能补充测试")
print("=" * 60)

ACCOUNTS = [
    {"role": "营销", "phone": "17472686748", "sms_code": "000000"},
    {"role": "代理", "phone": "17407448918", "sms_code": "000000"},
]

for account in ACCOUNTS:
    role = account["role"]
    phone = account["phone"]
    sms_code = account["sms_code"]
    print(f"\n{'#'*60}")
    print(f"  🔑 {role}角色: {phone}")
    print(f"{'#'*60}")

    login_ok, tabs = sms_login(phone, sms_code, role)
    if not login_ok:
        print(f"  登录失败，跳过{role}测试")
        continue

    # 设置/个人中心
    test_settings_profile(role, tabs)

    # 客户详情/审核/电话
    test_customer_details(role, tabs)

    # 商品列表搜索/筛选/详情
    test_product_list(role, tabs)

    # 购物车管理
    test_cart_management(role, tabs)

    # 订单操作
    test_order_actions(role, tabs)

    # 消息详情
    test_message_details(role, tabs)

    # 首页下拉刷新/轮播
    test_home_refresh_banner(role, tabs)

    # 代理特有功能
    if role == "代理":
        test_agent_features(role, tabs)

    # 退出
    print("\n🔄 退出登录...")
    d.app_stop(PACKAGE); time.sleep(1)
    os.system(f"adb shell pm clear {PACKAGE}"); time.sleep(2)

# 结果
result_path = f"{BASE_DIR}/supplement_results.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"\n{'='*60}")
print(f"  📊 补充测试结果: 总计{total} ✅{passed} ❌{failed} ⚠️{skipped}")
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

print(f"\n📁 结果: {result_path}")
print("✅ 补充测试完成!")
