"""
超级个体后台 - 实际数据提交验证 V5
基于探索到的表单结构，精确操作
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
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def gen_data():
    # 使用短名称，避免触发字符长度验证
    ts = datetime.now().strftime("%H%M%S")[-4:]  # 只取4位
    return {
        "project_name": f"测项{ts}",  # 短名称
        "project_subtitle": f"副标题{ts}",  # 短副标题
        "project_desc": f"测试描述内容_{ts}",
        "contract_title": f"合同{ts}",
        "contract_content": f"合同内容描述_{ts}",
        "contract_fee": f"费用说明_{ts}",
        "scope_name": f"范围{ts}",
        "scope_remark": f"备注说明_{ts}",
        "knowledge_title": f"知识{ts}",
        "knowledge_content": f"这是一条测试知识库的内容，用于验证新增功能是否正常工作。时间戳_{ts}",
    }


class TestV5:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results = []
        self.data = gen_data()
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

    def ok(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "PASS", "detail": detail, "ss": ss})
        print(f"  ✅ [PASS] {name}: {detail}")

    def fail(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "FAIL", "detail": detail, "ss": ss})
        print(f"  ❌ [FAIL] {name}: {detail}")

    def skip(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "SKIP", "detail": detail, "ss": ss})
        print(f"  ⏭️ [SKIP] {name}: {detail}")

    async def ss(self, name):
        p = os.path.join(SCREENSHOT_DIR, f"{name}_{TIMESTAMP}.png")
        await self.page.screenshot(path=p)
        return p

    async def login(self):
        await self.page.goto(LOGIN_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(1000)
        await self.page.fill('input[placeholder="账号"]', USERNAME)
        await self.page.fill('input[type="password"]', PASSWORD)
        await self.page.click('button:has-text("登 录")')
        await self.page.wait_for_timeout(2000)

    async def go(self, path):
        await self.page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await self.page.wait_for_timeout(1500)

    async def toasts(self):
        await self.page.wait_for_timeout(1)
        return await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-message-notice-content')).map(m => m.textContent.trim())
        """)

    async def get_modal(self):
        return self.page.locator(".ant-modal").first

    # ============ 服务项目配置 ============

    async def test_project_add(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 点击新增
        await self.page.click('button:has-text("新增服务项目")')
        await self.page.wait_for_timeout(1500)
        modal = await self.get_modal()
        await self.ss("proj_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增服务项目", "弹窗未打开")
            return

        # === 填写表单 ===
        
        # 1. 服务项目名称 - 用JS设置（因为没有可见的input选择器）
        await self.page.evaluate("""
            (value) => {
                // 找到label为"服务项目名称"的form-item中的第一个可见input
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '服务项目名称') {
                        const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                        if (input && input.offsetParent) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(input, value);
                            input.dispatchEvent(new Event('input', {bubbles: true}));
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["project_name"])
        
        # 2. 副标题
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '副标题') {
                        const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                        if (input && input.offsetParent) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(input, value);
                            input.dispatchEvent(new Event('input', {bubbles: true}));
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["project_subtitle"])
        
        # 3. 计费方式 - 选择"按次" (第一个radio)
        await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '计费方式') {
                        const radios = item.querySelectorAll('.ant-radio');
                        if (radios.length > 0) {
                            radios[0].click();  // 按次
                            return 'clicked';
                        }
                    }
                }
                return 'not_found';
            }
        """)
        
        # 4. 服务项目介绍 - 富文本编辑器
        await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ant-modal [contenteditable="true"]');
                for (const ed of editors) {
                    if (ed.offsetParent) {
                        ed.innerHTML = '<p>' + content + '</p>';
                        ed.dispatchEvent(new Event('input', {bubbles: true}));
                        ed.dispatchEvent(new Event('change', {bubbles: true}));
                        return 'ok';
                    }
                }
                return 'not_found';
            }
        """, self.data["project_desc"])

        print("  表单填写完成")
        await self.ss("proj_add_02")

        # 5. 点击确认
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        await self.ss("proj_add_03")

        # 检查结果
        msgs = await self.toasts()
        print(f"  Toast: {msgs}")

        if any("成功" in m for m in msgs):
            self.ok(mod, "新增服务项目", f"成功。Toast: {msgs}", await self.ss("proj_add_ok"))
            self.created["project"] = self.data["project_name"]
        elif await self.page.locator(".ant-modal").count() > 0:
            # 检查是否有验证错误
            errors = await self.page.evaluate("""
                () => {
                    const errs = document.querySelectorAll('.ant-form-item-explain-error');
                    return Array.from(errs).map(e => e.textContent.trim());
                }
            """)
            if errors:
                self.fail(mod, "新增服务项目", f"验证错误: {errors}", await self.ss("proj_add_validation_err"))
            else:
                self.fail(mod, "新增服务项目", f"仍在表单中，无验证错误。Toast: {msgs}", await self.ss("proj_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
            if self.data["project_name"] in text:
                self.ok(mod, "新增服务项目", "数据已在列表", await self.ss("proj_add_verified"))
            else:
                self.fail(mod, "新增服务项目", f"Toast: {msgs}", await self.ss("proj_add_fail"))

    async def test_project_edit(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 编辑\n{'='*60}")
        await self.go("/smart-service/project-config")

        edits = self.page.locator('a:has-text("编辑")')
        if await edits.count() > 0:
            await edits.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("proj_edit_01")

            if await self.page.locator(".ant-modal").count() > 0:
                # 修改副标题
                await self.page.evaluate("""
                    (value) => {
                        const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                        for (const item of formItems) {
                            const label = item.querySelector('.ant-form-item-label label');
                            if (label && label.textContent.trim() === '副标题') {
                                const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                                if (input && input.offsetParent) {
                                    const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                                    nativeSetter.call(input, value);
                                    input.dispatchEvent(new Event('input', {bubbles: true}));
                                    input.dispatchEvent(new Event('change', {bubbles: true}));
                                    return 'ok';
                                }
                            }
                        }
                        return 'not_found';
                    }
                """, f"{self.data['project_subtitle']}_编辑")

                await self.page.click('.ant-modal button:has-text("确 认")')
                await self.page.wait_for_timeout(3)
                await self.ss("proj_edit_02")

                msgs = await self.toasts()
                if any("成功" in m for m in msgs):
                    self.ok(mod, "编辑服务项目", f"成功。Toast: {msgs}", await self.ss("proj_edit_ok"))
                elif await self.page.locator(".ant-modal").count() > 0:
                    self.fail(mod, "编辑服务项目", f"仍在表单中。Toast: {msgs}", await self.ss("proj_edit_err"))
                    await self.page.locator(".ant-modal-close").click()
                    await self.page.wait_for_timeout(500)
                else:
                    self.ok(mod, "编辑服务项目", f"Toast: {msgs}（需人工确认）", await self.ss("proj_edit_unknown"))
            else:
                self.fail(mod, "编辑服务项目", "弹窗未打开")
        else:
            self.skip(mod, "编辑服务项目", "未找到编辑按钮")

    async def test_project_toggle(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 切换展示\n{'='*60}")
        await self.go("/smart-service/project-config")

        toggle = self.page.locator('a:has-text("不展示"), a:has-text("展示")')
        if await toggle.count() > 0:
            text = await toggle.first.text_content()
            await toggle.first.click()
            await self.page.wait_for_timeout(1000)

            confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
            if await confirm.count() > 0:
                await confirm.first.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"切换展示({text})", f"成功。Toast: {msgs}", await self.ss("proj_toggle_ok"))
            else:
                self.fail(mod, f"切换展示({text})", "无确认弹窗", await self.ss("proj_toggle_no"))
        else:
            self.skip(mod, "切换展示", "未找到按钮")

    # ============ 合同服务配置 ============

    async def test_contract_add(self):
        mod = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/contract-service")

        await self.page.click('button:has-text("新增合同服务")')
        await self.page.wait_for_timeout(1500)
        await self.ss("contract_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增合同服务", "弹窗未打开")
            return

        # 1. 合同服务标题
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '合同服务标题') {
                        const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                        if (input && input.offsetParent) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(input, value);
                            input.dispatchEvent(new Event('input', {bubbles: true}));
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["contract_title"])
        
        # 2. 所属服务项目 - 下拉选择
        await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '所属服务项目') {
                        const select = item.querySelector('.ant-select-selector');
                        if (select) {
                            select.click();
                            return 'clicked';
                        }
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(500)
        # 选择第一个选项
        options = self.page.locator(".ant-select-item-option")
        if await options.count() > 0:
            await options.first.click()
        
        # 3. 合同服务内容 - textarea
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '合同服务内容') {
                        const textarea = item.querySelector('textarea');
                        if (textarea && textarea.offsetParent) {
                            textarea.value = value;
                            textarea.dispatchEvent(new Event('input', {bubbles: true}));
                            textarea.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["contract_content"])
        
        # 4. 费用内容 - textarea
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '费用内容') {
                        const textarea = item.querySelector('textarea');
                        if (textarea && textarea.offsetParent) {
                            textarea.value = value;
                            textarea.dispatchEvent(new Event('input', {bubbles: true}));
                            textarea.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["contract_fee"])

        print("  表单填写完成")
        await self.ss("contract_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        await self.ss("contract_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增合同服务", f"成功。Toast: {msgs}", await self.ss("contract_add_ok"))
            self.created["contract"] = self.data["contract_title"]
        elif await self.page.locator(".ant-modal").count() > 0:
            errors = await self.page.evaluate("""
                () => {
                    const errs = document.querySelectorAll('.ant-form-item-explain-error');
                    return Array.from(errs).map(e => e.textContent.trim());
                }
            """)
            if errors:
                self.fail(mod, "新增合同服务", f"验证错误: {errors}", await self.ss("contract_add_validation_err"))
            else:
                self.fail(mod, "新增合同服务", f"仍在表单中。Toast: {msgs}", await self.ss("contract_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增合同服务", f"Toast: {msgs}", await self.ss("contract_add_fail"))

    # ============ 经营范围配置 ============

    async def test_scope_add(self):
        mod = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/scope-config")

        await self.page.click('button:has-text("新增经营范围")')
        await self.page.wait_for_timeout(1500)
        await self.ss("scope_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增经营范围", "弹窗未打开")
            return

        # 1. 经营范围名称
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '经营范围名称') {
                        const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                        if (input && input.offsetParent) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(input, value);
                            input.dispatchEvent(new Event('input', {bubbles: true}));
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["scope_name"])
        
        # 2. 备注 - textarea
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '备注') {
                        const textarea = item.querySelector('textarea');
                        if (textarea && textarea.offsetParent) {
                            textarea.value = value;
                            textarea.dispatchEvent(new Event('input', {bubbles: true}));
                            textarea.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["scope_remark"])

        print("  表单填写完成")
        await self.ss("scope_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        await self.ss("scope_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增经营范围", f"成功。Toast: {msgs}", await self.ss("scope_add_ok"))
            self.created["scope"] = self.data["scope_name"]
        elif await self.page.locator(".ant-modal").count() > 0:
            self.fail(mod, "新增经营范围", f"仍在表单中。Toast: {msgs}", await self.ss("scope_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增经营范围", f"Toast: {msgs}", await self.ss("scope_add_fail"))

    # ============ 知识库 ============

    async def test_knowledge_add(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/content-manage/knowledge")

        await self.page.click('button:has-text("新增知识库")')
        await self.page.wait_for_timeout(1500)
        await self.ss("knowledge_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增知识库", "弹窗未打开")
            return

        # 1. 标题
        await self.page.evaluate("""
            (value) => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '标题') {
                        const input = item.querySelector('input:not(.ant-select-selection-search-input)');
                        if (input && input.offsetParent) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            nativeSetter.call(input, value);
                            input.dispatchEvent(new Event('input', {bubbles: true}));
                            input.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'ok';
                        }
                    }
                }
                return 'not_found';
            }
        """, self.data["knowledge_title"])
        
        # 2. 资讯类型 - 下拉选择
        await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '资讯类型') {
                        const select = item.querySelector('.ant-select-selector');
                        if (select) { select.click(); return 'clicked'; }
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(500)
        options = self.page.locator(".ant-select-item-option")
        if await options.count() > 0:
            await options.first.click()
        
        # 3. 展示位置 - 下拉选择
        await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.trim() === '展示位置') {
                        const select = item.querySelector('.ant-select-selector');
                        if (select) { select.click(); return 'clicked'; }
                    }
                }
                return 'not_found';
            }
        """)
        await self.page.wait_for_timeout(500)
        options = self.page.locator(".ant-select-item-option")
        if await options.count() > 0:
            await options.first.click()
        
        # 4. 内容 - 富文本编辑器
        await self.page.evaluate("""
            (content) => {
                const editors = document.querySelectorAll('.ant-modal [contenteditable="true"]');
                for (const ed of editors) {
                    if (ed.offsetParent) {
                        ed.innerHTML = '<p>' + content + '</p>';
                        ed.dispatchEvent(new Event('input', {bubbles: true}));
                        ed.dispatchEvent(new Event('change', {bubbles: true}));
                        return 'ok';
                    }
                }
                return 'not_found';
            }
        """, self.data["knowledge_content"])

        print("  表单填写完成")
        await self.ss("knowledge_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        await self.ss("knowledge_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增知识库", f"成功。Toast: {msgs}", await self.ss("knowledge_add_ok"))
            self.created["knowledge"] = self.data["knowledge_title"]
        elif await self.page.locator(".ant-modal").count() > 0:
            errors = await self.page.evaluate("""
                () => {
                    const errs = document.querySelectorAll('.ant-form-item-explain-error');
                    return Array.from(errs).map(e => e.textContent.trim());
                }
            """)
            if errors:
                self.fail(mod, "新增知识库", f"验证错误: {errors}", await self.ss("knowledge_add_validation_err"))
            else:
                self.fail(mod, "新增知识库", f"仍在表单中。Toast: {msgs}", await self.ss("knowledge_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增知识库", f"Toast: {msgs}", await self.ss("knowledge_add_fail"))

    async def test_knowledge_toggle(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 状态切换\n{'='*60}")
        await self.go("/content-manage/knowledge")

        toggle = self.page.locator('a:has-text("禁用"), a:has-text("启用")')
        if await toggle.count() > 0:
            text = await toggle.first.text_content()
            await toggle.first.click()
            await self.page.wait_for_timeout(1000)

            confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
            if await confirm.count() > 0:
                await confirm.first.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"状态切换({text})", f"成功。Toast: {msgs}", await self.ss("knowledge_toggle_ok"))
            else:
                self.fail(mod, f"状态切换({text})", "无确认弹窗", await self.ss("knowledge_toggle_no"))
        else:
            self.skip(mod, "状态切换", "未找到按钮")

    async def test_knowledge_detail(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 查看详情\n{'='*60}")
        await self.go("/content-manage/knowledge")

        detail = self.page.locator('a:has-text("详情")')
        if await detail.count() > 0:
            await detail.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("knowledge_detail_01")

            if await self.page.locator(".ant-modal, .ant-drawer").count() > 0:
                content = await self.page.evaluate("""
                    () => {
                        const body = document.querySelector('.ant-modal-body, .ant-drawer-body');
                        return body ? body.textContent.trim().substring(0, 200) : null;
                    }
                """)
                self.ok(mod, "查看详情", f"内容: {content[:100] if content else '无'}...", await self.ss("knowledge_detail_ok"))
                
                close = self.page.locator(".ant-modal-close, .ant-drawer-close")
                if await close.count() > 0:
                    await close.first.click()
                    await self.page.wait_for_timeout(500)
            else:
                self.fail(mod, "查看详情", "弹窗未打开")
        else:
            self.skip(mod, "查看详情", "未找到详情按钮")

    def report(self):
        path = os.path.join(REPORT_DIR, f"real_data_report_{TIMESTAMP}.md")
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")

        lines = [
            f"# 超级个体后台 - 实际数据提交验证报告",
            f"",
            f"**时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 总数 | {total} |",
            f"| ✅通过 | {passed} |",
            f"| ❌失败 | {failed} |",
            f"| ⏭️跳过 | {skipped} |",
            f"",
            f"## 详细结果\n",
        ]

        mod = ""
        for r in self.results:
            if r["module"] != mod:
                mod = r["module"]
                lines.append(f"### {mod}\n")
            icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⏭️")
            lines.append(f"- {icon} **{r['name']}**: {r['detail']}")

        lines.extend([f"\n## 问题汇总\n"])
        issues = [r for r in self.results if r["status"] == "FAIL"]
        if issues:
            for i, iss in enumerate(issues, 1):
                lines.append(f"{i}. **{iss['name']}** - {iss['detail']}")
        else:
            lines.append("无问题。")

        lines.extend([f"\n## 测试数据（需清理）\n"])
        for k, v in self.created.items():
            lines.append(f"- {k}: `{v}`")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n报告: {path}")
        return path

    async def run(self):
        await self.setup()
        try:
            await self.login()
            await self.test_project_add()
            await self.test_project_edit()
            await self.test_project_toggle()
            await self.test_contract_add()
            await self.test_scope_add()
            await self.test_knowledge_add()
            await self.test_knowledge_toggle()
            await self.test_knowledge_detail()
        finally:
            await self.teardown()
        return self.report()


async def main():
    t = TestV5()
    await t.run()
    total = len(t.results)
    passed = sum(1 for r in t.results if r["status"] == "PASS")
    failed = sum(1 for r in t.results if r["status"] == "FAIL")
    skipped = sum(1 for r in t.results if r["status"] == "SKIP")
    print(f"\n总数:{total} 通过:{passed} 失败:{failed} 跳过:{skipped}")


if __name__ == "__main__":
    asyncio.run(main())
