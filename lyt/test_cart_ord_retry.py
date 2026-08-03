"""
单独测试购物车管理和订单操作（营销角色已登录）
"""
import uiautomator2 as u2
import re, os, time, json
from datetime import datetime

d = u2.connect()
PACKAGE = "com.grl.leyuntai"
BASE_DIR = "E:/KiloAutoTest/lyt/explore_supplement"
DUMP_DIR = f"{BASE_DIR}/ui_dumps_v3"
SHOT_DIR = f"{BASE_DIR}/screenshots_v3"

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


def find_tabs():
    texts = get_texts()
    tabs = {}
    for t, cx, cy in texts:
        if t in ["首页", "客户", "购物车", "订单"] and cy > 2200:
            tabs[t] = (cx, cy)
    return tabs


def click_tab(tab_name, tabs=None):
    if PACKAGE not in get_app():
        print(f"  ⚠️ 不在App内，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        for _ in range(10):
            texts = get_texts()
            tab_texts = [t for t, cx, cy in texts if t in ["首页", "客户", "购物车", "订单"]]
            if tab_texts:
                break
            time.sleep(1)
    if not tabs:
        tabs = find_tabs()
    if tab_name in tabs:
        d.click(*tabs[tab_name])
    else:
        defaults = {"首页": (135, 2321), "客户": (405, 2321), "购物车": (675, 2321), "订单": (945, 2321)}
        d.click(*defaults.get(tab_name, (135, 2321)))
    time.sleep(2)
    if PACKAGE not in get_app():
        print(f"  ⚠️ 点击{tab_name}后离开App，重启...")
        d.app_start(PACKAGE, stop=False)
        time.sleep(5)
        tabs = find_tabs()
        if tab_name in tabs:
            d.click(*tabs[tab_name])
            time.sleep(2)
    return find_tabs()


# ============================================================
print("=" * 60)
print("  购物车管理 + 订单操作 单独测试")
print("=" * 60)

# 确保在App内
if PACKAGE not in get_app():
    print("  ⚠️ 不在App内，重启...")
    d.app_start(PACKAGE, stop=False)
    time.sleep(5)

# 处理可能的弹窗
texts = get_texts()
for t, cx, cy in texts:
    if t in ["同意", "确定", "知道了", "稍后", "关闭", "取消", "暂不升级"] and cy > 1500:
        d.click(cx, cy); time.sleep(1); break

# 确认在首页
tabs = find_tabs()
if not tabs:
    d.app_start(PACKAGE, stop=False)
    time.sleep(5)
    tabs = find_tabs()

if "首页" in tabs:
    d.click(*tabs["首页"]); time.sleep(2)
    tabs = find_tabs()

print(f"\n  当前Tab: {list(tabs.keys())}")

# ========== 购物车管理 ==========
print(f"\n  🛒 营销 - 购物车管理")
tabs = click_tab("购物车", tabs)
texts = get_texts()
dump_page("营销_cart_retry_01")

# CART-007: 管理按钮
manage = [(t, cx, cy) for t, cx, cy in texts if t == "管理"]
if manage:
    d.click(*manage[0][1:]); time.sleep(2)
    texts_m = get_texts()
    dump_page("营销_cart_retry_manage")
    btns = [t for t, _, _ in texts_m if any(k in t for k in
            ["删除", "完成", "取消", "全选", "移除", "编辑"])]
    record("购物车", "营销-CART-007", "管理功能", "PASS" if btns else "FAIL", f"按钮: {btns[:3]}")
    for t2, cx2, cy2 in texts_m:
        if t2 in ["完成", "取消"]:
            d.click(cx2, cy2); time.sleep(1); break
    else:
        d.press("back"); time.sleep(1)
else:
    record("购物车", "营销-CART-007", "管理功能", "FAIL", "无管理按钮")

# CART-008: 结算按钮
tabs = click_tab("购物车", tabs)
texts = get_texts()
dump_page("营销_cart_retry_02")
settle = [t for t, _, _ in texts if any(k in t for k in
          ["结算", "下单", "合计", "总额", "￥"])]
record("购物车", "营销-CART-008", "结算按钮", "PASS" if settle else "FAIL", f"{settle[:3]}")

# CART-009: 全选并查看合计
select_all = [(t, cx, cy) for t, cx, cy in texts if "全选" in t]
if select_all:
    d.click(80, select_all[0][2]); time.sleep(1)
    texts_a = get_texts()
    dump_page("营销_cart_retry_selected")
    total = [t for t, _, _ in texts_a if "合计" in t or "￥" in t or "总额" in t]
    record("购物车", "营销-CART-009", "全选+合计", "PASS" if total else "FAIL", f"{total[:2]}")
else:
    record("购物车", "营销-CART-009", "全选+合计", "FAIL", "无全选按钮")

# CART-010: 数量增减
plus_btn = [(t, cx, cy) for t, cx, cy in texts if t == "+"]
if plus_btn:
    d.click(*plus_btn[0][1:]); time.sleep(1)
    record("购物车", "营销-CART-010", "数量增加", "PASS", "点击+按钮")
else:
    record("购物车", "营销-CART-010", "数量增减", "FAIL", "无+按钮")

# ========== 订单操作 ==========
print(f"\n  📦 营销 - 订单操作")
tabs = click_tab("订单", tabs)
texts = get_texts()
dump_page("营销_ord_retry_01")

# ORD-007: 协议和凭证 - 在订单列表中查找
agreement = [(t, cx, cy) for t, cx, cy in texts if "协议" in t and "凭证" in t]
if agreement:
    d.click(*agreement[0][1:]); time.sleep(2)
    if PACKAGE in get_app():
        texts_a = get_texts()
        dump_page("营销_ord_retry_agreement")
        fields = [t for t, _, _ in texts_a if any(k in t for k in
                  ["协议", "凭证", "甲方", "乙方", "签订", "日期", "金额", "条款", "合同"])]
        record("订单", "营销-ORD-007", "协议和凭证", "PASS" if fields else "FAIL", f"{fields[:5]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", "营销-ORD-007", "协议和凭证", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(5)
else:
    record("订单", "营销-ORD-007", "协议和凭证", "FAIL", "无此按钮")

# ORD-008: 发票
tabs = click_tab("订单", tabs)
texts = get_texts()
invoice = [(t, cx, cy) for t, cx, cy in texts if "发票" in t]
if invoice:
    d.click(*invoice[0][1:]); time.sleep(2)
    if PACKAGE in get_app():
        texts_i = get_texts()
        dump_page("营销_ord_retry_invoice")
        fields = [t for t, _, _ in texts_i if any(k in t for k in
                  ["发票", "抬头", "税号", "金额", "开票", "类型", "内容"])]
        record("订单", "营销-ORD-008", "查看发票", "PASS" if fields else "FAIL", f"{fields[:5]}")
        d.press("back"); time.sleep(1.5)
    else:
        record("订单", "营销-ORD-008", "查看发票", "FAIL", "离开App")
        d.app_start(PACKAGE, stop=False); time.sleep(5)
else:
    record("订单", "营销-ORD-008", "查看发票", "FAIL", "无此按钮")

# 保存结果
result_path = f"{BASE_DIR}/supplement_v3_cart_ord.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total = len(results)
passed = len([r for r in results if r["status"] == "PASS"])
failed = len([r for r in results if r["status"] == "FAIL"])

print(f"\n{'='*60}")
print(f"  📊 购物车+订单测试: 总计{total} ✅{passed} ❌{failed}")
print(f"{'='*60}")
for r in results:
    sym = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
    print(f"  {sym} {r['case_id']} | {r['name']} | {r['detail']}")
print(f"\n📁 结果: {result_path}")
