"""
深入测试2 - 修正第一轮的问题
1. 设备详情页正确进入
2. 订单不同状态的详情页
3. 客户详情（入驻状态的客户）
4. 快速切换Tab问题验证
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

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_test_results")
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

# ============================================================
# 测试1: 设备详情页 - 正确进入
# ============================================================
print("\n" + "="*60, flush=True)
print("测试1: 设备详情页（正确进入）", flush=True)
print("="*60)

restart_app()
d(text="设备").click()
time.sleep(2)
screenshot("01_device_list")

# 获取商品卡片位置 - 找到"加入购物车"按钮
if d(text="加入购物车").exists(timeout=2):
    # 找到第一个"加入购物车"按钮的位置
    elem = d(text="加入购物车")
    bounds = elem.info.get('bounds', {})
    print(f"  找到加入购物车按钮: {bounds}", flush=True)
    
    # 点击商品图片区域（在加入购物车按钮上方）
    # 商品图片应该在按钮上方约200像素
    if bounds:
        x = (bounds['left'] + bounds['right']) // 2
        y = bounds['top'] - 100  # 上移100像素点击商品
        print(f"  点击商品图片: ({x}, {y})", flush=True)
        d.click(x, y)
        time.sleep(3)
        screenshot("02_device_detail")
        
        detail_texts = get_texts()
        print(f"  设备详情文本: {detail_texts[:15]}", flush=True)
        
        # 检查是否进入了详情页（应有"设备详情"或"拨打电话"等）
        is_detail = any("设备详情" in t or "详情" in t for t in detail_texts)
        log_test("进入设备详情页", is_detail, f"文本: {detail_texts[:5]}")
        
        if is_detail:
            # 检查详情页元素
            detail_checks = [
                ("商品图片", "图片"),
                ("商品名称", "轮式"),
                ("商品价格", "元"),
                ("加入购物车", "加入购物车"),
                ("拨打电话", "拨打电话"),
                ("商品描述", "描述"),
                ("规格参数", "规格"),
                ("店铺信息", "店铺"),
                ("新旧程度", "新旧"),
                ("品牌", "品牌"),
                ("类目", "类目"),
                ("已售", "已售"),
                ("编号", "编号"),
                ("机械型号", "型号"),
            ]
            
            for name, keyword in detail_checks:
                found = any(keyword in t for t in detail_texts)
                log_test(f"详情-{name}", found)
            
            # 测试拨打电话
            print("\n--- 1.1 测试拨打电话 ---", flush=True)
            if d(text="拨打电话").exists(timeout=1):
                d(text="拨打电话").click()
                time.sleep(2)
                screenshot("03_call_dialog")
                
                call_texts = get_texts()
                print(f"  拨打电话弹窗: {call_texts[:10]}", flush=True)
                
                has_call_dialog = any("呼叫" in t or "拨打" in t or "取消" in t for t in call_texts)
                log_test("拨打电话弹窗显示", has_call_dialog)
                
                # 取消
                if d(text="取消").exists(timeout=1):
                    d(text="取消").click()
                    time.sleep(1)
            
            # 测试加入购物车
            print("\n--- 1.2 测试加入购物车 ---", flush=True)
            if d(text="加入购物车").exists(timeout=1):
                d(text="加入购物车").click()
                time.sleep(2)
                screenshot("04_add_cart_result")
                
                after_cart = get_texts()
                has_success = any("成功" in t or "已加入" in t for t in after_cart)
                has_dialog = any("规格" in t or "数量" in t or "确定" in t for t in after_cart)
                log_test("加入购物车有反馈", has_success or has_dialog)
                
                # 关闭弹窗
                if d(text="确定").exists(timeout=1):
                    d(text="确定").click()
                    time.sleep(1)
                elif d(text="关闭").exists(timeout=1):
                    d(text="关闭").click()
                    time.sleep(1)

# ============================================================
# 测试2: 订单详情 - 不同状态
# ============================================================
print("\n" + "="*60, flush=True)
print("测试2: 订单详情（不同状态）", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)
screenshot("05_order_list")

# 获取所有订单状态
order_texts = get_texts()
print(f"  订单列表: {order_texts[:15]}", flush=True)

# 查找所有状态
statuses = []
for t in order_texts:
    if t in ["已完成", "待付款", "待发货", "待收货", "草稿", "待确认", "已取消"]:
        statuses.append(t)
print(f"  订单状态: {statuses}", flush=True)

# 滚动查看更多订单
d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
time.sleep(1)
more_texts = get_texts()
for t in more_texts:
    if t in ["已完成", "待付款", "待发货", "待收货", "草稿", "待确认", "已取消"] and t not in statuses:
        statuses.append(t)

print(f"  所有状态: {statuses}", flush=True)

# 点击不同状态的订单
d.click(*TAB_ORDER)
time.sleep(2)

# 尝试找到草稿/待确认状态的订单（这些可能有操作按钮）
for target_status in ["草稿", "待确认", "待付款", "待发货", "待收货"]:
    if any(target_status in t for t in get_texts()):
        print(f"\n  查找 {target_status} 订单...", flush=True)
        # 点击该状态附近的订单
        # 找到状态文本的位置
        elem = d(text=target_status)
        if elem.exists:
            info = elem.info
            bounds = info.get('bounds', {})
            if bounds:
                # 点击该订单卡片
                x = 540
                y = (bounds['top'] + bounds['bottom']) // 2
                print(f"  点击订单 ({x}, {y})", flush=True)
                d.click(x, y)
                time.sleep(2)
                screenshot(f"06_order_{target_status}")
                
                detail_texts = get_texts()
                print(f"  {target_status}订单详情: {detail_texts[:10]}", flush=True)
                
                # 检查操作按钮
                action_buttons = ["取消订单", "去支付", "确认收货", "再次购买", "评价", "编辑", "删除", "提交", "发送", "上传协议"]
                found_actions = [btn for btn in action_buttons if any(btn in t for t in detail_texts)]
                
                log_test(f"{target_status}订单有操作按钮", len(found_actions) > 0, f"按钮: {found_actions}")
                
                if found_actions:
                    print(f"  ✓ 找到操作按钮: {found_actions}", flush=True)
                else:
                    log_issue("订单详情", f"{target_status}订单无操作按钮", "中",
                             f"{target_status}状态的订单应有相关操作按钮",
                             f"订单 → 找{target_status}订单 → 点击查看详情")
                
                d.press("back")
                time.sleep(1)
                break

# ============================================================
# 测试3: 客户详情 - 入驻客户
# ============================================================
print("\n" + "="*60, flush=True)
print("测试3: 客户详情（入驻客户）", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)

# 点击"已入驻"Tab
if d(text="已入驻").exists(timeout=1):
    d(text="已入驻").click()
    time.sleep(2)
    screenshot("07_customer入驻")
    
    customer_texts = get_texts()
    print(f"  入驻客户列表: {customer_texts[:10]}", flush=True)
    
    # 点击第一个客户
    d.click(540, 400)
    time.sleep(2)
    screenshot("08_customer_detail入驻")
    
    detail_texts = get_texts()
    print(f"  入驻客户详情: {detail_texts[:15]}", flush=True)
    
    # 检查详情元素
    detail_fields = ["联系人", "联系电话", "企业名称", "公司地址", "营业执照", "信用代码"]
    for field in detail_fields:
        has_field = any(field in t for t in detail_texts)
        log_test(f"入驻客户-{field}", has_field)
    
    # 检查操作按钮
    action_buttons = ["拨打电话", "编辑", "发消息", "分享", "删除"]
    for btn in action_buttons:
        has_btn = any(btn in t for t in detail_texts)
        if has_btn:
            log_test(f"入驻客户详情-{btn}", True)
        elif btn == "拨打电话":
            log_test(f"入驻客户详情-{btn}", False, "重要功能缺失")
            log_issue("客户详情", "入驻客户也缺少拨打电话按钮", "中",
                     "入驻客户详情页应有一键拨号功能",
                     "客户 → 已入驻 → 点击客户 → 查看详情")
    
    # 检查拨打电话的实际位置
    print("\n--- 3.1 查找拨打电话入口 ---", flush=True)
    # 也许拨打电话是图标按钮，不是文本
    xml = d.dump_hierarchy()
    
    # 查找所有可点击的ImageView
    clickables = re.findall(
        r'<node[^>]*clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*class="([^"]*)"',
        xml
    )
    
    print(f"  可点击元素: {len(clickables)} 个", flush=True)
    for x1, y1, x2, y2, cls in clickables[:10]:
        center_x = (int(x1) + int(x2)) // 2
        center_y = (int(y1) + int(y2)) // 2
        print(f"    ({center_x}, {center_y}) {cls}", flush=True)
    
    # 查找电话图标（通常在底部）
    for x1, y1, x2, y2, cls in clickables:
        center_y = (int(y1) + int(y2)) // 2
        if center_y > 1500:  # 底部区域
            center_x = (int(x1) + int(x2)) // 2
            print(f"  尝试点击底部按钮: ({center_x}, {center_y})", flush=True)
            d.click(center_x, center_y)
            time.sleep(2)
            
            after_click = get_texts()
            has_call = any("呼叫" in t or "拨打" in t or "电话" in t for t in after_click)
            if has_call:
                log_test("找到拨打电话入口（图标）", True, f"位置: ({center_x}, {center_y})")
                screenshot("09_call_found")
                
                # 取消
                if d(text="取消").exists(timeout=1):
                    d(text="取消").click()
                    time.sleep(1)
                break
    else:
        log_test("找到拨打电话入口", False, "未找到任何拨号入口")

# ============================================================
# 测试4: 快速切换Tab问题验证
# ============================================================
print("\n" + "="*60, flush=True)
print("测试4: 快速切换Tab问题验证", flush=True)
print("="*60)

restart_app()
time.sleep(2)

# 先记录首页状态
d.click(*TAB_HOME)
time.sleep(2)
initial_texts = get_texts()
print(f"  初始首页: {[t for t in initial_texts if '杨涛轩' in t or '营销' in t][:2]}", flush=True)

# 快速切换
for _ in range(5):
    d.click(*TAB_CUSTOMER)
    time.sleep(0.2)
    d.click(*TAB_CART)
    time.sleep(0.2)
    d.click(*TAB_ORDER)
    time.sleep(0.2)
    d.click(*TAB_HOME)
    time.sleep(0.2)

time.sleep(3)
screenshot("10_after_fast_switch")

after_texts = get_texts()
is_home = any("杨涛轩" in t or "营销333" in t for t in after_texts)
log_test("快速切换后首页稳定", is_home)

if not is_home:
    print(f"  快速切换后页面: {after_texts[:10]}", flush=True)
    log_issue("导航", "快速切换Tab后页面状态异常", "中",
             "快速切换Tab可能导致页面状态混乱，无法回到首页",
             "快速点击客户/购物车/订单/首页Tab各5次 → 检查首页状态")

# ============================================================
# 测试5: 我的页面 - 深入测试
# ============================================================
print("\n" + "="*60, flush=True)
print("测试5: 我的页面 - 深入测试", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
screenshot("11_my_page_full")

my_texts = get_texts()
print(f"  我的页面: {my_texts[:20]}", flush=True)

# 检查所有菜单项
menu_items = ["公司资质", "意见反馈", "系统设置", "关于我们", "客服电话"]
for item in menu_items:
    has_item = any(item in t for t in my_texts)
    log_test(f"我的-{item}", has_item)

# 测试客服电话
if any("客服电话" in t for t in my_texts):
    print("\n--- 5.1 测试客服电话 ---", flush=True)
    if d(textContains="客服电话").exists(timeout=1):
        d(textContains="客服电话").click()
        time.sleep(2)
        screenshot("12_service_call")
        
        call_texts = get_texts()
        has_call_dialog = any("呼叫" in t or "拨打" in t or "4001150629" in t for t in call_texts)
        log_test("客服电话弹窗", has_call_dialog)
        
        if has_call_dialog:
            if d(text="取消").exists(timeout=1):
                d(text="取消").click()
                time.sleep(1)

# 测试系统设置
print("\n--- 5.2 测试系统设置 ---", flush=True)
if d(text="系统设置").exists(timeout=1):
    d(text="系统设置").click()
    time.sleep(2)
    screenshot("13_settings")
    
    setting_texts = get_texts()
    print(f"  设置页面: {setting_texts[:15]}", flush=True)
    
    # 检查设置项
    setting_items = ["缓存", "版本", "通知", "账号", "隐私", "退出", "清除", "关于"]
    for item in setting_items:
        has_item = any(item in t for t in setting_texts)
        log_test(f"设置-{item}", has_item)
    
    # 测试清除缓存
    if d(textContains="缓存").exists(timeout=1):
        print("\n  测试清除缓存...", flush=True)
        d(textContains="缓存").click()
        time.sleep(2)
        
        after_clear = get_texts()
        has_clear_result = any("已清除" in t or "清除成功" in t or "完成" in t for t in after_clear)
        log_test("清除缓存有反馈", has_clear_result)
    
    d.press("back")
    time.sleep(1)

# 测试公司资质
print("\n--- 5.3 测试公司资质 ---", flush=True)
d.click(*MY_BUTTON)
time.sleep(2)

if d(text="公司资质").exists(timeout=1):
    d(text="公司资质").click()
    time.sleep(2)
    screenshot("14_company_qualification")
    
    qual_texts = get_texts()
    print(f"  公司资质: {qual_texts[:10]}", flush=True)
    log_test("公司资质页面显示", len(qual_texts) > 3)
    
    d.press("back")
    time.sleep(1)

# ============================================================
# 测试6: 设备列表 - 筛选功能
# ============================================================
print("\n" + "="*60, flush=True)
print("测试6: 设备列表 - 筛选功能", flush=True)
print("="*60)

restart_app()
d(text="设备").click()
time.sleep(2)

# 测试筛选
if d(text="筛选").exists(timeout=1):
    d(text="筛选").click()
    time.sleep(2)
    screenshot("15_filter")
    
    filter_texts = get_texts()
    print(f"  筛选页面: {filter_texts[:15]}", flush=True)
    
    # 检查筛选项
    filter_options = ["价格", "品牌", "类目", "新旧", "地区", "排序"]
    for opt in filter_options:
        has_opt = any(opt in t for t in filter_texts)
        log_test(f"筛选-{opt}", has_opt)
    
    # 测试价格筛选
    if d(textContains="价格").exists(timeout=1):
        print("\n  测试价格筛选...", flush=True)
        # 可能需要选择价格区间
    
    d.press("back")
    time.sleep(1)

# 测试排序
if d(textContains="排序").exists(timeout=1):
    print("\n--- 6.1 测试排序 ---", flush=True)
    d(textContains="排序").click()
    time.sleep(1)
    screenshot("16_sort")
    
    sort_texts = get_texts()
    print(f"  排序选项: {sort_texts[:10]}", flush=True)
    
    sort_options = ["价格", "销量", "最新", "距离"]
    for opt in sort_options:
        has_opt = any(opt in t for t in sort_texts)
        log_test(f"排序-{opt}", has_opt)

# ============================================================
# 测试7: 购物车 - 删除商品
# ============================================================
print("\n" + "="*60, flush=True)
print("测试7: 购物车 - 删除商品流程", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)

# 记录商品数量
initial_texts = get_texts()
initial_items = len([t for t in initial_texts if "元/台" in t or "元/吨" in t])
print(f"  初始商品数: {initial_items}", flush=True)

# 进入管理模式
if d(text="管理").exists(timeout=1):
    d(text="管理").click()
    time.sleep(1)
    
    # 全选
    if d(text="全选").exists(timeout=1):
        d(text="全选").click()
        time.sleep(0.5)
    
    # 查找删除按钮
    if d(text="删除").exists(timeout=1):
        print("  找到删除按钮，但不实际删除（避免破坏数据）", flush=True)
        log_test("删除按钮可用", True)
        
        # 取消操作
        if d(text="完成").exists(timeout=1):
            d(text="完成").click()
            time.sleep(1)
    else:
        log_test("删除按钮", False, "未找到删除按钮")
        log_issue("购物车", "管理模式下无删除按钮", "中",
                 "管理模式下应显示删除按钮",
                 "购物车 → 管理 → 全选 → 查找删除按钮")

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60, flush=True)
print("深入测试汇总", flush=True)
print("="*60)

print(f"\n测试总数: {test_count}", flush=True)
print(f"通过: {pass_count}", flush=True)
print(f"失败: {test_count - pass_count}", flush=True)
print(f"通过率: {pass_count/test_count*100:.1f}%" if test_count > 0 else "无测试", flush=True)

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

with open(os.path.join(screenshot_dir, "deep_test_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告: {os.path.join(screenshot_dir, 'deep_test_report.json')}", flush=True)