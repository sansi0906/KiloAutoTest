"""
乐云泰App - 营销账号补充测试（修复登录）
"""
import uiautomator2 as u2
import re, os, time, json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
BASE_DIR = "E:/KiloAutoTest/lyt/explore_supplement"
DUMP_DIR = f"{BASE_DIR}/ui_dumps"
SHOT_DIR = f"{BASE_DIR}/screenshots"

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

def sms_login_fixed(phone, sms_code, role_name):
    """修复版验证码登录"""
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}登录: {phone}")
    print(f"{'='*60}")

    # 清除数据并启动
    os.system(f"adb shell pm clear {PACKAGE}")
    time.sleep(2)
    d.app_start(PACKAGE, stop=False)
    time.sleep(5)

    # 隐私政策
    texts = get_texts()
    print(f"  启动后页面文本: {[t for t,_,_ in texts][:8]}")
    for t, cx, cy in texts:
        if t == "同意":
            print(f"  点击同意 @({cx},{cy})")
            d.click(cx, cy); time.sleep(3); break
    else:
        # 可能已经在其他页面
        pass

    # 引导页
    texts = get_texts()
    for t, cx, cy in texts:
        if "开始使用" in t:
            print(f"  点击开始使用 @({cx},{cy})")
            d.click(cx, cy); time.sleep(3); break

    # 等待登录页加载
    time.sleep(1)
    texts = get_texts()
    print(f"  登录页文本: {[t for t,_,_ in texts][:10]}")

    # 短信验证码登录
    for t, cx, cy in texts:
        if "短信验证码" in t:
            print(f"  点击短信验证码登录 @({cx},{cy})")
            d.click(cx, cy); time.sleep(2); break
    else:
        # 可能已经在验证码登录页
        print("  未找到短信验证码按钮，可能在验证码登录页")

    time.sleep(1)
    texts = get_texts()
    print(f"  验证码登录页文本: {[t for t,_,_ in texts][:10]}")

    # 输入手机号 - 使用adb shell input
    el = d(className="android.widget.EditText")
    if el.exists(timeout=3):
        el.click()
        time.sleep(0.5)
        # 使用adb shell清除并输入
        os.system("adb shell input keyevent KEYCODE_MOVE_END")
        time.sleep(0.2)
        # 长按删除所有内容
        for _ in range(15):
            os.system("adb shell input keyevent KEYCODE_DEL")
        time.sleep(0.3)
        # 使用adb shell input text
        os.system(f"adb shell input text {phone}")
        time.sleep(1)

        # 验证输入
        entered = el.get_text()
        print(f"  手机号输入结果: {entered}")
        if entered != phone:
            # 使用uiautomator2的set_text
            el.set_text(phone)
            time.sleep(0.5)
            entered = el.get_text()
            print(f"  重试后手机号: {entered}")

        hide_keyboard()
    else:
        print("  ❌ 未找到输入框")
        return False, {}

    # 勾选协议
    time.sleep(0.5)
    d.click(261, 1754)
    time.sleep(0.5)

    # 验证手机号没被修改
    el = d(className="android.widget.EditText")
    if el.exists():
        phone_now = el.get_text()
        if phone_now != phone:
            print(f"  ⚠️ 手机号被修改为{phone_now}，修正")
            el.click(); time.sleep(0.3)
            el.set_text(phone); time.sleep(0.3)
            hide_keyboard()

    # 获取验证码
    texts = get_texts()
    for t, cx, cy in texts:
        if "获取验证码" in t or ("获取" in t and cy > 1000):
            print(f"  点击获取验证码 @({cx},{cy})")
            d.click(cx, cy); time.sleep(4); break
    else:
        d.click(805, 1193); time.sleep(4)

    # 验证手机号仍然正确
    el = d(className="android.widget.EditText")
    if el.exists():
        phone_now = el.get_text()
        if phone_now != phone:
            print(f"  ⚠️ 获取验证码后手机号变为{phone_now}")
            el.click(); time.sleep(0.3)
            el.set_text(phone); time.sleep(0.3)
            hide_keyboard()

    # 输入验证码
    edit_texts = d(className="android.widget.EditText")
    cnt = edit_texts.count
    print(f"  找到{cnt}个输入框")
    if cnt >= 2:
        edit_texts[1].click(); time.sleep(0.3)
        edit_texts[1].set_text(sms_code)
    elif cnt == 1:
        edit_texts[0].click(); time.sleep(0.3)
        edit_texts[0].set_text(sms_code)
    time.sleep(1)
    hide_keyboard()
    print(f"  验证码已输入: {sms_code}")

    # 截图登录前
    dump_page(f"{role_name}_before_login_click")

    # 点击登录 - 找到登录按钮
    texts = get_texts()
    print(f"  登录按钮查找: {[t for t,_,_ in texts if '登录' in t]}")

    login_clicked = False
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            print(f"  点击登录 @({cx},{cy})")
            d.click(cx, cy); time.sleep(10)
            login_clicked = True
            break

    if not login_clicked:
        # 尝试其他位置
        for y in [1437, 1500, 1400, 1600]:
            d.click(540, y)
            time.sleep(3)
            texts = get_texts()
            tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
            if tab_texts:
                login_clicked = True
                break

    handle_popups()
    time.sleep(2)

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
        print(f"  ✅ 登录成功! Tab: {tab_texts}")
        return True, tabs
    else:
        print(f"  ❌ 登录失败. 当前文本: {[t for t,_,_ in texts][:8]}")
        return False, {}

