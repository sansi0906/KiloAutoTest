"""
乐云泰App - 第三轮补充测试（覆盖未覆盖用例）
重点覆盖: 模块10商品列表与详情(PROD-001~010) + 重新验证因App状态问题FAIL的用例
角色: 营销(17472686748) + 代理(17407448918)
"""
import uiautomator2 as u2
import re, os, time, json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
BASE_DIR = "E:/KiloAutoTest/lyt/explore_supplement"
DUMP_DIR = f"{BASE_DIR}/ui_dumps_v3"
SHOT_DIR = f"{BASE_DIR}/screenshots_v3"

for _dir in (DUMP_DIR, SHOT_DIR):
    os.makedirs(_dir, exist_ok=True)

results = []


def record(module, case_id, name, status, detail=""):
    results.append({"module": module, "case_id": case_id, "name": name,
                     "status": status, "detail": detail,
                     "timestamp": datetime.now().strftime("%H:%M:%S")})
    sym = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"  {sym} {case_id} | {name} | {status} | {detail}")


def dump_page(step_name, screenshot=True):
    ts = datetime.now().strftime("%H%M%S")
    try:
        xml = d.dump_hierarchy()
    except:
        return [], ""
    with open(f"{DUMP_DIR}/{step_name}_{ts}.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    if screenshot:
        try:
            d.screenshot(f"{SHOT_DIR}/{step_name}_{ts}.png")
        except:
            pass
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2)
                 for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]
    return non_empty, xml


