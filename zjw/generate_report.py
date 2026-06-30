"""
测试报告生成器
生成包含全局统计、用例明细、失败截图、分类筛选的自定义 HTML 报告
"""
import os
import json
import base64
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, reports_dir: str = None):
        self.reports_dir = reports_dir or os.path.join(os.path.dirname(__file__), "reports")
        self.screenshots_dir = os.path.join(self.reports_dir, "screenshots")
        self.allure_results_dir = os.path.join(self.reports_dir, "allure-results")
        self.html_output_dir = os.path.join(self.reports_dir, "html")
        
        # 确保输出目录存在
        os.makedirs(self.html_output_dir, exist_ok=True)
        
        # 测试结果数据
        self.test_results: List[Dict[str, Any]] = []
        self.summary: Dict[str, Any] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
            "duration": 0.0,
            "pass_rate": 0.0
        }
        
        # 测试环境信息
        self.environment: Dict[str, str] = {}
        
    def parse_allure_results(self) -> None:
        """解析 Allure 结果文件"""
        if not os.path.exists(self.allure_results_dir):
            print(f"Allure 结果目录不存在: {self.allure_results_dir}")
            return
            
        # 解析环境信息
        env_file = os.path.join(self.allure_results_dir, "environment.properties")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        self.environment[key] = value
        
        # 解析测试结果 JSON 文件
        for filename in os.listdir(self.allure_results_dir):
            if filename.endswith("-result.json"):
                filepath = os.path.join(self.allure_results_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        result = json.load(f)
                        self._process_test_result(result)
                except Exception as e:
                    print(f"解析文件失败 {filename}: {e}")
    
    def _process_test_result(self, result: Dict[str, Any]) -> None:
        """处理单个测试结果"""
        test_info = {
            "uuid": result.get("uuid", ""),
            "name": result.get("name", "未知测试"),
            "status": result.get("status", "unknown"),
            "stage": result.get("stage", ""),
            "start": result.get("start", 0),
            "stop": result.get("stop", 0),
            "duration": 0.0,
            "feature": "",
            "description": "",
            "error_message": "",
            "error_trace": "",
            "screenshot": "",
            "screenshot_base64": ""
        }
        
        # 计算执行时长
        if test_info["start"] and test_info["stop"]:
            test_info["duration"] = (test_info["stop"] - test_info["start"]) / 1000.0
        
        # 获取功能模块
        labels = result.get("labels", [])
        for label in labels:
            if label.get("name") == "feature":
                test_info["feature"] = label.get("value", "")
        
        # 获取描述
        test_info["description"] = result.get("description", "")
        
        # 获取错误信息
        status_details = result.get("statusDetails", {})
        if status_details:
            test_info["error_message"] = status_details.get("message", "")
            test_info["error_trace"] = status_details.get("trace", "")
        
        # 查找截图
        attachments = result.get("attachments", [])
        for attachment in attachments:
            attachment_name = attachment.get("name", "")
            # 支持失败截图和通过截图
            if "截图" in attachment_name or "screenshot" in attachment_name.lower():
                screenshot_name = attachment.get("source", "")
                if screenshot_name:
                    screenshot_path = os.path.join(self.allure_results_dir, screenshot_name)
                    if os.path.exists(screenshot_path):
                        test_info["screenshot"] = screenshot_path
                        test_info["screenshot_name"] = attachment_name
                        # 读取并转换为 base64
                        with open(screenshot_path, "rb") as f:
                            test_info["screenshot_base64"] = base64.b64encode(f.read()).decode("utf-8")
                        break  # 只取第一个截图
        
        # 如果 Allure 附件中没有截图，尝试从截图目录查找
        if not test_info["screenshot_base64"]:
            screenshot_base64 = self.find_screenshot_for_test(test_info["name"])
            if screenshot_base64:
                test_info["screenshot_base64"] = screenshot_base64
                test_info["screenshot_name"] = "测试截图"
        
        self.test_results.append(test_info)
        
        # 更新统计
        self.summary["total"] += 1
        self.summary["duration"] += test_info["duration"]
        
        status = test_info["status"]
        if status == "passed":
            self.summary["passed"] += 1
        elif status == "failed":
            self.summary["failed"] += 1
        elif status == "skipped":
            self.summary["skipped"] += 1
        elif status == "broken":
            self.summary["error"] += 1
        
        # 计算通过率
        if self.summary["total"] > 0:
            self.summary["pass_rate"] = (self.summary["passed"] / self.summary["total"]) * 100
    
    def find_screenshot_for_test(self, test_name: str) -> Optional[str]:
        """为测试查找截图文件（支持在子文件夹中查找）"""
        if not os.path.exists(self.screenshots_dir):
            return None
            
        # 首先尝试在子文件夹中查找（以报告名称命名的文件夹）
        for folder_name in os.listdir(self.screenshots_dir):
            folder_path = os.path.join(self.screenshots_dir, folder_name)
            if os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    if test_name.replace("::", "_").replace(".", "_") in filename:
                        filepath = os.path.join(folder_path, filename)
                        with open(filepath, "rb") as f:
                            return base64.b64encode(f.read()).decode("utf-8")
        
        # 如果子文件夹中没有找到，尝试在根目录查找
        for filename in os.listdir(self.screenshots_dir):
            filepath = os.path.join(self.screenshots_dir, filename)
            if os.path.isfile(filepath) and test_name.replace("::", "_").replace(".", "_") in filename:
                with open(filepath, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        
        return None
    
    def generate_html_report(self, output_file: str = None, 
                            tester: str = "", remark: str = "") -> str:
        """生成 HTML 报告"""
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.html_output_dir, f"test_report_{timestamp}.html")
        
        # 更新环境信息
        if tester:
            self.environment["测试人员"] = tester
        if remark:
            self.environment["备注"] = remark
        
        html_content = self._generate_html_content()
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"HTML 报告已生成: {output_file}")
        return output_file
    
    def _generate_html_content(self) -> str:
        """生成 HTML 内容"""
        # 生成测试结果表格行
        test_rows = self._generate_test_rows()
        
        # 生成模块筛选选项
        module_options = self._generate_module_options()
        
        # 生成环境信息
        env_info = self._generate_env_info()
        
        # 生成统计卡片
        stats_cards = self._generate_stats_cards()
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - 天津市建筑产业互联网平台</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #1a1a2e;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}
        .stat-card.total .number {{ color: #3b82f6; }}
        .stat-card.passed .number {{ color: #10b981; }}
        .stat-card.failed .number {{ color: #ef4444; }}
        .stat-card.skipped .number {{ color: #f59e0b; }}
        .stat-card.error .number {{ color: #8b5cf6; }}
        .stat-card.rate .number {{ color: #06b6d4; }}
        .stat-card.duration .number {{ color: #ec4899; }}
        
        .env-section {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .env-section h2 {{
            color: #1a1a2e;
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        .env-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .env-item {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background: #f8fafc;
            border-radius: 8px;
        }}
        .env-item .key {{
            color: #64748b;
            min-width: 80px;
            font-size: 14px;
        }}
        .env-item .value {{
            color: #1e293b;
            font-weight: 500;
        }}
        
        .filter-section {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-section label {{
            color: #374151;
            font-weight: 500;
        }}
        .filter-section select, .filter-section input {{
            padding: 10px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }}
        .filter-section select:focus, .filter-section input:focus {{
            border-color: #3b82f6;
        }}
        .filter-btn {{
            padding: 10px 20px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.3s;
        }}
        .filter-btn:hover {{
            background: #2563eb;
        }}
        .reset-btn {{
            padding: 10px 20px;
            background: #6b7280;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.3s;
        }}
        .reset-btn:hover {{
            background: #4b5563;
        }}
        
        .results-section {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .results-section h2 {{
            color: #1a1a2e;
            font-size: 18px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        .results-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .results-table th {{
            background: #f8fafc;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
        }}
        .results-table td {{
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}
        .results-table tr:hover {{
            background: #f8fafc;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-passed {{ background: #d1fae5; color: #065f46; }}
        .status-failed {{ background: #fee2e2; color: #991b1b; }}
        .status-skipped {{ background: #fef3c7; color: #92400e; }}
        .status-broken {{ background: #ede9fe; color: #5b21b6; }}
        .status-unknown {{ background: #e5e7eb; color: #374151; }}
        
        .error-details {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            color: #991b1b;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
        }}
        .screenshot-container {{
            margin-top: 10px;
        }}
        .screenshot-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s;
        }}
        .screenshot-container img:hover {{
            transform: scale(1.02);
        }}
        .screenshot-toggle {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            margin-bottom: 10px;
        }}
        .screenshot-toggle:hover {{
            background: #2563eb;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        .modal.active {{
            display: flex;
        }}
        .modal img {{
            max-width: 95%;
            max-height: 95%;
            border-radius: 8px;
        }}
        .modal-close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            cursor: pointer;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: rgba(255,255,255,0.8);
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .results-table {{
                font-size: 12px;
            }}
            .results-table th, .results-table td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>测试报告</h1>
            <div class="subtitle">天津市建筑产业互联网平台 - 自动化测试报告</div>
            <div class="subtitle" style="margin-top: 10px;">生成时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="stats-grid">
            {stats_cards}
        </div>
        
        <div class="env-section">
            <h2>测试环境</h2>
            <div class="env-grid">
                {env_info}
            </div>
        </div>
        
        <div class="filter-section">
            <label>模块筛选:</label>
            <select id="moduleFilter">
                <option value="">全部模块</option>
                {module_options}
            </select>
            
            <label>状态筛选:</label>
            <select id="statusFilter">
                <option value="">全部状态</option>
                <option value="passed">通过</option>
                <option value="failed">失败</option>
                <option value="skipped">跳过</option>
                <option value="broken">错误</option>
            </select>
            
            <label>搜索:</label>
            <input type="text" id="searchInput" placeholder="输入用例名称搜索...">
            
            <button class="filter-btn" onclick="applyFilter()">筛选</button>
            <button class="reset-btn" onclick="resetFilter()">重置</button>
        </div>
        
        <div class="results-section">
            <h2>用例明细</h2>
            <table class="results-table" id="resultsTable">
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 15%">模块</th>
                        <th style="width: 30%">用例名称</th>
                        <th style="width: 10%">状态</th>
                        <th style="width: 10%">执行时长</th>
                        <th style="width: 30%">详情</th>
                    </tr>
                </thead>
                <tbody>
                    {test_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>测试报告由 Playwright + Pytest 自动生成</p>
        </div>
    </div>
    
    <div class="modal" id="imageModal" onclick="closeModal()">
        <span class="modal-close">&times;</span>
        <img id="modalImage" src="" alt="截图预览">
    </div>
    
    <script>
        function applyFilter() {{
            const moduleFilter = document.getElementById('moduleFilter').value;
            const statusFilter = document.getElementById('statusFilter').value;
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            
            const rows = document.querySelectorAll('#resultsTable tbody tr');
            
            rows.forEach(row => {{
                const module = row.getAttribute('data-module') || '';
                const status = row.getAttribute('data-status') || '';
                const name = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
                
                let show = true;
                
                if (moduleFilter && module !== moduleFilter) show = false;
                if (statusFilter && status !== statusFilter) show = false;
                if (searchText && !name.includes(searchText)) show = false;
                
                row.style.display = show ? '' : 'none';
            }});
        }}
        
        function resetFilter() {{
            document.getElementById('moduleFilter').value = '';
            document.getElementById('statusFilter').value = '';
            document.getElementById('searchInput').value = '';
            
            const rows = document.querySelectorAll('#resultsTable tbody tr');
            rows.forEach(row => row.style.display = '');
        }}
        
        function toggleScreenshot(btn) {{
            const container = btn.nextElementSibling;
            if (container.style.display === 'none') {{
                container.style.display = 'block';
                btn.textContent = '隐藏截图';
            }} else {{
                container.style.display = 'none';
                btn.textContent = '查看截图';
            }}
        }}
        
        function openModal(imgSrc) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modalImg.src = imgSrc;
            modal.classList.add('active');
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').classList.remove('active');
        }}
    </script>
</body>
</html>'''
    
    def _generate_stats_cards(self) -> str:
        """生成统计卡片"""
        return f'''
        <div class="stat-card total">
            <div class="number">{self.summary["total"]}</div>
            <div class="label">用例总数</div>
        </div>
        <div class="stat-card passed">
            <div class="number">{self.summary["passed"]}</div>
            <div class="label">通过</div>
        </div>
        <div class="stat-card failed">
            <div class="number">{self.summary["failed"]}</div>
            <div class="label">失败</div>
        </div>
        <div class="stat-card skipped">
            <div class="number">{self.summary["skipped"]}</div>
            <div class="label">跳过</div>
        </div>
        <div class="stat-card error">
            <div class="number">{self.summary["error"]}</div>
            <div class="label">错误</div>
        </div>
        <div class="stat-card rate">
            <div class="number">{self.summary["pass_rate"]:.1f}%</div>
            <div class="label">通过率</div>
        </div>
        <div class="stat-card duration">
            <div class="number">{self.summary["duration"]:.2f}s</div>
            <div class="label">总耗时</div>
        </div>'''
    
    def _generate_env_info(self) -> str:
        """生成环境信息"""
        default_env = {
            "测试环境": "生产环境",
            "测试地址": "https://www.tjjzcy.com/",
            "浏览器": "Chromium",
            "测试人员": "未指定",
            "备注": "无"
        }
        
        # 合并默认值和实际值
        env = {**default_env, **self.environment}
        
        items = []
        for key, value in env.items():
            items.append(f'''
            <div class="env-item">
                <span class="key">{key}:</span>
                <span class="value">{value}</span>
            </div>''')
        
        return "\n".join(items)
    
    def _generate_module_options(self) -> str:
        """生成模块筛选选项"""
        modules = set()
        for result in self.test_results:
            if result["feature"]:
                modules.add(result["feature"])
        
        options = []
        for module in sorted(modules):
            options.append(f'<option value="{module}">{module}</option>')
        
        return "\n".join(options)
    
    def _generate_test_rows(self) -> str:
        """生成测试结果表格行"""
        rows = []
        for i, result in enumerate(self.test_results, 1):
            status_class = f"status-{result['status']}"
            status_text = {
                "passed": "通过",
                "failed": "失败",
                "skipped": "跳过",
                "broken": "错误",
                "unknown": "未知"
            }.get(result["status"], result["status"])
            
            # 生成详情内容
            details = ""
            
            # 添加错误信息
            if result["error_message"]:
                details += f'''
                <div class="error-details">
                    <strong>错误信息:</strong>
                    {result["error_message"]}
                    
                    <strong style="margin-top: 10px; display: block;">堆栈跟踪:</strong>
                    {result["error_trace"]}
                </div>'''
            
            # 添加截图
            if result["screenshot_base64"]:
                details += f'''
                <div class="screenshot-container">
                    <button class="screenshot-toggle" onclick="toggleScreenshot(this)">查看截图</button>
                    <div style="display: none;">
                        <img src="data:image/png;base64,{result["screenshot_base64"]}" 
                             alt="失败截图" 
                             onclick="openModal(this.src)">
                    </div>
                </div>'''
            
            row = f'''
            <tr data-module="{result["feature"]}" data-status="{result["status"]}">
                <td>{i}</td>
                <td>{result["feature"]}</td>
                <td>{result["name"]}</td>
                <td><span class="status-badge {status_class}">{status_text}</span></td>
                <td>{result["duration"]:.2f}s</td>
                <td>{details}</td>
            </tr>'''
            
            rows.append(row)
        
        return "\n".join(rows)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成测试报告")
    parser.add_argument("--tester", default="", help="测试人员姓名")
    parser.add_argument("--remark", default="", help="测试备注")
    parser.add_argument("--reports-dir", default=None, help="报告目录")
    
    args = parser.parse_args()
    
    generator = TestReportGenerator(args.reports_dir)
    generator.parse_allure_results()
    
    output_file = generator.generate_html_report(
        tester=args.tester,
        remark=args.remark
    )
    
    print(f"\n报告生成完成!")
    print(f"文件路径: {output_file}")


if __name__ == "__main__":
    main()
