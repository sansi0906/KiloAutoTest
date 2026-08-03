"""
乐云泰App自动化测试 - 设备管理模块
"""
import uiautomator2 as u2
import subprocess
import time
import os


class DeviceManager:
    def __init__(self, package_name):
        self.package = package_name
        self.d = None

    def connect(self):
        self.d = u2.connect()
        self.d.implicitly_wait(10.0)
        info = self.d.info
        print(f"  设备: {info.get('productName', 'unknown')}")
        print(f"  分辨率: {self.d.window_size()}")
        self.d.settings["wait_timeout"] = 15
        return self.d

    @property
    def width(self):
        return self.d.window_size()[0]

    @property
    def height(self):
        return self.d.window_size()[1]

    def launch_app(self):
        self.d.app_start(self.package, stop=False)
        time.sleep(3)

    def stop_app(self):
        self.d.app_stop(self.package)

    def is_app_foreground(self):
        current = self.d.app_current()
        return current.get("package") == self.package

    def screenshot(self, name="screenshot"):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "screenshots", f"{name}.png")
        self.d.screenshot(path)
        return path

    def dump_hierarchy(self):
        return self.d.dump_hierarchy()

    def press_back(self):
        self.d.press("back")
        time.sleep(1)

    def cleanup(self):
        pass