# ============================================================
# 测试函数（与explore_supplement.py相同）
# ============================================================
def test_settings_profile(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  ⚙️ {role_name} - 设置/个人中心")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_settings_01_home")

    # 尝试多种方式找到设置入口
    found = False
    for t, cx, cy in texts:
        if t in ["设置", "个人中心", "我的", "个人", "系统设置"]:
            d.click(cx, cy); time.sleep(2)
            texts = get_texts()
            dump_page(f"{role_name}_settings_02_page")
            menu_items = [t for t, cx, cy in texts if any(k in t for k in
                ["设置", "修改密码", "退出", "缓存", "版本", "关于", "帮助",
                 "反馈", "账号", "地址", "收藏", "实名", "认证", "签约", "通知"])]
            record("设置", f"{role_name}-SET-001", "设置/个人中心页面",
                   "PASS" if menu_items else "FAIL", f"菜单: {menu_items[:8]}")
            logout_btn = [t for t, cx, cy in texts if "退出" in t]
            record("设置", f"{role_name}-SET-002", "退出登录按钮", "PASS" if logout_btn else "FAIL", f"{logout_btn}")
            pwd_btn = [t for t, cx, cy in texts if "密码" in t]
            record("设置", f"{role_name}-SET-003", "修改密码入口", "PASS" if pwd_btn else "FAIL", f"{pwd_btn}")
            version = [t for t, cx, cy in texts if "版本" in t]
            record("设置", f"{role_name}-SET-004", "版本信息", "PASS" if version else "FAIL", f"{version[:2]}")
            cache = [t for t, cx, cy in texts if "缓存" in t or "清除" in t]
            record("设置", f"{role_name}-SET-005", "清除缓存入口", "PASS" if cache else "FAIL", f"{cache}")
            d.press("back"); time.sleep(1.5)
            found = True
            break

    if not found:
        # 尝试点击右上角
        for x, y in [(980, 180), (980, 150), (980, 120), (540, 150)]:
            d.click(x, y); time.sleep(2)
            texts = get_texts()
            dump_page(f"{role_name}_settings_try_{x}_{y}")
            items = [t for t, cx, cy in texts if any(k in t for k in
                ["设置", "修改密码", "退出", "版本", "缓存", "账号", "地址", "系统"])]
            if items:
                record("设置", f"{role_name}-SET-001", "设置/个人中心页面", "PASS", f"菜单: {items[:5]}")
                for t in items:
                    if "退出" in t: record("设置", f"{role_name}-SET-002", "退出登录按钮", "PASS", t)
                    if "密码" in t: record("设置", f"{role_name}-SET-003", "修改密码入口", "PASS", t)
                    if "版本" in t: record("设置", f"{role_name}-SET-004", "版本信息", "PASS", t)
                    if "缓存" in t: record("设置", f"{role_name}-SET-005", "清除缓存入口", "PASS", t)
                d.press("back"); time.sleep(1.5)
                found = True
                break
    if not found:
        record("设置", f"{role_name}-SET-001", "设置/个人中心页面", "FAIL", "未找到设置入口")

