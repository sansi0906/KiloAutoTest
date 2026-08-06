"""
乐云台 App - 下单流程深度测试
覆盖：实际提交、边界情况、表单交互、订单编辑、上传协议
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

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "order_deep_test")
os.makedirs(screenshot_dir, exist_ok=True)

def restart_app():
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
    return any(keyword in t for t in get_texts())

def find_and_click(keyword, exact=False):
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

def enter_order_flow():
    """进入下单流程：购物车→全选→生成订单"""
    restart_app()
    d.click(*TAB_CART)
    time.sleep(3)
    find_and_click("全选")
    time.sleep(1)
    if find_and_click("生成订单"):
        time.sleep(2)
        return True
    return False

# ============================================================
# 测试1: 客户订单 - 完整提交流程
# ============================================================
print("\n" + "="*60, flush=True)
print("测试1: 客户订单 - 完整提交流程", flush=True)
print("="*60)

if enter_order_flow():
    screenshot("01_order_type")
    log_test("进入订单类型选择", has_text("客户订单"))
    
    # 1.1 选择客户订单
    if find_and_click("客户订单"):
        time.sleep(2)
        screenshot("02_customer_order_form")
        log_test("进入客户订单表单", has_text("选择客户"))
        
        # 1.2 测试选择客户
        print("\n--- 1.2 选择客户 ---", flush=True)
        if find_and_click("选择客户"):
            time.sleep(2)
            screenshot("03_customer_select")
            
            customer_texts = get_texts()
            print(f"  客户选择页: {customer_texts[:8]}", flush=True)
            
            log_test("客户选择页显示", has_text("搜索"))
            
            # 检查客户列表
            has_customers = any("联系人" in t or "电话" in t for t in customer_texts)
            log_test("客户列表有数据", has_customers)
            
            # 点击第一个客户
            d.click(540, 400)
            time.sleep(2)
            screenshot("04_customer_selected")
            
            after_select = get_texts()
            # 检查是否选成功（应该回到表单页）
            log_test("选客户后返回表单", has_text("发货") or has_text("价格"))
            
            # 1.3 测试发货设置
            print("\n--- 1.3 测试发货设置 ---", flush=True)
            if has_text("需要发货"):
                find_and_click("需要发货")
                time.sleep(1)
                screenshot("05_shipping_on")
                
                shipping_texts = get_texts()
                print(f"  发货设置: {shipping_texts[:10]}", flush=True)
                
                # 检查发货相关字段
                has_address = any("地址" in t or "收货" in t for t in shipping_texts)
                log_test("需要发货-显示地址", has_address)
                
                if has_address:
                    # 尝试点击地址输入
                    if d(textContains="地址").exists(timeout=1):
                        d(textContains="地址").click()
                        time.sleep(2)
                        screenshot("06_address_input")
                        
                        addr_texts = get_texts()
                        log_test("地址输入页显示", len(addr_texts) > 3)
                        
                        # 检查地址选择方式
                        has_search = any("搜索" in t for t in addr_texts)
                        has_list = any("省" in t or "市" in t or "区" in t for t in addr_texts)
                        log_test("地址选择-搜索方式", has_search)
                        log_test("地址选择-列表方式", has_list)
                        
                        d.press("back")
                        time.sleep(1)
            
            # 测试无需发货
            if has_text("无需发货"):
                find_and_click("无需发货")
                time.sleep(1)
                screenshot("07_no_shipping")
                log_test("无需发货选项可用", True)
            
            # 1.4 测试价格输入
            print("\n--- 1.4 测试价格输入 ---", flush=True)
            price_inputs = d(className="android.widget.EditText")
            if price_inputs.exists:
                count = price_inputs.count
                print(f"  找到 {count} 个输入框", flush=True)
                
                # 输入价格
                for i in range(min(count, 4)):
                    try:
                        price_inputs[i].click()
                        time.sleep(0.3)
                        price_inputs[i].set_text("1000")
                        time.sleep(0.3)
                    except:
                        pass
                screenshot("08_price_filled")
                log_test("价格输入完成", True)
            
            # 1.5 测试提交
            print("\n--- 1.5 测试提交订单 ---", flush=True)
            submit_keywords = ["提交", "确认提交", "生成", "确认"]
            submitted = False
            for kw in submit_keywords:
                if d(textContains=kw).exists(timeout=1):
                    print(f"  找到提交按钮: '{kw}'", flush=True)
                    d(textContains=kw).click()
                    time.sleep(3)
                    submitted = True
                    break
            
            if submitted:
                screenshot("09_after_submit")
                after_submit = get_texts()
                print(f"  提交后文本: {after_submit[:10]}", flush=True)
                
                # 检查提交结果
                has_success = any("成功" in t or "完成" in t or "已提交" in t for t in after_submit)
                has_error = any("错误" in t or "失败" in t or "请" in t for t in after_submit)
                
                if has_success:
                    log_test("订单提交成功", True)
                elif has_error:
                    log_test("订单提交失败-有错误提示", False, f"提示: {[t for t in after_submit if '请' in t or '错误' in t][:3]}")
                else:
                    # 可能直接跳转到订单列表
                    has_order_list = any("订单" in t and ("全部" in t or "客户订单" in t) for t in after_submit)
                    log_test("订单提交后跳转", has_order_list, f"页面: {after_submit[:5]}")
            else:
                log_test("找到提交按钮", False, "未找到任何提交按钮")
                log_issue("下单流程", "客户订单表单无提交按钮", "高",
                         "填写完表单后找不到提交按钮",
                         "购物车→全选→生成订单→客户订单→选客户→填价格→查找提交按钮")

# ============================================================
# 测试2: 价格输入边界测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试2: 价格输入边界测试", flush=True)
print("="*60)

if enter_order_flow():
    find_and_click("客户订单")
    time.sleep(2)
    
    price_inputs = d(className="android.widget.EditText")
    if price_inputs.exists and price_inputs.count > 0:
        # 2.1 测试输入0
        print("\n--- 2.1 测试价格输入0 ---", flush=True)
        price_inputs[0].click()
        time.sleep(0.3)
        price_inputs[0].set_text("0")
        time.sleep(0.5)
        
        # 尝试提交
        if find_and_click("提交") or find_and_click("确认"):
            time.sleep(2)
            after_texts = get_texts()
            has_error = any("价格" in t and ("大于" in t or "不能" in t or "请输入" in t) for t in after_texts)
            log_test("价格0有验证", has_error, f"提示: {[t for t in after_texts if '价格' in t][:2]}")
            
            if not has_error:
                log_issue("下单流程", "价格输入0可提交", "高",
                         "价格为0时应被拦截",
                         "下单→价格输入0→提交")
        
        # 2.2 测试输入负数
        print("\n--- 2.2 测试价格输入负数 ---", flush=True)
        price_inputs[0].click()
        time.sleep(0.3)
        try:
            price_inputs[0].set_text("-100")
            time.sleep(0.5)
            screenshot("10_negative_price")
            
            after_input = get_texts()
            has_negative = any("-100" in t for t in after_input)
            log_test("负数价格输入", has_negative, "可能需要人工确认是否允许")
            
            if has_negative:
                log_issue("下单流程", "允许输入负数价格", "高",
                         "价格不应允许负数",
                         "下单→价格输入-100")
        except:
            log_test("负数价格输入", False, "输入失败（可能已限制）")
        
        # 2.3 测试输入超大数
        print("\n--- 2.3 测试价格输入超大数 ---", flush=True)
        price_inputs[0].click()
        time.sleep(0.3)
        price_inputs[0].set_text("999999999")
        time.sleep(0.5)
        screenshot("11_huge_price")
        
        after_huge = get_texts()
        has_huge = any("999999999" in t for t in after_huge)
        log_test("超大数价格输入", has_huge, "可能需要人工确认是否有上限")
        
        # 2.4 测试输入非数字
        print("\n--- 2.4 测试价格输入非数字 ---", flush=True)
        price_inputs[0].click()
        time.sleep(0.3)
        try:
            price_inputs[0].set_text("abc")
            time.sleep(0.5)
            after_abc = get_texts()
            has_abc = any("abc" in t for t in after_abc)
            log_test("非数字价格输入", not has_abc, "应限制非数字输入")
            
            if has_abc:
                log_issue("下单流程", "允许输入非数字价格", "高",
                         "价格应只允许数字",
                         "下单→价格输入abc")
        except:
            log_test("非数字价格输入", True, "已限制")

# ============================================================
# 测试3: 客户选择页搜索功能
# ============================================================
print("\n" + "="*60, flush=True)
print("测试3: 客户选择页搜索功能", flush=True)
print("="*60)

if enter_order_flow():
    find_and_click("客户订单")
    time.sleep(2)
    find_and_click("选择客户")
    time.sleep(2)
    screenshot("12_customer_search_page")
    
    # 3.1 测试搜索
    search_input = d(className="android.widget.EditText")
    if search_input.exists:
        search_input.click()
        time.sleep(0.3)
        search_input.set_text("测试")
        time.sleep(1)
        d.press("enter")
        time.sleep(2)
        screenshot("13_customer_search_result")
        
        result_texts = get_texts()
        log_test("客户搜索有结果", len(result_texts) > 3)
        
        # 3.2 测试空搜索结果
        search_input.click()
        time.sleep(0.3)
        search_input.set_text("不存在的客户12345")
        time.sleep(1)
        d.press("enter")
        time.sleep(2)
        screenshot("14_customer_search_empty")
        
        empty_texts = get_texts()
        has_empty_tip = any("暂无" in t or "没有" in t or "找不到" in t for t in empty_texts)
        log_test("空搜索结果有提示", has_empty_tip)
        
        if not has_empty_tip:
            log_issue("客户选择", "搜索无结果时无提示", "低",
                     "应显示'暂无匹配客户'",
                     "下单→选客户→搜索'不存在的客户'")
        
        # 3.3 清空搜索
        search_input.clear_text()
        time.sleep(1)
        d.press("enter")
        time.sleep(2)
        after_clear = get_texts()
        has_list = any("联系人" in t or "电话" in t for t in after_clear)
        log_test("清空搜索后恢复列表", has_list)

# ============================================================
# 测试4: 草稿订单编辑功能
# ============================================================
print("\n" + "="*60, flush=True)
print("测试4: 草稿订单编辑功能", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)

# 找草稿订单
order_texts = get_texts()
print(f"  订单列表: {order_texts[:15]}", flush=True)

# 滚动查找草稿订单
found_draft = False
for scroll_count in range(3):
    if "草稿" in str(order_texts):
        # 找到草稿订单
        elem = d(text="草稿")
        if elem.exists:
            info = elem.info
            bounds = info.get('bounds', {})
            if bounds:
                y = (bounds['top'] + bounds['bottom']) // 2
                d.click(540, y)
                time.sleep(2)
                screenshot("15_draft_order")
                found_draft = True
                break
    
    # 滚动
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)
    order_texts = get_texts()

if found_draft:
    draft_texts = get_texts()
    print(f"  草稿订单详情: {draft_texts[:10]}", flush=True)
    
    # 检查草稿订单的元素
    log_test("草稿订单显示编辑按钮", any("编辑" in t for t in draft_texts))
    log_test("草稿订单显示上传协议", any("上传协议" in t for t in draft_texts))
    
    # 4.1 测试编辑
    print("\n--- 4.1 测试编辑草稿订单 ---", flush=True)
    if find_and_click("编辑"):
        time.sleep(2)
        screenshot("16_edit_draft")
        
        edit_texts = get_texts()
        print(f"  编辑页面: {edit_texts[:10]}", flush=True)
        
        # 检查编辑页面元素
        log_test("编辑页显示订单信息", any("订单" in t for t in edit_texts))
        log_test("编辑页显示客户信息", any("客户" in t for t in edit_texts))
        log_test("编辑页显示商品信息", any("设备" in t or "建材" in t for t in edit_texts))
        
        # 检查编辑页的操作按钮
        edit_actions = ["保存", "提交", "取消", "删除", "放弃"]
        found_edit_actions = [a for a in edit_actions if any(a in t for t in edit_texts)]
        log_test("编辑页有操作按钮", len(found_edit_actions) > 0, f"按钮: {found_edit_actions}")
        
        if not found_edit_actions:
            log_issue("订单编辑", "编辑页无操作按钮", "中",
                     "编辑订单时应提供保存/取消按钮",
                     "订单→草稿→编辑→查找按钮")
    
    # 4.2 测试上传协议
    print("\n--- 4.2 测试上传协议 ---", flush=True)
    d.press("back")
    time.sleep(1)
    
    if find_and_click("上传协议"):
        time.sleep(2)
        screenshot("17_upload_agreement")
        
        upload_texts = get_texts()
        print(f"  上传协议页: {upload_texts[:10]}", flush=True)
        
        log_test("上传协议页显示", len(upload_texts) > 3)
        
        # 检查上传方式
        has_camera = any("拍照" in t for t in upload_texts)
        has_album = any("相册" in t or "图片" in t for t in upload_texts)
        has_file = any("文件" in t for t in upload_texts)
        
        log_test("支持拍照上传", has_camera)
        log_test("支持相册上传", has_album)
        log_test("支持文件上传", has_file)
        
        if not (has_camera or has_album or has_file):
            log_issue("上传协议", "无上传方式入口", "中",
                     "应提供拍照/相册等上传方式",
                     "订单→草稿→上传协议")
        
        d.press("back")
        time.sleep(1)
else:
    log_test("找到草稿订单", False, "订单列表中无草稿订单")
    print("  跳过草稿订单测试", flush=True)

# ============================================================
# 测试5: 发货设置详细测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试5: 发货设置详细测试", flush=True)
print("="*60)

if enter_order_flow():
    find_and_click("客户订单")
    time.sleep(2)
    find_and_click("选择客户")
    time.sleep(2)
    d.click(540, 400)  # 选客户
    time.sleep(2)
    
    # 5.1 测试需要发货
    print("\n--- 5.1 需要发货模式 ---", flush=True)
    if has_text("需要发货"):
        find_and_click("需要发货")
        time.sleep(1)
        screenshot("18_need_shipping")
        
        ship_texts = get_texts()
        
        # 检查发货相关字段
        ship_fields = ["收货人", "联系电话", "收货地址", "省", "市", "区"]
        for field in ship_fields:
            has_field = any(field in t for t in ship_texts)
            log_test(f"发货-{field}", has_field)
        
        # 检查是否有运费设置
        has_freight = any("运费" in t or "物流" in t for t in ship_texts)
        log_test("发货-运费设置", has_freight)
    
    # 5.2 测试无需发货
    print("\n--- 5.2 无需发货模式 ---", flush=True)
    if has_text("无需发货"):
        find_and_click("无需发货")
        time.sleep(1)
        screenshot("19_no_shipping")
        
        no_ship_texts = get_texts()
        
        # 无需发货时不应显示地址等字段
        has_address = any("收货地址" in t for t in no_ship_texts)
        log_test("无需发货-隐藏地址", not has_address, "无需发货时不应显示收货地址")
        
        if has_address:
            log_issue("发货设置", "无需发货仍显示收货地址", "低",
                     "选择无需发货后应隐藏收货地址字段",
                     "下单→选无需发货→检查地址字段")

# ============================================================
# 测试6: 记录订单流程
# ============================================================
print("\n" + "="*60, flush=True)
print("测试6: 记录订单完整流程", flush=True)
print("="*60)

if enter_order_flow():
    screenshot("20_record_order_type")
    
    if find_and_click("记录订单"):
        time.sleep(2)
        screenshot("21_record_order_form")
        
        record_texts = get_texts()
        print(f"  记录订单表单: {record_texts[:10]}", flush=True)
        
        # 对比客户订单和记录订单的差异
        log_test("记录订单-选择客户入口", has_text("选择客户"))
        log_test("记录订单-发货选项", has_text("发货"))
        log_test("记录订单-商品列表", has_text("设备") or has_text("建材"))
        log_test("记录订单-价格输入", has_text("请输入价格"))
        
        # 检查记录订单是否有特殊字段
        has_record_date = any("交易时间" in t or "成交时间" in t or "日期" in t for t in record_texts)
        log_test("记录订单-交易时间", has_record_date, "记录订单应记录实际交易时间")
        
        if not has_record_date:
            log_issue("记录订单", "缺少交易时间字段", "中",
                     "记录订单是记录已发生的交易，应有交易时间",
                     "下单→记录订单→检查表单字段")

# ============================================================
# 测试7: 购物车数量边界
# ============================================================
print("\n" + "="*60, flush=True)
print("测试7: 购物车数量边界测试", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)

# 7.1 测试数量增加到很大
print("\n--- 7.1 测试数量增加 ---", flush=True)
if d(text="+").exists(timeout=1):
    # 记录初始数量
    initial_texts = get_texts()
    for i, t in enumerate(initial_texts):
        if t == "-":
            initial_qty = initial_texts[i+1] if i+1 < len(initial_texts) else "?"
            print(f"  初始数量: {initial_qty}", flush=True)
            break
    
    # 连续点击+
    for _ in range(20):
        if d(text="+").exists(timeout=0.5):
            d(text="+").click()
            time.sleep(0.2)
    
    time.sleep(1)
    screenshot("22_max_quantity")
    after_plus = get_texts()
    
    for i, t in enumerate(after_plus):
        if t == "-":
            max_qty = after_plus[i+1] if i+1 < len(after_plus) else "?"
            print(f"  增加20次后数量: {max_qty}", flush=True)
            log_test("数量增加有效", max_qty != initial_qty)
            break

# 7.2 测试数量减到1
print("\n--- 7.2 测试数量减到最小 ---", flush=True)
if d(text="-").exists(timeout=1):
    for _ in range(20):
        if d(text="-").exists(timeout=0.5):
            d(text="-").click()
            time.sleep(0.2)
    
    time.sleep(1)
    screenshot("23_min_quantity")
    after_minus = get_texts()
    
    for i, t in enumerate(after_minus):
        if t == "-":
            min_qty = after_minus[i+1] if i+1 < len(after_minus) else "?"
            print(f"  减少20次后数量: {min_qty}", flush=True)
            log_test("数量最小限制为1", min_qty == "1", f"最终数量: {min_qty}")
            
            if min_qty != "1" and min_qty != "0":
                log_issue("购物车", f"数量减到{min_qty}而非1", "低",
                         "数量最小应为1",
                         "购物车→连续点-按钮")
            break

# ============================================================
# 测试8: 我的页面深入测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试8: 我的页面深入测试", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
screenshot("24_my_page")

my_texts = get_texts()
print(f"  我的页面: {my_texts[:20]}", flush=True)

# 检查营销账号特有功能
marketing_features = ["业绩排名", "销售额", "客户", "订单(笔)", "用户评价"]
for feat in marketing_features:
    has_feat = any(feat in t for t in my_texts)
    log_test(f"营销账号-{feat}", has_feat)

# 8.1 测试意见反馈
print("\n--- 8.1 测试意见反馈 ---", flush=True)
if find_and_click("意见反馈"):
    time.sleep(2)
    screenshot("25_feedback")
    
    feedback_texts = get_texts()
    print(f"  反馈页: {feedback_texts[:10]}", flush=True)
    
    log_test("反馈页显示", len(feedback_texts) > 3)
    
    # 检查反馈表单
    has_input = d(className="android.widget.EditText").exists
    log_test("反馈-输入框", has_input)
    
    has_type = any("类型" in t or "分类" in t for t in feedback_texts)
    log_test("反馈-类型选择", has_type)
    
    has_submit = any("提交" in t or "发送" in t for t in feedback_texts)
    log_test("反馈-提交按钮", has_submit)
    
    d.press("back")
    time.sleep(1)

# 8.2 测试关于我们
print("\n--- 8.2 测试关于我们 ---", flush=True)
d.click(*MY_BUTTON)
time.sleep(2)
if find_and_click("关于我们"):
    time.sleep(2)
    screenshot("26_about")
    
    about_texts = get_texts()
    print(f"  关于页: {about_texts[:10]}", flush=True)
    
    log_test("关于页显示", len(about_texts) > 3)
    
    # 检查关于页内容
    has_version = any("版本" in t for t in about_texts)
    has_company = any("公司" in t or "乐云台" in t for t in about_texts)
    log_test("关于-版本号", has_version)
    log_test("关于-公司信息", has_company)
    
    d.press("back")
    time.sleep(1)

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60, flush=True)
print("下单流程深度测试汇总", flush=True)
print("="*60)

print(f"\n测试总数: {test_count}", flush=True)
print(f"通过: {pass_count}", flush=True)
print(f"失败: {test_count - pass_count}", flush=True)
print(f"通过率: {pass_count/test_count*100:.1f}%" if test_count > 0 else "无测试", flush=True)

print(f"\n新发现问题: {len(issues)} 个", flush=True)

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

# 保存
report = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "测试总数": test_count,
    "通过数": pass_count,
    "失败数": test_count - pass_count,
    "通过率": f"{pass_count/test_count*100:.1f}%" if test_count > 0 else "0%",
    "问题数": len(issues),
    "问题列表": issues
}

with open(os.path.join(screenshot_dir, "order_deep_test_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告: {os.path.join(screenshot_dir, 'order_deep_test_report.json')}", flush=True)