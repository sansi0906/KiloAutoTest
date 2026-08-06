"""
乐云台 App - 逐步探索脚本（不使用返回键）
策略：每步操作前先启动App，确保状态干净
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

class Explorer:
    TAB_HOME = (135, 2256)
    TAB_CUSTOMER = (405, 2256)
    TAB_CART = (675, 2256)
    TAB_ORDER = (945, 2256)
    MY_BUTTON = (1011, 138)
    
    def __init__(self):
        self.d = None
        self.issues = []
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), "explore_results_v3")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.step = 0
        
    def connect(self):
        print("连接设备...", flush=True)
        self.d = u2.connect()
        self.d.implicitly_wait(10.0)
        print(f"✓ 设备: {self.d.info.get('productName', 'unknown')}", flush=True)
        return self
    
    def restart_app(self):
        """重启App，确保状态干净"""
        current = self.d.app_current()
        if current.get('package') == DINGTALK:
            self.d.app_stop(DINGTALK)
            time.sleep(1)
        
        self.d.app_start(PACKAGE, stop=True)
        time.sleep(4)
        self.d.click(*self.TAB_HOME)  # 确保在首页
        time.sleep(2)
    
    def screenshot(self, name):
        self.step += 1
        path = os.path.join(self.screenshot_dir, f"{self.step:03d}_{name}.png")
        self.d.screenshot(path)
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
        print(f"  ❌ #{issue['序号']} [{module}] {description}", flush=True)
        if detail:
            print(f"     {detail}", flush=True)
    
    def get_texts(self):
        xml = self.d.dump_hierarchy()
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]
    
    def go_tab(self, tab_name):
        """切换到指定Tab"""
        tabs = {
            "home": self.TAB_HOME,
            "customer": self.TAB_CUSTOMER,
            "cart": self.TAB_CART,
            "order": self.TAB_ORDER,
        }
        coord = tabs.get(tab_name)
        if coord:
            self.d.click(*coord)
            time.sleep(3)
        return self.get_texts()
    
    def explore(self):
        print("\n" + "="*60, flush=True)
        print("乐云台 App 逐步探索 v3", flush=True)
        print("="*60, flush=True)
        
        try:
            self.connect()
            
            # ========== 1. 首页 ==========
            print("\n--- 1. 首页 ---", flush=True)
            self.restart_app()
            self.screenshot("home")
            
            texts = self.get_texts()
            home_checks = [
                ("杨涛轩", "用户名"),
                ("营销333", "营销账号"),
                ("销售额", "业绩数据"),
                ("客户", "客户数量"),
                ("订单(笔)", "订单数量"),
                ("设备", "功能入口"),
                ("建材", "功能入口"),
                ("人才", "功能入口"),
                ("服务", "功能入口"),
            ]
            
            for keyword, desc in home_checks:
                if any(keyword in t for t in texts):
                    print(f"  ✓ {desc}: {keyword}", flush=True)
                else:
                    self.log_issue("首页", f"{desc}缺失", "中" if "入口" in desc else "低")
            
            # ========== 2. 设备列表 ==========
            print("\n--- 2. 设备列表 ---", flush=True)
            self.restart_app()  # 重启确保干净
            self.d(text="设备").click()
            time.sleep(2)
            self.screenshot("device_list")
            
            texts = self.get_texts()
            device_checks = ["搜索", "设备出售", "加入购物车", "拨打电话"]
            for check in device_checks:
                if any(check in t for t in texts):
                    print(f"  ✓ {check}", flush=True)
                else:
                    self.log_issue("设备列表", f"{check}缺失", "中" if check in ["加入购物车", "拨打电话"] else "低")
            
            # 点击第一个商品进入详情
            if any("加入购物车" in t for t in texts):
                self.d.click(312, 600)
                time.sleep(2)
                self.screenshot("device_detail")
                
                texts = self.get_texts()
                if any("加入购物车" in t for t in texts):
                    print(f"  ✓ 设备详情-加入购物车", flush=True)
                else:
                    self.log_issue("设备详情", "加入购物车按钮未找到", "高")
            
            # ========== 3. 客户管理 ==========
            print("\n--- 3. 客户管理 ---", flush=True)
            self.restart_app()
            texts = self.go_tab("customer")
            self.screenshot("customer_list")
            
            customer_checks = [
                ("搜索", "搜索框"),
                ("筛选", "筛选按钮"),
                ("待审核", "客户状态Tab"),
                ("已入驻", "客户状态Tab"),
                ("手动录入", "新增客户入口"),
            ]
            
            for keyword, desc in customer_checks:
                if any(keyword in t for t in texts):
                    print(f"  ✓ {desc}: {keyword}", flush=True)
                else:
                    self.log_issue("客户管理", f"{desc}不明显", "中")
            
            # 点击第一个客户
            if self.d(textContains="联系人").exists(timeout=1):
                self.d.click(312, 500)
                time.sleep(2)
                self.screenshot("customer_detail")
                
                texts = self.get_texts()
                if any("联系电话" in t for t in texts):
                    print(f"  ✓ 客户详情-联系电话", flush=True)
                else:
                    self.log_issue("客户详情", "联系电话未找到", "中")
                
                if any("拨打电话" in t for t in texts) or any("呼叫" in t for t in texts):
                    print(f"  ✓ 拨打电话入口", flush=True)
                else:
                    self.log_issue("客户详情", "拨打电话入口未找到", "中")
            
            # ========== 4. 购物车 ==========
            print("\n--- 4. 购物车 ---", flush=True)
            self.restart_app()
            texts = self.go_tab("cart")
            self.screenshot("cart")
            
            cart_checks = ["购物车", "管理", "全选", "结算", "合计"]
            for check in cart_checks:
                if any(check in t for t in texts):
                    print(f"  ✓ 购物车: {check}", flush=True)
                else:
                    if check in ["结算", "合计"]:
                        self.log_issue("购物车", f"{check}未找到", "高")
                    elif check == "管理":
                        self.log_issue("购物车", "管理按钮未找到", "中")
            
            # 如果有"管理"但没"结算"，点击管理后再检查
            if any("管理" in t for t in texts) and not any("结算" in t for t in texts):
                print("  尝试点击管理查找结算...", flush=True)
                for text in texts:
                    if "管理" in text:
                        try:
                            self.d(text=text).click()
                            time.sleep(1)
                            texts2 = self.get_texts()
                            
                            if any("结算" in t for t in texts2) or any("合计" in t for t in texts2):
                                print(f"  ✓ 点击管理后出现结算/合计", flush=True)
                                self.log_issue("购物车", "有商品但结算按钮不直接显示，需点击管理才出现", "高", "UI逻辑不合理")
                            
                            # 取消管理
                            if any("完成" in t for t in texts2):
                                for t in texts2:
                                    if "完成" in t:
                                        self.d(text=t).click()
                                        time.sleep(0.5)
                                        break
                            break
                        except:
                            pass
            
            # ========== 5. 订单 ==========
            print("\n--- 5. 订单列表 ---", flush=True)
            self.restart_app()
            texts = self.go_tab("order")
            self.screenshot("order")
            
            order_checks = ["全部", "客户订单", "记录订单", "订单编号", "查看协议", "查看发票"]
            for check in order_checks:
                if any(check in t for t in texts):
                    print(f"  ✓ 订单: {check}", flush=True)
                else:
                    self.log_issue("订单列表", f"{check}缺失", "中" if check in ["查看协议", "查看发票"] else "低")
            
            # 点击第一个订单
            if any("订单编号" in t for t in texts):
                self.d.click(540, 500)
                time.sleep(2)
                self.screenshot("order_detail")
                
                texts = self.get_texts()
                action_checks = ["取消订单", "去支付", "确认收货", "再次购买"]
                found_actions = [a for a in action_checks if any(a in t for t in texts)]
                
                if found_actions:
                    print(f"  ✓ 订单操作: {found_actions}", flush=True)
                else:
                    self.log_issue("订单详情", "订单操作按钮未显示", "低", "已完成订单可能无操作按钮")
            
            # ========== 6. 我的 ==========
            print("\n--- 6. 我的 ---", flush=True)
            self.restart_app()
            self.d.click(*self.MY_BUTTON)
            time.sleep(2)
            self.screenshot("my_page")
            
            texts = self.get_texts()
            my_checks = ["设置", "关于", "反馈"]
            found_my = [c for c in my_checks if any(c in t for t in texts)]
            
            if found_my:
                print(f"  ✓ 我的: {found_my}", flush=True)
            else:
                self.log_issue("我的", "菜单未正确显示", "高")
            
        except Exception as e:
            print(f"\n❌ 探索出错: {e}", flush=True)
            import traceback
            traceback.print_exc()
            self.screenshot("error")
        
        self.save_results()
    
    def save_results(self):
        print("\n" + "="*60, flush=True)
        print("探索完成 - 问题汇总", flush=True)
        print("="*60, flush=True)
        
        if self.issues:
            severity_order = {"高": 0, "中": 1, "低": 2}
            self.issues.sort(key=lambda x: severity_order.get(x["严重程度"], 99))
            
            print(f"\n发现 {len(self.issues)} 个问题:", flush=True)
            
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
        
        result_file = os.path.join(self.screenshot_dir, "explore_issues.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "探索时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "问题总数": len(self.issues),
                "问题列表": self.issues
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果: {result_file}", flush=True)

if __name__ == "__main__":
    Explorer().explore()