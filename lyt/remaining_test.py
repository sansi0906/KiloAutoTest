"""
乐云台 App - 未覆盖按钮补充测试
覆盖所有之前未测试的按钮
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

screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remaining_test_results")
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
# 测试1: 客户详情 - 审核通过/驳回
# ============================================================
print("\n" + "="*60, flush=True)
print("测试1: 客户审核（通过/驳回）", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)

# 进入待审核Tab
if find_and_click("待审核"):
    time.sleep(2)
    screenshot("01_pending_customers")
    
    # 点击第一个待审核客户
    d.click(540, 500)
    time.sleep(2)
    screenshot("02_pending_customer_detail")
    
    detail_texts = get_texts()
    print(f"  待审核客户详情: {detail_texts[:10]}", flush=True)
    
    # 1.1 测试通过按钮
    print("\n--- 1.1 测试通过按钮 ---", flush=True)
    if d(text="通过").exists(timeout=1):
        log_test("找到通过按钮", True)
        
        # 点击通过（但不确认，避免实际修改数据）
        d(text="通过").click()
        time.sleep(2)
        screenshot("03_approve_dialog")
        
        dialog_texts = get_texts()
        print(f"  通过弹窗: {dialog_texts[:10]}", flush=True)
        
        # 检查是否有确认弹窗
        has_confirm = any("确认" in t or "确定" in t for t in dialog_texts)
        log_test("通过有确认弹窗", has_confirm)
        
        if not has_confirm:
            log_issue("客户审核", "点击通过无确认弹窗", "高",
                     "审核通过应二次确认，避免误操作",
                     "客户→待审核→点击客户→点通过")
        
        # 取消
        if find_and_click("取消"):
            time.sleep(1)
        elif find_and_click("关闭"):
            time.sleep(1)
    else:
        log_test("找到通过按钮", False, "待审核客户详情无通过按钮")
    
    # 1.2 测试驳回
    print("\n--- 1.2 测试驳回 ---", flush=True)
    # 返回并重新进入
    d.press("back")
    time.sleep(1)
    d.click(540, 500)
    time.sleep(2)
    
    if has_text("驳回"):
        log_test("找到驳回入口", True)
        
        # 查找驳回按钮的位置
        if d(textContains="驳回").exists(timeout=1):
            d(textContains="驳回").click()
            time.sleep(2)
            screenshot("04_reject_dialog")
            
            reject_texts = get_texts()
            print(f"  驳回弹窗: {reject_texts[:10]}", flush=True)
            
            # 检查驳回是否需要填写原因
            has_reason = any("原因" in t for t in reject_texts)
            log_test("驳回需填写原因", has_reason)
            
            if not has_reason:
                log_issue("客户审核", "驳回无填写原因", "中",
                         "驳回应要求填写原因",
                         "客户→待审核→客户详情→驳回")
            
            # 取消
            find_and_click("取消")
            time.sleep(1)
    else:
        log_test("找到驳回入口", False)

# ============================================================
# 测试2: 手动录入 - 上传文件/协议
# ============================================================
print("\n" + "="*60, flush=True)
print("测试2: 手动录入 - 上传文件/协议", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(2)
find_and_click("手动录入")
time.sleep(2)
screenshot("05_manual_input")

input_texts = get_texts()
print(f"  手动录入页: {input_texts[:10]}", flush=True)

# 2.1 测试委托服务协议
print("\n--- 2.1 测试委托服务协议 ---", flush=True)
if d(text="委托服务协议").exists(timeout=1):
    d(text="委托服务协议").click()
    time.sleep(2)
    screenshot("06_service_agreement")
    
    agreement_texts = get_texts()
    print(f"  协议页: {agreement_texts[:8]}", flush=True)
    log_test("委托服务协议可打开", len(agreement_texts) > 3)
    
    d.press("back")
    time.sleep(1)

# 2.2 测试技术服务协议
print("\n--- 2.2 测试技术服务协议 ---", flush=True)
if d(text="技术服务协议").exists(timeout=1):
    d(text="技术服务协议").click()
    time.sleep(2)
    screenshot("07_tech_agreement")
    
    tech_texts = get_texts()
    log_test("技术服务协议可打开", len(tech_texts) > 3)
    
    d.press("back")
    time.sleep(1)

# 2.3 测试上传文件
print("\n--- 2.3 测试上传文件 ---", flush=True)
if d(text="上传文件").exists(timeout=1):
    d(text="上传文件").click()
    time.sleep(2)
    screenshot("08_upload_options")
    
    upload_texts = get_texts()
    print(f"  上传选项: {upload_texts[:10]}", flush=True)
    
    # 检查上传方式
    has_camera = any("拍照" in t for t in upload_texts)
    has_album = any("相册" in t or "图库" in t for t in upload_texts)
    has_file = any("文件" in t or "文档" in t for t in upload_texts)
    
    log_test("上传-拍照", has_camera)
    log_test("上传-相册", has_album)
    log_test("上传-文件", has_file)
    
    if not (has_camera or has_album or has_file):
        log_issue("手动录入", "上传文件无选项", "中",
                 "应提供上传方式选项",
                 "客户→手动录入→上传文件")
    
    # 取消
    d.press("back")
    time.sleep(1)

# ============================================================
# 测试3: 邀约入驻
# ============================================================
print("\n" + "="*60, flush=True)
print("测试3: 邀约入驻", flush=True)
print("="*60)

restart_app()
d.click(*TAB_CUSTOMER)
time.sleep(3)

# 3.1 客户列表中的邀约入驻
print("\n--- 3.1 客户列表-邀约入驻 ---", flush=True)
if d(text="邀约入驻").exists(timeout=1):
    d(text="邀约入驻").click()
    time.sleep(2)
    screenshot("09_invite")
    
    invite_texts = get_texts()
    print(f"  邀约入驻页: {invite_texts[:10]}", flush=True)
    
    log_test("邀约入驻页显示", len(invite_texts) > 3)
    
    # 检查邀约方式
    has_wechat = any("微信" in t for t in invite_texts)
    has_qq = any("QQ" in t for t in invite_texts)
    has_sms = any("短信" in t for t in invite_texts)
    has_link = any("链接" in t for t in invite_texts)
    has_qrcode = any("二维码" in t or "扫码" in t for t in invite_texts)
    
    log_test("邀约-微信", has_wechat)
    log_test("邀约-QQ", has_qq)
    log_test("邀约-短信", has_sms)
    log_test("邀约-链接", has_link)
    log_test("邀约-二维码", has_qrcode)
    
    if not (has_wechat or has_qq or has_sms or has_link or has_qrcode):
        log_issue("邀约入驻", "无邀约方式", "中",
                 "应提供至少一种邀约方式",
                 "客户→邀约入驻")
    
    d.press("back")
    time.sleep(1)
else:
    log_test("客户列表-邀约入驻按钮", False, "未找到邀约入驻按钮")

# ============================================================
# 测试4: 订单详情 - 终止订单
# ============================================================
print("\n" + "="*60, flush=True)
print("测试4: 订单详情 - 终止订单", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)

# 查找有"终止订单"按钮的订单
found_terminate = False
for scroll_count in range(3):
    # 点击第一个订单
    d.click(540, 500)
    time.sleep(2)
    screenshot(f"10_order_detail_{scroll_count}")
    
    if has_text("终止订单"):
        found_terminate = True
        print("  找到终止订单按钮", flush=True)
        
        # 4.1 测试终止订单
        print("\n--- 4.1 测试终止订单 ---", flush=True)
        if d(text="终止订单").exists(timeout=1):
            d(text="终止订单").click()
            time.sleep(2)
            screenshot("11_terminate_dialog")
            
            dialog_texts = get_texts()
            print(f"  终止订单弹窗: {dialog_texts[:10]}", flush=True)
            
            # 检查是否有确认弹窗
            has_confirm = any("确认" in t or "确定" in t for t in dialog_texts)
            has_reason = any("原因" in t for t in dialog_texts)
            
            log_test("终止订单有确认弹窗", has_confirm)
            log_test("终止订单需填原因", has_reason)
            
            if not has_confirm:
                log_issue("订单详情", "终止订单无确认弹窗", "高",
                         "终止订单是破坏性操作，应二次确认",
                         "订单→订单详情→终止订单")
            
            # 取消
            find_and_click("取消")
            time.sleep(1)
        
        d.press("back")
        time.sleep(1)
        break
    
    d.press("back")
    time.sleep(1)
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)

if not found_terminate:
    log_test("找到终止订单按钮", False, "未找到有终止按钮的订单")

# ============================================================
# 测试5: 草稿订单 - 保存草稿/生成订单实际提交
# ============================================================
print("\n" + "="*60, flush=True)
print("测试5: 草稿订单 - 保存草稿/生成订单", flush=True)
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
            screenshot("12_draft_edit")
            found_draft = True
            
            # 5.1 测试保存草稿
            print("\n--- 5.1 测试保存草稿 ---", flush=True)
            if d(text="保存草稿").exists(timeout=1):
                d(text="保存草稿").click()
                time.sleep(2)
                screenshot("13_save_draft")
                
                after_save = get_texts()
                has_success = any("成功" in t or "已保存" in t for t in after_save)
                has_order_list = any("全部" in t and "客户订单" in t for t in after_save)
                
                log_test("保存草稿有反馈", has_success or has_order_list, f"页面: {after_save[:5]}")
            else:
                log_test("找到保存草稿按钮", False)
            
            # 5.2 重新进入测试生成订单
            print("\n--- 5.2 测试生成订单 ---", flush=True)
            d.press("back")
            time.sleep(1)
            
            # 再次进入草稿订单
            if d(text="草稿").exists(timeout=1):
                elem = d(text="草稿")
                bounds = elem.info.get('bounds', {})
                if bounds:
                    y = (bounds['top'] + bounds['bottom']) // 2
                    d.click(540, y)
                    time.sleep(2)
                    
                    if d(text="生成订单").exists(timeout=1):
                        log_test("找到生成订单按钮", True)
                        # 不实际提交，避免破坏数据
                        print("  (不实际提交，避免破坏数据)", flush=True)
            
            break
    
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)

if not found_draft:
    log_test("找到草稿订单", False)

# ============================================================
# 测试6: 上传协议实际操作
# ============================================================
print("\n" + "="*60, flush=True)
print("测试6: 上传协议实际操作", flush=True)
print("="*60)

restart_app()
d.click(*TAB_ORDER)
time.sleep(3)

# 查找待上传的订单
found_upload = False
for _ in range(3):
    if d(textContains="待上传").exists(timeout=1) or d(text="上传协议和凭证").exists(timeout=1):
        # 点击该订单
        if d(textContains="待上传").exists(timeout=1):
            elem = d(textContains="待上传")
        else:
            elem = d(text="上传协议和凭证")
        
        bounds = elem.info.get('bounds', {})
        if bounds:
            y = (bounds['top'] + bounds['bottom']) // 2
            d.click(540, y)
            time.sleep(2)
            screenshot("14_upload_page")
            found_upload = True
            
            upload_texts = get_texts()
            print(f"  上传协议页: {upload_texts[:10]}", flush=True)
            
            # 查找上传按钮
            if d(text="上传协议和凭证").exists(timeout=1):
                d(text="上传协议和凭证").click()
                time.sleep(2)
                screenshot("15_upload_options")
                
                options_texts = get_texts()
                print(f"  上传选项: {options_texts[:10]}", flush=True)
                
                has_camera = any("拍照" in t for t in options_texts)
                has_album = any("相册" in t or "图库" in t for t in options_texts)
                has_file = any("文件" in t or "文档" in t for t in options_texts)
                
                log_test("上传协议-拍照", has_camera)
                log_test("上传协议-相册", has_album)
                log_test("上传协议-文件", has_file)
                
                d.press("back")
                time.sleep(1)
            
            break
    
    d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
    time.sleep(1)

if not found_upload:
    log_test("找到待上传订单", False)

# ============================================================
# 测试7: 意见反馈 - 上传凭证
# ============================================================
print("\n" + "="*60, flush=True)
print("测试7: 意见反馈 - 上传凭证", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("意见反馈")
time.sleep(2)

# 7.1 测试投诉类型选择
print("\n--- 7.1 测试投诉类型 ---", flush=True)
if d(text="功能问题").exists(timeout=1):
    d(text="功能问题").click()
    time.sleep(0.5)
    log_test("选择功能问题", True)

if d(text="服务问题").exists(timeout=1):
    d(text="服务问题").click()
    time.sleep(0.5)
    log_test("选择服务问题", True)

# 7.2 测试上传凭证
print("\n--- 7.2 测试上传凭证 ---", flush=True)
if d(textContains="上传凭证").exists(timeout=1):
    d(textContains="上传凭证").click()
    time.sleep(2)
    screenshot("16_feedback_upload")
    
    upload_texts = get_texts()
    print(f"  上传选项: {upload_texts[:10]}", flush=True)
    
    has_camera = any("拍照" in t for t in upload_texts)
    has_album = any("相册" in t or "图库" in t for t in upload_texts)
    
    log_test("反馈-拍照上传", has_camera)
    log_test("反馈-相册上传", has_album)
    
    d.press("back")
    time.sleep(1)

# 7.3 测试空内容提交
print("\n--- 7.3 测试空内容提交 ---", flush=True)
if d(text="提交").exists(timeout=1):
    d(text="提交").click()
    time.sleep(2)
    screenshot("17_feedback_empty_submit")
    
    after_submit = get_texts()
    has_error = any("请" in t or "不能为空" in t or "至少" in t for t in after_submit)
    log_test("空反馈提交有验证", has_error, f"提示: {[t for t in after_submit if '请' in t or '不能' in t][:3]}")
    
    if not has_error:
        log_issue("意见反馈", "空内容可提交", "中",
                 "空反馈应被验证拦截",
                 "我的→意见反馈→直接点提交")

d.press("back")
time.sleep(1)

# ============================================================
# 测试8: 关于我们 - 服务协议/隐私政策
# ============================================================
print("\n" + "="*60, flush=True)
print("测试8: 关于我们 - 服务协议/隐私政策", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("关于我们")
time.sleep(2)

# 8.1 服务协议
print("\n--- 8.1 服务协议 ---", flush=True)
if d(text="服务协议").exists(timeout=1):
    d(text="服务协议").click()
    time.sleep(2)
    screenshot("18_service_agreement")
    
    agreement_texts = get_texts()
    print(f"  服务协议: {agreement_texts[:8]}", flush=True)
    log_test("服务协议可打开", len(agreement_texts) > 5)
    
    # 检查协议内容
    has_content = any("协议" in t or "条款" in t or "服务" in t for t in agreement_texts)
    log_test("服务协议有内容", has_content)
    
    d.press("back")
    time.sleep(1)

# 8.2 隐私政策
print("\n--- 8.2 隐私政策 ---", flush=True)
if d(text="隐私政策").exists(timeout=1):
    d(text="隐私政策").click()
    time.sleep(2)
    screenshot("19_privacy_policy")
    
    privacy_texts = get_texts()
    print(f"  隐私政策: {privacy_texts[:8]}", flush=True)
    log_test("隐私政策可打开", len(privacy_texts) > 5)
    
    has_content = any("隐私" in t or "信息" in t or "保护" in t for t in privacy_texts)
    log_test("隐私政策有内容", has_content)
    
    d.press("back")
    time.sleep(1)

# ============================================================
# 测试9: 系统设置 - 注销账户/退出登录
# ============================================================
print("\n" + "="*60, flush=True)
print("测试9: 系统设置 - 注销账户/退出登录", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("系统设置")
time.sleep(2)
screenshot("20_settings")

# 9.1 测试注销账户
print("\n--- 9.1 测试注销账户 ---", flush=True)
if d(text="注销账户").exists(timeout=1):
    d(text="注销账户").click()
    time.sleep(2)
    screenshot("21_cancel_account")
    
    cancel_texts = get_texts()
    print(f"  注销账户页: {cancel_texts[:10]}", flush=True)
    
    # 检查注销警告
    has_warning = any("删除" in t or "不可恢复" in t or "警告" in t for t in cancel_texts)
    log_test("注销账户有警告", has_warning)
    
    if not has_warning:
        log_issue("系统设置", "注销账户无警告", "高",
                 "注销账户应显示不可恢复警告",
                 "我的→系统设置→注销账户")
    
    # 检查是否有确认按钮
    has_confirm = any("确认" in t or "确定" in t for t in cancel_texts)
    log_test("注销账户有确认按钮", has_confirm)
    
    # 返回
    d.press("back")
    time.sleep(1)
else:
    log_test("找到注销账户按钮", False)

# 9.2 测试退出登录
print("\n--- 9.2 测试退出登录 ---", flush=True)
if d(text="退出登录").exists(timeout=1):
    d(text="退出登录").click()
    time.sleep(2)
    screenshot("22_logout_dialog")
    
    logout_texts = get_texts()
    print(f"  退出登录弹窗: {logout_texts[:10]}", flush=True)
    
    # 检查确认弹窗
    has_confirm = any("确认" in t or "确定" in t for t in logout_texts)
    log_test("退出登录有确认弹窗", has_confirm)
    
    if not has_confirm:
        log_issue("系统设置", "退出登录无确认", "中",
                 "退出登录应二次确认",
                 "我的→系统设置→退出登录")
    
    # 取消
    find_and_click("取消")
    time.sleep(1)
else:
    log_test("找到退出登录按钮", False)

# ============================================================
# 测试10: 公司资质 - 下载
# ============================================================
print("\n" + "="*60, flush=True)
print("测试10: 公司资质 - 下载", flush=True)
print("="*60)

restart_app()
d.click(*MY_BUTTON)
time.sleep(2)
find_and_click("公司资质")
time.sleep(2)
screenshot("23_qualification")

qual_texts = get_texts()
print(f"  公司资质页: {qual_texts[:10]}", flush=True)

log_test("公司资质页显示", len(qual_texts) > 3)

# 检查资质内容
has_image = d(className="android.widget.ImageView").exists
has_download = any("download" in t.lower() or "下载" in t for t in qual_texts)
log_test("资质-显示图片", has_image)
log_test("资质-下载链接", has_download)

# 测试点击下载
if has_download:
    # 找到下载链接并点击
    for t in qual_texts:
        if "download" in t.lower() or "下载" in t:
            if d(text=t).exists(timeout=1):
                d(text=t).click()
                time.sleep(2)
                screenshot("24_download_action")
                
                after_click = get_texts()
                has_download_confirm = any("下载" in t for t in after_click)
                log_test("下载有响应", has_download_confirm or len(after_click) != len(qual_texts))
                break

# ============================================================
# 测试11: 客户选择页 - 邀约入驻
# ============================================================
print("\n" + "="*60, flush=True)
print("测试11: 客户选择页 - 邀约入驻", flush=True)
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

if d(text="邀约入驻").exists(timeout=1):
    d(text="邀约入驻").click()
    time.sleep(2)
    screenshot("25_customer_invite")
    
    invite_texts = get_texts()
    print(f"  客户选择-邀约入驻: {invite_texts[:10]}", flush=True)
    log_test("客户选择-邀约入驻可用", len(invite_texts) > 3)
    
    d.press("back")
    time.sleep(1)
else:
    log_test("客户选择-邀约入驻按钮", False, "未找到邀约入驻")

# ============================================================
# 测试12: 首页 - 消息中心
# ============================================================
print("\n" + "="*60, flush=True)
print("测试12: 首页 - 消息中心", flush=True)
print("="*60)

restart_app()
d.click(*TAB_HOME)
time.sleep(2)

if d(text="消息").exists(timeout=1):
    d(text="消息").click()
    time.sleep(2)
    screenshot("26_messages")
    
    msg_texts = get_texts()
    print(f"  消息页: {msg_texts[:10]}", flush=True)
    
    log_test("消息中心显示", len(msg_texts) > 3)
    
    # 检查消息列表
    has_msg = any("订单" in t or "待上传" in t or "待开票" in t for t in msg_texts)
    log_test("消息列表有内容", has_msg)
    
    # 测试更多消息
    if d(text="更多消息").exists(timeout=1):
        d(text="更多消息").click()
        time.sleep(2)
        screenshot("27_more_messages")
        
        more_texts = get_texts()
        log_test("更多消息页显示", len(more_texts) > 3)
        
        d.press("back")
        time.sleep(1)

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60, flush=True)
print("补充测试汇总", flush=True)
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

with open(os.path.join(screenshot_dir, "remaining_test_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告: {os.path.join(screenshot_dir, 'remaining_test_report.json')}", flush=True)