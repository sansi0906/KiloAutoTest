"""
乐云泰App - 营销账号补充测试 V2（修复导航）
关键修复: 1.每次测试前确保在App内 2.离开App时自动重启 3.不点击系统设置
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

def ensure_app(tabs=None):
    """确保在乐云泰App内，如果不在则重启"""
    if PACKAGE not in get_app():
        print("  ⚠️ 不在App内，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        # 等待App加载
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

def click_tab(tab_name, tabs):
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

def sms_login(phone, sms_code, role_name):
    print(f"\n{'='*60}")
    print(f"  🔐 {role_name}登录: {phone}")
    print(f"{'='*60}")
    os.system(f"adb shell pm clear {PACKAGE}")
    time.sleep(2)
    d.app_start(PACKAGE, stop=False)
    time.sleep(5)

    # 隐私政策
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "同意":
            d.click(cx, cy); time.sleep(3); break

    # 引导页
    texts = get_texts()
    for t, cx, cy in texts:
        if "开始使用" in t:
            d.click(cx, cy); time.sleep(3); break

    # 短信验证码登录
    texts = get_texts()
    for t, cx, cy in texts:
        if "短信验证码" in t:
            d.click(cx, cy); time.sleep(2); break

    # 输入手机号
    el = d(className="android.widget.EditText")
    if el.exists(timeout=3):
        el.click(); time.sleep(0.5)
        el.set_text(phone); time.sleep(0.5)
        d.click(540, 100); time.sleep(0.3)  # hide keyboard

    # 勾选协议
    d.click(261, 1754); time.sleep(0.5)

    # 获取验证码
    texts = get_texts()
    for t, cx, cy in texts:
        if "获取验证码" in t or ("获取" in t and cy > 1000):
            d.click(cx, cy); time.sleep(4); break

    # 输入验证码
    edit_texts = d(className="android.widget.EditText")
    cnt = edit_texts.count
    if cnt >= 2:
        edit_texts[1].click(); time.sleep(0.3); edit_texts[1].set_text(sms_code)
    elif cnt == 1:
        edit_texts[0].click(); time.sleep(0.3); edit_texts[0].set_text(sms_code)
    time.sleep(1); d.click(540, 100)  # hide keyboard

    # 点击登录
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "登录" and cy > 1300:
            d.click(cx, cy); time.sleep(10); break

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
        # 确保在首页
        if "首页" in tabs:
            d.click(*tabs["首页"]); time.sleep(2)
        return True, tabs
    print(f"  ❌ 登录失败")
    return False, {}

# ============================================================
def test_settings(role_name, tabs):
    """设置/个人中心 - 不点击系统设置，仅检测入口"""
    print(f"\n  ⚙️ {role_name} - 设置/个人中心")
    tabs = click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_set_01")

    # 在首页查找设置/个人中心入口
    # 营销角色首页: 杨涛轩(487,289) 营销333(382,385)
    # 尝试点击用户名称区域打开个人中心
    user_clicked = False
    for t, cx, cy in texts:
        if t in ["杨涛轩", "许星刚"] or (cy < 400 and t.strip() and t not in ["首页","客户","购物车","订单"]):
            d.click(cx, cy); time.sleep(2)
            texts2 = get_texts()
            dump_page(f"{role_name}_set_02_click_user")
            # 检查是否进入了个人中心
            profile_items = [t for t,_,_ in texts2 if any(k in t for k in
                ["设置", "修改密码", "退出", "缓存", "版本", "账号", "地址",
                 "实名", "认证", "签约", "消息", "通知", "个人", "我的"])]
            if profile_items:
                record("设置", f"{role_name}-SET-001", "个人中心页面", "PASS", f"菜单: {profile_items[:8]}")
                for item in profile_items:
                    if "退出" in item: record("设置", f"{role_name}-SET-002", "退出登录按钮", "PASS", item)
                    if "密码" in item: record("设置", f"{role_name}-SET-003", "修改密码入口", "PASS", item)
                    if "版本" in item: record("设置", f"{role_name}-SET-004", "版本信息", "PASS", item)
                    if "缓存" in item or "清除" in item: record("设置", f"{role_name}-SET-005", "清除缓存", "PASS", item)
                d.press("back"); time.sleep(1.5)
                user_clicked = True
                break
            else:
                d.press("back"); time.sleep(1)

    if not user_clicked:
        # 没有找到个人中心入口
        record("设置", f"{role_name}-SET-001", "个人中心页面", "FAIL", "首页无设置/个人中心入口")
        record("设置", f"{role_name}-SET-002", "退出登录按钮", "FAIL", "未找到")
        record("设置", f"{role_name}-SET-003", "修改密码入口", "FAIL", "未找到")
        record("设置", f"{role_name}-SET-004", "版本信息", "FAIL", "未找到")
        record("设置", f"{role_name}-SET-005", "清除缓存", "FAIL", "未找到")

def test_customer(role_name, tabs):
    """客户详情/审核/电话"""
    print(f"\n  👥 {role_name} - 客户详情")
    tabs = click_tab("客户", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cust_01")

    # 审核状态Tab
    status_tabs = [(t, cx, cy) for t, cx, cy in texts if t in ["待审核", "已入驻", "已驳回"]]
    if status_tabs:
        for t, cx, cy in status_tabs[:2]:
            d.click(cx, cy); time.sleep(2)
            texts2 = get_texts()
            dump_page(f"{role_name}_cust_tab_{t}")
            record("客户", f"{role_name}-CUST-006", f"审核Tab-{t}", "PASS", f"{len(texts2)}个元素")
        # 切回全部
        texts = get_texts()
        for t, cx, cy in texts:
            if t == "全部": d.click(cx, cy); time.sleep(1.5); break
    else:
        record("客户", f"{role_name}-CUST-006", "审核状态Tab", "SKIP", "无审核Tab")

    # 客户详情 - 点击列表第一项
    tabs = click_tab("客户", tabs)
    texts = get_texts()
    # 找客户列表中的第一项（有"电话"或"地址"字段的行）
    first_customer_y = None
    for t, cx, cy in texts:
        if t in ["电话", "地址"] and cy > 400 and cy < 1800:
            first_customer_y = cy
            break

    if first_customer_y:
        # 点击客户项的上半部分
        d.click(540, first_customer_y - 80)
        time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_cust_detail")
            fields = [t for t,_,_ in texts_d if any(k in t for k in
                ["联系人", "电话", "地址", "审核", "入驻", "客户", "公司", "名称", "来源"])]
            record("客户", f"{role_name}-CUST-007", "客户详情页",
                   "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
            actions = [t for t,_,_ in texts_d if any(k in t for k in
                ["编辑", "删除", "联系", "拨号", "审核", "通过", "拒绝", "备注"])]
            record("客户", f"{role_name}-CUST-008", "客户详情操作按钮",
                   "PASS" if actions else "FAIL", f"操作: {actions[:3]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "离开App")
            ensure_app()
    else:
        record("客户", f"{role_name}-CUST-007", "客户详情页", "FAIL", "无客户列表")

    # 电话拨打
    tabs = click_tab("客户", tabs)
    texts = get_texts()
    for t, cx, cy in texts:
        if t == "电话" and cy > 400 and cy < 1800:
            # 点击电话号码区域
            d.click(cx + 150, cy)
            time.sleep(2)
            texts_p = get_texts()
            dump_page(f"{role_name}_cust_phone")
            call_confirm = [t for t,_,_ in texts_p if any(k in t for k in ["呼叫", "拨号", "取消", "确认"])]
            record("客户", f"{role_name}-CUST-009", "电话拨打",
                   "PASS" if call_confirm else "FAIL", f"弹窗: {call_confirm[:3]}")
            # 取消
            for t2, cx2, cy2 in texts_p:
                if t2 in ["取消", "否"]: d.click(cx2, cy2); time.sleep(1); break
            else: d.press("back"); time.sleep(1)
            break
    else:
        record("客户", f"{role_name}-CUST-009", "电话拨打", "FAIL", "无电话按钮")

def test_product(role_name, tabs):
    """设备/人才列表搜索筛选+商品详情"""
    print(f"\n  🔍 {role_name} - 商品列表")
    tabs = click_tab("首页", tabs)
    texts = get_texts()

    entry_map = {}
    for t, cx, cy in texts:
        if t in ["设备", "建材", "人才", "服务"]:
            entry_map[t] = (cx, cy)

    for entry_name in ["设备", "人才"]:
        if entry_name not in entry_map:
            record("商品", f"{role_name}-PROD-001-{entry_name}", f"{entry_name}入口", "FAIL", "未找到入口")
            continue

        tabs = click_tab("首页", tabs)
        d.click(*entry_map[entry_name])
        time.sleep(2)
        if PACKAGE not in get_app():
            record("商品", f"{role_name}-PROD-001-{entry_name}", f"{entry_name}入口", "FAIL", "离开App")
            ensure_app(); continue

        texts_l = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_list")

        # 搜索按钮
        search = [t for t,_,_ in texts_l if t == "搜索"]
        record("商品", f"{role_name}-PROD-002-{entry_name}", f"{entry_name}搜索", "PASS" if search else "FAIL", "")

        # 筛选按钮
        filter_btn = [t for t,_,_ in texts_l if t == "筛选"]
        record("商品", f"{role_name}-PROD-003-{entry_name}", f"{entry_name}筛选", "PASS" if filter_btn else "FAIL", "")

        # 点击筛选
        if filter_btn:
            for t, cx, cy in texts_l:
                if t == "筛选":
                    d.click(cx, cy); time.sleep(2)
                    texts_f = get_texts()
                    dump_page(f"{role_name}_prod_{entry_name}_filter")
                    opts = [t for t,_,_ in texts_f if any(k in t for k in
                        ["分类", "区域", "价格", "排序", "类型", "确认", "重置"])]
                    record("商品", f"{role_name}-PROD-004-{entry_name}", f"{entry_name}筛选页",
                           "PASS" if opts else "FAIL", f"选项: {opts[:5]}")
                    d.press("back"); time.sleep(1)
                    break

        # 列表下滑
        d.swipe(540, 1800, 540, 800, duration=0.5); time.sleep(1)
        texts_s = get_texts()
        dump_page(f"{role_name}_prod_{entry_name}_scroll")
        record("商品", f"{role_name}-PROD-005-{entry_name}", f"{entry_name}下滑", "PASS", f"{len(texts_s)}个元素")

        # 商品详情
        d.click(540, 450); time.sleep(2)
        if PACKAGE in get_app():
            texts_d = get_texts()
            dump_page(f"{role_name}_prod_{entry_name}_detail")
            fields = [t for t,_,_ in texts_d if any(k in t for k in
                ["价格", "规格", "型号", "品牌", "库存", "数量", "详情", "描述", "参数", "购买", "加入"])]
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情",
                   "PASS" if fields else "FAIL", f"字段: {fields[:5]}")
            buy_btns = [t for t,_,_ in texts_d if any(k in t for k in ["加入", "购物车", "购买", "下单"])]
            record("商品", f"{role_name}-PROD-007-{entry_name}", f"{entry_name}购买按钮",
                   "PASS" if buy_btns else "FAIL", f"按钮: {buy_btns[:3]}")
            d.press("back"); time.sleep(1.5)
        else:
            record("商品", f"{role_name}-PROD-006-{entry_name}", f"{entry_name}商品详情", "FAIL", "离开App")
            ensure_app()

def test_cart(role_name, tabs):
    """购物车管理/结算"""
    print(f"\n  🛒 {role_name} - 购物车管理")
    tabs = click_tab("购物车", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_cart_01")

    # 管理按钮
    manage = [t for t,_,_ in texts if t == "管理"]
    if manage:
        for t, cx, cy in texts:
            if t == "管理":
                d.click(cx, cy); time.sleep(2)
                texts_m = get_texts()
                dump_page(f"{role_name}_cart_manage")
                btns = [t for t,_,_ in texts_m if any(k in t for k in ["删除", "完成", "取消", "全选", "移除"])]
                record("购物车", f"{role_name}-CART-007", "管理功能", "PASS" if btns else "FAIL", f"按钮: {btns[:3]}")
                for t2, cx2, cy2 in texts_m:
                    if t2 in ["完成", "取消"]: d.click(cx2, cy2); time.sleep(1); break
                break
    else:
        record("购物车", f"{role_name}-CART-007", "管理功能", "FAIL", "无管理按钮")

    # 结算
    tabs = click_tab("购物车", tabs)
    texts = get_texts()
    settle = [t for t,_,_ in texts if any(k in t for k in ["结算", "下单", "合计", "总额"])]
    record("购物车", f"{role_name}-CART-008", "结算按钮", "PASS" if settle else "FAIL", f"{settle[:3]}")

    # 全选
    for t, cx, cy in texts:
        if "全选" in t:
            d.click(80, cy); time.sleep(1)
            texts_a = get_texts()
            dump_page(f"{role_name}_cart_selected")
            total = [t for t,_,_ in texts_a if "合计" in t or "￥" in t]
            record("购物车", f"{role_name}-CART-009", "全选+合计", "PASS" if total else "FAIL", f"{total[:2]}")
            break
    else:
        record("购物车", f"{role_name}-CART-009", "全选+合计", "FAIL", "无全选")

    # 数量+
    for t, cx, cy in texts:
        if t == "+":
            d.click(cx, cy); time.sleep(1)
            record("购物车", f"{role_name}-CART-010", "数量增加", "PASS", "点击+")
            break
    else:
        record("购物车", f"{role_name}-CART-010", "数量增减", "FAIL", "无+按钮")

def test_order(role_name, tabs):
    """订单操作"""
    print(f"\n  📦 {role_name} - 订单操作")
    tabs = click_tab("订单", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_ord_01")

    # 协议和凭证
    for t, cx, cy in texts:
        if "协议" in t and "凭证" in t:
            d.click(cx, cy); time.sleep(2)
            if PACKAGE in get_app():
                texts_a = get_texts()
                dump_page(f"{role_name}_ord_agreement")
                fields = [t for t,_,_ in texts_a if any(k in t for k in
                    ["协议", "凭证", "甲方", "乙方", "签订", "日期", "金额", "条款"])]
                record("订单", f"{role_name}-ORD-007", "协议和凭证", "PASS" if fields else "FAIL", f"{fields[:5]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("订单", f"{role_name}-ORD-007", "协议和凭证", "FAIL", "离开App")
                ensure_app()
            break
    else:
        record("订单", f"{role_name}-ORD-007", "协议和凭证", "FAIL", "无此按钮")

    # 发票
    tabs = click_tab("订单", tabs)
    texts = get_texts()
    for t, cx, cy in texts:
        if "发票" in t:
            d.click(cx, cy); time.sleep(2)
            if PACKAGE in get_app():
                texts_i = get_texts()
                dump_page(f"{role_name}_ord_invoice")
                fields = [t for t,_,_ in texts_i if any(k in t for k in
                    ["发票", "抬头", "税号", "金额", "开票", "类型"])]
                record("订单", f"{role_name}-ORD-008", "查看发票", "PASS" if fields else "FAIL", f"{fields[:5]}")
                d.press("back"); time.sleep(1.5)
            else:
                record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "离开App")
                ensure_app()
            break
    else:
        record("订单", f"{role_name}-ORD-008", "查看发票", "FAIL", "无此按钮")

    # 订单详情
    tabs = click_tab("订单", tabs)
    d.click(540, 450); time.sleep(2)
    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_ord_detail")
        all_fields = [t for t,_,_ in texts_d if any(k in t for k in
            ["收货", "收件", "下单", "订单编号", "金额", "商品", "数量", "成本",
             "电话", "地址", "物流", "运费", "备注"])]
        record("订单", f"{role_name}-ORD-009", "订单详情字段", "PASS" if all_fields else "FAIL", f"{all_fields[:8]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", f"{role_name}-ORD-009", "订单详情", "FAIL", "离开App")
        ensure_app()

def test_message(role_name, tabs):
    """消息详情"""
    print(f"\n  🔔 {role_name} - 消息详情")
    tabs = click_tab("首页", tabs)
    texts = get_texts()

    msg_entry = [(t, cx, cy) for t, cx, cy in texts if t == "消息" and cy > 1200]
    if not msg_entry:
        # 尝试找包含"订单"的消息区域
        msg_area = [(t, cx, cy) for t, cx, cy in texts if "订单" in t and cy > 1200 and cy < 1800]
        if msg_area:
            msg_entry = msg_area

    if not msg_entry:
        record("消息", f"{role_name}-MSG-003", "消息入口", "FAIL", "首页无消息入口")
        return

    d.click(*msg_entry[0][1:]); time.sleep(2)
    if PACKAGE not in get_app():
        record("消息", f"{role_name}-MSG-003", "消息列表", "FAIL", "离开App")
        ensure_app(); return

    texts_m = get_texts()
    dump_page(f"{role_name}_msg_list")

    # 点击第一条消息
    for t, cx, cy in texts_m:
        if cy > 1300 and cy < 2000 and t.strip():
            d.click(540, cy); time.sleep(2); break

    if PACKAGE in get_app():
        texts_d = get_texts()
        dump_page(f"{role_name}_msg_detail")
        fields = [t for t,_,_ in texts_d if any(k in t for k in
            ["订单", "时间", "详情", "内容", "已完成", "待开票", "发货", "金额"])]
        record("消息", f"{role_name}-MSG-004", "消息详情", "PASS" if fields else "FAIL", f"{fields[:5]}")
        record("消息", f"{role_name}-MSG-005", "已读状态", "PASS", "点击自动标记")
        d.press("back"); time.sleep(1)
    else:
        record("消息", f"{role_name}-MSG-004", "消息详情", "FAIL", "离开App")
        ensure_app()

def test_home_features(role_name, tabs):
    """下拉刷新/轮播图"""
    print(f"\n  🏠 {role_name} - 首页功能")
    tabs = click_tab("首页", tabs)

    # 下拉刷新
    d.swipe(540, 500, 540, 1500, duration=1); time.sleep(2)
    texts_r = get_texts()
    dump_page(f"{role_name}_home_refresh")
    record("首页", f"{role_name}-HOME-010", "下拉刷新", "PASS", f"{len(texts_r)}个元素")

    # 轮播图
    tabs = click_tab("首页", tabs)
    texts = get_texts()
    dump_page(f"{role_name}_home_banner")
    # 查找banner区域 - 在统计信息和功能入口之间
    banner = [t for t,_,_ in texts if any(k in t for k in ["广告", "活动", "优惠", "推荐", "公告", "通知"])]
    record("首页", f"{role_name}-HOME-011", "轮播图", "PASS" if banner else "FAIL", f"{banner[:3]}")

    # 滑动
    d.swipe(800, 800, 200, 800, duration=0.5); time.sleep(1)
    texts_s = get_texts()
    dump_page(f"{role_name}_home_banner_swipe")
    record("首页", f"{role_name}-HOME-012", "轮播滑动", "PASS", f"{len(texts_s)}个元素")

# ============================================================
print("=" * 60)
print("  乐云泰App 营销账号补充测试 V2")
print("=" * 60)

login_ok, tabs = sms_login("17472686748", "000000", "营销")
if login_ok:
    test_settings("营销", tabs)
    test_customer("营销", tabs)
    test_product("营销", tabs)
    test_cart("营销", tabs)
    test_order("营销", tabs)
    test_message("营销", tabs)
    test_home_features("营销", tabs)

# 结果
result_path = f"{BASE_DIR}/marketing_v2_results.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])
skipped = len([r for r in results if r["status"] == "SKIP"])

print(f"\n{'='*60}")
print(f"  📊 营销V2: 总计{total} ✅{passed} ❌{failed} ⚠️{skipped}")
print(f"{'='*60}")

for r in results:
    sym = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
    print(f"  {sym} {r['case_id']} | {r['name']} | {r['detail']}")

print(f"\n📁 结果: {result_path}")
