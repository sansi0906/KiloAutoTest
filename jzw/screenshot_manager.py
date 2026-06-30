#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
截图管理器
负责管理测试过程中的截图
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime


class ScreenshotManager:
    def __init__(self, screenshot_dir):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_count = 0
        
    def take_screenshot(self, name):
        """截取屏幕并保存"""
        try:
            self.screenshot_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成文件名
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # 执行ADB截图命令
            cmd = f'adb shell screencap -p /sdcard/screenshot_temp.png'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            # 将截图从设备拉取到本地
            pull_cmd = f'adb pull /sdcard/screenshot_temp.png "{filepath}"'
            subprocess.run(pull_cmd, shell=True, check=True, capture_output=True)
            
            # 清理设备上的临时文件
            cleanup_cmd = 'adb shell rm /sdcard/screenshot_temp.png'
            subprocess.run(cleanup_cmd, shell=True, capture_output=True)
            
            print(f"    截图已保存: {filename}")
            return str(filepath)
            
        except subprocess.CalledProcessError as e:
            print(f"    截图失败: {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"    截图异常: {str(e)}")
            return None
    
    def take_error_screenshot(self, test_case_id, error_message):
        """在错误发生时截图"""
        filename = f"ERROR_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        return self.take_screenshot(filename)
    
    def get_screenshot_path(self, filename):
        """获取截图的完整路径"""
        return str(self.screenshot_dir / filename)
    
    def get_all_screenshots(self):
        """获取所有截图文件"""
        return list(self.screenshot_dir.glob("*.png"))
    
    def cleanup_old_screenshots(self, keep_days=7):
        """清理旧的截图文件"""
        try:
            import time
            current_time = time.time()
            
            for screenshot_file in self.get_all_screenshots():
                file_time = screenshot_file.stat().st_mtime
                if (current_time - file_time) > (keep_days * 86400):  # 86400秒 = 1天
                    screenshot_file.unlink()
                    print(f"清理旧截图: {screenshot_file.name}")
                    
        except Exception as e:
            print(f"清理截图失败: {str(e)}")
    
    def get_screenshot_count(self):
        """获取截图数量"""
        return len(self.get_all_screenshots())