#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试报告生成器
生成HTML格式的测试报告
"""

from pathlib import Path
from datetime import datetime


class TestReportGenerator:
    def __init__(self, report_file, timestamp):
        self.report_file = Path(report_file)
        self.timestamp = timestamp
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self, test_results, is_intermediate=False):
        """生成测试报告"""
        try:
            # 统计数据
            total = len(test_results)
            passed = sum(1 for r in test_results if r['status'] == 'PASS')
            failed = sum(1 for r in test_results if r['status'] == 'FAIL')
            skipped = sum(1 for r in test_results if r['status'] == 'SKIP')
            
            # 按模块分组
            modules = {}
            for result in test_results:
                module = result.get('module', '未知模块')
                if module not in modules:
                    modules[module] = []
                modules[module].append(result)
            
            # 生成HTML报告
            html_content = self._generate_html_content(
                test_results, modules, total, passed, failed, skipped, is_intermediate
            )
            
            # 写入文件
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"测试报告已生成: {self.report_file}")
            
        except Exception as e:
            print(f"生成测试报告失败: {str(e)}")
            raise
    
    def _generate_html_content(self, test_results, modules, total, passed, failed, skipped, is_intermediate):
        """生成HTML内容"""
        report_type = "中间测试报告" if is_intermediate else "最终测试报告"
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>津筑网 App 自动化测试报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .summary {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .stat-card.pass {{
            border-left-color: #28a745;
        }}
        
        .stat-card.fail {{
            border-left-color: #dc3545;
        }}
        
        .stat-card.skip {{
            border-left-color: #ffc107;
        }}
        
        .stat-card .number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card.pass .number {{
            color: #28a745;
        }}
        
        .stat-card.fail .number {{
            color: #dc3545;
        }}
        
        .stat-card.skip .number {{
            color: #ffc107;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background-color: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 20px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        
        .module-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .module-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .test-case {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .test-case-header {{
            padding: 15px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .test-case-header:hover {{
            background: #e9ecef;
        }}
        
        .test-case.pass .test-case-header {{
            border-left: 4px solid #28a745;
        }}
        
        .test-case.fail .test-case-header {{
            border-left: 4px solid #dc3545;
        }}
        
        .test-case.skip .test-case-header {{
            border-left: 4px solid #ffc107;
        }}
        
        .test-case-info {{
            flex: 1;
        }}
        
        .test-case-id {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .test-case-name {{
            color: #333;
            font-size: 16px;
        }}
        
        .test-case-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        .test-case.pass .test-case-status {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .test-case.fail .test-case-status {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .test-case.skip .test-case-status {{
            background-color: #fff3cd;
            color: #856404;
        }}
        
        .test-case-details {{
            padding: 15px;
            display: none;
            border-top: 1px solid #e9ecef;
        }}
        
        .test-case.show-details .test-case-details {{
            display: block;
        }}
        
        .detail-row {{
            margin-bottom: 10px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            color: #333;
        }}
        
        .screenshot-container {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }}
        
        .screenshot {{
            max-width: 200px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        
        .screenshot:hover {{
            transform: scale(1.05);
            border-color: #667eea;
        }}
        
        .priority-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .priority-P0 {{
            background-color: #dc3545;
            color: white;
        }}
        
        .priority-P1 {{
            background-color: #ffc107;
            color: #333;
        }}
        
        .priority-P2 {{
            background-color: #17a2b8;
            color: white;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
        }}
        
        .error-message {{
            color: #dc3545;
            background: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        @media print {{
            .test-case-details {{
                display: block !important;
            }}
            .screenshot {{
                max-width: 150px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>津筑网 App 自动化测试报告</h1>
            <div class="meta">
                <p>报告类型: {report_type}</p>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>时间戳: {self.timestamp}</p>
            </div>
        </div>
        
        <div class="summary">
            <h2>测试概览</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{total}</div>
                    <div class="label">总用例数</div>
                </div>
                <div class="stat-card pass">
                    <div class="number">{passed}</div>
                    <div class="label">通过</div>
                </div>
                <div class="stat-card fail">
                    <div class="number">{failed}</div>
                    <div class="label">失败</div>
                </div>
                <div class="stat-card skip">
                    <div class="number">{skipped}</div>
                    <div class="label">跳过</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {passed/total*100 if total > 0 else 0:.1f}%">
                    {passed/total*100 if total > 0 else 0:.1f}%
                </div>
            </div>
        </div>
"""
        
        # 添加各模块的测试结果
        for module_name, module_results in modules.items():
            html += f"""
        <div class="module-section">
            <h3>{module_name}</h3>
"""
            
            for result in module_results:
                html += self._generate_test_case_html(result)
            
            html += """
        </div>
"""
        
        # 添加页脚
        html += f"""
        <div class="footer">
            <p>津筑网 App 自动化测试系统 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
"""
        
        # 添加JavaScript代码（单独处理以避免f-string解析问题）
        js_code = """
    <script>
        // 点击测试用例头部显示/隐藏详情
        document.querySelectorAll('.test-case-header').forEach(header => {
            header.addEventListener('click', function() {
                this.parentElement.classList.toggle('show-details');
            });
        });
        
        // 点击截图放大显示
        document.querySelectorAll('.screenshot').forEach(img => {
            img.addEventListener('click', function() {
                window.open(this.src, '_blank');
            });
        });
    </script>
</body>
</html>
"""
        html += js_code
        
        return html
    
    def _generate_test_case_html(self, result):
        """生成单个测试用例的HTML"""
        status_class = result['status'].lower()
        
        screenshot_html = ""
        if result.get('before_screenshot'):
            screenshot_html += f'<img src="{result["before_screenshot"]}" class="screenshot" alt="执行前截图" title="执行前">'
        if result.get('after_screenshot'):
            screenshot_html += f'<img src="{result["after_screenshot"]}" class="screenshot" alt="执行后截图" title="执行后">'
        
        error_html = ""
        if result['status'] == 'FAIL' and result.get('message'):
            error_html = f'<div class="error-message">错误信息: {result["message"]}</div>'
        
        html = f"""
            <div class="test-case {status_class}">
                <div class="test-case-header">
                    <div class="test-case-info">
                        <div class="test-case-id">
                            {result['id']} 
                            <span class="priority-badge priority-{result['priority']}">{result['priority']}</span>
                        </div>
                        <div class="test-case-name">{result['name']}</div>
                    </div>
                    <div class="test-case-status">{result['status']}</div>
                </div>
                <div class="test-case-details">
                    <div class="detail-row">
                        <div class="detail-label">优先级</div>
                        <div class="detail-value">{result['priority']}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">开始时间</div>
                        <div class="detail-value">{result['start_time']}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">结束时间</div>
                        <div class="detail-value">{result['end_time']}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">执行耗时</div>
                        <div class="detail-value">{result['duration']:.2f} 秒</div>
                    </div>
                    {error_html}
                    <div class="detail-row">
                        <div class="detail-label">测试截图</div>
                        <div class="screenshot-container">
                            {screenshot_html}
                        </div>
                    </div>
                </div>
            </div>
"""
        
        return html