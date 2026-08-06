"""
乐云台 App - 问题复现验证脚本
针对之前发现的问题进行重新验证
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

results = []

def log(issue_id, module, description, status, severity="中", detail=""):
    result = {
        "ID": issue_id,
        "模块": module,
        "问题描述": description,
        "状态": status,
        "严重程度": severity,
        "详情": detail,
        "时间": datetime.now().strftime("%H:%M:%S")
    }
    results.append(result)
    symbol = "✅" if status == "通过" else "❌" if status == "失败" else "⚠️"
    print(f"  {symbol} #{issue_id} [{module}] {description} → {status}", flush=True)
    if detail:
        print(f"     {detail}", flush=True)

print("连接设备...", flush=True)
d = u2.connect()
d.implicitly_wait(10.0)
print(f"✓ 设备: {d.info.get('productName', 'unknown')}", flush=True)

# 停止钉钉
current = d.app_current()
if current.get('package') == DINGTALK:
    d.app_stop(DINGTALK)
    time.sleep(1)

# 重启App
d.app_start(PACKAGE, stop=True)
time.sleep(5)

screenshot_dir = os.path.join(os.path.dirname(__file__), " reverify_results")
os.makedirs(screenshot_dir, exist_ok=True)

def get_texts():
    xml = d.dump_hierarchy()
    texts = re.findall(r'text="([^"]*)"', xml)
    return [t for t in texts if t.strip()]

def screenshot(name):
    d.screenshot(os.path.join(screenshot_dir, f"{name}.png"))

# ========== 验证1: 首页 ==========
print("\n" + "="*60, flush=True)
print("验证1: 首页", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(3)
screenshot("01_home")
texts = get_texts()

log("H1", "首页", "用户名显示（杨涛轩）", 
    "通过" if any("杨涛轩" in t for t in texts) else "失败",
    "低")

log("H2", "首页", "营销账号显示（营销333）", 
    "通过" if any("营销333" in t for t in texts) else "失败",
    "低")

log("H3", "首页", "业绩数据（销售额）", 
    "通过" if any("销售额" in t for t in texts) else "失败",
    "中")

log("H4", "首页", "客户数量", 
    "通过" if any("客户" in t for t in texts) else "失败",
    "低")

log("H5", "首页", "订单数量", 
    "通过" if any("订单" in t for t in texts) else "失败",
    "低")

log("H6", "首页", "功能入口-设备", 
    "通过" if any("设备" in t for t in texts) else "失败",
    "低")

log("H7", "首页", "功能入口-建材", 
    "通过" if any("建材" in t for t in texts) else "失败",
    "低")

log("H8", "首页", "功能入口-人才", 
    "通过" if any("人才" in t for t in texts) else "失败",
    "低")

log("H9", "首页", "功能入口-服务", 
    "通过" if any("服务" in t for t in texts) else "失败",
    "低")

# ========== 验证2: 设备列表 ==========
print("\n" + "="*60, flush=True)
print("验证2: 设备列表", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(1)
d(text="设备").click()
time.sleep(2)
screenshot("02_device_list")
texts = get_texts()

log("D1", "设备列表", "搜索框", 
    "通过" if any("搜索" in t for t in texts) else "失败",
    "低")

log("D2", "设备列表", "商品卡片（设备出售）", 
    "通过" if any("设备出售" in t for t in texts) else "失败",
    "中")

log("D3", "设备列表", "加入购物车按钮", 
    "通过" if any("加入购物车" in t for t in texts) else "失败",
    "高")

log("D4", "设备列表", "拨打电话按钮", 
    "通过" if any("拨打电话" in t for t in texts) else "失败",
    "中")

# 点击第一个商品
d.click(312, 600)
time.sleep(2)
screenshot("03_device_detail")
texts = get_texts()

log("D5", "设备详情", "加入购物车按钮", 
    "通过" if any("加入购物车" in t for t in texts) else "失败",
    "高")

log("D6", "设备详情", "立即购买按钮", 
    "通过" if any("立即购买" in t for t in texts) else "未找到",
    "低", "可能使用其他购买方式")

# 返回
d.press("back")
time.sleep(1)

# ========== 验证3: 客户管理 ==========
print("\n" + "="*60, flush=True)
print("验证3: 客户管理", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(1)
d.click(*TAB_CUSTOMER)
time.sleep(3)
screenshot("04_customer_list")
texts = get_texts()

log("C1", "客户管理", "搜索框", 
    "通过" if any("搜索" in t for t in texts) else "失败",
    "低")

log("C2", "客户管理", "筛选按钮", 
    "通过" if any("筛选" in t for t in texts) else "失败",
    "中", "按钮不明显")

log("C3", "客户管理", "状态Tab（待审核）", 
    "通过" if any("待审核" in t for t in texts) else "失败",
    "低")

log("C4", "客户管理", "状态Tab（已入驻）", 
    "通过" if any("已入驻" in t for t in texts) else "失败",
    "低")

log("C5", "客户管理", "新增客户入口", 
    "通过" if any("手动录入" in t for t in texts) else "失败",
    "中", "入口不明显")

# 点击第一个客户
d.click(312, 500)
time.sleep(2)
screenshot("05_customer_detail")
texts = get_texts()

log("C6", "客户详情", "联系人信息", 
    "通过" if any("联系人" in t for t in texts) else "失败",
    "低")

log("C7", "客户详情", "联系电话", 
    "通过" if any("联系电话" in t for t in texts) else "失败",
    "中")

log("C8", "客户详情", "拨打电话入口", 
    "通过" if (any("拨打电话" in t for t in texts) or any("呼叫" in t for t in texts)) else "失败",
    "中", "缺少一键拨号功能")

# 返回
d.press("back")
time.sleep(1)

# ========== 验证4: 购物车 ==========
print("\n" + "="*60, flush=True)
print("验证4: 购物车", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(1)
d.click(*TAB_CART)
time.sleep(3)
screenshot("06_cart")
texts = get_texts()

log("K1", "购物车", "购物车标题", 
    "通过" if any("购物车" in t for t in texts) else "失败",
    "低")

log("K2", "购物车", "管理按钮", 
    "通过" if any("管理" in t for t in texts) else "失败",
    "中")

log("K3", "购物车", "全选按钮", 
    "通过" if any("全选" in t for t in texts) else "失败",
    "低")

log("K4", "购物车", "合计金额显示", 
    "通过" if any("合计" in t for t in texts) else "失败",
    "高")

log("K5", "购物车", "合计金额非0", 
    "通过" if (any("合计" in t for t in texts) and not any("0.00" in t for t in texts)) else "失败",
    "高", "商品可能未选中")

log("K6", "购物车", "结算按钮", 
    "通过" if any("结算" in t for t in texts) else "失败",
    "高", "核心交易按钮缺失")

log("K7", "购物车", "生成订单按钮", 
    "通过" if any("生成订单" in t for t in texts) else "失败",
    "高")

# 点击生成订单测试
if any("生成订单" in t for t in texts):
    log("K8", "购物车", "生成订单按钮可点击", 
        "待验证",
        "中", "点击测试中...")
    
    # 找按钮位置
    for text in texts:
        if "生成订单" in text:
            d(text=text).click()
            time.sleep(2)
            break
    
    texts2 = get_texts()
    
    order_indicators = ["收货地址", "支付方式", "提交订单", "确认订单"]
    found_order = [ind for ind in order_indicators if any(ind in t for t in texts2)]
    
    log("K8", "购物车", "点击生成订单进入下单流程", 
        "通过" if found_order else "失败",
        "高", f"点击无效，无反应")

# ========== 验证5: 订单列表 ==========
print("\n" + "="*60, flush=True)
print("验证5: 订单列表", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(1)
d.click(*TAB_ORDER)
time.sleep(3)
screenshot("07_orders")
texts = get_texts()

log("O1", "订单列表", "订单Tab-全部", 
    "通过" if any("全部" in t for t in texts) else "失败",
    "低")

log("O2", "订单列表", "订单Tab-客户订单", 
    "通过" if any("客户订单" in t for t in texts) else "失败",
    "低")

log("O3", "订单列表", "订单Tab-记录订单", 
    "通过" if any("记录订单" in t for t in texts) else "失败",
    "低")

log("O4", "订单列表", "订单编号显示", 
    "通过" if any("订单编号" in t for t in texts) else "失败",
    "中")

# 点击第一个订单
d.click(540, 500)
time.sleep(2)
screenshot("08_order_detail")
texts = get_texts()

log("O5", "订单详情", "查看协议入口", 
    "通过" if any("查看协议" in t for t in texts) else "失败",
    "中")

log("O6", "订单详情", "查看发票入口", 
    "通过" if any("查看发票" in t for t in texts) else "失败",
    "中")

log("O7", "订单详情", "操作按钮（取消/支付/收货）", 
    "通过" if any(kw in str(texts) for kw in ["取消订单", "去支付", "确认收货", "再次购买"]) else "未找到",
    "低", "已完成订单可能无操作按钮")

# 返回
d.press("back")
time.sleep(1)

# ========== 验证6: 我的 ==========
print("\n" + "="*60, flush=True)
print("验证6: 我的", flush=True)
print("="*60)

d.click(*TAB_HOME)
time.sleep(1)
d.click(*MY_BUTTON)
time.sleep(2)
screenshot("09_my_page")
texts = get_texts()

log("M1", "我的", "设置入口", 
    "通过" if any("设置" in t for t in texts) else "失败",
    "中")

log("M2", "我的", "关于入口", 
    "通过" if any("关于" in t for t in texts) else "失败",
    "低")

log("M3", "我的", "反馈入口", 
    "通过" if any("反馈" in t for t in texts) else "失败",
    "低")

# ========== 汇总 ==========
print("\n" + "="*60, flush=True)
print("验证汇总", flush=True)
print("="*60)

passed = [r for r in results if r["状态"] == "通过"]
failed = [r for r in results if r["状态"] == "失败"]
pending = [r for r in results if r["状态"] == "未找到" or r["状态"] == "待验证"]

print(f"\n总计: {len(results)} 项", flush=True)
print(f"  ✅ 通过: {len(passed)}", flush=True)
print(f"  ❌ 失败: {len(failed)}", flush=True)
print(f"  ⚠️ 待验证/未找到: {len(pending)}", flush=True)

if failed:
    print(f"\n失败项详情:", flush=True)
    for r in failed:
        print(f"  #{r['ID']} [{r['模块']}] {r['问题描述']} ({r['严重程度']})", flush=True)
        if r['详情']:
            print(f"      {r['详情']}", flush=True)

# 保存结果
result_file = os.path.join(os.path.dirname(__file__), " reverify_results", "verification_report.json")
with open(result_file, "w", encoding="utf-8") as f:
    json.dump({
        "验证时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "总计": len(results),
        "通过": len(passed),
        "失败": len(failed),
        "待验证": len(pending),
        "详细结果": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n报告: {result_file}", flush=True)