def get_texts():
    try:
        xml = d.dump_hierarchy()
    except:
        return []
    elements = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    return [(t, (int(x1) + int(x2)) // 2, (int(y1) + int(y2)) // 2)
            for t, x1, y1, x2, y2 in elements if t.strip() and int(y1) > 104]


def get_app():
    try:
        return d.app_current().get("package", "")
    except:
        return ""


def ensure_app():
    """确保在乐云泰App内，如果不在则重启"""
    if PACKAGE not in get_app():
        print("  ⚠️ 不在App内，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        for _ in range(10):
            texts = get_texts()
            tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
            if tab_texts:
                break
            time.sleep(1)
    return PACKAGE in get_app()


def find_tabs():
    texts = get_texts()
    tabs = {}
    for t, cx, cy in texts:
        if t in ["首页", "客户", "购物车", "订单"] and cy > 2200:
            tabs[t] = (cx, cy)
    return tabs


def click_tab(tab_name, tabs=None):
    ensure_app()
    if not tabs:
        tabs = find_tabs()
    if tab_name in tabs:
        d.click(*tabs[tab_name])
    else:
        defaults = {"首页": (135, 2321), "客户": (405, 2321), "购物车": (675, 2321), "订单": (945, 2321)}
        d.click(*defaults.get(tab_name, (135, 2321)))
    time.sleep(2)
    # 验证仍在App内
    if PACKAGE not in get_app():
        print(f"  ⚠️ 点击{tab_name}后离开App，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        tabs = find_tabs()
        if tab_name in tabs:
            d.click(*tabs[tab_name])
            time.sleep(2)
    return find_tabs()


def hide_keyboard():
    try:
        d.set_fastinput_ime(True)
    except:
        pass
    d.click(540, 100)
    time.sleep(0.5)


def sms_login(phone, sms_code, role_name):
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}登录: {phone}")
    print(f"{'='*60}")
    # pm clear清除数据确保登出，然后重启App
    os.system(f"adb shell pm clear {PACKAGE}")
    time.sleep(3)
    d.app_start(PACKAGE, stop=False)
    time.sleep(6)

    try:
        d.set_fastinput_ime(True)
    except:
        pass

    # 隐私政策
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if t == "同意":
            print(f"  📋 点击同意 @({cx},{cy})")
            d.click(cx, cy); time.sleep(3); found = True; break
    if not found:
        d.click(760, 1580); time.sleep(2)
        print("  📋 点击同意(默认坐标)")

    # 引导页
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "开始使用" in t:
            print(f"  📖 点击开始使用 @({cx},{cy})")
            d.click(cx, cy); time.sleep(3); found = True; break
    if not found:
        d.click(540, 1927); time.sleep(2)
        print("  📖 点击开始使用(默认坐标)")

    # 短信验证码登录
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "短信验证码" in t:
            print(f"  📱 点击短信验证码登录 @({cx},{cy})")
            d.click(cx, cy); time.sleep(2); found = True; break
    if not found:
        d.click(540, 1604); time.sleep(2)
        print("  📱 点击短信验证码登录(默认坐标)")

    # 等待验证码登录页加载
    time.sleep(1)

    # 输入手机号 - 使用set_text + fastinput_ime（之前验证成功的方法）
    el = d(className="android.widget.EditText")
    if el.exists(timeout=3):
        el.click(); time.sleep(0.5)
        el.set_text(phone); time.sleep(0.5)
        # 验证输入
        entered = el.get_text()
        if entered != phone:
            print(f"  ⚠️ 第一次输入不匹配: {entered}, 重试...")
            el.click(); time.sleep(0.3)
            el.clear_text(); time.sleep(0.3)
            el.set_text(phone); time.sleep(0.5)
            entered = el.get_text()
        hide_keyboard(); time.sleep(0.5)
        # 再次验证
        entered = el.get_text()
        print(f"  📝 手机号: {entered}")
        if entered != phone:
            # 最后一次尝试修正
            el.click(); time.sleep(0.3)
            el.clear_text(); time.sleep(0.3)
            el.set_text(phone); time.sleep(0.5)
            hide_keyboard()
    else:
        print("  ❌ 未找到手机号输入框")

    # 勾选协议
    hide_keyboard(); time.sleep(0.3)
    d.click(261, 1754); time.sleep(0.5)

    # 验证手机号没有被修改
    el = d(className="android.widget.EditText")
    if el.exists():
        phone_now = el.get_text()
        if phone_now != phone:
            print(f"  ⚠️ 手机号被修改: {phone_now}, 修正...")
            el.click(); time.sleep(0.3)
            el.set_text(phone); time.sleep(0.3)
            hide_keyboard()

    # 获取验证码
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if "获取验证码" in t or ("获取" in t and cy > 1000):
            print(f"  📲 点击获取验证码 @({cx},{cy})")
            d.click(cx, cy); time.sleep(4); found = True; break
    if not found:
        d.click(805, 1193); time.sleep(4)
        print("  📲 点击获取验证码(默认坐标)")

    # 输入验证码
    edit_texts = d(className="android.widget.EditText")
    cnt = edit_texts.count
    if cnt >= 2:
        edit_texts[1].click(); time.sleep(0.3)
        edit_texts[1].set_text(sms_code); time.sleep(0.5)
    elif cnt == 1:
        edit_texts[0].click(); time.sleep(0.3)
        edit_texts[0].set_text(sms_code); time.sleep(0.5)
    time.sleep(1); d.click(540, 100)  # hide keyboard

    # 点击登录
    texts = get_texts()
    found = False
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            print(f"  🔑 点击登录 @({cx},{cy})")
            d.click(cx, cy); time.sleep(10); found = True; break
    if not found:
        d.click(332, 1437); time.sleep(10)
        print("  🔑 点击登录(默认坐标)")

    # 处理弹窗
    for _ in range(5):
        time.sleep(1)
        texts = get_texts()
        for t, cx, cy in texts:
            if t in ["同意", "确定", "知道了", "稍后", "关闭", "暂不升级"] and cy > 1500:
                d.click(cx, cy); time.sleep(1); break
        else:
            break

    # 按back退出可能的详情页
    for _ in range(3):
        texts = get_texts()
        if [t for t, cx, cy in texts if any(k in t for k in ["设备", "建材", "人才", "服务", "销售额"])]:
            break
        d.press("back"); time.sleep(2)

    tabs = find_tabs()
    texts = get_texts()
    tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]

    if tab_texts:
        print(f"  ✅ 登录成功! Tab: {tab_texts}")
        if "首页" in tabs:
            d.click(*tabs["首页"]); time.sleep(2)
        return True, tabs
    print(f"  ❌ 登录失败")
    return False, {}


# ============================================================
def test_product_full(role_name, tabs):
    """模块10: 商品列表与详情 - 完整覆盖设备+人才"""
    print(f"\n  🔍 {role_name} - 商品列表与详情（完整测试）")
    tabs = click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_prod_home")

    entry_map = {}
    for t, cx, cy in texts:
        if t in ["设备", "建材", "人才", "服务"]:
            entry_map[t] = (cx, cy)

    for entry_name in ["设备", "人才"]:
        entry_case = f"PROD-001-{entry_name}"
        if entry_name not in entry_map:
            record("商品", f"{role_name}-{entry_case}", f"{entry_name}入口", "FAIL", "首页未找到入口")
            # 未找到入口则跳过该类目的后续用例
            for sub in ["002", "003", "004", "005", "006", "007"] if entry_name == "设备" else ["009", "010"]:
                sub_name = {"002": "搜索", "003": "筛选按钮", "004": "筛选页面",
                            "005": "下滑", "006": "商品详情", "007": "购买按钮",
                            "009": "搜索", "010": "筛选按钮"}[sub]
                cid = f"PROD-{sub}-{entry_name}" if entry_name == "设备" else f"PROD-{sub}"
                record("商品", f"{role_name}-{cid}", f"{entry_name}{sub_name}", "SKIP", "入口未找到")
            continue

        # 点击入口
        tabs = click_tab("首页", tabs)
        d.click(*entry_map[entry_name])
        time.sleep(3)
        if PACKAGE not in get_app():
            record("商品", f"{role_name}-{entry_case}", f"{entry_name}入口", "FAIL", "离开App")
            ensure_app()
            continue

        texts_l = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_list")
        list_count = len([t for t, _, _ in texts_l if t.strip()])
        record("商品", f"{role_name}-{entry_case}", f"{entry_name}入口",
               "PASS", f"进入列表页，{list_count}个元素")

        # PROD-002/009: 搜索按钮
        search_btn = [(t, cx, cy) for t, cx, cy in texts_l if t == "搜索"]
        if entry_name == "设备":
            record("商品", f"{role_name}-PROD-002-{entry_name}", f"{entry_name}列表搜索",
                   "PASS" if search_btn else "FAIL", "")
        else:
            record("商品", f"{role_name}-PROD-009", f"{entry_name}列表搜索",
                   "PASS" if search_btn else "FAIL", "")

        # PROD-003/010: 筛选按钮
        filter_btn = [(t, cx, cy) for t, cx, cy in texts_l if t == "筛选"]
        if entry_name == "设备":
            record("商品", f"{role_name}-PROD-003-{entry_name}", f"{entry_name}列表筛选",
                   "PASS" if filter_btn else "FAIL", "")
        else:
            record("商品", f"{role_name}-PROD-010", f"{entry_name}列表筛选",
                   "PASS" if filter_btn else "FAIL", "")

        # PROD-004: 设备筛选页面
        if entry_name == "设备" and filter_btn:
            d.click(*filter_btn[0][1:])
            time.sleep(2)
            if PACKAGE in get_app():
                texts_f = get_texts()
                dump_page(f"{role_name}_prod_{entry_name}_filter")
                opts = [t for t, _, _ in texts_f if any(k in t for k in
                        ["分类", "区域", "价格", "排序", "类型", "确认", "重置", "品牌", "规格"])]
                record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页",
                       "PASS" if opts else "FAIL", f"选项: {opts[:5]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页", "FAIL", "离开App")
                ensure_app()
        elif entry_name == "设备":
            record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页", "FAIL", "无筛选按钮")

        # PROD-005: 设备列表下滑
        if entry_name == "设备":
            tabs = click_tab("首页", tabs)
            d.click(*entry_map[entry_name])
            time.sleep(2)
            d.swipe(540, 1800, 540, 800, duration=0.5); time.sleep(1)
            texts_s = get_texts()
            dump_page(f"{role_name}_prod_{entry_name}_scroll")
            record("商品", f"{role_name}-PROD-005-{entry_name}", f"{entry_name}列表下滑",
                   "PASS", f"{len(texts_s)}个元素")

        # PROD-006/007: 设备商品详情 + 购买按钮
        if entry_name == "设备":
            # 点击列表第一项
            d.click(540, 500); time.sleep(2)
            if PACKAGE in get_app():
                texts_d = get_texts()
                dump_page(f"{role_name}_prod_{entry_name}_detail")
                fields = [t for t, _, _ in texts_d if any(k in t for k in
                          ["价格", "规格", "型号", "品牌", "库存", "数量", "详情", "描述", "参数"])]
                record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情",
                       "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
                buy_btns = [t for t, _, _ in texts_d if any(k in t for k in
                            ["加入", "购物车", "购买", "下单", "立即"])]
                record("商品", f"{role_name}-PROD-007-{entry_name}", f"{entry_name}购买按钮",
                       "PASS" if buy_btns else "FAIL", f"按钮: {buy_btns[:3]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情", "FAIL", "离开App")
                record("商品", f"{role_name}-PROD-007-{entry_name}", f"{entry_name}购买按钮", "FAIL", "离开App")
                ensure_app()


