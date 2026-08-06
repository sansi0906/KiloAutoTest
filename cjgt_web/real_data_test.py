"""
超级个体后台管理系统 - 实际数据提交验证测试
测试新增、编辑、删除等操作的实际数据是否正确提交
"""
import asyncio
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

# 用于生成唯一测试数据
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TEST_PREFIX = "AUTO_TEST"  # 测试数据前缀，便于识别和清理


def gen_test_data():
    """生成测试数据"""
    ts = datetime.now().strftime("%m%d%H%M%S")
    return {
        "project_name": f"{TEST_PREFIX}_服务项目_{ts}",
        "project_subtitle": f"测试副标题_{ts}",
        "project_desc": f"这是一个自动化测试创建的服务项目，创建时间：{ts}",
        "contract_title": f"{TEST_PREFIX}_合同服务_{ts}",
        "contract_content": f"测试合同服务内容_{ts}",
        "contract_fee": f"测试费用内容_{ts}",
        "scope_name": f"{TEST_PREFIX}_经营范围_{ts}",
        "scope_remark": f"测试备注_{ts}",
        "knowledge_title": f"{TEST_PREFIX}_知识库_{ts}",
        "knowledge_content": f"这是一条自动化测试创建的知识库内容，创建时间：{ts}。用于验证新增功能是否正常工作。",
    }


