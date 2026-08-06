"""
超级个体后台管理系统 - 实际数据提交验证测试 V2
使用JavaScript直接操作DOM，避免Playwright选择器歧义
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TEST_PREFIX = "AUTO_TEST"


def gen_test_data():
    ts = datetime.now().strftime("%m%d%H%M%S")
    return {
        "project_name": f"{TEST_PREFIX}_项目_{ts}",
        "project_subtitle": f"测试副标题_{ts}",
        "project_desc": f"自动化测试创建的服务项目，时间：{ts}",
        "contract_title": f"{TEST_PREFIX}_合同_{ts}",
        "contract_content": f"测试合同内容_{ts}",
        "contract_fee": f"测试费用_{ts}",
        "scope_name": f"{TEST_PREFIX}_经营范围_{ts}",
        "scope_remark": f"测试备注_{ts}",
        "knowledge_title": f"{TEST_PREFIX}_知识库_{ts}",
        "knowledge_content": f"自动化测试创建的知识库内容，时间：{ts}。用于验证新增功能。",
    }


class RealDataTestV2:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results = []
        self.data = gen_test_data()
        self.created = {}

    async def setup(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def teardown(self):
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

    def log(self, module, test_name, status, detail="", screenshot_path=""):
        self.results.append({
            "module": module, "test_name": test_name,
            "status": status, "detail": detail,
            "screenshot": screenshot_path,
        })
        icon = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "⏭️")
        print(f"  {icon} [{status}] {test_name}: {detail}")

    async def screenshot(self, name):
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{TIMESTAMP}.png")
        await self.page.screenshot(path=path)
        return path

    async def login(self):
        await self.page.goto(LOGIN_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(1500)
        await self.page.fill('input[placeholder="账号"]', USERNAME)
        await self.page.fill('input[type="password"]', PASSWORD)
        await self.page.click('button:has-text("登 录")')
        await self.page.wait_for_timeout(2500)
        return "/dashboard" in self.page.url

    async def nav(self, path):
        await self.page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await self.page.wait_for_timeout(1500)

    # ========== JavaScript 辅助方法 ==========

    async def js_fill_input_by_label(self, label_text, value):
        """根据标签文本填写input"""
        return await self.page.evaluate("""
            ([labelText, value]) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item, .ant-drawer .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    if (!label.textContent.includes(labelText)) continue;
                    if (item.style.display === 'none') continue;
                    
                    const input = item.querySelector('input[type="text"]:not(.ant-select-selection-search-input), input:not([type]):not(.ant-select-selection-search-input)');
                    if (input) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(input, value);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return 'filled';
                    }
                    return 'input_not_found';
                }
                return 'label_not_found';
            }
        """, [label_text, value])

    async def js_click_radio_by_label(self, label_text, index=0):
        """根据标签文本点击单选按钮"""
        return await self.page.evaluate("""
            ([labelText, index]) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item, .ant-drawer .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    if (!label.textContent.includes(labelText)) continue;
                    if (item.style.display === 'none') continue;
                    
                    const radios = item.querySelectorAll('.ant-radio');
                    if (radios[index]) {
                        radios[index].click();
                        return 'clicked';
                    }
                    return 'radio_not_found';
                }
                return 'label_not_found';
            }
        """, [label_text, index])

    async def js_set_editor_content(self, content):
        """设置富文本编辑器内容"""
        return await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ql-editor, .w-e-text, [contenteditable="true"]');
                for (const editor of editors) {
                    if (editor.closest('.ant-modal, .ant-drawer')) {
                        editor.innerHTML = content;
                        editor.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'set';
                    }
                }
                return 'not_found';
            }
        """, content)

    async def js_select_dropdown_option(self, label_text, option_index=0):
        """根据标签文本选择下拉框选项"""
        # 先点击下拉框
        await self.page.evaluate("""
            ([labelText]) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item, .ant-drawer .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    if (!label.textContent.includes(labelText)) continue;
                    if (item.style.display === 'none') continue;
                    
                    const select = item.querySelector('.ant-select-selector');
                    if (select) {
                        select.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """, [label_text])
        await self.page.wait_for_timeout(500)
        
        # 选择第一个选项
        return await self.page.evaluate("""
            ([index]) => {
                const options = document.querySelectorAll('.ant-select-item-option');
                if (options[index]) {
                    options[index].click();
                    return 'selected';
                }
                return 'option_not_found';
            }
        """, [option_index])

    async def js_fill_textarea_by_label(self, label_text, value):
        """根据标签文本填写textarea"""
        return await self.page.evaluate("""
            ([labelText, value]) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item, .ant-drawer .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    if (!label.textContent.includes(labelText)) continue;
                    if (item.style.display === 'none') continue;
                    
                    const textarea = item.querySelector('textarea');
                    if (textarea) {
                        textarea.value = value;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                        return 'filled';
                    }
                }
                return 'label_not_found';
            }
        """, [label_text, value])

    async def js_click_submit(self):
        """点击提交/确认按钮"""
        return await self.page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('.ant-modal button, .ant-drawer button');
                const texts = ['确 认', '确认', '确 定', '确定', '保存', '提交'];
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    if (texts.includes(text) && !btn.disabled) {
                        btn.click();
                        return text;
                    }
                }
                return null;
            }
        """)

    async def js_get_toast_messages(self):
        """获取Toast消息"""
        await self.page.wait_for_timeout(2)
        return await self.page.evaluate("""
            () => {
                const selectors = ['.ant-message-notice-content', '.ant-message'];
                const messages = [];
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        if (text && text.length < 100) messages.push(text);
                    }
                }
                return [...new Set(messages)];
            }
        """)

    async def js_has_modal(self):
        """检查弹窗是否存在"""
        return await self.page.evaluate("""
            () => {
                const modal = document.querySelector('.ant-modal, .ant-drawer');
                return modal && getComputedStyle(modal).display !== 'none';
            }
        """)

    async def js_close_modal(self):
        """关闭弹窗"""
        return await self.page.evaluate("""
            () => {
                const closeBtn = document.querySelector('.ant-modal-close, .ant-drawer-close');
                if (closeBtn) { closeBtn.click(); return 'closed'; }
                return 'not_found';
            }
        """)

    async def js_find_in_table(self, keyword):
        """在表格中查找关键词"""
        return await self.page.evaluate("""
            (keyword) => {
                const rows = document.querySelectorAll('.ant-table-tbody tr');
                const found = [];
                for (const row of rows) {
                    if (row.textContent.includes(keyword)) {
                        found.push(row.textContent.trim());
                    }
                }
                return found;
            }
        """, keyword)

    # ========== 测试方法 ==========

    async def test_project_config_add(self):
        module = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n测试: {module} - 新增服务项目\n{'='*60}")

        await self.nav("/smart-service/project-config")
        
        # 点击新增
        await self.page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.includes('新增服务项目')) {
                        btn.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(1500)
        await self.screenshot("project_add_01_opened")

        if not await self.js_has_modal():
            self.log(module, "新增服务项目", "FAIL", "弹窗未打开")
            return

        # 填写表单
        await self.js_fill_input_by_label("服务项目名称", self.data["project_name"])
        await self.js_fill_input_by_label("副标题", self.data["project_subtitle"])
        await self.js_click_radio_by_label("计费方式", 0)
        await self.js_click_radio_by_label("是否展示", 0)
        await self.js_set_editor_content(self.data["project_desc"])
        print(f"  表单填写完成")

        await self.screenshot("project_add_02_filled")

        # 提交
        btn_text = await self.js_click_submit()
        print(f"  点击提交按钮: {btn_text}")
        await self.page.wait_for_timeout(3)
        await self.screenshot("project_add_03_after_submit")

        # 检查结果
        toast_msgs = await self.js_get_toast_messages()
        print(f"  Toast提示: {toast_msgs}")

        if any('成功' in m for m in toast_msgs):
            self.log(module, "新增服务项目-提交", "PASS", f"Toast: {toast_msgs}",
                    await self.screenshot("project_add_04_success"))
            self.created["project"] = self.data["project_name"]
        elif await self.js_has_modal():
            self.log(module, "新增服务项目-提交", "FAIL", f"表单仍显示，可能有验证错误。Toast: {toast_msgs}",
                    await self.screenshot("project_add_05_validation_error"))
            await self.js_close_modal()
        else:
            # 验证数据
            found = await self.js_find_in_table(self.data["project_name"])
            if found:
                self.log(module, "新增服务项目-提交", "PASS", f"数据已在列表中",
                        await self.screenshot("project_add_04_verified"))
                self.created["project"] = self.data["project_name"]
            else:
                self.log(module, "新增服务项目-提交", "FAIL", f"Toast: {toast_msgs}, 数据未找到",
                        await self.screenshot("project_add_05_failed"))

    async def test_project_config_edit(self):
        module = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n测试: {module} - 编辑服务项目\n{'='*60}")

        await self.nav("/smart-service/project-config")

        # 点击第一个编辑按钮
        clicked = await self.page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                for (const link of links) {
                    if (link.textContent.trim() === '编辑') {
                        link.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        print(f"  点击编辑: {clicked}")
        await self.page.wait_for_timeout(1500)
        await self.screenshot("project_edit_01_opened")

        if not await self.js_has_modal():
            self.log(module, "编辑服务项目", "FAIL", "编辑弹窗未打开")
            return

        # 修改副标题
        new_subtitle = f"{self.data['project_subtitle']}_编辑"
        await self.js_fill_input_by_label("副标题", new_subtitle)
        print(f"  修改副标题为: {new_subtitle}")

        await self.screenshot("project_edit_02_filled")

        # 提交
        btn_text = await self.js_click_submit()
        print(f"  点击提交: {btn_text}")
        await self.page.wait_for_timeout(3)

        toast_msgs = await self.js_get_toast_messages()
        print(f"  Toast提示: {toast_msgs}")

        if any('成功' in m for m in toast_msgs):
            self.log(module, "编辑服务项目-提交", "PASS", f"Toast: {toast_msgs}",
                    await self.screenshot("project_edit_04_success"))
        elif await self.js_has_modal():
            self.log(module, "编辑服务项目-提交", "FAIL", f"表单仍显示。Toast: {toast_msgs}",
                    await self.screenshot("project_edit_05_error"))
            await self.js_close_modal()
        else:
            self.log(module, "编辑服务项目-提交", "PASS/FAIL", f"Toast: {toast_msgs}, 需人工确认",
                    await self.screenshot("project_edit_06_unknown"))

    async def test_contract_service_add(self):
        module = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}\n测试: {module} - 新增合同服务\n{'='*60}")

        await self.nav("/smart-service/contract-service")

        # 点击新增
        await self.page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.includes('新增合同服务')) {
                        btn.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(1500)
        await self.screenshot("contract_add_01_opened")

        if not await self.js_has_modal():
            self.log(module, "新增合同服务", "FAIL", "弹窗未打开")
            return

        # 填写表单
        await self.js_fill_input_by_label("合同服务标题", self.data["contract_title"])
        await self.js_set_editor_content(self.data["contract_content"])
        await self.js_fill_input_by_label("费用内容", self.data["contract_fee"])
        # 选择所属服务项目
        await self.js_select_dropdown_option("所属服务项目", 0)
        print(f"  表单填写完成")

        await self.screenshot("contract_add_02_filled")

        # 提交
        btn_text = await self.js_click_submit()
        await self.page.wait_for_timeout(3)
        await self.screenshot("contract_add_03_after_submit")

        toast_msgs = await self.js_get_toast_messages()
        print(f"  Toast提示: {toast_msgs}")

        if any('成功' in m for m in toast_msgs):
            self.log(module, "新增合同服务-提交", "PASS", f"Toast: {toast_msgs}",
                    await self.screenshot("contract_add_04_success"))
            self.created["contract"] = self.data["contract_title"]
        elif await self.js_has_modal():
            self.log(module, "新增合同服务-提交", "FAIL", f"表单仍显示。Toast: {toast_msgs}",
                    await self.screenshot("contract_add_05_error"))
            await self.js_close_modal()
        else:
            found = await self.js_find_in_table(self.data["contract_title"])
            if found:
                self.log(module, "新增合同服务-提交", "PASS", "数据已在列表中",
                        await self.screenshot("contract_add_04_verified"))
            else:
                self.log(module, "新增合同服务-提交", "FAIL", f"Toast: {toast_msgs}",
                        await self.screenshot("contract_add_06_failed"))

    async def test_scope_config_add(self):
        module = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}\n测试: {module} - 新增经营范围\n{'='*60}")

        await self.nav("/smart-service/scope-config")

        # 点击新增
        await self.page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.includes('新增经营范围')) {
                        btn.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(1500)
        await self.screenshot("scope_add_01_opened")

        if not await self.js_has_modal():
            self.log(module, "新增经营范围", "FAIL", "弹窗未打开")
            return

        # 填写表单
        await self.js_fill_input_by_label("经营范围名称", self.data["scope_name"])
        await self.js_fill_input_by_label("备注", self.data["scope_remark"])
        print(f"  表单填写完成")

        await self.screenshot("scope_add_02_filled")

        # 提交
        btn_text = await self.js_click_submit()
        await self.page.wait_for_timeout(3)
        await self.screenshot("scope_add_03_after_submit")

        toast_msgs = await self.js_get_toast_messages()
        print(f"  Toast提示: {toast_msgs}")

        if any('成功' in m for m in toast_msgs):
            self.log(module, "新增经营范围-提交", "PASS", f"Toast: {toast_msgs}",
                    await self.screenshot("scope_add_04_success"))
            self.created["scope"] = self.data["scope_name"]
        elif await self.js_has_modal():
            self.log(module, "新增经营范围-提交", "FAIL", f"表单仍显示。Toast: {toast_msgs}",
                    await self.screenshot("scope_add_05_error"))
            await self.js_close_modal()
        else:
            found = await self.js_find_in_table(self.data["scope_name"])
            if found:
                self.log(module, "新增经营范围-提交", "PASS", "数据已在列表中",
                        await self.screenshot("scope_add_04_verified"))
            else:
                self.log(module, "新增经营范围-提交", "FAIL", f"Toast: {toast_msgs}",
                        await self.screenshot("scope_add_06_failed"))

    async def test_knowledge_add(self):
        module = "内容管理-知识库"
        print(f"\n{'='*60}\n测试: {module} - 新增知识库\n{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 点击新增
        await self.page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.includes('新增知识库')) {
                        btn.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(1500)
        await self.screenshot("knowledge_add_01_opened")

        if not await self.js_has_modal():
            self.log(module, "新增知识库", "FAIL", "弹窗未打开")
            return

        # 填写表单
        await self.js_fill_input_by_label("标题", self.data["knowledge_title"])
        await self.js_set_editor_content(self.data["knowledge_content"])
        await self.js_select_dropdown_option("展示位置", 0)
        await self.js_select_dropdown_option("资讯类型", 0)
        print(f"  表单填写完成")

        await self.screenshot("knowledge_add_02_filled")

        # 提交
        btn_text = await self.js_click_submit()
        await self.page.wait_for_timeout(3)
        await self.screenshot("knowledge_add_03_after_submit")

        toast_msgs = await self.js_get_toast_messages()
        print(f"  Toast提示: {toast_msgs}")

        if any('成功' in m for m in toast_msgs):
            self.log(module, "新增知识库-提交", "PASS", f"Toast: {toast_msgs}",
                    await self.screenshot("knowledge_add_04_success"))
            self.created["knowledge"] = self.data["knowledge_title"]
        elif await self.js_has_modal():
            self.log(module, "新增知识库-提交", "FAIL", f"表单仍显示。Toast: {toast_msgs}",
                    await self.screenshot("knowledge_add_05_error"))
            await self.js_close_modal()
        else:
            self.log(module, "新增知识库-提交", "FAIL", f"Toast: {toast_msgs}",
                    await self.screenshot("knowledge_add_06_failed"))

    async def test_knowledge_toggle_status(self):
        module = "内容管理-知识库"
        print(f"\n{'='*60}\n测试: {module} - 禁用/启用状态切换\n{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 查找并点击禁用/启用按钮
        result = await self.page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                for (const link of links) {
                    const text = link.textContent.trim();
                    if (text === '禁用' || text === '启用') {
                        link.click();
                        return { clicked: true, text };
                    }
                }
                return { clicked: false };
            }
        """)
        print(f"  点击: {result}")

        if result.get("clicked"):
            await self.page.wait_for_timeout(1000)
            await self.screenshot("knowledge_toggle_01_confirm")

            # 检查确认弹窗
            has_confirm = await self.page.evaluate("""
                () => {
                    return !!document.querySelector('.ant-popconfirm, .ant-popover');
                }
            """)
            print(f"  有确认弹窗: {has_confirm}")

            if has_confirm:
                # 点击确认
                await self.page.evaluate("""
                    () => {
                        const confirmBtns = document.querySelectorAll('.ant-popconfirm button.ant-btn-primary, .ant-popover button.ant-btn-primary');
                        for (const btn of confirmBtns) {
                            if (!btn.disabled) {
                                btn.click();
                                return 'confirmed';
                            }
                        }
                        return 'not_found';
                    }
                """)
                await self.page.wait_for_timeout(2)

                toast_msgs = await self.js_get_toast_messages()
                success = any('成功' in m for m in toast_msgs)
                self.log(module, f"知识库状态切换({result['text']})", "PASS" if success else "FAIL",
                        f"Toast: {toast_msgs}",
                        await self.screenshot("knowledge_toggle_02_result"))
            else:
                self.log(module, f"知识库状态切换", "FAIL", "无确认弹窗",
                        await self.screenshot("knowledge_toggle_no_confirm"))
        else:
            self.log(module, "知识库状态切换", "SKIP", "未找到禁用/启用按钮")

    async def test_knowledge_detail(self):
        module = "内容管理-知识库"
        print(f"\n{'='*60}\n测试: {module} - 查看详情\n{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 点击详情
        result = await self.page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                for (const link of links) {
                    if (link.textContent.trim() === '详情') {
                        link.click();
                        return 'clicked';
                    }
                }
                return 'not_found';
            }
        """)
        if result == 'clicked':
            await self.page.wait_for_timeout(1500)
            await self.screenshot("knowledge_detail_01_opened")

            if await self.js_has_modal():
                content = await self.page.evaluate("""
                    () => {
                        const body = document.querySelector('.ant-modal-body, .ant-drawer-body');
                        return body ? body.textContent.trim().substring(0, 200) : null;
                    }
                """)
                has_content = content and len(content) > 0
                self.log(module, "知识库-查看详情", "PASS" if has_content else "FAIL",
                        f"内容: {content[:100] if content else '无'}...",
                        await self.screenshot("knowledge_detail_02_content"))
                await self.js_close_modal()
            else:
                self.log(module, "知识库-查看详情", "FAIL", "详情弹窗未打开")
        else:
            self.log(module, "知识库-查看详情", "SKIP", "未找到详情按钮")

    def generate_report(self):
        report_path = os.path.join(REPORT_DIR, f"real_data_test_report_{TIMESTAMP}.md")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")

        lines = [
            f"# 超级个体后台管理系统 - 实际数据提交验证报告",
            f"",
            f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"**测试环境:** http://172.16.1.165:9100",
            f"",
            f"## 测试结果汇总",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 测试总数 | {total} |",
            f"| ✅ 通过 | {passed} |",
            f"| ❌ 失败 | {failed} |",
            f"| ⏭️ 跳过 | {skipped} |",
            f"| 通过率 | {passed/total*100:.1f}% |" if total > 0 else "| 通过率 | 0% |",
            f"",
            f"## 详细测试结果",
            f"",
        ]

        current_module = ""
        for r in self.results:
            if r["module"] != current_module:
                current_module = r["module"]
                lines.append(f"### {current_module}")
                lines.append(f"")
            icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⏭️")
            lines.append(f"- {icon} **{r['test_name']}**: {r['detail']}")

        lines.extend([f"", f"## 问题汇总", f""])
        issues = [r for r in self.results if r["status"] == "FAIL"]
        if issues:
            for i, issue in enumerate(issues, 1):
                lines.append(f"{i}. **{issue['test_name']}** - {issue['detail']}")
        else:
            lines.append("无发现问题。")

        lines.extend([f"", f"## 测试数据（需手动清理）", f""])
        for key, value in self.created.items():
            lines.append(f"- {key}: `{value}`")

        report_content = "\n".join(lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n报告: {report_path}")
        return report_path

    async def run_all(self):
        await self.setup()
        try:
            print("登录系统...")
            await self.login()

            await self.test_project_config_add()
            await self.test_project_config_edit()
            await self.test_contract_service_add()
            await self.test_scope_config_add()
            await self.test_knowledge_add()
            await self.test_knowledge_toggle_status()
            await self.test_knowledge_detail()
        finally:
            await self.teardown()

        return self.generate_report()


async def main():
    tester = RealDataTestV2()
    report_path = await tester.run_all()
    
    total = len(tester.results)
    passed = sum(1 for r in tester.results if r["status"] == "PASS")
    failed = sum(1 for r in tester.results if r["status"] == "FAIL")
    print(f"\n总数: {total}, 通过: {passed}, 失败: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
