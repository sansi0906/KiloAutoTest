"""
乐云台 App - 全面功能测试脚本
覆盖购物车、下单流程、设备详情、订单详情等所有按钮和交互
"""
import uiautomator2 as u2
import time
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

PACKAGE = "com.grl.leyuntai"
DINGTALK = "com.alibaba.android.rimet"

TAB_HOME = (135, 2256)
TAB_CUSTOMER = (405, 2256)
TAB_CART = (675, 2256)
TAB_ORDER = (945, 2256)
MY_BUTTON = (1011, 138)

issues = []
test_count = 0
pass_count = 0

def log_issue(module, description, severity="中", detail="", reproduce=""):
    issue = {
        "序号": len(issues) + 1,
        "模块": module,
        "问题": description,
        "严重程度": severity,
        "详情": detail,
        "复现步骤": reproduce,
        "时间": datetime.now().strftime("%H:%M:%S")
    }
    issues.append(issue)
    print(f"  ❌ #{issue['序号']} [{module}] {description} ({severity})", flush=True)
    if detail:
        print(f"     详情: {detail}", flush=True)

def log_test(name, passed, detail=""):
    global test_count, pass_count
    test_count += 1
    if passed:
        pass_count += 1
        print(f"  ✅ {name}", flush=True)
    else:
        print(f"  ❌ {name}", flush=True)
    if detail:
        print(f"     {detail}", flush=True)

print("连接设备...", flush=True)
d = u2.connect()
d.implicitly_wait(10.0)
print(f"✓ 设备: {d.info.get('productName', 'unknown')}", flush=True)

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "full_test_results")
os.makedirs(screenshot_dir, exist_ok=True)

def restart_app():
    """重启App确保状态干净"""
    current = d.app_current()
    if current.get('package') == DINGTALK:
        d.app_stop(DINGTALK)
        time.sleep(1)
    d.app_start(PACKAGE, stop=True)
    time.sleep(4)
    d.click(*TAB_HOME)
    time.sleep(2)

def get_texts():
    xml = d.dump_hierarchy()
    texts = re.findall(r'text="([^"]*)"', xml)
    return [t for t in texts if t.strip()]

def screenshot(name):
    d.screenshot(os.path.join(screenshot_dir, f"{name}.png"))

def has_text(keyword):
    texts = get_texts()
    return any(keyword in t for t in texts)

def click_text(keyword, exact=False):
    """点击包含关键词的文本"""
    try:
        if exact:
            if d(text=keyword).exists(timeout=2):
                d(text=keyword).click()
                return True
        else:
            if d(textContains=keyword).exists(timeout=2):
                d(textContains=keyword).click()
                return True
    except:
        pass
    return False

# ============================================================
# 测试1: 购物车 - 全选/取消全选/管理/删除
# ============================================================
print("\n" + "="*60, flush=True)
print("测试1: 购物车 - 全选/取消全选/管理/删除", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)
screenshot("01_cart_initial")

# 1.1 测试全选
print("\n--- 1.1 测试全选 ---", flush=True)
initial_texts = get_texts()
initial_total = next((t for t in initial_texts if "0.00" in t), "未知")
print(f"  初始合计: {initial_total}", flush=True)

# 点击全选
if click_text("全选"):
    time.sleep(1)
    after_select_texts = get_texts()
    after_total = next((t for t in after_select_texts if "0.00" in t or "￥" in t), "未知")
    
    # 检查合计是否变化
    has_amount = any(("￥" in t and "0.00" not in t) for t in after_select_texts)
    log_test("全选后合计金额变化", has_amount, f"全选后: {after_total}")
    
    if not has_amount:
        log_issue("购物车", "全选后合计金额仍为0", "高", 
                 "点击全选按钮后，合计金额应该显示选中商品的总价",
                 "进入购物车 → 点击全选 → 查看合计")

# 1.2 测试取消全选
print("\n--- 1.2 测试取消全选 ---", flush=True)
if click_text("全选"):
    time.sleep(1)
    after_deselect = get_texts()
    has_zero = any("0.00" in t for t in after_deselect)
    log_test("取消全选后合计归零", has_zero)
    
    if not has_zero:
        log_issue("购物车", "取消全选后合计未归零", "中",
                 "再次点击全选按钮应取消选中，合计应归零",
                 "购物车 → 全选 → 再次点击全选 → 查看合计")