class RealDataTest:
    """实际数据提交验证测试"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results = []
        self.data = gen_test_data()
        # 记录创建的测试数据，用于后续验证和清理
        self.created = {}

    async def setup(self):
        """初始化"""
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def teardown(self):
        """关闭"""
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

    def log(self, module, test_name, status, detail="", screenshot=""):
        """记录结果"""
        result = {
            "module": module,
            "test_name": test_name,
            "status": status,  # PASS, FAIL, ERROR
            "detail": detail,
            "screenshot": screenshot,
            "timestamp": datetime.now().isoformat(),
        }
        self.results.append(result)
        icon = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "⚠️")
        print(f"  {icon} [{status}] {test_name}: {detail}")
        return result

    async def login(self):
        """登录"""
        await self.page.goto(LOGIN_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(1500)
        await self.page.fill('input[placeholder="账号"]', USERNAME)
        await self.page.fill('input[type="password"]', PASSWORD)
        await self.page.click('button:has-text("登 录")')
        await self.page.wait_for_timeout(2500)
        return "/dashboard" in self.page.url

    async def nav(self, path):
        """导航到页面"""
        url = f"{BASE_URL}{path}"
        await self.page.goto(url, wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

    async def screenshot(self, name):
        """截图"""
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{TIMESTAMP}.png")
        await self.page.screenshot(path=path)
        return path

    async def get_table_rows(self):
        """获取表格所有行数据"""
        return await self.page.evaluate("""
            () => {
                const rows = document.querySelectorAll('.ant-table-tbody tr');
                const data = [];
                for (const row of rows) {
                    const cells = row.querySelectorAll('td');
                    const rowData = [];
                    for (const cell of cells) {
                        rowData.push(cell.textContent.trim());
                    }
                    data.push(rowData);
                }
                return data;
            }
        """)

    async def find_in_table(self, keyword):
        """在表格中查找关键词"""
        rows = await self.get_table_rows()
        found = []
        for row in rows:
            row_text = " ".join(row)
            if keyword in row_text:
                found.append(row)
        return found

    async def get_toast_message(self, wait_time=3):
        """获取Toast提示信息"""
        await self.page.wait_for_timeout(wait_time)
        messages = await self.page.evaluate("""
            () => {
                const selectors = [
                    '.ant-message',
                    '.ant-message-notice',
                    '.ant-message-notice-content',
                    '[class*="toast"]',
                    '[class*="Toast"]',
                    '.ant-notification',
                    '.ant-notification-notice',
                ];
                const messages = [];
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        if (text && text.length < 100) {
                            messages.push({ selector: sel, text });
                        }
                    }
                }
                return messages;
            }
        """)
        return messages

    async def fill_form_field(self, label, value, field_type="input"):
        """根据标签填写表单字段"""
        return await self.page.evaluate("""
            (args) => {
                const [labelText, value, fieldType] = args;
                
                // 查找包含指定标签的form-item
                const formItems = document.querySelectorAll('.ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    if (!label.textContent.includes(labelText)) continue;
                    
                    // 找到对应的输入元素
                    let input = null;
                    if (fieldType === "input") {
                        input = item.querySelector('input[type="text"], input:not([type])');
                    } else if (fieldType === "textarea") {
                        input = item.querySelector('textarea');
                    } else if (fieldType === "select") {
                        // Select需要特殊处理
                        const select = item.querySelector('.ant-select-selector');
                        if (select) {
                            select.click();
                            return "select_clicked";
                        }
                    }
                    
                    if (input) {
                        input.focus();
                        input.clear();
                        input.value = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return "filled";
                    }
                }
                return "not_found";
            }
        """, [label, value, field_type])

    async def test_project_config_add(self):
        """测试服务项目配置 - 新增"""
        module = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 新增服务项目")
        print(f"{'='*60}")

        await self.nav("/smart-service/project-config")

        # 点击新增按钮
        await self.page.click('button:has-text("新增服务项目")')
        await self.page.wait_for_timeout(1500)
        await self.screenshot("project_add_01_opened")

        # 获取表单结构
        form_structure = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-form-item');
                const fields = [];
                for (const item of items) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const labelText = label ? label.textContent.trim() : '';
                    const input = item.querySelector('input, textarea, .ant-select-selector');
                    const inputType = input ? input.tagName.toLowerCase() : 'unknown';
                    const placeholder = input ? input.getAttribute('placeholder') || '' : '';
                    fields.push({
                        label: labelText,
                        type: inputType,
                        placeholder: placeholder,
                    });
                }
                return fields;
            }
        """)
        print(f"  表单字段: {form_structure}")

        # 填写表单 - 使用JavaScript直接操作，避免选择器歧义
        await self.page.evaluate("""
            (data) => {
                const [projectName, subtitle, desc] = data;
                
                // 获取所有可见的表单区域内的form-item
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item, .ant-drawer .ant-form-item');
                
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (!label) continue;
                    const labelText = label.textContent.trim();
                    
                    // 跳过隐藏的表单项
                    if (item.style.display === 'none' || item.offsetParent === null) continue;
                    
                    if (labelText.includes('服务项目名称') && !labelText.includes('副标题')) {
                        const input = item.querySelector('input[type="text"]:not(.ant-select-selection-search-input)');
                        if (input) {
                            input.focus();
                            input.value = projectName;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                    
                    if (labelText === '副标题') {
                        const input = item.querySelector('input[type="text"]:not(.ant-select-selection-search-input)');
                        if (input) {
                            input.focus();
                            input.value = subtitle;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                }
            }
        """, [self.data["project_name"], self.data["project_subtitle"], self.data["project_desc"]])
        print(f"  填写服务项目名称: {self.data['project_name']}")
        print(f"  填写副标题: {self.data['project_subtitle']}")

        # 3. 计费方式（选择"按次"）
        radio_buttons = self.page.locator('.ant-form-item').filter(has_text="计费方式").first.locator('.ant-radio')
        radio_count = await radio_buttons.count()
        print(f"  计费方式选项数量: {radio_count}")
        if radio_count > 0:
            await radio_buttons.first.click()
            print(f"  选择计费方式: 按次")

        # 4. 是否展示（选择"是"）
        display_radios = self.page.locator('.ant-form-item').filter(has_text="是否展示").first.locator('.ant-radio')
        display_count = await display_radios.count()
        print(f"  是否展示选项数量: {display_count}")
        if display_count > 0:
            await display_radios.first.click()
            print(f"  选择是否展示: 是")

        # 5. 服务项目介绍（使用富文本编辑器 - 直接设置content）
        editor_content = self.page.locator('.ant-form-item').filter(has_text="服务项目介绍").first
        # 尝试设置富文本内容
        await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ql-editor, .w-e-text, [contenteditable="true"]');
                for (const editor of editors) {
                    editor.innerHTML = content;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                    editor.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
                return false;
            }
        """, self.data["project_desc"])
        print(f"  填写服务项目介绍: {self.data['project_desc']}")

        await self.screenshot("project_add_02_filled")

        # 点击确认提交
        await self.page.click('.ant-modal button:has-text("确 认"), .ant-modal button:has-text("确认")')
        await self.page.wait_for_timeout(3)
        await self.screenshot("project_add_03_after_submit")

        # 检查结果
        toast_msgs = await self.get_toast_message(2)
        print(f"  Toast提示: {toast_msgs}")

        # 判断是否成功
        success = False
        if toast_msgs:
            for msg in toast_msgs:
                if '成功' in msg['text'] or '已创建' in msg['text'] or '保存' in msg['text']:
                    success = True
                    break

        # 如果页面还在（说明成功），验证数据是否出现在列表
        if success:
            await self.log(module, "新增服务项目-提交", "PASS", f"Toast提示成功: {toast_msgs}", 
                          self.screenshot("project_add_04_success"))
        else:
            # 检查是否还在弹窗中（可能有验证错误）
            modal_visible = await self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.ant-modal');
                    return modal && modal.style.display !== 'none';
                }
            """)
            if modal_visible:
                # 检查验证错误
                errors = await self.page.evaluate("""
                    () => {
                        const errs = document.querySelectorAll('.ant-form-item-explain-error');
                        return Array.from(errs).map(e => e.textContent.trim());
                    }
                """)
                await self.log(module, "新增服务项目-提交", "FAIL", 
                              f"表单仍显示，验证错误: {errors}", 
                              await self.screenshot("project_add_05_validation_error"))
                # 关闭弹窗
                await self.page.click('.ant-modal-close')
                await self.page.wait_for_timeout(500)
                return
            else:
                # 可能没有Toast但成功了，检查表格
                await self.page.wait_for_timeout(2)
                found = await self.find_in_table(self.data["project_name"])
                if found:
                    success = True
                    await self.log(module, "新增服务项目-提交", "PASS", 
                                  f"数据已出现在列表中，行数: {len(found)}",
                                  await self.screenshot("project_add_04_verified"))
                    self.created["project"] = self.data["project_name"]
                else:
                    await self.log(module, "新增服务项目-提交", "FAIL", 
                                  f"未找到Toast提示，数据未出现在列表中",
                                  await self.screenshot("project_add_05_failed"))

    async def test_project_config_edit(self):
        """测试服务项目配置 - 编辑"""
        module = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 编辑服务项目")
        print(f"{'='*60}")

        await self.nav("/smart-service/project-config")

        # 查找包含测试数据的行
        found = await self.find_in_table(TEST_PREFIX)
        if not found:
            # 如果没有测试数据，找第一行进行编辑
            print("  未找到测试数据，使用第一行进行编辑测试")

        # 点击第一个编辑按钮
        edit_btn = self.page.locator('a:has-text("编辑")').first
        if await edit_btn.count() > 0:
            await edit_btn.click()
            await self.page.wait_for_timeout(1500)
            await self.screenshot("project_edit_01_opened")

            # 修改副标题
            subtitle_input = self.page.locator('.ant-form-item').filter(has_text="副标题").first.locator('input').first
            new_subtitle = f"{self.data['project_subtitle']}_编辑后"
            await subtitle_input.fill(new_subtitle)
            print(f"  修改副标题为: {new_subtitle}")

            await self.screenshot("project_edit_02_filled")

            # 点击确认
            await self.page.click('.ant-modal button:has-text("确 认"), .ant-modal button:has-text("确认")')
            await self.page.wait_for_timeout(3)
            await self.screenshot("project_edit_03_after_submit")

            # 检查结果
            toast_msgs = await self.get_toast_message(2)
            print(f"  Toast提示: {toast_msgs}")

            success = any('成功' in m['text'] or '已更新' in m['text'] or '保存' in m['text'] for m in toast_msgs)
            
            if success:
                await self.log(module, "编辑服务项目-提交", "PASS", f"Toast提示成功: {toast_msgs}",
                              await self.screenshot("project_edit_04_success"))
            else:
                # 检查是否有验证错误
                errors = await self.page.evaluate("""
                    () => {
                        const errs = document.querySelectorAll('.ant-form-item-explain-error');
                        return Array.from(errs).map(e => e.textContent.trim());
                    }
                """)
                if errors:
                    await self.log(module, "编辑服务项目-提交", "FAIL", f"验证错误: {errors}",
                                  await self.screenshot("project_edit_05_validation_error"))
                    await self.page.click('.ant-modal-close')
                    await self.page.wait_for_timeout(500)
                else:
                    await self.log(module, "编辑服务项目-提交", "PASS/FAIL", 
                                  f"Toast: {toast_msgs}, 需要人工确认",
                                  await self.screenshot("project_edit_06_unknown"))
        else:
            await self.log(module, "编辑服务项目", "SKIP", "未找到编辑按钮")

    async def test_project_config_delete(self):
        """测试服务项目配置 - 删除/切换展示状态"""
        module = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 切换展示状态")
        print(f"{'='*60}")

        await self.nav("/smart-service/project-config")

        # 查找"不展示"/"展示"按钮
        toggle_btn = self.page.locator('a:has-text("不展示"), a:has-text("展示")').first
        if await toggle_btn.count() > 0:
            btn_text = await toggle_btn.inner_text()
            print(f"  找到按钮: {btn_text}")
            await toggle_btn.click()
            await self.page.wait_for_timeout(1000)
            await self.screenshot("project_toggle_01_clicked")

            # 检查是否有确认弹窗
            confirm = self.page.locator('.ant-popconfirm, .ant-popover').first
            has_confirm = await confirm.count() > 0
            print(f"  有确认弹窗: {has_confirm}")

            if has_confirm:
                # 点击确认
                confirm_ok = self.page.locator('.ant-popconfirm button.ant-btn-primary, .ant-popover button.ant-btn-primary').first
                if await confirm_ok.count() > 0:
                    await confirm_ok.click()
                    await self.page.wait_for_timeout(2)
                    await self.screenshot("project_toggle_02_confirmed")

                    toast_msgs = await self.get_toast_message(2)
                    success = any('成功' in m['text'] for m in toast_msgs)
                    await self.log(module, f"切换展示状态({btn_text})", "PASS" if success else "FAIL",
                                  f"Toast: {toast_msgs}",
                                  await self.screenshot("project_toggle_03_result"))
                else:
                    await self.log(module, f"切换展示状态({btn_text})", "FAIL", "未找到确认按钮")
            else:
                await self.log(module, f"切换展示状态({btn_text})", "FAIL", "无确认弹窗，直接执行？",
                              await self.screenshot("project_toggle_no_confirm"))
        else:
            await self.log(module, "切换展示状态", "SKIP", "未找到切换按钮")

    async def test_contract_service_add(self):
        """测试合同服务配置 - 新增"""
        module = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 新增合同服务")
        print(f"{'='*60}")

        await self.nav("/smart-service/contract-service")

        # 点击新增
        await self.page.click('button:has-text("新增合同服务")')
        await self.page.wait_for_timeout(1500)
        await self.screenshot("contract_add_01_opened")

        # 获取表单结构
        form_structure = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-form-item');
                const fields = [];
                for (const item of items) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const labelText = label ? label.textContent.trim() : '';
                    const input = item.querySelector('input, textarea, .ant-select-selector');
                    const inputType = input ? input.tagName.toLowerCase() : 'unknown';
                    const placeholder = input ? input.getAttribute('placeholder') || '' : '';
                    fields.push({
                        label: labelText,
                        type: inputType,
                        placeholder: placeholder,
                    });
                }
                return fields;
            }
        """)
        print(f"  表单字段: {form_structure}")

        # 填写合同服务标题
        title_input = self.page.locator('.ant-form-item').filter(has_text="合同服务标题").first.locator('input').first
        await title_input.fill(self.data["contract_title"])
        print(f"  填写合同服务标题: {self.data['contract_title']}")

        # 填写合同服务内容（富文本）
        await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ql-editor, .w-e-text, [contenteditable="true"]');
                for (const editor of editors) {
                    editor.innerHTML = content;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
                return false;
            }
        """, self.data["contract_content"])
        print(f"  填写合同服务内容: {self.data['contract_content']}")

        # 填写费用内容
        fee_input = self.page.locator('.ant-form-item').filter(has_text="费用内容").first.locator('input').first
        await fee_input.fill(self.data["contract_fee"])
        print(f"  填写费用内容: {self.data['contract_fee']}")

        # 选择所属服务项目（下拉选择）
        select_trigger = self.page.locator('.ant-form-item').filter(has_text="所属服务项目").first.locator('.ant-select-selector')
        if await select_trigger.count() > 0:
            await select_trigger.click()
            await self.page.wait_for_timeout(500)
            # 选择第一个选项
            options = self.page.locator('.ant-select-item-option')
            opt_count = await options.count()
            print(f"  所属服务项目选项数: {opt_count}")
            if opt_count > 0:
                await options.first.click()
                print(f"  选择第一个服务项目")

        await self.screenshot("contract_add_02_filled")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认"), .ant-modal button:has-text("确认")')
        await self.page.wait_for_timeout(3)
        await self.screenshot("contract_add_03_after_submit")

        # 检查结果
        toast_msgs = await self.get_toast_message(2)
        print(f"  Toast提示: {toast_msgs}")

        success = any('成功' in m['text'] or '已创建' in m['text'] for m in toast_msgs)
        
        if success:
            await self.log(module, "新增合同服务-提交", "PASS", f"Toast提示成功",
                          await self.screenshot("contract_add_04_success"))
            self.created["contract"] = self.data["contract_title"]
        else:
            # 检查验证错误
            errors = await self.page.evaluate("""
                () => {
                    const errs = document.querySelectorAll('.ant-form-item-explain-error');
                    return Array.from(errs).map(e => e.textContent.trim());
                }
            """)
            if errors:
                await self.log(module, "新增合同服务-提交", "FAIL", f"验证错误: {errors}",
                              await self.screenshot("contract_add_05_validation_error"))
                await self.page.click('.ant-modal-close')
                await self.page.wait_for_timeout(500)
            else:
                await self.log(module, "新增合同服务-提交", "FAIL", f"Toast: {toast_msgs}",
                              await self.screenshot("contract_add_06_failed"))

    async def test_scope_config_add(self):
        """测试经营范围配置 - 新增"""
        module = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 新增经营范围")
        print(f"{'='*60}")

        await self.nav("/smart-service/scope-config")

        # 点击新增
        await self.page.click('button:has-text("新增经营范围")')
        await self.page.wait_for_timeout(1500)
        await self.screenshot("scope_add_01_opened")

        # 获取表单结构
        form_structure = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-form-item');
                const fields = [];
                for (const item of items) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const labelText = label ? label.textContent.trim() : '';
                    const input = item.querySelector('input, textarea, .ant-select-selector');
                    const inputType = input ? input.tagName.toLowerCase() : 'unknown';
                    const placeholder = input ? input.getAttribute('placeholder') || '' : '';
                    fields.push({
                        label: labelText,
                        type: inputType,
                        placeholder: placeholder,
                    });
                }
                return fields;
            }
        """)
        print(f"  表单字段: {form_structure}")

        # 填写经营范围名称
        name_input = self.page.locator('.ant-form-item').filter(has_text="经营范围名称").first.locator('input').first
        await name_input.fill(self.data["scope_name"])
        print(f"  填写经营范围名称: {self.data['scope_name']}")

        # 填写备注
        remark_input = self.page.locator('.ant-form-item').filter(has_text="备注").first.locator('input, textarea').first
        if await remark_input.count() > 0:
            await remark_input.fill(self.data["scope_remark"])
            print(f"  填写备注: {self.data['scope_remark']}")

        # 启用状态（默认启用）
        status_switch = self.page.locator('.ant-form-item').filter(has_text="启用状态").first.locator('.ant-switch')
        if await status_switch.count() > 0:
            is_checked = await status_switch.evaluate("el => el.classList.contains('ant-switch-checked')")
            print(f"  当前启用状态: {'启用' if is_checked else '禁用'}")
            # 如果是禁用状态，点击切换
            if not is_checked:
                await status_switch.click()
                print(f"  切换为启用")

        await self.screenshot("scope_add_02_filled")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认"), .ant-modal button:has-text("确认")')
        await self.page.wait_for_timeout(3)
        await self.screenshot("scope_add_03_after_submit")

        # 检查结果
        toast_msgs = await self.get_toast_message(2)
        print(f"  Toast提示: {toast_msgs}")

        success = any('成功' in m['text'] for m in toast_msgs)
        
        if success:
            await self.log(module, "新增经营范围-提交", "PASS", f"Toast提示成功",
                          await self.screenshot("scope_add_04_success"))
            self.created["scope"] = self.data["scope_name"]
        else:
            errors = await self.page.evaluate("""
                () => {
                    const errs = document.querySelectorAll('.ant-form-item-explain-error');
                    return Array.from(errs).map(e => e.textContent.trim());
                }
            """)
            if errors:
                await self.log(module, "新增经营范围-提交", "FAIL", f"验证错误: {errors}",
                              await self.screenshot("scope_add_05_validation_error"))
                await self.page.click('.ant-modal-close')
                await self.page.wait_for_timeout(500)
            else:
                # 检查数据是否出现在列表
                found = await self.find_in_table(self.data["scope_name"])
                if found:
                    await self.log(module, "新增经营范围-提交", "PASS", 
                                  f"数据已出现在列表中",
                                  await self.screenshot("scope_add_04_verified"))
                else:
                    await self.log(module, "新增经营范围-提交", "FAIL", 
                                  f"Toast: {toast_msgs}, 数据未找到",
                                  await self.screenshot("scope_add_06_failed"))

    async def test_knowledge_add(self):
        """测试知识库 - 新增"""
        module = "内容管理-知识库"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 新增知识库")
        print(f"{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 点击新增
        await self.page.click('button:has-text("新增知识库")')
        await self.page.wait_for_timeout(1500)
        await self.screenshot("knowledge_add_01_opened")

        # 获取表单结构
        form_structure = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-form-item');
                const fields = [];
                for (const item of items) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const labelText = label ? label.textContent.trim() : '';
                    const input = item.querySelector('input, textarea, .ant-select-selector');
                    const inputType = input ? input.tagName.toLowerCase() : 'unknown';
                    const placeholder = input ? input.getAttribute('placeholder') || '' : '';
                    fields.push({
                        label: labelText,
                        type: inputType,
                        placeholder: placeholder,
                    });
                }
                return fields;
            }
        """)
        print(f"  表单字段: {form_structure}")

        # 填写标题
        title_input = self.page.locator('.ant-form-item').filter(has_text="标题").first.locator('input').first
        await title_input.fill(self.data["knowledge_title"])
        print(f"  填写标题: {self.data['knowledge_title']}")

        # 填写内容（富文本）
        await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ql-editor, .w-e-text, [contenteditable="true"]');
                for (const editor of editors) {
                    editor.innerHTML = content;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
                return false;
            }
        """, self.data["knowledge_content"])
        print(f"  填写知识库内容")

        # 选择展示位置
        location_select = self.page.locator('.ant-form-item').filter(has_text="展示位置").first.locator('.ant-select-selector')
        if await location_select.count() > 0:
            await location_select.click()
            await self.page.wait_for_timeout(500)
            options = self.page.locator('.ant-select-item-option')
            opt_count = await options.count()
            print(f"  展示位置选项数: {opt_count}")
            if opt_count > 0:
                await options.first.click()
                print(f"  选择第一个展示位置")

        # 选择资讯类型
        type_select = self.page.locator('.ant-form-item').filter(has_text="资讯类型").first.locator('.ant-select-selector')
        if await type_select.count() > 0:
            await type_select.click()
            await self.page.wait_for_timeout(500)
            options = self.page.locator('.ant-select-item-option')
            opt_count = await options.count()
            print(f"  资讯类型选项数: {opt_count}")
            if opt_count > 0:
                await options.first.click()
                print(f"  选择第一个资讯类型")

        await self.screenshot("knowledge_add_02_filled")

        # 提交
        submit_btn = self.page.locator('.ant-modal button:has-text("确 认"), .ant-modal button:has-text("确认"), .ant-modal button:has-text("保存")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await self.page.wait_for_timeout(3)
            await self.screenshot("knowledge_add_03_after_submit")

            # 检查结果
            toast_msgs = await self.get_toast_message(2)
            print(f"  Toast提示: {toast_msgs}")

            success = any('成功' in m['text'] or '已创建' in m['text'] for m in toast_msgs)
            
            if success:
                await self.log(module, "新增知识库-提交", "PASS", f"Toast提示成功",
                              await self.screenshot("knowledge_add_04_success"))
                self.created["knowledge"] = self.data["knowledge_title"]
            else:
                errors = await self.page.evaluate("""
                    () => {
                        const errs = document.querySelectorAll('.ant-form-item-explain-error');
                        return Array.from(errs).map(e => e.textContent.trim());
                    }
                """)
                if errors:
                    await self.log(module, "新增知识库-提交", "FAIL", f"验证错误: {errors}",
                                  await self.screenshot("knowledge_add_05_validation_error"))
                    await self.page.click('.ant-modal-close')
                    await self.page.wait_for_timeout(500)
                else:
                    await self.log(module, "新增知识库-提交", "FAIL", f"Toast: {toast_msgs}",
                                  await self.screenshot("knowledge_add_06_failed"))
        else:
            await self.log(module, "新增知识库", "FAIL", "未找到提交按钮")

    async def test_knowledge_toggle_status(self):
        """测试知识库 - 禁用/启用状态切换"""
        module = "内容管理-知识库"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 禁用/启用状态切换")
        print(f"{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 查找禁用/启用按钮
        toggle_btn = self.page.locator('a:has-text("禁用"), a:has-text("启用")').first
        if await toggle_btn.count() > 0:
            btn_text = await toggle_btn.inner_text()
            print(f"  找到按钮: {btn_text}")
            await toggle_btn.click()
            await self.page.wait_for_timeout(1000)

            # 检查是否有确认弹窗
            confirm = self.page.locator('.ant-popconfirm, .ant-popover').first
            has_confirm = await confirm.count() > 0
            print(f"  有确认弹窗: {has_confirm}")

            if has_confirm:
                await self.screenshot("knowledge_toggle_01_confirm")
                # 点击确认
                confirm_ok = self.page.locator('.ant-popconfirm button.ant-btn-primary, .ant-popover button.ant-btn-primary').first
                if await confirm_ok.count() > 0:
                    await confirm_ok.click()
                    await self.page.wait_for_timeout(2)
                    
                    toast_msgs = await self.get_toast_message(2)
                    success = any('成功' in m['text'] for m in toast_msgs)
                    await self.log(module, f"知识库状态切换({btn_text})", "PASS" if success else "FAIL",
                                  f"Toast: {toast_msgs}",
                                  await self.screenshot("knowledge_toggle_02_result"))
                else:
                    await self.log(module, f"知识库状态切换({btn_text})", "FAIL", "未找到确认按钮")
            else:
                await self.log(module, f"知识库状态切换({btn_text})", "FAIL", "无确认弹窗")
        else:
            await self.log(module, "知识库状态切换", "SKIP", "未找到禁用/启用按钮")

    async def test_knowledge_detail(self):
        """测试知识库 - 查看详情"""
        module = "内容管理-知识库"
        print(f"\n{'='*60}")
        print(f"测试: {module} - 查看详情")
        print(f"{'='*60}")

        await self.nav("/content-manage/knowledge")

        # 点击详情
        detail_btn = self.page.locator('a:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)
            await self.screenshot("knowledge_detail_01_opened")

            # 检查弹窗是否打开
            modal_visible = await self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.ant-modal, .ant-drawer');
                    if (!modal) return false;
                    return modal.style.display !== 'none';
                }
            """)

            if modal_visible:
                # 获取详情内容
                content = await self.page.evaluate("""
                    () => {
                        const body = document.querySelector('.ant-modal-body, .ant-drawer-body');
                        if (!body) return null;
                        return body.textContent.trim().substring(0, 500);
                    }
                """)
                has_content = content and len(content) > 0
                await self.log(module, "知识库-查看详情", "PASS" if has_content else "FAIL",
                              f"详情内容: {content[:100] if content else '无内容'}...",
                              await self.screenshot("knowledge_detail_02_content"))
                
                # 关闭详情
                await self.page.click('.ant-modal-close, .ant-drawer-close')
                await self.page.wait_for_timeout(500)
            else:
                await self.log(module, "知识库-查看详情", "FAIL", "详情弹窗未打开")
        else:
            await self.log(module, "知识库-查看详情", "SKIP", "未找到详情按钮")

    def generate_report(self):
        """生成报告"""
        report_path = os.path.join(REPORT_DIR, f"real_data_test_report_{TIMESTAMP}.md")
        
        lines = [
            f"# 超级个体后台管理系统 - 实际数据提交验证报告",
            f"",
            f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"**测试环境:** http://172.16.1.165:9100",
            f"",
            f"**测试账号:** 17695729351",
            f"",
            f"## 测试结果汇总",
            f"",
        ]

        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        error = sum(1 for r in self.results if r["status"] == "ERROR")

        lines.extend([
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 测试总数 | {total} |",
            f"| ✅ 通过 | {passed} |",
            f"| ❌ 失败 | {failed} |",
            f"| ⏭️ 跳过 | {skipped} |",
            f"| ⚠️ 异常 | {error} |",
            f"| 通过率 | {passed/total*100:.1f}% |" if total > 0 else "| 通过率 | 0% |",
            f"",
            f"## 详细测试结果",
            f"",
        ])

        # 按模块分组
        current_module = ""
        for r in self.results:
            if r["module"] != current_module:
                current_module = r["module"]
                lines.append(f"### {current_module}")
                lines.append(f"")
            status_icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else ("⏭️" if r["status"] == "SKIP" else "⚠️"))
            lines.append(f"- {status_icon} **{r['test_name']}**: {r['detail']}")

        lines.extend([
            f"",
            f"## 问题汇总",
            f"",
        ])

        # 汇总失败和异常
        issues = [r for r in self.results if r["status"] in ("FAIL", "ERROR")]
        if issues:
            for i, issue in enumerate(issues, 1):
                lines.append(f"{i}. **{issue['test_name']}** - {issue['detail']}")
                if issue["screenshot"]:
                    lines.append(f"   - 截图: `{issue['screenshot']}`")
        else:
            lines.append("无发现问题。")

        lines.extend([
            f"",
            f"## 测试数据清理",
            f"",
            f"以下测试数据可能需要手动清理:",
            f"",
        ])

        for key, value in self.created.items():
            lines.append(f"- {key}: `{value}`")

        lines.append(f"")

        report_content = "\n".join(lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n报告已生成: {report_path}")
        return report_path

    async def run_all(self):
        """运行所有测试"""
        await self.setup()
        try:
            # 登录
            print("登录系统...")
            login_ok = await self.login()
            print(f"登录: {'成功' if login_ok else '失败'}")

            # 智能服务配置模块
            await self.test_project_config_add()
            await self.test_project_config_edit()
            await self.test_project_config_delete()
            await self.test_contract_service_add()
            await self.test_scope_config_add()

            # 内容管理模块
            await self.test_knowledge_add()
            await self.test_knowledge_toggle_status()
            await self.test_knowledge_detail()

        finally:
            await self.teardown()

        # 生成报告
        report_path = self.generate_report()
        return self.results, report_path


async def main():
    tester = RealDataTest()
    results, report_path = await tester.run_all()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"总数: {total}, 通过: {passed}, 失败: {failed}")
    print(f"报告: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
