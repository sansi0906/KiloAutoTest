"""
乐云台 App - 全面探索脚本 v2（更稳健的Tab切换）
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
    # 坐标已校准
    TAB_HOME = (135, 2256)
    TAB_CUSTOMER = (405, 2256)
    TAB_CART = (675, 2256)
    TAB_ORDER = (945, 2256)
    MY_BUTTON = (1011, 138)
    
    def __init__(self):
        self.d = None
        self.issues = []
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), "explore_results_v2")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.step = 0
        
    def connect(self):
        print("连接设备...", flush=True)
        self.d = u2.connect()
        self.d.implicitly_wait(10.0)
        print(f"✓ 设备: {self.d.info.get('productName', 'unknown')}", flush=True)
        
        # 停止钉钉
        current = self.d.app_current()
        if current.get('package') == DINGTALK:
            print("  停止钉钉...", flush=True)
            self.d.app_stop(DINGTALK)
            time.sleep(2)
        
        # 确保乐云台在前台
        current = self.d.app_current()
        if current.get('package') != PACKAGE:
            print(f"  启动 {PACKAGE}...", flush=True)
            self.d.app_start(PACKAGE)
            time.sleep(4)
        
        return self
    
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
    
    def get_texts(self):
        xml = self.d.dump_hierarchy()
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]
    
    def go_home(self):
        """回到首页 - 先按返回键再点击首页Tab"""
        # 先按返回键确保从详情页/弹窗中退出
        for _ in range(3):
            self.d.press("back")
            time.sleep(0.8)
        
        # 点击首页Tab
        self.d.click(*self.TAB_HOME)
        time.sleep(3)
        
        # 验证是否在首页
        texts = self.get_texts()
        if any("杨涛轩" in t or "营销333" in t for t in texts):
            return True
        else:
            # 再试一次
            self.d.click(*self.TAB_HOME)
            time.sleep(3)
            texts = self.get_texts()
            return any("杨涛轩" in t or "营销333" in t for t in texts)
    
    def go_tab(self, tab_name):
        """切换到指定Tab"""
        self.go_home()
        
        tabs = {
            "home": self.TAB_HOME,
            "customer": self.TAB_CUSTOMER,
            "cart": self.TAB_CART,
            "order": self.TAB_ORDER,
        }
        
        coord = tabs.get(tab_name)
        if coord and tab_name != "home":
            self.d.click(*coord)
            time.sleep(3)
        
        return self.get_texts()
    
    def press_back(self, count=1):
        """按返回键"""
        for _ in range(count):
            self.d.press("back")
            time.sleep(1)
    
    def explore(self):
        print("\n" + "="*60, flush=True)
        print("乐云台 App 全面功能探索 v2", flush=True)
        print("="*60, flush=True)
        
        try:
            self.connect()
            self.screenshot("00_start")
            
            # ========== 1. 首页 ==========
            print("\n--- 1. 首页 ---", flush=True)
            texts = self.go_tab("home")
            self.screenshot("home")
            
            # 验证首页元素
            home_checks = {
                "杨涛轩": "用户名",
                "营销333": "营销账号",
                "销售额": "业绩数据",
                "客户": "客户数量",
                "订单(笔)": "订单数量",
                "设备": "功能入口",
                "建材": "功能入口",
                "人才": "功能入口",
                "服务": "功能入口",
            }
            
            for keyword, desc in home_checks.items():
                if any(keyword in t for t in texts):
                    print(f"  ✓ {desc}: {keyword}", flush=True)
                else:
                    self.log_issue("首页", f"{desc}({keyword})缺失", "中" if "入口" in desc else "低")
            
            # ========== 2. 设备列表（从首页点击） ==========
            print("\n--- 2. 设备列表 ---", flush=True)
            if self.d(text="设备").exists(timeout=2):
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
                
                # 点击第一个商品
                self.d.click(312, 600)
                time.sleep(2)
                self.screenshot("device_detail")
                
                texts = self.get_texts()
                if any("加入购物车" in t for t in texts):
                    print(f"  ✓ 加入购物车按钮", flush=True)
                else:
                    self.log_issue("设备详情", "加入购物车按钮未找到", "高")
                
                # 返回首页
                self.press_back(2)
                time.sleep(1)
            else:
                self.log_issue("设备列表", "无法进入设备列表", "高")
            
            # ========== 3. 客户管理 ==========
            print("\n--- 3. 客户管理 ---", flush=True)
            texts = self.go_tab("customer")
            self.screenshot("customer_list")
            
            customer_checks = {
                "搜索": "搜索框",
                "筛选": "筛选按钮",
                "待审核": "客户状态Tab",
                "已入驻": "客户状态Tab",
                "手动录入": "新增客户入口",
            }
            
            for keyword, desc in customer_checks.items():
                if any(keyword in t for t in texts):
                    print(f"  ✓ {desc}: {keyword}", flush=True)
                else:
                    self.log_issue("客户管理", f"{desc}({keyword})不明显", "中")
            
            # 点击第一个客户查看详情
            if self.d(textContains="联系人").exists(timeout=1):
                self.d.click(312, 500)
                time.sleep(2)
                self.screenshot("customer_detail")
                
                texts = self.get_texts()
                detail_checks = ["联系人", "联系电话", "信用代码", "营业执照", "拨打电话"]
                for check in detail_checks:
                    if any(check in t for t in texts):
                        print(f"  ✓ 客户详情: {check}", flush=True)
                    elif check == "拨打电话":
                        self.log_issue("客户详情", "拨打电话入口未找到", "中")
                
                self.press_back()
                time.sleep(1)
            else:
                self.log_issue("客户管理", "无客户可查看", "低")
            
            # ========== 4. 购物车 ==========
            print("\n--- 4. 购物车 ---", flush=True)
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
            
            # 如果有"管理"按钮，点击后检查结算
            if any("管理" in t for t in texts) and not any("结算" in t for t in texts):
                print("  尝试点击管理后查找结算...", flush=True)
                # 找管理按钮
                for text in texts:
                    if "管理" in text:
                        try:
                            self.d(text=text).click()
                            time.sleep(1)
                            self.screenshot("cart_after_manage")
                            texts2 = self.get_texts()
                            
                            if any("结算" in t for t in texts2) or any("合计" in t for t in texts2):
                                print(f"  ✓ 点击管理后出现结算/合计", flush=True)
                                self.log_issue("购物车", "结算按钮需点击管理后才出现，逻辑不合理", "中", "有商品时应直接显示结算按钮")
                            
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
            texts = self.go_tab("order")
            self.screenshot("order")
            
            order_checks = {
                "全部": "订单Tab",
                "客户订单": "订单Tab",
                "记录订单": "订单Tab",
                "订单编号": "订单卡片",
                "查看协议": "订单详情",
                "查看发票": "订单详情",
            }
            
            for keyword, desc in order_checks.items():
                if any(keyword in t for t in texts):
                    print(f"  ✓ {desc}: {keyword}", flush=True)
                else:
                    self.log_issue("订单列表", f"{desc}({keyword})缺失", "中" if "订单详情" in desc else "低")
            
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
                    self.log_issue("订单详情", "订单操作按钮未显示（已完成订单无操作可能正常）", "低")
                
                self.press_back()
                time.sleep(1)
            
            # ========== 6. 我的 ==========
            print("\n--- 6. 我的 ---", flush=True)
            self.go_home()
            self.d.click(*self.MY_BUTTON)
            time.sleep(2)
            self.screenshot("my_page")
            
            texts = self.get_texts()
            my_checks = ["设置", "关于", "反馈", "个人中心", "账号管理", "退出登录"]
            found_my = [c for c in my_checks if any(c in t for t in texts)]
            
            if found_my:
                print(f"  ✓ 我的页面元素: {found_my}", flush=True)
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