# 1.3 测试管理按钮
print("\n--- 1.3 测试管理按钮 ---", flush=True)
if click_text("管理"):
    time.sleep(1)
    screenshot("02_cart_manage_mode")
    manage_texts = get_texts()
    
    # 管理模式下应出现"完成"或"删除"按钮
    has_complete = any("完成" in t for t in manage_texts)
    has_delete = any("删除" in t for t in manage_texts)
    
    log_test("管理模式显示完成按钮", has_complete)
    log_test("管理模式显示删除按钮", has_delete)
    
    if not has_complete and not has_delete:
        log_issue("购物车", "点击管理后无完成/删除按钮", "中",
                 "管理模式下应显示删除或完成按钮",
                 "购物车 → 点击管理 → 查看按钮变化")
    
    # 退出管理模式
    if has_complete:
        click_text("完成")
        time.sleep(1)

# 1.4 测试数量增减
print("\n--- 1.4 测试数量增减 ---", flush=True)
restart_app()
d.click(*TAB_CART)
time.sleep(3)

# 找到第一个商品的+按钮
plus_buttons = d(resourceId="image")
# 实际上+按钮是文本"+"
if d(text="+").exists(timeout=2):
    # 获取当前数量
    before_texts = get_texts()
    # 找到第一个数量值（在-和+之间）
    qty_index = -1
    for i, t in enumerate(before_texts):
        if t == "-":
            qty_index = i + 1
            break
    
    if qty_index > 0 and qty_index < len(before_texts):
        before_qty = before_texts[qty_index]
        print(f"  当前数量: {before_qty}", flush=True)
        
        # 点击+
        d(text="+").click()
        time.sleep(1)
        after_texts = get_texts()
        after_qty = after_texts[qty_index] if qty_index < len(after_texts) else "未知"
        
        log_test("点击+增加数量", before_qty != after_qty, f"{before_qty} → {after_qty}")
        
        # 点击-减少
        if d(text="-").exists(timeout=1):
            d(text="-").click()
            time.sleep(1)
            final_texts = get_texts()
            final_qty = final_texts[qty_index] if qty_index < len(final_texts) else "未知"
            log_test("点击-减少数量", after_qty != final_qty, f"{after_qty} → {final_qty}")
    else:
        log_test("找到商品数量", False, "无法定位数量文本")
else:
    log_test("找到+按钮", False)

# 1.5 测试数量减到0
print("\n--- 1.5 测试数量减到0的边界 ---", flush=True)
# 找到数量为1的商品，连续点-
minus_count = 0
for _ in range(10):
    if d(text="-").exists(timeout=1):
        d(text="-").click()
        time.sleep(0.5)
        minus_count += 1
    else:
        break

print(f"  连续点击- {minus_count} 次", flush=True)
screenshot("03_after_minus")

# 检查是否有提示或异常
after_minus_texts = get_texts()
has_toast = any("至少" in t or "不能" in t or "最小" in t for t in after_minus_texts)
log_test("数量减到最小时有提示", has_toast, "可能需要人工确认")

# ============================================================
# 测试2: 生成订单 - 客户订单完整流程
# ============================================================
print("\n" + "="*60, flush=True)
print("测试2: 生成订单 - 客户订单流程", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)

# 全选
click_text("全选")
time.sleep(1)

