"""
乐云台 App - 全面探索脚本（带Tab校准）
Tab坐标已校准：首页(135,2256), 客户(405,2256), 购物车(675,2256), 订单(945,2256)
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

class Explorer:
    TAB_HOME = (135, 2256)
    TAB_CUSTOMER = (405, 2256)
    TAB_CART = (675, 2256)
    TAB_ORDER = (945, 2256)
    MY_BUTTON = (1011, 138)  # 右上角"我的"按钮（三个竖点区域）
    
    def __init__(self):
        self.d = None
        self.issues = []
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), "explore_results")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.step = 0
        
    def connect(self):
        print("连接设备...", flush=True)
        self.d = u2.connect()
        self.d.implicitly_wait(10.0)
        print(f"✓ 设备: {self.d.info.get('productName', 'unknown')}", flush=True)
        
        # 停止钉钉，确保乐云台在前台
        current = self.d.app_current()
        if current.get('package') == "com.alibaba.android.rimet":
            print("  停止钉钉...", flush=True)
            self.d.app_stop("com.alibaba.android.rimet")
            time.sleep(2)
        
        # 确保乐云台在前台
        current = self.d.app_current()
        if current.get('package') != PACKAGE:
            print(f"  启动 {PACKAGE}...", flush=True)
            self.d.app_start(PACKAGE, stop=False)
            time.sleep(3)
        
        return self
    
    def screenshot(self, name):
        self.step += 1
        path = os.path.join(self.screenshot_dir, f"{self.step:03d}_{name}.png")
        self.d.screenshot(path)
        print(f"  📷 {name}", flush=True)
        return path
    
    def log_issue(self, module, description, severity="中", detail=""):
        issue = {
            "序号": len(self.issues) + 1,
            "模块": module,
            "问题": description,
            "严重程度": severity,
            "详情": detail,
            "时间": datetime.now().strftime("%H:%M:%S")
        }
        self.issues.append(issue)
        print(f"  ❌ ISSUE #{issue['序号']}: [{module}] {description}", flush=True)
        if detail:
            print(f"     详情: {detail}", flush=True)
    
    def go_tab(self, tab_name, wait=2):
        """点击指定Tab，先回首页确保状态正确"""
        tabs = {
            "home": self.TAB_HOME,
            "customer": self.TAB_CUSTOMER,
            "cart": self.TAB_CART,
            "order": self.TAB_ORDER,
        }
        
        # 先回首页（除非已经在首页）
        if tab_name != "home":
            self.d.click(*self.TAB_HOME)
            time.sleep(1)
        
        # 点击目标Tab
        coord = tabs.get(tab_name)
        if coord:
            self.d.click(*coord)
            time.sleep(wait)
            self.dismiss_popups()
            return True
        return False
    
    def dismiss_popups(self):
        popups = ["同意", "允许", "确定", "忽略本次", "我知道了", "关闭", "始终允许", "仅本次允许"]
        for text in popups:
            if self.d(text=text).exists(timeout=0.3):
                self.d(text=text).click()
                time.sleep(0.5)
    
    def get_texts(self):
        xml = self.d.dump_hierarchy()
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]
    
    def scroll_down(self, duration=0.5):
        self.d.swipe(0.5, 0.7, 0.5, 0.3, duration=duration)
        time.sleep(1.5)
    
    def scroll_up(self, duration=0.5):
        self.d.swipe(0.5, 0.3, 0.5, 0.7, duration=duration)
        time.sleep(1.5)
    
    def click_back(self):
        self.d.press("back")
        time.sleep(1.5)
    
    def explore_home(self):
        """探索首页"""
        print("\n▶ 探索首页...", flush=True)
        self.go_tab("home")
        self.screenshot("home_overview")
        
        texts = self.get_texts()
        print(f"  首页前15个文本: {texts[:15]}", flush=True)
        
        # 验证首页元素
        home_elements = ["杨涛轩", "营销333", "销售额", "客户", "订单"]
        found = [e for e in home_elements if any(e in t for t in texts)]
        missing = [e for e in home_elements if e not in found]
        
        if missing:
            self.log_issue("首页", f"首页元素缺失: {missing}", "中")
        else:
            print(f"  ✓ 首页元素完整", flush=True)
        
        # 下拉刷新
        self.d.swipe(0.5, 0.3, 0.5, 0.8, duration=0.8)
        time.sleep(1)
        self.screenshot("home_refresh")
        
        # 滑动到底部
        for _ in range(3):
            self.scroll_down()
        self.screenshot("home_bottom")
        
        # 滑回顶部
        for _ in range(3):
            self.scroll_up()
        
        # 检查功能入口
        entries = ["设备", "建材", "人才", "服务"]
        for entry in entries:
            if self.d(text=entry).exists(timeout=1):
                print(f"  ✓ 功能入口: {entry}", flush=True)
            else:
                self.log_issue("首页", f"功能入口缺失: {entry}", "低")
        
        # 点击设备入口
        if self.d(text="设备").exists(timeout=1):
            self.d(text="设备").click()
            time.sleep(2)
            self.screenshot("device_list")
            
            # 检查搜索框
            search = self.d(className="android.widget.EditText")
            if search.exists:
                print(f"  ✓ 设备列表搜索框存在", flush=True)
            
            # 检查商品卡片
            goods_indicators = ["设备出售", "元/台", "加入购物车", "拨打电话"]
            found_goods = [g for g in goods_indicators if self.d(textContains=g).exists(timeout=1)]
            print(f"  ✓ 设备列表元素: {found_goods}", flush=True)
            
            # 点击第一个商品
            self.d.click(312, 800)
            time.sleep(2)
            self.screenshot("device_detail")
            
            # 检查详情页
            detail_checks = ["加入购物车", "立即购买", "收藏"]
            found_detail = [c for c in detail_checks if self.d(text=c).exists(timeout=1)]
            print(f"  ✓ 设备详情页元素: {found_detail}", flush=True)
            
            if "加入购物车" in found_detail:
                # 测试加入购物车
                self.d(text="加入购物车").click()
                time.sleep(1)
                self.screenshot("add_cart_dialog")
                
                # 检查是否有规格选择
                spec_checks = ["规格", "数量", "确定", "确认"]
                found_spec = [s for s in spec_checks if self.d(text=s).exists(timeout=1)]
                print(f"  ✓ 加入购物车弹窗元素: {found_spec}", flush=True)
                
                if found_spec:
                    self.log_issue("购物车", "加入购物车需选择规格/弹窗异常", "低")
                
                self.click_back()  # 关闭弹窗
                self.click_back()  # 返回详情
            else:
                self.log_issue("设备详情", "加入购物车按钮未找到", "高")
            
            self.click_back()  # 返回列表
            time.sleep(1)
    
    def explore_customer(self):
        """探索客户管理"""
        print("\n▶ 探索客户管理...", flush=True)
        self.go_tab("customer")
        self.screenshot("customer_overview")
        
        texts = self.get_texts()
        print(f"  客户页前15个文本: {texts[:15]}", flush=True)
        
        # 检查搜索功能
        if self.d(className="android.widget.EditText").exists:
            print(f"  ✓ 客户搜索框存在", flush=True)
        else:
            self.log_issue("客户管理", "搜索框未找到", "高")
        
        # 检查筛选
        if self.d(text="筛选").exists(timeout=1):
            print(f"  ✓ 筛选按钮存在", flush=True)
        else:
            self.log_issue("客户管理", "筛选按钮不明显", "中")
        
        # 检查新增客户
        add_keywords = ["新增", "添加客户", "手动录入"]
        found_add = [k for k in add_keywords if self.d(textContains=k).exists(timeout=1)]
        if found_add:
            print(f"  ✓ 新增客户入口: {found_add}", flush=True)
        else:
            self.log_issue("客户管理", "新增客户入口不明显", "低")
        
        # 点击第一个客户
        self.d.click(312, 600)
        time.sleep(2)
        self.screenshot("customer_detail")
        
        # 检查客户详情
        detail_elements = ["联系人", "联系电话", "信用代码", "营业执照"]
        found_detail = [e for e in detail_elements if self.d(textContains=e).exists(timeout=1)]
        print(f"  ✓ 客户详情元素: {found_detail}", flush=True)
        
        # 检查拨打电话
        if self.d(text="拨打电话").exists(timeout=1) or self.d(text="呼叫").exists(timeout=1):
            print(f"  ✓ 拨打电话按钮存在", flush=True)
        else:
            self.log_issue("客户详情", "拨打电话入口未找到", "中")
        
        self.click_back()  # 返回列表
        time.sleep(1)
        
        # 测试搜索
        search = self.d(className="android.widget.EditText")
        if search.exists:
            search.click()
            search.set_text("测试")
            time.sleep(1)
            self.screenshot("customer_search")
            self.d.press("enter")
            time.sleep(2)
            self.screenshot("customer_search_result")
    
    def explore_cart(self):
        """探索购物车"""
        print("\n▶ 探索购物车...", flush=True)
        self.go_tab("cart")
        self.screenshot("cart_overview")
        
        texts = self.get_texts()
        print(f"  购物车前15个文本: {texts[:15]}", flush=True)
        
        # 检查购物车状态
        if self.d(text="暂无商品").exists() or self.d(text="去逛逛").exists():
            print(f"  ⚠ 购物车为空", flush=True)
            self.log_issue("购物车", "购物车为空，无法验证结算流程", "中", "需先添加商品到购物车")
        else:
            # 检查管理按钮
            if self.d(text="管理").exists(timeout=1):
                print(f"  ✓ 管理按钮存在", flush=True)
                self.d(text="管理").click()
                time.sleep(1)
                self.screenshot("cart_manage")
                
                # 检查全选
                if self.d(text="全选").exists(timeout=1):
                    print(f"  ✓ 全选按钮存在", flush=True)
                    self.d(text="全选").click()
                    time.sleep(0.5)
                
                # 检查结算
                if self.d(text="结算").exists(timeout=1):
                    print(f"  ✓ 结算按钮存在", flush=True)
                    self.screenshot("cart_with_checkout")
                    
                    # 点击结算测试
                    self.d(text="结算").click()
                    time.sleep(2)
                    self.screenshot("checkout_process")
                    
                    # 检查结算页面
                    checkout_checks = ["收货地址", "支付", "提交订单"]
                    found_checkout = [c for c in checkout_checks if self.d(textContains=c).exists(timeout=1)]
                    print(f"  ✓ 结算流程元素: {found_checkout}", flush=True)
                    
                    if not found_checkout:
                        self.log_issue("购物车", "结算流程异常", "高")
                    
                    self.click_back()
                    self.click_back()
                else:
                    self.log_issue("购物车", "结算按钮未找到", "高")
                
                # 取消管理
                if self.d(text="完成").exists(timeout=1):
                    self.d(text="完成").click()
                    time.sleep(0.5)
            else:
                self.log_issue("购物车", "管理按钮未找到", "中")
    
    def explore_order(self):
        """探索订单列表"""
        print("\n▶ 探索订单列表...", flush=True)
        self.go_tab("order")
        self.screenshot("order_overview")
        
        texts = self.get_texts()
        print(f"  订单前15个文本: {texts[:15]}", flush=True)
        
        # 检查订单Tab
        order_tabs = ["全部", "待付款", "待发货", "待收货", "已完成", "客户订单", "记录订单"]
        found_tabs = [t for t in order_tabs if self.d(text=t).exists(timeout=1)]
        print(f"  ✓ 订单Tab: {found_tabs}", flush=True)
        
        # 遍历订单Tab
        for tab in found_tabs[:3]:  # 只检查前3个避免耗时太长
            if self.d(text=tab).exists(timeout=1):
                self.d(text=tab).click()
                time.sleep(2)
                self.screenshot(f"order_tab_{tab}")
                
                # 检查订单卡片
                order_indicators = ["订单编号", "下单时间", "金额", "客户"]
                found_order_indicators = [i for i in order_indicators if self.d(textContains=i).exists(timeout=1)]
                print(f"  {tab} - 订单卡片元素: {found_order_indicators}", flush=True)
                
                # 点击第一个订单
                self.d.click(540, 500)
                time.sleep(2)
                self.screenshot(f"order_detail_{tab}")
                
                # 检查订单详情
                detail_checks = ["订单编号", "收货地址", "查看协议", "查看发票"]
                found_detail = [c for c in detail_checks if self.d(textContains=c).exists(timeout=1)]
                print(f"  {tab} - 订单详情元素: {found_detail}", flush=True)
                
                # 检查操作按钮
                action_checks = ["取消订单", "去支付", "确认收货", "再次购买", "评价"]
                found_actions = [a for a in action_checks if self.d(text=a).exists(timeout=1)]
                
                if found_actions:
                    print(f"  {tab} - 订单操作: {found_actions}", flush=True)
                else:
                    self.log_issue("订单详情", f"{tab}订单操作按钮未显示", "低", "可能受订单状态影响")
                
                self.click_back()  # 返回列表
                time.sleep(1)
    
    def explore_my(self):
        """探索'我的'（右上角三个竖点）"""
        print("\n▶ 探索我的页面...", flush=True)
        
        # 从首页点击右上角
        self.go_tab("home")
        time.sleep(1)
        
        # 点击右上角三个竖点
        self.d.click(*self.MY_BUTTON)
        time.sleep(2)
        self.screenshot("my_page")
        
        texts = self.get_texts()
        print(f"  我的页面前15个文本: {texts[:15]}", flush=True)
        
        # 检查菜单项
        my_items = ["个人中心", "账号管理", "设置", "退出登录", "关于", "帮助", "反馈"]
        found_items = [i for i in my_items if self.d(text=i).exists(timeout=1)]
        
        if found_items:
            print(f"  ✓ 我的菜单项: {found_items}", flush=True)
        else:
            # 可能是其他页面，检查当前页面
            if "客户详情" in texts or "联系人" in texts:
                print(f"  ⚠ 点击到了客户详情页而非'我的'", flush=True)
                self.log_issue("导航", "右上角'我的'按钮坐标不准确", "高", f"当前页面: {texts[:5]}")
            else:
                self.log_issue("导航", "右上角'我的'按钮未响应", "高")
        
        # 尝试点击菜单项
        for item in found_items[:2]:
            if self.d(text=item).exists(timeout=1):
                self.d(text=item).click()
                time.sleep(2)
                self.screenshot(f"my_{item}")
                self.click_back()
                time.sleep(1)
    
    def explore_all(self):
        """执行全面探索"""
        print("\n" + "="*60, flush=True)
        print("乐云台 App 全面功能探索", flush=True)
        print("="*60, flush=True)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        
        try:
            self.connect()
            
            # 确认App在前台
            current = self.d.app_current()
            if current.get("package") != PACKAGE:
                print(f"启动 {PACKAGE}...", flush=True)
                self.d.app_start(PACKAGE)
                time.sleep(3)
            
            self.screenshot("00_start")
            
            self.explore_home()
            self.explore_customer()
            self.explore_cart()
            self.explore_order()
            self.explore_my()
            
        except Exception as e:
            print(f"\n❌ 探索出错: {e}", flush=True)
            import traceback
            traceback.print_exc()
            self.screenshot("error_state")
        
        self.save_results()
    
    def save_results(self):
        print("\n" + "="*60, flush=True)
        print("探索完成 - 问题汇总", flush=True)
        print("="*60, flush=True)
        
        if self.issues:
            # 按严重程度排序
            severity_order = {"高": 0, "中": 1, "低": 2}
            self.issues.sort(key=lambda x: severity_order.get(x["严重程度"], 99))
            
            print(f"\n发现 {len(self.issues)} 个问题:", flush=True)
            
            # 按严重程度分组
            for severity in ["高", "中", "低"]:
                group = [i for i in self.issues if i["严重程度"] == severity]
                if group:
                    print(f"\n【{severity}】", flush=True)
                    for issue in group:
                        print(f"  #{issue['序号']} [{issue['模块']}] {issue['问题']}", flush=True)
                        if issue['详情']:
                            print(f"      {issue['详情']}", flush=True)
        else:
            print("\n✓ 未发现明显问题", flush=True)
        
        # 保存JSON
        result_file = os.path.join(self.screenshot_dir, "explore_issues.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "探索时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "问题总数": len(self.issues),
                "问题列表": self.issues
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果: {result_file}", flush=True)

if __name__ == "__main__":
    explorer = Explorer()
    explorer.explore_all()