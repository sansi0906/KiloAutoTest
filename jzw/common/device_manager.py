"""
津筑网App自动化测试 - 设备管理模块
封装uiautomator2连接和基础ADB操作
"""
import uiautomator2 as u2
import subprocess
import time
import os


class DeviceManager:
    """管理Android设备连接"""

    def __init__(self, package_name):
        self.package = package_name
        self.d = None

    def connect(self):
        """连接设备并初始化uiautomator2"""
        print("\n🔗 正在连接设备...")
        self.d = u2.connect()
        self.d.implicitly_wait(10.0)  # 隐式等待10秒

        info = self.d.info
        print(f"  ✅ 设备已连接: {info.get('productName', 'unknown')}")
        print(f"  📱 屏幕尺寸: {self.d.window_size()}")
        print(f"  📦 目标包名: {self.package}")

        # 启动atx-agent
        self.d.settings["wait_timeout"] = 15
        self.d.settings["operation_timeout"] = 10
        return self.d

    @property
    def width(self):
        return self.d.window_size()[0]

    @property
    def height(self):
        return self.d.window_size()[1]

    def launch_app(self):
        """启动津筑网App"""
        print("🚀 启动津筑网App...")
        self.d.app_start(self.package, stop=False)
        time.sleep(3)

    def stop_app(self):
        """停止津筑网App"""
        self.d.app_stop(self.package)
        print("🛑 App已停止")

    def is_app_foreground(self):
        """检查App是否在前台"""
        current = self.d.app_current()
        return current.get("package") == self.package

    def screenshot(self, name="screenshot"):
        """截图并保存"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "screenshots", f"{name}.png")
        self.d.screenshot(path)
        print(f"  📸 截图: {path}")
        return path

    def dump_hierarchy(self):
        """获取当前页面UI层级XML"""
        return self.d.dump_hierarchy()

    def press_back(self):
        """按返回键"""
        self.d.press("back")
        time.sleep(1)

    def press_home(self):
        """按Home键"""
        self.d.press("home")
        time.sleep(1)

    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        # 保持App运行，只断开uiautomator2连接
        self.d.settings["operation_delay"] = 0
        print("  ✅ 清理完成")