# 点击生成订单
print("\n--- 2.1 点击生成订单 ---", flush=True)
if click_text("生成订单"):
    time.sleep(2)
    screenshot("04_order_type_selection")
    
    log_test("进入订单类型选择", has_text("客户订单") and has_text("记录订单"))
    
    # 2.2 选择客户订单
    print("\n--- 2.2 选择客户订单 ---", flush=True)
    if click_text("客户订单"):
        time.sleep(2)
        screenshot("05_customer_order_form")
        
        order_texts = get_texts()
        print(f"  客户订单表单文本: {order_texts[:10]}", flush=True)
        
        # 检查表单元素
        log_test("显示选择客户入口", any("选择客户" in t for t in order_texts))
        log_test("显示发货选项", any("发货" in t for t in order_texts))
        log_test("显示需要发货选项", any("需要发货" in t for t in order_texts))
        log_test("显示无需发货选项", any("无需发货" in t for t in order_texts))
        log_test("显示商品列表", any("设备" in t or "建材" in t for t in order_texts))
        log_test("显示价格输入框", any("请输入价格" in t for t in order_texts))
        
        # 2.3 测试不选客户直接提交
        print("\n--- 2.3 测试不选客户直接提交 ---", flush=True)
        # 查找提交按钮
        submit_keywords = ["提交", "确认", "下一步", "生成"]
        found_submit = False
        for kw in submit_keywords:
            if d(textContains=kw).exists(timeout=1):
                d(textContains=kw).click()
                time.sleep(2)
                found_submit = True
                break
        
        if found_submit:
            after_submit_texts = get_texts()
            has_error = any(kw in t for t in after_submit_texts for kw in ["请选择", "不能为空", "提示", "错误"])
            log_test("未选客户提交有错误提示", has_error, f"提示: {[t for t in after_submit_texts if '请' in t or '不能' in t][:3]}")
            
            if not has_error:
                log_issue("下单流程", "未选客户可提交订单", "高",
                         "未选择客户时应阻止提交并给出提示",
                         "购物车 → 全选 → 生成订单 → 客户订单 → 不选客户 → 点提交")
        
        # 2.4 测试选择客户
        print("\n--- 2.4 测试选择客户 ---", flush=True)
        if click_text("选择客户"):
            time.sleep(2)
            screenshot("06_customer_selection")
            
            customer_texts = get_texts()
            print(f"  客户选择页文本: {customer_texts[:10]}", flush=True)
            
            log_test("进入客户选择页", any("客户" in t for t in customer_texts))
            
            # 检查是否有客户列表
            has_list = any("联系人" in t or "电话" in t for t in customer_texts)
            log_test("客户列表显示", has_list)
            
            # 选择第一个客户
            d.click(540, 400)
            time.sleep(2)
            
            after_select_customer = get_texts()
            print(f"  选择客户后文本: {after_select_customer[:10]}", flush=True)
            
            # 2.5 测试发货设置
            print("\n--- 2.5 测试发货设置 ---", flush=True)
            if any("需要发货" in t for t in after_select_customer):
                # 点击需要发货
                click_text("需要发货")
                time.sleep(1)
                screenshot("07_shipping_setting")
                
                shipping_texts = get_texts()
                log_test("发货设置显示", any("地址" in t or "收货" in t for t in shipping_texts))
                
                # 检查地址输入
                has_address = any("地址" in t for t in shipping_texts)
                log_test("显示收货地址", has_address)
            
            # 2.6 测试价格输入
            print("\n--- 2.6 测试价格输入 ---", flush=True)
            price_inputs = d(className="android.widget.EditText")
            if price_inputs.exists:
                count = price_inputs.count
                print(f"  找到 {count} 个输入框", flush=True)
                log_test("价格输入框存在", count > 0)
                
                # 尝试输入价格
                if count > 0:
                    try:
                        price_inputs[0].click()
                        time.sleep(0.5)
                        price_inputs[0].set_text("1000")
                        time.sleep(1)
                        screenshot("08_price_input")
                        log_test("价格输入成功", True)
                    except:
                        log_test("价格输入", False, "输入失败")
            else:
                log_test("价格输入框", False, "未找到输入框")

# ============================================================
# 测试3: 生成订单 - 记录订单流程
# ============================================================
print("\n" + "="*60, flush=True)
print("测试3: 生成订单 - 记录订单流程", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)
click_text("全选")
time.sleep(1)

if click_text("生成订单"):
    time.sleep(2)
    
    if click_text("记录订单"):
        time.sleep(2)
        screenshot("09_record_order_form")
        
        record_texts = get_texts()
        print(f"  记录订单表单: {record_texts[:10]}", flush=True)
        
        log_test("记录订单表单显示", len(record_texts) > 5)
        
        # 对比客户订单和记录订单的差异
        has_customer = any("选择客户" in t for t in record_texts)
        log_test("记录订单也需要选客户", has_customer)

# ============================================================
# 测试4: 设备详情页所有按钮
# ============================================================
print("\n" + "="*60, flush=True)
print("测试4: 设备详情页所有按钮", flush=True)
print("="*60)

restart_app()
d(text="设备").click()
time.sleep(2)

# 点击第一个商品
d.click(312, 600)
time.sleep(2)
screenshot("10_device_detail")