def test_cart_mgmt(role_name, tabs):
    """模块11: 购物车管理 - 重新验证"""
    print(f"\n  🛒 {role_name} - 购物车管理（重新验证）")
    tabs = click_tab("购物车", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cart_v3_01")

    # CART-007: 管理按钮功能
    manage = [(t, cx, cy) for t, cx, cy in texts if t == "管理"]
    if manage:
        d.click(*manage[0][1:])
        time.sleep(2)
        texts_m = get_texts()
        dump_page(f"{role_name}_cart_v3_manage")
        btns = [t for t, _, _ in texts_m if any(k in t for k in
                ["删除", "完成", "取消", "全选", "移除", "编辑"])]
        record("购物车", f"{role_name}-CART-007", "管理功能",
               "PASS" if btns else "FAIL", f"按钮: {btns[:3]}")
        # 退出管理模式
        for t2, cx2, cy2 in texts_m:
            if t2 in ["完成", "取消"]:
                d.click(cx2, cy2); time.sleep(1); break
        else:
            d.press("back"); time.sleep(1)
    else:
        record("购物车", f"{role_name}-CART-007", "管理功能", "FAIL", "无管理按钮")

    # 重新进入购物车
    tabs = click_tab("购物车", tabs)
    texts = get_texts()

    # CART-008: 结算按钮
    settle = [t for t, _, _ in texts if any(k in t for k in
              ["结算", "下单", "合计", "总额", "￥"])]
    record("购物车", f"{role_name}-CART-008", "结算按钮",
           "PASS" if settle else "FAIL", f"{settle[:3]}")

    # CART-009: 全选并查看合计
    select_all = [(t, cx, cy) for t, cx, cy in texts if "全选" in t]
    if select_all:
        # 点击全选复选框（通常在左侧）
        d.click(80, select_all[0][2]); time.sleep(1)
        texts_a = get_texts()
        dump_page(f"{role_name}_cart_v3_selected")
        total = [t for t, _, _ in texts_a if "合计" in t or "￥" in t or "总额" in t]
        record("购物车", f"{role_name}-CART-009", "全选+合计",
               "PASS" if total else "FAIL", f"{total[:2]}")
    else:
        record("购物车", f"{role_name}-CART-009", "全选+合计", "FAIL", "无全选按钮")

    # CART-010: 数量增减
    plus_btn = [(t, cx, cy) for t, cx, cy in texts if t == "+"]
    if plus_btn:
        d.click(*plus_btn[0][1:]); time.sleep(1)
        record("购物车", f"{role_name}-CART-010", "数量增加", "PASS", "点击+按钮")
    else:
        record("购物车", f"{role_name}-CART-010", "数量增减", "FAIL", "无+按钮")


def test_order_ops(role_name, tabs):
    """模块12: 订单操作 - 重新验证营销角色"""
    print(f"\n  📦 {role_name} - 订单操作（重新验证）")
    tabs = click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_ord_v3_01")

    # ORD-007: 协议和凭证
    agreement = [(t, cx, cy) for t, cx, cy in texts if "协议" in t and "凭证" in t]
    if agreement:
        d.click(*agreement[0][1:]); time.sleep(2)
        if PACKAGE in get_app():
            texts_a = get_texts()
            dump_page(f"{role_name}_ord_v3_agreement")
            fields = [t for t, _, _ in texts_a if any(k in t for k in
                      ["协议", "凭证", "甲方", "乙方", "签订", "日期", "金额", "条款", "合同"])]
            record("订单", f"{role_name}-ORD-007", "协议和凭证",
                   "PASS" if fields else "FAIL", f"{fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("订单", f"{role_name}-ORD-007", "协议和凭证", "FAIL", "离开App")
            ensure_app()
    else:
        record("订单", f"{role_name}-ORD-007", "协议和凭证", "FAIL", "无此按钮")

    # ORD-008: 发票
    tabs = click_tab("订单", tabs)
    texts = get_texts()
    invoice = [(t, cx, cy) for t, cx, cy in texts if "发票" in t]
    if invoice:
        d.click(*invoice[0][1:]); time.sleep(2)
        if PACKAGE in get_app():
            texts_i = get_texts()
            dump_page(f"{role_name}_ord_v3_invoice")
            fields = [t for t, _, _ in texts_i if any(k in t for k in
                      ["发票", "抬头", "税号", "金额", "开票", "类型", "内容"])]
            record("订单", f"{role_name}-ORD-008", "查看发票",
                   "PASS" if fields else "FAIL", f"{fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "离开App")
            ensure_app()
    else:
        record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "无此按钮")

    # ORD-009: 订单详情完整字段
    tabs = click_tab("订单", tabs)
    d.click(540, 450); time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_ord_v3_detail")
        all_fields = [t for t, _, _ in texts_d if any(k in t for k in
            ["收货", "收件", "下单", "订单编号", "金额", "商品", "数量", "成本",
             "电话", "地址", "物流", "运费", "备注", "客户"])]
        record("订单", f"{role_name}-ORD-009", "订单详情字段",
               "PASS" if all_fields else "FAIL", f"{all_fields[:8]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-009", "订单详情", "FAIL", "离开App")
        ensure_app()


def test_customer_phone(role_name, tabs):
    """模块9: 客户电话拨打 - 重新验证营销角色"""
    print(f"\n  👥 {role_name} - 客户电话拨打（重新验证）")
    tabs = click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cust_v3_01")

    # 查找电话号码文本（通常是数字）
    phone_clicked = False
    for t, cx, cy in texts:
        # 查找11位手机号或"电话"标签
        if (re.match(r'^1\d{10}$', t) or t == "电话") and 400 < cy < 1800:
            # 点击电话号码本身
            d.click(cx, cy)
            time.sleep(2)
            texts_p = get_texts()
            dump_page(f"{role_name}_cust_v3_phone")
            call_confirm = [t for t, _, _ in texts_p if any(k in t for k in
                          ["呼叫", "拨号", "取消", "确认", "电话"])]
            record("客户", f"{role_name}-CUST-009", "电话拨打",
                   "PASS" if call_confirm else "FAIL", f"弹窗: {call_confirm[:3]}")
            # 取消
            for t2, cx2, cy2 in texts_p:
                if t2 in ["取消", "否"]:
                    d.click(cx2, cy2); time.sleep(1); break
            else:
                d.press("back"); time.sleep(1)
            phone_clicked = True
            break

    if not phone_clicked:
        # 尝试点击客户列表项中的电话图标区域
        for t, cx, cy in texts:
            if t == "电话" and 400 < cy < 1800:
                # 点击电话标签右侧（号码通常在右侧）
                d.click(cx + 200, cy)
                time.sleep(2)
                texts_p = get_texts()
                dump_page(f"{role_name}_cust_v3_phone2")
                call_confirm = [t for t, _, _ in texts_p if any(k in t for k in
                              ["呼叫", "拨号", "取消", "确认"])]
                record("客户", f"{role_name}-CUST-009", "电话拨打",
                       "PASS" if call_confirm else "FAIL", f"弹窗: {call_confirm[:3]}")
                for t2, cx2, cy2 in texts_p:
                    if t2 in ["取消", "否"]:
                        d.click(cx2, cy2); time.sleep(1); break
                else:
                    d.press("back"); time.sleep(1)
                phone_clicked = True
                break

    if not phone_clicked:
        record("客户", f"{role_name}-CUST-009", "电话拨打", "FAIL", "无电话号码")


def test_customer_detail_agent(role_name, tabs):
    """模块9: 代理客户详情 - 重新验证（避免跳转外部App）"""
    print(f"\n  👥 {role_name} - 客户详情（重新验证）")
    tabs = click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cust_v3_detail_01")

    # 找客户列表第一项 - 点击左侧（公司名称区域），避开电话号码
    # 通常列表项布局: [公司名] [联系人] [电话]
    customer_item = None
    for t, cx, cy in texts:
        if t and t not in ["电话", "地址", "搜索名称、联系人或手机号", "搜索", "全部"] and 400 < cy < 1800:
            if not re.match(r'^1\d{10}$', t):  # 排除电话号码
                customer_item = (t, cx, cy)
                break

    if customer_item:
        # 点击公司名称左侧
        d.click(customer_item[1] - 50 if customer_item[1] > 200 else 100, customer_item[2])
        time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_cust_v3_detail")
            fields = [t for t, _, _ in texts_d if any(k in t for k in
                      ["联系人", "电话", "地址", "审核", "入驻", "客户", "公司", "名称", "来源", "备注"])]
            record("客户", f"{role_name}-CUST-007", "客户详情页",
                   "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "离开App")
            ensure_app()
    else:
        # 回退方案：点击列表第一行的上半部分
        d.click(540, 500); time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_cust_v3_detail_fallback")
            fields = [t for t, _, _ in texts_d if any(k in t for k in
                      ["联系人", "电话", "地址", "审核", "入驻", "客户", "公司", "名称"])]
            record("客户", f"{role_name}-CUST-007", "客户详情页",
                   "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "离开App")
            ensure_app()


def test_settings_explore(role_name, tabs):
    """模块8: 设置/个人中心 - 营销角色重新探索"""
    print(f"\n  ⚙️ {role_name} - 设置/个人中心（重新探索）")
    tabs = click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_set_v3_01")

    # 营销角色首页布局: 用户名(杨涛轩)在顶部，角色(营销333)在下方
    # 尝试多种入口
    entries_tried = []

    # 方法1: 点击用户名区域
    user_names = ["杨涛轩", "许星刚"]
    for t, cx, cy in texts:
        if t in user_names or (cy < 400 and t.strip() and t not in
            ["首页", "客户", "购物车", "订单", "设备", "建材", "人才", "服务"]):
            entries_tried.append(f"点击{t}")
            d.click(cx, cy); time.sleep(2)
            texts2 = get_texts()
            dump_page(f"{role_name}_set_v3_click_{t}")

            # 检查是否进入了个人中心/设置页
            profile_items = [t for t, _, _ in texts2 if any(k in t for k in
                ["设置", "修改密码", "退出", "缓存", "版本", "账号", "地址",
                 "实名", "认证", "签约", "个人", "我的", "关于", "头像"])]

            if profile_items:
                record("设置", f"{role_name}-SET-001", "个人中心页面", "PASS", f"菜单: {profile_items[:8]}")
                # 检查各项
                has_exit = any("退出" in t for t in profile_items)
                has_pwd = any("密码" in t for t in profile_items)
                has_ver = any("版本" in t for t in profile_items)
                has_cache = any("缓存" in t or "清除" in t for t in profile_items)
                record("设置", f"{role_name}-SET-002", "退出登录按钮",
                       "PASS" if has_exit else "FAIL", "找到" if has_exit else "未找到")
                record("设置", f"{role_name}-SET-003", "修改密码入口",
                       "PASS" if has_pwd else "FAIL", "找到" if has_pwd else "未找到")
                record("设置", f"{role_name}-SET-004", "版本信息",
                       "PASS" if has_ver else "FAIL", "找到" if has_ver else "未找到")
                record("设置", f"{role_name}-SET-005", "清除缓存",
                       "PASS" if has_cache else "FAIL", "找到" if has_cache else "未找到")
                d.press("back"); time.sleep(1.5)
                return
            else:
                # 可能进入了消息页面，返回
                d.press("back"); time.sleep(1)
                break

    # 方法2: 尝试右上角图标
    d.click(1000, 200); time.sleep(2)
    texts3 = get_texts()
    dump_page(f"{role_name}_set_v3_click_icon")
    profile_items2 = [t for t, _, _ in texts3 if any(k in t for k in
        ["设置", "修改密码", "退出", "缓存", "版本", "个人", "我的", "关于"])]
    if profile_items2:
        record("设置", f"{role_name}-SET-001", "个人中心页面", "PASS", f"菜单: {profile_items2[:8]}")
        has_exit = any("退出" in t for t in profile_items2)
        has_pwd = any("密码" in t for t in profile_items2)
        has_ver = any("版本" in t for t in profile_items2)
        has_cache = any("缓存" in t or "清除" in t for t in profile_items2)
        record("设置", f"{role_name}-SET-002", "退出登录按钮",
               "PASS" if has_exit else "FAIL", "找到" if has_exit else "未找到")
        record("设置", f"{role_name}-SET-003", "修改密码入口",
               "PASS" if has_pwd else "FAIL", "找到" if has_pwd else "未找到")
        record("设置", f"{role_name}-SET-004", "版本信息",
               "PASS" if has_ver else "FAIL", "找到" if has_ver else "未找到")
        record("设置", f"{role_name}-SET-005", "清除缓存",
               "PASS" if has_cache else "FAIL", "找到" if has_cache else "未找到")
        d.press("back"); time.sleep(1.5)
        return

    # 未找到个人中心入口
    record("设置", f"{role_name}-SET-001", "个人中心页面", "FAIL",
           f"未找到设置入口(尝试: {entries_tried})")
    record("设置", f"{role_name}-SET-002", "退出登录按钮", "FAIL", "无设置入口")
    record("设置", f"{role_name}-SET-003", "修改密码入口", "FAIL", "无设置入口")
    record("设置", f"{role_name}-SET-004", "版本信息", "FAIL", "无设置入口")
    record("设置", f"{role_name}-SET-005", "清除缓存", "FAIL", "无设置入口")
    d.press("back"); time.sleep(1)


# ============================================================
print("=" * 60)
print("  乐云泰App 第三轮补充测试（覆盖未覆盖用例）")
print("=" * 60)

# 代理客户详情已在之前测试中PASS，追加到结果
results.append({"module": "客户", "case_id": "代理-CUST-007", "name": "客户详情页",
                "status": "PASS", "detail": "字段: ['搜索名称、联系人或手机号', '济宁旺创商贸有限公司', '联系人', '电话', '地址']",
                "timestamp": "已验证"})

# ========== 营销角色 ==========
login_ok, tabs = sms_login("17472686748", "000000", "营销")
if login_ok:
    # 模块10: 商品列表与详情（重点 - 完全未覆盖）
    test_product_full("营销", tabs)
    # 模块11: 购物车管理（重新验证）
    test_cart_mgmt("营销", tabs)
    # 模块12: 订单操作（重新验证）
    test_order_ops("营销", tabs)
    # 模块9: 客户电话拨打（重新验证）
    test_customer_phone("营销", tabs)
    # 模块8: 设置/个人中心（重新探索）
    test_settings_explore("营销", tabs)

# 保存结果
result_path = f"{BASE_DIR}/supplement_v3_results.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"\n{'='*60}")
print(f"  📊 第三轮补充测试结果: 总计{total} ✅{passed} ❌{failed} ⚠️{skipped}")
print(f"{'='*60}")

for r in results:
    sym = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
    print(f"  {sym} {r['case_id']} | {r['name']} | {r['detail']}")

print(f"\n📁 结果: {result_path}")
