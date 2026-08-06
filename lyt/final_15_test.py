"""
乐云台 App - 最后15个未测试按钮补充
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

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_15_test")
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

# ============================================================
# 测试1: 订单详情 - 查看协议和凭证
# ============================================================
print("\n" + "="*60, flush=True)
print("测试1: 订单详情 - 查看协议和凭证", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)

# 点击第一个订单
d.click(540, 500)
time.sleep(2)
screenshot("01_order_detail")

# 1.1 查看协议和凭证
print("\n--- 1.1 查看协议和凭证 ---", flush=True)
if d(text="查看协议和凭证").exists(timeout=1):
    d(text="查看协议和凭证").click()
    time.sleep(2)
    screenshot("02_agreement_proof")
    
    agreement_texts = get_texts()
    print(f"  协议和凭证页: {agreement_texts[:10]}", flush=True)
    
    log_test("协议和凭证页显示", len(agreement_texts) > 3)
    
    # 检查内容
    has_agreement = any("协议" in t for t in agreement_texts)
    has_proof = any("凭证" in t for t in agreement_texts)
    has_download = any("下载" in t for t in agreement_texts)
    has_image = d(className="android.widget.ImageView").exists
    
    log_test("协议和凭证-协议内容", has_agreement)
    log_test("协议和凭证-凭证内容", has_proof)
    log_test("协议和凭证-下载功能", has_download)
    log_test("协议和凭证-图片显示", has_image)
    
    if not has_agreement and not has_proof:
        log_issue("订单详情", "查看协议和凭证无内容", "中",
                 "应显示协议和凭证内容",
                 "订单→订单详情→查看协议和凭证")
    
    d.press("back")
    time.sleep(1)
else:
    log_test("找到查看协议和凭证按钮", False)

# 1.2 查看发票
print("\n--- 1.2 查看发票 ---", flush=True)
if d(text="查看发票").exists(timeout=1):
    d(text="查看发票").click()
    time.sleep(2)
    screenshot("03_invoice")
    
    invoice_texts = get_texts()
    print(f"  发票页: {invoice_texts[:10]}", flush=True)
    
    log_test("发票页显示", len(invoice_texts) > 3)
    
    # 检查发票内容
    has_invoice = any("发票" in t for t in invoice_texts)
    has_image = d(className="android.widget.ImageView").exists
    has_download = any("下载" in t for t in invoice_texts)
    
    log_test("发票-内容显示", has_invoice or has_image)
    log_test("发票-下载功能", has_download)
    
    if not has_invoice and not has_image:
        log_issue("订单详情", "查看发票无内容", "中",
                 "应显示发票内容",
                 "订单→订单详情→查看发票")
    
    d.press("back")
    time.sleep(1)
else:
    log_test("找到查看发票按钮", False)

# ============================================================
# 测试2: 客户详情 - 编辑/驳回原因
# ============================================================
print("\n" + "="*60, flush=True)
print("测试2: 客户详情 - 编辑/驳回原因", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)

# 2.1 测试编辑（已入驻客户）
print("\n--- 2.1 测试编辑客户 ---", flush=True)
find_and_click("已入驻")
time.sleep(2)

d.click(540, 400)  # 点击第一个客户
time.sleep(2)
screenshot("04_customer_detail_edit")

if d(text="编辑").exists(timeout=1):
    d(text="编辑").click()
    time.sleep(2)
    screenshot("05_edit_customer_form")
    
    edit_texts = get_texts()
    print(f"  编辑表单: {edit_texts[:10]}", flush=True)
    
    log_test("编辑表单显示", len(edit_texts) > 3)
    
    # 检查可编辑字段
    has_input = d(className="android.widget.EditText").exists
    log_test("编辑-有输入框", has_input)
    
    # 检查字段
    fields = ["联系人", "联系电话", "企业名称", "地址"]
    for field in fields:
        has_field = any(field in t for t in edit_texts)
        log_test(f"编辑-{field}", has_field)
    
    # 检查保存按钮
    has_save = any("保存" in t or "提交" in t for t in edit_texts)
    log_test("编辑-有保存按钮", has_save)
    
    if not has_save:
        log_issue("客户编辑", "编辑表单无保存按钮", "中",
                 "编辑表单应有保存按钮",
                 "客户→已入驻→客户详情→编辑")
    
    d.press("back")
    time.sleep(1)
else:
    log_test("找到编辑按钮", False)

# 2.2 测试驳回原因
print("\n--- 2.2 测试驳回原因 ---", flush=True)
d.press("back")
time.sleep(1)
d.click(*TAB_CUSTOMER)
time.sleep(2)

find_and_click("已驳回")
time.sleep(2)
screenshot("06_rejected_customers")

if has_text("驳回原因"):
    # 点击第一个已驳回客户
    d.click(540, 500)
    time.sleep(2)
    screenshot("07_rejected_detail")
    
    detail_texts = get_texts()
    print(f"  已驳回客户详情: {detail_texts[:10]}", flush=True)
    
    # 查找驳回原因
    if d(textContains="驳回原因").exists(timeout=1):
        # 点击驳回原因
        d(textContains="驳回原因").click()
        time.sleep(2)
        screenshot("08_reject_reason")
        
        reason_texts = get_texts()
        print(f"  驳回原因: {reason_texts[:10]}", flush=True)
        
        log_test("驳回原因显示", len(reason_texts) > 3)
        
        # 检查是否有具体原因
        has_reason = any("原因" in t or "不符" in t or "信息" in t for t in reason_texts)
        log_test("驳回原因有内容", has_reason)
        
        d.press("back")
        time.sleep(1)
    else:
        log_test("找到驳回原因入口", False)
else:
    log_test("已驳回客户有驳回原因", False)

# ============================================================
# 测试3: 手动录入 - 技术服务协议/编辑/通过
# ============================================================
print("\n" + "="*60, flush=True)
print("测试3: 手动录入 - 技术服务协议/编辑/通过", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(2)

# 进入待审核客户的详情
find_and_click("待审核")
time.sleep(2)
d.click(540, 500)
time.sleep(2)
screenshot("09_pending_detail")

detail_texts = get_texts()
print(f"  待审核客户详情: {detail_texts[:10]}", flush=True)

# 3.1 技术服务协议
print("\n--- 3.1 技术服务协议 ---", flush=True)
if d(text="技术服务协议").exists(timeout=1):
    d(text="技术服务协议").click()
    time.sleep(2)
    screenshot("10_tech_agreement")
    
    tech_texts = get_texts()
    print(f"  技术服务协议: {tech_texts[:8]}", flush=True)
    log_test("技术服务协议可打开", len(tech_texts) > 3)
    
    has_content = any("协议" in t or "服务" in t or "技术" in t for t in tech_texts)
    log_test("技术服务协议有内容", has_content)
    
    d.press("back")
    time.sleep(1)
else:
    log_test("找到技术服务协议", False)

# 3.2 编辑（待审核客户）
print("\n--- 3.2 编辑待审核客户 ---", flush=True)
if d(text="编辑").exists(timeout=1):
    d(text="编辑").click()
    time.sleep(2)
    screenshot("11_edit_pending")
    
    edit_texts = get_texts()
    log_test("待审核客户编辑表单", len(edit_texts) > 3)
    
    has_save = any("保存" in t or "提交" in t for t in edit_texts)
    log_test("编辑-有保存按钮", has_save)
    
    d.press("back")
    time.sleep(1)
else:
    log_test("找到编辑按钮", False)

# ============================================================
# 测试4: 系统设置 - 退出登录
# ============================================================
print("\n" + "="*60, flush=True)
print("测试4: 系统设置 - 退出登录", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("系统设置")
time.sleep(2)
screenshot("12_settings")

# 先取消注销（如果上次弹窗还在）
if has_text("注销"):
    find_and_click("取消")
    time.sleep(1)

# 4.1 退出登录
print("\n--- 4.1 退出登录 ---", flush=True)
if d(text="退出登录").exists(timeout=1):
    d(text="退出登录").click()
    time.sleep(2)
    screenshot("13_logout_dialog")
    
    logout_texts = get_texts()
    print(f"  退出登录弹窗: {logout_texts[:10]}", flush=True)
    
    has_confirm = any("确认" in t or "确定" in t for t in logout_texts)
    has_cancel = any("取消" in t for t in logout_texts)
    
    log_test("退出登录有确认弹窗", has_confirm)
    log_test("退出登录有取消按钮", has_cancel)
    
    if not has_confirm:
        log_issue("系统设置", "退出登录无确认弹窗", "中",
                 "退出登录应二次确认",
                 "我的→系统设置→退出登录")
    
    # 取消退出
    if find_and_click("取消"):
        time.sleep(1)
    elif find_and_click("关闭"):
        time.sleep(1)
else:
    log_test("找到退出登录按钮", False, "可能被注销弹窗遮挡")

# ============================================================
# 测试5: 草稿订单 - 生成订单实际提交
# ============================================================
print("\n" + "="*60, flush=True)
print("测试5: 草稿订单 - 生成订单实际提交", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)

# 滚动查找草稿订单
found_draft = False
for _ in range(3):
    if d(text="草稿").exists(timeout=1):
        elem = d(text="草稿")
        bounds = elem.info.get('bounds', {})
        if bounds:
            y = (bounds['top'] + bounds['bottom']) // 2
            d.click(540, y)
            time.sleep(2)
            screenshot("14_draft_detail")
            found_draft = True
            
            # 5.1 点击生成订单
            print("\n--- 5.1 点击生成订单 ---", flush=True)
            if d(text="生成订单").exists(timeout=1):
                d(text="生成订单").click()
                time.sleep(3)
                screenshot("15_after_generate")
                
                after_gen = get_texts()
                print(f"  生成订单后: {after_gen[:10]}", flush=True)
                
                # 检查结果
                has_success = any("成功" in t for t in after_gen)
                has_error = any("错误" in t or "失败" in t or "请" in t for t in after_gen)
                has_order_list = any("全部" in t and "客户订单" in t for t in after_gen)
                has_confirm = any("确认" in t or "确定" in t for t in after_gen)
                
                log_test("生成订单有反馈", has_success or has_error or has_order_list or has_confirm)
                
                if has_confirm:
                    log_test("生成订单有确认弹窗", True)
                    # 取消
                    find_and_click("取消")
                    time.sleep(1)
                elif has_success:
                    log_test("生成订单成功", True)
                elif has_error:
                    log_test("生成订单-有错误提示", False, f"提示: {[t for t in after_gen if '请' in t][:2]}")
            else:
                log_test("找到生成订单按钮", False)
            
            break
    
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)

if not found_draft:
    log_test("找到草稿订单", False)

# ============================================================
# 测试6: 客户选择页 - 手动录入
# ============================================================
print("\n" + "="*60, flush=True)
print("测试6: 客户选择页 - 手动录入", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)
find_and_click("全选")
time.sleep(1)
find_and_click("生成订单")
time.sleep(2)
find_and_click("客户订单")
time.sleep(2)
find_and_click("选择客户")
time.sleep(2)
screenshot("16_customer_select")

if d(text="手动录入").exists(timeout=1):
    d(text="手动录入").click()
    time.sleep(2)
    screenshot("17_manual_from_select")
    
    manual_texts = get_texts()
    print(f"  手动录入页: {manual_texts[:10]}", flush=True)
    
    log_test("客户选择-手动录入可用", len(manual_texts) > 3)
    
    # 检查表单字段
    has_form = any("联系人" in t or "电话" in t for t in manual_texts)
    log_test("手动录入-有表单", has_form)
    
    d.press("back")
    time.sleep(1)
else:
    log_test("客户选择-手动录入按钮", False)

# ============================================================
# 测试7: 我的 - 客服电话
# ============================================================
print("\n" + "="*60, flush=True)
print("测试7: 我的 - 客服电话", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
screenshot("18_my_page")

if d(text="客服电话").exists(timeout=1):
    d(text="客服电话").click()
    time.sleep(2)
    screenshot("19_service_call")
    
    call_texts = get_texts()
    print(f"  客服电话弹窗: {call_texts[:10]}", flush=True)
    
    # 检查是否显示号码
    has_number = any("4001150629" in t for t in call_texts)
    has_call_button = any("呼叫" in t or "拨打" in t for t in call_texts)
    has_cancel = any("取消" in t for t in call_texts)
    
    log_test("客服电话-显示号码", has_number)
    log_test("客服电话-有呼叫按钮", has_call_button)
    log_test("客服电话-有取消按钮", has_cancel)
    
    if not has_call_button and not has_number:
        log_issue("客服电话", "点击客服电话无反应", "中",
                 "应显示客服号码并提供拨打选项",
                 "我的→客服电话")
    
    # 取消
    find_and_click("取消")
    time.sleep(1)
else:
    log_test("找到客服电话按钮", False)

# ============================================================
# 测试8: 意见反馈 - 上传凭证
# ============================================================
print("\n" + "="*60, flush=True)
print("测试8: 意见反馈 - 上传凭证", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("意见反馈")
time.sleep(2)
screenshot("20_feedback")

# 8.1 上传凭证
print("\n--- 8.1 上传凭证 ---", flush=True)
# 上传凭证可能是一个区域，不是文本按钮
# 尝试点击"上传凭证"文本
if d(textContains="上传凭证").exists(timeout=1):
    d(textContains="上传凭证").click()
    time.sleep(2)
    screenshot("21_upload_proof")
    
    upload_texts = get_texts()
    print(f"  上传凭证选项: {upload_texts[:10]}", flush=True)
    
    has_camera = any("拍照" in t for t in upload_texts)
    has_album = any("相册" in t or "图库" in t for t in upload_texts)
    has_file = any("文件" in t or "文档" in t for t in upload_texts)
    
    log_test("反馈-拍照上传", has_camera)
    log_test("反馈-相册上传", has_album)
    log_test("反馈-文件上传", has_file)
    
    if not (has_camera or has_album or has_file):
        # 可能是直接打开了相册
        log_test("上传凭证-有响应", len(upload_texts) != 0)
    
    d.press("back")
    time.sleep(1)
else:
    # 尝试点击图片区域
    image_views = d(className="android.widget.ImageView")
    if image_views.exists:
        # 点击中间的图片（上传凭证区域）
        for i in range(min(image_views.count, 5)):
            info = image_views[i].info
            bounds = info.get('bounds', {})
            if bounds:
                center_y = (bounds['top'] + bounds['bottom']) // 2
                if 900 < center_y < 1200:  # 上传凭证区域
                    center_x = (bounds['left'] + bounds['right']) // 2
                    d.click(center_x, center_y)
                    time.sleep(2)
                    screenshot("22_upload_via_image")
                    
                    upload_texts = get_texts()
                    has_camera = any("拍照" in t for t in upload_texts)
                    has_album = any("相册" in t or "图库" in t for t in upload_texts)
                    
                    log_test("反馈-拍照上传", has_camera)
                    log_test("反馈-相册上传", has_album)
                    
                    d.press("back")
                    time.sleep(1)
                    break
        else:
            log_test("找到上传凭证入口", False, "未找到上传凭证区域")
    else:
        log_test("找到上传凭证入口", False)

# ============================================================
# 测试9: 建材/人才/服务列表
# ============================================================
print("\n" + "="*60, flush=True)
print("测试9: 建材/人才/服务列表", flush=True)
print("="*60)

# 9.1 建材列表
print("\n--- 9.1 建材列表 ---", flush=True)
restart_app()
d(text="建材").click()
time.sleep(2)
screenshot("23_building_list")

building_texts = get_texts()
print(f"  建材列表: {building_texts[:10]}", flush=True)

log_test("建材列表显示", len(building_texts) > 5)
has_items = any("元/" in t for t in building_texts)
log_test("建材列表有商品", has_items)
has_add_cart = any("加入购物车" in t for t in building_texts)
log_test("建材-加入购物车", has_add_cart)

# 9.2 人才列表
print("\n--- 9.2 人才列表 ---", flush=True)
restart_app()
d(text="人才").click()
time.sleep(2)
screenshot("24_talent_list")

talent_texts = get_texts()
print(f"  人才列表: {talent_texts[:10]}", flush=True)

log_test("人才列表显示", len(talent_texts) > 5)
has_talent = any("班组" in t or "木工" in t or "电工" in t for t in talent_texts)
log_test("人才列表有数据", has_talent)

# 9.3 服务列表
print("\n--- 9.3 服务列表 ---", flush=True)
restart_app()
d(text="服务").click()
time.sleep(2)
screenshot("25_service_list")

service_texts = get_texts()
print(f"  服务列表: {service_texts[:10]}", flush=True)

log_test("服务列表显示", len(service_texts) > 5)

# ============================================================
# 测试10: 下单表单 - 管理按钮
# ============================================================
print("\n" + "="*60, flush=True)
print("测试10: 下单表单 - 管理按钮", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CART)
time.sleep(3)
find_and_click("全选")
time.sleep(1)
find_and_click("生成订单")
time.sleep(2)
find_and_click("客户订单")
time.sleep(2)
screenshot("26_order_form")

if d(text="管理").exists(timeout=1):
    d(text="管理").click()
    time.sleep(2)
    screenshot("27_after_manage")
    
    after_manage = get_texts()
    print(f"  点击管理后: {after_manage[:10]}", flush=True)
    
    # 管理按钮应该返回购物车管理页面
    has_cart = any("购物车" in t and ("完成" in t or "管理" in t) for t in after_manage)
    log_test("管理按钮返回购物车", has_cart)
else:
    log_test("找到管理按钮", False)

# ============================================================
# 测试11: 公司资质 - 下载
# ============================================================
print("\n" + "="*60, flush=True)
print("测试11: 公司资质 - 下载", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("公司资质")
time.sleep(2)
screenshot("28_qualification")

# 查找可点击元素
xml = d.dump_hierarchy()
clickables = re.findall(
    r'<node[^>]*clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
    xml
)

print(f"  可点击元素: {len(clickables)} 个", flush=True)

# 点击资质图片区域（可能是下载）
for x1, y1, x2, y2 in clickables:
    center_x = (int(x1) + int(x2)) // 2
    center_y = (int(y1) + int(y2)) // 2
    # 点击中间区域
    if 300 < center_y < 1500:
        print(f"  尝试点击: ({center_x}, {center_y})", flush=True)
        d.click(center_x, center_y)
        time.sleep(2)
        screenshot("29_qualification_click")
        
        after_click = get_texts()
        has_download = any("下载" in t for t in after_click)
        has_preview = any("预览" in t or "查看" in t for t in after_click)
        
        log_test("资质-点击有响应", len(after_click) > 0)
        log_test("资质-下载功能", has_download)
        log_test("资质-预览功能", has_preview)
        break

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60, flush=True)
print("最后15个按钮测试汇总", flush=True)
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

with open(os.path.join(screenshot_dir, "final_15_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告: {os.path.join(screenshot_dir, 'final_15_report.json')}", flush=True)