detail_texts = get_texts()
print(f"  设备详情文本: {detail_texts[:15]}", flush=True)

# 检查详情页元素
detail_checks = [
    ("商品图片", "图片"),
    ("商品名称", "设备"),
    ("商品价格", "元"),
    ("加入购物车", "加入购物车"),
    ("拨打电话", "拨打电话"),
    ("收藏", "收藏"),
    ("分享", "分享"),
    ("立即购买", "立即购买"),
    ("商品描述", "描述"),
    ("规格参数", "规格"),
    ("店铺信息", "店铺"),
]

for name, keyword in detail_checks:
    found = any(keyword in t for t in detail_texts)
    if found:
        log_test(f"设备详情-{name}", True)
    else:
        if name in ["加入购物车", "拨打电话"]:
            log_test(f"设备详情-{name}", False, "关键按钮缺失")
            log_issue("设备详情", f"{name}按钮缺失", "高",
                     f"设备详情页应包含{name}按钮",
                     "首页 → 设备 → 点击商品 → 查看详情页")
        elif name in ["收藏", "分享", "立即购买"]:
            log_test(f"设备详情-{name}", False, "可选功能")
        else:
            log_test(f"设备详情-{name}", False)

# 测试收藏按钮
print("\n--- 4.1 测试收藏 ---", flush=True)
if d(text="收藏").exists(timeout=1):
    d(text="收藏").click()
    time.sleep(1)
    after_favorite = get_texts()
    has_favorited = any("已收藏" in t or "取消收藏" in t for t in after_favorite)
    log_test("收藏成功", has_favorited)

# 测试分享按钮
print("\n--- 4.2 测试分享 ---", flush=True)
if d(text="分享").exists(timeout=1):
    d(text="分享").click()
    time.sleep(1)
    after_share = get_texts()
    has_share_panel = any("微信" in t or "QQ" in t or "分享" in t for t in after_share)
    log_test("分享面板显示", has_share_panel)
    if has_share_panel:
        d.press("back")
        time.sleep(1)

# ============================================================
# 测试5: 订单详情所有操作按钮
# ============================================================
print("\n" + "="*60, flush=True)
print("测试5: 订单详情所有操作按钮", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)
screenshot("11_order_list")

order_texts = get_texts()
print(f"  订单列表文本: {order_texts[:15]}", flush=True)

# 检查订单Tab
order_tabs = ["全部", "待付款", "待发货", "待收货", "已完成", "客户订单", "记录订单"]
for tab in order_tabs:
    if any(tab in t for t in order_texts):
        log_test(f"订单Tab-{tab}", True)

# 遍历每个Tab
for tab in ["全部", "客户订单", "记录订单"]:
    if d(text=tab).exists(timeout=1):
        d(text=tab).click()
        time.sleep(2)
        screenshot(f"12_order_tab_{tab}")
        
        tab_texts = get_texts()
        
        # 点击第一个订单
        d.click(540, 500)
        time.sleep(2)
        screenshot(f"13_order_detail_{tab}")
        
        detail_texts = get_texts()
        print(f"\n  {tab} - 订单详情: {detail_texts[:10]}", flush=True)
        
        # 检查详情元素
        detail_checks = [
            "订单编号",
            "下单时间",
            "订单状态",
            "商品信息",
            "收货地址",
            "查看协议",
            "查看发票",
            "联系客户",
            "取消订单",
            "去支付",
            "确认收货",
            "再次购买",
            "评价",
        ]
        
        for check in detail_checks:
            if any(check in t for t in detail_texts):
                log_test(f"{tab}-{check}", True)
        
        # 检查是否有操作按钮
        action_buttons = ["取消订单", "去支付", "确认收货", "再次购买", "评价", "联系客户"]
        found_actions = [btn for btn in action_buttons if any(btn in t for t in detail_texts)]
        
        if not found_actions:
            log_issue("订单详情", f"{tab}订单无任何操作按钮", "中",
                     "订单详情页应有相关操作按钮",
                     f"订单 → {tab} → 点击订单 → 查看详情")
        
        d.press("back")
        time.sleep(1)

# ============================================================
# 测试6: 搜索功能
# ============================================================
print("\n" + "="*60, flush=True)
print("测试6: 搜索功能", flush=True)
print("="*60)