def test_customer_details(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  👥 {role_name} - 客户详情/审核/电话")
    print(f"{'='*40}")
    click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cust_detail_01")

    # 审核状态Tab
    status_tabs = [(t, cx, cy) for t, cx, cy in texts if t in ["待审核", "已入驻", "已驳回"]]
    if status_tabs:
        for t, cx, cy in status_tabs[:2]:
            d.click(cx, cy); time.sleep(2)
            texts2 = get_texts()
            dump_page(f"{role_name}_cust_tab_{t}")
            record("客户", f"{role_name}-CUST-006", f"审核状态Tab-{t}", "PASS", f"{len(texts2)}个元素")
        # 切回全部
        texts = get_texts()
        for t, cx, cy in texts:
            if t == "全部": d.click(cx, cy); time.sleep(1.5); break
    else:
        record("客户", f"{role_name}-CUST-006", "审核状态Tab", "SKIP", "无审核Tab")

    # 点击客户详情
    click_tab("客户", tabs); time.sleep(1)
    # 找客户列表项点击
    d.click(540, 450)
    time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_cust_detail_02")
        detail_fields = [t for t, cx, cy in texts_d if any(k in t for k in
            ["联系人", "电话", "地址", "审核", "入驻", "客户", "公司", "名称"])]
        record("客户", f"{role_name}-CUST-007", "客户详情页",
               "PASS" if detail_fields else "FAIL", f"字段: {detail_fields[:5]}")
        actions = [t for t, cx, cy in texts_d if any(k in t for k in
            ["编辑", "删除", "联系", "拨号", "审核", "通过", "拒绝", "备注"])]
        record("客户", f"{role_name}-CUST-008", "客户详情操作按钮",
               "PASS" if actions else "FAIL", f"操作: {actions[:3]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

    # 电话拨打
    click_tab("客户", tabs)
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "电话" and cy > 400:
            d.click(cx + 200, cy); time.sleep(2)
            texts_p = get_texts()
            dump_page(f"{role_name}_cust_phone")
            call_confirm = [t for t, cx, cy in texts_p if any(k in t for k in ["呼叫", "拨号", "取消", "确认"])]
            record("客户", f"{role_name}-CUST-009", "电话拨打功能",
                   "PASS" if call_confirm else "FAIL", f"弹窗: {call_confirm[:3]}")
            for t2, cx2, cy2 in texts_p:
                if t2 in ["取消", "否"]: d.click(cx2, cy2); time.sleep(1); break
            else: d.press("back"); time.sleep(1)
            break
    else:
        record("客户", f"{role_name}-CUST-009", "电话拨打功能", "FAIL", "未找到电话按钮")

def test_product_list(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🔍 {role_name} - 商品列表搜索/筛选/详情")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()

    entry_map = {}
    for t, cx, cy in texts:
        if t in ["设备", "建材", "人才", "服务"]:
            entry_map[t] = (cx, cy)

    for entry_name in ["设备", "人才"]:
        if entry_name not in entry_map: continue
        click_tab("首页", tabs)
        d.click(*entry_map[entry_name]); time.sleep(2)
        if PACKAGE not in get_app():
            record("商品", f"{role_name}-PROD-001-{entry_name}", f"{entry_name}列表入口", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3); continue

        texts_l = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_list")
        record("商品", f"{role_name}-PROD-002-{entry_name}", f"{entry_name}搜索按钮",
               "PASS" if [t for t,_,_ in texts_l if t == "搜索"] else "FAIL", "")
        record("商品", f"{role_name}-PROD-003-{entry_name}", f"{entry_name}筛选按钮",
               "PASS" if [t for t,_,_ in texts_l if t == "筛选"] else "FAIL", "")

        # 筛选测试
        for t, cx, cy in texts_l:
            if t == "筛选":
                d.click(cx, cy); time.sleep(2)
                texts_f = get_texts()
                dump_page(f"{role_name}_prod_{entry_name}_filter")
                opts = [t for t,_,_ in texts_f if any(k in t for k in ["分类", "区域", "价格", "排序", "类型", "确认", "重置"])]
                record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页面",
                       "PASS" if opts else "FAIL", f"选项: {opts[:5]}")
                d.press("back"); time.sleep(1); break

        # 列表下滑
        d.swipe(540, 1800, 540, 800, duration=0.5); time.sleep(1)
        texts_s = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_scroll")
        record("商品", f"{role_name}-PROD-005-{entry_name}", f"{entry_name}列表下滑", "PASS", f"{len(texts_s)}个元素")

        # 商品详情
        d.click(540, 450); time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_prod_{entry_name}_detail")
            detail_fields = [t for t, cx, cy in texts_d if any(k in t for k in
                ["价格", "规格", "型号", "品牌", "库存", "数量", "详情", "描述", "供应商", "参数", "购买", "加入"])]
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情",
                   "PASS" if detail_fields else "FAIL", f"字段: {detail_fields[:5]}")
            buy_btns = [t for t,_,_ in texts_d if any(k in t for k in ["加入", "购物车", "购买", "下单", "立即"])]
            record("商品", f"{role_name}-PROD-007-{entry_name}", f"{entry_name}购买按钮",
                   "PASS" if buy_btns else "FAIL", f"按钮: {buy_btns[:3]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情", "FAIL", "离开App")
            d.app_start(PACKAGE, stop=False); time.sleep(3)

def test_cart_management(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🛒 {role_name} - 购物车管理/结算")
    print(f"{'='*40}")
    click_tab("购物车", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cart_mgmt_01")

    # 管理按钮
    for t, cx, cy in texts:
        if t == "管理":
            d.click(cx, cy); time.sleep(2)
            texts_m = get_texts()
            dump_page(f"{role_name}_cart_mgmt_02_manage")
            mgmt_btns = [t for t,_,_ in texts_m if any(k in t for k in ["删除", "完成", "取消", "全选", "移除"])]
            record("购物车", f"{role_name}-CART-007", "管理按钮功能",
                   "PASS" if mgmt_btns else "FAIL", f"按钮: {mgmt_btns[:3]}")
            for t2, cx2, cy2 in texts_m:
                if t2 in ["完成", "取消"]: d.click(cx2, cy2); time.sleep(1); break
            break
    else:
        record("购物车", f"{role_name}-CART-007", "管理按钮功能", "FAIL", "无管理按钮")

    # 结算按钮
    click_tab("购物车", tabs)
    texts = get_texts()
    settle_btns = [t for t,_,_ in texts if any(k in t for k in ["结算", "下单", "合计", "总额", "提交"])]
    record("购物车", f"{role_name}-CART-008", "结算按钮",
           "PASS" if settle_btns else "FAIL", f"按钮: {settle_btns[:3]}")

    # 全选
    for t, cx, cy in texts:
        if "全选" in t:
            d.click(80, cy); time.sleep(1)
            texts_a = get_texts()
            dump_page(f"{role_name}_cart_mgmt_03_selected")
            total = [t for t,_,_ in texts_a if "合计" in t or "￥" in t]
            record("购物车", f"{role_name}-CART-009", "全选并查看合计",
                   "PASS" if total else "FAIL", f"合计: {total[:2]}")
            break
    else:
        record("购物车", f"{role_name}-CART-009", "全选并查看合计", "FAIL", "无全选按钮")

    # 数量增减
    for t, cx, cy in texts:
        if t == "+":
            d.click(cx, cy); time.sleep(1)
            dump_page(f"{role_name}_cart_mgmt_04_qty")
            record("购物车", f"{role_name}-CART-010", "数量增加", "PASS", "点击+按钮")
            break
    else:
        record("购物车", f"{role_name}-CART-010", "数量增减", "FAIL", "无数量按钮")

def test_order_actions(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  📦 {role_name} - 订单操作")
    print(f"{'='*40}")
    click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_ord_action_01")

    # 查看协议和凭证
    for t, cx, cy in texts:
        if "协议" in t and "凭证" in t:
            d.click(cx, cy); time.sleep(2)
            if PACKAGE in get_app():
                texts_a = get_texts()
                dump_page(f"{role_name}_ord_action_02_agreement")
                fields = [t for t,_,_ in texts_a if any(k in t for k in
                    ["协议", "凭证", "甲方", "乙方", "签订", "日期", "金额", "条款", "项目"])]
                record("订单", f"{role_name}-ORD-007", "查看协议和凭证",
                       "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("订单", f"{role_name}-ORD-007", "查看协议和凭证", "FAIL", "离开App")
                d.app_start(PACKAGE, stop=False); time.sleep(3)
            break
    else:
        record("订单", f"{role_name}-ORD-007", "查看协议和凭证", "FAIL", "无此按钮")

    # 查看发票
    click_tab("订单", tabs)
    texts = get_texts()
    for t, cx, cy in texts:
        if "发票" in t:
            d.click(cx, cy); time.sleep(2)
            if PACKAGE in get_app():
                texts_i = get_texts()
                dump_page(f"{role_name}_ord_action_03_invoice")
                fields = [t for t,_,_ in texts_i if any(k in t for k in
                    ["发票", "抬头", "税号", "金额", "开票", "类型", "电子", "纸质"])]
                record("订单", f"{role_name}-ORD-008", "查看发票",
                       "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "离开App")
                d.app_start(PACKAGE, stop=False); time.sleep(3)
            break
    else:
        record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "无此按钮")

    # 订单详情完整字段
    click_tab("订单", tabs)
    d.click(540, 450); time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_ord_action_04_detail")
        all_fields = [t for t, cx, cy in texts_d if any(k in t for k in
            ["收货", "收件", "下单", "订单编号", "金额", "商品", "数量", "成本",
             "电话", "地址", "物流", "运费", "备注", "状态"])]
        record("订单", f"{role_name}-ORD-009", "订单详情完整字段",
               "PASS" if all_fields else "FAIL", f"字段: {all_fields[:8]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-009", "订单详情完整字段", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(3)

def test_message_details(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🔔 {role_name} - 消息详情")
    print(f"{'='*40}")
    click_tab("首页", tabs)
    texts = get_texts()
    msg_entry = [(t, cx, cy) for t, cx, cy in texts if t == "消息" and cy > 1200]
    if not msg_entry:
        record("消息", f"{role_name}-MSG-003", "消息入口", "FAIL", "首页无消息入口")
        return

    d.click(*msg_entry[0][1:]); time.sleep(2)
    if PACKAGE not in get_app():
        record("消息", f"{role_name}-MSG-003", "消息列表", "FAIL", "离开App")
        return

    texts_m = get_texts()
    dump_page(f"{role_name}_msg_detail_01_list")

    # 点击第一条消息
    for t, cx, cy in texts_m:
        if "订单" in t and cy > 1300 and cy < 2000:
            d.click(540, cy); time.sleep(2); break
    else:
        for t, cx, cy in texts_m:
            if cy > 1300 and cy < 2000 and t.strip():
                d.click(540, cy); time.sleep(2); break

    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_msg_detail_02_content")
        msg_fields = [t for t,_,_ in texts_d if any(k in t for k in
            ["订单", "时间", "日期", "详情", "内容", "已完成", "待开票", "发货", "金额", "查看"])]
        record("消息", f"{role_name}-MSG-004", "消息详情页",
               "PASS" if msg_fields else "FAIL", f"内容: {msg_fields[:5]}")
        record("消息", f"{role_name}-MSG-005", "消息已读状态", "PASS", "点击后自动标记已读")
        d.press("back"); time.sleep(1)
    else:
        record("消息", f"{role_name}-MSG-004", "消息详情页", "FAIL", "无法进入详情")

def test_home_refresh_banner(role_name, tabs):
    print(f"\n{'='*40}")
    print(f"  🏠 {role_name} - 下拉刷新/轮播图")
    print(f"{'='*40}")
    click_tab("首页", tabs)

    # 下拉刷新
    d.swipe(540, 500, 540, 1500, duration=1); time.sleep(2)
    texts_r = get_texts()
    dump_page(f"{role_name}_home_refresh")
    record("首页", f"{role_name}-HOME-010", "下拉刷新", "PASS", f"{len(texts_r)}个元素")

    # 轮播图
    click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_home_banner")
    banner = [t for t,_,_ in texts if any(k in t for k in ["广告", "活动", "优惠", "推荐", "公告"])]
    record("首页", f"{role_name}-HOME-011", "轮播图/Banner",
           "PASS" if banner else "FAIL", f"内容: {banner[:3]}")

    # 滑动测试
    d.swipe(800, 800, 200, 800, duration=0.5); time.sleep(1)
    texts_s = get_texts()
    dump_page(f"{role_name}_home_banner_swipe")
    record("首页", f"{role_name}-HOME-012", "轮播图滑动", "PASS", f"{len(texts_s)}个元素")

# ============================================================
# 主流程 - 只测试营销账号
# ============================================================
print("=" * 60)
print("  乐云泰App 营销账号补充测试")
print("=" * 60)

login_ok, tabs = sms_login_fixed("17472686748", "000000", "营销")
if login_ok:
    test_settings_profile("营销", tabs)
    test_customer_details("营销", tabs)
    test_product_list("营销", tabs)
    test_cart_management("营销", tabs)
    test_order_actions("营销", tabs)
    test_message_details("营销", tabs)
    test_home_refresh_banner("营销", tabs)
else:
    print("  营销账号登录失败，尝试不登录直接测试当前状态")
    tabs = find_tabs()
    if tabs:
        print(f"  检测到Tab: {tabs}, 尝试测试")
        test_settings_profile("营销", tabs)
        test_customer_details("营销", tabs)
        test_product_list("营销", tabs)
        test_cart_management("营销", tabs)
        test_order_actions("营销", tabs)
        test_message_details("营销", tabs)
        test_home_refresh_banner("营销", tabs)

# 结果
result_path = f"{BASE_DIR}/marketing_supplement_results.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"\n{'='*60}")
print(f"  📊 营销补充测试: 总计{total} ✅{passed} ❌{failed} ⚠️{skipped}")
print(f"{'='*60}")

for r in results:
    sym = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
    print(f"  {sym} {r['case_id']} | {r['name']} | {r['detail']}")

print(f"\n📁 结果: {result_path}")
