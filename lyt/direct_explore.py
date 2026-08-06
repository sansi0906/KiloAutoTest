"""
乐云台 App - 直接探索脚本（从已登录状态开始）
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

class DirectExplorer:
    # 底部导航坐标 (1080x2400) - 营销角色可能的Tab
    # 根据手工报告：首页、客户、购物车、订单
    TAB_COORDS = {
        "首页": (180, 2280),    # 左侧第一个
        "客户": (360, 2280),    # 第二个
        "购物车": (720, 2280),  # 第三个
        "订单": (900, 2280),    # 右侧
    }
    
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
    
    def click_tab(self, tab_name):
        """点击底部Tab"""
        coord = self.TAB_COORDS.get(tab_name)
        if coord:
            self.d.click(*coord)
            time.sleep(2)
            self.dismiss_popups()
            return True
        return False
    
    def dismiss_popups(self):
        """关闭弹窗"""
        popups = ["同意", "允许", "确定", "忽略本次", "我知道了", "关闭", "始终允许", "仅本次允许"]
        for text in popups:
            if self.d(text=text).exists(timeout=0.3):
                self.d(text=text).click()
                time.sleep(0.5)
    
    def get_current_texts(self):
        """获取当前界面所有文本"""
        xml = self.d.dump_hierarchy()
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]
    
    def explore_tab(self, tab_name, actions):
        """探索某个Tab"""
        print(f"\n▶ 探索 {tab_name}...", flush=True)
        
        if not self.click_tab(tab_name):
            self.log_issue("导航", f"无法点击 {tab_name} Tab", "高")
            return
        
        self.screenshot(f"{tab_name}_01_overview")
        
        texts = self.get_current_texts()
        print(f"  当前页面文本: {texts[:15]}...", flush=True)
        
        # 执行指定操作
        for action in actions:
            self.perform_action(action)
    
    def perform_action(self, action):
        """执行单个操作"""
        action_type = action.get("type")
        
        if action_type == "scroll_down":
            self.d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
            time.sleep(1)
            self.screenshot(action.get("name", "scroll_down"))
        
        elif action_type == "scroll_up":
            self.d.swipe(0.5, 0.3, 0.5, 0.7, duration=0.5)
            time.sleep(1)
            self.screenshot(action.get("name", "scroll_up"))
        
        elif action_type == "click_text":
            text = action.get("text")
            if self.d(text=text).exists(timeout=2):
                self.d(text=text).click()
                time.sleep(2)
                self.dismiss_popups()
                self.screenshot(action.get("name", f"click_{text}"))
                
                # 检查操作结果
                if action.get("check"):
                    self.check_result(action.get("check"))
                
                # 返回
                if action.get("back_after"):
                    self.d.press("back")
                    time.sleep(1)
            else:
                if action.get("required"):
                    self.log_issue(action.get("module", "未知"), f"{text} 未找到", action.get("severity", "中"))
        
        elif action_type == "click_coord":
            x, y = action.get("coord", (540, 1200))
            self.d.click(x, y)
            time.sleep(2)
            self.dismiss_popups()
            self.screenshot(action.get("name", "click_coord"))
            
            if action.get("back_after"):
                self.d.press("back")
                time.sleep(1)
    
    def check_result(self, check_desc):
        """检查操作结果"""
        texts = self.get_current_texts()
        expected = check_desc.get("expected_texts", [])
        
        for exp in expected:
            if exp not in texts:
                self.log_issue(check_desc.get("module", "未知"), f"未找到预期文本: {exp}", "低")
    
    def explore_all(self):
        """执行全面探索"""
        print("\n" + "="*60, flush=True)
        print("乐云台 App 全面功能探索", flush=True)
        print("="*60, flush=True)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        
        try:
            self.connect()
            
            # 确认 App 在前台
            current = self.d.app_current()
            if current.get("package") != PACKAGE:
                print(f"启动 {PACKAGE}...", flush=True)
                self.d.app_start(PACKAGE)
                time.sleep(3)
            
            self.screenshot("00_initial_state")
            
            # 1. 探索首页
            self.explore_tab("首页", [
                {"type": "scroll_down", "name": "home_scroll_down"},
                {"type": "scroll_up", "name": "home_scroll_up"},
            ])
            
            # 2. 探索客户
            self.explore_tab("客户", [
                {"type": "scroll_down", "name": "customer_scroll"},
            ])
            
            # 3. 探索购物车
            self.explore_tab("购物车", [
                {"type": "scroll_down", "name": "cart_scroll"},
            ])
            
            # 4. 探索订单
            self.explore_tab("订单", [
                {"type": "scroll_down", "name": "orders_scroll"},
            ])
            
            # 5. 尝试点击商品列表项
            print("\n▶ 探索商品详情...", flush=True)
            self.d.click(540, 600)  # 点击屏幕中间的商品
            time.sleep(2)
            self.screenshot("goods_detail")
            
            # 检查详情页元素
            detail_elements = ["加入购物车", "立即购买", "收藏", "分享", "拨打电话"]
            found = []
            for elem in detail_elements:
                if self.d(text=elem).exists(timeout=1):
                    found.append(elem)
            
            print(f"  商品详情页元素: {found}", flush=True)
            
            if "立即购买" not in found and "加入购物车" not in found:
                self.log_issue("商品详情", "购买/加入购物车按钮缺失", "中")
            
            # 测试加入购物车
            if self.d(text="加入购物车").exists(timeout=1):
                self.d(text="加入购物车").click()
                time.sleep(1)
                self.screenshot("add_cart_result")
                self.d.press("back")
                time.sleep(1)
            
            self.d.press("back")
            time.sleep(1)
            
            # 6. 探索分类入口（设备、建材、人才、服务）
            print("\n▶ 探索分类入口...", flush=True)
            categories = ["设备", "建材", "人才", "服务"]
            for cat in categories:
                if self.d(text=cat).exists(timeout=1):
                    self.d(text=cat).click()
                    time.sleep(2)
                    self.screenshot(f"category_{cat}")
                    self.d.press("back")
                    time.sleep(1)
            
            # 7. 探索搜索
            print("\n▶ 探索搜索...", flush=True)
            search_box = self.d(className="android.widget.EditText")
            if search_box.exists:
                search_box.click()
                search_box.set_text("测试")
                time.sleep(1)
                self.d.press("enter")
                time.sleep(2)
                self.screenshot("search_result")
                self.d.press("back")
                time.sleep(1)
            
        except Exception as e:
            print(f"\n❌ 探索出错: {e}", flush=True)
            self.screenshot("error_state")
        
        self.save_results()
    
    def save_results(self):
        """保存结果"""
        print("\n" + "="*60, flush=True)
        print("探索完成 - 问题汇总", flush=True)
        print("="*60, flush=True)
        
        if self.issues:
            print(f"\n发现 {len(self.issues)} 个问题:", flush=True)
            for issue in self.issues:
                print(f"\n#{issue['序号']} [{issue['模块']}] {issue['问题']}", flush=True)
                print(f"   严重程度: {issue['严重程度']}", flush=True)
                if issue['详情']:
                    print(f"   详情: {issue['详情']}", flush=True)
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
    explorer = DirectExplorer()
    explorer.explore_all()