restart_app()
d(text="设备").click()
time.sleep(2)

# 测试搜索
search_input = d(className="android.widget.EditText")
if search_input.exists:
    search_input.click()
    time.sleep(0.5)
    search_input.set_text("测试")
    time.sleep(1)
    d.press("enter")
    time.sleep(2)
    screenshot("14_search_result")
    
    result_texts = get_texts()
    log_test("搜索功能可用", len(result_texts) > 0)
    
    # 检查空结果处理
    search_input.click()
    time.sleep(0.5)
    search_input.set_text("不存在的商品12345")
    time.sleep(1)
    d.press("enter")
    time.sleep(2)
    screenshot("15_search_empty")
    
    empty_texts = get_texts()
    has_empty_tip = any("暂无" in t or "没有" in t or "找不到" in t for t in empty_texts)
    log_test("空结果有提示", has_empty_tip)
    
    if not has_empty_tip:
        log_issue("搜索", "搜索无结果时无提示", "低",
                 "搜索不到商品时应显示'暂无结果'等提示",
                 "设备列表 → 搜索'不存在的商品' → 查看结果")

# ============================================================
# 测试7: 客户管理详细测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试7: 客户管理详细测试", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)
screenshot("16_customer_list")

customer_texts = get_texts()
print(f"  客户列表: {customer_texts[:15]}", flush=True)

# 测试状态Tab
status_tabs = ["全部", "待审核", "已入驻", "已驳回"]
for tab in status_tabs:
    if d(text=tab).exists(timeout=1):
        d(text=tab).click()
        time.sleep(1)
        screenshot(f"17_customer_{tab}")
        tab_texts = get_texts()
        log_test(f"客户Tab-{tab}", len(tab_texts) > 0)

# 测试手动录入
print("\n--- 7.1 测试手动录入客户 ---", flush=True)
if d(textContains="手动录入").exists(timeout=1):
    d(textContains="手动录入").click()
    time.sleep(2)
    screenshot("18_manual_input")
    
    input_texts = get_texts()
    print(f"  手动录入表单: {input_texts[:10]}", flush=True)
    
    # 检查表单字段
    form_fields = ["企业名称", "联系人", "联系电话", "公司地址", "营业执照", "信用代码"]
    for field in form_fields:
        has_field = any(field in t for t in input_texts)
        log_test(f"手动录入-{field}", has_field)
    
    # 测试空表单提交
    if d(text="提交").exists(timeout=1) or d(text="保存").exists(timeout=1) or d(text="确认").exists(timeout=1):
        for btn in ["提交", "保存", "确认"]:
            if d(text=btn).exists(timeout=1):
                d(text=btn).click()
                time.sleep(1)
                break
        
        after_submit = get_texts()
        has_validation = any("请" in t or "不能为空" in t for t in after_submit)
        log_test("空表单提交有验证", has_validation)
        
        if not has_validation:
            log_issue("客户管理", "空表单可提交", "高",
                     "手动录入客户时，空表单应被验证拦截",
                     "客户 → 手动录入 → 不填信息 → 点提交")
    
    d.press("back")
    time.sleep(1)

# 测试客户详情
print("\n--- 7.2 测试客户详情 ---", flush=True)
d.click(*TAB_CUSTOMER)
time.sleep(2)
d.click(312, 500)
time.sleep(2)
screenshot("19_customer_detail_full")

detail_texts = get_texts()
print(f"  客户详情: {detail_texts[:15]}", flush=True)

# 检查详情页所有元素
detail_fields = ["联系人", "联系电话", "信用代码", "营业执照", "公司地址", "企业名称"]
for field in detail_fields:
    has_field = any(field in t for t in detail_texts)
    log_test(f"客户详情-{field}", has_field)

# 检查操作按钮
action_buttons = ["拨打电话", "编辑", "删除", "编辑客户", "发消息", "分享"]
for btn in action_buttons:
    has_btn = any(btn in t for t in detail_texts)
    if has_btn:
        log_test(f"客户详情-{btn}", True)
    elif btn in ["拨打电话", "编辑"]:
        log_test(f"客户详情-{btn}", False, "重要功能缺失")
        if btn == "拨打电话":
            log_issue("客户详情", "缺少拨打电话按钮", "中",
                     "客户详情页应有一键拨号功能",
                     "客户 → 点击客户 → 查看详情")

# ============================================================
# 测试8: 我的页面详细测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试8: 我的页面详细测试", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
screenshot("20_my_page")

my_texts = get_texts()
print(f"  我的页面: {my_texts[:15]}", flush=True)

# 检查菜单项
menu_items = ["设置", "关于", "反馈", "个人中心", "账号管理", "退出登录", "帮助", "消息"]
for item in menu_items:
    has_item = any(item in t for t in my_texts)
    if has_item:
        log_test(f"我的-{item}", True)

# 测试设置
print("\n--- 8.1 测试设置 ---", flush=True)
if d(text="设置").exists(timeout=1):
    d(text="设置").click()
    time.sleep(2)
    screenshot("21_settings")
    
    setting_texts = get_texts()
    print(f"  设置页面: {setting_texts[:10]}", flush=True)
    
    # 检查设置项
    setting_items = ["通知", "缓存", "版本", "账号", "隐私", "关于"]
    for item in setting_items:
        has_item = any(item in t for t in setting_texts)
        log_test(f"设置-{item}", has_item)
    
    d.press("back")
    time.sleep(1)

# ============================================================
# 测试9: 边界情况
# ============================================================
print("\n" + "="*60, flush=True)
print("测试9: 边界情况", flush=True)
print("="*60)

# 9.1 测试快速切换Tab
print("\n--- 9.1 快速切换Tab ---", flush=True)
restart_app()
for _ in range(3):
    d.click(*TAB_HOME)
    time.sleep(0.3)
    d.click(*TAB_CUSTOMER)
    time.sleep(0.3)
    d.click(*TAB_CART)
    time.sleep(0.3)
    d.click(*TAB_ORDER)
    time.sleep(0.3)

time.sleep(2)
d.click(*TAB_HOME)
time.sleep(2)
screenshot("22_after_fast_switch")

home_stable = any("杨涛轩" in t or "营销333" in t for t in get_texts())
log_test("快速切换Tab后首页稳定", home_stable)

if not home_stable:
    log_issue("导航", "快速切换Tab后页面异常", "中",
             "快速切换Tab可能导致页面状态混乱",
             "快速点击首页/客户/购物车/订单Tab多次 → 回首页")

# 9.2 测试返回键
print("\n--- 9.2 测试返回键 ---", flush=True)
restart_app()
d(text="设备").click()
time.sleep(2)
d.press("back")
time.sleep(2)

back_to_home = any("杨涛轩" in t or "营销333" in t for t in get_texts())
log_test("从设备列表返回首页", back_to_home)

# 9.3 测试空购物车提示
print("\n--- 9.3 测试购物车状态 ---", flush=True)
restart_app()
d.click(*TAB_CART)
time.sleep(3)

cart_texts = get_texts()
has_items = any("元/台" in t or "元/吨" in t for t in cart_texts)
log_test("购物车有商品", has_items)

# ============================================================
# 汇总报告
# ============================================================
print("\n" + "="*60, flush=True)
print("测试汇总报告", flush=True)
print("="*60)

print(f"\n测试总数: {test_count}", flush=True)
print(f"通过: {pass_count}", flush=True)
print(f"失败: {test_count - pass_count}", flush=True)
print(f"通过率: {pass_count/test_count*100:.1f}%", flush=True)

print(f"\n发现问题: {len(issues)} 个", flush=True)

if issues:
    severity_order = {"高": 0, "中": 1, "低": 2}
    issues.sort(key=lambda x: severity_order.get(x["严重程度"], 99))
    
    for severity in ["高", "中", "低"]:
        group = [i for i in issues if i["严重程度"] == severity]
        if group:
            print(f"\n【{severity}】({len(group)}个)", flush=True)
            for issue in group:
                print(f"  #{issue['序号']} [{issue['模块']}] {issue['问题']}", flush=True)
                if issue['详情']:
                    print(f"      {issue['详情']}", flush=True)

# 保存报告
report = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "测试总数": test_count,
    "通过数": pass_count,
    "失败数": test_count - pass_count,
    "通过率": f"{pass_count/test_count*100:.1f}%",
    "问题数": len(issues),
    "问题列表": issues
}

with open(os.path.join(screenshot_dir, "full_test_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告: {os.path.join(screenshot_dir, 'full_test_report.json')}", flush=True)